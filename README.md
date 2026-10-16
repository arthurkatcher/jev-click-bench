# jev-screenspot

Raw Jev 1.14 `box` grounding on ScreenSpot-v2. One screenshot + one instruction -> one `box` question -> click the box centre -> hit if the centre is inside the ground-truth bbox, edges inclusive (the standard ScreenSpot rule, same as SeeClick `pretrain/screenspot_test.py` and ScreenSpot-Pro `eval_sample_positive_gt`).

## Layout
- `jev.py`: OpenRouter `POST /api/alpha/decisions`, model `typesafe/jev-1.14`, header `TypeSafe-Danger-Zone-Images: true`, image as an `image_url` part in `state`. `fit()` scales screenshots so both sides are 280-1568 px (Jev's limit), no padding, so box fractions map 1:1 to the original (within ~1 px). `decide()` retries 429/5xx/504/524/529, timeouts and connection errors (honours Retry-After), raises `JevError`; 401/402/403 are fatal (stop the run). The key is never logged.
- `screenspot.py`:
  - `run_one(i)`: one case; every call writes a record (`status` ok / wrong_format / infra_error, raw response, pass id, ISO timestamp, prompt version + template hash, requested and resolved model, attempts, cost).
  - `run_all(pass)`: full pass into `results/pass<N>.jsonl`; resumes (skips scored cases, re-runs infra errors), thread pool, cost cap, stops on fatal errors.
  - `report(file)`: the six cells with n and hits, micro and macro averages, wrong_format / infra_error / not-run / degenerate counts, latency, cost, confidence AUROC and accuracy by confidence bin. A pass with any unscored case is printed as INCOMPLETE.
- `tests/test_offline.py`: mocked-API tests (no spend) for every path above.
- `data/screenspot-v2/`: OS-Copilot/ScreenSpot-v2 from Hugging Face: 1,272 cases over 730 referenced screenshots (the folder holds 756 files + a tar; 26 unreferenced). Cells: mobile text 290, mobile icon 211, desktop text 194, desktop icon 140, web text 234, web icon 203. bbox = [x, y, w, h] pixels.
- `ref/`: official eval code, read-only: SeeClick, OS-Atlas, ScreenSpot-Pro-GUI-Grounding (its model-adapter interface `ground_only_positive(instruction, image)` can take a Jev adapter later for ScreenSpot-Pro).
- `results/runs.jsonl`: dev log of single-case runs only (3 smoke calls on Oct 16 with the old v1 wording). Never part of a pass.

## Usage
    python3 tests/test_offline.py                       # offline tests, no API calls
    python3 screenspot.py 0 --dry                       # show one request
    python3 screenspot.py 0                             # one live case -> dev log
    python3 screenspot.py run --pass 1 --workers 4      # full pass (cap $0.30 by default)
    python3 screenspot.py report results/pass1.jsonl

## Protocol (frozen before the full run)
- Prompt v2: box instruction `In the screenshot, the UI element to use for this task: <instruction>`, instruction whitespace-normalised and passed unquoted (21 contain their own quotes, 40 start with "click", 17 with "tap"). No wording iteration on ScreenSpot-v2 rows; any wording ablation runs off-benchmark and is reported separately.
- Headline = pass 1, micro average (hits / 1,272), the convention published v2 tables use (OS-Atlas-7B's 84.12 recomputes as micro; its macro would be 82.20). Macro (mean of six cells) printed next to it, labelled. Baselines are compared under the convention their paper uses, checked against the paper's own table.
- Malformed answers count as misses (`wrong_format`), as in both official evals; their number is reported. Infrastructure failures (HTTP errors, transport errors, a 200 body with no `answers` object) are re-run until the pass is complete. A pass with unscored cases, mixed prompt versions or mixed requested/resolved models prints INCOMPLETE on every number and is not a headline.
- Edges are inclusive with a 1e-9 tolerance, so float noise on a 2-decimal box centre that sits exactly on a truth edge cannot flip a hit into a miss; such centres are counted (`on_edge`).
- Degenerate boxes (right <= left or bottom <= top) are scored by their centre like the official rule, flagged, and counted in the report.
- Pass 2 = same protocol, own file. Report pass 1 as the headline, pass 2, the case-level agreement and mean ± half the difference. Never best-of-two or union.
- Model pinned to `typesafe/jev-1.14` (jev-latest flips ~Oct 21); the resolved dated id is logged per case.
- Stated caveats: OpenRouter runs every image request in TypeSafe's long-context mode ("slower and less accurate"); 1,034 of 1,272 cases are downscaled to fit 1568 px (median 0.62x, mean 0.65x, min 0.54x), which hurts small icons.

## Budget
Cost = input tokens x $0.042/M, about 614 + 0.0024 tokens per sent pixel: ~$0.19 per pass. The current key (~$0.63 left) fits two passes. `--max-cost` (default $0.30) stops a pass early.

## Smoke calls (Oct 16 2026, v1 wording, dev log)
| Case | Type | Result | Conf | Time | Cost |
|---|---|---|---|---|---|
| 0 mobile/ios "check the weather" | icon | TRUE | 0.72 | 1.20 s | $0.00020 |
| 835 web/gitlab "create a new project" | text | TRUE | 0.92 | 0.83 s | $0.00016 |
| 838 web/gitlab "add a new one" | icon | TRUE (edge) | 0.75 | 0.77 s | $0.00016 |
