"""Deep audit of pass 1 (A1), pass 2 (A2) and zoom stage B (B), straight from the raw records.
Every integrity check is an assert; every number in analysis/AUDIT-run2.md is printed here.
  python3 analysis/audit_run2.py              # all numbers, about a minute
  python3 analysis/audit_run2.py --images     # + rebuild all 2,544 sent images and match their payload sizes
  python3 analysis/audit_run2.py --balance    # + read the key balance (free GET, no spend)"""
import ast, collections, concurrent.futures as cf, datetime, math, pathlib, random, statistics as st, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image
import jev
import screenspot as ss

N = 1272
CASES = ss.load()
FILES = {"A1": "pass1.jsonl", "A2": "pass2.jsonl", "B": "zoom2.jsonl"}
LINES = {k: ss.read(ss.OUT / f) for k, f in FILES.items()}
RUNS = {k: ss.latest(v) for k, v in LINES.items()}
A1, A2, B = RUNS["A1"], RUNS["A2"], RUNS["B"]
CELLS = [f"{p} {t}" for p, t in ss.CELLS]
# The 50 zoom breaks (A2 hit -> B miss), classified by eye from the sheets in analysis/label-audit/sheets/;
# every break not listed here is a precision break (B on the right element or its edge, click off).
BREAKS = {"neighbour pick": [125, 132, 235, 708, 762, 906, 909, 929, 961, 1087, 1222, 1257],
          "context loss (crop cut the label)": [46, 49, 57, 58, 136, 307, 311, 346, 484, 988, 1027, 1032, 1185, 1212],
          "garbage answer": [15, 673], "ambiguous label": [972]}
REGISTERED = (48.0, 17.5, 85.8)  # replay prediction before the run: fixed, broken, accuracy (analysis/zoom-replay/)


def section(t):
    print(f"\n## {t}")


def pct(xs):
    xs = list(xs)
    return round(100 * sum(map(bool, xs)) / len(xs), 2) if xs else None


def dist(r):  # click to the nearest edge of the true box, original px (0 = inside)
    W, H = r["orig_size"]; x, y, w, h = r["gt_px"]; px, py = r["point"][0] * W, r["point"][1] * H
    return math.hypot(max(x - px, 0, px - x - w), max(y - py, 0, py - y - h))


def centre_dist(r):  # click to the centre of the true box, original px
    W, H = r["orig_size"]; x, y, w, h = r["gt_px"]
    return math.hypot(r["point"][0] * W - x - w / 2, r["point"][1] * H - y - h / 2)


def sides(b):
    l, r = sorted((b["left"], b["right"])); t, bo = sorted((b["top"], b["bottom"]))
    return l, t, r, bo


def holds_centre(r):  # Jev's box contains the true centre: on a miss this is the "too-wide box" failure
    W, H = r["orig_size"]; x, y, w, h = r["gt_px"]; l, t, rr, bo = sides(r["box"])
    return l <= (x + w / 2) / W <= rr and t <= (y + h / 2) / H <= bo


def iou(a, b):
    al, at, ar, ab = sides(a); bl, bt, br, bb = sides(b)
    inter = max(0, min(ar, br) - max(al, bl)) * max(0, min(ab, bb) - max(at, bt))
    u = (ar - al) * (ab - at) + (br - bl) * (bb - bt) - inter
    return inter / u if u > 0 else 0.0


def inbox(pt, b):
    l, t, r, bo = sides(b)
    return l <= pt[0] <= r and t <= pt[1] <= bo


def auroc(pos, neg):  # rank form with tied ranks averaged (same value as ss.auroc, fast enough to bootstrap)
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    rank_sum, i = 0.0, 0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]:
            j += 1
        rank_sum += sum(l for _, l in allv[i:j]) * (i + j + 1) / 2
        i = j
    return (rank_sum - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def boot(d, reps=10000, seed=0):  # 95% bootstrap CI of a per-case mean difference, in pp
    rnd, n = random.Random(seed), len(d)
    m = sorted(100 * sum(d[rnd.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return round(m[int(0.025 * reps)], 2), round(m[int(0.975 * reps) - 1], 2)


def gain(S, a="h2", z="hb"):
    S = list(S); up = sum(1 for r in S if not r[a] and r[z]); dn = sum(1 for r in S if r[a] and not r[z])
    return (f"n={len(S)} {pct(r[a] for r in S)} -> {pct(r[z] for r in S)} "
            f"({100 * (up - dn) / len(S):+.1f} pp, fixed {up}, broken {dn}, p={ss.mcnemar(up, dn):.2g})") if S else "n=0"


def ts(r):
    return datetime.datetime.fromisoformat(r["ts"])


def by_start(R):  # call start order; ts has 1 s resolution, ties broken by case index
    return sorted(R.values(), key=lambda r: (ts(r), r["i"]))


# one row per case: the three answers plus geometry
rows = []
for i in range(N):
    a1, a2, b = A1[i], A2[i], B[i]
    W, H = a2["orig_size"]; x, y, w, h = a2["gt_px"]; s = a2["scale"]
    x0, y0, cw, ch = b["window"]; sb = b["sent_size"][0] / cw
    rows.append(dict(
        i=i, cell=f"{a2['platform']} {a2['type']}", platform=a2["platform"], source=a2["source"], W=W, H=H, s=s,
        h1=bool(a1["hit"]), h2=bool(a2["hit"]), hb=bool(b["hit"]),
        c1=a1["confidence"], c2=a2["confidence"], cb=b["confidence"], tw=w, th=h,
        tsz_a=math.sqrt(w * h) * s, tsz_b=math.sqrt(w * h) * sb, wf=b["window_frac"],
        d1=dist(a1), d2=dist(a2), db=dist(b), wide2=holds_centre(a2), wideb=holds_centre(b),
        full_in=x >= x0 and y >= y0 and x + w <= x0 + cw and y + h <= y0 + ch,
        visible=not (x + w < x0 or x > x0 + cw or y + h < y0 or y > y0 + ch)))
R_ = {r["i"]: r for r in rows}

section("1. Integrity (asserts)")
sizes = {}
for k, R in RUNS.items():
    assert len(LINES[k]) == N and sorted(R) == list(range(N)), (k, len(LINES[k]))
    assert all(r["status"] == "ok" for r in R.values()), k
    for i, r in R.items():
        c = CASES[i]; W, H = r["orig_size"]; x, y, w, h = c["bbox"]
        if c["img_filename"] not in sizes:
            sizes[c["img_filename"]] = Image.open(ss.DATA / "screenspotv2_image" / c["img_filename"]).size
        assert (W, H) == sizes[c["img_filename"]], (k, i)
        assert (r["file"], r["instruction"], r["platform"], r["type"]) == (c["img_filename"], c["instruction"], c["platform"], c["data_type"])
        assert r["gt"] == [x / W, y / H, (x + w) / W, (y + h) / H] and r["gt_px"] == [x, y, w, h], (k, i)
        assert r["instructions_sent"] == ss.TEMPLATE.format(instruction=ss.clean(c["instruction"])), (k, i)
        box, conf = ss.parse_box(r["raw"])  # re-parse the raw API answer
        assert all(abs(v * 100 - round(v * 100)) < 1e-9 for v in box.values()), (k, i)  # Jev answers on a 0.01 grid
        if k == "B":
            win = ss.zoom_window(A2[i], W, H)  # the crop is rebuilt from stage A's record alone
            assert r["window"] == list(win) and r["window_frac"] == round(win[2] / W, 4), i
            assert (r["zoom_f"], r["zoom_margin"]) == (ss.ZOOM_F, ss.ZOOM_MARGIN) and r["sent_size"] == A2[i]["sent_size"], i
            assert box == r["box_crop"], i
            x0, y0, cw, ch = win
            if tuple(win) != (0, 0, W, H):
                box = {"left": (x0 + box["left"] * cw) / W, "right": (x0 + box["right"] * cw) / W,
                       "top": (y0 + box["top"] * ch) / H, "bottom": (y0 + box["bottom"] * ch) / H}
        else:
            sc = max(min(1.0, jev.MAX_SIDE / max(W, H)), jev.MIN_SIDE / min(W, H))
            assert r["sent_size"] == ([round(W * sc), round(H * sc)] if sc != 1.0 else [W, H]) and r["scale"] == round(sc, 6), (k, i)
        assert box == r["box"] and conf == r["confidence"], (k, i)
        pt = [(box["left"] + box["right"]) / 2, (box["top"] + box["bottom"]) / 2]
        assert pt == r["point"] and ss.inside(pt, r["gt"]) == bool(r["hit"]), (k, i)
    hits = sum(bool(r["hit"]) for r in R.values())
    print(f"{k}: {len(LINES[k])} lines, {len(R)} cases, all ok, rescored from raw answers: {hits} hits = {100 * hits / N:.2f}%")
    print(f"   identity {dict(collections.Counter((r['requested_model'], r['model'], r['provider']) for r in R.values()))}"
          f" prompt {dict(collections.Counter((r['prompt_version'], r['template_hash']) for r in R.values()))}")
    print(f"   attempts {dict(collections.Counter(r['attempts'] for r in R.values()))}, output tokens "
          f"{dict(collections.Counter(r['usage']['output_tokens'] for r in R.values()))}, degenerate "
          f"{[i for i, r in R.items() if r['degenerate']]}, on_edge {[i for i, r in R.items() if r['on_edge']]}, "
          f"out_of_range {sum(r['out_of_range'] for r in R.values())}"
          + (f", out_of_crop {sum(r['out_of_crop'] for r in R.values())}, code_rev "
             f"{dict(collections.Counter(r['code_rev'] for r in R.values()))}" if k == "B" else ""))
print(f"screenshots {len(sizes)}, every orig_size matches the image file; B window, mapping and sent size rebuilt from A2")

# which commit ran each pass: the last commit before its first record
log = [l.split(" ", 1) for l in subprocess.run(["git", "-C", str(ROOT), "log", "--format=%cI %h"], capture_output=True,
                                                text=True, check=True).stdout.split("\n") if l]
commits = sorted((datetime.datetime.fromisoformat(t), h) for t, h in log)
for k, R in RUNS.items():
    T = by_start(R); t0, t1 = ts(T[0]), ts(T[-1])
    rev = [h for t, h in commits if t <= t0][-1]
    gaps = [(T[j]["i"], (ts(T[j]) - ts(T[j - 1])).seconds) for j in range(1, N) if (ts(T[j]) - ts(T[j - 1])).seconds > 5]
    print(f"{k}: {t0:%H:%M:%S}-{t1:%H:%M:%S} UTC, code at {rev}, gaps over 5 s before case {gaps}")
first20 = by_start(A1)[:20]
print(f"pass 1 start batch: cases {sorted(r['i'] for r in first20)[:3]}..{sorted(r['i'] for r in first20)[-1]}, "
      f"{ts(first20[0]):%H:%M:%S}-{ts(first20[-1]):%H:%M:%S}")


def fns(rev, path, names):
    src = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout
    tree = ast.parse(src)
    out = {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names}
    out.update({t.id: ast.get_source_segment(src, n.value) for n in tree.body if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name) and t.id in names})
    return out


rev1 = [h for t, h in commits if t <= ts(by_start(A1)[0])][-1]
rev2 = [h for t, h in commits if t <= ts(by_start(A2)[0])][-1]
for path, names in (("screenspot.py", {"load", "clean", "request", "parse_box", "inside", "TEMPLATE", "PROMPT_VERSION"}),
                    ("jev.py", {"fit", "data_url", "decide", "URL", "MODEL", "MAX_SIDE", "MIN_SIDE"})):
    f1, f2 = fns(rev1, path, names), fns(rev2, path, names)
    print(f"stage-A code {path} {rev1} vs {rev2}: " + ", ".join(f"{n} {'same' if f1.get(n) == f2.get(n) else 'DIFFERS'}" for n in sorted(names)))

if "--images" in sys.argv:
    def rebuild(i):
        c = CASES[i]; orig = Image.open(ss.DATA / "screenspotv2_image" / c["img_filename"])
        img, _ = jev.fit(orig)
        x0, y0, cw, ch = B[i]["window"]
        bimg = orig.crop((x0, y0, x0 + cw, y0 + ch)).resize(tuple(A2[i]["sent_size"]), resample=3)
        return i, len(jev.data_url(img)), list(img.size), len(jev.data_url(bimg))
    with cf.ProcessPoolExecutor() as ex:
        out = list(ex.map(rebuild, range(N), chunksize=8))
    for i, la, sa, lb in out:
        assert la == A1[i]["payload_bytes"] == A2[i]["payload_bytes"] and sa == A1[i]["sent_size"] and lb == B[i]["payload_bytes"], i
    print(f"images: all {2 * N} sent images rebuilt (A once for A1 and A2, B from the window), payload lengths match exactly")

section("2. Accuracy")
for k, h in (("A1", "h1"), ("A2", "h2"), ("B", "hb")):
    n = sum(r[h] for r in rows); lo, hi = ss.wilson(n, N)
    macro = st.mean(100 * sum(r[h] for r in rows if r["cell"] == c) / sum(r["cell"] == c for r in rows) for c in CELLS)
    print(f"{k}: {n}/{N} = {100 * n / N:.2f}% (Wilson {lo:.2f}-{hi:.2f}), macro {macro:.2f}; cells "
          + ", ".join(f"{c} {pct(r[h] for r in rows if r['cell'] == c)}" for c in CELLS))
for a, z, nm in (("h1", "h2", "A1->A2 (rerun)"), ("h2", "hb", "A2->B (zoom vs its own A)"), ("h1", "hb", "A1->B")):
    up = sum(1 for r in rows if not r[a] and r[z]); dn = sum(1 for r in rows if r[a] and not r[z])
    print(f"{nm}: miss->hit {up}, hit->miss {dn}, exact McNemar p={ss.mcnemar(up, dn):.2g}, "
          f"paired bootstrap 95% CI {ss.paired_ci([r[a] for r in rows], [r[z] for r in rows])}")
d = [r["hb"] - (r["h1"] + r["h2"]) / 2 for r in rows]
print(f"B vs mean(A1, A2): {100 * sum(d) / N:+.2f} pp, bootstrap 95% CI {boot(d)}")
pat = collections.Counter(("hit" if r["h1"] else "miss", "hit" if r["h2"] else "miss", "hit" if r["hb"] else "miss") for r in rows)
print("A1, A2, B patterns:", ", ".join(f"{'/'.join(k)} {v}" for k, v in pat.most_common()))
both_miss = pat[("miss", "miss", "hit")] + pat[("miss", "miss", "miss")]; both_hit = pat[("hit", "hit", "hit")] + pat[("hit", "hit", "miss")]
print(f"zoom fixed {pat[('miss', 'miss', 'hit')]} of {both_miss} double-raw misses, broke {pat[('hit', 'hit', 'miss')]} of {both_hit} double-raw hits "
      f"({100 * pat[('hit', 'hit', 'miss')] / both_hit:.1f}%)")

section("3. Rerun jitter (A1 vs A2: identical requests)")
shift = [math.hypot((A1[i]["point"][0] - A2[i]["point"][0]) * R_[i]["W"], (A1[i]["point"][1] - A2[i]["point"][1]) * R_[i]["H"]) * R_[i]["s"] for i in range(N)]
ious = [iou(A1[i]["box"], A2[i]["box"]) for i in range(N)]
same_box = [i for i in range(N) if A1[i]["box"] == A2[i]["box"]]
print(f"identical box {len(same_box)}, identical box+confidence {sum(A1[i]['confidence'] == A2[i]['confidence'] for i in same_box)}; "
      f"click shift median {st.median(shift):.1f} sent px; IoU>=0.5 {pct(v >= 0.5 for v in ious)}%; IoU<0.1 (switched element) {sum(v < 0.1 for v in ious)}")
flips = [r for r in rows if r["h1"] != r["h2"]]
print(f"flips {len(flips)}: on the target's edge (the hit sits inside, the miss within 15 orig px) "
      f"{sum(1 for r in flips if max(r['d1'], r['d2']) < 15)}, switched element {sum(ious[r['i']] < 0.1 for r in flips)}")
print(f"confidence correlation A1-A2 {st.correlation([r['c1'] for r in rows], [r['c2'] for r in rows]):.3f}, "
      f"A2-B {st.correlation([r['c2'] for r in rows], [r['cb'] for r in rows]):.3f}; input-token difference on identical requests "
      f"{dict(sorted(collections.Counter(A2[i]['usage']['input_tokens'] - A1[i]['usage']['input_tokens'] for i in range(N)).items()))}")

section("4. Why zoom helps")
for lo, hi in ((0, 30), (30, 45), (45, 60), (60, 80), (80, 120), (120, 1e9)):
    print(f"target {lo}-{hi} px in A's image: {gain(r for r in rows if lo <= r['tsz_a'] < hi)}")
print(f"under 60 px: {gain(r for r in rows if r['tsz_a'] < 60)}")
print(f"60 px and up: {gain(r for r in rows if r['tsz_a'] >= 60)}")
print(f"A at native size (B only upsamples): {gain(r for r in rows if r['s'] >= 0.999)}")
print(f"A downscaled (B also recovers pixels): {gain(r for r in rows if r['s'] < 0.999)}")
print(f"960x540 desktop (native, pure upsample): {gain(r for r in rows if (r['W'], r['H']) == (960, 540))}")
both = [r for r in rows if r["h2"] and r["hb"]]
print(f"precision on the {len(both)} cases both hit: click to target centre median A2 {st.median(centre_dist(A2[r['i']]) for r in both):.1f}, "
      f"B {st.median(centre_dist(B[r['i']]) for r in both):.1f} orig px")
for k, R in (("A2", A2), ("B", B)):
    wr = [abs(R[i]["box"]["right"] - R[i]["box"]["left"]) * R_[i]["W"] / R_[i]["tw"] for i in range(N)]
    print(f"{k} box width / target width: median {st.median(wr):.2f}, over 1.5x {pct(v > 1.5 for v in wr)}%, over 3x {pct(v > 3 for v in wr)}%; "
          f"too-wide misses {sum(1 for i in range(N) if not R[i]['hit'] and holds_centre(R[i]))}")
M = [r for r in rows if not r["h2"]]
print(f"A2 misses {len(M)}: too-wide {sum(r['wide2'] for r in M)} fixed {pct(r['hb'] for r in M if r['wide2'])}%, "
      f"off-target {sum(not r['wide2'] for r in M)} fixed {pct(r['hb'] for r in M if not r['wide2'])}%")
for nm, f in (("off-target <=25 px", lambda r: not r["wide2"] and r["d2"] <= 25), ("off-target 25-100 px", lambda r: not r["wide2"] and 25 < r["d2"] <= 100),
              ("off-target >100 px", lambda r: not r["wide2"] and r["d2"] > 100), ("target fully in the window", lambda r: r["full_in"]),
              ("target not visible in the window", lambda r: not r["visible"])):
    S = [r for r in M if f(r)]; print(f"   {nm}: {len(S)}, fixed {sum(r['hb'] for r in S)} ({pct(r['hb'] for r in S)}%)")
for (p, s_), S in sorted(collections.Counter((r["platform"], r["source"]) for r in rows).items()):
    print(f"source {p} {s_}: {gain(r for r in rows if (r['platform'], r['source']) == (p, s_))}")
for lo, hi in ((0, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
    print(f"A2 confidence {lo}-{hi}: {gain(r for r in rows if lo <= r['c2'] < hi)}")
for p in ("mobile", "desktop", "web"):
    print(f"platform {p}: {gain(r for r in rows if r['platform'] == p)}")

section("5. The 50 breaks (A2 hit -> B miss)")
brk = {r["i"] for r in rows if r["h2"] and not r["hb"]}
listed = {i for v in BREAKS.values() for i in v}
assert listed <= brk and len(listed) == sum(map(len, BREAKS.values())), sorted(listed - brk)
cls = {**{i: k for k, v in BREAKS.items() for i in v}, **{i: "precision" for i in brk - listed}}
for k, n in collections.Counter(cls.values()).most_common():
    S = [R_[i] for i in brk if cls[i] == k]
    print(f"{k}: {n} (mobile {sum(r['platform'] == 'mobile' for r in S)}, desktop {sum(r['platform'] == 'desktop' for r in S)}, "
          f"web {sum(r['platform'] == 'web' for r in S)})")
prec = [R_[i] for i in brk if cls[i] == "precision"]
print(f"precision breaks check: B within max(25 px, half the short side) or too-wide in "
      f"{sum(1 for r in prec if r['db'] <= max(25, min(r['tw'], r['th']) / 2) or r['wideb'])} of {len(prec)}; "
      f"B distance median {st.median(r['db'] for r in prec):.0f} orig px")
print(f"B confidence lower than A2's in {sum(R_[i]['cb'] < R_[i]['c2'] for i in brk)} of {len(brk)} breaks; "
      f"higher in {sum(1 for r in rows if not r['h2'] and r['hb'] and r['cb'] > r['c2'])} of {sum(1 for r in rows if not r['h2'] and r['hb'])} fixes")
Bm = [r for r in rows if not r["hb"]]
print(f"B misses {len(Bm)}: all three runs miss {sum(not r['h1'] and not r['h2'] for r in Bm)}, target outside the window "
      f"{sum(not r['visible'] for r in Bm)}, over 100 px away {sum(r['db'] > 100 for r in Bm)}, too-wide {sum(r['wideb'] for r in Bm)}")
print(f"registered replay prediction: fixed {REGISTERED[0]}, broken {REGISTERED[1]}, {REGISTERED[2]}%; actual fixed "
      f"{sum(1 for r in rows if not r['h2'] and r['hb'])}, broken {len(brk)}, {pct(r['hb'] for r in rows)}%")

section("6. Confidence and agreement")
au = {k: auroc([r[c] for r in rows if r[h]], [r[c] for r in rows if not r[h]]) for k, c, h in (("A1", "c1", "h1"), ("A2", "c2", "h2"), ("B", "cb", "hb"))}
assert abs(au["A2"] - ss.auroc([r["c2"] for r in rows if r["h2"]], [r["c2"] for r in rows if not r["h2"]])) < 1e-12
rnd = random.Random(7); dd = []
for _ in range(2000):
    S = [rows[rnd.randrange(N)] for _ in range(N)]
    dd.append(auroc([r["cb"] for r in S if r["hb"]], [r["cb"] for r in S if not r["hb"]]) - auroc([r["c2"] for r in S if r["h2"]], [r["c2"] for r in S if not r["h2"]]))
dd.sort()
print(f"AUROC A1 {au['A1']:.3f}, A2 {au['A2']:.3f}, B {au['B']:.3f}; B-A2 bootstrap 95% CI {dd[50]:.3f} to {dd[1949]:.3f}")
for t in (0.5, 0.7, 0.8, 0.9):
    S = [r for r in rows if r["cb"] >= t]; T = [r for r in rows if r["c2"] >= t]
    print(f"conf >= {t}: B {len(S)} cases ({100 * len(S) / N:.1f}%) {pct(r['hb'] for r in S)}% right | A2 {len(T)} ({100 * len(T) / N:.1f}%) {pct(r['h2'] for r in T)}% right")
agree = [r for r in rows if inbox(B[r["i"]]["point"], A2[r["i"]]["box"]) and inbox(A2[r["i"]]["point"], B[r["i"]]["box"])]
dis = [r for r in rows if r not in agree]
print(f"A2 and B agree (each click inside the other's box): {len(agree)}, B right {pct(r['hb'] for r in agree)}%; "
      f"disagree {len(dis)}: B right {pct(r['hb'] for r in dis)}%, A2 right {pct(r['h2'] for r in dis)}%")
print(f"post-hoc, not protocol: higher-confidence answer {pct(r['hb'] if r['cb'] >= r['c2'] else r['h2'] for r in rows)}%, "
      f"oracle A2 or B {pct(r['h2'] or r['hb'] for r in rows)}%, oracle any of three {pct(r['h1'] or r['h2'] or r['hb'] for r in rows)}%, "
      f"zoom on desktop+web only {pct(r['hb'] if r['platform'] != 'mobile' else r['h2'] for r in rows)}%")

section("7. Cost and speed")
tot = {k: sum(r["usage"]["cost"] for r in R.values()) for k, R in RUNS.items()}
tok = {k: sum(r["usage"]["input_tokens"] for r in R.values()) for k, R in RUNS.items()}
price = collections.Counter(round(r["usage"]["cost"] / r["usage"]["input_tokens"] * 1e6, 6) for R in RUNS.values() for r in R.values())
print(f"price per 1M input tokens {dict(price)} (output tokens not charged)")
print(f"cost A1 ${tot['A1']:.6f}, A2 ${tot['A2']:.6f}, B ${tot['B']:.6f}, run 2 (A2+B) ${tot['A2'] + tot['B']:.6f}, all three ${sum(tot.values()):.6f}")
print(f"input tokens A1 {tok['A1']:,}, A2 {tok['A2']:,}, B {tok['B']:,}; per click A ${tot['A2'] / N:.6f}, A+B ${(tot['A2'] + tot['B']) / N:.6f}")
xs = [(A2[i]["sent_pixels"], A2[i]["usage"]["input_tokens"]) for i in range(N)]
mx, my = st.mean(x for x, _ in xs), st.mean(y for _, y in xs)
bslope = sum((x - mx) * (y - my) for x, y in xs) / sum((x - mx) ** 2 for x, _ in xs)
print(f"tokens = {my - bslope * mx:.0f} + {bslope:.6f} x sent pixels (max residual {max(abs(y - (my - bslope * mx) - bslope * x) for x, y in xs):.0f})")
q = lambda v, p: sorted(v)[int(p * (len(v) - 1))]
for k, R in RUNS.items():
    v = [r["seconds"] for r in R.values()]
    print(f"latency {k}: median {st.median(v):.3f} s, p90 {q(v, .9):.3f}, max {max(v):.3f}")
ab = [A2[i]["seconds"] + B[i]["seconds"] for i in range(N)]
t2 = sorted(ts(r) for r in list(A2.values()) + list(B.values()))
end2 = max(ts(r) + datetime.timedelta(seconds=r["wall_seconds"]) for r in list(A2.values()) + list(B.values()))
print(f"A+B per click median {st.median(ab):.3f} s, p90 {q(ab, .9):.3f}; run 2 {t2[0]:%H:%M:%S}-{end2:%H:%M:%S} UTC = {(end2 - t2[0]).seconds} s with 4 workers")
before2 = float([l for l in open(ss.OUT / "pass2.run.log") if l.startswith("key balance before:")][0].split(":")[1])
print(f"key balance before run 2 ${before2:.6f} (pass2.run.log) - logged run 2 ${tot['A2'] + tot['B']:.6f} = ${before2 - tot['A2'] - tot['B']:.6f} expected now")
if "--balance" in sys.argv:
    v = jev.balance(); print(f"key balance now: {v if isinstance(v, str) else f'${v:.6f}'}")
