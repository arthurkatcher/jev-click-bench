exec(open("zoomsim3.py").read().split("print(' f     est%  fixed")[0])
# variant B: window must contain A's whole box (+margin m on each side), at least f of the image
def window_box(r, f, m=0.1):
    W,H=r['orig_size']; b=r['box']
    bl,br=sorted((b['left'],b['right'])); bt,bb=sorted((b['top'],b['bottom']))
    bw,bh=(br-bl)*W,(bb-bt)*H
    k=max(f, min(1.0, max(bw*(1+2*m)/W, bh*(1+2*m)/H)))  # keep image aspect, so tokens match A
    cw,ch=k*W,k*H; cx,cy=(bl+br)/2*W,(bt+bb)/2*H
    return min(max(cx-cw/2,0),W-cw), min(max(cy-ch/2,0),H-ch), cw, ch
def run(winf, f):
    tot=fixed=broke=0; vis=0; ks=[]
    for r in R:
        W,H=r['orig_size']; x1,y1,x2,y2=[v*d for v,d in zip(r['gt'],(W,H,W,H))]
        q=0.97 if r['hit'] else 0.15
        x0,y0,cw,ch=winf(r,f); s=r['sent_size'][0]/cw; ks.append(cw/W)  # runner rule: crop resized to A's sent size
        vx=min(x2,x0+cw)-max(x1,x0); vy=min(y2,y0+ch)-max(y1,y0)
        if vx*s>=8 and vy*s>=8:
            p=sg(lg(q)+w[1]*math.log(max(math.sqrt(vx*vy)*s,1)/max(tsize(r,r['scale']),1)))
            vis+= not r['hit']
        else: p=0.0
        tot+=p; fixed+=(not r['hit'])*p; broke+=r['hit']*(1-p)
    return 100*tot/1272, fixed, broke, vis, np.median(ks), np.mean(np.array(ks)>f+1e-9)
print('            est%  fixed broken  miss-targets-in-crop  median window  share widened')
for f in (0.6,0.5,0.4):
    print('click f=%.1f  %5.1f  %5.1f  %5.1f   %d/212  %.2f  %.0f%%' % (f, *run(lambda r,f: window(r,f), f)[:4], f, 0))
    e=run(window_box,f); print('box   f=%.1f  %5.1f  %5.1f  %5.1f   %d/212  %.2f  %.0f%%' % (f,*e[:4],e[4],100*e[5]))
