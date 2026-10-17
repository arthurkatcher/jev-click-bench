"""Post-run checks for ScreenSpot-Pro run 2 (A2 raw + B 2x zoom). Read-only, offline, no API.
1. Integrity: counts, statuses, code_rev, model, window config.
2. Independent official re-score from the raw responses (B: crop box mapped back through the window).
3. Declared diagnostics of the frozen 2x zoom (reported, never used to pick a setting):
   a. ceiling: when A2 missed, was the target inside B's window?
   b. grid: targets smaller than one answer step, in A's view vs in B's view.
"""
import json, glob, collections, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
import screenspot as ss

ss.use("pro")
R = ss.OUT
raw = {}
for f in sorted(glob.glob(str(ss.DATA / "annotations" / "*.json"))):
    for c in json.load(open(f)):
        raw[c["id"]] = c


def official(sample, point):  # ScreenSpot-Pro eval_sample_positive_gt, verbatim logic
    bbox = sample["bbox"]; img_size = sample["img_size"]
    bbox = [bbox[0] / img_size[0], bbox[1] / img_size[1], bbox[2] / img_size[0], bbox[3] / img_size[1]]
    if point is None:
        return "wrong_format"
    return "correct" if (bbox[0] <= point[0] <= bbox[2]) and (bbox[1] <= point[1] <= bbox[3]) else "wrong"


def load(name):
    by = {}
    for l in open(R / name):
        if l.strip():
            r = json.loads(l); by[r["i"]] = r
    return by


A1, A2, B = load("pass1.jsonl"), load("pass2.jsonl"), load("zoom2.jsonl")
print("== 1. integrity")
for n, d in (("A1", A1), ("A2", A2), ("B", B)):
    print(f"{n}: {len(d)} cases, status {dict(collections.Counter(r['status'] for r in d.values()))}, "
          f"code_rev {dict(collections.Counter(r.get('code_rev') for r in d.values()))}, "
          f"model {dict(collections.Counter(r.get('model') for r in d.values()))}")
print("B zoom config:", dict(collections.Counter((r.get("zoom_f"), r.get("zoom_margin")) for r in B.values())))
assert len(A2) == len(B) == 1581 and all(B[i]["case_id"] == A2[i]["case_id"] for i in B)
# B's window must be the frozen rule applied to A2's own box
bad_win = [i for i in B if list(ss.zoom_window(A2[i], *A2[i]["orig_size"])) != B[i]["window"]]
print("B windows recomputed from A2's box with the frozen rule: mismatches", len(bad_win))
print("B sent size == A2 sent size:", sum(B[i]["sent_size"] == A2[i]["sent_size"] for i in B), "/ 1581")

print("\n== 2. official re-score from raw responses")
for n, d in (("A2", A2), ("B", B)):
    hits = diff = 0
    for i, r in d.items():
        b = r["raw"]["answers"]["target"]["box"]
        if n == "B":
            W, H = r["orig_size"]; x0, y0, cw, ch = r["window"]
            if (x0, y0, cw, ch) != (0, 0, W, H):
                b = {"left": (x0 + b["left"] * cw) / W, "right": (x0 + b["right"] * cw) / W,
                     "top": (y0 + b["top"] * ch) / H, "bottom": (y0 + b["bottom"] * ch) / H}
        pt = [(b["left"] + b["right"]) / 2, (b["top"] + b["bottom"]) / 2]
        ok = official(raw[r["case_id"]], pt) == "correct"
        hits += ok; diff += ok != r["hit"]
    print(f"{n}: {hits}/1581 = {100 * hits / 1581:.2f}%, disagreements with recorded hit: {diff}")

print("\n== 3a. ceiling: target inside B's window (declared diagnostic)")
def gt_in_window(i, whole):
    x0, y0, cw, ch = B[i]["window"]
    x1, y1, x2, y2 = raw[B[i]["case_id"]]["bbox"]  # original pixels, [x1, y1, x2, y2]
    if whole:
        return x1 >= x0 and y1 >= y0 and x2 <= x0 + cw and y2 <= y0 + ch
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    return x0 <= cx <= x0 + cw and y0 <= cy <= y0 + ch
miss = [i for i in A2 if not A2[i]["hit"]]
hitA = [i for i in A2 if A2[i]["hit"]]
for lab, sel in (("A2 misses", miss), ("A2 hits", hitA)):
    c_in = sum(gt_in_window(i, False) for i in sel); w_in = sum(gt_in_window(i, True) for i in sel)
    fixed = sum(1 for i in sel if B[i]["hit"])
    print(f"{lab}: n={len(sel)}, target centre in window {c_in} ({100 * c_in / len(sel):.1f}%), "
          f"whole target in window {w_in} ({100 * w_in / len(sel):.1f}%), B hit {fixed}")
fixable = [i for i in miss if gt_in_window(i, False)]
print(f"A2 misses with the target in view: {len(fixable)}, of which B fixed "
      f"{sum(1 for i in fixable if B[i]['hit'])} ({100 * sum(1 for i in fixable if B[i]['hit']) / max(1, len(fixable)):.1f}%)")
out_view = [i for i in miss if not gt_in_window(i, False)]
print(f"A2 misses with the target outside the window (B cannot fix by construction): {len(out_view)}, "
      f"B hit anyway {sum(1 for i in out_view if B[i]['hit'])}")

print("\n== 3b. grid: targets smaller than one 0.01 answer step on a side (declared diagnostic)")
def sub_step(i, k):
    c = raw[B[i]["case_id"]]; W, H = c["img_size"]; x1, y1, x2, y2 = c["bbox"]
    return (x2 - x1) / W < 0.01 * k or (y2 - y1) / H < 0.01 * k
nA = sum(sub_step(i, 1.0) for i in B)
nB = sum(sub_step(i, B[i]["window_frac"]) for i in B)
print(f"in A's view (full screen): {nA}/1581; in B's view (step = 0.01 x window_frac): {nB}/1581")
for lab, k in (("sub-step in A", True), ("not sub-step in A", False)):
    sel = [i for i in B if sub_step(i, 1.0) == k]
    a = sum(A2[i]["hit"] for i in sel); b = sum(B[i]["hit"] for i in sel)
    print(f"  {lab}: n={len(sel)}, A2 {100 * a / len(sel):.1f}%, B {100 * b / len(sel):.1f}%")
wf = collections.Counter("half (2x)" if r["window_frac"] <= 0.51 else ("full screen" if r["window_frac"] >= 0.9999 else "widened")
                         for r in B.values())
print("window types:", dict(wf))
