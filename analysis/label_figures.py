"""Label-audit figures from the run records. Offline, no API.
  python3 analysis/label_figures.py sheets          # audit sheets -> analysis/label-audit/sheets/*.jpg
  python3 analysis/label_figures.py full CASE ...   # whole screenshot per case -> analysis/figures/labels/case_NNNN.png
Colours: green = answer key, red = pass 1 (A1), purple = pass 2 (A2), orange = zoom answer (B), grey = zoom window.
Dot = the click (box centre)."""
import json, pathlib, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import screenspot as ss

LA = ROOT / "analysis" / "label-audit"
RUNS = {k: ss.latest(ss.read(ss.OUT / f)) for k, f in (("A1", "pass1.jsonl"), ("A2", "pass2.jsonl"), ("B", "zoom2.jsonl"))}
COL = {"A1": (230, 0, 0), "A2": (150, 0, 200), "B": (255, 140, 0)}
GREEN, GREY = (0, 190, 0), (120, 120, 120)
F = lambda s, b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)


def sides(b):
    l, r = sorted((b["left"], b["right"])); t, bo = sorted((b["top"], b["bottom"]))
    return l, t, r, bo


def tile(i, TW, TH, window=False, fs=20):
    """Region around the key and every answer, padded, at the tile's aspect; instruction + results on top."""
    a = RUNS["A2"][i]; W, H = a["orig_size"]; x, y, w, h = a["gt_px"]
    orig = Image.open(ss.DATA / "screenspotv2_image" / a["file"]).convert("RGB")
    boxes = [(x, y, x + w, y + h)] + [(l * W, t * H, r * W, b * H) for l, t, r, b in (sides(R[i]["box"]) for R in RUNS.values())]
    X0, Y0 = min(b[0] for b in boxes), min(b[1] for b in boxes); X1, Y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    pw, ph = (X1 - X0) * 0.25 + 80, (Y1 - Y0) * 0.25 + 80
    X0, Y0, X1, Y1 = max(0, X0 - pw), max(0, Y0 - ph), min(W, X1 + pw), min(H, Y1 + ph)
    cw, ch = X1 - X0, Y1 - Y0
    if cw / ch < TW / TH:
        need = ch * TW / TH - cw; X0, X1 = max(0, X0 - need / 2), min(W, X1 + need / 2)
    else:
        need = cw * TH / TW - ch; Y0, Y1 = max(0, Y0 - need / 2), min(H, Y1 + need / 2)
    crop = orig.crop((int(X0), int(Y0), int(X1), int(Y1)))
    s = min(TW / crop.width, TH / crop.height); crop = crop.resize((max(1, round(crop.width * s)), max(1, round(crop.height * s))))
    d = ImageDraw.Draw(crop)
    tr = lambda px, py: ((px - int(X0)) * s, (py - int(Y0)) * s)
    if window:
        x0, y0, ww, wh = RUNS["B"][i]["window"]; d.rectangle([*tr(x0, y0), *tr(x0 + ww, y0 + wh)], outline=GREY, width=3)
    d.rectangle([*tr(x, y), *tr(x + w, y + h)], outline=GREEN, width=4)
    for k, R in RUNS.items():
        l, t, r, b = sides(R[i]["box"]); d.rectangle([*tr(l * W, t * H), *tr(r * W, b * H)], outline=COL[k], width=2)
        px, py = tr(R[i]["point"][0] * W, R[i]["point"][1] * H); d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=COL[k], outline="white")
    out = Image.new("RGB", (TW, TH + 70), "white"); out.paste(crop, (0, 70)); t = ImageDraw.Draw(out)
    res = " ".join(f"{k}:{'T' if R[i]['hit'] else 'F'}" for k, R in RUNS.items())
    t.text((6, 2), f"#{i} {a['platform']} {a['type']}  {res}", fill="black", font=F(fs, True))
    t.text((6, 30), textwrap.shorten(a["instruction"], int(1600 / fs * TW / 940)), fill=(0, 0, 160), font=F(fs, True))
    return out


def sheets(name, ids, TW, TH, cols, rows, window=False, fs=20):
    per = cols * rows
    for k in range(0, len(ids), per):
        sheet = Image.new("RGB", (cols * TW + 20 * (cols - 1), rows * (TH + 70) + 20 * (rows - 1)), (200, 200, 200))
        for j, i in enumerate(ids[k:k + per]):
            sheet.paste(tile(i, TW, TH, window, fs), ((j % cols) * (TW + 20), (j // cols) * (TH + 70 + 20)))
        (LA / "sheets").mkdir(exist_ok=True)
        sheet.save(LA / "sheets" / f"{name}_{k // per:02d}.jpg", quality=82, optimize=True)
    print(name, len(ids), "cases,", -(-len(ids) // per), "sheets")


def full(i, max_side=1600):
    a = RUNS["A2"][i]; W, H = a["orig_size"]; x, y, w, h = a["gt_px"]
    im = Image.open(ss.DATA / "screenspotv2_image" / a["file"]).convert("RGB")
    s = min(max_side / W, max_side / H, 1.0); im = im.resize((round(W * s), round(H * s))); d = ImageDraw.Draw(im)
    x0, y0, cw, ch = RUNS["B"][i]["window"]; d.rectangle([x0 * s, y0 * s, (x0 + cw) * s, (y0 + ch) * s], outline=GREY, width=2)
    d.rectangle([x * s, y * s, (x + w) * s, (y + h) * s], outline=GREEN, width=4)
    for k, R in RUNS.items():
        l, t, r, b = sides(R[i]["box"]); d.rectangle([l * W * s, t * H * s, r * W * s, b * H * s], outline=COL[k], width=3)
        px, py = R[i]["point"][0] * W * s, R[i]["point"][1] * H * s; d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=COL[k], outline="white")
    head = 92; out = Image.new("RGB", (max(im.width, 1100), im.height + head), "white"); out.paste(im, (0, head)); t = ImageDraw.Draw(out)
    res = "   ".join(f"{k} {'TRUE' if R[i]['hit'] else 'FALSE'} ({R[i]['confidence']:.2f})" for k, R in RUNS.items())
    t.text((8, 6), textwrap.shorten(f'#{i} {a["platform"]} {a["type"]}: "{a["instruction"]}"', 95), fill="black", font=F(22, True))
    t.text((8, 36), res, fill="black", font=F(19))
    t.text((8, 64), "green = answer key   red = pass 1   purple = pass 2   orange = zoom   grey = zoom window", fill=(80, 80, 80), font=F(17))
    p = ROOT / "analysis" / "figures" / "labels" / f"case_{i:04d}.png"; p.parent.mkdir(parents=True, exist_ok=True)
    out.save(p, optimize=True); print(p.relative_to(ROOT), out.size)


if __name__ == "__main__":
    if sys.argv[1] == "sheets":
        sheets("wrong_element", json.load(open(LA / "cand_wrong_element.json")), 940, 640, 2, 3)
        sheets("near", json.load(open(LA / "cand_near.json")), 620, 430, 3, 3, fs=17)
        brk = [i for i in range(1272) if RUNS["A2"][i]["hit"] and not RUNS["B"][i]["hit"]]
        sheets("zoom_breaks", brk, 940, 640, 2, 3, window=True)
    elif sys.argv[1] == "full":
        for i in map(int, sys.argv[2:]):
            full(i)
