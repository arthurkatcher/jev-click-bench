# Jev 1.14 box on ScreenSpot-v2: run report

Status as of Fri Oct 16 2026, 21:30 CEST. Living document: updated after each run.

## 1. Summary

- Raw Jev 1.14 `box` scores **83.33%** on ScreenSpot-v2 (1060 of 1272, 95% CI 81.2-85.3), first full public run of the real model on this benchmark as far as our research found.
- Text targets are easy (93% on mobile and desktop), icons and web pages are hard (web icon 69%).
- It is fast and nearly free: median 0.89 s per answer, $0.00015 per case, $0.19 for the full benchmark.
- Most misses are close: median 24 px away in the image Jev saw. Almost half are one specific failure: Jev boxes the whole bar or row the target sits in, and the box centre lands beside the target.
- Accuracy depends strongly on how big the target is after resizing to Jev's 1568 px limit. This motivated the next method: a second call on a 2x zoomed crop. It is built, frozen and under review; not run yet.

## 2. What has been done (Oct 16 2026, CEST)

| Time | Step |
|---|---|
| ~18:00-19:57 | Research: Jev in computer use (X, ~30 GitHub repos, web). Gap: no public ScreenSpot run of real Jev 1.14 `box` |
| ~20:00-20:39 | Bench built: client, runner, scoring, offline tests, protocol frozen in README |
| 20:39-20:55 | 3 review rounds (12 agents), every confirmed finding fixed before spending |
| 20:55-21:03 | Pass 1: 20-case start, raw answers read, then the full pass resumed unchanged |
| 21:08 | Error analysis of the 212 misses (analysis/ERRORS-pass1.md) |
| 21:10-21:24 | Zoom method designed from pass 1 (offline replay, no calls), implemented with tests |
| 21:24- | Review workflow of the zoom harness running |

Commits: 0a89357 (bench), fc84df2 and d9596d8 (review fixes, observability), 5266a58 (error analysis), 7b3c2d4 (zoom method).

## 3. Setup

- **Model:** `typesafe/jev-1.14` via OpenRouter `POST /api/alpha/decisions`, header `TypeSafe-Danger-Zone-Images: true`. Resolved id on every case: `typesafe/jev-1.14-20261014`, provider TypeSafe.
- **Data:** OS-Copilot/ScreenSpot-v2, 1272 cases over 730 screenshots. Cells: mobile text 290, mobile icon 211, desktop text 194, desktop icon 140, web text 234, web icon 203.
- **Request:** one screenshot + one `box` question. Wording (v2, frozen before any v2 call): `In the screenshot, the UI element to use for this task: <instruction>`.
- **Image:** scaled so both sides fit 280-1568 px (Jev's limit), no padding. 1034 of 1272 cases are downscaled (median 0.62x among them); 238 are sent at native size.
- **Scoring:** the official ScreenSpot rule (SeeClick, ScreenSpot-Pro code): click = box centre, hit if inside the ground-truth box, edges inclusive, strict float compare. Headline = micro average (hits / 1272), as published v2 tables use.
- **Protocol rules:** no wording or method tuning on test rows; malformed answers count as misses; infrastructure errors are re-run; pass 1 is the headline; pass 2 is reported next to it, never best-of-two.

### Review before spending
Three review rounds, each with independent auditors (scoring, image pipeline, API, methodology) and a skeptic per finding:
- **Round 1 (5 major, 14 minor confirmed).** Malformed answers would have dropped out of the denominator instead of counting as misses. No resume or concurrency. Timeouts and bad 200 bodies were not caught. Dev calls were mixed into the same log as a pass. Plus the definition of "average", quote nesting in the instruction wrapper, and README counts.
- **Round 2 (7 minor).** No resolved-model gate. Float noise on an edge could flip a hit. A provider error body was scored as a model miss. Some transport errors escaped the retry loop.
- **Round 3 (8 minor).** No confidence interval. A truncated log line would crash resume. Out-of-range boxes were mis-scored. Agreement between passes was not computed.

All fixed and covered by offline tests (`tests/test_offline.py`, mocked API, no spend).

## 4. Pass 1 results

| Platform | Type | n | Hits | Acc | 95% CI |
|---|---|---|---|---|---|
| mobile | text | 290 | 269 | 92.76 | 89.2-95.2 |
| mobile | icon | 211 | 175 | 82.94 | 77.3-87.4 |
| desktop | text | 194 | 180 | 92.78 | 88.3-95.7 |
| desktop | icon | 140 | 109 | 77.86 | 70.3-83.9 |
| web | text | 234 | 187 | 79.91 | 74.3-84.5 |
| web | icon | 203 | 140 | 68.97 | 62.3-74.9 |
| **all (micro)** | | 1272 | 1060 | **83.33** | 81.2-85.3 |
| all (macro, mean of 6) | | | | 82.54 | |

Run health: 1272 of 1272 scored, 0 wrong_format, 0 infra errors, 0 retries, 2 degenerate boxes (#821 miss, #1100 hit), 0 centres on an edge, 0 boxes outside the image. The edge-tolerant side metric equals the strict one (0 cases differ).

### Speed, tokens, cost

| Metric | Value |
|---|---|
| Latency per answer | min 0.52 s, median 0.89 s, p90 1.91 s, p99 4.69 s, max 5.89 s |
| Wall time, full pass | 7 min 12 s with 4 workers |
| Input tokens | 4.54M total, mean 3573 per case (min 653, max 6170) |
| Token cost of an image | about 423 + 0.00253 x sent pixels |
| Output tokens | 20 per answer |
| Cost | $0.1909 logged, $0.00015 per case |
| Payload | median 358 KB, max 2.8 MB per request |

| Cell | Median latency | Mean tokens | Cost |
|---|---|---|---|
| mobile text | 0.86 s | 3415 | $0.0416 |
| mobile icon | 0.86 s | 3565 | $0.0316 |
| desktop text | 0.85 s | 3261 | $0.0266 |
| desktop icon | 0.87 s | 3237 | $0.0190 |
| web text | 0.96 s | 3927 | $0.0386 |
| web icon | 0.99 s | 3927 | $0.0335 |

Note: the OpenRouter key balance lags billing by many minutes; the logged cost per response is the reliable number.

### Confidence as a signal
AUROC hit vs miss = 0.655 (weak). Mean confidence 0.68 on hits, 0.55 on misses.

| Confidence | n | Acc |
|---|---|---|
| 0.0-0.5 | 263 | 68.1 |
| 0.5-0.6 | 171 | 84.2 |
| 0.6-0.7 | 226 | 85.4 |
| 0.7-0.8 | 251 | 88.8 |
| 0.8-0.9 | 262 | 87.8 |
| 0.9-1.0 | 99 | 91.9 |

Low confidence is a usable warning (68% vs 86-92% above 0.5), but no threshold makes answers safe.

## 5. What drives accuracy

### Target size in the image Jev saw (square root of area, sent px)

| Size | n | Acc |
|---|---|---|
| under 20 px | 3 | 0.0 |
| 20-30 px | 24 | 54.2 |
| 30-45 px | 118 | 57.6 |
| 45-60 px | 153 | 69.9 |
| 60-80 px | 219 | 87.7 |
| 80-120 px | 284 | 88.0 |
| 120+ px | 471 | 91.3 |

Accuracy climbs steeply up to about 60 px and is flat above it. Downscaled cases score 82.2%, native-size cases 88.2%.

### Screen resolution

| Screenshot | Platform | n | Scale | Acc |
|---|---|---|---|---|
| 2560x1440 | web | 373 | 0.61 | 76.4 |
| 1080x2400 | mobile | 211 | 0.65 | 89.1 |
| 1170x2532 | mobile | 182 | 0.62 | 90.7 |
| 960x540 | desktop | 109 | 1.00 | 87.2 |
| 2360x1640 | mobile (tablet) | 77 | 0.66 | 81.8 |
| 1920x1080 | web | 64 | 0.82 | 65.6 |
| 1280x2774 | mobile | 28 | 0.57 | 89.3 |
| 2560x1440 | desktop | 20 | 0.61 | 75.0 |

Resolution is not the whole story: 1920x1080 web pages are shrunk less than 2560x1440 ones and still score lower. Dense web layouts are hard on their own.

### Source

| Source | n | Acc |
|---|---|---|
| mobile android | 211 | 89.1 |
| mobile ios | 238 | 88.7 |
| mobile shop | 52 | 86.5 |
| desktop macos | 147 | 88.4 |
| desktop windows | 159 | 86.2 |
| desktop shop | 28 | 78.6 |
| web forum | 79 | 81.0 |
| web shop | 165 | 75.8 |
| web gitlab | 73 | 72.6 |
| web tool | 120 | 70.8 |

## 6. Error research (212 misses)

Full list with every miss: `analysis/ERRORS-pass1.md`, `analysis/errors_pass1.csv`.

### How far off
Distance from Jev's click to the nearest edge of the true box, in sent px.

| Cell | Misses | Median dist | 10 px or less | 10-25 | 25-50 | 50-100 | 100-300 | 300+ |
|---|---|---|---|---|---|---|---|---|
| mobile text | 21 | 95 | 3 | 4 | 0 | 4 | 8 | 2 |
| mobile icon | 36 | 228 | 3 | 0 | 4 | 6 | 8 | 15 |
| desktop text | 14 | 15 | 5 | 3 | 5 | 0 | 0 | 1 |
| desktop icon | 31 | 10 | 16 | 6 | 3 | 1 | 3 | 2 |
| web text | 47 | 13 | 22 | 9 | 3 | 5 | 4 | 4 |
| web icon | 63 | 19 | 23 | 14 | 9 | 6 | 9 | 2 |
| **all** | 212 | 24 | 72 | 36 | 24 | 22 | 32 | 26 |

Desktop and web misses are near misses (median 10-19 px). Mobile misses are far: Jev picked a different element.

### Two kinds of miss
- **Too-wide box, 98 of 212 (46%).** Jev's box contains the target's centre but is a median 1.75x wider than the target: it boxes the whole search bar, toolbar or row the icon sits in, so the box centre lands beside the target. Examples: #744 "next page" (target 62x112 px, Jev box 1176x61), #331 "search games" (61x52 vs 649x78), #1095 "search result" (77x66 vs 580x62).
- **Off target, 114 of 212.** The box is about the right size (median 0.94x the target width) but sits a median 40 px away: a neighbouring or wrong element.

### Systematic bias
Misses lean left: 109 of 212 land left of the target (down 42, right 27, up 16, diagonals 18). The mean horizontal offset over all cases is -0.16 target widths, -0.36 on web icons. It mostly comes from the too-wide boxes (an icon at the right end of a bar).

Decision: no bias correction in code. Shifting clicks right after seeing these numbers would be tuning on the test set.

## 7. Zoom method (built, frozen, not run)

### Idea, in three steps
1. Jev boxes the target on the full screenshot (stage A, the raw call).
2. Cut the area around that box from the original screenshot and enlarge it 2x.
3. Jev boxes the target again on the enlarged piece (stage B). That second box is the answer, always: never a pick between the two.

### Rules (frozen in README and code before any zoom call)
- **Window:** half of each side of the screenshot, centred on A's box. It grows to contain A's whole box plus a 10% margin on each side, up to the full screen, and is slid to stay inside the image.
- **Size and cost:** same aspect as the screenshot, resized to A's sent size, so stage B costs the same tokens as stage A.
- **Same request:** same prompt, same question, same scoring after mapping B's box back to the full screenshot.
- **No gate:** stage B runs on every case.

### How the crop was chosen
Offline replay of pass 1, no API calls (`analysis/zoom-replay/`):
- For each crop size, place the window on A's real answer, check whether the true target falls inside it, and predict stage B from the size curve above.
- Each case keeps its pass-1 difficulty: A hits start at 0.97, misses at 0.15, which gives about 5% flips on a plain rerun, the repeat rate others measured.

| Window (share of each side) | Est. acc | Miss targets inside crop |
|---|---|---|
| 1.0 (rerun, no zoom) | 83.7 | 212 / 212 |
| 0.6 | 85.4 | 186 / 212 |
| 0.5 (chosen, 2x) | 86.0 | 183 / 212 |
| 0.4 | 86.7 | 176 / 212 |
| 0.3 | 87.5 | 165 / 212 |

- The estimate keeps rising for tighter crops only because it assumes bigger is always better. Pass 1 shows that stops near 60 px, and below 0.5 the enlargement adds pixels with no new detail while targets start falling out of the crop. 0.5 sits on the flat part and is the round 2x choice.
- Drawing real misses showed that centring the window on A's click cuts the target out of too-wide misses (#744: the "next page" arrow sits at the end of a wide row). Hence the window must contain A's whole box. That keeps 193 of 212 miss targets inside the crop (vs 183 for click-centred) and widens the window in 14% of cases. Estimate unchanged at about 86%.
- Examples: `analysis/zoom-examples/` (miss_*_click.png vs miss_*_box.png, and B_sent_*.png = the exact image stage B would send).

What zoom can and cannot fix:
- **#1095** (too-wide, small target): fixable. At 2x the magnifier is a large blue square next to an empty field.
- **#744**: fixable with the grown window.
- **#331** (title-bar box as wide as the screen): the window is the full screen, so stage B is just a second try. Zoom does not fix a wrong pick.

Disclosure for any write-up: the crop rule was picked from pass 1 misses on the same test set (light selection: one round value on a flat curve, no search against real zoom scores). A clean confirmation would be ScreenSpot-Pro with the same frozen rule.

### Planned run
`python3 screenspot.py run --pass 2 --zoom --workers 4 --max-cost 0.40`
- Stage A is byte-identical to a raw pass and goes to `results/pass2.jsonl`, so it is also pass 2: the rerun stability check.
- Stage B goes to `results/zoom2.jsonl`.
- Report: raw pass 1 (headline), raw pass 2 with pass-1/pass-2 agreement, zoom (A+B) with flips both ways against its own A, cost and latency of A+B vs A, all six cells.
- Expected cost about $0.38, against about $0.44 real credit. The cap of $0.40 stops cleanly, and resume re-runs only the missing stage.

### Live smoke (dev log, not part of any pass)
One live A+B call on #1095, about 21:45: A FALSE (search field boxed, conf 0.36), B FALSE (on the 2x crop Jev boxed the search field again, conf 0.32). Mechanics correct: same image size and tokens as A (3922 vs 3926), box mapped back right. The miss is an interpretation, not blur. No design change from this case. Figure: `analysis/figures/live-zoom-smoke_case_1095.png`.

### Review
- **Round 1:** 3 auditors (crop and mapping maths, runner and data completeness, methodology), one skeptic each. 13 confirmed findings, all minor, none changing a score. Fixed in 1b2e535:
  - live B error counters and stderr lines
  - progress split by stage
  - copied wrong_format records no longer double A's time
  - paired exact McNemar plus identical-answer count in `compare`, and no raw/zoom "mean"
  - model/template check across files
  - zoom config and code revision logged on every B record, mixed configs gated
  - `out_of_crop` separate from `out_of_range`
  - replay archived with its search grid and the registered ~86% prediction
  - resume and balance-lag notes
- Key balance before launch read $0.440.
- **Round 2:** running.

## 8. Budget

| Item | Cost |
|---|---|
| 3 smoke calls (v1 wording, dev log) | ~$0.0005 |
| Pass 1 | $0.1909 |
| Real credit left (per Arthur) | ~$0.44 |
| Pass 2 + zoom (planned) | ~$0.38 |

## 9. Published comparison points (from the research notes, check each paper before public use)

| Model | ScreenSpot-v2 |
|---|---|
| Holo2-235B (H Company) | 95.9 |
| POINTS-GUI-G-8B | 95.7 |
| Holo1.5-72B | 94.4 |
| GUI-Cursor | 93.9 |
| UI-TARS-7B | 91.6 |
| GUI-Eyes-3B | 88.4 |
| **Jev 1.14 raw (this run)** | **83.33** |

OS-Atlas-7B is often cited around 84.1 but is unverified here. Jev is a general decision model, not a grounding specialist, and runs in TypeSafe's long-context mode on OpenRouter for every image request ("slower and less accurate" per TypeSafe).

## 10. Pinned for after the zoom run

- **Label audit of the misses (Arthur, Oct 16).** Some ScreenSpot-v2 instructions fit more than one element (e.g. #1095 "search result": Jev boxes the search field, the key says the magnifier button). v2 is already the OS-Atlas cleanup of v1, but ambiguity is left. Plan: go through the misses (pass 1, pass 2, zoom), mark the ones where the instruction honestly fits another element, report "X of the misses are arguable labels" as a side note. The score always stays the official answer key, never re-scored.
- **Wording ablation, off-benchmark only.** Whether a different wrapper sentence moves Jev toward buttons can only be tested on screenshots outside ScreenSpot-v2.
- **ScreenSpot-Pro** with the same frozen zoom rule, as the clean confirmation of the crop choice.

## 11. Caveats

- One pass so far. Run-to-run variation is unknown until pass 2 (others measured ~5% of identical requests changing their pick).
- 81% of cases are downscaled to fit 1568 px, which hurts small targets. That is a property of the API limit, reported rather than worked around in the raw number.
- Long-context mode is forced for images on OpenRouter; the direct TypeSafe API might score differently.
- `jev-latest` changes around Oct 21. This run is pinned to `jev-1.14`, and the resolved dated id is logged per case.
