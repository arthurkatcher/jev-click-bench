import json, sys
from PIL import Image, ImageDraw, ImageFont
D='/home/bionics/jev-screenspot/data/screenspot-v2/screenspotv2_image/'
R={}
for l in open('/home/bionics/jev-screenspot/results/pass1.jsonl'):
    try: r=json.loads(l); R[r['i']]=r
    except: pass
F=0.5
MODE=sys.argv[1]
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
except: font=ImageFont.load_default()
def make(i):
    r=R[i]; im=Image.open(D+r['file']).convert('RGB'); W,H=im.size
    cw,ch=F*W,F*H; px,py=r['point'][0]*W,r['point'][1]*H
    if MODE=='box':
        bl,br=sorted((r['box']['left'],r['box']['right'])); bt,bb=sorted((r['box']['top'],r['box']['bottom']))
        k=max(F,min(1.0,max((br-bl)*1.2,(bb-bt)*1.2))); cw,ch=k*W,k*H; cx,cy=(bl+br)/2*W,(bt+bb)/2*H
    else: cx,cy=px,py
    x0=min(max(cx-cw/2,0),W-cw); y0=min(max(cy-ch/2,0),H-ch)
    g=[v*d for v,d in zip(r['gt'],(W,H,W,H))]; b=r['box']; a=[b['left']*W,b['top']*H,b['right']*W,b['bottom']*H]
    full=im.copy(); d=ImageDraw.Draw(full); lw=max(3,W//400)
    d.rectangle([x0,y0,x0+cw,y0+ch],outline=(0,120,255),width=lw*2)
    d.rectangle(g,outline=(0,200,0),width=lw); d.rectangle(a,outline=(255,0,0),width=lw)
    d.ellipse([px-lw*3,py-lw*3,px+lw*3,py+lw*3],fill=(255,0,0))
    crop=im.crop((round(x0),round(y0),round(x0+cw),round(y0+ch)))
    s=1568/max(crop.size); crop=crop.resize((round(crop.width*s),round(crop.height*s)),3)
    dc=ImageDraw.Draw(crop); gc=[(g[0]-x0)*s,(g[1]-y0)*s,(g[2]-x0)*s,(g[3]-y0)*s]
    dc.rectangle(gc,outline=(0,200,0),width=4)
    # side by side, both scaled to same height
    h=900; fa=full.resize((round(full.width*h/full.height),h)); ca=crop.resize((round(crop.width*h/crop.height),h))
    out=Image.new('RGB',(fa.width+ca.width+30,h+110),'white'); out.paste(fa,(0,110)); out.paste(ca,(fa.width+30,110))
    t=ImageDraw.Draw(out)
    t.text((10,8),f"#{i} {r['platform']} {r['type']}: \"{r['instruction']}\"   conf {r['confidence']}",fill='black',font=font)
    t.text((10,50),f"LEFT: what A saw. green = target, red = A's box + click, blue = zoom window ({'centred on click' if MODE=='click' else 'contains A box'})    RIGHT: what B would see",fill=(60,60,60),font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20) if hasattr(font,'path') else font)
    p=f'zoomviz/miss_{i:04d}_{MODE}.png'; out.save(p); print(p, out.size)
for i in map(int,sys.argv[2:]): make(i)
