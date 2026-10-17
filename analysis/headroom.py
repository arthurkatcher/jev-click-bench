"""Headroom after zoom, from the three v2 runs. Offline, no API. Post-hoc: these are ceilings and
diagnostics, never a protocol (any rule picked from them would be tuned on the test set).
  python3 analysis/headroom.py"""
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import screenspot as ss

R = {k: ss.latest(ss.read(ss.OUT / f)) for k, f in (("A1", "pass1.jsonl"), ("A2", "pass2.jsonl"), ("B", "zoom2.jsonl"))}
N = 1272


def sides(b):
    l, r = sorted((b["left"], b["right"])); t, bo = sorted((b["top"], b["bottom"]))
    return l, t, r, bo


def inside(p, b):
    l, t, r, bo = sides(b)
    return l <= p[0] <= r and t <= p[1] <= bo


def agree(x, y, i):  # each click inside the other's box
    return inside(R[x][i]["point"], R[y][i]["box"]) and inside(R[y][i]["point"], R[x][i]["box"])


H = lambda k, i: R[k][i]["hit"]
acc = lambda f: 100 * sum(bool(f(i)) for i in range(N)) / N


def vote(i):  # majority of A1, A2, B: take A2 when both raw runs agree against B
    if not agree("A2", "B", i) and agree("A1", "A2", i) and not agree("A1", "B", i):
        return H("A2", i)
    return H("B", i)


print(f"always B                      {acc(lambda i: H('B', i)):.2f}")
print(f"majority vote A1+A2 vs B      {acc(vote):.2f}")
print(f"skip zoom on mobile           {acc(lambda i: H('A2', i) if R['B'][i]['platform'] == 'mobile' else H('B', i)):.2f}")
print(f"oracle A1 or A2               {acc(lambda i: H('A1', i) or H('A2', i)):.2f}")
print(f"oracle any of three           {acc(lambda i: H('A1', i) or H('A2', i) or H('B', i)):.2f}")
dis = [i for i in range(N) if not agree("A2", "B", i)]
sub = [i for i in dis if agree("A1", "A2", i) and not agree("A1", "B", i)]
print(f"A2/B disagree {len(dis)}; A1 sides with A2 in {len(sub)}: B right {sum(H('B', i) for i in sub)}, A2 right {sum(H('A2', i) for i in sub)}")
print("target size in the image B saw (sqrt area, px):")
rows = []
for i in range(N):
    b = R["B"][i]; x, y, w, h = b["gt_px"]; s = b["sent_size"][0] / b["window"][2]
    rows.append((math.sqrt(w * h) * s, H("B", i)))
for lo, hi in ((0, 45), (45, 60), (60, 80), (80, 120), (120, 1e9)):
    sub = [r for r in rows if lo <= r[0] < hi]
    print(f"  {lo}-{hi if hi < 1e9 else ''} px: n={len(sub)}  B {100 * sum(r[1] for r in sub) / len(sub):.1f}%")
