exec(open('zoomsim.py').read().split("print('\\n f")[0])
# anchored: each case keeps its own difficulty. A-hit cases q=0.97, A-miss q=0.15
# (gives ~5% flips on a plain rerun, the repeat rate others measured); zoom shifts the logit by w1*ln(zoom)
lg = lambda p: math.log(p/(1-p)); sg = lambda z: 1/(1+math.exp(-z))
def sim2(f, maxup=None, gate=None, cells_out=False):
    tot=fixed=broke=lost=0; per={}
    for r in R:
        W,H = r['orig_size']; x1,y1,x2,y2 = r['gt']; gx,gy=(x1+x2)/2*W,(y1+y2)/2*H
        q = 0.97 if r['hit'] else 0.15
        if gate is not None and (r['confidence'] or 0) >= gate: p = q
        else:
            x0,y0,cw,ch = window(r,f); s = max(min(1568/max(cw,ch), 1e9), 280/min(cw,ch))
            if maxup: s = min(s, maxup)
            z = s/r['scale']
            c = x0<=gx<=x0+cw and y0<=gy<=y0+ch
            p = sg(lg(q) + w[1]*math.log(z)) if c else 0.0
            if not c and r['hit']: lost += 1
        tot += p; fixed += (not r['hit'])*p; broke += r['hit']*(1-p)
        k=(r['platform'],r['type']); per.setdefault(k,[0,0]); per[k][0]+=p; per[k][1]+=1
    return 100*tot/1272, fixed, broke, lost, per
print(' f     est%  fixed  broken  (A-hits cut out of crop)')
for f in (1.0,0.8,0.7,0.6,0.5,0.45,0.4,0.35,0.3,0.25,0.2):
    e=sim2(f); print(' %.2f  %5.1f  %5.1f  %5.1f   %d' % (f,*e[:4]))
print('\nno upscaling past native:')
for f in (1.0,0.8,0.7,0.6,0.5,0.4):
    e=sim2(f,maxup=1.0); print(' %.2f  %5.1f  %5.1f  %5.1f   %d' % (f,*e[:4]))
for f in (0.6,0.5,0.4):
  e=sim2(f); print('\nper cell f=%.2f:' % f, {f'{k[0]} {k[1]}': round(100*v[0]/v[1],1) for k,v in sorted(e[4].items())})
a={}
for r in R:
    k=(r['platform'],r['type']); a.setdefault(k,[0,0]); a[k][0]+=r['hit']; a[k][1]+=1
print('pass1 per cell:', {f'{k[0]} {k[1]}': round(100*v[0]/v[1],1) for k,v in sorted(a.items())})
print('\nscale==1 (not downscaled) cases in pass 1:', sum(1 for r in R if r['scale']>=0.999), 'acc', round(100*np.mean([r['hit'] for r in R if r['scale']>=0.999]),1))
print('orig sizes:'); import collections; print(collections.Counter(tuple(r['orig_size']) for r in R).most_common(8))
