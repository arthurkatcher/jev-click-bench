"""Label audit of every case the zoom answer B missed on ScreenSpot-Pro (905 cases), plus the UI language of all
1,581 screens. A side note: the official answer key stays the score, never re-scored.
Checks that the by-eye verdict files cover B's misses exactly, maps the codes to groups and prints every table in
analysis/LABELS-audit-pro.md: groups, codes against geometry, what Jev confused, unlabelled targets, accuracy by
UI language, and the dataset scans over all 1,581 keys.
  python3 analysis/labels_audit_pro.py
Verdicts: analysis/label-audit-pro/verdicts/batch_NN.txt (one reviewer per app batch, instructions in
analysis/label-audit-pro/INSTRUCTIONS.md); languages: analysis/label-audit-pro/lang/batch_NN.txt."""
import collections, glob, hashlib, itertools, json, math, pathlib, statistics as st, sys
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import screenspot as ss

ss.use("pro")
N = 1581
LA = ROOT / "analysis" / "label-audit-pro"
RUNS = {k: ss.latest(ss.read(ss.OUT / f)) for k, f in (("A1", "pass1.jsonl"), ("A2", "pass2.jsonl"), ("B", "zoom2.jsonl"))}
A1, A2, B = RUNS["A1"], RUNS["A2"], RUNS["B"]
GROUPS = [  # (group, verdict codes, is it a label issue?), the same groups as the v2 audit
    ("answer key and instruction disagree", {"KEYERROR"}, True),
    ("two valid answers", {"ARGUABLE"}, True),
    ("same control, key box covers part of it", {"SAME"}, True),
    ("loose or broken wording, key still the best answer", {"VAGUE"}, True),
    ("cannot verify", {"UNSURE"}, True),
    ("same request keyed to two different elements", {"TWIN"}, True),
    ("wrong element: model error", {"MODEL", "NEIGHBOUR"}, False),
    ("right element, click off", {"PRECISION", "WIDE", "EDGE"}, False),
    ("zoom crop cut the naming label", {"CROP"}, False),
]
# by eye, my quality pass over the reviewers' verdicts (Oct 17); every change is printed. Plain typos whose meaning is
# clear are not label issues (the v2 rule), so those cases keep the model code the reviewer gave or named in the note.
OVERRIDE = {  # case: (code, tag, reason)
    322: ("NEIGHBOUR", "-", "typo 'cel'"), 335: ("WIDE", "-", "typo 'th'"), 480: ("MODEL", "OTHER", "typo 'featues'"),
    568: ("NEIGHBOUR", "-", "typo 'recepient'"), 591: ("PRECISION", "-", "typo 'volumn'"), 633: ("WIDE", "-", "typo 'dropdows'"),
    656: ("WIDE", "-", "typo 'delect'"), 676: ("WIDE", "-", "typo 'delect'"), 726: ("EDGE", "-", "typos 'colse', 'grah1'"),
    778: ("WIDE", "-", "typo 'hade'"), 796: ("MODEL", "OTHER", "typo 'backgroud'"), 860: ("MODEL", "SAMEGROUP", "typo 'Underlying' (Underline)"),
    975: ("WIDE", "-", "typos 'refrash', 'hierachy'"), 984: ("WIDE", "-", "typo 'pycharmto'"), 1002: ("NEIGHBOUR", "-", "typo 'hierachy'"),
    1004: ("MODEL", "SAMEGROUP", "typo 'excute'"), 1005: ("WIDE", "-", "typos 'reposity', 'pycahrm'"), 1008: ("WIDE", "-", "typo 'plost'"),
    1061: ("MODEL", "SAMEGROUP", "typo 'Progranmer'"), 1375: ("MODEL", "SAMETEXT", "typo 'Learderboard'"), 1438: ("WIDE", "-", "typo 'volumn'"),
    1439: ("NEIGHBOUR", "-", "typo 'found' (find)"), 1526: ("NEIGHBOUR", "-", "typo 'fuction'"), 1556: ("WIDE", "-", "typo 'previoius'"),
    1493: ("ARGUABLE", "SAMETEXT", "typo 'volumn'; B aims at the nav pane's Data (D:), which also opens D"),
    759: ("ARGUABLE", "SAMETEXT", "two scatter (散点图) controls, gallery button and fly-out item; B's box spans both (blend box, as v2's #563)"),
    992: ("TWIN", "-", "twin #1025 keys the File tab"), 1025: ("TWIN", "-", "twin #992 keys the Problems title"),
    # 639/666 (MATLAB) and 1042/1069 (Quartus) were TWIN until the upstream check (Oct 17, upstream-issue-pro/VERIFY.md):
    # a menu is open in one shot and closed in the other, and each key is right for its own screen. So 639 and 1069
    # keep their reviewers' codes (PRECISION; MODEL SAMEGROUP).
    # batch 07 coded the same Origin pattern MODEL (754, 755, 765, 770) or PRECISION (these): a full-height column box
    # whose centre lands mid-screen, ~1000 px from the toolbar key. Not a click slightly off, so MODEL for all of them.
    **{i: ("MODEL", "OTHER", "full-height column box, click mid-screen ~1000 px from the key")
       for i in (711, 728, 730, 738, 739, 758)},
}
# by eye: which run's answer is on the element a corrected key would mark (#657: A2's raw hit is on the wrong key)
KEY_FIX = {133: set(), 491: set(), 657: {"B"}}
# by eye: two-answer cases where B's click is on the other valid element (the rest aim at it and land beside it)
ON_OTHER = {5, 20, 121, 184, 199, 257, 629, 686, 869, 877, 890, 937, 1255, 1297, 1313, 1443, 1467}
CODES = set().union(*(g[1] for g in GROUPS))
LABEL = set().union(*(g[1] for g in GROUPS if g[2]))
TAGGED = {"MODEL", "ARGUABLE", "CROP"}
TAGS = {"SAMETEXT", "LOOKALIKE", "RELATED", "SAMEGROUP", "SELECTED", "OTHER"}
LANGS = ("EN", "ZH", "OTHER")


def pct(xs):
    xs = list(xs)
    return round(100 * sum(map(bool, xs)) / len(xs), 1) if xs else None


def parse(path, nfields):
    out = {}
    for l in open(path, encoding="utf-8"):
        if l.strip() and not l.lstrip().startswith("#"):
            parts = [x.strip() for x in l.split("|", nfields - 1)]
            assert len(parts) == nfields, (path, l)
            i = int(parts[0])
            assert i not in out, (path, i)
            out[i] = parts[1:]
    return out


def dist_sent(r):  # click to the nearest edge of the key box, px in A's sent image
    W, H = r["orig_size"]; x, y, w, h = r["gt_px"]; px, py = r["point"][0] * W, r["point"][1] * H
    return math.hypot(max(x - px, 0, px - x - w), max(y - py, 0, py - y - h)) * A2[r["i"]]["scale"]


def holds_centre(r):
    W, H = r["orig_size"]; x, y, w, h = r["gt_px"]
    l, rr = sorted((r["box"]["left"], r["box"]["right"])); t, bo = sorted((r["box"]["top"], r["box"]["bottom"]))
    return l <= (x + w / 2) / W <= rr and t <= (y + h / 2) / H <= bo


def centre_in_window(i):
    x0, y0, cw, ch = B[i]["window"]; x, y, w, h = A2[i]["gt_px"]
    return x0 <= x + w / 2 <= x0 + cw and y0 <= y + h / 2 <= y0 + ch


# 1. coverage and format
missB = [i for i in range(N) if not B[i]["hit"]]
V, L = {}, {}
for f in sorted(glob.glob(str(LA / "verdicts" / "batch_*.txt"))):
    v = parse(f, 6); assert not set(v) & set(V), (f, sorted(set(v) & set(V))[:5]); V.update(v)
for f in sorted(glob.glob(str(LA / "lang" / "batch_*.txt"))):
    v = parse(f, 2); assert not set(v) & set(L), (f, sorted(set(v) & set(L))[:5]); L.update({i: x[0] for i, x in v.items()})
assert sorted(V) == missB, f"verdicts must cover B's misses exactly: missing {sorted(set(missB) - set(V))[:10]}, extra {sorted(set(V) - set(missB))[:10]}"
assert sorted(L) == list(range(N)), f"languages must cover all cases: missing {sorted(set(range(N)) - set(L))[:10]}"
for i, (c, tag, named, lang, note) in V.items():
    assert c in CODES - {"TWIN"} and named in ("Y", "N") and lang in LANGS and note, (i, c, named, lang)
    assert (tag in TAGS) if c in TAGGED else tag == "-", (i, c, tag)
assert set(L.values()) <= set(LANGS), set(L.values())
for i, (c, t, why) in sorted(OVERRIDE.items()):
    print(f"override #{i}: {V[i][0]} {V[i][1]} -> {c} {t} ({why})")
    V[i] = [c, t] + V[i][2:]
code = {i: v[0] for i, v in V.items()}
agree = sum(V[i][3] == L[i] for i in V)
print(f"B misses {len(missB)}: all have one verdict; UI language for all {N} cases; the two language looks agree on {agree} of {len(V)}"
      + (f" (differ: {', '.join(f'#{i} {V[i][3]}/{L[i]}' for i in V if V[i][3] != L[i])})" if agree < len(V) else ""))
print("codes:", dict(collections.Counter(code.values()).most_common()))

# 2. groups (the v2 table, for B's misses) and which other runs missed the same case
miss = {k: {i for i in range(N) if not R[i]["hit"]} for k, R in RUNS.items()}
print("\n| Group | B misses | A2 also missed | A1 also missed | All three missed | Text | Icon |")
print("|---|---|---|---|---|---|---|")
rows = GROUPS + [("TOTAL label issues", LABEL, None), ("TOTAL label-fine", CODES - LABEL, None)]
for g, cs, _ in rows:
    S = [i for i in missB if code[i] in cs]
    print(f"| {g} | {len(S)} | {sum(i in miss['A2'] for i in S)} | {sum(i in miss['A1'] for i in S)} | "
          f"{sum(i in miss['A1'] and i in miss['A2'] for i in S)} | {sum(A2[i]['type'] == 'text' for i in S)} | {sum(A2[i]['type'] == 'icon' for i in S)} |")
print(f"| all B misses | {len(missB)} | {sum(i in miss['A2'] for i in missB)} | {sum(i in miss['A1'] for i in missB)} | "
      f"{sum(i in miss['A1'] and i in miss['A2'] for i in missB)} | {sum(A2[i]['type'] == 'text' for i in missB)} | {sum(A2[i]['type'] == 'icon' for i in missB)} |")
KIND = {"wrong element": {"MODEL", "NEIGHBOUR"}, "click off": {"PRECISION", "WIDE", "EDGE"}, "crop": {"CROP"}, "label issue": LABEL}
print("\n| Group | B misses | Wrong element | Right element, click off | Crop cut the label | Label issue |")
print("|---|---|---|---|---|---|")
for g in ("CAD", "Dev", "Creative", "Scientific", "Office", "OS", "text", "icon"):
    S = [i for i in missB if g in (A2[i]["group"], A2[i]["type"])]
    print(f"| {g} | {len(S)} | " + " | ".join(f"{sum(code[i] in cs for i in S)} ({pct(code[i] in cs for i in S)}%)" for cs in KIND.values()) + " |")
lab = [i for i in missB if code[i] in LABEL]
print(f"\nlabel issues {len(lab)} of {len(missB)} B misses ({100 * len(lab) / len(missB):.1f}%), {100 * len(lab) / N:.2f}% of all cases; "
      f"by group {dict(collections.Counter(A2[i]['group'] for i in lab))}")
for g, cs, isl in GROUPS:
    if isl:
        S = [i for i in missB if code[i] in cs]
        print(f"{g} ({len(S)}): " + "; ".join(f"#{i} {A2[i]['source']}: {V[i][4]}" for i in S))
assert set(KEY_FIX) == {i for i in missB if code[i] == "KEYERROR"} and ON_OTHER <= {i for i in missB if code[i] == "ARGUABLE"}
print("answer-key errors, answers a corrected key would score as hits (side note, not a score): "
      + ", ".join(f"{k} {sum(k in v for v in KEY_FIX.values())}" for k in RUNS)
      + f"; raw hits that sit on a wrong key: {[(i, k) for i in KEY_FIX for k in RUNS if RUNS[k][i]['hit']]}")
two = [i for i in missB if code[i] == "ARGUABLE"]
same_c = [i for i in missB if code[i] == "SAME"]
print(f"two valid answers: B's click on the other valid element in {len(ON_OTHER)} of {len(two)}; same control: {len(same_c)} clicks "
      f"that work on a real screen. Upper bound of what label issues cost B: {len(ON_OTHER) + len(same_c) + sum('B' in v for v in KEY_FIX.values())} "
      f"hits = {100 * (len(ON_OTHER) + len(same_c) + sum('B' in v for v in KEY_FIX.values())) / N:.2f} pp")

# 3. codes against geometry (consistency of the by-eye codes with the recorded answers)
print("\n| Code | n | B click to key box, median sent px | B box holds the key centre | key centre outside B's window |")
print("|---|---|---|---|---|")
for c, n in collections.Counter(code.values()).most_common():
    S = [i for i in missB if code[i] == c]
    print(f"| {c} | {n} | {st.median(dist_sent(B[i]) for i in S):.1f} | {sum(holds_centre(B[i]) for i in S)} | {sum(not centre_in_window(i) for i in S)} |")
out_w = [i for i in missB if not centre_in_window(i)]
print(f"B misses with the key centre outside B's window: {len(out_w)}, codes {dict(collections.Counter(code[i] for i in out_w).most_common())}")

# 3b. the 55 breaks (A2 hit, B miss): the reviewers' codes against the classes given by eye in audit_pro_run2.py section 5
BREAKS = {"precision": {"EDGE", "WIDE", "PRECISION", "SAME"}, "neighbour pick": {"NEIGHBOUR"}, "wrong element far away": {"MODEL"},
          "ambiguous label": {"ARGUABLE", "VAGUE", "UNSURE"}, "answer-key error": {"KEYERROR"}}
MINE = {"neighbour pick": [98, 120, 325, 337, 437, 844, 857, 1020, 1091, 1095, 1238, 1256, 1279, 1526],  # copied from audit_pro_run2.py
        "wrong element far away": [972, 1123, 1284, 1431, 1580], "ambiguous label": [759], "answer-key error": [657]}
breaks = [i for i in range(N) if A2[i]["hit"] and not B[i]["hit"]]
mine = {i: k for k, ids in MINE.items() for i in ids}
mine.update({i: "precision" for i in breaks if i not in mine})
same = [i for i in breaks if code[i] in BREAKS[mine[i]]]
print(f"\nbreaks {len(breaks)}: the reviewers' code matches the audit's class in {len(same)}; differ: "
      + "; ".join(f"#{i} audit {mine[i]}, reviewer {code[i]}" for i in breaks if i not in same))

# 4. what Jev confused the target with (MODEL, ARGUABLE, CROP), and unlabelled targets
tag = {i: V[i][1] for i in missB if code[i] in TAGGED}
print("\ntags:", dict(collections.Counter(tag.values()).most_common()))
for c in sorted(TAGGED):
    S = [i for i in tag if code[i] == c]
    if S:
        print(f"   {c}: {dict(collections.Counter(tag[i] for i in S).most_common())}")
named = {i: V[i][2] for i in missB}
for t in ("text", "icon"):
    S = [i for i in missB if A2[i]["type"] == t]
    print(f"named by visible text, {t} B misses: Y {sum(named[i] == 'Y' for i in S)}, N {sum(named[i] == 'N' for i in S)}")
for nm, cs in (("wrong element", {"MODEL", "NEIGHBOUR"}), ("right element, click off", {"PRECISION", "WIDE", "EDGE"}), ("label issue", LABEL)):
    S = [i for i in missB if code[i] in cs]
    print(f"   {nm} ({len(S)}): named N {sum(named[i] == 'N' for i in S)} ({pct(named[i] == 'N' for i in S)}%)")

# 5. UI language, all 1,581 cases
print("\nUI language:", dict(collections.Counter(L.values())))
apps = collections.OrderedDict()
for i in range(N):
    apps.setdefault(A2[i]["source"], []).append(i)
print("by app: " + ", ".join(f"{a} " + "/".join(f"{k}{sum(L[i] == k for i in ids)}" for k in LANGS if any(L[i] == k for i in ids)) for a, ids in apps.items()))
for k in LANGS:
    S = [i for i in range(N) if L[i] == k]
    if S:
        lo, hi = ss.wilson(sum(B[i]["hit"] for i in S), len(S))
        print(f"{k}: n={len(S)} (text {sum(A2[i]['type'] == 'text' for i in S)}, icon {sum(A2[i]['type'] == 'icon' for i in S)}), "
              f"A1 {pct(A1[i]['hit'] for i in S)}, A2 {pct(A2[i]['hit'] for i in S)}, B {pct(B[i]['hit'] for i in S)} (Wilson {lo:.1f}-{hi:.1f}); "
              f"text B {pct(B[i]['hit'] for i in S if A2[i]['type'] == 'text')}, icon B {pct(B[i]['hit'] for i in S if A2[i]['type'] == 'icon')}")
mixed = [a for a, ids in apps.items() if len({L[i] for i in ids}) > 1]
for a in mixed:
    for k in LANGS:
        S = [i for i in apps[a] if L[i] == k]
        if S:
            print(f"   within {a}, {k}: n={len(S)}, A2 {pct(A2[i]['hit'] for i in S)}, B {pct(B[i]['hit'] for i in S)}")
zh = [i for i in missB if L[i] == "ZH"]
print(f"B misses on ZH screens {len(zh)}: codes {dict(collections.Counter(code[i] for i in zh).most_common())}")
en = [i for i in missB if L[i] == "EN"]
print(f"B misses on EN screens {len(en)}: codes {dict(collections.Counter(code[i] for i in en).most_common())}")

# 6. dataset scans over all 1,581 keys
raw = {}
for f in sorted((ss.DATA / "annotations").glob("*.json")):
    for c in json.loads(f.read_text()):
        raw[c["id"]] = c
files = [A2[i]["file"] for i in range(N)]
print(f"\nscreenshots: {len(set(files))} files for {N} cases")
digest = collections.defaultdict(list)
for i in range(N):
    digest[hashlib.md5((ss.DATA / ss.IMAGES / files[i]).read_bytes()).hexdigest()].append(i)
print(f"byte-identical screenshots used by more than one case: {[v for v in digest.values() if len(v) > 1]}")
dig = {i: d for d, ids in digest.items() for i in ids}


def iou(a, b):  # two cases' key boxes, in fractions of their screenshots
    (ax, ay, aw, ah), (bx, by, bw, bh) = [[v / s for v, s in zip(ss_["gt_px"], ss_["orig_size"] * 2)] for ss_ in (A2[a], A2[b])]
    w = max(0, min(ax + aw, bx + bw) - max(ax, bx)); h = max(0, min(ay + ah, by + bh) - max(ay, by))
    return w * h / (aw * ah + bw * bh - w * h)


def screen_diff(a, b):  # mean absolute grey difference of 96x54 thumbnails, 0-255 (0 = the same picture)
    t = [Image.open(ss.DATA / ss.IMAGES / files[i]).convert("L").resize((96, 54), Image.BILINEAR).tobytes() for i in (a, b)]
    return sum(abs(x - y) for x, y in zip(*t)) / len(t[0])


for ids in (v for v in digest.values() if len(v) > 1):
    for a, b in itertools.combinations(ids, 2):
        if iou(a, b) >= 0.3:
            print(f"same screenshot, overlapping keys (IoU {iou(a, b):.2f}): #{a} '{A2[a]['instruction']}' / #{b} '{A2[b]['instruction']}'")
inst = collections.defaultdict(list)
for i in range(N):
    inst[(A2[i]["source"], " ".join(A2[i]["instruction"].lower().split()))].append(i)
print(f"same app and same instruction: {sum(len(v) > 1 for v in inst.values())} groups "
      "(same screen = byte-identical, or the same size and under 2/255 apart on 96x54 grey thumbnails)")
kinds = collections.defaultdict(list)
for (app, text), ids in inst.items():
    for a, b in itertools.combinations(ids, 2):
        d = 0.0 if dig[a] == dig[b] else screen_diff(a, b)
        same = A2[a]["orig_size"] == A2[b]["orig_size"] and d < 2
        kind = ("other screen" if not same else "duplicate case (same key)" if iou(a, b) >= 0.5
                else "keys apart on a near-identical screen" if iou(a, b) < 0.1 else "same screen, keys partly overlap")
        kinds[kind].append(f"#{a}/#{b}")
        print(f"   #{a} / #{b} {app} '{text}': screenshots {d:.1f}/255 apart"
              + ("" if A2[a]["orig_size"] == A2[b]["orig_size"] else ", other size")
              + f"; keys IoU {iou(a, b):.2f}; B {'hit' if B[a]['hit'] else 'miss'}/{'hit' if B[b]['hit'] else 'miss'} = {kind}")
print("   " + "; ".join(f"{k}: {len(v)} ({', '.join(v)})" for k, v in kinds.items()))
print("   by eye (upstream check, Oct 17): #639/#666 and #1042/#1069 differ by an open menu and each key is right for its "
      "own screen; #992/#1025 is the one real contradiction")
boxes = collections.defaultdict(list)
for i in range(N):
    boxes[tuple(raw[A2[i]["case_id"]]["bbox"])].append(i)
print("the same key box on different screenshots: "
      + str([v for v in boxes.values() if len({dig[i] for i in v}) > 1]))
for i in range(N):
    W, H = A2[i]["orig_size"]; x, y, w, h = A2[i]["gt_px"]
    if x < 0 or y < 0 or x + w > W or y + h > H or w <= 0 or h <= 0:
        print(f"key box outside the screenshot or empty: #{i} {raw[A2[i]['case_id']]['bbox']} on {W}x{H}, hits A1/A2/B "
              f"{A1[i]['hit']}/{A2[i]['hit']}/{B[i]['hit']}")
small = [i for i in range(N) if min(A2[i]["gt_px"][2], A2[i]["gt_px"][3]) < 8]
print(f"key boxes under 8 original px on a side: {len(small)} ({', '.join(f'#{i}' for i in small[:12])}{', ...' if len(small) > 12 else ''})")
