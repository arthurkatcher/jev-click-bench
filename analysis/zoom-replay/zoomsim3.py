exec(open('zoomsim2.py').read().split("print(' f     est%")[0])
# coverage = the visible part of the target in the crop is at least 8x8 px of the image Jev sees
def sim3(f, maxup=None, minvis=8):
    tot=fixed=broke=0; per={}; cut=0
    for r in R:
        W,H = r['orig_size']; x1,y1,x2,y2 = [v*d for v,d in zip(r['gt'],(W,H,W,H))]
        q = 0.97 if r['hit'] else 0.15
        x0,y0,cw,ch = window(r,f); s = max(1568/max(cw,ch), 280/min(cw,ch))
        if maxup: s = min(s, maxup)
        vx = min(x2,x0+cw)-max(x1,x0); vy = min(y2,y0+ch)-max(y1,y0)
        if vx*s >= minvis and vy*s >= minvis:
            size = math.sqrt(vx*vy)*s; size0 = tsize(r, r['scale'])
            p = sg(lg(q) + w[1]*math.log(max(size,1)/max(size0,1)))
        else:
            p = 0.0; cut += r['hit']
        tot+=p; fixed+=(not r['hit'])*p; broke+=r['hit']*(1-p)
        k=(r['platform'],r['type']); per.setdefault(k,[0,0]); per[k][0]+=p; per[k][1]+=1
    return 100*tot/1272, fixed, broke, cut, per

print(' f     est%  fixed  broken  A-hits cut out')
for f in (1.0,0.8,0.7,0.6,0.5,0.45,0.4,0.35,0.3,0.25,0.2,0.15):
    e=sim3(f); print(' %.2f  %5.1f  %5.1f  %5.1f   %d' % (f,*e[:4]))
for f in (0.6,0.4,0.3):
  e=sim3(f); print('per cell f=%.2f:' % f, {f'{k[0]} {k[1]}': round(100*v[0]/v[1],1) for k,v in sorted(e[4].items())})
