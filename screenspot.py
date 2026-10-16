"""ScreenSpot-v2 x Jev box. Screenshot + instruction -> one box question -> click the box centre -> hit?

Scoring = the standard ScreenSpot rule (SeeClick pretrain/screenspot_test.py, ScreenSpot-Pro
eval_sample_positive_gt): hit if the box centre is inside the ground-truth bbox, edges inclusive.
Every case gets a record. A malformed answer is a miss ("wrong_format"), like the official evals.
An infrastructure failure ("infra_error") is not scored: it is retried by re-running the pass.

  python3 screenspot.py 0 [--dry]               # one case, dev log results/runs.jsonl
  python3 screenspot.py run --pass 1 [--workers 4] [--max-cost 0.30] [--limit N]
  python3 screenspot.py report results/pass1.jsonl
  python3 screenspot.py compare results/pass1.jsonl results/pass2.jsonl
"""
import argparse, collections, datetime, hashlib, json, math, pathlib, statistics, sys, threading
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


def run_one(i, dry=False, cases=None, out=DEV_LOG, pass_id="dev", annotate_mode="misses"):
    case = (cases or load())[i]
    orig = Image.open(DATA / "screenspotv2_image" / case["img_filename"])
    W, H = orig.size
    img, scale = jev.fit(orig)
    state, questions, text = request(case, img)
    x, y, w, h = case["bbox"]
    gt = [x / W, y / H, (x + w) / W, (y + h) / H]  # normalized x1, y1, x2, y2 (SeeClick conversion)
    rec = {"pass": pass_id, "i": i, "file": case["img_filename"], "platform": case["platform"],
           "source": case["data_source"], "type": case["data_type"], "instruction": case["instruction"],
           "instructions_sent": text, "prompt_version": PROMPT_VERSION, "template_hash": TEMPLATE_HASH,
           "requested_model": jev.MODEL, "orig_size": [W, H], "sent_size": list(img.size), "gt": gt}
    if dry:
        print(json.dumps(rec, indent=1), "\nquestions:", json.dumps(questions),
              f"\nimage part: {len(state[1]['image_url']['url']) // 1024} KB base64")
        return rec

    rec["ts"] = now()
    try:
        resp, secs, attempts = jev.decide(state, questions)
    except jev.JevError as e:
        rec.update(status="infra_error", hit=None, error=str(e), http_status=e.status,
                   error_body=e.body, attempts=e.attempts, fatal=e.fatal)
        write(out, rec)
        return rec
    except Exception as e:  # backstop: never let one case abort a pass
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
    point = [(b["left"] + b["right"]) / 2, (b["top"] + b["bottom"]) / 2]
    # hit = the official rule exactly (SeeClick / ScreenSpot-Pro: strict float compare, edges inclusive).
    # hit_tolerant adds 1e-9 so float noise on a 2-decimal centre that sits exactly on an edge cannot
    # flip it; reported next to the headline, never instead of it.
    hit = inside(point, gt)
    hit_tolerant = inside(point, gt, EPS)
    on_edge = any(abs(point[k % 2] - gt[k]) < EPS for k in range(4))
    # Official rule scores the centre whatever the box shape or range; both are flagged and counted.
    degenerate = b["right"] <= b["left"] or b["bottom"] <= b["top"]
    out_of_range = any(not 0 <= v <= 1 for v in b.values())
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


def run_all(pass_id, workers=4, max_cost=0.30, limit=None, annotate_mode="misses"):
    cases = load()
    out = OUT / f"pass{pass_id}.jsonl"
    done = {i for i, r in latest(read(out)).items() if r["status"] in ("ok", "wrong_format")} if out.exists() else set()
    spent = sum(cost(r) for r in read(out)) if out.exists() else 0.0
    todo = [c["i"] for c in cases if c["i"] not in done][:limit]
    print(f"pass {pass_id}: {len(done)} done, {len(todo)} to run, ${spent:.4f} logged so far, cap ${max_cost}")
    before = jev.balance()
    print(f"key balance before: {before}")
    stop = threading.Event()
    state = {"spent": spent, "n": 0}

    def job(i):
        if stop.is_set():
            return
        rec = run_one(i, cases=cases, out=out, pass_id=str(pass_id), annotate_mode=annotate_mode)
        with _lock:
            state["n"] += 1
            state["spent"] += cost(rec)
            if rec.get("fatal"):
                print(f"FATAL {rec['error']} on #{i}: stopping the run", file=sys.stderr)
                stop.set()
            if state["spent"] >= max_cost:
                print(f"cost cap reached (${state['spent']:.4f}): stopping", file=sys.stderr)
                stop.set()
            if state["n"] % 50 == 0:
                print(f"  {state['n']}/{len(todo)}  ${state['spent']:.4f}")

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, todo))
    after = jev.balance()
    if isinstance(before, float) and isinstance(after, float):
        print(f"key balance after: {after:.6f}  (billed this run: ${before - after:.6f}, "
              f"logged this run: ${state['spent'] - spent:.6f})")
    report(out)


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
    rp = sub.add_parser("report")
    rp.add_argument("path")
    cp = sub.add_parser("compare")
    cp.add_argument("pass_a")
    cp.add_argument("pass_b")
    args = ap.parse_args()
    if args.cmd == "run":
        run_all(args.pass_id, args.workers, args.max_cost, args.limit, args.annotate)
    elif args.cmd == "compare":
        compare(args.pass_a, args.pass_b)
    else:
        report(args.path)
