"""Per-error analysis of a pass: distance from Jev's click to the target, per cell, plus systematic offset.
  python3 analysis/errors.py results/pass1.jsonl  -> analysis/errors_pass1.csv + analysis/ERRORS-pass1.md"""
import csv, json, math, pathlib, statistics, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import screenspot as ss

path = pathlib.Path(sys.argv[1]); name = path.stem
R = sorted(ss.latest(ss.read(path)).values(), key=lambda r: r["i"])
BUCKETS = [(0, 10), (10, 25), (25, 50), (50, 100), (100, 300), (300, 10 ** 9)]

def geo(r):
    W, H = r["orig_size"]; s = r["scale"]; x, y, w, h = r["gt_px"]
    px, py = r["point"][0] * W, r["point"][1] * H
    dx = (x - px) if px < x else (px - (x + w)) if px > x + w else 0.0
    dy = (y - py) if py < y else (py - (y + h)) if py > y + h else 0.0
    d = math.hypot(max(dx, 0), max(dy, 0))
    cx, cy = x + w / 2, y + h / 2
    b = r["box"]
    return {"dist_orig_px": d, "dist_sent_px": d * s, "dist_pct_diag": 100 * d / math.hypot(W, H),
            "off_x_rel": (px - cx) / w, "off_y_rel": (py - cy) / h,  # offset of click from target centre, in target widths/heights
            "dir": ("up" if py < y else "down" if py > y + h else "") + ("-left" if px < x else "-right" if px > x + w else ""),
            "tgt_sent_w": w * s, "tgt_sent_h": h * s,
            "jev_box_sent_w": (b["right"] - b["left"]) * W * s, "jev_box_sent_h": (b["bottom"] - b["top"]) * H * s,
            "box_contains_target_centre": b["left"] * W <= cx <= b["right"] * W and b["top"] * H <= cy <= b["bottom"] * H}

rows = []
for r in R:
    if r["status"] != "ok":
        continue
    g = geo(r)
    rows.append({**{k: r[k] for k in ("i", "platform", "type", "source", "instruction", "hit", "confidence", "file")}, **g})
miss = [x for x in rows if not x["hit"]]
out_csv = path.parent.parent / "analysis" / f"errors_{name}.csv"
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(miss[0].keys())); w.writeheader()
    for m in sorted(miss, key=lambda m: (m["platform"], m["type"], m["dist_sent_px"])):
        w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})

L = [f"# Errors in {name} (Jev 1.14 box, ScreenSpot-v2)", "",
     f"{len(miss)} misses of {len(rows)} scored. Distance = from Jev's click point to the nearest edge of the true box, "
     "in pixels of the image Jev saw (sent px) and as % of the screen diagonal.", ""]
L += ["| Cell | n | misses | median dist (sent px) | <=10 | 10-25 | 25-50 | 50-100 | 100-300 | >300 | median % diag | box covered target centre |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for p, t in ss.CELLS:
    cell = [x for x in rows if x["platform"] == p and x["type"] == t]
    ms = [x for x in cell if not x["hit"]]
    ds = [m["dist_sent_px"] for m in ms]
    bk = [sum(lo <= d < hi for d in ds) for lo, hi in BUCKETS]
    L.append(f"| {p} {t} | {len(cell)} | {len(ms)} | {statistics.median(ds):.0f} | " + " | ".join(map(str, bk)) +
             f" | {statistics.median(m['dist_pct_diag'] for m in ms):.1f}% | {sum(m['box_contains_target_centre'] for m in ms)} |")
ds = [m["dist_sent_px"] for m in miss]
bk = [sum(lo <= d < hi for d in ds) for lo, hi in BUCKETS]
L.append(f"| **all** | {len(rows)} | {len(miss)} | {statistics.median(ds):.0f} | " + " | ".join(map(str, bk)) +
         f" | {statistics.median(m['dist_pct_diag'] for m in miss):.1f}% | {sum(m['box_contains_target_centre'] for m in miss)} |")
L += ["", "## Systematic offset (all scored cases)",
      "Mean offset of the click from the target centre, in target widths (x) / heights (y). Positive = right / down.", "",
      "| Cell | mean x | mean y | hits mean x | hits mean y |", "|---|---|---|---|---|"]
for p, t in ss.CELLS + [("all", "all")]:
    cell = [x for x in rows if (p == "all" or (x["platform"] == p and x["type"] == t))]
    h = [x for x in cell if x["hit"]]
    L.append(f"| {p} {t} | {statistics.mean(x['off_x_rel'] for x in cell):+.2f} | {statistics.mean(x['off_y_rel'] for x in cell):+.2f} | "
             f"{statistics.mean(x['off_x_rel'] for x in h):+.2f} | {statistics.mean(x['off_y_rel'] for x in h):+.2f} |")
dirs = {}
for m in miss:
    dirs[m["dir"].strip("-") or "inside?"] = dirs.get(m["dir"].strip("-") or "inside?", 0) + 1
L += ["", "Direction of misses: " + ", ".join(f"{k} {v}" for k, v in sorted(dirs.items(), key=lambda x: -x[1])), ""]
L += ["## Every miss", "", "| # | Cell | Instruction | Target (sent px) | Dist (sent px) | Dir | Conf |", "|---|---|---|---|---|---|---|"]
for m in sorted(miss, key=lambda m: (ss.CELLS.index((m["platform"], m["type"])), m["dist_sent_px"])):
    ins = m["instruction"].replace("|", "/")[:50]
    L.append(f"| {m['i']} | {m['platform']} {m['type']} | {ins} | {m['tgt_sent_w']:.0f}x{m['tgt_sent_h']:.0f} | "
             f"{m['dist_sent_px']:.0f} | {m['dir'].strip('-')} | {m['confidence']} |")
out_md = path.parent.parent / "analysis" / f"ERRORS-{name}.md"
out_md.write_text("\n".join(L) + "\n")
print("\n".join(L[:30]))
print(f"\n-> {out_md}\n-> {out_csv}")
