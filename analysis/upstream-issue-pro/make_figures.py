"""Figures for the upstream ScreenSpot-Pro label issue. Offline, reads only data/screenspot-pro.
  python3 analysis/upstream-issue-pro/make_figures.py
Red = the stored answer key, [x1, y1, x2, y2] as stored (drawn 3 px outside the box so it does not hide the target).
Green dashed = suggested correction. Blue dashed = another element that also fits (judgment calls only).
No model answers are drawn. Each PNG is kept under MAX_BYTES (palette-quantized if needed)."""
import io, json, pathlib, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "screenspot-pro"
OUT = pathlib.Path(__file__).resolve().parent
RED, GREEN, BLUE, GREY = (225, 0, 0), (0, 165, 0), (0, 90, 255), (95, 95, 95)
NOTO = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
F = lambda s, b=False: ImageFont.truetype(NOTO % ("Bold" if b else "Regular"), s, index=2)  # face 2 = SC
MAX_BYTES = 490_000

CASES = {}
for f in sorted((DATA / "annotations").glob("*.json")):
    for k, c in enumerate(json.loads(f.read_text())):
        CASES[c["id"]] = dict(c, _file=f.name, _k=k)


def dashed(d, box, color, width=3, dash=10):
    x0, y0, x1, y1 = box
    for a, b, horiz in ((x0, x1, True), (y0, y1, False)):
        for s in range(int(a), int(b), dash * 2):
            e = min(s + dash, b)
            if horiz:
                d.line([s, y0, e, y0], fill=color, width=width); d.line([s, y1, e, y1], fill=color, width=width)
            else:
                d.line([x0, s, x0, e], fill=color, width=width); d.line([x1, s, x1, e], fill=color, width=width)


def panel(cid, region=None, fix=(), alt=(), max_w=1100, max_h=800, max_s=6.0, note="", key=True, head=True,
          fix_label="suggested"):
    """Crop `region` (x0, y0, x1, y1 in original px; default whole image; outside the image = black),
    draw the stored key (red), suggested fixes (green dashed) and other fitting elements (blue dashed)."""
    c = CASES[cid]
    im = Image.open(DATA / "images" / c["img_filename"]).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = region or (0, 0, W, H)
    im = im.crop((x0, y0, x1, y1))
    s = min(max_w / im.width, max_h / im.height, max_s)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    tr = lambda b, o=3: ((b[0] - x0) * s - o, (b[1] - y0) * s - o, (b[2] - x0) * s + o, (b[3] - y0) * s + o)
    if key:
        d.rectangle(tr(c["bbox"]), outline=RED, width=3)
    for b in fix:
        dashed(d, tr(b, 5), GREEN)
    for b in alt:
        dashed(d, tr(b, 5), BLUE)
    lines = []
    if head:
        lines += [(f"{c['_file']} [{c['_k']}]   id = {c['id']}   {c['img_filename']} ({W}x{H})", (0, 0, 0), F(16, True)),
                  (textwrap.shorten(f'instruction: "{c["instruction"]}"', 100), (0, 0, 150), F(17, True)),
                  (f'instruction_cn: "{c["instruction_cn"]}"', (0, 0, 150), F(16)),
                  (f"stored bbox [x1, y1, x2, y2] = {c['bbox']}" + (f"   {fix_label} = {list(fix[0])}" if fix else ""), (0, 0, 0), F(16))]
    for n in ([note] if isinstance(note, str) else note):
        if n:
            lines.append((n, GREY, F(15)))
    head_h = 10 + 27 * len(lines)
    text_w = max([16 + font.getlength(txt) for txt, _, font in lines] or [0])
    out = Image.new("RGB", (max(im.width, round(text_w)), im.height + head_h), "white")
    out.paste(im, (0, head_h)); t = ImageDraw.Draw(out)
    for i, (txt, col, font) in enumerate(lines):
        t.text((8, 4 + 27 * i), txt, fill=col, font=font)
    return out


def side(*ims, gap=20):
    out = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), (200, 200, 200))
    x = 0
    for i in ims:
        out.paste(i, (x, 0)); x += i.width + gap
    return out


def stack(*ims, gap=20):
    out = Image.new("RGB", (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), (200, 200, 200))
    y = 0
    for i in ims:
        out.paste(i, (0, y)); y += i.height + gap
    return out


def pair_row(cid, close, overview, note="", close_w=640):
    """One case of a pair: a legible close-up of the target with the header, plus a small overview."""
    a = panel(cid, region=close, max_w=close_w, max_s=2.5, note=note)
    b = panel(cid, region=overview, head=False, max_w=560, max_h=a.height, note="whole area")
    return side(a, b)


def save(im, name):
    """PNG, optimized; palette-quantized and then downscaled only if it would exceed MAX_BYTES."""
    p = OUT / name
    while True:
        buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
        if buf.tell() > MAX_BYTES:
            buf = io.BytesIO(); im.convert("P", palette=Image.ADAPTIVE, colors=256).save(buf, "PNG", optimize=True)
        if buf.tell() <= MAX_BYTES:
            break
        im = im.resize((round(im.width * 0.85), round(im.height * 0.85)), Image.LANCZOS)
    p.write_bytes(buf.getvalue())
    print(f"{p.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}  {buf.tell() // 1024} KB")


if __name__ == "__main__":
    # 1. Wrong answer boxes
    a = panel("blender_windows_19", region=(790, 370, 1000, 450), fix=[(917, 399, 971, 419)], max_s=5,
              note="red = stored key, on the green (Y) arrow   green dashed = suggested, the red (X) arrow (measured by eye)")
    b = panel("blender_windows_19", region=(1545, 105, 1645, 195), key=False, head=False, max_s=4,
              note=["navigation gizmo of the", "same screenshot:", "X = red, Y = green"])
    save(side(a, b), "fig_blender_19_x_axis.png")
    save(panel("matlab_macos_41", region=(1600, 470, 2050, 620), fix=[(1772, 571, 1794, 593)], max_s=3,
               note="red = stored key, the FontSize field   green dashed = suggested, the FontWeight (B) toggle (measured by eye)"),
         "fig_matlab_41_font_weight.png")
    # 2. Wrong English instruction (the key matches instruction_cn) + the box that starts at y = -1
    save(panel("inventor_windows_60", region=(60, -8, 260, 42), fix=[(171, 0, 187, 19)], max_s=6, fix_label="Redo's dropdown",
               note=["red = stored key, the dropdown of Undo (left arrow). 撤销 in instruction_cn means undo, so key and Chinese agree.",
                     "green dashed = Redo's dropdown, the target only if the English 'redo' is kept. Black strip = above the image (y < 0)."]),
         "fig_inventor_60_undo_not_redo.png")
    # 3. Contradictory pair: same screen and words, two non-overlapping keys
    save(stack(panel("pycharm_macos_36", region=(0, 1960, 1500, 2110), note="key: the 'Problems' title of the tool window"),
               panel("pycharm_macos_69", region=(0, 1960, 1500, 2110),
                     note="key: the 'File 18' tab. Same screen 52 s later: only the caret line, the focus and the clock differ.")),
         "fig_pycharm_36_69_contradictory.png")
    # 4. Near-duplicate cases: same words, same key, same UI state; only the drawing changed
    save(stack(pair_row("autocad_windows_14", (0, 50, 430, 240), (0, 30, 1700, 760)),
               pair_row("autocad_windows_25", (0, 50, 430, 240), (0, 30, 1700, 760),
                        note="70 s later: same open Hole (孔) flyout, same key; only the drawing changed")),
         "fig_autocad_14_25_near_duplicate.png")
    save(stack(pair_row("inventor_windows_1", (440, 20, 1000, 140), (0, 0, 1400, 1000)),
               pair_row("inventor_windows_43", (440, 20, 1000, 140), (0, 0, 1400, 1000),
                        note="104 s later: same ribbon, same key (粘贴, Paste); only the sketch changed")),
         "fig_inventor_1_43_near_duplicate.png")
    # 5. Wording: the English points elsewhere, is cut short, or translates the Chinese label word for word
    save(panel("inventor_windows_68", region=(880, 30, 1960, 300),
               note="red = stored key: 主视图 (Home View, house icon). The ViewCube on the right shows its 前 (Front) face."),
         "fig_inventor_68_home_view.png")
    save(panel("origin_windows_42", region=(1150, 50, 1500, 110), max_s=3,
               note="key = Import Excel (by app knowledge), which imports from Excel; both instructions say into Excel"),
         "fig_origin_42_import_excel.png")
    save(panel("inventor_windows_54", region=(60, 20, 420, 130), max_s=3, note="key = 圆弧 (Arc); instruction_cn says 画圆弧, draw an arc"),
         "fig_inventor_54_arc.png")
    save(panel("powerpoint_windows_1", region=(0, 0, 500, 140), max_s=2.5, note="key = Undo; 'Und' is cut short (撤销 = undo)"),
         "fig_powerpoint_1_und.png")
    save(panel("vivado_windows_56", region=(740, 740, 1300, 900), max_s=2,
               note="the IP Properties pane is already open; the key is its ? (help) button (cf. vivado_windows_34 and _59)"),
         "fig_vivado_56_help.png")
    save(panel("fruitloops_windows_21", region=(0, 60, 300, 160), max_s=4,
               note="key = the Browser's Search (magnifier) button; 'fine' is probably 'find'"),
         "fig_fruitloops_21_search.png")
    save(panel("solidworks_windows_18", region=(450, 20, 900, 125), max_s=2.5, note="key = 抽壳 (Shell)"),
         "fig_solidworks_18_shell.png")
    save(panel("solidworks_windows_54", region=(300, 0, 760, 260), max_s=2, note="key = Insert (插入) > 配合 (Mate)"),
         "fig_solidworks_54_mate.png")
    save(panel("solidworks_windows_70", region=(0, 30, 400, 400), max_s=2,
               note="key = 智能尺寸 (Smart Dimension), top item of the open dimension dropdown"),
         "fig_solidworks_70_dimension.png")
    save(panel("solidworks_windows_2", region=(0, 30, 420, 140), max_s=2.5, note="key = 质量属性 (Mass Properties)"),
         "fig_solidworks_2_mass_properties.png")
    save(panel("solidworks_windows_64", region=(250, 30, 600, 140), max_s=2.5, note="key = 等距实体 (Offset Entities)"),
         "fig_solidworks_64_offset.png")
    save(panel("autocad_windows_21", region=(200, 40, 700, 160), max_s=2.5,
               note="key = datum identifier (基准标识, by app knowledge); 基准 = datum here"),
         "fig_autocad_21_datum.png")
    save(panel("autocad_windows_30", region=(60, 40, 560, 160), max_s=2.5,
               note="key = 引线注释 (Leader Note); instruction_cn has 引出注释"),
         "fig_autocad_30_leader_note.png")
    # 6. Judgment calls (opinions)
    save(panel("matlab_macos_70", region=(170, 60, 660, 300), alt=[(256, 111, 325, 172)], max_s=2.5,
               note="red = stored key ('area' under MATLAB LINE PLOTS)   blue dashed = the same 'area' command under FAVORITES"),
         "fig_matlab_70_area_twice.png")
    save(panel("matlab_macos_13", region=(0, 40, 400, 140), alt=[(5, 54, 42, 123)], max_s=3.5,
               note="red = stored key (the 'New' dropdown)   blue dashed = 'New Script', which does this in one click"),
         "fig_matlab_13_new_script.png")
    save(panel("eviews_windows_26", region=(1000, 600, 1300, 720), alt=[(1081, 674, 1256, 691)], max_s=3,
               note="red = stored key (checkbox square only)   blue dashed = its label, which toggles the same checkbox"),
         "fig_eviews_26_checkbox_label.png")
