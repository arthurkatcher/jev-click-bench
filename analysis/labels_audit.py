"""Label audit of every case any run missed. A side note: the official answer key stays the score, never re-scored.
Rebuilds the two candidate sets from the records, checks the by-eye verdict files cover them exactly, maps the
codes to groups, prints per-run miss counts, the dataset scans and the recurring error patterns.
  python3 analysis/labels_audit.py        (verdicts: analysis/label-audit/verdicts_*.txt, write-up: analysis/LABELS-audit.md)"""
import collections, json, math, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import screenspot as ss

LA = ROOT / "analysis" / "label-audit"
N = 1272
RUNS = {k: ss.latest(ss.read(ss.OUT / f)) for k, f in (("A1", "pass1.jsonl"), ("A2", "pass2.jsonl"), ("B", "zoom2.jsonl"))}
A2 = RUNS["A2"]
GROUPS = [  # (group, verdict codes, is it a label issue?)
    ("answer-key error", {"KEYERROR"}, True),
    ("two valid answers", {"ARGUABLE"}, True),
    ("same control, key box covers part of it", {"SAME"}, True),
    ("loose or broken wording, key still the best answer", {"VAGUE"}, True),
    ("cannot verify", {"UNSURE"}, True),
    ("wrong element: model error", {"MODEL", "NEIGHBOUR"}, False),
    ("right element, click off", {"PRECISION", "WIDE", "EDGE"}, False),
    ("zoom crop cut the naming label", {"CROP"}, False),
]
# by eye, from the full-screen views: which run's answer is on the element a corrected key would mark
KEY_FIX = {458: {"A1", "A2", "B"}, 487: {"A1", "A2", "B"}, 1035: set(), 1037: {"B"}}
PATTERNS = {  # recurring model errors seen while auditing (case ids; each one is a missed case)
    "selected-state pull: picks the option that is currently selected or highlighted":
        [11, 61, 127, 129, 194, 218, 668, 688, 719, 799, 841, 1120, 1142, 1155, 1192],
    "previous/next and left-neighbour pull": [121, 437, 926, 1240],
    "label-name pull: picks the named noun instead of the control that acts on it":
        [856, 860, 906, 907, 910, 1009, 1038, 1159, 1195, 1264],
    "blend box: one box over two candidates, centre between them": [563, 869, 986],
    "group box: boxes a group or quantity instead of one item": [953, 1200],
}
TYPOS = {457: "calandar", 235: "massages", 94: "ore details", 385: "a emoji", 407: "softwares",
         833: "show previous (previews)", 247: "link attributes (Ink)"}


def dist(r):  # click to the nearest edge of the key box, original px (same as analysis/audit_run2.py)
    W, H = r["orig_size"]; x, y, w, h = r["gt_px"]; px, py = r["point"][0] * W, r["point"][1] * H
    return math.hypot(max(x - px, 0, px - x - w), max(y - py, 0, py - y - h))


def verdicts(name):
    out = {}
    for l in open(LA / name):
        if l.strip() and not l.startswith("#"):
            i, code, note = (x.strip() for x in l.split("|", 2))
            assert int(i) not in out, i
            out[int(i)] = (code, note)
    return out


# 1. candidate sets, rebuilt from the records
missed = [i for i in range(N) if any(not R[i]["hit"] for R in RUNS.values())]
far = lambda r: not r["hit"] and dist(r) > max(25, min(r["gt_px"][2], r["gt_px"][3]) / 2)
wrong = [i for i in missed if any(far(R[i]) for R in RUNS.values())]
near = [i for i in missed if i not in wrong]
assert wrong == json.load(open(LA / "cand_wrong_element.json")) and near == json.load(open(LA / "cand_near.json"))
V = {**verdicts("verdicts_wrong_element.txt"), **verdicts("verdicts_near.txt")}
assert sorted(V) == missed, "every missed case needs exactly one verdict"
codes = {c for g in GROUPS for c in g[1]}
assert {c for c, _ in V.values()} <= codes, {c for c, _ in V.values()} - codes
print(f"missed by at least one run: {len(missed)} (wrong-element set {len(wrong)}, near set {len(near)}); all have a verdict")
for nm, S in (("wrong-element", wrong), ("near", near)):
    print(f"  {nm} codes: {dict(collections.Counter(V[i][0] for i in S).most_common())}")

# 2. groups and per-run misses
miss = {k: {i for i in range(N) if not R[i]["hit"]} for k, R in RUNS.items()}
print(f"\n| Group | Cases | A1 misses | A2 misses | B misses | missed by all three |")
print("|---|---|---|---|---|---|")
tot = collections.Counter()
for g, cs, label in GROUPS + [("TOTAL label issues", {c for g in GROUPS if g[2] for c in g[1]}, None),
                               ("TOTAL label-fine", {c for g in GROUPS if not g[2] for c in g[1]}, None)]:
    S = {i for i in missed if V[i][0] in cs}
    allthree = sum(all(i in miss[k] for k in RUNS) for i in S)
    print(f"| {g} | {len(S)} | " + " | ".join(str(len(S & miss[k])) for k in RUNS) + f" | {allthree} |")
print(f"| all misses | {len(missed)} | " + " | ".join(str(len(miss[k])) for k in RUNS) + f" | {sum(all(i in miss[k] for k in RUNS) for i in missed)} |")
label_cases = sorted(i for i in missed if V[i][0] in {c for g in GROUPS if g[2] for c in g[1]})
print(f"\nlabel-issue cases by platform: {dict(collections.Counter(A2[i]['platform'] for i in label_cases))}")
for g, cs, label in GROUPS:
    if label:
        print(f"{g}: " + ", ".join(f"#{i}" for i in label_cases if V[i][0] in cs))
two = [i for i in wrong if V[i][0] in ("ARGUABLE", "SAME")]
print(f"two-answer + same-control cases in the wrong-element set: {len(two)}, missed by all three runs: "
      f"{sum(all(i in miss[k] for k in RUNS) for i in two)}")
print("answer-key errors, answers a corrected key would score as hits (side note, not a score): "
      + ", ".join(f"{k} {sum(k in v for v in KEY_FIX.values())}" for k in RUNS))
assert set(KEY_FIX) == {i for i in missed if V[i][0] == "KEYERROR"}

# 3. dataset scans (all 1,272 keys, not only the missed cases)
byfile = collections.defaultdict(list)
for i in range(N):
    byfile[A2[i]["file"]].append(i)
bybox = collections.defaultdict(set)
for i in range(N):
    bybox[tuple(A2[i]["gt_px"])].add(A2[i]["file"])


def iou_px(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    inter = max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0, min(ay + ah, by + bh) - max(ay, by))
    return inter / (aw * ah + bw * bh - inter)


pairs = [(i, j, iou_px(A2[i]["gt_px"], A2[j]["gt_px"])) for f, ids in byfile.items() for a, i in enumerate(ids) for j in ids[a + 1:]]
dup = [(i, j) for i, j, _ in pairs if A2[i]["instruction"].strip().lower() == A2[j]["instruction"].strip().lower()]
print(f"\nscreenshots {len(byfile)}, with more than one case {sum(len(v) > 1 for v in byfile.values())}")
print(f"key boxes shared by different screenshots: {[(sorted(i for i in range(N) if tuple(A2[i]['gt_px']) == b)) for b, fs in bybox.items() if len(fs) > 1]}")
print(f"same screenshot, different instruction: identical box {sum(1 for i, j, v in pairs if v > 0.999 and (i, j) not in dup)}, "
      f"overlapping box (IoU >= 0.3) {sum(1 for i, j, v in pairs if 0.3 <= v <= 0.999 and (i, j) not in dup)}")
print(f"duplicate test cases (same screenshot and instruction): {dup}, same key: {[A2[i]['gt_px'] == A2[j]['gt_px'] for i, j in dup]}")
over = {i: max(-A2[i]["gt_px"][0], -A2[i]["gt_px"][1], A2[i]["gt_px"][0] + A2[i]["gt_px"][2] - A2[i]["orig_size"][0],
                A2[i]["gt_px"][1] + A2[i]["gt_px"][3] - A2[i]["orig_size"][1]) for i in range(N)}
print(f"empty key boxes: {[i for i in range(N) if A2[i]['gt_px'][2] <= 0 or A2[i]['gt_px'][3] <= 0]}; key boxes past the image edge: "
      + ", ".join(f"#{i} by {v:g} px (hit by {sum(bool(R[i]['hit']) for R in RUNS.values())} of 3 runs)" for i, v in over.items() if v > 0))

# 4. recurring model errors
print()
for p, ids in PATTERNS.items():
    assert set(ids) <= set(missed), set(ids) - set(missed)
    print(f"{p}: {len(ids)} cases; misses A1 {sum(i in miss['A1'] for i in ids)}, A2 {sum(i in miss['A2'] for i in ids)}, "
          f"B {sum(i in miss['B'] for i in ids)}")
print("typos in instructions: " + ", ".join(f"#{i} '{t}'" for i, t in TYPOS.items()))
