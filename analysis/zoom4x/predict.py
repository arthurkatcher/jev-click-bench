"""Stage C (4x) prediction, written and committed before any stage-C call. Offline, no API.

Stage C = the frozen 2x zoom step once more, on Pro run 2's stage-B answers (screenspot.py zoom4x):
half of each side of B's window around B's box, so each target is 4x its size in A's image.
Designed after seeing Pro run 2, so it is a labelled extra next to 42.76, never in its place.

The model replays the 2x step one level up. In A2 -> B, whether B hit depended on whether A2 had hit
and on the target's size in B's image. Those rates (cases with the target centre inside B's window)
are applied to B -> C: B's outcome is the earlier one, the size is the target's size in C's image,
and a target centre outside C's window is a miss. Cross-check: the size curve alone, tested out of
sample on the 2x step (A1's raw curve by size, applied to B's sizes, against the real B).
  python3 analysis/zoom4x/predict.py > analysis/zoom4x/prediction.txt
"""
import collections, math, random, statistics, sys
sys.path.insert(0, "/home/bionics/jev-screenspot")
import screenspot as ss

ss.use("pro")
CASES = ss.load()
A1, A2, B = (ss.latest(ss.read(ss.OUT / f)) for f in ("pass1.jsonl", "pass2.jsonl", "zoom2.jsonl"))
BINS = (0, 10, 20, 30, 45, 60, 80, math.inf)  # the audit's size bins; 80 px and up pooled (few A2 -> B cases are bigger)


def bin_of(px):
    return next(k for k in range(len(BINS) - 1) if px < BINS[k + 1])


def label(k):
    return f"{BINS[k]}-{BINS[k + 1]} px" if BINS[k + 1] < math.inf else f"{BINS[k]}+ px"


def size(c, sent_w, win_w):  # square root of the key box area, in px of the image Jev saw
    return math.sqrt(c["bbox"][2] * c["bbox"][3]) * sent_w / win_w


def centre_in(c, win):
    x0, y0, cw, ch = win
    gx, gy, gw, gh = c["bbox"]
    return x0 <= gx + gw / 2 <= x0 + cw and y0 <= gy + gh / 2 <= y0 + ch


rows = []
for c in CASES:
    i, W, sent_w = c["i"], c["img_size"][0], B[c["i"]]["sent_size"][0]
    assert B[i]["sent_size"] == A2[i]["sent_size"]
    win_b, win_c = B[i]["window"], ss.zoom_again_window(B[i])
    rows.append({"a1": A1[i]["hit"], "a2": A2[i]["hit"], "b": B[i]["hit"], "sA": size(c, sent_w, W),
                 "sB": size(c, sent_w, win_b[2]), "sC": size(c, sent_w, win_c[2]), "inB": centre_in(c, win_b),
                 "inC": centre_in(c, win_c), "kC": win_c[2] / win_b[2], "zB": sent_w / win_b[2], "zC": sent_w / win_c[2]})


def table(pairs):  # [(key, hit)] -> {key: [hits, n]}
    t = collections.defaultdict(lambda: [0, 0])
    for key, hit in pairs:
        t[key][0] += hit
        t[key][1] += 1
    return t


def rate(t, key):
    k, n = t[key]
    assert n >= 5, f"too few cases behind {key}: {n}"
    return k / n


step = lambda rs: table(((r["a2"], bin_of(r["sB"])), r["b"]) for r in rs if r["inB"])  # the 2x step
T = step(rows)
p_t = lambda t, r: rate(t, (r["b"], bin_of(r["sC"]))) if r["inC"] else 0.0
n_hit, n_miss = sum(r["b"] for r in rows), sum(not r["b"] for r in rows)
fixes = sum(p_t(T, r) for r in rows if not r["b"])
keeps = sum(p_t(T, r) for r in rows if r["b"])
point = 100 * (fixes + keeps) / len(rows)

# 95% predictive range: resample the 2x step's cases (rate uncertainty), then draw C's outcomes
rng = random.Random(20261017)
sims = []
for _ in range(2000):
    t = step(rng.choice(rows) for _ in rows)
    sims.append(100 * sum(rng.random() < p_t(t, r) for r in rows) / len(rows))
sims.sort()
lo, hi = sims[49], sims[1949]

S = table((bin_of(r["sB"]), r["b"]) for r in rows if r["inB"])  # size alone: B's curve, target in view
size_alone = 100 * sum(rate(S, bin_of(r["sC"])) for r in rows if r["inC"]) / len(rows)
R = table((bin_of(r["sA"]), r["a1"]) for r in rows)  # A1's raw curve, for the out-of-sample test
raw_test = 100 * sum(R[bin_of(r["sB"])][0] / R[bin_of(r["sB"])][1] for r in rows if r["inB"]) / len(rows)

kinds = collections.Counter("half of B's side" if abs(r["kC"] - 0.5) < 0.01 else "B's whole window (big box)"
                            if r["kC"] > 0.999 else "between (box needs more)" for r in rows)
present = sorted(p.name for p in ss.OUT.glob("zoom4x*")) or "none"
med = lambda k: statistics.median(r[k] for r in rows)
print(f"""# Stage C (4x) prediction, registered before any stage-C call

Code rev when written: {ss.CODE_REV}. Stage-C result files present: {present}.
Stage C is the frozen 2x rule applied once more, inside B's window around B's answer. It was designed after seeing Pro run 2, so it is a labelled extra next to 42.76, never in its place.

## What C's crops look like (exact, from B's answers)
- C's window: {', '.join(f'{k} {v}' for k, v in kinds.most_common())}.
- Median target size in the image Jev sees: A {med('sA'):.1f} px, B {med('sB'):.1f} px, C {med('sC'):.1f} px.
- Blown-up crops (window smaller than the image sent): B {sum(r['zB'] > 1 for r in rows)}, C {sum(r['zC'] > 1 for r in rows)} of {len(rows)}. Blow-up factor: B up to {max(r['zB'] for r in rows):.2f}x, C median {med('zC'):.2f}x, up to {max(r['zC'] for r in rows):.2f}x, over 2x in {sum(r['zC'] > 2 for r in rows)} cases. On the 2x step, blown-up crops gained as much as the others (`AUDIT-pro-run2.md` section 4); nothing has tested factors over {max(r['zB'] for r in rows):.1f}x yet.
- Ceiling: the target centre is inside C's window in {sum(r['inC'] for r in rows if r['b'])} of B's {n_hit} hits and {sum(r['inC'] for r in rows if not r['b'])} of its {n_miss} misses, so C can reach about {100 * sum(r['inC'] for r in rows) / len(rows):.1f}%.

## What the 2x step did, by target size in B's image (target centre in B's window)
| Size in B's image | A2 hit: B kept | A2 miss: B fixed |
|---|---|---|""")
for k in range(len(BINS) - 1):
    cell = lambda prev: f"{100 * T[(prev, k)][0] / T[(prev, k)][1]:.0f}% (n={T[(prev, k)][1]})" if T[(prev, k)][1] else "-"
    print(f"| {label(k)} | {cell(True)} | {cell(False)} |")
print(f"""
A target A2 missed was later hit about as often as a fresh raw target of the same size (the raw curve in `AUDIT-pro-run2.md` section 4: 17.8% at 20-30 px, 39.4% at 30-45, 47.7% at 45-60, 66.7% at 60-80). So a miss at half the size says little once the target doubles. A hit carries over more strongly.

## Prediction
- **C = {point:.1f}%** (95% predictive range {lo:.1f}-{hi:.1f}%), from the 2x step's rates replayed on B's answers at C's sizes.
- That is about {fixes:.0f} of B's {n_miss} misses fixed and {n_hit - keeps:.0f} of its {n_hit} hits broken.
- Cross-check, size alone (B's hit rate by size, target in view, ignoring the earlier answer): {size_alone:.1f}%.
- How good is size alone? Tested on the 2x step, A1's raw size curve applied to B's sizes gave {raw_test:.1f}% against the real {100 * n_hit / len(rows):.2f}%. It under-predicted the 2x step by {100 * n_hit / len(rows) - raw_test:.1f} pp, so size is most of the zoom effect, not all of it.

## How to read the result
- Inside the range: the second doubling works like the first.
- Below it: 4x costs something 2x did not. Candidates: blown-up crops, a crop of 1/16 of the screen that loses context, or B's misses being harder than their size says.
- Above it: unexpected. Check the run before believing it.""")
