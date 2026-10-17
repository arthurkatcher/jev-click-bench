"""Deep audit of ScreenSpot-Pro pass 1 (A1), pass 2 (A2) and zoom stage B (B), straight from the raw records.
Same structure as analysis/audit_run2.py (v2). Every integrity check is an assert; every number in
analysis/AUDIT-pro-run2.md is printed here. Offline, no API calls.
  python3 analysis/audit_pro_run2.py              # all numbers, a few minutes
  python3 analysis/audit_pro_run2.py --images     # + rebuild all 3,162 sent images and match their payload sizes
  python3 analysis/audit_pro_run2.py --balance    # + read the key balance (free GET, no spend)
Distances and sizes are in the image Jev saw for the full screenshot (A's sent px) unless a line says otherwise."""
import ast, collections, concurrent.futures as cf, datetime, json, math, pathlib, random, statistics as st, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image
import jev
import screenspot as ss

FILES = {"A1": "pass1.jsonl", "A2": "pass2.jsonl", "B": "zoom2.jsonl"}
ss.use("v2")  # v2's three runs, only for the side-by-side comparisons
V2 = {k: ss.latest(ss.read(ss.OUT / f)) for k, f in FILES.items()}
ss.use("pro")
N = 1581
CASES = ss.load()
RAW = {}  # the official annotation files as published
for f in sorted((ss.DATA / "annotations").glob("*.json")):
    for c in json.loads(f.read_text()):
        RAW[c["id"]] = c
LINES = {k: ss.read(ss.OUT / f) for k, f in FILES.items()}
RUNS = {k: ss.latest(v) for k, v in LINES.items()}
A1, A2, B = RUNS["A1"], RUNS["A2"], RUNS["B"]
CELLS = [f"{g} {t}" for g, t in ss.CELLS]
REV = {"A1": "4099bfa", "A2": "3cc1088", "B": "3cc1088"}  # code_rev on every record (clean trees)
V2_RUN2_REV = "bb538fc"  # v2 run 2, for the "same frozen zoom as v2" check
# The 55 zoom breaks (A2 hit -> B miss), classified by eye from analysis/label-audit-pro/sheets/breaks_*.jpg;
# every break not listed here is a precision break (B on the right element or its edge, click off).
BREAKS = {"neighbour pick": [98, 120, 325, 337, 437, 844, 857, 1020, 1091, 1095, 1238, 1256, 1279, 1526],
          "wrong element far away": [972, 1123, 1284, 1431, 1580],
          "ambiguous label (two scatter-plot icons)": [759],
          "answer-key error (B is on the asked element)": [657]}
CEST = datetime.timezone(datetime.timedelta(hours=2))


def section(t):
    print(f"\n## {t}")


def pct(xs):
    xs = list(xs)
    return round(100 * sum(map(bool, xs)) / len(xs), 2) if xs else None


def official(r):  # ScreenSpot-Pro eval_sample_positive_gt, on the raw annotation (verbatim logic)
    c = RAW[r["case_id"]]; bbox = c["bbox"]; img_size = c["img_size"]
    bbox = [bbox[0] / img_size[0], bbox[1] / img_size[1], bbox[2] / img_size[0], bbox[3] / img_size[1]]
    return (bbox[0] <= r["point"][0] <= bbox[2]) and (bbox[1] <= r["point"][1] <= bbox[3])


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


def window_has(win, gt_px, whole=False):  # is the true box (its centre, or all of it) inside a window
    x0, y0, cw, ch = win; x, y, w, h = gt_px
    if whole:
        return x >= x0 and y >= y0 and x + w <= x0 + cw and y + h <= y0 + ch
    return x0 <= x + w / 2 <= x0 + cw and y0 <= y + h / 2 <= y0 + ch


def make_rows(R, pro):
    out = []
    for i in sorted(R["A2"]):
        a1, a2, b = R["A1"][i], R["A2"][i], R["B"][i]
        W, H = a2["orig_size"]; x, y, w, h = a2["gt_px"]; s = a2["scale"]
        x0, y0, cw, ch = b["window"]; sb = b["sent_size"][0] / cw
        out.append(dict(
            i=i, cell=f"{a2['group'] if pro else a2['platform']} {a2['type']}", group=a2["group"] if pro else a2["platform"],
            app=a2["source"], os=a2["platform"], type=a2["type"], W=W, H=H, s=s, sb=sb,
            h1=bool(a1["hit"]), h2=bool(a2["hit"]), hb=bool(b["hit"]),
            c1=a1["confidence"], c2=a2["confidence"], cb=b["confidence"], tw=w, th=h,
            tsz_a=math.sqrt(w * h) * s, tsz_b=math.sqrt(w * h) * sb, wf=b["window_frac"],
            d1=dist(a1) * s, d2=dist(a2) * s, db=dist(b) * s,  # A's sent px
            d1o=dist(a1), d2o=dist(a2), dbo=dist(b),  # original px
            wide1=holds_centre(a1), wide2=holds_centre(a2), wideb=holds_centre(b),
            sub_a=w / W < 0.01 or h / H < 0.01, sub_b=w / cw < 0.01 or h / ch < 0.01,  # under one 0.01 answer step
            full_in=window_has(b["window"], a2["gt_px"], True), centre_in=window_has(b["window"], a2["gt_px"]),
            visible=not (x + w < x0 or x > x0 + cw or y + h < y0 or y > y0 + ch)))
    return out


rows = make_rows(RUNS, True)
R_ = {r["i"]: r for r in rows}
v2rows = make_rows(V2, False)

section("1. Integrity (asserts)")
sizes = {}
for k, R in RUNS.items():
    assert len(LINES[k]) == N and sorted(R) == list(range(N)), (k, len(LINES[k]))
    assert all(r["status"] == "ok" for r in R.values()), k
    for i, r in R.items():
        c = CASES[i]; W, H = r["orig_size"]; x, y, w, h = c["bbox"]; raw = RAW[c["id"]]
        if c["img_filename"] not in sizes:
            sizes[c["img_filename"]] = Image.open(ss.DATA / ss.IMAGES / c["img_filename"]).size
        assert (W, H) == sizes[c["img_filename"]] == tuple(raw["img_size"]), (k, i)
        assert (r["file"], r["instruction"], r["platform"], r["type"], r["group"], r["case_id"], r["source"], r["bench"]) == \
               (raw["img_filename"], raw["instruction"], raw["platform"], raw["ui_type"], raw["group"], raw["id"], raw["application"], "pro"), (k, i)
        assert r["gt"] == [x / W, y / H, (x + w) / W, (y + h) / H] and r["gt_px"] == [x, y, w, h], (k, i)
        assert [x, y, x + w, y + h] == raw["bbox"], (k, i)  # stored [x, y, w, h] gives back the published [x1, y1, x2, y2]
        assert r["instructions_sent"] == ss.TEMPLATE.format(instruction=ss.clean(c["instruction"])), (k, i)
        assert (r["prompt_version"], r["template_hash"], r["requested_model"]) == (ss.PROMPT_VERSION, ss.TEMPLATE_HASH, jev.MODEL), (k, i)
        assert r["code_rev"] == REV[k], (k, i, r["code_rev"])
        box, conf = ss.parse_box(r["raw"])  # re-parse the raw API answer
        assert all(abs(v * 100 - round(v * 100)) < 1e-9 for v in box.values()), (k, i)  # Jev answers on a 0.01 grid
        if k == "B":
            win = ss.zoom_window(A2[i], W, H)  # the crop is rebuilt from stage A's record alone
            assert r["window"] == list(win) and r["window_frac"] == round(win[2] / W, 4), i
            assert (r["zoom_f"], r["zoom_margin"]) == (ss.ZOOM_F, ss.ZOOM_MARGIN) == (0.5, 0.1), i
            assert r["sent_size"] == A2[i]["sent_size"] and r["scale"] == round(r["sent_size"][0] / win[2], 6), i
            assert box == r["box_crop"] and r["out_of_crop"] == any(not 0 <= v <= 1 for v in box.values()), i
            x0, y0, cw, ch = win
            if tuple(win) != (0, 0, W, H):
                box = {"left": (x0 + box["left"] * cw) / W, "right": (x0 + box["right"] * cw) / W,
                       "top": (y0 + box["top"] * ch) / H, "bottom": (y0 + box["bottom"] * ch) / H}
        else:
            sc = max(min(1.0, jev.MAX_SIDE / max(W, H)), jev.MIN_SIDE / min(W, H))
            assert r["sent_size"] == ([round(W * sc), round(H * sc)] if sc != 1.0 else [W, H]) and r["scale"] == round(sc, 6), (k, i)
        assert box == r["box"] and conf == r["confidence"], (k, i)
        pt = [(box["left"] + box["right"]) / 2, (box["top"] + box["bottom"]) / 2]
        assert pt == r["point"] and ss.inside(pt, r["gt"]) == bool(r["hit"]) == official(r), (k, i)
    hits = sum(bool(r["hit"]) for r in R.values())
    print(f"{k}: {len(LINES[k])} lines, {len(R)} cases, all ok, rescored from raw answers with the official rule on the raw "
          f"annotation: {hits} hits = {100 * hits / N:.2f}%")
    print(f"   identity {dict(collections.Counter((r['requested_model'], r['model'], r['provider']) for r in R.values()))}"
          f" prompt {dict(collections.Counter((r['prompt_version'], r['template_hash']) for r in R.values()))} code_rev "
          f"{dict(collections.Counter(r['code_rev'] for r in R.values()))}")
    print(f"   attempts {dict(collections.Counter(r['attempts'] for r in R.values()))}, output tokens "
          f"{dict(collections.Counter(r['usage']['output_tokens'] for r in R.values()))}, degenerate "
          f"{[i for i, r in R.items() if r['degenerate']]}, on_edge {[i for i, r in R.items() if r['on_edge']]}, "
          f"out_of_range {[i for i, r in R.items() if r['out_of_range']]}, hit_tolerant differs "
          f"{[i for i, r in R.items() if r['hit_tolerant'] != r['hit']]}"
          + (f", out_of_crop {[i for i, r in R.items() if r['out_of_crop']]}" if k == "B" else ""))
print(f"screenshots {len(sizes)} (one per case), every orig_size matches the image file and the annotation's img_size; "
      f"B window, mapping and sent size rebuilt from A2")
print(f"sent sizes (A): {dict(collections.Counter((tuple(r['orig_size']), tuple(r['sent_size'])) for r in A2.values()).most_common())}")

for k, R in RUNS.items():
    T = by_start(R); t0, t1 = ts(T[0]), ts(T[-1])
    end = max(ts(r) + datetime.timedelta(seconds=r["wall_seconds"]) for r in R.values())
    gaps = [(T[j]["i"], (ts(T[j]) - ts(T[j - 1])).seconds) for j in range(1, N) if (ts(T[j]) - ts(T[j - 1])).seconds > 5]
    print(f"{k}: first call {t0.astimezone(CEST):%H:%M:%S}, last call {t1.astimezone(CEST):%H:%M:%S}, last answer "
          f"{end.astimezone(CEST):%H:%M:%S} CEST, gaps over 5 s {gaps}")
order = [r["i"] for r in by_start(A2)]
print(f"run 2 order: B of a case starts after its A2 answer in {sum(ts(B[i]) >= ts(A2[i]) for i in range(N))} of {N}; "
      f"A2 call order follows case order (first 5 {order[:5]}, last {order[-1]})")


def fns(rev, path, names):
    src = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout
    tree = ast.parse(src)
    out = {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:  # NAME = v, and NAME1, NAME2 = v1, v2
                pairs = [(t, n.value)] if isinstance(t, ast.Name) else (
                    list(zip(t.elts, n.value.elts)) if isinstance(t, ast.Tuple) and isinstance(n.value, ast.Tuple) else [])
                out.update({e.id: ast.get_source_segment(src, v) for e, v in pairs if isinstance(e, ast.Name) and e.id in names})
    return out


for (r1, r2), groups in (((REV["A1"], REV["A2"]), (("screenspot.py", {"load", "load_pro", "clean", "request", "parse_box", "inside", "run_one",
                                                                          "zoom_window", "TEMPLATE", "PROMPT_VERSION", "ZOOM_F", "ZOOM_MARGIN"}),
                                                       ("jev.py", {"fit", "data_url", "decide", "URL", "MODEL", "MAX_SIDE", "MIN_SIDE"}))),
                         ((V2_RUN2_REV, REV["B"]), (("screenspot.py", {"clean", "request", "parse_box", "inside", "zoom_window", "TEMPLATE",
                                                                          "PROMPT_VERSION", "ZOOM_F", "ZOOM_MARGIN"}),
                                                     ("jev.py", {"fit", "data_url", "decide", "URL", "MODEL", "MAX_SIDE", "MIN_SIDE"})))):
    for path, names in groups:
        f1, f2 = fns(r1, path, names), fns(r2, path, names)
        print(f"code {path} {r1} vs {r2}: " + ", ".join(
            f"{n} {'MISSING' if f1.get(n) is None or f2.get(n) is None else ('same' if f1[n] == f2[n] else 'DIFFERS')}" for n in sorted(names)))

if "--images" in sys.argv:
    def rebuild(i):
        c = CASES[i]; orig = Image.open(ss.DATA / ss.IMAGES / c["img_filename"])
        img, _ = jev.fit(orig)
        x0, y0, cw, ch = B[i]["window"]
        bimg = orig.crop((x0, y0, x0 + cw, y0 + ch)).resize(tuple(A2[i]["sent_size"]), resample=3)
        return i, len(jev.data_url(img)), list(img.size), len(jev.data_url(bimg))
    with cf.ProcessPoolExecutor(max_workers=3) as ex:
        out = list(ex.map(rebuild, range(N), chunksize=4))
    for i, la, sa, lb in out:
        assert la == A1[i]["payload_bytes"] == A2[i]["payload_bytes"] and sa == A1[i]["sent_size"] and lb == B[i]["payload_bytes"], i
    print(f"images: all {2 * N} sent images rebuilt (A once for A1 and A2, B from the window), payload lengths match exactly")

section("2. Accuracy")
for k, h in (("A1", "h1"), ("A2", "h2"), ("B", "hb")):
    n = sum(r[h] for r in rows); lo, hi = ss.wilson(n, N)
    macro = st.mean(100 * sum(r[h] for r in rows if r["cell"] == c) / sum(r["cell"] == c for r in rows) for c in CELLS)
    print(f"{k}: {n}/{N} = {100 * n / N:.2f}% (Wilson {lo:.2f}-{hi:.2f}), macro {macro:.2f}, text {pct(r[h] for r in rows if r['type'] == 'text')}, "
          f"icon {pct(r[h] for r in rows if r['type'] == 'icon')}; cells " + ", ".join(f"{c} {pct(r[h] for r in rows if r['cell'] == c)}" for c in CELLS))
for a, z, nm in (("h1", "h2", "A1->A2 (rerun)"), ("h2", "hb", "A2->B (zoom vs its own A)"), ("h1", "hb", "A1->B")):
    up = sum(1 for r in rows if not r[a] and r[z]); dn = sum(1 for r in rows if r[a] and not r[z])
    print(f"{nm}: miss->hit {up}, hit->miss {dn}, exact McNemar p={ss.mcnemar(up, dn):.3g}, "
          f"paired bootstrap 95% CI {tuple(round(v, 2) for v in ss.paired_ci([r[a] for r in rows], [r[z] for r in rows]))}")
d = [r["hb"] - (r["h1"] + r["h2"]) / 2 for r in rows]
print(f"B vs mean(A1, A2): {100 * sum(d) / N:+.2f} pp, bootstrap 95% CI {boot(d)}")
pat = collections.Counter(("hit" if r["h1"] else "miss", "hit" if r["h2"] else "miss", "hit" if r["hb"] else "miss") for r in rows)
print("A1, A2, B patterns:", ", ".join(f"{'/'.join(k)} {v}" for k, v in pat.most_common()))
both_miss = pat[("miss", "miss", "hit")] + pat[("miss", "miss", "miss")]; both_hit = pat[("hit", "hit", "hit")] + pat[("hit", "hit", "miss")]
print(f"zoom fixed {pat[('miss', 'miss', 'hit')]} of {both_miss} double-raw misses ({100 * pat[('miss', 'miss', 'hit')] / both_miss:.1f}%), "
      f"broke {pat[('hit', 'hit', 'miss')]} of {both_hit} double-raw hits ({100 * pat[('hit', 'hit', 'miss')] / both_hit:.1f}%)")
for g in ss.PRO_GROUPS:
    print(f"group {g}: {gain(r for r in rows if r['group'] == g)}")
for c in CELLS:
    print(f"cell {c}: {gain(r for r in rows if r['cell'] == c)}")
for t in ("text", "icon"):
    print(f"type {t}: {gain(r for r in rows if r['type'] == t)}")

section("3. How noisy is a rerun (A1 vs A2: identical requests)")
shift = [math.hypot((A1[i]["point"][0] - A2[i]["point"][0]) * R_[i]["W"], (A1[i]["point"][1] - A2[i]["point"][1]) * R_[i]["H"]) * R_[i]["s"] for i in range(N)]
ious = [iou(A1[i]["box"], A2[i]["box"]) for i in range(N)]
same_box = [i for i in range(N) if A1[i]["box"] == A2[i]["box"]]
print(f"identical box {len(same_box)}, identical box+confidence {sum(A1[i]['confidence'] == A2[i]['confidence'] for i in same_box)}; "
      f"click shift median {st.median(shift):.1f} sent px; IoU>=0.5 {pct(v >= 0.5 for v in ious)}%; IoU<0.1 (switched element) {sum(v < 0.1 for v in ious)}")
flips = [r for r in rows if r["h1"] != r["h2"]]
print(f"flips {len(flips)}: the miss within 5 sent px of the target (edge cases) {sum(1 for r in flips if max(r['d1'], r['d2']) <= 5)}, "
      f"switched element (IoU<0.1) {sum(ious[r['i']] < 0.1 for r in flips)}")
print(f"confidence correlation A1-A2 {st.correlation([r['c1'] for r in rows], [r['c2'] for r in rows]):.3f}, "
      f"A2-B {st.correlation([r['c2'] for r in rows], [r['cb'] for r in rows]):.3f}; input-token difference on identical requests "
      f"{dict(sorted(collections.Counter(A2[i]['usage']['input_tokens'] - A1[i]['usage']['input_tokens'] for i in range(N)).items()))}")
v2shift = [math.hypot((V2["A1"][i]["point"][0] - V2["A2"][i]["point"][0]) * V2["A2"][i]["orig_size"][0],
                      (V2["A1"][i]["point"][1] - V2["A2"][i]["point"][1]) * V2["A2"][i]["orig_size"][1]) * V2["A2"][i]["scale"] for i in V2["A2"]]
print(f"v2 for comparison: click shift median {st.median(v2shift):.1f} sent px, flips {sum(r['h1'] != r['h2'] for r in v2rows)} of {len(v2rows)} "
      f"({pct(r['h1'] != r['h2'] for r in v2rows)}%), identical box {sum(V2['A1'][i]['box'] == V2['A2'][i]['box'] for i in V2['A2'])}")

section("4. Why zoom helps")
BINS = ((0, 10), (10, 15), (15, 20), (20, 30), (30, 45), (45, 60), (60, 1e9))
for lo, hi in BINS:
    print(f"target {lo}-{hi} px in A's image: {gain(r for r in rows if lo <= r['tsz_a'] < hi)}")
print(f"target size in A's image, sent px: median {st.median(r['tsz_a'] for r in rows):.1f} (v2 {st.median(r['tsz_a'] for r in v2rows):.1f}); "
      f"in B's image median {st.median(r['tsz_b'] for r in rows):.1f} (v2 {st.median(r['tsz_b'] for r in v2rows):.1f}); "
      f"share of the screen median {100 * st.median(r['tw'] * r['th'] / (r['W'] * r['H']) for r in rows):.3f}% "
      f"(v2 {100 * st.median(r['tw'] * r['th'] / (r['W'] * r['H']) for r in v2rows):.3f}%)")
print("same apparent size, both benchmarks (raw A2 by target size in A's image | B by target size in B's image):")
MB = ((0, 10), (10, 20), (20, 30), (30, 45), (45, 60), (60, 80), (80, 120), (120, 1e9))
for lo, hi in MB:
    pa = [r["h2"] for r in rows if lo <= r["tsz_a"] < hi]; va = [r["h2"] for r in v2rows if lo <= r["tsz_a"] < hi]
    pb = [r["hb"] for r in rows if lo <= r["tsz_b"] < hi]; vb = [r["hb"] for r in v2rows if lo <= r["tsz_b"] < hi]
    print(f"   {lo}-{hi} px: Pro A2 n={len(pa)} {pct(pa)} | v2 A2 n={len(va)} {pct(va)} || Pro B n={len(pb)} {pct(pb)} | v2 B n={len(vb)} {pct(vb)}")
for t in ("text", "icon"):
    for lo, hi in ((0, 20), (20, 45), (45, 1e9)):
        pa = [r["h2"] for r in rows if r["type"] == t and lo <= r["tsz_a"] < hi]; va = [r["h2"] for r in v2rows if r["type"] == t and lo <= r["tsz_a"] < hi]
        pb = [r["hb"] for r in rows if r["type"] == t and lo <= r["tsz_b"] < hi]
        print(f"   {t} {lo}-{hi} px: Pro A2 n={len(pa)} {pct(pa)} | v2 A2 n={len(va)} {pct(va)} | Pro B (size in B's image) n={len(pb)} {pct(pb)}")
for (wh, s_), n in sorted(collections.Counter(((r["W"], r["H"]), r["s"]) for r in rows).items(), key=lambda kv: -kv[0][1]):
    print(f"screen {wh[0]}x{wh[1]} (sent at {s_:.2f}x): {gain(r for r in rows if (r['W'], r['H']) == wh)}")
for lo, hi in ((0.25, 0.35), (0.35, 0.5), (0.5, 0.65), (0.65, 0.85)):
    print(f"A sent at {lo}-{hi}x: {gain(r for r in rows if lo <= r['s'] < hi)}")
print(f"grid: under one 0.01 step on a side in A's view {sum(r['sub_a'] for r in rows)}, in B's view {sum(r['sub_b'] for r in rows)} "
      f"(v2: {sum(r['sub_a'] for r in v2rows)} / {sum(r['sub_b'] for r in v2rows)})")
print(f"   sub-step in A's view: {gain(r for r in rows if r['sub_a'])}")
print(f"   not sub-step in A's view: {gain(r for r in rows if not r['sub_a'])}")
print(f"   sub-step in A's view and still sub-step in B's: {gain(r for r in rows if r['sub_a'] and r['sub_b'])}")
print(f"   sub-step in A's view, not in B's: {gain(r for r in rows if r['sub_a'] and not r['sub_b'])}")
both = [r for r in rows if r["h2"] and r["hb"]]
print(f"precision on the {len(both)} cases both hit: click to target centre median A2 {st.median(centre_dist(A2[r['i']]) * r['s'] for r in both):.1f}, "
      f"B {st.median(centre_dist(B[r['i']]) * r['s'] for r in both):.1f} sent px (orig px {st.median(centre_dist(A2[r['i']]) for r in both):.1f} / "
      f"{st.median(centre_dist(B[r['i']]) for r in both):.1f}); in half-target units A2 "
      f"{st.median(centre_dist(A2[r['i']]) / (math.sqrt(r['tw'] * r['th']) / 2) for r in both):.2f}, B "
      f"{st.median(centre_dist(B[r['i']]) / (math.sqrt(r['tw'] * r['th']) / 2) for r in both):.2f}")
for k, R in (("A2", A2), ("B", B)):
    wr = [abs(R[i]["box"]["right"] - R[i]["box"]["left"]) * R_[i]["W"] / R_[i]["tw"] for i in range(N)]
    print(f"{k} box width / target width: median {st.median(wr):.2f}, over 1.5x {pct(v > 1.5 for v in wr)}%, over 3x {pct(v > 3 for v in wr)}%; "
          f"too-wide misses {sum(1 for i in range(N) if not R[i]['hit'] and holds_centre(R[i]))}")


def miss_kinds(M, label):
    print(f"{label} A2 misses {len(M)}: too-wide {sum(r['wide2'] for r in M)} fixed {pct(r['hb'] for r in M if r['wide2'])}%, "
          f"off-target {sum(not r['wide2'] for r in M)} fixed {pct(r['hb'] for r in M if not r['wide2'])}%")
    for nm, f in (("off-target <=15 sent px", lambda r: not r["wide2"] and r["d2"] <= 15),
                  ("off-target 15-60 sent px", lambda r: not r["wide2"] and 15 < r["d2"] <= 60),
                  ("off-target >60 sent px", lambda r: not r["wide2"] and r["d2"] > 60),
                  ("target centre in the window", lambda r: r["centre_in"]),
                  ("target fully in the window", lambda r: r["full_in"]),
                  ("target not visible in the window", lambda r: not r["visible"]),
                  ("target centre outside the window", lambda r: not r["centre_in"])):
        S = [r for r in M if f(r)]; print(f"   {nm}: {len(S)}, fixed {sum(r['hb'] for r in S)} ({pct(r['hb'] for r in S)}%)")


miss_kinds([r for r in rows if not r["h2"]], "Pro")
miss_kinds([r for r in v2rows if not r["h2"]], "v2 (same units)")
for app in sorted({r["app"] for r in rows}, key=lambda a: (-sum(R_[i]["app"] == a for i in R_), a)):
    S = [r for r in rows if r["app"] == app]
    print(f"app {app} ({S[0]['group']}): {gain(S)}; A1 {pct(r['h1'] for r in S)}")
for o in ("windows", "macos", "linux"):
    print(f"os {o}: {gain(r for r in rows if r['os'] == o)}")
for lo, hi in ((0, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
    print(f"A2 confidence {lo}-{hi}: {gain(r for r in rows if lo <= r['c2'] < hi)}")
for nm, f in (("half (2x)", lambda r: r["wf"] <= ss.ZOOM_F + 0.01), ("widened", lambda r: ss.ZOOM_F + 0.01 < r["wf"] < 0.9999),
              ("full screen", lambda r: r["wf"] >= 0.9999)):  # the same groups as screenspot.py zoomstats
    print(f"window {nm}: {gain(r for r in rows if f(r))}")

section("5. What zoom costs: the breaks (A2 hit -> B miss)")
brk = {r["i"] for r in rows if r["h2"] and not r["hb"]}
listed = {i for v in BREAKS.values() for i in v}
assert listed <= brk and len(listed) == sum(map(len, BREAKS.values())), sorted(listed - brk)
cls = {**{i: k for k, v in BREAKS.items() for i in v}, **{i: "precision" for i in brk - listed}}
print(f"breaks {len(brk)}: " + ", ".join(f"#{i}" for i in sorted(brk)))
for k, n in collections.Counter(cls.values()).most_common():
    S = [R_[i] for i in brk if cls[i] == k]
    print(f"{k}: {n} (" + ", ".join(f"{g} {sum(r['group'] == g for r in S)}" for g in ss.PRO_GROUPS) + f"; text {sum(r['type'] == 'text' for r in S)}, "
          f"icon {sum(r['type'] == 'icon' for r in S)}): " + ", ".join(f"#{r['i']}" for r in S))
prec = [R_[i] for i in brk if cls[i] == "precision"]
if prec:
    print(f"precision breaks: B within 1 target size of the box or too-wide in "
          f"{sum(1 for r in prec if r['dbo'] <= math.sqrt(r['tw'] * r['th']) or r['wideb'])} of {len(prec)}; "
          f"B distance median {st.median(r['db'] for r in prec):.1f} sent px")
print(f"breaks: target centre in B's window {sum(R_[i]['centre_in'] for i in brk)} of {len(brk)}; A2 confidence median "
      f"{st.median(R_[i]['c2'] for i in brk):.2f}; B distance median {st.median(R_[i]['db'] for i in brk):.1f} sent px")
print(f"B confidence lower than A2's in {sum(R_[i]['cb'] < R_[i]['c2'] for i in brk)} of {len(brk)} breaks; "
      f"higher in {sum(1 for r in rows if not r['h2'] and r['hb'] and r['cb'] > r['c2'])} of {sum(1 for r in rows if not r['h2'] and r['hb'])} fixes")

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
print(f"confidence under 0.5: B {sum(r['cb'] < 0.5 for r in rows)} cases {pct(r['hb'] for r in rows if r['cb'] < 0.5)}% right | "
      f"A2 {sum(r['c2'] < 0.5 for r in rows)} {pct(r['h2'] for r in rows if r['c2'] < 0.5)}% right")
agree = [r for r in rows if inbox(B[r["i"]]["point"], A2[r["i"]]["box"]) and inbox(A2[r["i"]]["point"], B[r["i"]]["box"])]
ag = {r["i"] for r in agree}; dis = [r for r in rows if r["i"] not in ag]
print(f"A2 and B agree (each click inside the other's box): {len(agree)}, B right {pct(r['hb'] for r in agree)}%; "
      f"disagree {len(dis)}: B right {pct(r['hb'] for r in dis)}%, A2 right {pct(r['h2'] for r in dis)}%")
maj = [(r["h1"] + r["h2"] + r["hb"]) >= 2 for r in rows]
print(f"post-hoc, not protocol: higher-confidence answer {pct(r['hb'] if r['cb'] >= r['c2'] else r['h2'] for r in rows)}%, "
      f"oracle A2 or B {pct(r['h2'] or r['hb'] for r in rows)}%, oracle any of three {pct(r['h1'] or r['h2'] or r['hb'] for r in rows)}%, "
      f"majority of three hits {pct(maj)}%")

section("7. Cost and speed")
tot = {k: sum(r["usage"]["cost"] for r in R.values()) for k, R in RUNS.items()}
tok = {k: sum(r["usage"]["input_tokens"] for r in R.values()) for k, R in RUNS.items()}
price = collections.Counter(round(r["usage"]["cost"] / r["usage"]["input_tokens"] * 1e6, 6) for R in RUNS.values() for r in R.values())
print(f"price per 1M input tokens {dict(price)} (output tokens not charged)")
print(f"cost A1 ${tot['A1']:.6f}, A2 ${tot['A2']:.6f}, B ${tot['B']:.6f}, run 2 (A2+B) ${tot['A2'] + tot['B']:.6f}, all three ${sum(tot.values()):.6f}")
print(f"input tokens A1 {tok['A1']:,}, A2 {tok['A2']:,}, B {tok['B']:,}; per click A ${tot['A2'] / N:.6f}, A+B ${(tot['A2'] + tot['B']) / N:.6f}; "
      f"mean tokens per call A {tok['A2'] / N:.0f}")
xs = [(A2[i]["sent_pixels"], A2[i]["usage"]["input_tokens"]) for i in range(N)]
mx, my = st.mean(x for x, _ in xs), st.mean(y for _, y in xs)
bslope = sum((x - mx) * (y - my) for x, y in xs) / sum((x - mx) ** 2 for x, _ in xs)
print(f"tokens = {my - bslope * mx:.0f} + {bslope:.6f} x sent pixels (max residual {max(abs(y - (my - bslope * mx) - bslope * x) for x, y in xs):.0f})")
print(f"B tokens - A2 tokens per case: {dict(sorted(collections.Counter(B[i]['usage']['input_tokens'] - A2[i]['usage']['input_tokens'] for i in range(N)).items()))}")
q = lambda v, p: sorted(v)[int(p * (len(v) - 1))]
for k, R in RUNS.items():
    v = [r["seconds"] for r in R.values()]
    print(f"latency {k}: median {st.median(v):.3f} s, p90 {q(v, .9):.3f}, max {max(v):.3f}")
ab = [A2[i]["seconds"] + B[i]["seconds"] for i in range(N)]
for k, Rs in (("pass 1", [A1]), ("run 2", [A2, B])):
    allr = [r for R in Rs for r in R.values()]
    t0 = min(ts(r) for r in allr); t1 = max(ts(r) + datetime.timedelta(seconds=r["wall_seconds"]) for r in allr)
    print(f"{k}: {t0.astimezone(CEST):%H:%M:%S}-{t1.astimezone(CEST):%H:%M:%S} CEST = {(t1 - t0).seconds} s with 4 workers")
print(f"A+B per click median {st.median(ab):.3f} s, p90 {q(ab, .9):.3f}")
logs = {p: (ss.OUT / f"{p}.log").read_text() for p in ("pass1", "pass2")}
bal = {p: (float(l.split(":")[1]) for l in logs[p].splitlines() if l.startswith("key balance before:")) for p in logs}
before1 = next(bal["pass1"]); before2 = next(bal["pass2"])
print(f"key balance before pass 1 ${before1:.6f}, before run 2 ${before2:.6f} (run logs); logged pass 1 ${tot['A1']:.6f}, run 2 ${tot['A2'] + tot['B']:.6f}; "
      f"expected once billing settles ${before1 - sum(tot.values()):.6f}")
t_first = ts(by_start(A1)[0])
late = [r for r in ss.read(ss.OUT / "pass0.jsonl") if datetime.timedelta(0) <= t_first - ts(r) <= datetime.timedelta(seconds=60)]
late_cost = sum(r["usage"]["cost"] for r in late)
print(f"between the runs the balance fell ${before1 - before2:.6f} for pass 1's ${tot['A1']:.6f} logged; a 3-case raw smoke (pass 0, cases "
      f"{sorted(r['i'] for r in late)}) ran {min((t_first - ts(r)).seconds for r in late)} s before pass 1 for ${late_cost:.6f}, after the balance reading")
print(f"expected now incl. that smoke ${before1 - sum(tot.values()) - late_cost:.6f}")
if "--balance" in sys.argv:
    v = jev.balance(); print(f"key balance now: {v if isinstance(v, str) else f'${v:.6f}'}")

section("8. What is left: B's misses")
Bm = [r for r in rows if not r["hb"]]
print(f"B misses {len(Bm)} (text {sum(r['type'] == 'text' for r in Bm)}, icon {sum(r['type'] == 'icon' for r in Bm)}): all three runs miss "
      f"{sum(not r['h1'] and not r['h2'] for r in Bm)}; target centre outside B's window {sum(not r['centre_in'] for r in Bm)}; "
      f"too-wide {sum(r['wideb'] for r in Bm)}")
for nm, f in (("within 5 sent px of the box", lambda r: r["db"] <= 5), ("5-15", lambda r: 5 < r["db"] <= 15), ("15-60", lambda r: 15 < r["db"] <= 60),
              ("60-200", lambda r: 60 < r["db"] <= 200), ("over 200", lambda r: r["db"] > 200)):
    S = [r for r in Bm if f(r)]
    print(f"   B click {nm}: {len(S)} (text {sum(r['type'] == 'text' for r in S)}, icon {sum(r['type'] == 'icon' for r in S)}, too-wide {sum(r['wideb'] for r in S)})")
print(f"B misses, target size in B's image median {st.median(r['tsz_b'] for r in Bm):.1f} px vs B hits {st.median(r['tsz_b'] for r in rows if r['hb']):.1f}; "
      f"still under one 0.01 step in B's view {sum(r['sub_b'] for r in Bm)}")
for lo, hi in MB:
    S = [r for r in Bm if lo <= r["tsz_b"] < hi]
    print(f"   B misses with target {lo}-{hi} px in B's image: {len(S)}")
# ceiling of a hypothetical third look (post-hoc diagnostic, not a run): a 4x window (quarter of each side)
# placed by the same rule on B's mapped box. Would the target centre be inside it?
def quarter(r):
    W, H = r["orig_size"]; b = {k: min(1.0, max(0.0, v)) for k, v in r["box"].items()}
    l, rr = sorted((b["left"], b["right"])); t, bo = sorted((b["top"], b["bottom"]))
    k = max(0.25, min(1.0, max(rr - l, bo - t) * 1.2)); cw, ch = max(1, round(k * W)), max(1, round(k * H))
    return (min(max(round((l + rr) / 2 * W - cw / 2), 0), W - cw), min(max(round((t + bo) / 2 * H - ch / 2), 0), H - ch), cw, ch)
cin = [r for r in Bm if window_has(quarter(B[r["i"]]), A2[r["i"]]["gt_px"])]
print(f"post-hoc: B misses whose target centre is inside a 4x window on B's answer: {len(cin)} of {len(Bm)}; of B hits {sum(window_has(quarter(B[r['i']]), A2[r['i']]['gt_px']) for r in rows if r['hb'])} of {sum(r['hb'] for r in rows)}")
print(f"near-miss share: B misses within one target size of the box {sum(1 for r in Bm if r['dbo'] <= math.sqrt(r['tw'] * r['th']))}, "
      f"within 3 target sizes {sum(1 for r in Bm if r['dbo'] <= 3 * math.sqrt(r['tw'] * r['th']))}")
for g in ss.PRO_GROUPS:
    S = [r for r in Bm if r["group"] == g]
    print(f"   {g}: B misses {len(S)}, far (>60 sent px) {sum(r['db'] > 60 for r in S)}, near (<=15) {sum(r['db'] <= 15 for r in S)}")

section("9. v2 and Pro side by side")
for nm, R2 in (("v2", v2rows), ("Pro", rows)):
    n = len(R2); up = sum(1 for r in R2 if not r["h2"] and r["hb"]); dn = sum(1 for r in R2 if r["h2"] and not r["hb"])
    a2m = [r for r in R2 if not r["h2"]]
    print(f"{nm}: n={n}, A1 {pct(r['h1'] for r in R2)}, A2 {pct(r['h2'] for r in R2)}, B {pct(r['hb'] for r in R2)}, fixed {up}, broken {dn}, "
          f"rerun flips {pct(r['h1'] != r['h2'] for r in R2)}%, zoom flips {pct(r['h2'] != r['hb'] for r in R2)}%, "
          f"A2 miss median distance {st.median(r['d2'] for r in a2m):.1f} sent px, A2 too-wide misses {pct(r['wide2'] for r in a2m)}% of misses, "
          f"target median {st.median(r['tsz_a'] for r in R2):.1f} px in A's image")
