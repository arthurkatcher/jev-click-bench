# jev-screenspot

How well Jev 1.14's `box` tool clicks: a full run on ScreenSpot-v2 and ScreenSpot-Pro with the official scoring, plus a zoomed second look that more than doubles it on Pro. Write-up: [Jev 1.14 can click: 84% on ScreenSpot-v2, 43% on Pro with a second look](https://arthurkatcher.com/blog/how-well-jev-clicks).

| Benchmark | Setup | Calls per click | Score | Cost per 1,000 clicks |
|---|---|---|---|---|
| ScreenSpot-v2 (1,272) | Jev box | 1 | 84.36% | $0.15 |
| ScreenSpot-v2 | + 2x zoom | 2 | 87.89% | $0.30 |
| ScreenSpot-Pro (1,581) | Jev box | 1 | 18.66% | $0.16 |
| ScreenSpot-Pro | + 2x zoom | 2 | 42.76% | $0.32 |
| ScreenSpot-Pro | + 4x zoom, post-hoc | 3 | 60.15% | $0.48 |

- Raw and zoom rows are the same run (pass 2 + zoom). A separate first raw pass scored 83.33% (v2) and 19.17% (Pro), the same within noise.
- The 4x step was designed after the 2x result, with its prediction committed first (`analysis/zoom4x/prediction.txt`): 63.2%, range 59.7-66.2.
- Every score uses the official answer key, even where the label audit thinks the key is wrong.
- Costs are OpenRouter's billed cost per request, logged in each record.

Everything behind the numbers is here: the harness, every request's record (`results/`, one JSON line per click with Jev's raw response, box, click, hit and cost), the run logs, the deep audits (`analysis/AUDIT-run2.md`, `analysis/AUDIT-pro-run2.md`), the label audits and the running report (`REPORT.md`).

Label problems found in both benchmarks were reported upstream: [OS-Atlas #65](https://github.com/OS-Copilot/OS-Atlas/issues/65) (ScreenSpot-v2), [ScreenSpot-Pro #32](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/issues/32) and [HF discussion #5](https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/discussions/5).

## Run it yourself

1. Python 3.10+, `pip install requests pillow`.
2. Get the data from Hugging Face into `data/`: [OS-Copilot/ScreenSpot-v2](https://huggingface.co/datasets/OS-Copilot/ScreenSpot-v2) into `data/screenspot-v2/`, [likaixin/ScreenSpot-Pro](https://huggingface.co/datasets/likaixin/ScreenSpot-Pro) (revision 210e78d) into `data/screenspot-pro/`. Screenshots are not in this repo.
3. Copy `.env.example` to `.env` and put in an OpenRouter key.
4. `python3 tests/test_offline.py` (no API calls), then `python3 screenspot.py run --pass 1 --workers 4`. A full v2 pass costs about $0.19, a Pro stage about $0.25.

The official eval code the scoring copies lives in `ref/` locally (SeeClick, OS-Atlas, ScreenSpot-Pro-GUI-Grounding) and is not redistributed here.

Datasets: ScreenSpot-v2 (Apache-2.0, OS-Copilot) and ScreenSpot-Pro (MIT, Li et al.). The result records quote their instructions and answer boxes. Code: MIT.

## Layout
- `jev.py`: OpenRouter `POST /api/alpha/decisions`, model `typesafe/jev-1.14`, header `TypeSafe-Danger-Zone-Images: true`, image as an `image_url` part in `state`. `fit()` scales screenshots so both sides are 280-1568 px (Jev's limit), no padding, so box fractions map 1:1 to the original (within ~1 px). `decide()` retries 429/5xx/504/524/529, timeouts and connection errors (honours Retry-After), raises `JevError`; 401/402/403 are fatal (stop the run). The key is never logged.
- `screenspot.py`:
  - `run_one(i)`: one case; every call writes a record (`status` ok / wrong_format / infra_error, raw response, pass id, ISO timestamp, prompt version + template hash, requested and resolved model, attempts, cost).
  - `run_all(pass)`: full pass into `results/pass<N>.jsonl`; resumes (skips scored cases, re-runs infra errors), thread pool, cost cap, stops on fatal errors.
  - `report(file)`: the six cells with n and hits, micro and macro averages, wrong_format / infra_error / not-run / degenerate counts, latency, cost, confidence AUROC and accuracy by confidence bin. A pass with any unscored case is printed as INCOMPLETE.
- `tests/test_offline.py`: mocked-API tests (no spend) for every path above.
- `tests/test_zoom4x_offline.py`: mocked tests for stage C (window rule on all 1,581 B answers, exact mapping, official rule, cost cap, resume, failure paths).
- `data/screenspot-v2/`: OS-Copilot/ScreenSpot-v2 from Hugging Face: 1,272 cases over 730 referenced screenshots (the folder holds 756 files + a tar; 26 unreferenced). Cells: mobile text 290, mobile icon 211, desktop text 194, desktop icon 140, web text 234, web icon 203. bbox = [x, y, w, h] pixels.
- `ref/`: official eval code, read-only: SeeClick, OS-Atlas, ScreenSpot-Pro-GUI-Grounding (its model-adapter interface `ground_only_positive(instruction, image)` can take a Jev adapter later for ScreenSpot-Pro).
- `results/runs.jsonl`: dev log of single-case runs only (3 smoke calls on Oct 16 with the old v1 wording, then the live zoom smoke on #1095, A and B). Never part of a pass.
- `REPORT.md`: the run report. `analysis/`: `pro_run2_analysis.py` (Pro run 2 integrity, official re-score, declared zoom diagnostics), `audit_run2.py` (deep audit: integrity asserts and every number in `AUDIT-run2.md`), `labels_audit.py` + `label-audit/` (label audit of every missed case, `LABELS-audit.md`), `errors.py` (pass-1 error table), `figures.py` and `label_figures.py` (article figures, listed in `figures/INDEX.md`), `zoom-replay/`, `zoom-examples/`, `headroom.py` (post-hoc selectors and ceilings after zoom), `leaderboard/` (sourced v2 and Pro score tables, official Pro leaderboard data), `upstream-issue/` (the label report posted as OS-Atlas issue #65, figures, prior-report check). ScreenSpot-Pro: `audit_pro_run2.py` (deep audit: integrity asserts and every number in `AUDIT-pro-run2.md`; `--images`, `--balance`), `labels_audit_pro.py` + `label-audit-pro/` (label audit of B's 905 misses and the UI language of all cases, `LABELS-audit-pro.md`; reviewer instructions, verdicts, language labels, QC notes), `pro_label_figures.py` (case images, language sheets, close-ups; the images themselves are not in git), `upstream-issue-pro/` (the label report posted as ScreenSpot-Pro issue #32 and HF discussion #5), `zoom4x/` (stage C: prediction registered before any stage-C call, analysis and results).

## Usage
    python3 tests/test_offline.py                       # offline tests, no API calls
    python3 screenspot.py 0 --dry                       # show one request
    python3 screenspot.py 0                             # one live case -> dev log
    python3 screenspot.py run --pass 1 --workers 4      # full pass (cap $0.30 by default)
    python3 screenspot.py report results/pass1.jsonl
    python3 screenspot.py compare results/pass1.jsonl results/pass2.jsonl
    python3 screenspot.py run --pass 2 --zoom --max-cost 0.40   # raw pass 2 + zoom in one run
    python3 screenspot.py compare results/pass2.jsonl results/zoom2.jsonl   # A vs A+B (auto: method comparison)
    python3 screenspot.py zoomstats results/pass2.jsonl results/zoom2.jsonl --rerun results/pass1.jsonl

ScreenSpot-Pro: the same commands with `--bench pro` first; data in `data/screenspot-pro/`, results in `results/pro/`.

    python3 tests/test_pro_offline.py                   # Pro offline tests, no API calls
    python3 screenspot.py --bench pro check             # offline preflight: images, sizes, boxes
    python3 screenspot.py --bench pro run --pass 1 --workers 4                  # Run A: raw pass 1, ~$0.25
    python3 screenspot.py --bench pro run --pass 2 --zoom --workers 4 --max-cost 0.60   # run 2: raw A2 + 2x zoom B, ~$0.50
    python3 screenspot.py --bench pro zoomstats results/pro/pass2.jsonl results/pro/zoom2.jsonl --rerun results/pro/pass1.jsonl
    python3 analysis/audit_pro_run2.py                  # Pro deep audit, offline (--images, --balance)
    python3 analysis/labels_audit_pro.py                # Pro label audit tables, offline
    python3 tests/test_zoom4x_offline.py                # stage C offline tests, no API calls
    python3 analysis/zoom4x/predict.py                  # stage C prediction, offline
    python3 screenspot.py --bench pro zoom4x --limit 3 --annotate all --out zoom4x_smoke.jsonl --max-cost 0.01   # stage C smoke
    python3 screenspot.py --bench pro zoom4x --workers 4 --max-cost 0.28      # stage C (4x, post-hoc): ~$0.25

## Protocol (frozen before the full run)
- Prompt v2: box instruction `In the screenshot, the UI element to use for this task: <instruction>`, instruction whitespace-normalised and passed unquoted (21 contain their own quotes, 40 start with "click", 17 with "tap"). No wording iteration on ScreenSpot-v2 rows; any wording ablation runs off-benchmark and is reported separately.
- Headline = pass 1, micro average (hits / 1,272), the convention published v2 tables use (OS-Atlas-7B's 84.12 recomputes as micro; its macro would be 82.20). Macro (mean of six cells) printed next to it, labelled. Baselines are compared under the convention their paper uses, checked against the paper's own table.
- Malformed answers count as misses (`wrong_format`), as in both official evals; their number is reported. Infrastructure failures (HTTP errors, transport errors, a 200 body with no `answers` object) are re-run until the pass is complete. A pass with unscored cases, mixed prompt versions or mixed requested/resolved models prints INCOMPLETE on every number and is not a headline.
- Headline hit = the official rule exactly (strict float compare, edges inclusive). A 1e-9 edge-tolerant average is printed next to it with the number of cases that differ. Boxes with edges outside [0,1] are scored by centre like the official code and counted; a response with no box at all is re-run as an infra error. Report prints Wilson 95% CIs; gaps to a baseline inside the CI are called on par.
- Pass 1 starts with `--limit 20` (the first live calls of the frozen v2 wording), raw answers read, then the same pass resumes with no change. `compare` gives pass-1/pass-2 agreement after both are complete. Billed spend is checked against the key balance before and after each run.
- Degenerate boxes (right <= left or bottom <= top) are scored by their centre like the official rule, flagged, and counted in the report.
- Pass 2 = same protocol, own file. Report pass 1 as the headline, pass 2, the case-level agreement and mean ± half the difference. Never best-of-two or union.
- Model pinned to `typesafe/jev-1.14` (jev-latest flips ~Oct 21); the resolved dated id is logged per case.
- Stated caveats: OpenRouter runs every image request in TypeSafe's long-context mode ("slower and less accurate"); 1,034 of 1,272 cases are downscaled to fit 1568 px (median 0.62x, mean 0.65x, min 0.54x), which hurts small icons.

## Zoom method (frozen Oct 16 2026, before any zoom call)
A separate method, never the headline. Two `box` calls per case:
- Stage A = the raw call, byte-identical to a normal pass, written to `results/pass<N>.jsonl`. So a zoom run is also a full raw pass (pass 2 = the rerun/stability check).
- Stage B = the same prompt and question on a crop of the ORIGINAL screenshot: half of each side (`ZOOM_F = 0.5`) centred on A's box, grown to contain A's whole box + 10% margin per side (`ZOOM_MARGIN`, capped at the full screen), same aspect ratio, slid to stay inside the image. The crop is resized (bicubic) to A's sent size, so B costs the same tokens as A and the zoom is 1/k (2x for a small box). B's box (fractions of the crop) is mapped back to the full screenshot and scored with the same official rule, written to `results/zoom<N>.jsonl` (`stage: "B"`, `window`, `window_frac`, raw `box_crop`).
- A full-screen window sends the identical image, and B's box is kept exactly (no remap), so it compares 1:1 with A.
- When A's box + margin covers the whole screen (~7% of pass-1 boxes, `window_frac` 1.0), B re-asks the identical image: those cases are a free in-run noise control and are reported as their own group (by `window_frac`: 0.5 / widened / 1.0).
- B records carry `zoom_f`, `zoom_margin`, `code_rev`; `report` marks a file with mixed zoom configs INCOMPLETE. `out_of_range` is on the mapped box (outside the screenshot); `out_of_crop` flags a B box past the crop edge (allowed: the target can be cut by the crop).
- B runs on every case (no confidence gate). A wrong_format A gives a copied wrong_format zoom record, no call. Resume re-runs only the missing stage; `--max-cost` covers both stages; 401/402/403 on either stage stops the run.
- Report: raw pass 1 (headline), raw pass 2 (stage A) + pass-1/pass-2 agreement and identical-answer count, zoom (A+B) + miss->hit / hit->miss vs its own A, per cell, cost and latency of A+B vs A. Method-vs-method and pass-vs-pass gaps use the paired exact McNemar test on the same cases (`compare` prints it), not CI overlap; pass 1 vs pass 2 is the noise floor for the zoom flips.
- Resume after a stop: the cap counts everything already logged in pass2 + zoom2, so rerun the same command with `--max-cost` raised to the logged total plus ~$0.0003 per remaining case. A run whose logged spend is already at the cap makes no call; B is never started once A has reached the cap.
- `zoomstats` prints the paired table (all, six cells, window groups half / widened / full screen, native vs downscaled), a 95% bootstrap CI of the delta, the full-screen group's flips next to the raw rerun's flips (noise floor), latency median/p90 and tokens over the same cases, and total logged cost.
- The key balance lags billing by many minutes (pass 1: "billed" $0.019 right after, logged $0.187); logged `usage.cost` is the cost of record, the balance is rechecked later. Balance before the zoom run: $0.440.
- How the crop was chosen (stated in any write-up): from pass-1 answers, offline, no calls. Accuracy by target size saturates around 60 sent px; a replay estimated ~86% for this crop (anchored model, each case keeps its pass-1 difficulty) with diminishing returns past 2x and targets falling out of tighter crops; centring on A's click alone cut the target out of too-wide misses (#744), so the window must contain A's box. Choosing the crop from pass-1 data is light test-set selection; 0.5 is also the round 2x choice. What was compared, all on pass-1 outcomes and never on a zoom answer: 12 crop sizes (0.15-1.0 of each side), click-centred vs box-containing window (3 sizes), confidence gates 0.7/0.8/0.9/none, an upscale cap; margin fixed at 0.1, not swept. Registered prediction before any zoom call: ~86% (range ~85-87%); the same replay under the runner's exact resize rule (crop resized to A's sent size, `zoomsim6.py`): 85.8%. Coverage on pass-1 answers: miss targets at least partly visible (>=8 sent px) 193/212, fully inside 177, centre inside 185; hits partly visible 1060/1060, centre inside 1046 (14 full-width rows half cut). One live zoom smoke before the run (#1095, dev log, chosen as the showcase case): A FALSE, B FALSE; nothing changed after it, no further smokes; article zoom figures come from `results/zoom2.jsonl` only. Scripts and their printed tables: `analysis/zoom-replay/` (`replay-output.txt`); example images: `analysis/zoom-examples/`.

## Stage C on Pro: the zoom step once more (Oct 17 2026, post-hoc)
- Designed after seeing Pro run 2 (the audit's 4x ceiling), on Arthur's go. A labelled extra, reported next to the Pro zoom result 42.76 and never in its place.
- Rule: the frozen zoom rule applied once more, inside B's window around B's box (`zoom_again_window`): half of each side of B's window, grown for a big box, slid to stay inside it. So a small target is 4x its size in A's image. The crop is resized to A's sent size (the same tokens as B), the box is mapped back to the full screenshot and scored with the official rule.
- One call per case, into `results/pro/zoom4x.jsonl` (`stage: "C"`, pass `c2`, `window`, `parent_window` = B's window). A wrong_format B would give a copied miss with no call (run 2 has none). Resumable, `--max-cost` covers the file, 401/402/403 stops the run.
- Prediction registered before any stage-C call, smoke included (`analysis/zoom4x/prediction.txt`): C = 63.2%, 95% range 59.7-66.2%, about 397 of B's 905 misses fixed and 74 of its 676 hits broken. The model replays what the 2x step did (B's keep and fix rates by target size in B's image) on B's answers at C's sizes. Ceiling: the target centre stays in C's window in 1,377 cases (87.1%).
- Smoke: 3 cases into `results/pro/zoom4x_smoke.jsonl`, never part of the score.
- Result (Oct 17 11:39-11:47, log `results/pro/zoom4x.log`): **60.15%**, +17.39 pp over B (340 fixed, 65 broken), inside the registered range, 0 errors, $0.2523. Analysis: `analysis/zoom4x/analyze.py` -> `results.txt`; write-up in REPORT.md 1g.

## Budget
Cost = input tokens x $0.042/M, about 614 + 0.0024 tokens per sent pixel: ~$0.19 per v2 pass, ~$0.25 per Pro stage (every Pro screenshot is sent at the 1568 px limit). The key held $0.295 on Oct 17 10:34 and $0.042 on Oct 17 11:49 after the 4x step (both matching the logs): any further run needs a top-up. `--max-cost` (default $0.30) stops a pass early.

## Smoke calls (Oct 16 2026, v1 wording, dev log)
| Case | Type | Result | Conf | Time | Cost |
|---|---|---|---|---|---|
| 0 mobile/ios "check the weather" | icon | TRUE | 0.72 | 1.20 s | $0.00020 |
| 835 web/gitlab "create a new project" | text | TRUE | 0.92 | 0.83 s | $0.00016 |
| 838 web/gitlab "add a new one" | icon | TRUE (edge) | 0.75 | 0.77 s | $0.00016 |
