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
OUT = ROOT / "results"
DEV_LOG = OUT / "runs.jsonl"

# Frozen before the full run. The instruction is passed through unquoted (some contain their own
# quotes, some start with "click"/"tap"). OpenRouter guide: describe the target and name the image.
PROMPT_VERSION = "v2"
TEMPLATE = "In the screenshot, the UI element to use for this task: {instruction}"
TEMPLATE_HASH = hashlib.sha256(TEMPLATE.encode()).hexdigest()[:12]

EPS = 1e-9
CELLS = [(p, t) for p in ("mobile", "desktop", "web") for t in ("text", "icon")]
_lock = threading.Lock()


def load():
    cases = []
    for platform in ("mobile", "desktop", "web"):
        for c in json.loads((DATA / f"screenspot_{platform}_v2.json").read_text()):
            c["platform"] = platform
            cases.append(c)
    for i, c in enumerate(cases):
        c["i"] = i
    return cases  # 1,272 cases over 730 screenshots, bbox = [x, y, w, h] in original pixels


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


def run_one(i, dry=False, cases=None, out=DEV_LOG, pass_id="dev", annotate_mode="misses", window=None, size=None):
    """window=(x0, y0, cw, ch) in original px + size=(w, h): stage B of the zoom method. The crop is
    resized to `size` (stage A's sent size, so the same tokens) and the box is mapped back to the
    full screenshot before scoring. Everything else (prompt, question, scoring) is identical."""
    case = (cases or load())[i]
    orig = Image.open(DATA / "screenspotv2_image" / case["img_filename"])
    W, H = orig.size
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
    if window:
        rec.update(stage="B", window=list(window), window_frac=round(cw / W, 4))
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
    out_of_range = any(not 0 <= v <= 1 for v in b.values())  # edges outside the image Jev saw
    if window:  # crop fractions -> full-screenshot fractions
        rec["box_crop"] = b
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


def write(out, rec):
    out.parent.mkdir(exist_ok=True)
    with _lock, open(out, "a") as f:
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
             "tokens": 0, "t0": time.time(), "zoom_hits": 0, "zoom_scored": 0}
    prog = OUT / f"pass{pass_id}.progress.json"

    def progress(final=False):
        n, el = state["n"], time.time() - state["t0"]
        sc = state["ok"] + state["wrong_format"]
        tmp = prog.with_suffix(".tmp")
        tmp.write_text(json.dumps({
            "pass": pass_id, "updated": now(), "final": final, "done_this_run": n, "todo_this_run": len(todo),
            "already_done_before": len(done), "total_cases": len(cases),
            "scored_total": len(done) + sc, "hits_this_run": state["hits"],
            "running_acc_this_run": round(100 * state["hits"] / sc, 2) if sc else None,
            "ok": state["ok"], "wrong_format": state["wrong_format"], "infra_error": state["infra_error"],
            "spent_logged_total": round(state["spent"], 6), "input_tokens_this_run": state["tokens"],
            "median_latency_s": round(statistics.median(state["secs"]), 3) if state["secs"] else None,
            "elapsed_s": round(el, 1), "eta_s": round(el / n * (len(todo) - n), 1) if n else None,
            "stopped": stop.is_set(), "zoom": zoom, "zoom_scored_this_run": state["zoom_scored"],
            "zoom_running_acc_this_run": round(100 * state["zoom_hits"] / state["zoom_scored"], 2)
            if state["zoom_scored"] else None}))
        os.replace(tmp, prog)

    def stage_b(i, a):
        """Stage B for case i from stage A's scored record. A wrong_format A has no box to zoom on:
        the zoom answer is the same miss (copied, no cost)."""
        if a["status"] != "ok":
            z = {k: v for k, v in a.items() if k not in ("usage", "raw")}
            z.update({"pass": f"z{pass_id}", "stage": "B", "zoom_skipped": "stage A wrong_format", "ts": now()})
            write(zout, z)
            return z
        W, H = a["orig_size"]
        return run_one(i, cases=cases, out=zout, pass_id=f"z{pass_id}", annotate_mode=annotate_mode,
                       window=zoom_window(a, W, H), size=a["sent_size"])

    def job(i):
        if stop.is_set():
            return
        resumed = i in a_done
        if resumed:  # A scored before, only B is missing
            rec, new_cost = a_done[i], 0.0
        else:
            rec = run_one(i, cases=cases, out=out, pass_id=str(pass_id), annotate_mode=annotate_mode)
            new_cost = cost(rec)
        z = None
        if zoom and rec["status"] in ("ok", "wrong_format") and not rec.get("fatal") and not stop.is_set():
            z = stage_b(i, rec)
        with _lock:
            state["n"] += 1
            state["spent"] += new_cost + (cost(z) if z else 0.0)
            if z:
                if z["status"] in ("ok", "wrong_format"):
                    state["zoom_scored"] += 1
                    state["zoom_hits"] += 1 if z.get("hit") else 0
                if z.get("fatal"):
                    print(f"FATAL {z['error']} on #{i} (zoom): stopping the run", file=sys.stderr)
                    stop.set()
            if not resumed:  # the A counters are this run's A calls only
                state[rec["status"]] = state.get(rec["status"], 0) + 1
                state["hits"] += 1 if rec.get("hit") else 0
                if rec.get("seconds") is not None:
                    state["secs"].append(rec["seconds"])
            for x in ((rec,) if not resumed else ()) + ((z,) if z else ()):
                u = x.get("usage") if isinstance(x.get("usage"), dict) else {}
                state["tokens"] += u["input_tokens"] if isinstance(u.get("input_tokens"), int) else 0
            progress()
            if rec.get("fatal"):
                print(f"FATAL {rec['error']} on #{i}: stopping the run", file=sys.stderr)
                stop.set()
            if state["spent"] >= max_cost:
                print(f"cost cap reached (${state['spent']:.4f}): stopping", file=sys.stderr)
                stop.set()
            if state["n"] % 50 == 0:
                print(f"  {state['n']}/{len(todo)}  ${state['spent']:.4f}")

    progress()
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, todo))
    progress(final=True)
    after = jev.balance()
    if isinstance(before, float) and isinstance(after, float):
        print(f"key balance after: {after:.6f}  (billed this run: ${before - after:.6f}, "
              f"logged this run: ${state['spent'] - spent:.6f})")
    report(out)
    if zoom:
        report(zout)
        compare(out, zout)


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
    if len({m[0] for m in models}) > 1 or len({m[1] for m in models}) > 1:
        problems.append("mixed requested/resolved models")
    complete = not problems
    flag = "" if complete else f"  ** INCOMPLETE ({', '.join(problems)}): not a headline number **"
    lines = [f"# {pathlib.Path(path).name}" + flag, f"prompt versions: {dict(versions)}",
             f"models (requested, resolved, provider): {dict(models)}"]
    lines.append("| Platform | Type | n | scored | hits | acc | 95% CI |")
    lines.append("|---|---|---|---|---|---|---|")
    cell_acc = []
    for p, t in CELLS:
        idx = [c["i"] for c in cases if c["platform"] == p and c["data_type"] == t]
        hits = sum(1 for i in idx if scored.get(i, {}).get("hit"))
        acc = hits / len(idx)
        cell_acc.append(acc)
        lo, hi = wilson(hits, len(idx))
        lines.append(f"| {p} | {t} | {len(idx)} | {sum(1 for i in idx if i in scored)} | {hits} | {100 * acc:.2f} "
                     f"| {lo:.1f}-{hi:.1f} |")
    hits = sum(1 for r in scored.values() if r["hit"])
    lines.append("")
    lo, hi = wilson(hits, n_total)
    lines.append(f"Avg (micro, hits / {n_total}, official strict rule, as published v2 tables): "
                 f"{100 * hits / n_total:.2f}  (95% Wilson CI {lo:.1f}-{hi:.1f})" + flag)
    tol = sum(1 for r in scored.values() if r.get("hit_tolerant"))
    lines.append(f"Avg (micro, 1e-9 edge tolerance): {100 * tol / n_total:.2f}  "
                 f"({sum(1 for r in scored.values() if bool(r.get('hit_tolerant')) != bool(r['hit']))} cases differ)" + flag)
    lines.append(f"Avg (macro, mean of 6 cells): {100 * statistics.mean(cell_acc):.2f}" + flag)
    ok = [r for r in scored.values() if r["status"] == "ok"]
    lines.append(f"scored {len(scored)}/{n_total}, wrong_format {len(scored) - len(ok)}, infra_error {len(infra)}, "
                 f"not run {missing}, degenerate boxes {sum(1 for r in ok if r['degenerate'])}, "
                 f"centre on a truth edge {sum(1 for r in ok if r.get('on_edge'))}, "
                 f"edges outside [0,1] {sum(1 for r in ok if r.get('out_of_range'))}")
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


def compare(p1, p2):
    a, b = latest(read(p1)), latest(read(p2))
    sa = {i: r for i, r in a.items() if r["status"] in ("ok", "wrong_format")}
    sb = {i: r for i, r in b.items() if r["status"] in ("ok", "wrong_format")}
    n = len(load())
    if len(sa) != n or len(sb) != n:
        print(f"INCOMPLETE: {len(sa)} and {len(sb)} of {n} scored; finish both passes first")
        return None
    agree = sum(1 for i in sa if bool(sa[i]["hit"]) == bool(sb[i]["hit"]))
    up = sum(1 for i in sa if not sa[i]["hit"] and sb[i]["hit"])
    down = sum(1 for i in sa if sa[i]["hit"] and not sb[i]["hit"])
    m1 = 100 * sum(1 for r in sa.values() if r["hit"]) / n
    m2 = 100 * sum(1 for r in sb.values() if r["hit"]) / n
    print(f"pass A {m1:.2f}  pass B {m2:.2f}  mean {(m1 + m2) / 2:.2f} +- {abs(m1 - m2) / 2:.2f}")
    print(f"case-level agreement {agree}/{n} ({100 * agree / n:.1f}%), miss->hit {up}, hit->miss {down}")
    return agree


if __name__ == "__main__":
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
    args = ap.parse_args()
    if args.cmd == "run":
        run_all(args.pass_id, args.workers, args.max_cost, args.limit, args.annotate, args.zoom)
    elif args.cmd == "compare":
        compare(args.pass_a, args.pass_b)
    else:
        report(args.path)
