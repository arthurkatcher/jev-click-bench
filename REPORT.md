# Jev 1.14 box on ScreenSpot-v2 and ScreenSpot-Pro: run report

Status as of Sat Oct 17 2026, 11:10 CEST. Living document: updated after each run.

## 1. Summary

- Raw Jev 1.14 `box` scores **83.33%** on ScreenSpot-v2 (1060 of 1272, 95% CI 81.2-85.3), first full public run of the real model on this benchmark as far as our research found.
- Text targets are easy (93% on mobile and desktop), icons and web pages are hard (web icon 69%).
- It is fast and nearly free: median 0.89 s per answer, $0.00015 per case, $0.19 for the full benchmark.
- Most misses are close: median 24 px away in the image Jev saw. Almost half are one specific failure: Jev boxes the whole bar or row the target sits in, and the box centre lands beside the target.
- Accuracy depends strongly on how big the target is in the image Jev sees. That motivated the zoom method, a second call on a 2x crop around the first answer: **87.89%**, +3.54 pp over its own raw answer (p=0.0002). See 1b.
- Deep audit (1c): every answer rescored from the raw API response, every sent image rebuilt, logs and billing reconciled. No number changed.
- Label audit (1d): of the 271 cases any run missed, 4 have a wrong answer key and 39 more sit on ambiguous or loose instructions. Side note only: the score stays the official key.
- Oct 17 (1e): the label errors are reported upstream (OS-Atlas issue #65), both leaderboards are collected, and the headroom analysis says a better v2 number would be tuned on the test set.
- **ScreenSpot-Pro (1e, Oct 17):** raw Jev scores **19.17%** (pass 1; pass 2 18.66%, same within noise). The same frozen 2x zoom, fixed before any Pro call, lifts it to **42.76%**: +24.10 pp over its own raw answer (436 fixed, 55 broken, p = 1.2e-74), about 7x the v2 gain. Pro targets are about 20x smaller than v2's, so zoom matters far more. Cost $0.00032 per task with zoom.
- **Pro deep audit and label audit (1f, Oct 17):**
  - Every Pro number checks out. Zoom works by size alone: after zoom, a target is hit about as often as a raw target of the same apparent size.
  - At the same size, Pro is still 20-35 pp harder than v2.
  - The misses are the model, not the key: 67 of the 905 zoom misses have a label issue, worth at most 2.28 pp. The rest are the wrong element (462) or the right element with the click off (376).
  - Pro has its own broken tasks: 3 where the key and the English instruction disagree, 3 pairs with the same request and two different keys, and 2 duplicates. An upstream report is drafted, not posted.

## 1b. Pass 2 + zoom (run 21:49-22:01 CEST, 0 errors, $0.3817 logged)

**Q1. Is A1 different from A2? No, within noise.** Pass 1 83.33%, pass 2 84.36% (CI 82.3-86.2), mean 83.84 +- 0.51. 1223 of 1272 cases agree (96.1%): 31 miss->hit, 18 hit->miss, exact McNemar p = 0.085 (not significant). Jev is not deterministic: only 383 of 1272 boxes are identical and 55 of 1272 box+confidence, but the box stays on the same element. Rerun noise floor: 3.9% of cases flip.

**Q2. Is A+B better than A? Yes, clearly.** Zoom 87.89% (CI 86.0-89.6) vs its own A 84.36%: +3.54 pp, paired 95% bootstrap CI +1.73 to +5.42, 95 miss->hit vs 50 hit->miss, exact McNemar p = 0.00023. Beat the registered prediction (85.8%).

| Cell | raw A | zoom A+B | delta pp | miss->hit | hit->miss | McNemar p |
|---|---|---|---|---|---|---|
| all | 84.36 | 87.89 | +3.54 | 95 | 50 | 0.00023 |
| mobile text | 93.10 | 93.79 | +0.69 | 7 | 5 | 0.77 |
| mobile icon | 84.36 | 82.46 | -1.90 | 10 | 14 | 0.54 |
| desktop text | 90.72 | 94.85 | +4.12 | 12 | 4 | 0.077 |
| desktop icon | 79.29 | 86.43 | +7.14 | 17 | 7 | 0.064 |
| web text | 83.76 | 89.32 | +5.56 | 21 | 8 | 0.024 |
| web icon | 69.95 | 77.83 | +7.88 | 28 | 12 | 0.017 |

| Window group | n | raw A | zoom A+B | delta pp |
|---|---|---|---|---|
| half (2x zoom) | 1108 | 83.84 | 87.36 | +3.52 |
| widened to hold A's box | 75 | 80.00 | 86.67 | +6.67 |
| full screen (same image re-asked) | 89 | 94.38 | 95.51 | +1.12 (1 flip) |
| A at native size (B upsample only) | 238 | 87.39 | 91.18 | +3.78 |
| A downscaled (B recovers pixels) | 1034 | 83.66 | 87.14 | +3.48 |

| Platform | n | raw A1 | raw A2 | zoom A+B | delta vs A2 | miss->hit | hit->miss | McNemar p | bootstrap CI |
|---|---|---|---|---|---|---|---|---|---|
| desktop + web | 771 | 79.90 | 81.06 | 87.16 | +6.10 | 78 | 31 | 0.0000077 | +3.4 to +8.7 |
| desktop | 334 | 86.53 | 85.93 | 91.32 | +5.39 | 29 | 11 | 0.0064 | +1.8 to +9.0 |
| web | 437 | 74.83 | 77.35 | 83.98 | +6.64 | 49 | 20 | 0.00064 | +3.0 to +10.3 |
| mobile | 501 | 88.62 | 89.42 | 89.02 | -0.40 | 17 | 19 | 0.87 | -2.8 to +2.0 |

The platform split is read after the run, but the reason (small targets shrunk by the 1568 px cap) was written down before it. Harness rule it suggests: zoom on desktop and web, skip it on mobile (saves the second call on ~40% of cases).

- Zoom helps where predicted: desktop, web and small targets. The gain also shows at native size, so it comes from the target's size relative to the image, not only from pixels lost to the 1568 px cap (1c). It does nothing on mobile: the fixes there are cancelled by crops that cut the row label.
- The cost is 50 cases that A had right and B broke, vs 95 fixed. Zoom flips 11.4% of cases against 3.9% for a plain rerun, so the change is real, not noise.
- Confidence gets much more useful after zoom: AUROC 0.651 (A) -> 0.758 (B), and B answers at confidence >= 0.9 are right 98.7% of the time (150 cases).
- Cost and speed: exactly 2x tokens (4.54M + 4.54M), $0.19 + $0.19, median latency 0.84 s -> 1.67 s per case (A then B).
- Key balance re-read at 22:57: $0.058079, exactly the balance before the run minus the logged $0.381729 (the $0.370 read right after the run was lag). Credit left is below one raw pass.

## 1c. Deep audit of all three runs

Full write-up: `analysis/AUDIT-run2.md`. Every number there comes from `python3 analysis/audit_run2.py`.

- **Integrity: all checks passed.** Records, identity, frozen wording and resolved model all check out, with 0 retries and 0 errors. Every answer was re-parsed and rescored (1060 / 1073 / 1118, as logged). Every zoom window and mapping was rebuilt from A2, and all 2,544 sent images were rebuilt with exact payload lengths. The stage-A code is identical in both runs (d9596d8 vs bb538fc), and run 2's billing matches its logs exactly.
- **Rerun noise.** The same request twice gives an identical box in only 383 of 1272 cases. But the click moves a median 4.8 px, and 32 of the 49 flips are edge cases.
- **Why zoom helps.** Targets under 60 px in A's image gain +11.4 pp (p=0.0001); 60 px and up gain +1.1 (not significant). Native-size screenshots gain too (+3.8 pp; 960x540 desktop 86.2 -> 93.6). So the cause is relative size and a finer answer grid, not only lost pixels. Clicks also get tighter: a median 11.8 vs 18.8 px from the target centre on shared hits.
- **What zoom costs.** Of the 50 breaks: 21 precision slips, 14 context loss (the crop cut the label that names the target, 9 of them on mobile settings rows), 12 neighbour picks, 2 garbage answers and 1 ambiguous label.
- **Confidence.** B at 0.9 or more is right 98.7% of the time (150 cases), and A2 and B agreeing is right 92.1% (995 cases). Taking the more confident of A2 and B (86.95%) is worse than always taking B, which backs the no-gate design.
- **Against the mean of both raw runs,** zoom is +4.05 pp (CI +2.28 to +5.86).

## 1d. Label audit of the misses (side note: the score stays the official key)

Full write-up: `analysis/LABELS-audit.md`. The per-case verdicts are in `analysis/label-audit/`, and the counts come from `python3 analysis/labels_audit.py`. All 271 cases missed by at least one run were viewed with all three answers drawn.

| Group | Cases | A1 misses | A2 misses | B misses |
|---|---|---|---|---|
| Answer-key error | 4 | 4 | 4 | 4 |
| Two valid answers | 18 | 18 | 16 | 14 |
| Same control, key covers part of it | 12 | 12 | 11 | 8 |
| Loose wording, key still the best | 8 | 8 | 7 | 8 |
| Cannot verify | 1 | 1 | 1 | 1 |
| **Label issues, total** | **43** | **43** | **39** | **35** |
| Label-fine (model errors) | 228 | 169 | 160 | 119 |

- **Key errors.** #458's key box is copied from another screenshot and sits on empty space; #487, #1035 and #1037 mark the wrong element. A corrected key would add 2 hits to A1 and A2 and 3 to B (0.16-0.24 pp). Not applied.
- Jev reads the label-issue cases the same way every time: all three runs miss 32 of the 43.
- The dataset scans found one duplicate test case (#1017 = #1021) and one key box 1 px past the image edge (#449, hit by all runs).

## 1e. Oct 17: headroom, leaderboards, upstream report

### Can the harness go higher on v2?
From `python3 analysis/headroom.py` (post-hoc, offline, no calls):

| Selector on the three v2 runs | Acc % |
|---|---|
| always B (the protocol) | 87.89 |
| majority vote of A1, A2 and B | 84.91 |
| skip zoom on mobile | 88.05 |
| oracle A1 or A2 | 85.77 |
| oracle any of the three | 92.45 |

- **More samples of the same view hurt.** The two raw runs share the same mistakes and outvote B when B is right (where A1 sides with A2 against B, B is right 162 times and A2 124).
- **Bigger pixels are used up.** After zoom only 28 targets are under 60 px in the image B saw. The rest of B's misses are 69 wrong element, 36 right element with the click off, 35 label issues and 14 crop context losses.
- **Realistic v3 on v2: about 88.5-89.5%**, from a mobile crop fix plus a tighter click. Every idea comes from v2's test answers, so any such v2 number is tuned and must be labelled as such. The clean next step is ScreenSpot-Pro.

### Leaderboards (`analysis/leaderboard/`)
- **ScreenSpot-v2** (`screenspot-v2.md`, 39 rows): leader MAI-UI-32B 96.5 (Microsoft, Dec 2025), then OmegaUse-G 96.3 and UI-Venus-1.5-30B 96.2. VISTA (Jun 2026) calls v2 near saturation. Frontier labs stopped reporting it: the newest are Claude Sonnet 4 93.0 (H Company's run) and Gemini 3 Pro 93.7 (cited only). Jev raw 83.33 sits between Phi-Ground 83.8 and OS-Atlas-7B 84.1; Jev zoom 87.89 with OpenAI CUA 87.9, UGround-v1-7B 87.7 and Claude 3.7 Sonnet 87.6.
- **ScreenSpot-Pro** (`screenspot-pro.md`, 95 rows, plus the official leaderboard data): no-tools leader GPT-6 Astra 92.7 (OpenAI; XPeng re-ran it at 93.17), then Claude Mythos 5 87.3 and Opus 4.8 82.3. With tools (Python or crop): Claude Mythos Preview 93.0, Mythos 5 90.7, Opus 4.8 87.9, GPT-5.2 86.3. Best open models: Qwen-UI-Agent-27B 76.6 single-shot, GroundCascade 85.1 with zoom. Aggregators mix the two setups in one column, so charts must split them.
- Self-reported scores often disagree with third-party runs (GPT-5.6 Sol 76.9 vs 81.3; Opus 4.6 57.7 vs 49.5; Qwen3-VL-32B on v2 93.0 vs 95.8). Charts mark who measured each number.

### How the leaders' techniques compare to our zoom
- **Same idea as ours ("zoom-in"):** MAI-UI, Qwen3.7-Plus, Qwen-UI-Agent and Indeed-UI guess, crop around the guess, enlarge and guess again. GroundCascade uses the same 0.5 window (2x). Their gains: MAI-UI-32B 67.9 -> 73.5, Qwen3.7-Plus 68.9 -> 79.0. Our method is the standard one; the gap is mostly the model.
- **Beyond ours (1): the model drives the zoom.** "Python tools" (Claude Mythos, Opus 4.8, GPT-5.2, Muse Spark): the model gets a crop tool, picks where and how much to zoom, and can repeat with thinking in between. Smarter, but many calls and thinking tokens per answer.
- **Beyond ours (2): more looks plus a vote or a combination.** GroundCascade combines 2 models over ~2.6 calls per case, MAI-UI MVP votes over several crops (77.5), Holo2 agentic takes 3 steps (78.5).
- Jev has no tools (one box question per call), but a harness can imitate both tricks (repeated zoom steps, multi-crop vote). Possible later arms, each declared before a run. Setups come from the research agent's labels; the exact recipes in each paper were not read.
- Holo family (addenda in `analysis/leaderboard/`): Holo3-122B 72.2, Holo3.1-35B 71.5 and Holo3-35B 67.6 on Pro (no v2 number); Holo4 publishes no ScreenSpot number. H Company's own run of Claude Sonnet 4: v2 93.0, Pro 19.1.

### Upstream report
- Posted Oct 17 08:30 CEST: https://github.com/OS-Copilot/OS-Atlas/issues/65 ("ScreenSpot-v2: 4 wrong answer boxes and 1 duplicate case"). Draft, figures and script in `analysis/upstream-issue/`; figures hosted in a gist. Jev is not named in it. The HF discussion draft (`HF-DISCUSSION.md`) is not posted.
- No earlier report anywhere (`PRIOR-REPORTS.md`): all OS-Atlas and SeeClick issues and PRs, the HF discussions, v2 mirrors, web search.
- **New finding:** web [200] (#1035, "log in by x account") and web [202] (#1037, "check the weather news") were right in ScreenSpot v1 and broke in v2. Only 9 boxes changed between v1 and v2 for the same image and instruction. #455, #458, #487 and #449 are new in v2, and so is the duplicate.

### ScreenSpot-Pro run (frozen Oct 17 08:50, run Oct 17 09:24-09:54)
- Data: likaixin/ScreenSpot-Pro at revision 210e78d (Mar 18 2026), in `data/screenspot-pro/`. 1,581 cases, 26 apps, 6 groups, text 977 / icon 604, bbox = [x1, y1, x2, y2] (v2 is [x, y, w, h]). Scoring = the official `eval_sample_positive_gt`, overall = micro accuracy over all cases. Setting = the official leaderboard one: English instruction, positive cases only.
- Method: the v2 harness unchanged (Arthur, Oct 17: keep it simple). **Zoom: 2x alone (Arthur, Oct 17), the same frozen rule as v2.** No 3x arm. Nothing on Pro is looked at to pick settings.
- Download complete: all 1,618 files (the 62 with spaces in the name re-fetched URL-encoded). Preflight (`screenspot.py --bench pro check`, offline): every image present, every size equal to the annotation's img_size, every box with a positive area. One label quirk: #491's box starts at y = -1 (scored as given, like v2's #449, which runs 1 px past the edge).
- Every Pro screenshot is downscaled to fit Jev's 1568 px limit: 4K goes to 0.41x, 5K to 0.31x, the 6016 px ones to 0.26x. So zoom recovers more pixels here than on v2 (a 4K half-window is sent at 0.82x).
- Harness change = loading only (`use("pro")`, `load_pro()`): Pro's [x1, y1, x2, y2] is stored as [x, y, w, h], so the scoring path is the v2 one. `tests/test_pro_offline.py` checks our truth box equals the official conversion on all 1,581 cases and runs mocked raw + zoom calls through the official rule. Results go to `results/pro/`.
- Smoke (pass 0, 3 cases raw + zoom, plumbing only, not part of any score): all 6 calls ok, 3,931 input tokens per call, $0.00099 total, zoom crops mapped back correctly (checked on the annotated image of #1).
- Wider smoke (Oct 17 ~09:05, own files `results/pro/smoke_sizes_a/b.jsonl`, not a score): one case per screen size (14 sizes), raw + zoom, 28 calls all ok, $0.0046, no B box past its crop. Ultra-wide #80 (3840x1080) checked on its annotated image.
- Review, 2 rounds (Oct 17, workflow of 4 reviewers + 4 adversarial verifiers each, offline, no API spend). Round 1 on 01ec94a: scoring, zoom geometry and data all clean (mocked run of all 1,581 cases gives 0 differences vs the official scorer; every file's sha256 matches the pinned revision; zoom code byte-identical to v2). 2 minor findings confirmed and fixed in e2118e7: an unknown `--bench` value fell back to v2 paths (could rewrite a v2 progress file), and `code_rev` had no dirty flag and was missing on raw records. Round 2 on e2118e7: 0 confirmed findings, 3 rejected as out of scope; one of them (use("v2") after use("pro") did not reset paths) hardened anyway with a test.
- Cost: about 6.0M input tokens = $0.25 per stage, raw + zoom = $0.51 (confirmed by v2 billing at the same sent sizes).

### ScreenSpot-Pro Run A: raw, no zoom (Oct 17 09:24-09:33, `results/pro/pass1.jsonl`, log `pass1.log`)
- **Raw Jev 1.14 box on ScreenSpot-Pro: 19.17% (303/1581, Wilson 95% CI 17.3-21.2).** Text 26.10% (n=977), icon 7.95% (n=604), macro over the 12 cells 17.66%.
- Clean run: 1581/1581 scored, 0 wrong_format, 0 infra_error, 0 retries, all records code_rev 4099bfa on a clean tree, one model version (jev-1.14-20261014). Independent re-score from the raw responses with a verbatim copy of the official `eval_sample_positive_gt`: 303/1581, 0 disagreements.
- Cost and speed: 6.01M input tokens (mean 3,800 per case), $0.2523 logged (the "$0.2500 billed" first written here was a reading taken while billing still lagged; the settled key matches the logs exactly, 1f). Median 0.83 s per answer, p90 1.36 s, 8 min 54 s wall time on 4 workers.

| Group | Text | Icon |
|---|---|---|
| CAD | 12.69 (n=197) | 15.62 (n=64) |
| Dev | 27.92 (n=154) | 7.59 (n=145) |
| Creative | 20.20 (n=198) | 5.59 (n=143) |
| Scientific | 38.89 (n=144) | 7.27 (n=110) |
| Office | 41.81 (n=177) | 15.09 (n=53) |
| OS | 15.89 (n=107) | 3.37 (n=89) |

- Where it sits (official leaderboard data): between OS-Atlas-7B 18.9 and Aguvis-7B 22.9, above GPT5-minimal (resized) 18.5 and Claude (Computer Use) 17.1.
- Why it is so much lower than v2 (83.33): the median Pro target covers 0.035% of the screen vs 0.72% on v2, about 20x smaller. Jev answers on a 0.01 grid, and 562 of 1,581 Pro targets (36%) are smaller than one grid step on at least one side (v2: 1 of 1,272). Every screenshot is also sent downscaled (0.41x for 4K, down to 0.26x). Icons suffer most (7.95%). Correction from the deep audit (1f): size is only part of it. At the same apparent target size, raw Pro is still 20-35 pp below raw v2.
- Confidence still carries signal: AUROC 0.76; answers at 0.8 or more are right 46-50% of the time, under 0.5 only 6.7%.
### ScreenSpot-Pro run 2: raw A2 + frozen 2x zoom B (Oct 17 09:36-09:54, `results/pro/pass2.jsonl` + `zoom2.jsonl`, log `pass2.log`)
Same protocol as v2's run 2: a fresh raw pass (A2) and the zoom stage (B) on A2's own answers, in one run. Command: `python3 screenspot.py --bench pro run --pass 2 --zoom --workers 4 --max-cost 0.60`.

- **Zoom (A2+B) on ScreenSpot-Pro: 42.76% (676/1581, Wilson 95% CI 40.3-45.2)**, vs its own raw answer A2 18.66% (295/1581, CI 16.8-20.7): **+24.10 pp**, paired 95% bootstrap CI +21.63 to +26.63, 436 miss->hit vs 55 hit->miss, exact McNemar p = 1.2e-74. Text 57.01%, icon 19.70%, macro over 12 cells 39.23%.
- On v2 the same frozen rule gave +3.54 pp. On Pro it gives about 7x that, as expected from the target sizes (below): Pro is the benchmark where zoom matters.
- **Q1. Is A1 different from A2? No, within noise.** A1 19.17%, A2 18.66%, mean 18.91 +- 0.25, exact McNemar p = 0.55. 1445 of 1581 cases agree (91.4%), 64 miss->hit, 72 hit->miss; identical box in 302 of 1581. Rerun noise: 8.6% of cases flip vs 31.1% flipped by zoom.
- Clean run: 3,162 calls, all ok (0 wrong_format, 0 infra_error, 0 retries), one model version, code_rev 3cc1088 on a clean tree. Every B window recomputes exactly from A2's box with the frozen rule (0 mismatches), every B image was sent at A2's size. Independent official re-score from the raw responses (B mapped back through its window): A2 295, B 676, 0 disagreements with the recorded hits.
- Cost and speed: 6.01M + 6.01M input tokens (B = exactly A's tokens), $0.5047 logged (the "$0.4961 billed" first written here was a lagging balance reading; the settled key matches the logs exactly, 1f). Median per case: A 0.89 s, A+B 1.72 s (p90 2.60 s). 17 min 31 s wall time on 4 workers. About $0.00032 per task with zoom.

| Group | Text: A2 -> B | Icon: A2 -> B |
|---|---|---|
| CAD | 12.69 -> 44.67 | 14.06 -> 18.75 |
| Dev | 30.52 -> 64.29 | 6.90 -> 19.31 |
| Creative | 19.70 -> 52.53 | 2.80 -> 13.99 |
| Scientific | 36.81 -> 64.58 | 6.36 -> 24.55 |
| Office | 41.24 -> 66.10 | 13.21 -> 33.96 |
| OS | 17.76 -> 52.34 | 2.25 -> 15.73 |

- Every cell gains; all but CAD icon (+4.7, p=0.58) are significant. Text gains +25 to +35 pp per group, icons +5 to +21.
- Window types: 1534 half (true 2x), 23 widened for a big A box, 24 full screen (A's box was so big the rule re-asks the same image: 0 flips there).
- **Declared diagnostics of the frozen 2x zoom** (reported only; nothing here changes a setting or a score):
  - Ceiling: when A2 missed (1286), the target was inside B's window 88.3% of the time (1135). B fixed 436 of those (38.4%). The other 151 misses had the target outside the window, which B cannot fix by construction (0 fixed). B kept 240 of A2's 295 hits.
  - Grid: targets smaller than one 0.01 answer step on a side drop from 562 in A's view to 83 in B's view. Those 562 go from 5.0% (A2) to 16.9% (B); the rest go from 26.2% to 57.0%. So the zoom helps both through the finer grid and through more pixels per target. The simpler statement, from the deep audit (1f): zoom makes the target bigger in the image Jev sees, and on Pro grid and pixels cannot be separated, since every screenshot is downscaled.
- Confidence after zoom: AUROC 0.756; answers at 0.8 or more right 68% of the time (n=407), under 0.5 13.5% (n=445).
- Where it sits (official leaderboard data and `analysis/leaderboard/screenspot-pro.md`): next to Phi-Ground 43.2 and GUI-Actor-2.5VL-3B 42.2 (both single-shot), below Claude Opus 4.5 45.7 (method not stated), above UI-TARS-72B 38.1 and Claude Sonnet 4.5 36.2. Caveat for any chart: Jev zoom is 2 calls per task, those entries 1. Parallel from the ScreenSpot-Pro paper: its search wrapper took OS-Atlas-7B from 18.9 to 48.1.
- Cost context (`analysis/leaderboard/cost-latency.md`, collected Oct 17 by a research agent; estimates, not measurements): no leaderboard entry publishes cost or tokens per task. On image tokens alone, before any thinking, a 4K Pro screenshot costs about $0.0011 (Gemini 3 Flash) to $0.03-0.10 (GPT-6 Astra) per call vs Jev's $0.00016. The agent also flagged newer v2 rows above MAI-UI-32B (GPT-6 Astra 97.88 in a third-party re-run, Qwen-UI-Agent-27B 97.5): not yet verified by hand, so section 9 is unchanged for now.

## 1f. ScreenSpot-Pro: deep audit and label audit (Oct 17)

Full write-ups:
- `analysis/AUDIT-pro-run2.md`: every number comes from `python3 analysis/audit_pro_run2.py`.
- `analysis/LABELS-audit-pro.md`: counts from `python3 analysis/labels_audit_pro.py`, per-case verdicts in `analysis/label-audit-pro/`.

The structure is the same as the v2 audit (1c, 1d).

**Deep audit:**
- **Integrity: all checks passed.**
  - Every answer was re-parsed and rescored with a verbatim copy of the official scorer: A1 303, A2 295, B 676, as logged.
  - Every zoom window and mapping was rebuilt from A2, and all 3,162 sent images were rebuilt with exact payload lengths.
  - The stage-A and zoom code is identical in both Pro runs and in v2's run 2.
  - The key balance now matches the logged cost exactly, $0.757008 plus a $0.000495 smoke. The earlier "billed" figures were lagging readings.
- **Rerun noise is higher than on v2:** 8.6% of cases flip between two identical raw passes (v2: 3.9%). They are mostly edge cases on tiny targets.
- **Why zoom helps: size alone.**
  - After zoom, a target is hit about as often as a raw target of the same apparent size. The crop neither costs context nor adds anything beyond the size it buys, and the curve is still climbing at 80-120 px.
  - At the same apparent size, Pro is 20-35 pp harder than v2: professional apps, dense toolbars, unlabelled icons, Chinese interfaces.
- **What zoom costs:** the 55 breaks are 34 precision slips (median 2.4 px off), 14 neighbour picks, 5 far wrong elements, 1 ambiguous label and 1 answer-key error. Context loss: 0 (v2: 14).
- **Confidence does not gate on Pro.** AUROC is flat (0.765 -> 0.756), and B at 0.8 or more is right only 68% (v2: 96.4%). Picking between the answers we already have is worth about 5 pp even with perfect hindsight.

**Label audit (side note: the score stays the official key).** All 905 of B's misses were viewed by eye, 14 reviewer agents plus a quality pass and a 30-case spot-check.

| Group | B misses |
|---|---|
| Answer key and instruction disagree | 3 |
| Two valid answers | 24 |
| Same control, key covers part of it | 18 |
| Loose or broken wording, key still the best | 18 |
| Same request, two different keys | 4 |
| **Label issues, total** | **67** |
| Wrong element (model error) | 462 |
| Right element, click off | 376 |
| Zoom crop cut the naming label | 0 |

- **The misses are the model.** 67 of 905 (7.4%, v2: 23%) have a label issue. Even scored in Jev's favour, they are worth at most 36 hits, 2.28 pp.
- **Wrong element (462).** 60% of these have no visible text naming the target. In 151 misses the first answer already looked in the wrong part of the screen, so no crop could help.
- **Click off (376).** Mostly boxes too wide over the target and its neighbours (252). These are what more zoom can still fix: a 4x window on B's answer would keep the target in 700 of the 905 misses. That figure is post-hoc.
- **Broken tasks:**
  - #133 marks Y for an X request, and #657 marks font size for font weight.
  - #491's English says "redo" where the Chinese instruction says undo (撤销). Its box also starts at y = -1.
  - 3 pairs ask the same thing on the same screen with two different keys (#639/#666, #992/#1025, #1042/#1069).
  - 2 cases are duplicates (#94/#105, #432/#474).
  - 30 screenshot files are byte copies of others.
  - On the Chinese-UI apps, many English instructions read as literal translations of the Chinese ones ("Benchmark Identifier" for 基准标识, datum identifier).
- **UI language:** 295 cases ask in English about a Chinese interface (AutoCAD, Inventor, Origin, SolidWorks, Stata). They score 30.2% after zoom vs 45.6% on English UIs, with the same zoom gain. Each of those apps is all Chinese, and six English apps score as low, so language and app cannot be separated.
- **Upstream:** a draft report for the ScreenSpot-Pro authors, with a check for earlier reports, is in `analysis/upstream-issue-pro/`. Not posted.

**What it leads to** (`AUDIT-pro-run2.md` section 11):
- 42.76% is the clean Pro number.
- More zoom could still fix the click-off half of the misses, but not the wrong-element half. That half needs a different first look or a model that knows these apps.
- The open option is a 4x second zoom step. It would be a separate, labelled experiment, "designed after seeing Pro run 2", with a prediction written down first, reported next to 42.76 and never instead of it. Arthur's call; not run.

## 2. What has been done (Oct 16-17 2026, CEST)

| Time | Step |
|---|---|
| ~18:00-19:57 | Research: Jev in computer use (X, ~30 GitHub repos, web). Gap: no public ScreenSpot run of real Jev 1.14 `box` |
| ~20:00-20:39 | Bench built: client, runner, scoring, offline tests, protocol frozen in README |
| 20:39-20:55 | 3 review rounds (12 agents), every confirmed finding fixed before spending |
| 20:55-21:03 | Pass 1: 20-case start, raw answers read, then the full pass resumed unchanged |
| 21:08 | Error analysis of the 212 misses (analysis/ERRORS-pass1.md) |
| 21:10-21:24 | Zoom method designed from pass 1 (offline replay, no calls), implemented with tests |
| 21:24-21:48 | Two review rounds of the zoom harness (12 agents, 26 minor findings, all fixed); one live smoke on #1095 |
| 21:49-22:01 | Pass 2 + zoom run: A2 84.36%, A+B 87.89%, 0 errors, $0.38 |
| 22:05-23:15 | Deep audit of all three runs (rescore, image rebuild, logs, billing) and label audit of the 271 missed cases |
| Oct 17 07:55-08:40 | Headroom analysis, both leaderboards collected (2 research agents), upstream issue drafted, checked for prior reports and posted (#65), ScreenSpot-Pro data downloaded |
| Oct 17 08:45-08:57 | Pro prep: 2x zoom alone frozen, loader + preflight + offline tests, download completed, 3-case smoke ($0.001) |
| Oct 17 09:00-09:33 | Two review rounds (fixes e2118e7, 4099bfa), wider and fresh smokes, Pro Run A raw: 19.17%, 0 errors, $0.25 |
| Oct 17 09:36-09:54 | Pro run 2: A2 18.66%, A2+B (2x zoom) 42.76%, 0 errors, $0.50; official re-score and diagnostics |
| Oct 17 09:58-11:15 | Pro deep audit, label audit of B's 905 misses, upstream draft |

Commits: 0a89357 (bench), fc84df2 and d9596d8 (review fixes, observability), 5266a58 (error analysis), 7b3c2d4 (zoom method), 1b2e535 and bb538fc (zoom review fixes), bb0aa6a and 89d0022 (pass 2 + zoom results), 02e029e and 5ea83f6 (deep audit and label audit), 74af257 and d206ea6 (headroom, leaderboards, upstream issue #65, Pro plan), 01ec94a, e2118e7 and 4099bfa (Pro loader, tests and review fixes), 3cc1088 (Pro Run A), b87db0d (Pro run 2).

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

## 7. Zoom method (frozen before the run, run in pass 2)

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
- Drawing real misses showed that centring the window on A's click cuts the target out of too-wide misses (#744: the "next page" arrow sits at the end of a wide row). Hence the window must contain A's whole box. That keeps 193 of 212 miss targets at least partly visible in the crop (vs 183 for click-centred; 177 fully inside, 185 with the centre inside) and widens the window in 14% of cases. Every pass-1 hit stays at least partly visible; 14 full-width list rows have their centre cut. Estimate unchanged at about 86% (85.8% under the runner's exact resize rule).
- Examples: `analysis/zoom-examples/` (miss_*_click.png vs miss_*_box.png, and B_sent_*.png = the exact image stage B would send).

What zoom can and cannot fix:
- **#1095** (too-wide, small target): fixable. At 2x the magnifier is a large blue square next to an empty field.
- **#744**: fixable with the grown window.
- **#331** (title-bar box as wide as the screen): the window is the full screen, so stage B is just a second try. Zoom does not fix a wrong pick.

In the run, #1095 stayed a miss: B boxed the field again, as in the smoke. #744 stayed a miss: A2 boxed the whole row again, so the window grew to 0.90 of the screen and the zoom was only 1.1x. #331 was hit by A2 and kept by B (conf 0.78).

Disclosure for any write-up: the crop rule was picked from pass 1 misses on the same test set (light selection: one round value on a flat curve, no search against real zoom scores). A clean confirmation would be ScreenSpot-Pro with the same frozen rule.

### The run (done 21:49-22:01, results in 1b)
`python3 screenspot.py run --pass 2 --zoom --workers 4 --max-cost 0.40`
- Stage A is byte-identical to a raw pass and goes to `results/pass2.jsonl`, so it is also pass 2: the rerun stability check.
- Stage B goes to `results/zoom2.jsonl`.
- Report: raw pass 1 (headline), raw pass 2 with pass-1/pass-2 agreement, zoom (A+B) with flips both ways against its own A, cost and latency of A+B vs A, all six cells.
- Expected cost about $0.38, against about $0.44 real credit. The cap of $0.40 stops cleanly, and resume re-runs only the missing stage.

### Live smoke (dev log, not part of any pass)
One live A+B call on #1095 at 21:35: A FALSE (search field boxed, conf 0.36), B FALSE (on the 2x crop Jev boxed the search field again, conf 0.32). Mechanics correct: same image size and tokens as A (3922 vs 3926), box mapped back right. The miss is an interpretation, not blur. No design change from this case. Figure: `analysis/figures/live-zoom-smoke_case_1095.png`.

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
- **Round 2:** 13 confirmed, all minor, 0 refuted. The crop and mapping maths were verified on all 1,272 cases, including 2,544 mocked calls. Fixed:
  - a full-screen window keeps B's box exactly
  - a half-written line after a hard kill is ended before the next append
  - the cap is checked before each call, and a rerun at the cap makes no call
  - `compare` auto-detects a zoom file
  - new `zoomstats` command: per cell, window groups, bootstrap CI, noise floor, latency and tokens over the same cases
  - identical box counted separately from identical box+confidence (confidence jitters: 0.38 vs 0.36 on identical #1095 requests)
  - the replay re-run under the runner's resize rule (85.8%)
  - the coverage wording
  - the smoke disclosure

## 8. Budget

| Item | Cost |
|---|---|
| 3 smoke calls (v1 wording, dev log) | $0.0005 |
| Pass 1 | $0.1909 |
| Live zoom smoke on #1095 (dev log) | $0.0003 |
| Pass 2 + zoom | $0.3817 |
| Credit left (read Oct 16 22:57, matches the logs) | $0.0581 |
| Key limit raised by Arthur (Oct 17) | |
| Pro smokes (3 plumbing cases, 14 screen sizes, 3 fresh) | $0.0061 |
| Pro Run A (raw) | $0.2523 |
| Pro run 2 (raw + zoom) | $0.5047 |
| Credit left (read Oct 17 10:34, matches the logs exactly) | $0.2950 |

One more Pro stage ($0.25) fits on the key; a v2 raw pass costs $0.19, and Pro raw + zoom ($0.50) needs a top-up. On Oct 16 the key also showed $0.0022 of usage that is not from the bench (`analysis/AUDIT-run2.md`, section 1).

## 9. Published comparison points (from the research notes, check each paper before public use)

Superseded by the sourced tables in `analysis/leaderboard/` (1e). The old list here missed the four models above 95.9.

| Model | ScreenSpot-v2 |
|---|---|
| MAI-UI-32B | 96.5 |
| OmegaUse-G | 96.3 |
| UI-Venus-1.5-30B-A3B | 96.2 |
| Holo2-235B (H Company) | 95.9 |
| UI-TARS-7B | 91.6 |
| OpenAI CUA | 87.9 |
| **Jev 1.14 zoom (this run)** | **87.89** |
| Claude 3.7 Sonnet | 87.6 |
| OS-Atlas-7B | 84.1 |
| **Jev 1.14 raw (this run)** | **83.33** |

OS-Atlas-7B appears as 84.1, 85.1 or 87.1 depending on the paper (4B vs 7B rows). Jev is a general decision model, not a grounding specialist, and runs in TypeSafe's long-context mode on OpenRouter for every image request ("slower and less accurate" per TypeSafe).

## 10. Pinned

- **Label audit of the misses: DONE** (1d, `analysis/LABELS-audit.md`). 43 of the 271 missed cases have a label issue, 4 of them wrong keys. Reported as a side note; the score stays the official key.
- **Wording ablation, off-benchmark only.** Whether a different wrapper sentence moves Jev toward buttons can only be tested on screenshots outside ScreenSpot-v2.
- **ScreenSpot-Pro with the same frozen zoom rule: DONE** (1e, 1f). 42.76%, the clean confirmation of the crop choice.
- **4x second zoom step on Pro:** an option, not decided (1f). It was designed after seeing Pro run 2, so it can only be a separate, labelled experiment with a prediction written down first.
- **Pro upstream label report** (`analysis/upstream-issue-pro/`): drafted, not posted. Needs Arthur's go.
- **HF discussion** version of the v2 label report (`analysis/upstream-issue/HF-DISCUSSION.md`), not posted.
- **Leaderboard charts** for the article, one per benchmark, no-tools and with-tools split, Jev highlighted.
- **Row-preserving crop for tall mobile screens.** The main cost of zoom is context loss on mobile settings rows (1c). Test it only on a separate set, never tuned on ScreenSpot-v2.

## 11. Caveats

- Run-to-run noise is measured: 49 of 1272 cases (3.9%) flip between two identical raw passes, and the 1.0 pp gap is not significant (p=0.085). The headline stays pass 1.
- The official answer key has 4 wrong boxes, and 39 more missed cases sit on ambiguous instructions (1d). All scores use the key as is, like every published table, so comparisons stay fair.
- The zoom crop rule was picked from pass 1 misses on this same test set (light selection, section 7). ScreenSpot-Pro is the clean check: the rule was reused there untouched (1e).
- The Pro answer key has its own errors: 3 cases where the key and the English instruction disagree, 3 pairs with contradictory keys, and 2 duplicates (1f). All Pro scores use the key as is.
- 295 Pro cases ask in English about a Chinese interface, as in the official leaderboard setting. They score lower, but language and app cannot be separated (1f).
- 81% of cases are downscaled to fit 1568 px, which hurts small targets. That is a property of the API limit, reported rather than worked around in the raw number.
- Long-context mode is forced for images on OpenRouter; the direct TypeSafe API might score differently.
- `jev-latest` changes around Oct 21. This run is pinned to `jev-1.14`, and the resolved dated id is logged per case.
