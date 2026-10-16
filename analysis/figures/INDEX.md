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
| live-zoom-smoke_case_1095.png | First live zoom call (dev log, Oct 16 21:35): B boxed the search field again, FALSE |

## Run 2: zoom fixes and breaks
Drawn with `analysis/figures.py results/pass2.jsonl results/zoom2.jsonl CASE --tag zoom-fix|zoom-break` (same colours as above).

| File | What it shows |
|---|---|
| zoom-fix_case_0625.png | "click to choose shapes": A boxes a tall strip (conf 0.27), B hits (0.75) |
| zoom-fix_case_1148.png | "open keras": A boxes Keras + Kubeflow, B hits (conf 0.95) |
| zoom-fix_case_0524.png | "view the personal account": A 3-6 px below the avatar, B hits |
| zoom-fix_case_1248.png | "close the pop-up window in the bottom right corner": tiny x, B hits |
| zoom-break_case_0057.png | Context loss: the crop cuts "Allow Siri When Locked" to "ed", B picks the toggle above |
| zoom-break_case_1032.png | Context loss: the crop cuts the first news item, "the third" is counted from the second |
| zoom-break_case_0708.png | Neighbour pick: "remove a network connected device", B picks + instead of - (conf 0.84) |
| zoom-break_case_0972.png | Ambiguous label: "add comment", B picks the Post button |

## Label audit (analysis/LABELS-audit.md)
Drawn with `analysis/label_figures.py full CASE ...`. Colours: green = answer key, red = pass 1, purple = pass 2,
orange = zoom answer, grey = zoom window, dot = the click.

| File (labels/) | What it shows |
|---|---|
| case_0458.png | Key error: key box copied from #455, lands on empty space; all three answers on the right toggle |
| case_0455.png | Where #458's key box comes from (keyboard, "switch to uppercase input": Shift vs abc) |
| case_0487.png | Key error: key on Notifications, all three answers on Fahrenheit |
| case_1035.png | Key error: "log in by x account", key on the YouTube icon |
| case_1037.png | Key error: "check the weather news", key on DelmarvaLife; B on Weather |
| case_1031.png | Two valid answers: sidebar "Create new page" vs the key "Create this page" |
| case_0089.png / case_0091.png | Same screenshot: #89's key is the ... menu, #91's key is the MORE link Jev picks on #89 |
| case_1214.png | Two valid answers: source or target language |
| case_0734.png | Two valid answers: two paperclips |
| case_1096.png | Same control: the footer logo and title are one link, the key marks only the title |
| case_1236.png | Same control: the radio's label clicked, the key marks only the circle |
| case_1097.png | Loose wording: "goto france wikipedia" on the Wiktionary portal |
| case_0986.png | Loose wording: "the first book" on a page of posts |
| case_0281.png | Cannot verify: which brush is watercolor |
| case_0127.png | Pattern: selected-state pull (picks the highlighted 30 mins) |
| case_0121.png | Pattern: "play next song" picks previous |
| case_1038.png | Pattern: label-name pull (picks the author name, not Follow) |
| case_1200.png | Pattern: "four stars" boxes the first four stars |

Audit sheets, every missed case with all three answers (JPEG): `analysis/label-audit/sheets/`
(wrong_element_00..25, near_00..13, zoom_breaks_00..08; grey = zoom window on the break sheets).

Pass 1 also wrote one annotated PNG per miss (212 files, ~70 MB) to `results/1_case_*.png`
(not in git: results/ is ignored). The zoom run will write `results/2_case_*.png` (A misses)
and `results/z2_case_*.png` (B misses).
