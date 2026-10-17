"""Stage C (4x) results. Offline, read-only, no API. Run after `screenspot.py --bench pro zoom4x`.
1. Integrity: records, statuses, code rev, model, C's window re-derived from B's answer.
2. Independent official re-score from the raw responses (C's crop box mapped back through C's window).
3. B -> C paired: fixed / broken, exact McNemar, 95% bootstrap CI of the gain.
4. Against the registered prediction (prediction.txt, commit 5649be5).
5. Does the second doubling work like the first? Hit rate by target size in the image Jev saw.
6. Where: group, text/icon, window type, blow-up factor. 7. Cost and latency per click.
  python3 analysis/zoom4x/analyze.py [results/pro/zoom4x.jsonl] > analysis/zoom4x/results.txt
"""
import collections, json, math, random, statistics, sys
sys.path.insert(0, "/home/bionics/jev-screenspot")
import screenspot as ss

ss.use("pro")
CASES = ss.load()
path = sys.argv[1] if len(sys.argv) > 1 else str(ss.OUT / "zoom4x.jsonl")
A2, B = ss.latest(ss.read(ss.OUT / "pass2.jsonl")), ss.latest(ss.read(ss.OUT / "zoom2.jsonl"))
recs = ss.read(path)
C = ss.latest(recs)
ids = sorted(C)
N = len(ids)
raw = {}
for f in sorted((ss.DATA / "annotations").glob("*.json")):
    for c in json.loads(f.read_text()):
        raw[c["id"]] = c


def official(c, point):  # ScreenSpot-Pro eval_sample_positive_gt on the raw annotation
    bbox, img_size = raw[c["id"]]["bbox"], raw[c["id"]]["img_size"]
    bbox = [bbox[0] / img_size[0], bbox[1] / img_size[1], bbox[2] / img_size[0], bbox[3] / img_size[1]]
    return (bbox[0] <= point[0] <= bbox[2]) and (bbox[1] <= point[1] <= bbox[3])


def pct(k, n):
    return f"{100 * k / n:.2f}" if n else "-"


print(f"# Stage C (4x) results: {path.split('/')[-1]}")
print(f"\n## 1. Integrity\n- {N} cases of {len(CASES)}" + ("" if N == len(CASES) else "  ** PARTIAL **")
      + f", {len(recs)} records, status {dict(collections.Counter(C[i]['status'] for i in ids))}")
print(f"- code rev {dict(collections.Counter(C[i].get('code_rev') for i in ids))}, "
      f"resolved model {dict(collections.Counter(C[i].get('model') for i in ids))}")
for i in ids:
    r = C[i]
    assert r["status"] in ("ok", "wrong_format"), (i, r["status"])
    assert r["stage"] == "C" and r["parent_window"] == B[i]["window"], i
    if r["status"] == "ok":
        assert r["window"] == list(ss.zoom_again_window(B[i])) and r["sent_size"] == B[i]["sent_size"], i
print("- every C window = the frozen rule on B's answer, inside B's window, sent at A's size")

# 2. independent re-score from the raw response: the method's own arithmetic (box edges mapped back
#    through the window, then the centre), then the official rule on the raw annotation
agree, ties = 0, []
for i in ids:
    r, c = C[i], CASES[i]
    if r["status"] != "ok":
        agree += r["hit"] is False
        continue
    b = r["raw"]["answers"]["target"]["box"]
    x0, y0, cw, ch = r["window"]
    W, H = r["orig_size"]
    l, rt, t, bo = (x0 + b["left"] * cw) / W, (x0 + b["right"] * cw) / W, (y0 + b["top"] * ch) / H, (y0 + b["bottom"] * ch) / H
    agree += official(c, ((l + rt) / 2, (t + bo) / 2)) == r["hit"]
    centre_first = ((x0 + (b["left"] + b["right"]) / 2 * cw) / W, (y0 + (b["top"] + b["bottom"]) / 2 * ch) / H)
    if official(c, centre_first) != r["hit"]:  # a click exactly on a key edge: float order decides
        ties.append(i)
print(f"\n## 2. Official re-score from the raw responses\n- agrees with the run on {agree} of {N}")
print(f"- exact-edge ties: {len(ties)} ({', '.join(f'#{i}' for i in ties) or 'none'}). The click sits on the key's edge; "
      f"averaging before mapping back would put it on the edge (a hit), the method's order puts it one float step "
      f"outside (a miss). They are the cases the 1e-9 tolerance score counts; the headline stays strict.")

# 3. B -> C paired
hC = {i: bool(C[i]["hit"]) for i in ids}
hB = {i: bool(B[i]["hit"]) for i in ids}
hA = {i: bool(A2[i]["hit"]) for i in ids}
kC, kB, kA = sum(hC.values()), sum(hB.values()), sum(hA.values())
fixed = [i for i in ids if hC[i] and not hB[i]]
broken = [i for i in ids if hB[i] and not hC[i]]
lo, hi = ss.wilson(kC, N)
rng = random.Random(20261017)
boot = sorted(sum(hC[j] - hB[j] for j in (rng.choice(ids) for _ in ids)) * 100 / N for _ in range(2000))
text = [i for i in ids if CASES[i]["data_type"] == "text"]
icon = [i for i in ids if CASES[i]["data_type"] == "icon"]
print(f"""
## 3. B -> C on the same cases
| | Raw A2 | 2x zoom B | 4x zoom C |
|---|---|---|---|
| Accuracy (hits / {N}) | {pct(kA, N)} | {pct(kB, N)} | {pct(kC, N)} |
| Text (n={len(text)}) | {pct(sum(hA[i] for i in text), len(text))} | {pct(sum(hB[i] for i in text), len(text))} | {pct(sum(hC[i] for i in text), len(text))} |
| Icon (n={len(icon)}) | {pct(sum(hA[i] for i in icon), len(icon))} | {pct(sum(hB[i] for i in icon), len(icon))} | {pct(sum(hC[i] for i in icon), len(icon))} |

- C = {pct(kC, N)}% (95% Wilson CI {lo:.1f}-{hi:.1f}), B = {pct(kB, N)}%: {100 * (kC - kB) / N:+.2f} pp (95% bootstrap CI {boot[49]:+.2f} to {boot[1949]:+.2f}).
- Fixed {len(fixed)}, broken {len(broken)}; exact McNemar p = {ss.mcnemar(len(fixed), len(broken)):.2g}.
- Both hit {sum(hB[i] and hC[i] for i in ids)}, both missed {sum(not hB[i] and not hC[i] for i in ids)}.""")

# 4. against the registered prediction (same model as predict.py, recomputed here)
BINS = (0, 10, 20, 30, 45, 60, 80, math.inf)
bin_of = lambda px: next(k for k in range(len(BINS) - 1) if px < BINS[k + 1])
label = lambda k: f"{BINS[k]}-{BINS[k + 1]} px" if BINS[k + 1] < math.inf else f"{BINS[k]}+ px"
size = lambda c, sent_w, win_w: math.sqrt(c["bbox"][2] * c["bbox"][3]) * sent_w / win_w


def centre_in(c, win):
    x0, y0, cw, ch = win
    gx, gy, gw, gh = c["bbox"]
    return x0 <= gx + gw / 2 <= x0 + cw and y0 <= gy + gh / 2 <= y0 + ch


info = {}
for c in CASES:
    i, W, sw = c["i"], c["img_size"][0], B[c["i"]]["sent_size"][0]
    wb, wc = B[i]["window"], ss.zoom_again_window(B[i])
    info[i] = {"sA": size(c, sw, W), "sB": size(c, sw, wb[2]), "sC": size(c, sw, wc[2]), "inB": centre_in(c, wb),
               "inC": centre_in(c, wc), "kC": wc[2] / wb[2], "zC": sw / wc[2]}
T = collections.defaultdict(lambda: [0, 0])  # the 2x step's rates, all 1,581 cases, as in predict.py
for i in range(len(CASES)):
    if info[i]["inB"]:
        T[(bool(A2[i]["hit"]), bin_of(info[i]["sB"]))][0] += bool(B[i]["hit"])
        T[(bool(A2[i]["hit"]), bin_of(info[i]["sB"]))][1] += 1
p = {i: (T[(hB[i], bin_of(info[i]["sC"]))][0] / T[(hB[i], bin_of(info[i]["sC"]))][1] if info[i]["inC"] else 0.0) for i in ids}
print(f"""
## 4. Against the registered prediction (63.2%, range 59.7-66.2%, written before any stage-C call)
- Result {pct(kC, N)}% vs model {100 * sum(p.values()) / N:.1f}% on these {N} cases: {'inside' if 59.7 <= 100 * kC / N <= 66.2 else 'OUTSIDE'} the registered range.
- Fixes {len(fixed)} vs {sum(p[i] for i in ids if not hB[i]):.0f} expected; breaks {len(broken)} vs {sum(1 - p[i] for i in ids if hB[i]):.0f} expected.
- Ceiling: target centre in C's window in {sum(info[i]['inC'] for i in ids)}; C hit {sum(hC[i] for i in ids if not info[i]['inC'])} of the {sum(not info[i]['inC'] for i in ids)} without it.

| Size in C's image | B missed: C fixed | expected | B hit: C kept | expected |
|---|---|---|---|---|""")
for k in range(len(BINS) - 1):
    row = []
    for prev in (False, True):
        sel = [i for i in ids if hB[i] == prev and info[i]["inC"] and bin_of(info[i]["sC"]) == k]
        row += [f"{pct(sum(hC[i] for i in sel), len(sel))}% (n={len(sel)})" if sel else "-",
                f"{100 * statistics.mean(p[i] for i in sel):.0f}%" if sel else "-"]
    print(f"| {label(k)} | " + " | ".join(row) + " |")

# 5. the size curve, stage by stage: hit rate by target size in the image Jev saw (target centre in view)
print("\n## 5. Hit rate by target size in the image Jev saw, each stage (target centre in that stage's view)")
print("| Size | Raw A2 | 2x zoom B | 4x zoom C |\n|---|---|---|---|")
for k in range(len(BINS) - 1):
    cells = []
    for hits, s, view in ((hA, "sA", None), (hB, "sB", "inB"), (hC, "sC", "inC")):
        sel = [i for i in ids if bin_of(info[i][s]) == k and (view is None or info[i][view])]
        cells.append(f"{pct(sum(hits[i] for i in sel), len(sel))} (n={len(sel)})" if sel else "-")
    print(f"| {label(k)} | " + " | ".join(cells) + " |")

# 6. where
print("\n## 6. Where\n| Group | n | B % | C % | fixed | broken |\n|---|---|---|---|---|---|")
for g in ss.PRO_GROUPS:
    sel = [i for i in ids if CASES[i]["group"] == g]
    print(f"| {g} | {len(sel)} | {pct(sum(hB[i] for i in sel), len(sel))} | {pct(sum(hC[i] for i in sel), len(sel))} "
          f"| {sum(hC[i] and not hB[i] for i in sel)} | {sum(hB[i] and not hC[i] for i in sel)} |")
kind = lambda i: "half of B" if abs(info[i]["kC"] - 0.5) < 0.01 else "B's whole window" if info[i]["kC"] > 0.999 else "widened"
blow = lambda i: next(f"{a}-{b}x" for a, b in ((0, 1), (1, 1.5), (1.5, 2), (2, 2.5), (2.5, 9)) if info[i]["zC"] < b)
for name, key in (("C window", kind), ("Blow-up of C's crop", blow)):
    print(f"\n| {name} | n | B % | C % | fixed | broken |\n|---|---|---|---|---|---|")
    for v in sorted({key(i) for i in ids}):
        sel = [i for i in ids if key(i) == v]
        print(f"| {v} | {len(sel)} | {pct(sum(hB[i] for i in sel), len(sel))} | {pct(sum(hC[i] for i in sel), len(sel))} "
              f"| {sum(hC[i] and not hB[i] for i in sel)} | {sum(hB[i] and not hC[i] for i in sel)} |")

# 7. cost and latency
cost = sum(ss.cost(r) for r in recs)
tok = sum(r["usage"]["input_tokens"] for r in recs if isinstance(r.get("usage"), dict) and isinstance(r["usage"].get("input_tokens"), int))
med = lambda d: statistics.median(d[i]["seconds"] for i in ids if d[i].get("seconds") is not None)
cost_ab = sum(ss.cost(r) for f in ("pass2.jsonl", "zoom2.jsonl") for r in ss.read(ss.OUT / f))
print(f"""
## 7. Cost and latency
- Stage C: ${cost:.6f} logged ({len(recs)} records), {tok:,} input tokens, median {med(C):.3f}s per call.
- Per click: A + B + C = 3 calls in a row, median {med(A2) + med(B) + med(C):.2f}s (A {med(A2):.2f} + B {med(B):.2f} + C {med(C):.2f}).
- Whole 4x method on Pro: run 2 (A2 + B) ${cost_ab:.4f} + C ${cost:.4f} = ${cost_ab + cost:.4f}, so ${(cost_ab + cost) / len(CASES) * 1000:.3f} per 1,000 clicks.""")

# 8. which of B's misses C fixed, by the label audit's by-eye class (analysis/labels_audit_pro.py, run silently)
import contextlib, io, runpy
with contextlib.redirect_stdout(io.StringIO()):
    LA = runpy.run_path(str(ss.ROOT / "analysis" / "labels_audit_pro.py"))
code, KIND = LA["code"], LA["KIND"]
print("\n## 8. B's misses by the label audit's class: how many C fixed\n| Class (by eye, B's answer) | B misses | C fixed | % |\n|---|---|---|---|")
for k, cs in KIND.items():
    sel = [i for i in ids if not hB[i] and code.get(i) in cs]
    print(f"| {k} | {len(sel)} | {sum(hC[i] for i in sel)} | {pct(sum(hC[i] for i in sel), len(sel))} |")
for k in ("MODEL", "NEIGHBOUR", "PRECISION", "WIDE", "EDGE"):
    sel = [i for i in ids if not hB[i] and code.get(i) == k]
    print(f"| . {k} | {len(sel)} | {sum(hC[i] for i in sel)} | {pct(sum(hC[i] for i in sel), len(sel))} |")
inview = [i for i in ids if not hB[i] and info[i]["inC"]]
for k, cs in (("wrong element", KIND["wrong element"]), ("click off", KIND["click off"])):
    sel = [i for i in inview if code.get(i) in cs]
    print(f"- {k}, target centre in C's window: {len(sel)}, C fixed {sum(hC[i] for i in sel)} ({pct(sum(hC[i] for i in sel), len(sel))}%)")
