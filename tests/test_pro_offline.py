"""Offline tests for the ScreenSpot-Pro path: jev.decide is mocked, no API calls, no spend.
  python3 tests/test_pro_offline.py"""
import json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import jev, screenspot as ss

ss.use("pro")
CASES = ss.load()
assert len(CASES) == 1581 and len({c["id"] for c in CASES}) == 1581
assert {c["group"] for c in CASES} == set(ss.PRO_GROUPS) and len(ss.CELLS) == 12
tmp = pathlib.Path(tempfile.mkdtemp())
ss.OUT = ss.DEV_LOG = tmp
jev.balance = lambda: 0.5  # never touch the network in tests


def official(c, point):
    """ScreenSpot-Pro eval_sample_positive_gt, lines 138-152, on the raw annotation."""
    bbox = c["raw_bbox"]
    img_size = c["img_size"]
    bbox = [bbox[0] / img_size[0], bbox[1] / img_size[1], bbox[2] / img_size[0], bbox[3] / img_size[1]]
    return (bbox[0] <= point[0] <= bbox[2]) and (bbox[1] <= point[1] <= bbox[3])


# 1. our truth box (run_one's [x, y, w, h] -> fractions) equals the official conversion, all cases
raw = {}
for f in sorted((ss.DATA / "annotations").glob("*.json")):
    for c in json.loads(f.read_text()):
        raw[c["id"]] = c
for c in CASES:
    r = raw[c["id"]]
    assert c["instruction"] == r["instruction"] and c["img_filename"] == r["img_filename"]
    W, H = c["img_size"]
    x, y, w, h = c["bbox"]
    ours = [x / W, y / H, (x + w) / W, (y + h) / H]
    want = [r["bbox"][0] / W, r["bbox"][1] / H, r["bbox"][2] / W, r["bbox"][3] / H]
    assert ours == want, (c["i"], ours, want)
    c["raw_bbox"] = r["bbox"]

# 2. a case whose image is on disk: raw call, hit and miss, same verdict as the official rule
i = next(c["i"] for c in CASES if (ss.DATA / ss.IMAGES / c["img_filename"]).exists())
c = CASES[i]
W, H = c["img_size"]
x1, y1, x2, y2 = c["raw_bbox"]


def answer(box, conf=0.8):
    return {"model": "typesafe/jev-1.14-test", "provider": "TypeSafe",
            "answers": {"target": {"type": "box", "box": box, "confidence": conf}},
            "usage": {"input_tokens": 4000, "output_tokens": 20, "cost": 0.00017}}


inner = {"left": (x1 + 1) / W, "right": (x2 - 1) / W, "top": (y1 + 1) / H, "bottom": (y2 - 1) / H}
far = {"left": 0.0, "right": 0.02, "top": 0.0, "bottom": 0.02} if x1 / W > 0.05 else \
      {"left": 0.97, "right": 0.99, "top": 0.97, "bottom": 0.99}
sent = []
for box, want in ((inner, True), (far, False)):
    jev.decide = lambda state, q, retries=4, box=box: (sent.append(state) or answer(box), 0.5, 1)
    r = ss.run_one(i, cases=CASES, out=tmp / "p.jsonl", pass_id="t", annotate_mode="none")
    assert r["status"] == "ok" and r["hit"] is want and official(c, r["point"]) is want, r
    assert r["bench"] == "pro" and r["group"] == c["group"] and r["case_id"] == c["id"]
    assert max(r["sent_size"]) <= jev.MAX_SIDE and r["instructions_sent"].endswith(ss.clean(c["instruction"]))

# 3. zoom stage B on Pro: same frozen window rule, answer mapped back to the full screenshot
a = ss.latest(ss.read(tmp / "p.jsonl"))[i]
a = dict(a, box=inner)
win = ss.zoom_window(a, W, H)
x0, y0, cw, ch = win
assert abs(cw / W - ss.ZOOM_F) < 0.01 or cw / W > ss.ZOOM_F  # half the screen, or widened for a big box
crop_box = {"left": ((x1 + x2) / 2 - 2 - x0) / cw, "right": ((x1 + x2) / 2 + 2 - x0) / cw,
            "top": ((y1 + y2) / 2 - 2 - y0) / ch, "bottom": ((y1 + y2) / 2 + 2 - y0) / ch}
jev.decide = lambda state, q, retries=4: (answer(crop_box), 0.5, 1)
z = ss.run_one(i, cases=CASES, out=tmp / "z.jsonl", pass_id="zt", annotate_mode="none", window=win, size=a["sent_size"])
assert z["status"] == "ok" and z["hit"] is True and official(c, z["point"]) and z["stage"] == "B", z
assert abs(z["point"][0] - (x1 + x2) / 2 / W) < 1e-9 and abs(z["point"][1] - (y1 + y2) / 2 / H) < 1e-9
assert z["sent_size"] == a["sent_size"]

# 4. results go to their own folder, never into the v2 results
ss.use("pro")
assert ss.OUT == ss.ROOT / "results" / "pro" and ss.DEV_LOG == ss.OUT / "runs.jsonl"
for typo in ("Pro", "pro2", ""):  # a typo exits before any path switches, never falls back to v2 files
    try:
        ss.use(typo)
        raise AssertionError(typo)
    except SystemExit:
        pass
assert ss.BENCH == "pro" and ss.OUT == ss.ROOT / "results" / "pro"
assert "code_rev" in r and "code_rev" in z  # every record names the code that ran
print("ALL PRO OFFLINE TESTS PASSED")
