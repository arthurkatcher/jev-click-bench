# Deep audit of the three runs (Jev 1.14 box, ScreenSpot-v2)

Oct 16 2026. A1 = pass 1 (raw), A2 = pass 2 (the same raw request again), B = the zoom answer (stage B, built on A2).
Every number below is printed by `python3 analysis/audit_run2.py`. Add `--images` for the image rebuild and `--balance` for the key balance. The integrity checks are asserts: the script stops if any of them fails.

## 1. Integrity: everything checked passed

- **Records.** 1272 lines per file, one per case, all status ok. 0 retries (attempts = 1 on all 3,816 answers), 0 malformed answers, 0 infrastructure errors.
- **Identity.** Every record matches the dataset: screenshot file, instruction, platform, type and key box. The screenshot size in every record matches the image file.
- **Prompt.** All 3,816 requests sent the frozen v2 wording (hash a723751c1725), rebuilt here from the raw instruction.
- **Model.** Every answer resolved to `typesafe/jev-1.14-20261014`, provider TypeSafe.
- **Rescore.** Every raw API answer was parsed again, the click recomputed and the official rule applied again: A1 1060, A2 1073, B 1118 hits, the same as logged.
- **Zoom mechanics.** Every B window was rebuilt from A2's record alone with the frozen rule, and every B box was mapped back to the full screenshot again: all match. B always sends the same image size as A.
- **Images.** All 2,544 sent images were rebuilt (A once, shared by A1 and A2; B from its window). Payload lengths match exactly.
- **Code.** Pass 1 ran at commit d9596d8, run 2 at bb538fc. The stage-A code is identical in both: image fit, PNG encoding, request, API call, parsing, scoring, wording and model constants.
- **Answer format.** Jev answers on a 0.01 grid: every box edge is a multiple of 0.01 of the image. Output is always 20 tokens.
- **Flags.** Degenerate boxes (zero or negative width or height): A1 #821, #1100; A2 #1100, #1161, #1203; B #15. One B click sits exactly on a key edge (#1241). No box outside the screenshot, no B box past its crop.
- **Timeline (UTC, CEST = UTC+2).** Pass 1 ran 18:55:52-19:03:21. It started with cases 0-19, paused 12 s while the raw answers were read, then resumed at case 20 unchanged. Run 2 (A2 + B) ran 19:49:15-20:01:12: 717 s with 4 workers, no pauses.
- **Money.** Every answer was billed at exactly $0.042 per 1M input tokens; output tokens are free. Logged cost: A1 $0.190869, A2 $0.190861, B $0.190867. Run 2 reconciles exactly: the balance before it was $0.439808 (pass2.run.log), minus its logged $0.381729 leaves $0.058079, and the key reads exactly $0.058079 now. The credit left is less than one raw pass ($0.19).
- **Usage outside the bench.** Over the whole day the key shows $0.0022 more usage than the bench logged ($0.575627 vs $0.573455). That is $0.00045 between 19:52 and 20:52 CEST (before pass 1), $0.00002 between pass 1 and run 2, and the rest before the bench existed. No bench call explains it. Every run reconciles, every review script used a dummy key, a blocked proxy or a mocked API, and no command in the session transcripts made an unlogged call. The key is shared with ~/jev-vocab, so the source is outside this repo. No result is affected.

## 2. Accuracy

| Run | Hits | Micro % | 95% CI | Macro % |
|---|---|---|---|---|
| A1 raw | 1060 | 83.33 | 81.19-85.28 | 82.54 |
| A2 raw | 1073 | 84.36 | 82.26-86.25 | 83.53 |
| B zoom | 1118 | 87.89 | 85.99-89.57 | 87.45 |

| Cell | A1 | A2 | B |
|---|---|---|---|
| mobile text | 92.76 | 93.10 | 93.79 |
| mobile icon | 82.94 | 84.36 | 82.46 |
| desktop text | 92.78 | 90.72 | 94.85 |
| desktop icon | 77.86 | 79.29 | 86.43 |
| web text | 79.91 | 83.76 | 89.32 |
| web icon | 68.97 | 69.95 | 77.83 |

| Paired | Miss->hit | Hit->miss | Exact McNemar p | Bootstrap 95% CI, pp |
|---|---|---|---|---|
| A1 -> A2 (rerun) | 31 | 18 | 0.085 | -0.08 to +2.12 |
| A2 -> B (zoom vs its own A) | 95 | 50 | 0.00023 | +1.73 to +5.42 |
| A1 -> B | 107 | 49 | 0.0000039 | +2.67 to +6.45 |

B against the mean of the two raw runs: +4.05 pp (95% CI +2.28 to +5.86).

| A1, A2, B | Cases |
|---|---|
| hit, hit, hit | 1001 |
| miss, miss, miss | 96 |
| miss, miss, hit | 85 |
| hit, hit, miss | 41 |
| miss, hit, hit | 22 |
| hit, miss, hit | 10 |
| miss, hit, miss | 9 |
| hit, miss, miss | 8 |

Of the 181 cases both raw runs missed, zoom fixed 85 (47%). Of the 1,042 both got right, it broke 41 (3.9%).

## 3. How noisy is a rerun

- Same request twice: the box is identical in 383 of 1272 cases, box and confidence together in 55. Jev is not deterministic.
- The click barely moves, though: a median 4.8 px in the image Jev saw. The two boxes overlap by IoU 0.5 or more in 94.2% of cases, and 22 cases switch to another element (IoU under 0.1).
- The 49 cases that flip between hit and miss: in 32 of them the miss sits within 15 px of the target (edge cases), and 11 switch element.
- Confidence repeats closely between the raw passes (correlation 0.971) but not after zoom (0.583 between A2 and B), since B judges a different image.
- Input tokens differ by -9 to +8 on identical requests. Cost effect: none worth counting.

## 4. Why zoom helps

| Target size in A's image | n | A2 % | B % | Delta pp | Fixed | Broken | p |
|---|---|---|---|---|---|---|---|
| under 30 px | 27 | 48.15 | 70.37 | +22.2 | 7 | 1 | 0.07 |
| 30-45 px | 118 | 60.17 | 72.88 | +12.7 | 24 | 9 | 0.014 |
| 45-60 px | 153 | 72.55 | 81.05 | +8.5 | 24 | 11 | 0.041 |
| 60-80 px | 219 | 87.21 | 87.67 | +0.5 | 12 | 11 | 1 |
| 80-120 px | 284 | 88.73 | 90.49 | +1.8 | 15 | 10 | 0.42 |
| 120 px and up | 471 | 92.36 | 93.42 | +1.1 | 13 | 8 | 0.38 |
| **under 60 px** | 298 | 65.44 | 76.85 | **+11.4** | 55 | 21 | 0.00012 |
| **60 px and up** | 974 | 90.14 | 91.27 | **+1.1** | 40 | 29 | 0.23 |

- **It is not only lost pixels.** Where A is sent at native size and B can only upsample, zoom still gains +3.8 pp (n=238). On the 960x540 desktop screenshots it goes 86.2 -> 93.6 (n=109). So the gain comes from the target being bigger relative to the image and from Jev's 0.01 answer grid getting finer on the crop, not only from pixels recovered after the 1568 px limit.
- **Precision.** On the 1,023 cases both answers hit, B's click is a median 11.8 px from the target centre vs 18.8 px for A2. Boxes more than 1.5x the target's width drop from 8.8% to 4.6% of answers, and too-wide misses from 78 to 52.
- **Which A2 misses get fixed:**

| A2 miss | n | Fixed by B |
|---|---|---|
| too-wide box (holds the target centre) | 78 | 43 (55%) |
| off target, 25 px or less | 40 | 34 (85%) |
| off target, 25-100 px | 33 | 16 (48%) |
| off target, over 100 px | 48 | 2 (4%) |
| target not visible in the zoom window (any kind, overlaps the rows above) | 21 | 0 |

- **Where:** mobile -0.4 pp (17 fixed, 19 broken), desktop +5.4 (29/11), web +6.6 (49/20). By source, GitLab +16.4 (13/1, p=0.0018) and desktop Windows +6.9 (14/3, p=0.013) gain most; the mobile sources are flat.
- **A2 confidence under 0.3:** +13.2 pp (n=68, 12/3). Above 0.3 the gain is +1 to +4 pp.

## 5. What zoom costs: the 50 breaks (A2 hit, B miss)

All 50 were viewed (`analysis/label-audit/sheets/zoom_breaks_*.jpg`).

| Kind | Breaks | Mobile | Desktop | Web |
|---|---|---|---|---|
| Precision: right element, click just off | 21 | 6 | 8 | 7 |
| Context loss: the crop cut the naming label | 14 | 9 | 0 | 5 |
| Neighbour pick | 12 | 3 | 2 | 7 |
| Garbage answer (#15 degenerate, #673 conf 0.09) | 2 | 1 | 1 | 0 |
| Ambiguous label (#972) | 1 | 0 | 0 | 1 |

- **Context loss is the real design cost.** On mobile settings screens the label sits on the left and the toggle on the right. A half-width crop around the toggle cuts the label, and Jev then picks the toggle of the row next to it (#46, #49, #57, #58, #136, #307, #311, #346, #484). On web: #1027 cut the entered query, #1032 cut the first news item so "the third" was counted from the second, #1185 changed the reading order, #1212 cut the repo names, #988 cut the "140".
- Mobile has 19 breaks against 17 fixes, which is why it stays flat. A crop that keeps whole rows on tall mobile screens is an idea for a separate test set, not something to tune here.
- B's confidence dropped in 32 of the 50 breaks. It rose in 50 of the 95 fixes.
- All 21 precision breaks are within max(25 px, half the target's short side) or too-wide; median 9 px off.

**Replay vs reality.** The prediction registered before the run was 48 fixed, 17.5 broken, 85.8%. Actual: 95 fixed, 50 broken, 87.89%. The size-only replay missed both the precision gain and the context-loss cost.

**What is left: B's 154 misses.** All three runs miss 96 of them. In 21 the target is outside the zoom window, so B cannot fix them by design. 80 are more than 100 px away (a different element), and 52 are too-wide boxes. The label audit (`analysis/LABELS-audit.md`) finds a label issue in 35 of the 154.

## 6. Confidence and agreement

- AUROC (how well confidence separates hits from misses): A1 0.655, A2 0.651, B 0.758. B minus A2: +0.107, 95% CI +0.053 to +0.160.

| Confidence | B cases | B right % | A2 cases | A2 right % |
|---|---|---|---|---|
| 0.5 or more | 972 (76.4%) | 93.0 | 1004 (78.9%) | 88.45 |
| 0.7 or more | 681 (53.5%) | 94.27 | 640 (50.3%) | 89.53 |
| 0.8 or more | 419 (32.9%) | 96.42 | 356 (28.0%) | 89.04 |
| 0.9 or more | 150 (11.8%) | 98.67 | 104 (8.2%) | 93.27 |

- **Agreement as a signal.** A2 and B agree on 995 cases (each click inside the other's box), and B is right on 92.1% of those. They disagree on 277: B right 72.9%, A2 right 57.0%.
- **Post-hoc selectors, not the protocol.** Taking the higher-confidence of A2 and B gives 86.95%, below always-B (87.89%), which supports the no-gate design. Oracle A2 or B: 91.82%. Oracle any of the three: 92.45%. Zoom only on desktop and web: 88.05%.

## 7. Cost and speed

- Tokens = 423 + 0.002529 x sent pixels: about one token per 20x20 px patch plus a fixed 423.
- Input tokens per run: A1 4,544,508, A2 4,544,315, B 4,544,459.
- Per click: A $0.000150, A+B $0.000300 ($0.30 per 1,000 clicks).
- Latency, median (p90): A1 0.894 s (1.896), A2 0.841 s (1.434), B 0.789 s (1.267). A+B per click 1.665 s (2.740).

## 8. Corrections to earlier statements

- "Zoom helps small icons shrunk by the 1568 px limit" is only part of it: the gain also appears at native size (section 4).
- "Every case has a true box on the screen" is wrong for 4 cases (`analysis/LABELS-audit.md`).
- The design examples in REPORT.md section 7 called #744 and #1095 fixable. In the real run both stayed misses. On #744, A2 again boxed the whole row, so the window grew to 0.90 of the screen. #1095 is an interpretation miss, as in the smoke test.
