import pathlib
ROOT = str(pathlib.Path(__file__).resolve().parents[2])
import json, math, sys
import numpy as np
recs = {}
for l in open(ROOT + '/results/pass1.jsonl'):
    try: r = json.loads(l)
    except: continue
    if r.get('status') in ('ok','wrong_format'): recs[r['i']] = r
R = list(recs.values()); assert len(R) == 1272
def tsize(r, scale):  # target size in px of the image Jev sees: sqrt(area)
    W,H = r['orig_size']; x1,y1,x2,y2 = r['gt']
    return math.sqrt((x2-x1)*W*(y2-y1)*H) * scale
# logistic fit: hit ~ log(size) + cell dummies (pass-1 data)
cells = sorted({(r['platform'], r['type']) for r in R})
def feats(r, size):
    return [1.0, math.log(max(size,1))] + [1.0 if (r['platform'],r['type'])==c else 0.0 for c in cells[1:]]
X = np.array([feats(r, tsize(r, r['scale'])) for r in R]); y = np.array([1.0 if r['hit'] else 0.0 for r in R])
w = np.zeros(X.shape[1])
for _ in range(50):  # Newton
    p = 1/(1+np.exp(-X@w)); g = X.T@(y-p); Hm = (X*(p*(1-p))[:,None]).T@X + 1e-6*np.eye(len(w)); w += np.linalg.solve(Hm, g)
pred = lambda r, size: 1/(1+math.exp(-np.dot(w, feats(r, size))))
print('log-size coef %.2f  (per doubling of target size, odds x%.2f)' % (w[1], 2**w[1]))
print('pass1 actual %.1f, model fit %.1f' % (100*y.mean(), 100*np.mean([pred(r, tsize(r, r['scale'])) for r in R])))

def window(r, f):  # crop f * image dims around A's point, clamped
    W,H = r['orig_size']; cw, ch = f*W, f*H
    px, py = r['point'][0]*W, r['point'][1]*H
    x0 = min(max(px-cw/2, 0), W-cw); y0 = min(max(py-ch/2, 0), H-ch)
    return x0, y0, cw, ch
def sim(f, gate=None, maxup=None):
    tot = cov = fixed = broke = 0; extra = 0; ups=[]
    for r in R:
        W,H = r['orig_size']; x1,y1,x2,y2 = r['gt']; gx, gy = (x1+x2)/2*W, (y1+y2)/2*H
        if gate is not None and (r['confidence'] or 0) >= gate:
            tot += r['hit']; continue
        extra += 1
        x0,y0,cw,ch = window(r, f)
        s = min(1568/max(cw,ch), 1e9)
        s = max(s, 280/min(cw,ch))
        if maxup: s = min(s, maxup)
        ups.append(s / r['scale'])
        c = x0 <= gx <= x0+cw and y0 <= gy <= y0+ch
        cov += c
        p = pred(r, tsize(r, s)) if c else 0.0
        tot += p
        if r['hit']: broke += 1-p
        else: fixed += p
    return 100*tot/1272, 100*cov/max(extra,1), fixed, broke, extra, np.median(ups)
print('\n f    est%   centre-covered%  fixed  broken  B-calls  median zoom vs A')
for f in (1.0, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15):
    e = sim(f); print(' %.2f  %5.1f   %5.1f           %5.1f  %5.1f   %4d     %.2fx' % (f, *e))
print('\nmisses only: how far A point was from target, as fraction of image side')
d = []
for r in R:
    if r['hit']: continue
    x1,y1,x2,y2 = r['gt']; px,py = r['point']
    dx = max(x1-px, 0, px-x2); dy = max(y1-py, 0, py-y2); d.append(max(dx,dy))
d = np.array(d)
for t in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3): print('  target edge within %.2f of A point: %d of %d misses' % (t, (d<=t).sum(), len(d)))
print('\nconfidence gate (B only when A conf < g), f=0.4:')
for g in (0.7, 0.8, 0.9, None):
    e = sim(0.4, gate=g); print('  gate %s: est %.1f, B calls %d' % (g, e[0], e[4]))
print('\nupscale cap (B never > native resolution), f sweep:')
for f in (0.6, 0.5, 0.4, 0.3):
    e = sim(f, maxup=1.0); print('  f %.2f: est %.1f covered %.1f median zoom %.2fx' % (f, e[0], e[1], e[5]))
