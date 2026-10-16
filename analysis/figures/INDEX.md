# Figures for the article

All drawn offline from real records or the frozen zoom rule. Redraw any case from run data with
`python3 analysis/figures.py results/passN.jsonl [results/zoomN.jsonl] CASE ... --tag NAME`.
Colours: green = true target, red = first answer (A), blue = zoom window, orange = zoomed answer (B).

| File | What it shows |
|---|---|
| pass1-miss_case_0744.png | Pass 1 miss: "next page" arrow, Jev boxed the whole card row |
| pass1-miss_case_0331.png | Pass 1 miss: "search games", Jev boxed the whole title bar |
| pass1-miss_case_1095.png | Pass 1 miss: Wikipedia "search result", Jev boxed the search field |
| miss_0744_click.png | Design: click-centred window cuts the target out |
| miss_0744_box.png | Design: window grown to hold A's box keeps the target |
| miss_0331_click.png / miss_0331_box.png | Design: a screen-wide box, zoom cannot help |
| miss_1095_click.png / miss_1095_box.png | Design: the case zoom is built for |
| B_sent_744.png, B_sent_1095.png, B_sent_331.png | The exact image the zoom call sends (from pass 1 answers) |
| live-zoom-smoke_case_1095.png | First live zoom call (dev log, Oct 16 ~21:45): B boxed the search field again, FALSE |

Pass 1 also wrote one annotated PNG per miss (212 files, ~70 MB) to `results/1_case_*.png`
(not in git: results/ is ignored). The zoom run will write `results/2_case_*.png` (A misses)
and `results/z2_case_*.png` (B misses).
