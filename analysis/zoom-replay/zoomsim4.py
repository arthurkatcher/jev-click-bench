exec(open("zoomsim3.py").read().split("SPLITHERE")[0])
# pass-1 accuracy by size, finer bins, to see where it saturates
S = np.array([tsize(r, r['scale']) for r in R]); Y = np.array([r['hit'] for r in R])
for lo,hi in [(0,20),(20,30),(30,45),(45,60),(60,80),(80,120),(120,1e9)]:
    m=(S>=lo)&(S<hi); print('size %3d-%-4s n=%4d acc %.1f' % (lo, hi if hi<1e9 else 'inf', m.sum(), 100*Y[m].mean()))
print('\nmisses: target visible in crop, and target size after zoom (median), by f')
M=[r for r in R if not r['hit']]
for f in (0.6,0.5,0.4,0.35,0.3,0.25,0.2):
    vis=0; sz=[]; up=[]
    for r in M:
        W,H=r['orig_size']; x1,y1,x2,y2=[v*d for v,d in zip(r['gt'],(W,H,W,H))]
        x0,y0,cw,ch=window(r,f); s=max(1568/max(cw,ch),280/min(cw,ch))
        vx=min(x2,x0+cw)-max(x1,x0); vy=min(y2,y0+ch)-max(y1,y0)
        if vx>0 and vy>0: vis+=1; sz.append(math.sqrt(vx*vy)*s)
        up.append(s)
    sz=np.array(sz)
    print(' f %.2f: target in crop %d/212, median size %.0f px, >=45px %d, upscale vs native median %.2fx' % (f,vis,np.median(sz),(sz>=45).sum(),np.median(up)))
print('\nmiss sizes now (sent px): median %.0f' % np.median([tsize(r,r['scale']) for r in M]))
# per platform: crop size in original px at f=0.4 / native ratio
for p in ('mobile','desktop','web'):
    rs=[r for r in R if r['platform']==p]
    print(p, 'median scale A %.2f' % np.median([r['scale'] for r in rs]), 'upscale at f=0.4 %.2fx' % np.median([1568/(0.4*max(r['orig_size'])) for r in rs]))
