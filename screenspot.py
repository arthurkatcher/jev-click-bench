"""ScreenSpot-v2 x Jev box. Screenshot + instruction -> one box question -> click the box centre -> hit?

Scoring = the standard ScreenSpot rule (SeeClick pretrain/screenspot_test.py, ScreenSpot-Pro
eval_sample_positive_gt): hit if the box centre is inside the ground-truth bbox, edges inclusive.
Every case gets a record. A malformed answer is a miss ("wrong_format"), like the official evals.
An infrastructure failure ("infra_error") is not scored: it is retried by re-running the pass.

  python3 screenspot.py 0 [--dry]               # one case, dev log results/runs.jsonl
  python3 screenspot.py run --pass 1 [--workers 4] [--max-cost 0.30] [--limit N] [--zoom]
  python3 screenspot.py report results/pass1.jsonl
  python3 screenspot.py compare results/pass1.jsonl results/pass2.jsonl
"""
import argparse, collections, datetime, hashlib, json, math, os, pathlib, statistics, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
import jev

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "screenspot-v2"
IMAGES = "screenspotv2_image"
OUT = ROOT / "results"
DEV_LOG = OUT / "runs.jsonl"
BENCH = "v2"
CELL_KEY = "platform"  # the report's cells = CELL_KEY x text/icon

# Frozen before the full run. The instruction is passed through unquoted (some contain their own
# quotes, some start with "click"/"tap"). OpenRouter guide: describe the target and name the image.
PROMPT_VERSION = "v2"
TEMPLATE = "In the screenshot, the UI element to use for this task: {instruction}"
TEMPLATE_HASH = hashlib.sha256(TEMPLATE.encode()).hexdigest()[:12]

EPS = 1e-9
CELLS = [(p, t) for p in ("mobile", "desktop", "web") for t in ("text", "icon")]
_lock = threading.Lock()


def load():
    if BENCH == "pro":
        return load_pro()
    cases = []
    for platform in ("mobile", "desktop", "web"):
        for c in json.loads((DATA / f"screenspot_{platform}_v2.json").read_text()):
            c["platform"] = platform
            cases.append(c)
    for i, c in enumerate(cases):
        c["i"] = i
    return cases  # 1,272 cases over 730 screenshots, bbox = [x, y, w, h] in original pixels


PRO_GROUPS = ("CAD", "Dev", "Creative", "Scientific", "Office", "OS")  # official leaderboard order


def use(bench):
    """Pick the benchmark before anything runs. Prompt, zoom rule and scoring are the same for both;
    only the data, the image folder, the results folder and the report cells change."""
    global BENCH, DATA, IMAGES, OUT, DEV_LOG, CELL_KEY, CELLS
    BENCH = bench
    if bench == "pro":
        DATA, IMAGES, OUT, CELL_KEY = ROOT / "data" / "screenspot-pro", "images", ROOT / "results" / "pro", "group"
        CELLS = [(g, t) for g in PRO_GROUPS for t in ("text", "icon")]
    DEV_LOG = OUT / "runs.jsonl"


def load_pro():
    """ScreenSpot-Pro in the official leaderboard setting (run_ss_pro.sh: --language en --gt_type positive
    --inst_style instruction): 1,581 cases, English instruction. Pro's bbox is [x1, y1, x2, y2]; it is
    stored as [x, y, w, h] like v2, so run_one's conversion gives back exactly x1/W, y1/H, x2/W, y2/H."""
    cases = []
    for f in sorted((DATA / "annotations").glob("*.json")):  # fixed order: file name, then file order
        for c in json.loads(f.read_text()):
            x1, y1, x2, y2 = c["bbox"]
            cases.append({"img_filename": c["img_filename"], "bbox": [x1, y1, x2 - x1, y2 - y1],
                          "instruction": c["instruction"], "platform": c["platform"], "group": c["group"],
                          "data_source": c["application"], "data_type": c["ui_type"], "id": c["id"],
                          "img_size": c["img_size"]})
    for i, c in enumerate(cases):
        c["i"] = i
    return cases


def clean(instruction):
    return " ".join(instruction.split())


def request(case, img):
    text = TEMPLATE.format(instruction=clean(case["instruction"]))
    state = [
        {"type": "text", "text": "Screenshot of a user interface:"},
        {"type": "image_url", "image_url": {"url": jev.data_url(img)}},
    ]
    return state, {"target": {"type": "box", "instructions": text}}, text


class MissingAnswer(Exception):
    """The response has no answers.target / box / edge keys: an infrastructure problem, re-run it."""


def parse_box(resp):
    """-> (box dict, confidence). MissingAnswer if the structure is absent; ValueError if the model
    produced edges that are not finite numbers (a wrong_format miss, as in the official evals)."""
    a = resp["answers"].get("target") if isinstance(resp.get("answers"), dict) else None
    b = a.get("box") if isinstance(a, dict) else None
    if not isinstance(b, dict) or any(k not in b for k in ("left", "top", "right", "bottom")):
        raise MissingAnswer(f"no complete box in answers.target: {a}")
    vals = [b[k] for k in ("left", "top", "right", "bottom")]
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in vals):
        raise ValueError(f"box edges are not finite numbers: {b}")
    return {k: float(b[k]) for k in ("left", "top", "right", "bottom")}, a.get("confidence")


def inside(point, gt, eps=0.0):
    return gt[0] - eps <= point[0] <= gt[2] + eps and gt[1] - eps <= point[1] <= gt[3] + eps


def cost(r):
    c = (r.get("usage") or {}).get("cost") if isinstance(r.get("usage"), dict) else None
    return float(c) if isinstance(c, (int, float)) and not isinstance(c, bool) and math.isfinite(c) else 0.0


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


ZOOM_F, ZOOM_MARGIN = 0.5, 0.1  # frozen before the zoom run (README "Zoom method")
try:
    import subprocess
    CODE_REV = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, timeout=5).stdout.strip() or None
except Exception:
    CODE_REV = None


def zoom_window(a, W, H):
    """Stage-B crop from stage A's record: half of each side of the screenshot around A's box,
    grown to hold A's whole box + 10% margin per side (capped at the full screen), same aspect as
    the screenshot, slid to stay inside it. -> (x0, y0, cw, ch) in original pixels."""
    b = {k: min(1.0, max(0.0, v)) for k, v in a["box"].items()}
    l, r = sorted((b["left"], b["right"]))
    t, bo = sorted((b["top"], b["bottom"]))
    k = max(ZOOM_F, min(1.0, max((r - l), (bo - t)) * (1 + 2 * ZOOM_MARGIN)))
    cw, ch = max(1, round(k * W)), max(1, round(k * H))
    x0 = min(max(round((l + r) / 2 * W - cw / 2), 0), W - cw)
    y0 = min(max(round((t + bo) / 2 * H - ch / 2), 0), H - ch)
    return x0, y0, cw, ch


def run_one(i, dry=False, cases=None, out=None, pass_id="dev", annotate_mode="misses", window=None, size=None):
    """window=(x0, y0, cw, ch) in original px + size=(w, h): stage B of the zoom method. The crop is
    resized to `size` (stage A's sent size, so the same tokens) and the box is mapped back to the
    full screenshot before scoring. Everything else (prompt, question, scoring) is identical."""
    out = out or DEV_LOG
    case = (cases or load())[i]
    orig = Image.open(DATA / IMAGES / case["img_filename"])
    W, H = orig.size
    if "img_size" in case and list(case["img_size"]) != [W, H]:  # Pro's official rule normalises by img_size
        raise ValueError(f"#{i}: image is {W}x{H}, annotation says {case['img_size']}")
    if window:
        x0, y0, cw, ch = window
        img = orig.crop((x0, y0, x0 + cw, y0 + ch)).resize(tuple(size), resample=3)  # 3 = BICUBIC, as fit()
        scale = size[0] / cw
    else:
        img, scale = jev.fit(orig)
    state, questions, text = request(case, img)
    x, y, w, h = case["bbox"]
    gt = [x / W, y / H, (x + w) / W, (y + h) / H]  # normalized x1, y1, x2, y2 (SeeClick conversion)
    rec = {"pass": pass_id, "i": i, "file": case["img_filename"], "platform": case["platform"],
           "source": case["data_source"], "type": case["data_type"], "instruction": case["instruction"],
           "instructions_sent": text, "prompt_version": PROMPT_VERSION, "template_hash": TEMPLATE_HASH,
           "requested_model": jev.MODEL, "orig_size": [W, H], "sent_size": list(img.size), "gt": gt}
    if BENCH != "v2":
        rec.update(bench=BENCH, group=case["group"], case_id=case["id"])
    if window:
        rec.update(stage="B", window=list(window), window_frac=round(cw / W, 4), zoom_f=ZOOM_F,
                   zoom_margin=ZOOM_MARGIN, code_rev=CODE_REV)
    if dry:
        print(json.dumps(rec, indent=1), "\nquestions:", json.dumps(questions),
              f"\nimage part: {len(state[1]['image_url']['url']) // 1024} KB base64")
        return rec

    rec["ts"] = now()
    rec.update(payload_bytes=len(state[1]["image_url"]["url"]), sent_pixels=img.size[0] * img.size[1],
               scale=round(scale, 6), gt_px=[x, y, w, h])
    t0 = time.time()
    try:
        resp, secs, attempts = jev.decide(state, questions)
        rec["wall_seconds"] = round(time.time() - t0, 3)
    except jev.JevError as e:
        rec["wall_seconds"] = round(time.time() - t0, 3)
        rec.update(status="infra_error", hit=None, error=str(e), http_status=e.status,
                   error_body=e.body, attempts=e.attempts, fatal=e.fatal)
        write(out, rec)
        return rec
    except Exception as e:  # backstop: never let one case abort a pass
        rec["wall_seconds"] = round(time.time() - t0, 3)
        rec.update(status="infra_error", hit=None, error=f"{type(e).__name__}: {e}", fatal=False)
        write(out, rec)
        return rec
    meta = resp if isinstance(resp, dict) else {}
    if not isinstance(resp, dict) or "error" in resp or not isinstance(resp.get("answers"), dict):
        rec.update(raw=resp, status="infra_error", hit=None, fatal=False, seconds=round(secs, 3),
                   attempts=attempts, usage=meta.get("usage"),
                   error="200 without an answers object (provider error body?)")
        write(out, rec)
        return rec
    rec.update(raw=resp, seconds=round(secs, 3), attempts=attempts, model=meta.get("model"),
               provider=meta.get("provider"), usage=meta.get("usage"))
    try:
        b, conf = parse_box(resp)
    except MissingAnswer as e:
        rec.update(status="infra_error", hit=None, fatal=False, error=str(e))
        write(out, rec)
        return rec
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        rec.update(status="wrong_format", hit=False, hit_tolerant=False, error=f"{type(e).__name__}: {e}")
        write(out, rec)
        return rec
    if window:  # crop fractions -> full-screenshot fractions
        rec["box_crop"] = b
        rec["out_of_crop"] = any(not 0 <= v <= 1 for v in b.values())  # pointed past the crop edge
    if window and tuple(window) != (0, 0, W, H):  # a full-screen window is the same image: keep b as is
        b = {"left": (x0 + b["left"] * cw) / W, "right": (x0 + b["right"] * cw) / W,
             "top": (y0 + b["top"] * ch) / H, "bottom": (y0 + b["bottom"] * ch) / H}
    point =[(b["left"] + b["right"]) / 2, (b["top"] + b["bottom"]) / 2]
    # hit = the official rule exactly (SeeClick / ScreenSpot-Pro: strict float compare, edges inclusive).
    # hit_tolerant adds 1e-9 so float noise on a 2-decimal centre that sits exactly on an edge cannot
    # flip it; reported next to the headline, never instead of it.
    hit = inside(point, gt)
    hit_tolerant = inside(point, gt, EPS)
    on_edge = any(abs(point[k % 2] - gt[k]) < EPS for k in range(4))
    # Official rule scores the centre whatever the box shape or range; both are flagged and counted.
    degenerate = b["right"] <= b["left"] or b["bottom"] <= b["top"]
    out_of_range = any(not 0 <= v <= 1 for v in b.values())  # edges outside the screenshot
    rec.update(status="ok", box=b, point=point, confidence=conf, hit=hit, hit_tolerant=hit_tolerant,
               degenerate=degenerate, out_of_range=out_of_range, on_edge=on_edge)
    if not isinstance((meta.get("usage") or {}).get("cost") if isinstance(meta.get("usage"), dict) else None, (int, float)):
        print(f"warning: #{i} answer has no usage.cost", file=sys.stderr)
    write(out, rec)
    if annotate_mode == "all" or (annotate_mode == "misses" and not hit):
        try:
            annotate(orig, gt, b, point, hit).save(OUT / f"{pass_id}_case_{i:04d}.png")
        except Exception as e:  # a drawing problem never kills a paid run
            print(f"annotate failed for #{i}: {e}", file=sys.stderr)
    return rec


_checked = set()


def write(out, rec):
    out.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        if out not in _checked:  # a hard kill can leave a half line: end it so the next record stays readable
            _checked.add(out)
            if out.exists() and out.stat().st_size:
                with open(out, "rb") as f:
                    f.seek(-1, 2)
                    tail = f.read(1)
                if tail != b"\n":
                    with open(out, "a") as f:
                        f.write("\n")
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")


def annotate(orig, gt, b, point, hit, max_w=1000):
    im = orig.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)))
    d = ImageDraw.Draw(im)
    W, H = im.size
    lw = max(2, W // 400)
    d.rectangle([gt[0] * W, gt[1] * H, gt[2] * W, gt[3] * H], outline=(0, 200, 0), width=lw)  # truth
    l, r = sorted((b["left"], b["right"]))
    t, bo = sorted((b["top"], b["bottom"]))
    d.rectangle([l * W, t * H, r * W, bo * H], outline=(230, 0, 0), width=lw)  # Jev
    px, py, rad = point[0] * W, point[1] * H, lw * 4
    d.ellipse([px - rad, py - rad, px + rad, py + rad], fill=(0, 120, 255) if hit else (230, 0, 0))
    return im


def read(path):
    """Records of a jsonl file; a truncated line (e.g. a killed run) is skipped with a warning."""
    out, bad = [], 0
    for l in open(path):
        if l.strip():
            try:
                out.append(json.loads(l))
            except ValueError:
                bad += 1
    if bad:
        print(f"warning: {bad} unreadable line(s) skipped in {path}", file=sys.stderr)
    return out


def latest(recs):
    """Last record per case index (a re-run of an infra_error replaces it)."""
    by = {}
    for r in recs:
        by[r["i"]] = r
    return by


def run_all(pass_id, workers=4, max_cost=0.30, limit=None, annotate_mode="misses", zoom=False):
    """zoom=False: the raw bench. zoom=True: the same raw call (stage A, into pass<N>.jsonl, so it is
    also a plain raw pass) followed by stage B on the zoom crop (into zoom<N>.jsonl). The cost cap
    covers both files."""
    cases = load()
    out = OUT / f"pass{pass_id}.jsonl"
    zout = OUT / f"zoom{pass_id}.jsonl"
    scored = lambda path: ({i: r for i, r in latest(read(path)).items() if r["status"] in ("ok", "wrong_format")}
                           if path.exists() else {})
    a_done = scored(out)
    z_done = scored(zout) if zoom else {}
    done = {i for i in a_done if not zoom or i in z_done}
    spent = sum(cost(r) for path in ((out, zout) if zoom else (out,)) if path.exists() for r in read(path))
    todo = [c["i"] for c in cases if c["i"] not in done][:limit]
    print(f"pass {pass_id}{' + zoom' if zoom else ''}: {len(done)} done, {len(todo)} to run, "
          f"${spent:.4f} logged so far, cap ${max_cost}")
    before = jev.balance()
    print(f"key balance before: {before}")
    stop = threading.Event()
    state = {"spent": spent, "n": 0, "hits": 0, "ok": 0, "wrong_format": 0, "infra_error": 0, "secs": [],
             "tokens": 0, "t0": time.time(), "zoom_hits": 0, "zoom_scored": 0, "zoom_wrong_format": 0,
             "zoom_infra_error": 0, "zoom_secs": [], "zoom_tokens": 0, "a_resumed": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    prog = OUT / f"pass{pass_id}.progress.json"

    def progress(final=False):
        n, el = state["n"], time.time() - state["t0"]
        sc = state["ok"] + state["wrong_format"]
        tmp = prog.with_suffix(".tmp")
        snap = {
            "pass": pass_id, "updated": now(), "final": final, "done_this_run": n, "todo_this_run": len(todo),
            "already_done_before": len(done), "total_cases": len(cases),  # zoom mode: both stages done
            "scored_total": len(done) + sc if not zoom else None, "hits_this_run": state["hits"],
            "running_acc_this_run": round(100 * state["hits"] / sc, 2) if sc else None,
            "ok": state["ok"], "wrong_format": state["wrong_format"], "infra_error": state["infra_error"],
            "spent_logged_total": round(state["spent"], 6), "input_tokens_this_run": state["tokens"],
            "median_latency_s": round(statistics.median(state["secs"]), 3) if state["secs"] else None,
            "elapsed_s": round(el, 1), "eta_s": round(el / n * (len(todo) - n), 1) if n else None,
            "stopped": stop.is_set(), "zoom": zoom}
        if zoom:
            snap.update({
                "a_scored_total": len(a_done) + sc, "a_resumed_this_run": state["a_resumed"],
                "zoom_scored_total": len(z_done) + state["zoom_scored"],
                "zoom_scored_this_run": state["zoom_scored"], "zoom_hits_this_run": state["zoom_hits"],
                "zoom_running_acc_this_run": round(100 * state["zoom_hits"] / state["zoom_scored"], 2)
                if state["zoom_scored"] else None,
                "zoom_wrong_format": state["zoom_wrong_format"], "zoom_infra_error": state["zoom_infra_error"],
                "zoom_median_latency_s": round(statistics.median(state["zoom_secs"]), 3) if state["zoom_secs"] else None,
                "zoom_input_tokens_this_run": state["zoom_tokens"]})
        tmp.write_text(json.dumps(snap))
        os.replace(tmp, prog)

    def stage_b(i, a):
        """Stage B for case i from stage A's scored record. A wrong_format A has no box to zoom on:
        the zoom answer is the same miss (copied, no cost)."""
        if a["status"] != "ok":
            z = {k: v for k, v in a.items() if k not in ("usage", "raw", "seconds", "wall_seconds", "attempts",
                                                         "payload_bytes", "sent_pixels", "scale")}
            z.update({"pass": f"z{pass_id}", "stage": "B", "zoom_skipped": "stage A wrong_format", "ts": now(),
                      "zoom_f": ZOOM_F, "zoom_margin": ZOOM_MARGIN, "code_rev": CODE_REV})
            write(zout, z)
            return z
        W, H = a["orig_size"]
        return run_one(i, cases=cases, out=zout, pass_id=f"z{pass_id}", annotate_mode=annotate_mode,
                       window=zoom_window(a, W, H), size=a["sent_size"])

    def over_cap():
        with _lock:
            return state["spent"] >= max_cost

    def job(i):
        if stop.is_set() or over_cap():
            return
        resumed = i in a_done
        if resumed:  # A scored before, only B is missing
            rec, new_cost = a_done[i], 0.0
        else:
            rec = run_one(i, cases=cases, out=out, pass_id=str(pass_id), annotate_mode=annotate_mode)
            new_cost = cost(rec)
        z = None
        with _lock:  # never start B once A has taken the logged spend to the cap (B stays resumable)
            room = state["spent"] + new_cost < max_cost
        if zoom and rec["status"] in ("ok", "wrong_format") and not rec.get("fatal") and not stop.is_set() and room:
            z = stage_b(i, rec)
        with _lock:
            state["n"] += 1
            state["spent"] += new_cost + (cost(z) if z else 0.0)
            state["a_resumed"] += 1 if resumed else 0
            if z:
                if z["status"] in ("ok", "wrong_format"):
                    state["zoom_scored"] += 1
                    state["zoom_hits"] += 1 if z.get("hit") else 0
                if z["status"] in ("wrong_format", "infra_error"):
                    state[f"zoom_{z['status']}"] += 1
                if z["status"] == "infra_error" and state["zoom_infra_error"] <= 20:
                    print(f"zoom infra_error on #{i}: {z.get('error')}", file=sys.stderr)
                if z.get("seconds") is not None:
                    state["zoom_secs"].append(z["seconds"])
                if z.get("fatal"):
                    print(f"FATAL {z['error']} on #{i} (zoom): stopping the run", file=sys.stderr)
                    stop.set()
            if not resumed:  # the A counters are this run's A calls only
                state[rec["status"]] = state.get(rec["status"], 0) + 1
                state["hits"] += 1 if rec.get("hit") else 0
                if rec.get("seconds") is not None:
                    state["secs"].append(rec["seconds"])
            for x, key in ((rec, "tokens"),) * (not resumed) + ((z, "zoom_tokens"),) * bool(z):
                u = x.get("usage") if isinstance(x.get("usage"), dict) else {}
                state[key] += u["input_tokens"] if isinstance(u.get("input_tokens"), int) else 0
            progress()
            if rec.get("fatal"):
                print(f"FATAL {rec['error']} on #{i}: stopping the run", file=sys.stderr)
                stop.set()
            if state["spent"] >= max_cost:
                print(f"cost cap reached (${state['spent']:.4f}): stopping", file=sys.stderr)
                stop.set()
            if state["n"] % 50 == 0:
                print(f"  {state['n']}/{len(todo)}  ${state['spent']:.4f}" + (
                    f"  zoom scored {state['zoom_scored']}, infra {state['zoom_infra_error']}" if zoom else ""))

    if spent >= max_cost:
        print(f"cap already reached (${spent:.4f} logged >= ${max_cost}): rerun with --max-cost raised to the "
              f"logged total + ~$0.0003 per remaining case")
        progress(final=True)
        return
    progress()
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, todo))
    progress(final=True)
    after = jev.balance()
    if isinstance(before, float) and isinstance(after, float):
        billed, logged = before - after, state["spent"] - spent
        print(f"key balance after: {after:.6f}  (billed this run: ${billed:.6f}, logged this run: ${logged:.6f})")
        if logged and abs(billed - logged) > 0.2 * logged:
            print("  note: the balance lags billing; check it again later. Logged usage.cost is the cost of record.")
    print(f"logged cost this run: ${state['spent'] - spent:.6f} (all stages, incl. billed error bodies)")
    report(out)
    if zoom:
        report(zout)
        zoomstats(out, zout)

def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def auroc(pos, neg):
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def report(path):
    cases = load()
    by = latest(read(path))
    n_total = len(cases)
    scored = {i: r for i, r in by.items() if r["status"] in ("ok", "wrong_format")}
    infra = [i for i, r in by.items() if r["status"] == "infra_error"]
    missing = n_total - len(by)
    for i, r in scored.items():  # identity check against the dataset
        assert r["file"] == cases[i]["img_filename"] and r["instruction"] == cases[i]["instruction"], i
    versions = collections.Counter((r["prompt_version"], r["template_hash"]) for r in scored.values())
    models = collections.Counter((r.get("requested_model"), r.get("model"), r.get("provider")) for r in scored.values())
    problems = []
    if infra:
        problems.append(f"{len(infra)} infra_error")
    if missing:
        problems.append(f"{missing} not run")
    if len(versions) > 1:
        problems.append("mixed prompt versions")
    zcfg = {(r.get("zoom_f"), r.get("zoom_margin"), r.get("code_rev")) for r in scored.values() if r.get("stage") == "B"}
    if len({c[:2] for c in zcfg}) > 1:
        problems.append("mixed zoom configs")
    if len({m[0] for m in models}) > 1 or len({m[1] for m in models}) > 1:
        problems.append("mixed requested/resolved models")
    complete = not problems
    flag = "" if complete else f"  ** INCOMPLETE ({', '.join(problems)}): not a headline number **"
    lines = [f"# {pathlib.Path(path).name}" + flag, f"prompt versions: {dict(versions)}",
             f"models (requested, resolved, provider): {dict(models)}"]
    lines.append(f"| {CELL_KEY.title()} | Type | n | scored | hits | acc | 95% CI |")
    lines.append("|---|---|---|---|---|---|---|")
    cell_acc = []
    for p, t in CELLS:
        idx = [c["i"] for c in cases if c[CELL_KEY] == p and c["data_type"] == t]
        hits = sum(1 for i in idx if scored.get(i, {}).get("hit"))
        acc = hits / len(idx)
        cell_acc.append(acc)
        lo, hi = wilson(hits, len(idx))
        lines.append(f"| {p} | {t} | {len(idx)} | {sum(1 for i in idx if i in scored)} | {hits} | {100 * acc:.2f} "
                     f"| {lo:.1f}-{hi:.1f} |")
    hits = sum(1 for r in scored.values() if r["hit"])
    lines.append("")
    lo, hi = wilson(hits, n_total)
    lines.append(f"Avg (micro, hits / {n_total}, official strict rule, as published {BENCH} tables): "
                 f"{100 * hits / n_total:.2f}  (95% Wilson CI {lo:.1f}-{hi:.1f})" + flag)
    for t in ("text", "icon"):  # the official text_acc / icon_acc
        idx = [c["i"] for c in cases if c["data_type"] == t]
        lines.append(f"  {t}: {100 * sum(1 for i in idx if scored.get(i, {}).get('hit')) / len(idx):.2f} (n={len(idx)})")
    tol = sum(1 for r in scored.values() if r.get("hit_tolerant"))
    lines.append(f"Avg (micro, 1e-9 edge tolerance): {100 * tol / n_total:.2f}  "
                 f"({sum(1 for r in scored.values() if bool(r.get('hit_tolerant')) != bool(r['hit']))} cases differ)" + flag)
    lines.append(f"Avg (macro, mean of {len(CELLS)} cells): {100 * statistics.mean(cell_acc):.2f}" + flag)
    ok = [r for r in scored.values() if r["status"] == "ok"]
    lines.append(f"scored {len(scored)}/{n_total}, wrong_format {len(scored) - len(ok)}, infra_error {len(infra)}, "
                 f"not run {missing}, degenerate boxes {sum(1 for r in ok if r['degenerate'])}, "
                 f"centre on a truth edge {sum(1 for r in ok if r.get('on_edge'))}, "
                 f"edges outside [0,1] {sum(1 for r in ok if r.get('out_of_range'))}"
                 + (f", stage B box past the crop edge {sum(1 for r in ok if r.get('out_of_crop'))}, "
                    f"zoom configs {sorted(zcfg, key=str)}" if zcfg else ""))
    secs = sorted(r["seconds"] for r in by.values() if r.get("seconds") is not None)
    spend = sum(cost(r) for r in read(path))
    if secs:
        lines.append(f"latency median {statistics.median(secs):.3f}s p90 {secs[int(0.9 * (len(secs) - 1))]:.3f}s, "
                     f"cost of logged responses ${spend:.4f} (retried attempts are not logged; compare the key balance)")
    toks = [r["usage"]["input_tokens"] for r in by.values() if isinstance(r.get("usage"), dict)
            and isinstance(r["usage"].get("input_tokens"), int)]
    walls = sorted(r["wall_seconds"] for r in by.values() if r.get("wall_seconds") is not None)
    if toks:
        lines.append(f"input tokens: total {sum(toks):,}, mean {statistics.mean(toks):.0f}, min {min(toks)}, max {max(toks)}; "
                     f"wall time incl. retries median {statistics.median(walls):.3f}s; "
                     f"retried cases {sum(1 for r in by.values() if (r.get('attempts') or 1) > 1)}")
    confs = [(r["confidence"], r["hit"]) for r in ok if isinstance(r.get("confidence"), (int, float))]
    a = auroc([c for c, h in confs if h], [c for c, h in confs if not h])
    lines.append(f"confidence AUROC (hit vs miss): {a if a is None else round(a, 3)}")
    edges = [0, .5, .6, .7, .8, .9, 1.0]
    for lo, hi in zip(edges, edges[1:]):
        b = [h for c, h in confs if lo <= c < hi or (hi == 1.0 and c == 1.0)]
        if b:
            lines.append(f"  conf [{lo:.1f}, {hi:.1f}{']' if hi == 1.0 else ')'}: n={len(b)} acc={100 * sum(b) / len(b):.1f}")
    print("\n".join(lines))
    return complete


def mcnemar(b, c):
    """Exact two-sided McNemar p-value on the discordant pairs (b = miss->hit, c = hit->miss)."""
    n = b + c
    if not n:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare(p1, p2, methods=None):
    """Case-level comparison. methods=False: two runs of the same method (rerun stability).
    methods=True: raw stage A vs zoom A+B (paired: delta + McNemar, no mean of the two).
    None: methods if the second file holds stage-B records."""
    a, b = latest(read(p1)), latest(read(p2))
    if methods is None:
        methods = any(r.get("stage") == "B" for r in b.values())
    sa = {i: r for i, r in a.items() if r["status"] in ("ok", "wrong_format")}
    sb = {i: r for i, r in b.items() if r["status"] in ("ok", "wrong_format")}
    n = len(load())
    if len(sa) != n or len(sb) != n:
        print(f"INCOMPLETE: {len(sa)} and {len(sb)} of {n} scored; finish both passes first")
        return None
    ident = lambda d: {(r.get("template_hash"), r.get("requested_model"), r.get("model")) for r in d.values()
                       if r["status"] == "ok"}
    if ident(sa) != ident(sb):
        print(f"INCOMPLETE: template/model differ between files: {ident(sa)} vs {ident(sb)}")
        return None
    agree = sum(1 for i in sa if bool(sa[i]["hit"]) == bool(sb[i]["hit"]))
    up = sum(1 for i in sa if not sa[i]["hit"] and sb[i]["hit"])
    down = sum(1 for i in sa if sa[i]["hit"] and not sb[i]["hit"])
    m1 = 100 * sum(1 for r in sa.values() if r["hit"]) / n
    m2 = 100 * sum(1 for r in sb.values() if r["hit"]) / n
    p = mcnemar(up, down)
    if methods:
        print(f"raw A {m1:.2f}  zoom A+B {m2:.2f}  delta {m2 - m1:+.2f} pp  (paired, exact McNemar p={p:.4g})")
    else:
        print(f"pass {pathlib.Path(p1).stem} {m1:.2f}  pass {pathlib.Path(p2).stem} {m2:.2f}  "
              f"mean {(m1 + m2) / 2:.2f} +- {abs(m1 - m2) / 2:.2f}  (exact McNemar p={p:.4g})")
    line = f"case-level agreement {agree}/{n} ({100 * agree / n:.1f}%), miss->hit {up}, hit->miss {down}"
    if not methods:  # determinism: identical answers, not just the same hit/miss (confidence jitters on its own)
        same_box = [i for i in sa if sa[i]["status"] == sb[i]["status"] == "ok" and sa[i].get("box") is not None
                    and sa[i].get("box") == sb[i].get("box")]
        same = sum(1 for i in same_box if sa[i].get("confidence") == sb[i].get("confidence"))
        line += f", identical box {len(same_box)}/{n}, identical box+confidence {same}/{n}"
    print(line)
    return agree


def paired_ci(xa, xb, reps=10000, seed=0):
    """95% bootstrap CI (resampling cases) of the paired accuracy delta in pp; deterministic seed."""
    import random
    rnd, n = random.Random(seed), len(xa)
    d = [b - a for a, b in zip(xa, xb)]
    ds = sorted(100 * sum(d[rnd.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return ds[int(0.025 * reps)], ds[int(0.975 * reps) - 1]


def zoomstats(pass_file, zoom_file, rerun=None):
    """Raw stage A vs zoom A+B, paired on the same cases: per cell, per window group, cost and latency.
    rerun: a second raw pass; its flips vs pass_file are the noise floor for the zoom flips."""
    a, z = latest(read(pass_file)), latest(read(zoom_file))
    ok = lambda r: r["status"] in ("ok", "wrong_format")
    ids = sorted(i for i in z if i in a and ok(a[i]) and ok(z[i]))
    n_all = len(load())
    if len(ids) != n_all:
        print(f"** INCOMPLETE: {len(ids)} of {n_all} cases have both stages scored **")
    if not ids:
        return None
    hit = lambda r: 1 if r.get("hit") else 0
    def row(name, sel):
        if not sel:
            return
        ha, hz = sum(hit(a[i]) for i in sel), sum(hit(z[i]) for i in sel)
        up = sum(1 for i in sel if not hit(a[i]) and hit(z[i]))
        dn = sum(1 for i in sel if hit(a[i]) and not hit(z[i]))
        print(f"| {name} | {len(sel)} | {100 * ha / len(sel):.2f} | {100 * hz / len(sel):.2f} | "
              f"{100 * (hz - ha) / len(sel):+.2f} | {up} | {dn} | {mcnemar(up, dn):.3g} |")
    print("| Group | n | raw A | zoom A+B | delta pp | miss->hit | hit->miss | McNemar p |")
    print("|---|---|---|---|---|---|---|---|")
    row("all", ids)
    cases = load()
    for p, t in CELLS:
        row(f"{p} {t}", [i for i in ids if cases[i][CELL_KEY] == p and cases[i]["data_type"] == t])
    wf = lambda i: z[i].get("window_frac")
    row("window half (zoom 2x)", [i for i in ids if wf(i) is not None and wf(i) <= ZOOM_F + 0.01])
    row("window widened", [i for i in ids if wf(i) is not None and ZOOM_F + 0.01 < wf(i) < 0.9999])
    full = [i for i in ids if wf(i) is not None and wf(i) >= 0.9999]
    row("window full screen (same image re-asked)", full)
    row("A wrong_format (no B call)", [i for i in ids if z[i].get("zoom_skipped")])
    row("A sent at native size (B = upsample only)", [i for i in ids if (a[i].get("scale") or 0) >= 0.999])
    row("A downscaled (B recovers pixels)", [i for i in ids if 0 < (a[i].get("scale") or 0) < 0.999])
    lo, hi = paired_ci([hit(a[i]) for i in ids], [hit(z[i]) for i in ids])
    print(f"paired delta 95% bootstrap CI: {lo:+.2f} to {hi:+.2f} pp")
    if full:
        same = sum(1 for i in full if z[i].get("box_crop") == a[i].get("box"))
        flips = sum(1 for i in full if hit(a[i]) != hit(z[i]))
        print(f"full-screen group: identical box {same}/{len(full)}, hit flips {flips}/{len(full)} "
              f"({100 * flips / len(full):.1f}%)")
    if rerun:
        r = latest(read(rerun))
        common = [i for i in ids if i in r and ok(r[i])]
        rf = sum(1 for i in common if hit(r[i]) != hit(a[i]))
        zf = sum(1 for i in ids if hit(a[i]) != hit(z[i]))
        print(f"noise floor: raw rerun flips {rf}/{len(common)} ({100 * rf / max(len(common), 1):.1f}%) vs "
              f"zoom flips {zf}/{len(ids)} ({100 * zf / len(ids):.1f}%)")
    both = [i for i in ids if a[i].get("seconds") is not None and z[i].get("seconds") is not None]
    if both:
        q = lambda xs: (statistics.median(xs), sorted(xs)[int(0.9 * (len(xs) - 1))])
        la = q([a[i]["seconds"] for i in both]); lab = q([a[i]["seconds"] + z[i]["seconds"] for i in both])
        wa = q([a[i]["wall_seconds"] for i in both if a[i].get("wall_seconds") is not None] or [0])
        wab = q([a[i]["wall_seconds"] + z[i]["wall_seconds"] for i in both
                 if a[i].get("wall_seconds") is not None and z[i].get("wall_seconds") is not None] or [0])
        ta = sum((a[i].get("usage") or {}).get("input_tokens") or 0 for i in both)
        tz = sum((z[i].get("usage") or {}).get("input_tokens") or 0 for i in both)
        print(f"latency per case over {len(both)} cases (median / p90): A {la[0]:.3f}/{la[1]:.3f}s, "
              f"A+B {lab[0]:.3f}/{lab[1]:.3f}s; wall incl. retries A {wa[0]:.3f}/{wa[1]:.3f}s, A+B {wab[0]:.3f}/{wab[1]:.3f}s")
        print(f"input tokens over the same cases: A {ta:,}, B {tz:,} (A+B = {(ta + tz) / max(ta, 1):.2f}x A)")
    ca = sum(cost(r) for r in read(pass_file)); cz = sum(cost(r) for r in read(zoom_file))
    print(f"logged cost, all records: A file ${ca:.4f}, zoom file ${cz:.4f}, total ${ca + cz:.4f}")
    return len(ids)


def check():
    """Offline preflight, no API: every image present and readable, its size equal to the annotation's
    img_size (Pro), every truth box with a positive area (boxes past the image edge are printed as notes).
    Prints the sent sizes."""
    cases, bad, notes, sent, files = load(), [], [], collections.Counter(), set()
    for c in cases:
        p = DATA / IMAGES / c["img_filename"]
        files.add(c["img_filename"])
        try:
            with Image.open(p) as im:
                W, H = im.size
        except Exception as e:
            bad.append(f"#{c['i']} {c['img_filename']}: {type(e).__name__}")
            continue
        if "img_size" in c and list(c["img_size"]) != [W, H]:
            bad.append(f"#{c['i']}: image {W}x{H}, annotation {c['img_size']}")
        x, y, w, h = c["bbox"]
        if not (w > 0 and h > 0):
            bad.append(f"#{c['i']}: bbox {c['bbox']} has no area")
        elif not (x >= 0 and y >= 0 and x + w <= W and y + h <= H):  # the official rule scores it as given
            notes.append(f"#{c['i']}: bbox {c['bbox']} runs past the {W}x{H} image edge")
        s = min(1.0, jev.MAX_SIDE / max(W, H))
        sent[(W, H, round(W * s), round(H * s))] += 1
    print(f"{BENCH}: {len(cases)} cases, {len(files)} screenshots, {len(bad)} problems")
    for b in bad[:30]:
        print("  ", b)
    for b in notes:
        print("   note (label quirk, scored as given):", b)
    print("original -> sent size (cases):")
    for (W, H, w, h), n in sent.most_common():
        print(f"  {W}x{H} -> {w}x{h}  ({n})")
    return not bad


if __name__ == "__main__":
    if "--bench" in sys.argv:  # python3 screenspot.py --bench pro run --pass 1 --zoom
        k = sys.argv.index("--bench")
        use(sys.argv[k + 1])
        del sys.argv[k:k + 2]
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        sys.exit(0 if check() else 1)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        i = int(sys.argv[1])
        rec = run_one(i, dry="--dry" in sys.argv, annotate_mode="all")
        if "status" in rec:
            if rec["status"] == "ok":
                print(f'{"TRUE" if rec["hit"] else "FALSE"}  #{i} [{rec["platform"]}/{rec["type"]}] "{rec["instruction"]}"'
                      f'  conf={rec["confidence"]}  {rec["seconds"]}s  usage={rec["usage"]}')
            else:
                print(f'{rec["status"].upper()}  #{i}: {rec["error"]}')
        sys.exit(0)
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--pass", dest="pass_id", type=int, required=True)
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--max-cost", type=float, default=0.30)
    r.add_argument("--limit", type=int)
    r.add_argument("--annotate", choices=["misses", "all", "none"], default="misses")
    r.add_argument("--zoom", action="store_true", help="A then B on the zoom crop (README: Zoom method)")
    rp = sub.add_parser("report")
    rp.add_argument("path")
    cp = sub.add_parser("compare")
    cp.add_argument("pass_a")
    cp.add_argument("pass_b")
    zs = sub.add_parser("zoomstats")
    zs.add_argument("pass_file")
    zs.add_argument("zoom_file")
    zs.add_argument("--rerun", help="another raw pass of the same method (noise floor), e.g. results/pass1.jsonl")
    args = ap.parse_args()
    if args.cmd == "run":
        run_all(args.pass_id, args.workers, args.max_cost, args.limit, args.annotate, args.zoom)
    elif args.cmd == "zoomstats":
        zoomstats(args.pass_file, args.zoom_file, args.rerun)
    elif args.cmd == "compare":
        compare(args.pass_a, args.pass_b)
    else:
        report(args.path)
