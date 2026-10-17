"""Offline tests for stage C (the zoom step once more, Pro): jev.decide is mocked, no API calls, no spend.
  python3 tests/test_zoom4x_offline.py"""
import collections, json, pathlib, shutil, sys, tempfile, threading
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import jev, screenspot as ss

ss.use("pro")
CASES = ss.load()
REAL_B = ss.OUT / "zoom2.jsonl"
B = ss.latest(ss.read(REAL_B))
assert sorted(B) == list(range(1581)) and all(B[i]["status"] == "ok" and "box_crop" in B[i] for i in B)
raw = {}
for f in sorted((ss.DATA / "annotations").glob("*.json")):
    for c in json.loads(f.read_text()):
        raw[c["id"]] = c


def official(c, point):
    """ScreenSpot-Pro eval_sample_positive_gt, lines 138-152, on the raw annotation."""
    bbox, img_size = raw[c["id"]]["bbox"], raw[c["id"]]["img_size"]
    bbox = [bbox[0] / img_size[0], bbox[1] / img_size[1], bbox[2] / img_size[0], bbox[3] / img_size[1]]
    return (bbox[0] <= point[0] <= bbox[2]) and (bbox[1] <= point[1] <= bbox[3])


# 1. the window rule on every real stage-B answer: inside B's window, same aspect, half of B's side
#    unless B's box needs more, and it holds B's whole box + 10% margin whenever it is not capped
kinds = collections.Counter()
for i, b in B.items():
    W, H = b["orig_size"]
    bx, by, bw, bh = b["window"]
    x0, y0, cw, ch = ss.zoom_again_window(b)
    assert bx <= x0 and by <= y0 and x0 + cw <= bx + bw and y0 + ch <= by + bh, (i, b["window"], (x0, y0, cw, ch))
    assert abs(cw / bw - ch / bh) < 0.01, (i, cw / bw, ch / bh)
    k = cw / bw
    kinds["half of B" if abs(k - 0.5) < 0.01 else "same as B" if cw == bw else "widened"] += 1
    assert k >= 0.5 - 0.01
    bc = {kk: min(1.0, max(0.0, v)) for kk, v in b["box_crop"].items()}
    l, r = sorted((bx + bc["left"] * bw, bx + bc["right"] * bw))
    t, bo = sorted((by + bc["top"] * bh, by + bc["bottom"] * bh))
    if cw < bw:  # not capped at B's window: B's whole box fits, with its centre-based placement
        assert x0 - 1 <= l and r <= x0 + cw + 1 and y0 - 1 <= t and bo <= y0 + ch + 1, (i, (l, t, r, bo), (x0, y0, cw, ch))
print("C windows:", dict(kinds))

# 2. a mocked full run of all 1,581 cases: answer the target centre whenever it is inside C's window,
#    else the crop corner farthest from it. Every mapped click must land where expected, and every hit
#    must agree with the official rule on the raw annotation.
tmp = pathlib.Path(tempfile.mkdtemp())
ss.OUT = ss.DEV_LOG = tmp
shutil.copy(REAL_B, tmp / "zoom2.jsonl")
jev.balance = lambda: 0.5  # never touch the network in tests
EXPECT, WIN = {}, {}
for c in CASES:
    i = c["i"]
    x0, y0, cw, ch = WIN[i] = ss.zoom_again_window(B[i])
    gx, gy, gw, gh = c["bbox"]
    cx, cy = gx + gw / 2, gy + gh / 2
    if x0 <= cx <= x0 + cw and y0 <= cy <= y0 + ch:
        u, v = (cx - x0) / cw, (cy - y0) / ch
        EXPECT[i] = (True, {"left": u - 1e-4, "right": u + 1e-4, "top": v - 1e-4, "bottom": v + 1e-4})
    else:
        u = 0.98 if (cx - x0) / cw < 0.5 else 0.0
        v = 0.98 if (cy - y0) / ch < 0.5 else 0.0
        EXPECT[i] = (False, {"left": u, "right": u + 0.02, "top": v, "bottom": v + 0.02})
tl = threading.local()
_request = ss.request


def request(case, img):
    tl.i, tl.size = case["i"], img.size
    return _request(case, img)


def answer(box, conf=0.8):
    return {"model": "typesafe/jev-1.14-test", "provider": "TypeSafe",
            "answers": {"target": {"type": "box", "box": box, "confidence": conf}},
            "usage": {"input_tokens": 6000, "output_tokens": 20, "cost": 0.00016}}


ss.request = request
jev.decide = lambda state, q, retries=4: (answer(EXPECT[tl.i][1]), 0.5, 1)

# 2a. the cost cap stops the run early, then a resume finishes it without running any case twice
ss.run_zoom4x(2, workers=8, max_cost=0.002, annotate_mode="none")
first = ss.read(tmp / "zoom4x.jsonl")
assert 0 < len(first) < 100, len(first)
ss.run_zoom4x(2, workers=8, max_cost=1.0, annotate_mode="none")
C = ss.read(tmp / "zoom4x.jsonl")
assert len(C) == 1581 and len({r["i"] for r in C}) == 1581, (len(C), len({r["i"] for r in C}))
C = ss.latest(C)
inside = collections.Counter()
for c in CASES:
    i, r = c["i"], C[c["i"]]
    want, box = EXPECT[i]
    inside["B hit" if B[i]["hit"] else "B miss", want] += 1
    assert r["status"] == "ok" and r["stage"] == "C" and r["pass"] == "c2", r
    assert r["window"] == list(WIN[i]) and r["parent_window"] == B[i]["window"], i
    assert r["sent_size"] == B[i]["sent_size"], i
    x0, y0, cw, ch = WIN[i]
    W, H = c["img_size"]
    px = (x0 + (box["left"] + box["right"]) / 2 * cw) / W  # the answer mapped back by hand
    py = (y0 + (box["top"] + box["bottom"]) / 2 * ch) / H
    assert abs(r["point"][0] - px) < 1e-9 and abs(r["point"][1] - py) < 1e-9, (i, r["point"], (px, py))
    assert r["hit"] is official(c, r["point"]), (i, r["hit"], r["point"])
    if want:  # an answer on the target centre is a hit, on the exact centre
        gx, gy, gw, gh = c["bbox"]
        assert r["hit"] is True, i
        assert abs(r["point"][0] - (gx + gw / 2) / W) < 1e-6 and abs(r["point"][1] - (gy + gh / 2) / H) < 1e-6, i
print("mocked run: 1581 records, stage C, windows and mapping exact, every hit = the official rule")
print("target centre inside C's window:", {f"{k[0]}, {'inside' if k[1] else 'outside'}": v for k, v in sorted(inside.items())})

# 3. failure paths, in a fresh folder: a transient error, a 200 without a box and a provider error body
#    are infra_error (not scored, re-run on resume); malformed edges are a scored miss (wrong_format);
#    a fatal key error (402) stops the run at once
tmp2 = pathlib.Path(tempfile.mkdtemp())
ss.OUT = ss.DEV_LOG = tmp2
shutil.copy(REAL_B, tmp2 / "zoom2.jsonl")
FAIL = {}


def decide(state, q, retries=4):
    kind = FAIL.get(tl.i)
    if kind == "fatal":
        raise jev.JevError("HTTP 402: out of credit", status=402, attempts=1)
    if kind == "503":
        raise jev.JevError("HTTP 503 after 5 attempts", status=503, attempts=5)
    if kind == "no box":
        return {"answers": {}, "usage": {"input_tokens": 6000, "cost": 0.00016}}, 0.5, 1
    if kind == "error body":
        return {"error": {"message": "provider error"}}, 0.5, 1
    if kind == "bad edges":
        return answer({"left": "a", "right": 0.5, "top": 0.1, "bottom": 0.2}), 0.5, 1
    return answer(EXPECT[tl.i][1]), 0.5, 1


jev.decide = decide
out2, prog2 = tmp2 / "zoom4x.jsonl", tmp2 / "zoom4x.progress.json"
FAIL.update({0: "503", 1: "no box", 2: "error body", 3: "bad edges"})
ss.run_zoom4x(2, workers=4, max_cost=1.0, limit=10, annotate_mode="none")
r2 = ss.latest(ss.read(out2))
assert [r2[i]["status"] for i in range(10)] == ["infra_error"] * 3 + ["wrong_format"] + ["ok"] * 6, r2
assert r2[3]["hit"] is False and not any(r2[i].get("fatal") for i in range(3))
p = json.loads(prog2.read_text())
assert (p["infra_error"], p["wrong_format"], p["ok"], p["final"], p["stopped"]) == (3, 1, 6, True, False), p
assert ss.report(out2) is False  # infra errors and unrun cases: flagged, never a headline
FAIL.clear()
ss.run_zoom4x(2, workers=4, max_cost=1.0, limit=3, annotate_mode="none")  # resume: re-runs only 0, 1, 2
r2 = ss.latest(ss.read(out2))
assert len(ss.read(out2)) == 13 and [r2[i]["status"] for i in range(10)] == ["ok"] * 3 + ["wrong_format"] + ["ok"] * 6
FAIL.update({i: "fatal" for i in range(1581)})
ss.run_zoom4x(2, workers=4, max_cost=1.0, limit=200, annotate_mode="none")
new = ss.read(out2)[13:]
assert 1 <= len(new) <= 4 and all(r["status"] == "infra_error" and r["fatal"] for r in new), new  # one per worker at most
assert json.loads(prog2.read_text())["stopped"] is True
print(f"failure paths: transient + no box + error body re-run on resume, bad edges = scored miss, "
      f"402 stopped the run after {len(new)} call(s)")

# 4. the real results are untouched
assert ss.latest(ss.read(REAL_B)) == B
print("all stage-C offline tests passed")
