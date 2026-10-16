"""Article figures from real run records. Offline, no API.

  python3 analysis/figures.py RESULTS_A.jsonl [RESULTS_B.jsonl] CASE [CASE ...] [--tag NAME]

Left: the full screenshot (green = true target, red = stage A box + click, blue = zoom window,
orange = stage B box mapped back). Right (when a B record exists): the crop exactly as stage B saw it,
with B's box in crop coordinates. Saved to analysis/figures/<tag>_case_<i>.png.
"""
import json, pathlib, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import screenspot as ss

OUT = ROOT / "analysis" / "figures"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GREEN, RED, BLUE, ORANGE = (0, 190, 0), (230, 0, 0), (0, 110, 255), (255, 140, 0)


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT.replace("Sans.ttf", "Sans-Bold.ttf") if bold else FONT, size)
    except OSError:
        return ImageFont.load_default()


def rect(d, box, W, H, color, lw, ox=0, oy=0, s=1.0):
    l, r = sorted((box["left"], box["right"]))
    t, b = sorted((box["top"], box["bottom"]))
    d.rectangle([ox + l * W * s, oy + t * H * s, ox + r * W * s, oy + b * H * s], outline=color, width=lw)


def draw(a, b, tag, h=900):
    orig = Image.open(ss.DATA / "screenspotv2_image" / a["file"]).convert("RGB")
    W, H = orig.size
    full = orig.copy()
    d = ImageDraw.Draw(full)
    lw = max(3, W // 400)
    g = a["gt"]
    d.rectangle([g[0] * W, g[1] * H, g[2] * W, g[3] * H], outline=GREEN, width=lw)
    if a.get("box"):
        rect(d, a["box"], W, H, RED, lw)
        px, py = a["point"][0] * W, a["point"][1] * H
        d.ellipse([px - 3 * lw, py - 3 * lw, px + 3 * lw, py + 3 * lw], fill=RED)
    panels = [full]
    if b and b.get("window"):
        x0, y0, cw, ch = b["window"]
        d.rectangle([x0, y0, x0 + cw, y0 + ch], outline=BLUE, width=2 * lw)
        if b.get("box"):
            rect(d, b["box"], W, H, ORANGE, lw)
            px, py = b["point"][0] * W, b["point"][1] * H
            d.ellipse([px - 3 * lw, py - 3 * lw, px + 3 * lw, py + 3 * lw], fill=ORANGE)
        crop = orig.crop((x0, y0, x0 + cw, y0 + ch)).resize(tuple(b["sent_size"]), resample=3)
        dc = ImageDraw.Draw(crop)
        sx, sy = crop.width / cw, crop.height / ch
        dc.rectangle([(g[0] * W - x0) * sx, (g[1] * H - y0) * sy, (g[2] * W - x0) * sx, (g[3] * H - y0) * sy],
                     outline=GREEN, width=4)
        if b.get("box_crop"):
            rect(dc, b["box_crop"], crop.width, crop.height, ORANGE, 4)
        panels.append(crop)
    scaled = [p.resize((round(p.width * h / p.height), h)) for p in panels]
    head = 120
    out = Image.new("RGB", (sum(p.width for p in scaled) + 30 * (len(scaled) - 1), h + head), "white")
    x = 0
    for p in scaled:
        out.paste(p, (x, head))
        x += p.width + 30
    t = ImageDraw.Draw(out)
    res = lambda r: "no answer" if not r or r.get("hit") is None else ("TRUE" if r["hit"] else "FALSE")
    line = f'#{a["i"]} {a["platform"]} {a["type"]}: "{a["instruction"]}"   A {res(a)} (conf {a.get("confidence")})'
    if b:
        line += f'   zoom {res(b)} (conf {b.get("confidence")}, window {b.get("window_frac")})'
    t.text((10, 10), line, fill="black", font=font(26, True))
    t.text((10, 56), "green = true target   red = first answer (A)   blue = zoom window   orange = zoomed answer (B)",
           fill=(70, 70, 70), font=font(20))
    t.text((10, 86), "left: full screenshot" + ("   right: the crop exactly as the zoom call saw it" if b else ""),
           fill=(70, 70, 70), font=font(20))
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{tag}_case_{a['i']:04d}.png"
    out.save(p)
    return p


if __name__ == "__main__":
    args = sys.argv[1:]
    tag = "fig"
    if "--tag" in args:
        k = args.index("--tag")
        tag = args[k + 1]
        del args[k:k + 2]
    files = [x for x in args if x.endswith(".jsonl")]
    idx = [int(x) for x in args if x.isdigit()]
    A = {r["i"]: r for r in ss.read(files[0]) if r.get("status") in ("ok", "wrong_format")}
    B = {r["i"]: r for r in ss.read(files[1]) if r.get("stage") == "B"} if len(files) > 1 else {}
    for i in idx:
        print(draw(A[i], B.get(i), tag))
