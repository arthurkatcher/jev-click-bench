# Deep audit of the three runs (Jev 1.14 box, ScreenSpot-Pro)

Oct 17 2026. A1 = pass 1 (raw), A2 = pass 2 (the same raw request again), B = the zoom answer (stage B, built on A2). The same structure as the v2 audit (`AUDIT-run2.md`), point by point, plus the two benchmarks side by side and what it all leads to.
Every number below is printed by `python3 analysis/audit_pro_run2.py`. Add `--images` for the image rebuild and `--balance` for the key balance. The integrity checks are asserts: the script stops if any of them fails. The by-eye side (the breaks here, all 905 of B's misses in `LABELS-audit-pro.md`) uses `analysis/pro_label_figures.py`.

## 1. Integrity: everything checked passed

- **Records.** 1581 lines per file, one per case, all status ok. 0 retries (attempts = 1 on all 4,743 answers), 0 malformed answers, 0 infrastructure errors.
- **Identity.** Every record was checked against the official annotation files as published: screenshot file, instruction, platform, type, group, id and app. Our stored [x, y, w, h] gives back the official [x1, y1, x2, y2] exactly. 1581 screenshot files, one per case (30 of them are byte-identical copies of another case's file, so 1,551 distinct images; see `LABELS-audit-pro.md`), and every size in the records matches both the image file and the annotation's img_size.
- **Prompt.** All 4,743 requests sent the frozen v2 wording (hash a723751c1725), rebuilt here from the raw instruction.
- **Model.** Every answer resolved to `typesafe/jev-1.14-20261014`, provider TypeSafe.
- **Rescore.** Every raw API answer was parsed again, the click recomputed, and a verbatim copy of the official `eval_sample_positive_gt` applied to the raw annotation: A1 303, A2 295, B 676 hits, the same as logged.
- **Zoom mechanics.** Every B window was rebuilt from A2's record alone with the frozen rule (0.5 of each side, 10% margin), and every B box was mapped back to the full screenshot again: all match. B always sends A2's image size. In all 1581 cases, B started after its own A2 answer.
- **Images.** All 3,162 sent images were rebuilt (A once, shared by A1 and A2; B from its window). Payload lengths match exactly.
- **Code.** Pass 1 ran at commit 4099bfa, run 2 at 3cc1088. The stage-A and zoom code is identical in both: image fit, PNG encoding, request, API call, parsing, scoring, loading, zoom window, wording and model constants. The zoom, image and request code is also identical to v2's run 2 (bb538fc), so Pro ran the v2 method unchanged.
- **Answer format.** Jev answers on a 0.01 grid: every box edge is a multiple of 0.01 of the image. Output is always 20 tokens.
- **Flags.** Degenerate boxes (zero or negative width or height): A1 14, A2 18, B 6 (#69, #747, #753, #764, #925, #1240), scored by their centre like the official rule. Clicks exactly on a key edge: A1 13, A2 17, B 13. No box outside the screenshot, no B box past its crop, and no case where a 1e-9 edge tolerance would change a hit.
- **Sent sizes.** Every Pro screenshot is downscaled to fit 1568 px: 14 screen sizes, from 1920x1080 at 0.82x to 6016x3384 at 0.26x. On v2, 238 cases were sent at native size; on Pro none are.
- **Timeline (CEST).** Pass 1 ran 09:24:34-09:33:27: 533 s with 4 workers, no gap over 5 s. Run 2 (A2 + B) ran 09:36:49-09:54:13: 1044 s with 4 workers, one 6 s gap (before case 462). A2 calls follow case order.
- **Money.** Every answer was billed at exactly $0.042 per 1M input tokens; output tokens are free. Logged cost: A1 $0.252335, A2 $0.252333, B $0.252339. The key read $1.052508 before pass 1 (pass1 log) and reads $0.295005 now (Oct 17 10:34): exactly the three runs' logged $0.757008 plus a 3-case raw smoke (pass 0, cases 3-5, $0.000495) that ran 17 s before pass 1, after that reading. Nothing on the key is unexplained.

## 2. Accuracy

| Run | Hits | Micro % | 95% CI | Macro % |
|---|---|---|---|---|
| A1 raw | 303 | 19.17 | 17.30-21.18 | 17.66 |
| A2 raw | 295 | 18.66 | 16.82-20.65 | 17.02 |
| B zoom | 676 | 42.76 | 40.34-45.21 | 39.23 |

| Cell | A1 | A2 | B |
|---|---|---|---|
| CAD text | 12.69 | 12.69 | 44.67 |
| CAD icon | 15.62 | 14.06 | 18.75 |
| Dev text | 27.92 | 30.52 | 64.29 |
| Dev icon | 7.59 | 6.90 | 19.31 |
| Creative text | 20.20 | 19.70 | 52.53 |
| Creative icon | 5.59 | 2.80 | 13.99 |
| Scientific text | 38.89 | 36.81 | 64.58 |
| Scientific icon | 7.27 | 6.36 | 24.55 |
| Office text | 41.81 | 41.24 | 66.10 |
| Office icon | 15.09 | 13.21 | 33.96 |
| OS text | 15.89 | 17.76 | 52.34 |
| OS icon | 3.37 | 2.25 | 15.73 |

| Paired | Miss->hit | Hit->miss | Exact McNemar p | Bootstrap 95% CI, pp |
|---|---|---|---|---|
| A1 -> A2 (rerun) | 64 | 72 | 0.549 | -1.96 to +0.95 |
| A2 -> B (zoom vs its own A) | 436 | 55 | 1.2e-74 | +21.63 to +26.63 |
| A1 -> B | 431 | 58 | 1.7e-71 | +21.13 to +26.06 |

B against the mean of the two raw runs: +23.85 pp (95% CI +21.47 to +26.22).

| A1, A2, B | Cases |
|---|---|
| hit, hit, hit | 195 |
| miss, miss, miss | 828 |
| miss, miss, hit | 386 |
| hit, hit, miss | 36 |
| miss, hit, hit | 45 |
| hit, miss, hit | 50 |
| miss, hit, miss | 19 |
| hit, miss, miss | 22 |

Of the 1,214 cases both raw runs missed, zoom fixed 386 (32%). Of the 231 both got right, it broke 36 (16%). On v2 these were 47% and 3.9%: on Pro a raw hit is often a lucky edge hit, so it is easier to lose.

| Group (A2 -> B) | n | A2 % | B % | Delta pp | Fixed | Broken | p |
|---|---|---|---|---|---|---|---|
| CAD | 261 | 13.03 | 38.31 | +25.3 | 78 | 12 | 5.2e-13 |
| Dev | 299 | 19.06 | 42.47 | +23.4 | 86 | 16 | 9.1e-13 |
| Creative | 341 | 12.61 | 36.36 | +23.8 | 87 | 6 | 1.7e-19 |
| Scientific | 254 | 23.62 | 47.24 | +23.6 | 67 | 7 | 2.1e-13 |
| Office | 230 | 34.78 | 58.70 | +23.9 | 67 | 12 | 2.0e-10 |
| OS | 196 | 10.71 | 35.71 | +25.0 | 51 | 2 | 3.2e-13 |
| text | 977 | 26.20 | 57.01 | +30.8 | 339 | 38 | 1.6e-61 |
| icon | 604 | 6.46 | 19.70 | +13.2 | 97 | 17 | 8.6e-15 |

- Every group gains almost exactly the same, +23 to +25 pp, from very different starting points.
- Every cell gains, and 11 of 12 significantly. The exception is CAD icon: +4.7 pp, 8 fixed and 5 broken, p=0.58.
- Text gains more than twice what icons gain (+30.8 vs +13.2 pp).

## 3. How noisy is a rerun

- Same request twice: the box is identical in 302 of 1581 cases, box and confidence together in 41. Jev is not deterministic.
- The click moves a median 7.8 px in the image Jev saw (v2: 4.8). The two boxes overlap by IoU 0.5 or more in 75.8% of cases (v2: 94.2%), and 112 cases switch to another element (IoU under 0.1; v2: 22).
- 136 cases (8.6%) flip between hit and miss (v2: 49, 3.9%). In 86 of them the miss sits within 5 px of the target; 4 switch element. So the flips are edge cases: the same small jitter crosses the edge of a tiny target much more often.
- Confidence repeats closely between the raw passes (correlation 0.981) but not after zoom (0.602 between A2 and B), since B judges a different image.
- Input tokens differ by -8 to +10 on identical requests. Cost effect: none worth counting.

## 4. Why zoom helps

| Target size in A's image | n | A2 % | B % | Delta pp | Fixed | Broken | p |
|---|---|---|---|---|---|---|---|
| under 10 px | 182 | 2.75 | 6.59 | +3.8 | 10 | 3 | 0.092 |
| 10-15 px | 308 | 2.27 | 16.88 | +14.6 | 50 | 5 | 2.1e-10 |
| 15-20 px | 261 | 6.90 | 29.12 | +22.2 | 69 | 11 | 2.0e-11 |
| 20-30 px | 371 | 17.79 | 53.10 | +35.3 | 145 | 14 | 1.3e-28 |
| 30-45 px | 338 | 39.35 | 70.41 | +31.1 | 120 | 15 | 1.6e-21 |
| 45-60 px | 86 | 47.67 | 84.88 | +37.2 | 35 | 3 | 6.7e-08 |
| 60 px and up | 35 | 71.43 | 80.00 | +8.6 | 7 | 4 | 0.55 |

Target size = square root of the key box area, in px of the image Jev saw. The median Pro target is 20.9 px in A's image (v2: 92.1) and 41.7 px in B's (v2: 182.7). It covers 0.035% of the screen (v2: 0.72%). On v2 the zoom gain stopped at 60 px; on Pro, 95% of the targets are under 45 px, so almost the whole benchmark sits in the range where zoom helps.

**The main finding: zoom works by size alone, and Pro is harder than v2 at every size.**

| Apparent target size | Pro raw A2 (size in A's image) | v2 raw A2 | Pro zoom B (size in B's image) |
|---|---|---|---|
| 10-20 px | 4.39 (n=569) | 0.0 (n=3) | 6.94 (n=173) |
| 20-30 px | 17.79 (n=371) | 54.17 (n=24) | 17.32 (n=306) |
| 30-45 px | 39.35 (n=338) | 60.17 (n=118) | 32.58 (n=356) |
| 45-60 px | 47.67 (n=86) | 72.55 (n=153) | 58.36 (n=269) |
| 60-80 px | 66.67 (n=21) | 87.21 (n=219) | 69.96 (n=273) |
| 80-120 px | 77.78 (n=9) | 88.73 (n=284) | 79.33 (n=150) |

- **Read across one row: zoom = a bigger target, nothing else.** After zoom, a target that is 30-45 px in the image B saw is hit about as often as a raw target of 30-45 px (32.6 vs 39.4), and the same holds in every row. The crop neither costs (lost context) nor adds anything beyond the size it buys. So more size should keep paying: the curve is still climbing at 80-120 px.
- **Read down the columns: Pro is harder than v2 at the same size.** Raw Pro is 20-35 pp below raw v2 at the same apparent size (20-30 px: 17.8 vs 54.2; 45-60 px: 47.7 vs 72.6; 60-80 px: 66.7 vs 87.2). By type, at 20-45 px: text 29.2 vs 65.0, icons 18.4 vs 58.2. So the "20x smaller targets" explain a large part of the gap, not all of it. The rest is what the targets are: dense professional toolbars, unlabelled tool icons, unfamiliar apps and non-English interfaces (`LABELS-audit-pro.md` measures each).

**The 0.01 answer grid.** 562 targets are smaller than one 0.01 step on a side in A's view, 83 still are in B's view (v2: 1 and 0).

| Grid group | n | A2 % | B % |
|---|---|---|---|
| sub-step in A's view, not in B's | 479 | 5.64 | 19.42 |
| sub-step in both views | 83 | 1.20 | 2.41 |
| not sub-step in A's view | 1019 | 26.20 | 57.02 |

A target that stays under one grid step after zoom is almost never hit (2 of 83). The grid is part of the size story: zoom makes each step finer on the target, the same way it makes the target bigger.

**It is not the resolution alone.** By screen size, zoom adds about the same at every sent scale: 0.25-0.35x +23.9 pp (n=142), 0.35-0.5x +23.0 (n=662), 0.5-0.65x +25.2 (n=659), 0.65-0.85x +24.6 (n=118). Big screens start lower (4K at 0.41x: 12.2 -> 31.9; 5120x1440 at 0.31x: 6.6 -> 31.1) and stay lower after zoom: a half window of a 4K screen is still sent at only 0.82x. The 19 cases on 1920x1080 screens (sent at 0.82x) do not move (15.8 -> 15.8, 1 fixed, 1 broken). Every Pro screenshot is downscaled, so unlike v2 the pixel and size effects cannot be separated here.

**Precision.** On the 240 cases both answers hit, B's click is a median 6.5 px from the target centre vs 11.9 px for A2 (0.40 vs 0.66 of half the target). Boxes more than 1.5x the target's width drop from 61.4% to 37.6% of answers (median box width / target width 2.02 -> 1.20), and too-wide misses from 395 to 274.

**Which A2 misses get fixed** (px in the image Jev saw, both benchmarks in the same units):

| A2 miss | Pro n | Pro fixed | v2 n | v2 fixed |
|---|---|---|---|---|
| too-wide box (holds the target centre) | 395 | 51.9% | 78 | 55.1% |
| off target, 15 px or less | 93 | 57.0% | 35 | 88.6% |
| off target, 15-60 px | 321 | 33.0% | 38 | 50.0% |
| off target, over 60 px | 477 | 15.1% | 48 | 4.2% |
| target centre outside B's window (overlaps the rows above) | 151 | 0 | 29 | 1 |

- Near misses get fixed less often than on v2 (57% vs 89%) because a Pro target is still small after zoom.
- Far misses get fixed more often (15% vs 4%): half of a 4K screen is a big window, so a wrong element 60+ px away still leaves the target inside it, and B finds it again.
- The ceiling: when A2 missed (1286), the target centre was inside B's window 1135 times, and B fixed 436 of those (38.4%). The other 151 cannot be fixed by construction.

**Where.**

| Best after zoom | A2 -> B | Worst after zoom | A2 -> B |
|---|---|---|---|
| Word (n=84) | 48.8 -> 75.0 | Origin (n=62) | 9.7 -> 17.7 |
| EViews (n=50) | 42.0 -> 74.0 | Premiere (n=52) | 9.6 -> 25.0 |
| PowerPoint (n=82) | 37.8 -> 62.2 | Windows common (n=81) | 6.2 -> 28.4 |
| MATLAB (n=93) | 32.3 -> 60.2 | Quartus (n=45) | 17.8 -> 28.9 |

- The gain is not significant (p over 0.05) on five small apps: Origin (+8.1, p=0.18), Quartus (+11.1, p=0.23), Unreal Engine (+17.1, p=0.11), AutoCAD (+20.6, p=0.092) and Illustrator (+22.6, p=0.065). The biggest gains: Blender +32.4, EViews +32.0, Photoshop +29.4, VMware +29.3.
- By OS: Windows 15.4 -> 38.8 (n=927), macOS 24.3 -> 49.2 (n=604), Linux 10.0 -> 38.0 (n=50).

**By A2's confidence, zoom helps everywhere.** 0-0.3: 2.9 -> 20.9 (n=450); 0.3-0.5: 11.5 -> 37.0 (n=322); 0.5-0.7: 21.2 -> 45.7 (n=363); 0.7-0.9: 36.1 -> 65.9 (n=393); 0.9 and up: 49.1 -> 71.7 (n=53). On v2 the gain sat almost all under 0.3. A confidence gate would only lose hits on Pro.

**Window types.** 1534 half windows (true 2x): 19.2 -> 43.7, 432 fixed, 55 broken. 23 widened for a big A box: 4.3 -> 21.7, 4 fixed, 0 broken. 24 full screen (A's box was so big that B re-asks the same image): all 24 missed by both, 0 flips.

## 5. What zoom costs: the 55 breaks (A2 hit, B miss)

All 55 were viewed (`analysis/label-audit-pro/sheets/breaks_*.jpg`).

| Kind | Breaks | CAD | Dev | Creative | Scientific | Office | OS |
|---|---|---|---|---|---|---|---|
| Precision: right element, click just off | 34 | 4 | 14 | 4 | 5 | 6 | 1 |
| Neighbour pick | 14 | 6 | 1 | 2 | 0 | 5 | 0 |
| Wrong element far away | 5 | 2 | 1 | 0 | 0 | 1 | 1 |
| Ambiguous label (#759) | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| Answer-key error (#657) | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| Context loss: the crop cut the naming label | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

- **No context loss on Pro (v2: 14).** The target centre was inside B's window in all 55 breaks. Half of a 2.5K-6K desktop screen keeps the whole toolbar or panel around a target, and desktop apps put the label next to the control, not across a phone-wide row. The main cost of the design on v2 does not show up here.
- **Precision slips are edge noise.** All 34 are within one target size of the key box or too-wide; the median click is 2.4 px off. A2 was barely in and B is barely out, the same kind of flip a plain rerun makes (86 of the 136 rerun flips are within 5 px).
- **Neighbour picks (14)** are most of the real breaks: B lands on the control next to the target in a dense toolbar or ribbon. Two are telling: #857, where B picks the tooltip that repeats the instruction's words, and #844, where B picks the status-bar Notes button.
- **Wrong element far away (5):** four of them at very low B confidence (#972, #1123, #1284, #1431, 0.04-0.20). The fifth, #1580 "home tab" at 0.72, picks the house icon in the title bar instead of the Home ribbon tab.
- **#657 is a key error, and B is right.** "Edit font weight": the key marks the FontSize "10" field, and B is on the FontWeight "B" button next to it. A2's too-wide box happened to hold the key.
- **#759 is ambiguous:** two scatter-plot (散点图) controls are on screen, the gallery button and the item in the open fly-out (the key). B's box spans both, and its centre lands on the fly-out header between them, a blend box like v2's #563.
- B's confidence dropped in only 23 of the 55 breaks (v2: 32 of 50), and it rose in 324 of the 436 fixes. B's own confidence does not flag its breaks.

**No replay this time.** On v2, the crop was chosen offline from pass-1 answers and a prediction (85.8%) was registered before the zoom run. On Pro, the same frozen 2x rule was reused untouched and nothing on Pro was looked at to choose it, so no Pro prediction was made.

## 6. Confidence and agreement

- AUROC (how well confidence separates hits from misses): A1 0.760, A2 0.765, B 0.756. B minus A2: -0.009, 95% CI -0.043 to +0.023. Flat. On v2, zoom raised it by +0.107.

| Confidence | B cases | B right % | A2 cases | A2 right % |
|---|---|---|---|---|
| 0.5 or more | 1136 (71.9%) | 54.23 | 809 (51.2%) | 30.28 |
| 0.7 or more | 728 (46.0%) | 63.05 | 446 (28.2%) | 37.67 |
| 0.8 or more | 407 (25.7%) | 68.06 | 233 (14.7%) | 43.78 |
| 0.9 or more | 61 (3.9%) | 68.85 | 53 (3.4%) | 49.06 |

Under 0.5: B 445 cases, 13.48% right; A2 772 cases, 6.48% right.

- **Confidence ranks, but it is not calibrated on Pro.** B says 0.8 or more on 407 answers and is right on 68% of them (v2: 96.4%). Above 0.8 it stops improving (0.9 or more: 68.9%).
- **Agreement as a signal.** A2 and B agree on 481 cases (each click inside the other's box), and B is right on 60.9% of those. They disagree on 1100: B right 34.8%, A2 right 6.0%.
- **Post-hoc selectors, not the protocol.** Taking the higher-confidence of A2 and B gives 37.76%, below always-B (42.76%), which again supports the no-gate design. Majority of three: 20.62%. Oracle A2 or B: 46.24%. Oracle any of the three: 47.63%. So choosing among the answers we already have is worth at most about 5 pp, even with perfect hindsight. The headroom is in new looks, not in picking.

## 7. Cost and speed

- Tokens = 343 + 0.002589 x sent pixels (max residual 67): about one token per 20x20 px patch, as on v2 (423 + 0.002529).
- Input tokens per run: A1 6,007,986, A2 6,007,925, B 6,008,079 (B - A2 per case: -9 to +9).
- Per click: A $0.000160, A+B $0.000319 ($0.32 per 1,000 clicks). The whole benchmark: $0.25 raw, $0.50 with zoom.
- Latency, median (p90): A1 0.827 s (1.364), A2 0.888 s (1.396), B 0.814 s (1.212). A+B per click 1.720 s (2.600). Slowest single answer 6.3 s.
- Wall time on 4 workers: pass 1 533 s, run 2 1044 s.

## 8. What is left: B's 905 misses

| B's click to the key box (px in A's image) | B misses | Text | Icon | Box too wide |
|---|---|---|---|---|
| within 5 px | 239 | 141 | 98 | 159 |
| 5-15 px | 190 | 95 | 95 | 73 |
| 15-60 px | 201 | 75 | 126 | 30 |
| 60-200 px | 75 | 39 | 36 | 9 |
| over 200 px | 200 | 70 | 130 | 3 |

- **They are hard cases for every run.** All three runs miss 828 of the 905.
- **Near and far misses.** 429 misses (47%) are within 15 px, and 275 (30%) are over 60 px. Office has the highest share of near misses (60 of its 95), and Scientific of far ones (52 of its 134).
- **The targets B misses are small.** The median is 30.6 px in B's image, against 60.0 for B's hits. 81 of them are still under one 0.01 grid step.
- **The first look was elsewhere in 151 cases.** The target centre was outside B's window, because A2's answer was already in the wrong part of the screen. No crop around it can fix these.
- **By eye** (all 905, `LABELS-audit-pro.md`):
  - wrong element 462, of which 60% have no visible text naming the target;
  - right element with the click off, 376, mostly boxes too wide over the target and its neighbours (252);
  - label issues 67;
  - crop cut the naming label: 0.
- **The ceiling for one more zoom step (post-hoc).**
  - A 4x window (a quarter of each side) centred on B's answer would still hold the target centre in 700 of the 905 misses, and in 675 of the 676 hits.
  - Each target would be twice its size in B's image. For the misses, that is a median of about 61 px, where the size curve in section 4 hits about two in three.
  - But these are cases B already failed at their size, so the real fix rate would be lower.
  - This idea comes from looking at Pro run 2's answers, so it cannot be a clean test on Pro (section 11).

## 9. v2 and Pro side by side

| | ScreenSpot-v2 | ScreenSpot-Pro |
|---|---|---|
| Cases | 1272 | 1581 |
| A1 raw % | 83.33 | 19.17 |
| A2 raw % | 84.36 | 18.66 |
| B zoom % | 87.89 | 42.76 |
| Zoom gain over its own A, pp | +3.54 | +24.10 |
| Zoom fixed / broken | 95 / 50 | 436 / 55 |
| Rerun flips | 3.9% | 8.6% |
| Zoom flips | 11.4% | 31.1% |
| Target median, A's image | 92.1 px | 20.9 px |
| Target median, B's image | 182.7 px | 41.7 px |
| A2 miss, median distance | 22.4 px | 38.3 px |
| Too-wide share of A2 misses | 39.2% | 30.7% |
| Context-loss breaks | 14 | 0 |
| AUROC A2 -> B | 0.651 -> 0.758 | 0.765 -> 0.756 |
| B at confidence 0.8 or more, right | 96.4% | 68.1% |
| Per click, A+B | $0.000300 | $0.000319 |
| A+B latency, median | 1.665 s | 1.720 s |
| B misses with a label issue | 35 of 154 (23%) | 67 of 905 (7.4%) |
| Answer-key errors | 4 | 3 |
| Same request, two different keys | 0 | 3 pairs |
| Duplicate cases | 1 | 2 |
| Crop cut the naming label (B misses) | 14 | 0 |

- **v2: the score was close to its ceiling.** About one zoom miss in four sat on a label issue, and the main cost of zoom was crops cutting row labels on mobile.
- **Pro: the misses are the model.**
  - About one miss in fourteen is a label issue, worth at most 2.28 pp. The other 838 split into the wrong element (462) and the right element with the click off (376).
  - Zoom never cut a naming label on Pro's large desktop screens.

## 10. Corrections to earlier statements

- REPORT.md (Run A) explained the drop from v2 to Pro by target size: about 20x smaller targets, the 0.01 grid and the downscaling. That is only part of it. At the same apparent size, raw Pro is still 20-35 pp below raw v2 (section 4).
- REPORT.md gave the key balance as "$0.2500 billed" for Run A and "$0.4961 billed" for run 2. Those were readings taken while billing still lagged. Billing has settled, and the key now matches the logged cost exactly, plus the 3-case smoke (section 1).
- REPORT.md said the zoom "helps both through the finer grid and through more pixels per target". Still true, but the simpler statement is the right one: zoom makes the target bigger in the image Jev sees, and after zoom a target is hit about as often as a raw target of the same apparent size. On Pro, grid and pixels cannot be separated, since every screenshot is downscaled.

## 11. What it leads to

1. **The zoom number is clean, and it is the one to quote.**
   - 42.76% (95% CI 40.34-45.21), at $0.000319 and 1.7 s per click.
   - It comes from the v2 method, run unchanged; nothing on Pro was used to choose it.
   - Single-shot models next to it on the leaderboard: Phi-Ground 43.2 and GUI-Actor-2.5VL-3B 42.2. Jev uses two calls.
2. **Pro is hard for Jev for two separate reasons.**
   - The targets are tiny: a median of 20.9 px in the image Jev sees, against 92.1 on v2. Zoom fixes this part, and it works by size alone. After zoom, a target is hit about as often as a raw target of the same apparent size (section 4).
   - At the same apparent size, Pro is still 20-35 pp harder than v2: professional apps, dense toolbars, unlabelled icons, Chinese interfaces. Zoom does not touch this part.
3. **The misses are the model, not the answer key.** 67 of B's 905 misses have a label issue, worth at most 2.28 pp. Unlike v2, the labels do not explain the score.
4. **The click-off misses (376) are where more zoom can still pay.**
   - They are mostly boxes too wide over the target and its neighbours, plus near misses. 429 of the 905 are within 15 px.
   - Size fixes them, and the size curve is still climbing at 80-120 px.
   - A 4x step would keep the target in view in 700 of the 905 misses (section 8).
5. **The wrong-element misses (462) need something other than zoom.**
   - 60% of them have no visible text naming the target: unlabelled icons that only someone who knows the app can find.
   - In 151 cases, the first answer already looked in the wrong part of the screen, so no crop around it can help.
   - These need a different first look (the screen in parts, or several candidates) or a model that knows these apps.
6. **Chinese interfaces score lower,** 30.2 vs 45.6 after zoom, with the same gain from zoom (+21.7 vs +24.6 pp). Each of the five apps is entirely Chinese, and six English apps score as low, so this cannot be pinned on the language alone.
7. **Confidence cannot gate on Pro.** AUROC is flat, and 0.8 or more is right only 68% of the time. Even with perfect hindsight, picking between the answers we already have is worth about 5 pp. The headroom is in new looks.
8. **2x zoom has no hidden cost on desktop.** There were 0 context-loss breaks and 0 crop misses. The 55 breaks are mostly edge noise.
9. **Pro has its own label errors, like v2:**
   - 3 cases where the key and the English instruction disagree (#133, #491, #657);
   - 3 pairs with the same request and two different keys;
   - 2 duplicate cases;
   - 30 copied screenshot files;
   - 1 box outside its image;
   - English instructions machine-translated from the Chinese ones.

   A draft upstream report is in `analysis/upstream-issue-pro/`, not posted.

**The open choice (Arthur's, not decided):**
- **(a) Stop at 42.76.** It is clean, cheap and simple, and the article has its Pro number.
- **(b) A 4x second zoom step as a separate, labelled experiment.** The evidence points at it: the size curve, and 700 of 905 targets still in view. But it was designed after seeing Pro run 2's answers, so it is not a clean test. Done honestly, that means:
  - freeze the rule and write down a prediction first;
  - run all 1,581 cases;
  - report it next to 42.76, never in place of it, as "designed after seeing Pro run 2".

  One more stage costs about $0.25, and the key holds $0.295.
