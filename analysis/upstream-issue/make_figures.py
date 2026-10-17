"""Figures for the upstream ScreenSpot-v2 label issue. Offline, reads only data/screenspot-v2.
  python3 analysis/upstream-issue/make_figures.py
Green = the stored answer key. Blue dashed = suggested correction. No model answers are drawn."""
import json, pathlib, textwrap
from PIL import Image, ImageDraw, ImageFont
ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "screenspot-v2"
OUT = pathlib.Path(__file__).resolve().parent
GREEN, BLUE = (0, 190, 0), (0, 90, 255)
F = lambda s, b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)

FILES = {p: json.loads((DATA / f"screenspot_{p}_v2.json").read_text()) for p in ("mobile", "desktop", "web")}


def rec(platform, k):
    return FILES[platform][k]


def dashed(d, box, color, width=4, dash=14):
    x0, y0, x1, y1 = box
    for a, b, horiz in ((x0, x1, True), (y0, y1, False)):
        for s in range(int(a), int(b), dash * 2):
            e = min(s + dash, b)
            if horiz:
                d.line([s, y0, e, y0], fill=color, width=width); d.line([s, y1, e, y1], fill=color, width=width)
            else:
                d.line([x0, s, x0, e], fill=color, width=width); d.line([x1, s, x1, e], fill=color, width=width)


def panel(platform, k, region=None, fix=None, max_w=1100, max_h=800, note=""):
    """Crop `region` (x0, y0, x1, y1 in original px, default whole image), draw the key and an optional fix."""
    c = rec(platform, k)
    im = Image.open(DATA / "screenspotv2_image" / c["img_filename"]).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = region or (0, 0, W, H)
    im = im.crop((x0, y0, x1, y1))
    s = min(max_w / im.width, max_h / im.height, 2.5)
    im = im.resize((round(im.width * s), round(im.height * s)))
    d = ImageDraw.Draw(im)
    tr = lambda bx, by, bw, bh: ((bx - x0) * s, (by - y0) * s, (bx + bw - x0) * s, (by + bh - y0) * s)
    d.rectangle(tr(*c["bbox"]), outline=GREEN, width=5)
    if fix:
        dashed(d, tr(*fix), BLUE)
    head = 112
    out = Image.new("RGB", (max(im.width, 760), im.height + head), "white")
    out.paste(im, (0, head)); t = ImageDraw.Draw(out)
    t.text((8, 6), f"screenspot_{platform}_v2.json [{k}]   {c['img_filename']} ({W}x{H})", fill="black", font=F(17, True))
    t.text((8, 32), textwrap.shorten(f'instruction: "{c["instruction"]}"', 95), fill=(0, 0, 150), font=F(17, True))
    t.text((8, 58), f"stored bbox [x, y, w, h] = {c['bbox']}" + (f"   suggested = {fix}" if fix else ""), fill="black", font=F(16))
    t.text((8, 84), note or ("green = stored key   blue dashed = suggested fix" if fix else "green = stored key"), fill=(90, 90, 90), font=F(15))
    return out


def side(a, b, gap=24):
    out = Image.new("RGB", (a.width + b.width + gap, max(a.height, b.height)), (200, 200, 200))
    out.paste(a, (0, 0)); out.paste(b, (a.width + gap, 0))
    return out


def save(im, name):
    p = OUT / name; im.save(p, optimize=True); print(p.relative_to(ROOT), im.size)


if __name__ == "__main__":
    # 1. Key errors
    save(side(panel("mobile", 455, max_w=760, max_h=560, note="for comparison: the same bbox, on its own screenshot"),
              panel("mobile", 458, max_w=420, max_h=900, fix=[1010, 2458, 150, 93])), "fig_mobile_455_458_copied_bbox.png")
    save(panel("mobile", 458, region=(0, 1150, 1280, 2700), max_w=900, max_h=1000, fix=[1010, 2458, 150, 93]), "fig_mobile_458_closeup.png")
    save(panel("mobile", 487, region=(380, 120, 1180, 760), fix=[509, 425, 490, 80]), "fig_mobile_487_fahrenheit.png")
    save(panel("web", 200, region=(1700, 380, 2560, 640), fix=[1979, 475, 71, 62],
               note="green = stored key   blue dashed = ScreenSpot v1 bbox for the same case"), "fig_web_200_x_account.png")
    save(panel("web", 202, region=(0, 170, 1500, 560), fix=[257, 306, 170, 109],
               note="green = stored key   blue dashed = ScreenSpot v1 bbox for the same case"), "fig_web_202_weather.png")
    # 2. Duplicate, 3. key past the edge
    save(panel("web", 182, region=(0, 0, 700, 260), note="web [182] and web [186] are identical: same image, instruction and bbox"),
         "fig_web_182_186_duplicate.png")
    save(panel("mobile", 449, note="bbox right edge = 645 + 1716 = 2361, image width = 2360"), "fig_mobile_449_edge.png")
    # 4. Judgment calls
    a = panel("mobile", 89, max_w=520, max_h=900, note="key: the ... button at the top")
    b = panel("mobile", 91, max_w=520, max_h=900, note="key: the MORE link")
    save(side(a, b), "fig_mobile_89_91_more_information.png")
    save(panel("web", 196, note='the sidebar link reads "Create new page"; the key is the "Create this page" button'),
         "fig_web_196_create_page.png")
    save(panel("web", 401, region=(1000, 470, 1420, 720), note="the key covers the radio dot only, not its label"),
         "fig_web_401_radio_label.png")
