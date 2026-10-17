# Cost, latency and compute per task: ScreenSpot-Pro and ScreenSpot-v2 leaders (collected Oct 17 2026)

Collected by research agents on 2026-10-17. All prices were read that day. No model provider API was called and nothing was spent. Entry list: `screenspot-pro.md`, `screenspot-v2.md` and `official-leaderboard-screenspot_pro.json` in this folder. Source keys (A1, O3, P8, ...) are listed at the end.

## Summary

**What is published**

- **Calls per task:** published, or derivable from the method, for most open-weight entries. Zoom-in = 2 calls, GroundCascade = 2.574, the KV-Ground + Qwen3.5 router = 4, Holo2 agentic = up to 3 steps, MVP = m+1 views, UI-Zoomer = 8 samples + 0 or 1 crop pass.
- **API prices:** published for every API model. Each provider documents its image-token rule.
- **Eval settings for frontier labs:** effort level, tools, and number of runs averaged (Anthropic: 5 runs).

**What is not published**

- **Dollar cost per task or per run:** no entry on either leaderboard publishes one.
- **Tokens per task:** no ScreenSpot entry publishes these. That includes thinking tokens for every reasoning model and tool-call counts for every "with Python" or "crop tool" run.
- **Latency per task:** essentially unpublished for ScreenSpot. The only measured time found is Duvo Eye-1's public eval logs: Pro 1,774.7 s for 1,581 tasks (about 1.12 s/task) and v2 379.2 s for 1,272 (about 0.30 s/task), sequential, local vLLM, GPU not stated. UI-Zoomer publishes total v2 wall times on 4x RTX 4090D. Phi-Ground publishes per-call latencies, but on a different benchmark (Showdown-click-dev).
- **Max turns, steps or tool-call caps:** no lab publishes these for its tool runs.

**Consequences for the chart**

- Any dollar figure for a leaderboard entry is an estimate: price x estimated tokens. Those numbers are in the Estimates section only.
- For tool and thinking runs, input-only estimates are a hard floor. The real cost is dominated by unpublished thinking output billed at $12-125 per M.
- Even on the image-only floor, every frontier API model costs 7x to 600x Jev per screenshot (see the estimates).

**New v2 rows that change the v2 top** (not in `screenspot-v2.md`; read from the cached paper text):

| v2 score | Model | Source |
|---|---|---|
| 97.88 | GPT-6 Astra | GroundAnything Table 2 (O8) |
| 97.5 | Qwen-UI-Agent-27B | Q5 Table 8 |
| 96.7 | Qwen-UI-Agent-35B-A3B | Q5 Table 8 |
| 95.8 | Indeed-UI-32B | HF card (P2) |
| 95.60 | GroundAnything | O8 |
| 95.05 | Duvo Eye-1 | Eval files (P14) |
| 94.6 | KV-Ground-8B | P3 |
| 94.4 | Fara1.5-27B | P16 |

MAI-UI-32B (96.5) is therefore no longer the v2 leader.

**Label corrections found along the way**

- **Qwen3-VL "v2" numbers (8B 94.4, 32B 95.8, 235B-Thinking 95.4):** Qwen's own card tables label the row "ScreenSpot", and the tech report cites v1 (V2, V3). Independent v2 runs of Qwen3-VL-8B give 91.7 to 93.2, and Qwen3-VL-32B gets 93.0 (V5).
- **OS-Atlas-Base-7B 87.1:** includes a GPT-4o planner call. Without the planner it is 84.12; 4B is 71.86 without and 79.09 with GPT-4o (V12 Table 8).
- **Anthropic re-scored older models under a new prompt.** The Mythos 5 card (A3) is the only same-prompt set: Mythos Preview 79.3 / 93.0, Opus 4.8 82.4 / 89.5, Mythos 5 87.3 / 90.7 (no tools / tools). Opus 4.8's own card says 82.3 / 87.9 (A1).
- **Opus 4.7 depends on resolution.** At the lower image resolution it scores 69.0 / 85.9 (A2), against 79.5 / 87.6 at full resolution.

## Our run (measured, from REPORT.md)

| Run | Score | Calls | Median latency | Input tok/task | Cost/task |
|---|---|---|---|---|---|
| Jev 1.14 v2 raw | 83.33 | 1 | 0.89 s | 3,573 mean | $0.00015 |
| Jev 1.14 v2 zoom | 87.89 | 2 | 1.67 s | 7,146 mean | $0.0003 |
| Jev 1.14 Pro raw (planned) | n/a | 1 | n/a | ~3,800 est. | ~$0.000158 est. |
| Jev 1.14 Pro zoom (planned) | n/a | 2 | n/a | ~7,600 est. | ~$0.00032 est. |

- **Price and output:** Jev is $0.042 per M input on OpenRouter, with 20 output tokens per answer. Pass-1 wall time was 7 min 12 s with 4 workers.
- **Pro estimate:** $0.25 per stage / 1,581 tasks.

## ScreenSpot-Pro: published calls, latency, tokens, cost

Scores as in `screenspot-pro.md`. "n.p." = not published.

| Entry | Score | Calls/task | Tools | Latency | Tokens | Cost | Src |
|---|---|---|---|---|---|---|---|
| GPT-6 Astra | 92.7 | n.p. | none | n.p. | n.p. | n.p. | O1 |
| GPT-6 Astra (XPeng re-run) | 93.17 | n.p. | none, effort High | n.p. | n.p. | n.p. | O8 |
| Claude Mythos Preview | 93.0 | n.p., 5 runs avg | Python + crop | n.p. | n.p. | n.p. | A3, A4 |
| Claude Mythos 5 | 90.7 | n.p., 5 runs avg | Python + crop | n.p. | n.p. | n.p. | A3 |
| Claude Mythos 5 | 87.3 | 1 + thinking, 5 runs | none | n.p. | n.p. | n.p. | A3 |
| Claude Opus 4.8 | 87.9 | n.p., 5 runs avg | Python | n.p. | n.p. | n.p. | A1 |
| Claude Opus 4.8 | 82.3 | 1 + thinking, 5 runs | none | n.p. | n.p. | n.p. | A1 |
| Claude Opus 4.7 | 87.6 / 79.5 | n.p., 5 runs avg | Python / none | n.p. | n.p. | n.p. | A2 |
| GPT-5.2 Thinking | 86.3 | n.p. | Python, xhigh | n.p. | n.p. | n.p. | O2 |
| GPT-5.4 xhigh | 85.4 | single attempt | Code Interpreter | n.p. | n.p. | n.p. | M2 |
| GroundCascade (32B + 8B) | 85.1 | 2.574 avg | 0.5 zoom, gates | n.p. | n.p. | n.p. | L1 |
| Qwen3.8-Max | 84.5 | n.p. | n.p. | n.p. | n.p. | n.p. | Q1 |
| Gemini 3.1 Pro (Meta run) | 84.4 | single attempt | crop tool | n.p. | n.p. | n.p. | M2 |
| Meta Muse Spark | 84.1 | single attempt | crop tool | n.p. | n.p. | n.p. | M1, M2 |
| Indeed-UI-32B zoom | 82.7 | 2 | 0.5 crop | n.p. (8 GPUs) | n.p. | n.p. | P1 |
| Qwen-UI-Agent-27B zoom | 81.5 | n.p. (zoom) | zoom-in | n.p. | n.p. | n.p. | Q5 |
| KV-Ground-8B + Qwen3.5-27B | 80.9 | 4 | 2-step zoom x2 | n.p. (H200) | n.p. | n.p. | P4 |
| KV-Ground-8B zoom | 80.5 | 2 | 0.5 crop | n.p. | n.p. | n.p. | P3, P4 |
| GUI-Owl-1.5-32B crop | 80.3 | 2 | 2-stage crop | n.p. | n.p. | n.p. | P13 |
| Qwen3.7-Plus | 79.0 / 68.9 | n.p. | zoom / none | n.p. | n.p. | n.p. | Q2, Q5 |
| Holo2-235B-A22B agentic | 78.5 | up to 3 steps | agentic | n.p. | n.p. | n.p. | P5 |
| MAI-UI-32B MVP | 77.5 | "max 2" (LB) | multi-crop vote | n.p. (4 A100) | n.p. | n.p. | L1, P10 |
| AdaZoom-GUI-4B | 76.8 | 1-2 + 1 refiner | cond. zoom | n.p. | n.p. | n.p. | P15 |
| Qwen-UI-Agent-27B | 76.6 | 1 | none | n.p. | n.p. | n.p. | Q5 |
| GroundAnything | 75.96 | 1 | diffusion decode | see note | <=1,024 vis tok | n.p. | O8 |
| UI-Venus-2-27B | 74.1 | 1 | reasoning off | n.p. | n.p. | n.p. | P11 |
| MAI-UI-32B zoom | 73.5 | 2 | 0.5 crop | n.p. | n.p. | n.p. | P9 |
| Indeed-UI-32B | 73.3 | 1 | none | n.p. | n.p. | n.p. | P1 |
| Duvo Eye-1 | 72.9 | 1 | none, temp 0 | 1.12 s/task | n.p. | n.p. | P14 |
| Holo3-122B-A10B | 72.2 | n.p. | n.p. | n.p. | n.p. | n.p. | P6 |
| Holo3.1-35B-A3B | 71.5 | n.p. | n.p. | n.p. | n.p. | n.p. | P7 |
| Holo2-235B-A22B | 70.6 | 1 | none | n.p. | n.p. | n.p. | P5 |
| UI-Venus-1.5-30B-A3B | 69.6 | 1 | none | n.p. | n.p. | n.p. | P12 |
| Gemini 3 Pro | 72.7 | n.p., pass@1 | screenshot tool | n.p. | n.p. | n.p. | G1 |
| Gemini 3 Flash | 69.1 | n.p., pass@1 | none | n.p. | n.p. | n.p. | G2 |
| MAI-UI-32B | 67.9 | 1 | none | n.p. | n.p. | n.p. | P9 |

**Settings as quoted**

- **Anthropic (A1-A4):** all six 2026 cards use "adaptive thinking, maximum effort", and "Scores are averaged over five runs" on the full 1,581 instructions. The Mythos 5 card says the tool runs were "provided with a container, with the image file and standard Python libraries installed, and an image cropping tool".
- **Anthropic image caps (A3, A2):** Mythos Preview was run at "a maximum of 1,568px along any single image dimension and up to 1,568 tokens". Mythos 5 ran at "a maximum of 2,576px ... and up to 4,784 tokens". Opus 4.7: 2576px and up to 3.75MP. No card gives max turns, a tool-call cap or max_tokens.
- **OpenAI Astra (O1):** "Evaluation scores are the maximum at any effort", so the effort behind 92.7 is not stated.
- **GroundAnything (O8):** "GPT-6 Astra uses thinking effort High". The paper gives no tokens, latency, cost, resolution or retries for the API models it re-ran.
- **GPT-5.2 (O2):** "A Python tool was enabled and reasoning effort was set to maximum."
- **Meta (M2):** "For our model and Gemini, we used a cropping tool; and for GPT we enabled a python code interpreter. We resize large images to fit within API limits." Also "a single attempt per problem". So the 84.4 Gemini 3.1 Pro row labelled "with Python" in aggregators was actually run with a cropping tool.
- **Gemini 3 Pro (G1):** "function calling with a 'capture screenshot' tool ... media_resolution parameter to 'extra_high'". At "high" resolution it scores 60.5.
- **Qwen3.7-Plus (Q2):** reported with "enable_thinking=False". The zoom split (79.0 zoom / 68.9 none) is from Alibaba's own Qwen-UI-Agent paper (Q5), which does not describe the zoom procedure.

**Open-weight harnesses**

- **GroundCascade (L1):** the leaderboard description reads "fixed 0.5 zoom; 1% self-consistency gate; 4% cross-model agreement gate; greedy decoding; 2.574 average model calls/example". No paper or repo exists; the leaderboard repo commit fd896b54 (2026-10-01) only adds JSON. How the calls split between the 32B and 8B models is not published.
- **KV-Ground + Qwen3.5-27B router (P4):** the paper says it "doubles inference cost (4 forward passes vs. 2)". Hardware: "NVIDIA H200 141GB". Qwen3.5-27B runs AWQ 4-bit.
- **Indeed-UI (P1):** the eval script uses crop_size_ratio 0.5, temperature 0, max_new_tokens 512, max_pixels 99999999, launched with torchrun on 8 GPUs (type not stated).
- **MAI-UI MVP (L1, P10):** the leaderboard says "MVP on attention layer 48; max inference process is 2". The MVP paper runs m views plus the full image (m + 1 predictions) and ran 32B models "on 4 A100", with no per-task time.
- **Duvo Eye-1 (P14):** the time comes from the public eval files: 1,774.7 s for 1,581 samples, sequential, local vLLM, GPU not stated. The model repo duvoai/duvo-eye-1 now returns 401; v1.5 and the evals dataset are public.
- **GroundAnything speed (O8):** measured on COCO, not GUI: 3.73 to 7.15 ms per output token on H800. Throughput is 127.0 to 223.8 TPS for the diffusion modes against 49.6 TPS for the autoregressive version.

**Frontier token use outside ScreenSpot (context only, not ScreenSpot cost)**

- **Opus 4.8 card, Fig 8.12.6.B (A1):** plots average output tokens per OSWorld-Verified task. Read off the chart at max effort: Opus 4.8 about 21,800, Opus 4.7 about 9,000, Opus 4.6 about 6,300, Sonnet 4.6 about 11,200.
- **Opus 5 card, Fig 8.12.3.B:** plots price per OSWorld 2.0 task, about $16-38 for Opus 4.8.
- **OpenAI (O1):** states "~40 minutes per task" for OSWorld 2.0.
- **Use:** these are 100-500-step agent tasks, useful only as an upper bound on thinking volume.

## ScreenSpot-v2: published calls, latency, tokens, cost

| Entry | v2 | Calls/task | Latency | Tokens | Cost | Src |
|---|---|---|---|---|---|---|
| GPT-6 Astra (XPeng run) | 97.88 | n.p. | n.p. | n.p. | n.p. | O8 |
| Qwen-UI-Agent-27B | 97.5 | 1 | n.p. | n.p. | n.p. | Q5 |
| MAI-UI-32B | 96.5 | 1 (no zoom) | n.p. | n.p. | n.p. | P9 |
| OmegaUse-G | 96.3 | n.p. | n.p. | 16,384 img cap (train) | n.p. | V1 |
| UI-Venus-1.5-30B-A3B | 96.2 | 1 | n.p. | n.p. | n.p. | P12 |
| Holo2-235B-A22B | 95.9 | 1 | n.p. | n.p. | n.p. | P5 |
| UI-Venus-1.5-8B | 95.9 | 1 | n.p. | n.p. | n.p. | P12 |
| Qwen3-VL-32B-Instruct | 95.8* | n.p. | n.p. | n.p. | n.p. | V2 |
| VISTA-9B / 35B-A3B | 95.8 | 1, temp 0 | n.p. | n.p. | n.p. | V4 |
| POINTS-GUI-G-8B | 95.7 | 1, greedy | n.p. | <2000x2000 px | n.p. | V5 |
| Self-distill (Qwen3.5-9B) | 95.68 | 1 | n.p. | n.p. | n.p. | V6 |
| VISTA-8B + MVP | 95.6 | m+1 views (m n.p.) | n.p. | n.p. | n.p. | V4, P10 |
| Duvo Eye-1 | 95.05 | 1 | 0.30 s/task | n.p. | n.p. | P14 |
| GTA1-32B | 95.2 | 1 | n.p. | native res | n.p. | V7 |
| GUI-SD | 95.1 | 1 | n.p. | n.p. | n.p. | V9 |
| UI-Venus-7B + UI-Zoomer | 94.9 | 8 samples + 0-1 crop | see note | 16,384 ctx | n.p. | V10 |
| Claude Sonnet 4 (H Co run) | 93.0 | n.p. | n.p. | n.p. | n.p. | A12 |
| OpenAI CUA | 87.9 | n.p. | n.p. | n.p. | n.p. | O7 |
| Claude 3.7 Sonnet | 87.6 | n.p. | n.p. | n.p. | n.p. | A11 |
| OS-Atlas-Base-7B + GPT-4o | 87.1 | 2 (planner) | n.p. | n.p. | n.p. | V12 |
| OS-Atlas-Base-7B | 84.1 | 1 | 1,788 ms (Showdown) | n.p. | n.p. | V12, V11 |
| Phi-Ground 7B-16C-DPO | 83.8 | 1 | 313 ms (Showdown) | 4,161 img tok | n.p. | V11 |
| Phi-Ground + o4-mini planner | 93.4 | 2 | n.p. | n.p. | n.p. | V11 |

\* labelled "ScreenSpot" (v1) in Qwen's own table; see Summary.

**Notes**

- **UI-Zoomer (V10):** published on 4x RTX 4090D with vLLM. A v2 baseline run took 35:47 total (81.84%); the same run with DiMo-GUI took 6:43:07 (77.20%). The paper says cropping everything "nearly doubles inference time (from ~5:50 to ~10:20)", with units not given.
- **Phi-Ground latency (V11 Table 15):** measured on Showdown-click-dev, not v2, with vLLM and hardware not stated: Phi-Ground 313 ms, UGround-v1-7B 209 ms, UI-TARS-7B 237 ms. OS-Atlas 7B 1,788 ms and 4B 1,288 ms were measured with HF transformers. The paper uses params x image tokens as its compute axis because latency "is often influenced by hardware".
- **Claude 3.7 Sonnet:** the 87.6 traces to the UI-TARS README (A11), with no method stated. Anthropic's 3.7 card has no ScreenSpot entry.
- **OpenAI CUA:** the 87.9 is from the UI-TARS-1.5 card (O7), with no method stated. OpenAI's CUA page has no ScreenSpot number.

## API prices (read 2026-10-17)

| Model | In $/M | Out $/M | Notes | Src |
|---|---|---|---|---|
| GPT-6 Astra | 10 | 50 | >272K: 20 / 75; batch half | O3 |
| GPT-5.6 Sol | 4 | 20 | >272K: 8 / 30; promo pricing | O3 |
| GPT-5.4 | 2.50 | 15 | >272K: 5 / 22.50 | O3 |
| GPT-5.2 | 1.75 | 14 | | O3 |
| computer-use-preview (CUA) | 3 | 12 | 8,192 ctx, 1,024 max out | O6 |
| Claude Mythos 5 | 10 | 50 | limited availability (Glasswing) | A5, A3 |
| Claude Mythos Preview | 25 | 125 | partners only, deprecated Jun 9 2026 | A8, A9 |
| Claude Opus 4.8 / 4.7 / 4.6 | 5 | 25 | | A5 |
| Claude Sonnet 4.6 / Sonnet 4 | 3 | 15 | Sonnet 4 retired except Bedrock/GCP | A5 |
| Claude 3.7 Sonnet | 3 | 15 | launch price; retired Feb 19 2026 | A10, A9 |
| Gemini 3.1 Pro | 2 | 12 | >200K: 4 / 18 | G3 |
| Gemini 3 Flash | 0.50 | 3 | flat | G3 |
| Gemini 3 Pro | n/a | n/a | shut down Mar 9 2026, not listed | G5 |
| Qwen3.8-Max | 2 | 6 | same price thinking or not | Q3 |
| Qwen3.7-Plus | 0.40 | 1.60 | <=256K list price, 20% promo now | Q3 |
| Muse Spark 1.1-1.3 | 1.25 | 4.25 | original Apr 2026 model not listed | M3 |
| Seed 2.1 Pro | 6 CNY | 30 CNY | Volcengine, 0-1024K input | B1 |
| Jev 1.14 (ours) | 0.042 | see note | OpenRouter | REPORT.md |

**Billing notes**

- **Thinking and reasoning tokens bill as output:** OpenAI "are billed as output tokens" (O5). Anthropic "billed as output tokens", for the full internal thinking, not the summary (A7). Gemini includes thinking in the output price (G3). Qwen: "the model's thought process is also counted as output tokens" (Q3). Meta: "at the same rate as visible output tokens" (M3).
- **Python tool runs on OpenAI:** Code Interpreter containers bill separately at $0.03 per 1 GB per 20-minute session (O3).
- **Not verified:** Gemini 3 Pro's old price ($2 / $12) appears only on a third-party page. The Seed 2.1 USD price was not obtained. Jev's output price was not re-read for this file.

## How each provider counts image tokens

| Provider / mode | Documented rule (short) | Src |
|---|---|---|
| Anthropic, all models | ceil(w/28) x ceil(h/28) visual tokens | A6 |
| Anthropic 4.7+ and Mythos 5 | max 2,576 px long edge, 4,784 tokens | A6, A3 |
| Anthropic other models | max 1,568 px long edge, 1,568 tokens | A6 |
| OpenAI GPT-5.x / 6 | 32 px patches, then x1.2 | O4 |
| OpenAI Astra "high" | cap 2,500 patches | O4 |
| OpenAI 5.6 / 5.4 "high" | fit 2048 px and 2,500 patches | O4 |
| OpenAI 5.2, any detail | 2048 px max, 6,144 patches | O4 |
| OpenAI "original" | native size (5.4: 6000 px, 10,000 patches) | O4 |
| OpenAI CUA | not documented | O4 |
| Gemini 3 media_resolution | max/image: 280, 560, 1120, 2240 | G4 |
| Qwen (Model Studio) | 32x32 px per token, +2; default 2,560 cap | Q4 |
| Qwen high-res flag | cap 16,384 tokens | Q4 |
| Seed 2.0+ "high" | fixed 1,280 tokens per image | B2 |
| Seed "xhigh" | 1,280-5,120 tok for 2.26M-9.03M px | B2 |
| Meta Muse Spark | "~1280px image adds ~1,300-1,500 tokens" | M4 |

- **Gemini levels (G4):** the four caps are low, medium, high (the default) and ultra_high. "extra_high", used for the 72.7, is not documented.
- **Anthropic resize (A6):** the doc's own example: "a 1920x1080 screenshot resizes to 1456x819, not 1568x882".
- **Anthropic computer use (A6):** oversized tool_result images are rejected, not downscaled.

## Open-weight models: parameters and hosted prices

Hosted prices read 2026-10-17 (OpenRouter API at 07:20 UTC). "Base" = price of the base model, not the grounder itself.

| Model | Total params | Active | Base model | Hosted $/M in / out | Src |
|---|---|---|---|---|---|
| Indeed-UI-32B | 33.36B | dense | GUI-Owl 1.5 (Qwen3-VL-32B) | none found | P1, P2 |
| Indeed-UI-8B | n.p. (17.5 GB bf16) | dense | GUI-Owl 1.5 8B | none found | P1 |
| KV-Ground-8B | 8.77B | dense | GUI-Owl-1.5-8B | none found | P3 |
| Qwen-UI-Agent-27B | n.p. (27B class) | dense | Qwen3.5-27B | base 0.195 / 1.56 | Q5, P17 |
| Qwen-UI-Agent-35B-A3B | n.p. (35B class) | 3B | not named | base 3.5-35B-A3B: 0.065-0.14 in | Q5, P17 |
| Holo2-235B-A22B | 235.67B | 22B | Qwen3-VL-235B-Thinking | base 0.45 / 3.49 | P5, P18 |
| Holo2-30B-A3B | 31.07B | 3B | Qwen3-VL-30B-Thinking | base 0.29 / 0.99 | P5, P18 |
| Holo3-122B-A10B | 122B | 10B | n.p. | H API 0.40 / 3.00 | P6, P8 |
| Holo3.1-35B-A3B | 35.11B | 3B | Qwen3.5 / 3.6-35B-A3B | H API 0.25 / 1.80 | P7, P8 |
| Holo4 27B / 35B-A3B | 27B / 35B | 3B (MoE) | n.p. | H API 0.40/3.00, 0.30/2.00 | P8 |
| MAI-UI-32B | n.p. (not on HF) | dense | Qwen3-VL | none found | P9 |
| MAI-UI-8B | 8.77B | dense | Qwen3-VL-8B | none found | P9 |
| UI-Venus-2-27B / 9B | 27B class / 9B class | dense | Qwen3.6-27B / Qwen3.5-9B | base 0.25/2.00, 0.10/0.15 | P11, P17 |
| UI-Venus-1.5-30B-A3B | 31.07B | 3B | Qwen3-VL-30B-A3B | base 0.15 / 0.60 | P12, P17 |
| GUI-Owl-1.5-32B | 33.36B | dense | Qwen3-VL-32B | none found | P13 |
| Duvo Eye-1 | 35.11B + LoRA | ~3B | Holo3.1-35B-A3B | base H API 0.25 / 1.80 | P14, P8 |
| GroundAnything | 4.84B | dense | MoonViT-V2 + Qwen3-4B | none found | O8 |
| Fara1.5-27B | 27.36B | dense | Qwen3.5-27B | base 0.195 / 1.56 | P16, P17 |
| OmegaUse-G | 30B | 3B | not named | none found | V1 |
| VISTA-9B | 9.41B | dense | Qwen3.5-9B | base 0.10 / 0.15 | V4, P18 |
| VISTA-35B-A3B | n.p. | 3B | Qwen3.5-35B-A3B | base 0.14 / 1.00 | V4, P18 |
| POINTS-GUI-G-8B | 8.91B | dense | POINTS-1.5, Qwen3-8B | none found | V5 |
| Qwen3-VL-32B | 33.36B | dense | | none with endpoints | P17 |
| Qwen3-VL-8B-Instruct | 8.77B | dense | | 0.18 / 0.69 (DeepInfra) | P18 |
| GTA1-32B | 33.45B | dense | OpenCUA-32B | none found | V7 |
| Phi-Ground 7B | 7B | dense | Phi-4-MM variant | base 0.05 / 0.10 | V11, P18 |
| OS-Atlas-Base-7B | 8.29B | dense | Qwen2-VL-7B | none found | V12 |
| UGround-V1-7B | 8.29B | dense | Qwen2-VL-7B | none found | V13 |

- **Holo3 (P6):** "10B active parameters (122B total)". H Company's API (P8) has a rate-limited free tier and no longer lists Holo3-35B-A3B. Holo2 is not on it.
- **Qwen3.5-27B base prices (P17):** OpenRouter's cheapest provider is Alibaba at $0.195 / $1.56. Model Studio Singapore lists $0.30 / $2.40.
- **Qwen3-VL-32B (P17):** OpenRouter has a page but `"endpoints":[]`. Aggregator claims of $0.10 / $0.42 could not be verified.
- **Fireworks (V16):** publishes a generic size-tier rule for unlisted models: 4-16B $0.20, MoE up to 56B $0.50, dense over 16B $0.90 per M. That is not a listing for any model here.
- **Other unlisted bases:** UI-TARS-1.5-7B is hosted at $0.10 / $0.20. Qwen2.5-VL-72B is $0.80 / $1.00 on Parasail.

## Estimates (computed here, not published)

**Assumptions**

1. **Image sizes.** API rows use the provider's own documented image rule at the named size: 1568x882 for v2, 3840x2160 for Pro. Most Pro screenshots are 2K to 4K, so 4K is the high case.
2. **Qwen-family visual tokens.** Open-weight rows use 32x32 px per visual token (the Qwen3-VL / 3.5 processors, patch 16, merge 2) applied to the real image sizes in Duvo's public prediction files: Pro mean 5,711 visual tokens, v2 mean 2,699. Add ~350 prompt tokens (the Indeed system prompt is 1,381 characters / 4) and 20 output tokens.
3. **No thinking or tool-call tokens** are included anywhere, because none are published. Every API row is therefore a floor, image input only. The "+1K think" column shows what each 1,000 output or thinking tokens adds.
4. **Not checked against a tokenizer.** The OpenAI patch arithmetic reproduces the doc's own examples (1024x1024 gives 1,229; 2048x2048 gives 3,000). The Anthropic rows come from running Anthropic's published resize rule locally, which matches the doc table.
5. **Ratio to Jev** uses Jev's Pro estimate of $0.000158 per call and its measured v2 $0.00015.

### Pro, per task, floor

| Entry | Arithmetic (image tokens x price) | Floor $/task | +1K think | x Jev |
|---|---|---|---|---|
| GPT-6 Astra, high | 2,931 x $10/M | $0.0293 | $0.050 | 185x |
| GPT-6 Astra, original | 9,792 x $10/M | $0.0979 | $0.050 | 620x |
| Claude Mythos 5 | 4,784 x $10/M | $0.0478 | $0.050 | 303x |
| Claude Mythos Preview | 1,560 x $25/M | $0.0390 | $0.125 | 247x |
| Claude Opus 4.8 / 4.7 | 4,784 x $5/M | $0.0239 | $0.025 | 151x |
| Claude Opus 4.6 | 1,560 x $5/M | $0.0078 | $0.025 | 49x |
| Claude Sonnet 4.6 | 1,560 x $3/M | $0.0047 | $0.015 | 30x |
| GPT-5.6 Sol, high | 2,765 x $4/M | $0.0111 | $0.020 | 70x |
| GPT-5.4, high | 2,765 x $2.50/M | $0.0069 | $0.015 | 44x |
| GPT-5.4, original | 9,792 x $2.50/M | $0.0245 | $0.015 | 155x |
| GPT-5.2 | 2,765 x $1.75/M | $0.0048 | $0.014 | 31x |
| Qwen3.8-Max, default | 2,481 x $2/M | $0.0050 | $0.006 | 31x |
| Qwen3.8-Max, high-res | 8,162 x $2/M | $0.0163 | $0.006 | 103x |
| Gemini 3.1 Pro, ultra_high | <=2,240 x $2/M | <=$0.0045 | $0.012 | 28x |
| Gemini 3 Flash, ultra_high | <=2,240 x $0.50/M | <=$0.0011 | $0.003 | 7x |
| Qwen3.7-Plus zoom, 2 calls | 2 x 2,481 x $0.40/M | $0.0020 | $0.0016 | 13x |
| Holo3-122B (H API), 1 call | 6,061 x 0.40 + 20 x 3.00, /1M | $0.0025 | n/a | 16x |
| Holo3.1 / Duvo base (H API) | 6,061 x 0.25 + 20 x 1.80, /1M | $0.00155 | n/a | 9.8x |
| Qwen-UI-Agent-27B zoom (base) | 2 x (6,061 x 0.195 + 20 x 1.56)/1M | $0.0024 | n/a | 15x |
| Qwen-UI-Agent-27B single (base) | 6,061 x 0.195 + 20 x 1.56, /1M | $0.0012 | n/a | 7.7x |
| GroundCascade, tokens only | 2.574 x 6,061 | 15,601 tok | n/a | n/a |
| KV-Ground + Qwen router, tokens | 4 x 6,061 | 24,244 tok | n/a | n/a |
| Jev raw / zoom (ours) | $0.25 / 1,581 per stage | $0.000158 / $0.00032 | n/a | 1x / 2x |

- **Tool runs:** for Mythos, Opus 4.8, GPT-5.2, GPT-5.4 and Muse Spark, each crop sent back adds roughly one more image, and max-effort thinking adds output tokens at the rate shown. A hypothetical 5,000 thinking tokens on Opus 4.8 adds 5 x $0.025 = $0.125 per task, about 6x its image floor.
- **GroundCascade cost:** cannot be priced. No hosted Indeed-UI or KV-Ground endpoint exists, and how calls split between the 32B and the 8B is not published. At Fireworks' generic dense-over-16B tier ($0.90/M), a hypothetical 15,601 x $0.90/M would be $0.014 per task.
- **Muse Spark and Seed 2.1 Pro:** not priced at 4K. Meta publishes no formula beyond ~1,280 px, and Seed is CNY-only. For reference, Seed "high" at 1,280 tokens x 6 CNY/M = 0.0077 CNY per image.

### v2, per task, floor

| Entry | Arithmetic | Floor $/task | x Jev |
|---|---|---|---|
| GPT-6 Astra (97.88) | 1,647 x $10/M | $0.0165 | 110x |
| Claude Sonnet 4 / 3.7 (93.0 / 87.6) | 1,560 x $3/M | $0.0047 | 31x |
| Holo2-235B base, Thinking (95.9) | 3,049 x 0.45 + 20 x 3.49, /1M | $0.0014 | 9.6x |
| Holo3.1 / Duvo Eye-1 via H API (95.05) | 3,049 x 0.25 + 20 x 1.80, /1M | $0.00080 | 5.3x |
| Qwen3-VL-235B-Instruct base | 3,049 x 0.20 + 20 x 0.88, /1M | $0.00063 | 4.2x |
| Qwen3-VL-8B (DeepInfra) | 3,049 x 0.18 + 20 x 0.69, /1M | $0.00056 | 3.8x |
| UI-Venus-1.5-30B-A3B base (96.2) | 3,049 x 0.15 + 20 x 0.60, /1M | $0.00047 | 3.1x |
| VISTA-35B-A3B base (95.8) | 3,049 x 0.14 + 20 x 1.00, /1M | $0.00045 | 3.0x |
| VISTA-9B / self-distill base (95.8) | 3,049 x 0.10 + 20 x 0.15, /1M | $0.00031 | 2.1x |
| Phi-Ground base, image only (83.8) | 4,161 x $0.05/M | $0.00021 | 1.4x |
| Jev raw / zoom (ours) | measured | $0.00015 / $0.0003 | 1x / 2x |

- **UI-Zoomer time (derived from published wall times, V10):** about 1.69 s per task without DiMo-GUI (2,147 s / 1,272) and 19.0 s with it (24,187 s / 1,272), on 4x RTX 4090D. This assumes the run covered all 1,272 v2 tasks.
- **UI-Zoomer calls:** 8 samples + 0 or 1 crop pass = 8 to 9 calls per task.
- **Holo2-235B:** a thinking base model, so every 1,000 thinking tokens adds $0.0035.
- **Base-model rows:** these use the base model's price. The fine-tuned grounders themselves have no hosted price.

## Entries where nothing (or almost nothing) was found

Beyond price, parameter count and setup:

- **Frontier models, nothing published:** latency, tokens, tool-call count and cost for every frontier model on both benchmarks. That covers GPT-6 Astra, GPT-5.6 Sol, GPT-5.2, GPT-5.4, Claude Mythos Preview, Mythos 5, Opus 4.8 / 4.7 / 4.6, Sonnet 4.6, Gemini 3 Pro / 3.1 Pro / 3 Flash, Qwen3.8-Max, Qwen3.7-Plus, Muse Spark and Seed 2.1 Pro.
- **Settings not stated:**
  - Qwen3.8-Max: effort and tools not stated.
  - GPT-6 Astra's 92.7: effort not stated ("maximum at any effort").
  - Qwen3.7-Plus: the zoom procedure is not described.
  - Seed 2.1 Pro: no ByteDance ScreenSpot-Pro number at all (only Qwen's re-run).
- **GroundCascade:** no paper or repo. Only the leaderboard description, which gives the call count and nothing else.
- **Holo3, Holo3.1, Holo4:** the grounding setup (steps, thinking) is not stated.
- **OmegaUse-G:** inference calls and weights not published; base model not named.
- **Qwen-UI-Agent:** zoom procedure, weights and latency not published.
- **No weights on Hugging Face:** MAI-UI-32B, UI-Venus-2-27B, Qwen-UI-Agent.
- **No hosted endpoint for any fine-tuned grounder** except H Company's own Holo3 / Holo3.1 / Holo4.
- **Claude 3.7 Sonnet (v2 87.6) and OpenAI CUA (v2 87.9):** method, resolution and calls not published. CUA's image token rule is not documented.
- **Gemini-3-Pro 93.7 on v2:** no primary source found.
- **Older multi-call setups:** VISTA's MVP view count is not published, and OS-Atlas has no latency on v2 itself.

## Sources (all read 2026-10-17)

**Anthropic**

- A1 Opus 4.8 system card, §8.12.5 p.220, Fig 8.12.6.B p.222: https://www-cdn.anthropic.com/0b4915911bb0d19eca5b5ee635c80fef830a37ea.pdf
- A2 Opus 4.7 system card, §8.9 p.202, §8.9.3 pp.205-206: https://www-cdn.anthropic.com/037f06850df7fbe871e206dad004c3db5fd50340/Claude%20Opus%204.7%20System%20Card.pdf
- A3 Fable 5 / Mythos 5 system card, §8.16.9 pp.288-289, §1 p.11: https://anthropic.com/claude-fable-5-mythos-5-system-card
- A4 Mythos Preview system card, §6.11.2 p.196: https://www.anthropic.com/claude-mythos-preview-system-card
- A5 Pricing: https://platform.claude.com/docs/en/about-claude/pricing
- A6 Vision, resolution and token cost: https://platform.claude.com/docs/en/build-with-claude/vision
- A7 Thinking cost: https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost
- A8 Glasswing ($25 / $125): https://www.anthropic.com/glasswing
- A9 Deprecations: https://platform.claude.com/docs/en/about-claude/model-deprecations
- A10 Claude 3.7 Sonnet launch: https://www.anthropic.com/news/claude-3-7-sonnet
- A11 UI-TARS README (Claude 3.7 v2 87.6): https://github.com/bytedance/UI-TARS
- A12 Holo1.5-72B card, Table 1 (Sonnet 4, in-house): https://huggingface.co/Hcompany/Holo1.5-72B
- A13 Sonnet 4.6 system card (no ScreenSpot entry): https://www-cdn.anthropic.com/78073f739564e986ff3e28522761a7a0b4484f84.pdf

**OpenAI**

openai.com returned 403, so O1, O2 and the CUA page were read via the Wayback Machine.

- O1 GPT-6 Astra: https://openai.com/index/gpt-6-astra/ (snapshot web.archive.org/web/20261015182235/)
- O2 GPT-5.2: https://openai.com/index/introducing-gpt-5-2/ (snapshot web.archive.org/web/20261009110458/)
- O3 Pricing: https://developers.openai.com/api/docs/pricing
- O4 Images and vision: https://developers.openai.com/api/docs/guides/images-vision
- O5 Reasoning: https://developers.openai.com/api/docs/guides/reasoning
- O6 computer-use-preview: https://developers.openai.com/api/docs/models/computer-use-preview
- O7 UI-TARS-1.5-7B card (CUA v2 87.9, Pro 23.4): https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B
- O8 GroundAnything, Table 2, Table 9, Table 27: https://arxiv.org/abs/2609.39600

**Google**

- G1 Gemini 3 Pro eval, p.3: https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_model_evaluation.pdf
- G2 Gemini 3 Flash eval: https://storage.googleapis.com/deepmind-media/gemini/gemini_3_flash_model_evaluation.pdf
- G3 Pricing: https://ai.google.dev/gemini-api/docs/pricing
- G4 Media resolution: https://ai.google.dev/gemini-api/docs/media-resolution
- G5 Deprecations: https://ai.google.dev/gemini-api/docs/deprecations

**Qwen**

- Q1 Qwen3.8 blog, footnote 8: https://qwen.ai/blog?id=qwen3.8 (read via qwen.ai/api/v2/article/)
- Q2 Qwen3.7-Plus blog: https://qwen.ai/blog?id=qwen3.7-plus
- Q3 Model Studio pricing (page updated Oct 15 2026): https://www.alibabacloud.com/help/en/model-studio/model-pricing
- Q4 Model Studio vision: https://www.alibabacloud.com/help/en/model-studio/vision
- Q5 Qwen-UI-Agent, Table 8: https://arxiv.org/abs/2607.28227

**Meta and ByteDance**

- M1 Muse Spark (chart image): https://ai.meta.com/blog/introducing-muse-spark-msl/
- M2 Muse Spark methodology: https://ai.meta.com/static-resource/muse-spark-eval-methodology
- M3 Meta API pricing: https://dev.meta.ai/docs/pricing-rate-limits
- M4 Meta image understanding: https://dev.meta.ai/docs/image-understanding
- B1 Volcengine pricing (page updated 2026-10-10): https://www.volcengine.com/docs/82379/1544106
- B2 Volcengine image understanding: https://www.volcengine.com/docs/82379/1362931

**Open-weight models and leaderboard**

- L1 Official leaderboard: https://gui-agent.github.io/grounding-leaderboard/ (repo GUI-Agent/grounding-leaderboard, commit fd896b54)
- P1 Indeed-UI repo (README, eval_sspro_zoomin_hf_dp.py): https://github.com/intelligence-indeed/Indeed-UI
- P2 Indeed-UI-32B: https://huggingface.co/intelligence-indeed/Indeed-UI-32B
- P3 KV-Ground-8B: https://huggingface.co/vocaela/KV-Ground-8B-BaseGuiOwl1.5-0315
- P4 Zoom-consistency routing (README, arxiv/main.tex): https://github.com/omxyz/zoom-consistency-routing
- P5 Holo2 cards: https://huggingface.co/Hcompany/Holo2-235B-A22B (and /Holo2-30B-A3B, /Holo2-8B)
- P6 Holo3: https://hcompany.ai/newsroom/holo3
- P7 Holo3.1: https://huggingface.co/blog/Hcompany/holo31 and https://huggingface.co/Hcompany/Holo-3.1-35B-A3B
- P8 H Company API pricing: https://hcompany.ai/holo-models-api
- P9 MAI-UI: https://arxiv.org/abs/2512.22047
- P10 MVP: https://arxiv.org/abs/2512.08529
- P11 UI-Venus-2: https://arxiv.org/abs/2609.00028
- P12 UI-Venus-1.5: https://arxiv.org/abs/2602.09082
- P13 GUI-Owl-1.5: https://arxiv.org/abs/2602.16855
- P14 Duvo Eye-1 evals: https://huggingface.co/datasets/duvoai/duvo-eye-1-evals and https://huggingface.co/duvoai/duvo-eye-1.5
- P15 AdaZoom-GUI: https://arxiv.org/abs/2603.17441
- P16 Fara1.5: https://arxiv.org/abs/2606.20785 and https://huggingface.co/microsoft/Fara1.5-27B
- P17 OpenRouter models and endpoints: https://openrouter.ai/api/v1/models
- P18 DeepInfra price list: https://api.deepinfra.com/models/list

**ScreenSpot-v2 papers and other prices**

- V1 OmegaUse: https://arxiv.org/abs/2601.20380
- V2 Qwen3-VL card table: https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3-VL/qwen3vl_2b_32b_vl_instruct.jpg
- V3 Qwen3-VL tech report, §5.10: https://arxiv.org/abs/2511.21631
- V4 VISTA: https://arxiv.org/abs/2606.14579 and https://huggingface.co/inclusionAI/VISTA-9B
- V5 POINTS-GUI-G: https://arxiv.org/abs/2602.06391 and https://huggingface.co/tencent/POINTS-GUI-G
- V6 Quality-aware self-distillation: https://arxiv.org/abs/2606.18101
- V7 GTA1: https://arxiv.org/abs/2507.05791 and https://huggingface.co/HelloKKMe/GTA1-32B
- V8 Step-GUI: https://arxiv.org/abs/2512.15431
- V9 GUI-SD: https://arxiv.org/abs/2605.00642
- V10 UI-Zoomer, Table 1: https://arxiv.org/abs/2604.14113
- V11 Phi-Ground, Tables 9, 10, 15: https://arxiv.org/abs/2507.23779
- V12 OS-Atlas, Table 8: https://arxiv.org/abs/2410.23218
- V13 UGround: https://github.com/OSU-NLP-Group/UGround
- V14 GUI-Eyes: https://arxiv.org/abs/2601.09770
- V15 Together pricing: https://www.together.ai/pricing
- V16 Fireworks pricing: https://docs.fireworks.ai/serverless/pricing
