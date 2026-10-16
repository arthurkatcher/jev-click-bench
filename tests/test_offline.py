"""Offline tests: jev.decide is mocked, no API calls, no spend.  python3 tests/test_offline.py"""
import json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import jev, screenspot as ss

CASES = ss.load()
assert len(CASES) == 1272
tmp = pathlib.Path(tempfile.mkdtemp())
ss.OUT = tmp
jev.balance = lambda: 0.5  # never touch the network in tests


def answer(box, conf=0.8):
    return {"model": "typesafe/jev-1.14-test", "provider": "TypeSafe",
            "answers": {"target": {"type": "box", "box": box, "confidence": conf}},
            "usage": {"input_tokens": 4000, "output_tokens": 20, "cost": 0.00017}}


def gt_box(i, inset=0.25):
    c = CASES[i]
    from PIL import Image
    W, H = Image.open(ss.DATA / "screenspotv2_image" / c["img_filename"]).size
    x, y, w, h = c["bbox"]
    return {"left": (x + w * inset) / W, "right": (x + w * (1 - inset)) / W,
            "top": (y + h * inset) / H, "bottom": (y + h * (1 - inset)) / H}


def mock(fn):
    jev.decide = lambda state, questions, retries=4: fn(state, questions)


def one(i, out):
    return ss.run_one(i, cases=CASES, out=out, pass_id="t", annotate_mode="misses")


out = tmp / "t.jsonl"
# 1. correct box -> ok, hit, raw saved, identity fields present
mock(lambda s, q: (answer(gt_box(0)), 0.5, 1))
r = one(0, out)
assert r["status"] == "ok" and r["hit"] is True and r["raw"] and r["degenerate"] is False
assert r["instructions_sent"].startswith("In the screenshot, the UI element") and '"' not in r["instructions_sent"].split(":")[0]
# 2. far box -> ok, miss, annotation written for the miss
mock(lambda s, q: (answer({"left": 0.97, "right": 0.99, "top": 0.97, "bottom": 0.99}), 0.5, 1))
r = one(1, out)
assert r["status"] == "ok" and r["hit"] is False and (tmp / "t_case_0001.png").exists()
# 3. inverted box -> scored by centre (official rule), flagged degenerate, annotate does not crash
b = gt_box(2); b = {"left": b["right"], "right": b["left"], "top": b["bottom"], "bottom": b["top"]}
mock(lambda s, q: (answer(b), 0.5, 1))
r = one(2, out)
assert r["status"] == "ok" and r["hit"] is True and r["degenerate"] is True
# 4. malformed answers -> wrong_format, hit False, raw kept
mock(lambda s, q: ({"answers": {}}, 0.5, 1))
assert one(3, out)["status"] == "infra_error"
for i, bad in [(4, answer({"left": "0.1", "right": 0.2, "top": 0.1, "bottom": 0.2})),
               (5, answer({"left": float("nan"), "right": 0.2, "top": 0.1, "bottom": 0.2})),
]:
    mock(lambda s, q, bad=bad: (bad, 0.5, 1))
    r = one(i, out)
    assert r["status"] == "wrong_format" and r["hit"] is False and "raw" in r, (i, r)
# 4b. edges outside [0,1] are scored by centre (official rule) and flagged
mock(lambda s, q: (answer({"left": 0.97, "right": 1.01, "top": 0.97, "bottom": 1.003}), 0.5, 1))
r = one(7, out)
assert r["status"] == "ok" and r["out_of_range"] is True and r["hit"] is False
# 5. missing confidence is fine
a = answer(gt_box(8)); del a["answers"]["target"]["confidence"]
mock(lambda s, q: (a, 0.5, 1))
r = one(8, out)
assert r["status"] == "ok" and r["confidence"] is None
# 6. infra error -> recorded, not scored
def boom(s, q): raise jev.JevError("ReadTimeout", None, None, 5)
mock(boom)
r = one(9, out)
assert r["status"] == "infra_error" and r["hit"] is None and r["fatal"] is False
recs = ss.read(out)
assert all("OPENROUTER" not in json.dumps(x) and "sk-or" not in json.dumps(x) for x in recs)

# 7. run_all: 402 stops the run; resume skips done; infra_error is re-run; report flags incomplete
calls = []
def flaky(s, q):
    calls.append(1)
    if len(calls) == 6:
        raise jev.JevError("HTTP 402", 402, "out of credit", 1)
    return answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1
mock(flaky)
ss.run_all(99, workers=1, max_cost=1.0, limit=10, annotate_mode="none")
p = tmp / "pass99.jsonl"
recs = ss.read(p)
assert len(recs) == 6 and recs[-1]["status"] == "infra_error" and recs[-1]["fatal"], [x["status"] for x in recs]
assert ss.report(p) is False  # incomplete -> not a headline
calls.clear(); mock(lambda s, q: (calls.append(1) or answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1))
ss.run_all(99, workers=4, max_cost=1.0, limit=10, annotate_mode="none")
assert len(calls) == 10, len(calls)  # 5 done skipped, the 402 case re-run + 9 new... limit applies to todo
by = ss.latest(ss.read(p))
assert sum(1 for r in by.values() if r["status"] == "ok") == 15
# 8. cost cap stops early
calls.clear(); mock(lambda s, q: (calls.append(1) or answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1))
ss.run_all(98, workers=1, max_cost=0.0005, limit=20, annotate_mode="none")
assert len(calls) == 3, len(calls)
# 9. full fake pass with every box = truth -> 100% micro and macro, complete
mock(lambda s, q: (answer({"left": 0, "right": 0, "top": 0, "bottom": 0}), 0.3, 1))
full = tmp / "pass97.jsonl"
for c in CASES:
    from PIL import Image
    W, H = Image.open(ss.DATA / "screenspotv2_image" / c["img_filename"]).size
    x, y, w, h = c["bbox"]
    rec = {"pass": "97", "i": c["i"], "file": c["img_filename"], "instruction": c["instruction"], "status": "ok",
           "hit": True, "degenerate": False, "confidence": 0.9, "seconds": 0.5, "usage": {"cost": 0.00015},
           "prompt_version": ss.PROMPT_VERSION, "template_hash": ss.TEMPLATE_HASH}
    ss.write(full, rec)
assert ss.report(full) is True
# 10. float edge: case 12 right edge = 413/2360 = 0.175, centre of (0.01, 0.34) = 0.17500000000000002
c = CASES[12]
assert c["bbox"] == [341, 70, 72, 69]
mock(lambda s, q: (answer({"left": 0.01, "right": 0.34, "top": 0.05, "bottom": 0.07}), 0.5, 1))
r = one(12, out)
assert r["hit"] is False and r["hit_tolerant"] is True and r["on_edge"] is True, r  # strict official rule
# 11. a 200 body without answers (provider error object) -> infra_error, re-runnable, not a miss
for bad in ({"error": {"message": "upstream"}}, {"model": "x"}, "oops", None):
    mock(lambda s, q, bad=bad: (bad, 0.5, 1))
    r = one(13, out)
    assert r["status"] == "infra_error" and r["hit"] is None and r["fatal"] is False, r
# 12. unexpected exception from decide -> infra_error record, run continues
def weird(s, q): raise OSError("disk hiccup")
mock(weird)
assert one(14, out)["status"] == "infra_error"
# 13. decide(): chunked-encoding error and NaN Retry-After are retried, not raised raw
import requests, types
real_post = requests.post
seq = []
def fake_post(url, headers, data, timeout):
    seq.append(1)
    if len(seq) == 1:
        raise requests.exceptions.ChunkedEncodingError("reset")
    if len(seq) == 2:
        return types.SimpleNamespace(status_code=429, headers={"Retry-After": "nan"}, text="slow")
    return types.SimpleNamespace(status_code=200, headers={}, text="{}", json=lambda: answer(gt_box(0)))
import importlib; jev_mod = importlib.reload(jev)
jev_mod.time.sleep = lambda s: None
requests.post = fake_post
resp, secs, attempts = jev_mod.decide([], {})
assert attempts == 3 and resp["answers"]["target"]["box"], attempts
requests.post = lambda *a, **k: (_ for _ in ()).throw(requests.exceptions.ChunkedEncodingError("x"))
try:
    jev_mod.decide([], {}); raise AssertionError("should raise")
except jev_mod.JevError as e:
    assert not e.fatal
requests.post = real_post
# 14. report gates mixed models / prompt versions
mixed = tmp / "pass96.jsonl"
for line in open(full):
    rec = json.loads(line)
    if rec["i"] == 5:
        rec["model"] = "typesafe/jev-1.14-OTHER"
    ss.write(mixed, rec)
assert ss.report(mixed) is False
# 15. truncated last line is skipped, not a crash
with open(out, "a") as f:
    f.write('{"pass": "t", "i": 5, "sta')
assert len(ss.read(out)) > 0
# 16. compare two complete passes
assert ss.compare(full, full) == 1272

# ---- zoom method (stage B) ----
import base64, io
from PIL import Image
jev.decide = jev_mod.decide = None  # re-mocked below
importlib.reload(ss); ss.OUT = tmp; jev.balance = lambda: 0.5
W, H = 2560, 1440
B = lambda l, t, r, b: {"box": {"left": l, "top": t, "right": r, "bottom": b}}
# Z1. window: small box -> half the screen, centred; corner -> slid inside; wide box -> grown; full-width -> whole screen
assert ss.zoom_window(B(0.49, 0.49, 0.51, 0.51), W, H) == (640, 360, 1280, 720)
assert ss.zoom_window(B(0.0, 0.0, 0.02, 0.02), W, H) == (0, 0, 1280, 720)
assert ss.zoom_window(B(0.97, 0.97, 0.99, 0.99), W, H) == (1280, 720, 1280, 720)
x0, y0, cw, ch = ss.zoom_window(B(0.1, 0.5, 0.7, 0.55), W, H)  # 0.6 wide -> k = 0.72
assert (cw, ch) == (1843, 1037) and x0 <= 0.1 * W and x0 + cw >= 0.7 * W, (x0, cw)
assert ss.zoom_window(B(0.0, 0.1, 0.95, 0.15), W, H) == (0, 0, W, H)
x0, y0, cw, ch = ss.zoom_window(B(1.02, 0.5, 0.95, 0.4), W, H)  # inverted + out of range: sorted, clamped, inside
assert 0 <= x0 and x0 + cw <= W and 0 <= y0 and y0 + ch <= H and cw == 1280
# Z2. run_one with a window: sent image = A's sent size, box mapped back to the full screenshot, scored as usual
seen = []
def capture(fn):
    def f(s, q):
        seen.append(Image.open(io.BytesIO(base64.b64decode(s[1]["image_url"]["url"].split(",", 1)[1]))).size)
        return fn(s, q)
    return f
c = CASES[1]; Wc, Hc = Image.open(ss.DATA / "screenspotv2_image" / c["img_filename"]).size
x, y, w, h = c["bbox"]
a = {"box": {"left": (x + w * .4) / Wc, "right": (x + w * .6) / Wc, "top": (y + h * .4) / Hc, "bottom": (y + h * .6) / Hc}}
win = ss.zoom_window(a, Wc, Hc)
x0, y0, cw, ch = win
crop_box = {"left": (x + w * .3 - x0) / cw, "right": (x + w * .7 - x0) / cw,
            "top": (y + h * .3 - y0) / ch, "bottom": (y + h * .7 - y0) / ch}
mock(capture(lambda s, q: (answer(crop_box), 0.5, 1)))
r = ss.run_one(1, cases=CASES, out=tmp / "z.jsonl", pass_id="zt", annotate_mode="none", window=win, size=(1568, 1090))
assert seen[-1] == (1568, 1090) and r["hit"] is True and r["stage"] == "B" and r["box_crop"] == crop_box, r
assert abs(r["box"]["left"] - (x + w * .3) / Wc) < 1e-9 and abs(r["box"]["bottom"] - (y + h * .7) / Hc) < 1e-9
assert r["window"] == list(win) and r["window_frac"] == round(cw / Wc, 4)
# the same crop box read as a full-screen box would miss: mapping really is applied
assert not ss.inside([(crop_box["left"] + crop_box["right"]) / 2, (crop_box["top"] + crop_box["bottom"]) / 2], r["gt"])
# Z3. run_all --zoom: A into passN, B into zoomN, B image = A's sent size, raw mode untouched
seen.clear(); calls.clear()
mock(capture(lambda s, q: (calls.append(1) or answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1)))
ss.run_all(90, workers=1, max_cost=1.0, limit=4, annotate_mode="none", zoom=True)
pa, pz = ss.read(tmp / "pass90.jsonl"), ss.read(tmp / "zoom90.jsonl")
assert len(calls) == 8 and len(pa) == 4 and len(pz) == 4 and all(z["stage"] == "B" and z["pass"] == "z90" for z in pz)
assert seen[1::2] == [tuple(ra["sent_size"]) for ra in pa], (seen, [ra["sent_size"] for ra in pa])
assert all("stage" not in ra for ra in pa)
calls.clear(); ss.run_all(91, workers=1, max_cost=1.0, limit=3, annotate_mode="none")
assert len(calls) == 3 and not (tmp / "zoom91.jsonl").exists()
# Z4. cost cap counts A + B: 0.00017 per call, cap 0.0005 -> stops after 2 cases (4 calls)
calls.clear(); ss.run_all(92, workers=1, max_cost=0.0005, limit=20, annotate_mode="none", zoom=True)
assert len(calls) == 4, len(calls)
# Z5. resume: B infra error on case 0 -> rerun calls only B for it, A not repeated
calls.clear()
def b_fails_once(s, q):
    calls.append(1)
    if len(calls) == 2:
        raise jev.JevError("ReadTimeout", None, None, 5)
    return answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1
mock(b_fails_once)
ss.run_all(93, workers=1, max_cost=1.0, limit=3, annotate_mode="none", zoom=True)
assert ss.latest(ss.read(tmp / "zoom93.jsonl"))[0]["status"] == "infra_error"
calls.clear(); mock(lambda s, q: (calls.append(1) or answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1))
ss.run_all(93, workers=1, max_cost=1.0, limit=3, annotate_mode="none", zoom=True)
assert len(calls) == 1 + 2 * 2, len(calls)  # B of case 0, then A+B of cases 3, 4
assert sum(1 for x in ss.read(tmp / "pass93.jsonl") if x["i"] == 0) == 1
assert ss.latest(ss.read(tmp / "zoom93.jsonl"))[0]["status"] == "ok"
# Z6. A wrong_format -> zoom record is the same miss, no B call, no cost
calls.clear()
mock(lambda s, q: (calls.append(1) or answer({"left": "x", "right": 0.2, "top": 0.1, "bottom": 0.2}), 0.5, 1))
ss.run_all(94, workers=1, max_cost=1.0, limit=2, annotate_mode="none", zoom=True)
pz = ss.read(tmp / "zoom94.jsonl")
assert len(calls) == 2 and all(z["status"] == "wrong_format" and z["zoom_skipped"] and "usage" not in z for z in pz)
# Z7. a fatal 402 on B stops the run
calls.clear()
def b_402(s, q):
    calls.append(1)
    if len(calls) == 2:
        raise jev.JevError("HTTP 402", 402, "out of credit", 1)
    return answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1
mock(b_402)
ss.run_all(95, workers=1, max_cost=1.0, limit=10, annotate_mode="none", zoom=True)
assert len(calls) == 2, len(calls)
# Z8. report + compare read a zoom file like any pass
zfull = tmp / "zoom97.jsonl"
for line in open(full):
    rec = json.loads(line); rec.update(stage="B", **{"pass": "z97"}); ss.write(zfull, rec)
assert ss.report(zfull) is True and ss.compare(full, zfull) == 1272
# Z9. review round 1 fixes
assert abs(ss.mcnemar(60, 26) - 0.00032) < 0.00002 and ss.mcnemar(0, 0) == 1.0 and ss.mcnemar(5, 5) == 1.0
z = ss.latest(ss.read(tmp / "zoom90.jsonl"))[0]
assert z["zoom_f"] == 0.5 and z["zoom_margin"] == 0.1 and "code_rev" in z and z["out_of_crop"] is False
assert all(k not in x for x in ss.read(tmp / "zoom94.jsonl") for k in ("seconds", "wall_seconds", "attempts"))
mixed_z = tmp / "zoom96.jsonl"  # an edited constant between stop and resume -> INCOMPLETE
for line in open(zfull):
    rec = json.loads(line); rec.update(zoom_f=0.5 if rec["i"] else 0.4, zoom_margin=0.1); ss.write(mixed_z, rec)
assert ss.report(mixed_z) is False
other = tmp / "pass89.jsonl"  # a different resolved model -> compare refuses
for line in open(full):
    rec = json.loads(line); rec.update(model="typesafe/jev-1.14-NEWER"); ss.write(other, rec)
assert ss.compare(full, other) is None
# B pointing past the crop edge: flagged out_of_crop, mapped box still inside the screen -> not out_of_range
mock(lambda s, q: (answer({"left": 1.01, "right": 1.05, "top": 0.4, "bottom": 0.5}), 0.5, 1))
r = ss.run_one(1, cases=CASES, out=tmp / "z.jsonl", pass_id="zt", annotate_mode="none", window=(0, 0, 1180, 820),
               size=(1568, 1090))
assert r["out_of_crop"] is True and r["out_of_range"] is False, r
# progress file in zoom mode after a B-only resume: A total right, B counters present
mock(b_fails_once); calls.clear()
ss.run_all(88, workers=1, max_cost=1.0, limit=3, annotate_mode="none", zoom=True)
pr = json.loads((tmp / "pass88.progress.json").read_text())
assert pr["zoom_infra_error"] == 1 and pr["zoom_scored_this_run"] == 2 and pr["a_scored_total"] == 3, pr
mock(lambda s, q: (answer({"left": 0.4, "right": 0.6, "top": 0.4, "bottom": 0.6}), 0.3, 1))
ss.run_all(88, workers=1, max_cost=1.0, limit=1, annotate_mode="none", zoom=True)
pr = json.loads((tmp / "pass88.progress.json").read_text())
assert pr["a_resumed_this_run"] == 1 and pr["a_scored_total"] == 3 and pr["zoom_scored_total"] == 3, pr
print("\nALL OFFLINE TESTS PASSED")
