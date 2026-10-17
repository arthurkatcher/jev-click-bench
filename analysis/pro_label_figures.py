"""Label-audit figures for ScreenSpot-Pro, from the run records. Offline, no API.
  python3 analysis/pro_label_figures.py cases [CASE ...]          # one review image per case (default: every case B missed)
                                                                  #   -> analysis/label-audit-pro/cases/case_NNNN.jpg
  python3 analysis/pro_label_figures.py zoom CASE CX CY SIDE OUT  # closer look: SIDE x SIDE original px around (CX, CY)
  python3 analysis/pro_label_figures.py lang                      # UI-language contact sheets, all 1,581 cases, 16 per sheet
                                                                  #   -> analysis/label-audit-pro/lang_sheets/lang_NN.jpg
Layout: header (case, results, instruction); left = whole screenshot with every mark, the two zoom panels outlined
and distance hints; middle = around the answer key; right = around the farthest missing answer that is not in the
middle panel (B first, then A2, then A1), or a close-up of the key when every answer is near it.
Colours: green = answer key (drawn 3 px outside it), red = pass 1 (A1), purple = pass 2 (A2), orange = zoom answer (B),
grey = B's zoom window. Dot = the click (box centre). Distances are px in the image Jev saw for the full screenshot."""
import math, pathlib, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import screenspot as ss

ss.use("pro")
RUNS = {k: ss.latest(ss.read(ss.OUT / f)) for k, f in (("A1", "pass1.jsonl"), ("A2", "pass2.jsonl"), ("B", "zoom2.jsonl"))}
COL = {"A1": (230, 0, 0), "A2": (150, 0, 200), "B": (255, 140, 0)}
GREEN, GREY = (0, 190, 0), (110, 110, 110)
F = lambda s, b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)
P, HEAD = 520, 100  # panel side, header height
OUTDIR = ROOT / "analysis" / "label-audit-pro" / "cases"


def sides(b):
    l, r = sorted((b["left"], b["right"])); t, bo = sorted((b["top"], b["bottom"]))
    return l, t, r, bo


def off(i, k):  # click to the nearest edge of the key box, px in A's sent image
    r = RUNS[k][i]; W, H = r["orig_size"]; x, y, w, h = r["gt_px"]; px, py = r["point"][0] * W, r["point"][1] * H
    return math.hypot(max(x - px, 0, px - x - w), max(y - py, 0, py - y - h)) * RUNS["A2"][i]["scale"]


def wide(i, k):  # the box holds the key centre (on a miss: the box is too wide, its centre lands beside the target)
    r = RUNS[k][i]; W, H = r["orig_size"]; x, y, w, h = r["gt_px"]; l, t, rr, bo = sides(r["box"])
    return l <= (x + w / 2) / W <= rr and t <= (y + h / 2) / H <= bo


def region(cx, cy, side, W, H):  # square, slid to stay inside the screenshot, original px
    side = min(side, W, H)
    return min(max(cx - side / 2, 0), W - side), min(max(cy - side / 2, 0), H - side), side


def inside(px, py, reg):
    x0, y0, s = reg
    return x0 <= px <= x0 + s and y0 <= py <= y0 + s


def marks(d, i, tr, lw=2, dot=6):
    a = RUNS["A2"][i]; W, H = a["orig_size"]; x, y, w, h = a["gt_px"]
    x0, y0, cw, ch = RUNS["B"][i]["window"]
    d.rectangle([*tr(x0, y0), *tr(x0 + cw, y0 + ch)], outline=GREY, width=lw + 1)
    (gx0, gy0), (gx1, gy1) = tr(x, y), tr(x + w, y + h)
    d.rectangle([gx0 - 3, gy0 - 3, gx1 + 3, gy1 + 3], outline=GREEN, width=lw + 1)
    for k, R in RUNS.items():
        l, t, r, b = sides(R[i]["box"]); d.rectangle([*tr(l * W, t * H), *tr(r * W, b * H)], outline=COL[k], width=lw)
    for k, R in RUNS.items():
        px, py = tr(R[i]["point"][0] * W, R[i]["point"][1] * H)
        d.ellipse([px - dot, py - dot, px + dot, py + dot], fill=COL[k], outline="white")


def panel(orig, i, reg, title, tcol):
    x0, y0, s = reg
    box = (int(x0), int(y0), int(round(x0 + s)), int(round(y0 + s)))
    crop = orig.crop(box).resize((P, P), resample=Image.LANCZOS)
    sx, sy = P / (box[2] - box[0]), P / (box[3] - box[1])
    d = ImageDraw.Draw(crop)
    marks(d, i, lambda px, py: ((px - box[0]) * sx, (py - box[1]) * sy))
    lab = f"{title}  ({sx:.2f}x of the original)"
    d.rectangle([0, 0, 10 + d.textlength(lab, font=F(15, True)), 22], fill="white")
    d.text((5, 2), lab, fill=tcol, font=F(15, True))
    return crop


def case_image(i):
    a, b = RUNS["A2"][i], RUNS["B"][i]; W, H = a["orig_size"]; x, y, w, h = a["gt_px"]
    orig = Image.open(ss.DATA / ss.IMAGES / a["file"]).convert("RGB")
    kx, ky = x + w / 2, y + h / 2
    kreg = region(kx, ky, max(6 * max(w, h), 360), W, H)
    right = None
    for k in ("B", "A2", "A1"):
        r = RUNS[k][i]; px, py = r["point"][0] * W, r["point"][1] * H
        if not r["hit"] and not inside(px, py, kreg):
            l, t, rr, bo = sides(r["box"])
            side = max(360, 1.3 * max((rr - l) * W, (bo - t) * H))
            right = (region(px, py, side, W, H), f"around {k}'s answer", COL[k]); break
    if right is None:
        right = (region(kx, ky, max(3 * max(w, h), 100), W, H), "close-up of the key", GREEN)
    out = Image.new("RGB", (3 * P + 20, HEAD + P), "white")
    # left column: whole screenshot, both panel regions outlined, hints under it
    ow = P; oh = round(P * H / W); s = ow / W
    ov = orig.resize((ow, oh), resample=Image.LANCZOS); d = ImageDraw.Draw(ov)
    tr = lambda px, py: (px * s, py * s)
    for (rx, ry, rs), col in ((kreg, GREEN), (right[0], right[2])):
        d.rectangle([*tr(rx, ry), *tr(rx + rs, ry + rs)], outline=col, width=1)
    marks(d, i, tr, lw=1, dot=4)
    d.ellipse([kx * s - 11, ky * s - 11, kx * s + 11, ky * s + 11], outline=GREEN, width=2)
    out.paste(ov, (0, HEAD))
    out.paste(panel(orig, i, kreg, "around the answer key (green)", (0, 120, 0)), (P + 10, HEAD))
    out.paste(panel(orig, i, right[0], right[1], right[2]), (2 * P + 20, HEAD))
    t = ImageDraw.Draw(out)
    res = "   ".join(f"{k} {'HIT' if R[i]['hit'] else 'miss'} ({R[i]['confidence']:.2f})" for k, R in RUNS.items())
    t.text((8, 4), f"#{i}  {a['group']} / {a['source']}  {a['type']}  {W}x{H}     {res}", fill="black", font=F(21, True))
    for j, line in enumerate(textwrap.wrap(f'"{a["instruction"]}"', 118)[:3]):
        t.text((8, 34 + 22 * j), line, fill=(0, 0, 170), font=F(19, True))
    hints = []
    for k in ("B", "A2", "A1"):
        r = RUNS[k][i]
        if r["hit"]:
            hints.append(f"{k}: hit")
        else:
            hints.append(f"{k}: {off(i, k):.0f} px off" + (", box holds the key centre (too wide)" if wide(i, k) else ""))
    x0, y0, cw, ch = b["window"]
    hints.append("key centre " + ("inside" if x0 <= kx <= x0 + cw and y0 <= ky <= y0 + ch else "OUTSIDE") + f" B's window ({b['window_frac']:.2f} of the screen)")
    hints.append(f"key box {w:.0f}x{h:.0f} px original = {w * a['scale']:.0f}x{h * a['scale']:.0f} px in Jev's full view")
    hints.append("green key  red A1  purple A2  orange B  grey B's window")
    for j, line in enumerate(hints):
        t.text((8, HEAD + oh + 8 + 21 * j), line, fill=(40, 40, 40), font=F(16))
    return out


def zoom(i, cx, cy, side, path):
    a = RUNS["A2"][i]; W, H = a["orig_size"]
    orig = Image.open(ss.DATA / ss.IMAGES / a["file"]).convert("RGB")
    reg = region(cx, cy, side, W, H)
    im = panel(orig, i, reg, f"#{i} closer look", (0, 0, 0)).resize((900, 900), resample=Image.LANCZOS)
    im.save(path, quality=90); print(path, im.size)


def save_case(i):
    case_image(i).save(OUTDIR / f"case_{i:04d}.jpg", quality=88)
    return i


def lang_tile(i, T=300):  # the UI around the key, for telling the interface language; no answers drawn
    a = RUNS["A2"][i]; W, H = a["orig_size"]; x, y, w, h = a["gt_px"]
    orig = Image.open(ss.DATA / ss.IMAGES / a["file"]).convert("RGB")
    x0, y0, s = region(x + w / 2, y + h / 2, max(6 * max(w, h), 480), W, H)
    box = (int(x0), int(y0), int(round(x0 + s)), int(round(y0 + s)))
    im = orig.crop(box).resize((T, T), resample=Image.LANCZOS); d = ImageDraw.Draw(im)
    f = T / (box[2] - box[0])
    d.rectangle([(x - box[0]) * f - 2, (y - box[1]) * f - 2, (x + w - box[0]) * f + 2, (y + h - box[1]) * f + 2], outline=GREEN, width=2)
    d.rectangle([0, 0, 64, 20], fill="white"); d.text((3, 1), f"#{i}", fill="black", font=F(15, True))
    return im


def lang_sheet(k, ids, T=300, cols=4):
    sheet = Image.new("RGB", (cols * T + 10 * (cols - 1), -(-len(ids) // cols) * (T + 10) - 10), (200, 200, 200))
    for j, i in enumerate(ids):
        sheet.paste(lang_tile(i, T), ((j % cols) * (T + 10), (j // cols) * (T + 10)))
    sheet.save(ROOT / "analysis" / "label-audit-pro" / "lang_sheets" / f"lang_{k:03d}.jpg", quality=85)
    return k


if __name__ == "__main__":
    import concurrent.futures as cf
    if sys.argv[1] == "cases":
        ids = [int(v) for v in sys.argv[2:]] or [i for i in range(len(RUNS["B"])) if not RUNS["B"][i]["hit"]]
        OUTDIR.mkdir(parents=True, exist_ok=True)
        with cf.ProcessPoolExecutor(max_workers=3) as ex:
            list(ex.map(save_case, ids, chunksize=4))
        print(len(ids), "case images in", OUTDIR.relative_to(ROOT))
    elif sys.argv[1] == "lang":
        (ROOT / "analysis" / "label-audit-pro" / "lang_sheets").mkdir(parents=True, exist_ok=True)
        ids = list(range(len(RUNS["A2"]))); chunks = [ids[k:k + 16] for k in range(0, len(ids), 16)]
        with cf.ProcessPoolExecutor(max_workers=3) as ex:
            list(ex.map(lang_sheet, range(len(chunks)), chunks))
        print(len(chunks), "language sheets of 16 cases")
    elif sys.argv[1] == "zoom":
        zoom(int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6])
