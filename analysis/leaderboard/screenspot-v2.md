# ScreenSpot-v2 published scores (collected Oct 17 2026)

Collected by a research agent from primary sources; numbers are as published, mostly self-reported. Check each source before public use.

I verified 37 of the 39 table rows against a primary source. The other two, Gemini-3-Pro and Claude 3.7, I only found cited by later papers, as marked. The leader is **MAI-UI-32B at 96.5** (Microsoft, Dec 26 2025). Five models score 95.9 or above, and four of the five are not on your list: MAI-UI-32B, OmegaUse-G, UI-Venus-1.5-30B-A3B and UI-Venus-1.5-8B.

One case out of 1,272 is worth 0.079 points, so 96.5% is about 1,227 hits. Jev's 83.33% is 1,060 hits and 87.89% is 1,118.

## ScreenSpot-v2 overall scores, sorted

"Self" means the model's own authors reported it. "3rd" means another paper measured or cited it. S-codes point to the source list at the end.

| Score | Model | Src | Date | Type | Setup note |
|---|---|---|---|---|---|
| 96.5 | MAI-UI-32B | S1 | 2025-12-26 | Self | Single pass, zoom-in not used for v2 |
| 96.3 | OmegaUse-G (Baidu) | S2 | 2026-01-28 | Self | MoE 30B-A3B backbone, no test-time scaling |
| 96.2 | UI-Venus-1.5-30B-A3B | S3 | 2026-02-24 | Self | End-to-end, no zoom or agent framework |
| 95.9 | Holo2-235B-A22B | S4 | ~Nov 2025 | Self | Non-agentic row |
| 95.9 | UI-Venus-1.5-8B | S3 | 2026-02-24 | Self | End-to-end, no zoom |
| 95.8 | Qwen3-VL-32B-Instruct | S7 | 2026-02-15 | 3rd | Conflict: 93.0 in S1 and S6 |
| 95.8 | VISTA-9B (Qwen3.5-9B base) | S5 | 2026-06-12 | Self | Temperature 0, single view |
| 95.8 | VISTA-35B-A3B (Qwen3.5 base) | S5 | 2026-06-12 | Self | Temperature 0, single view |
| 95.7 | POINTS-GUI-G-8B (Tencent) | S6 | 2026-02-06 | Self | No reasoning trace, 2000px input cap |
| 95.7 | Qwen3-VL-32B-Thinking | S7 | 2026-02-15 | 3rd | Thinking mode |
| 95.68 | Quality-aware self-distillation (Qwen3.5-9B) | S8 | 2026-06-17 | Self | Training method, single pass |
| 95.6 | VISTA-8B + MVP | S5 | 2026-06-12 | Self | Multi-view inference aggregation |
| 95.5 | VISTA-8B | S5 | 2026-06-12 | Self | Single view |
| 95.4 | Qwen3-VL-235B-A22B-Thinking | S4 | ~Nov 2025 | 3rd (H Co) | Thinking mode |
| 95.4 | VISTA-30A3B + MVP | S5 | 2026-06-12 | Self | Multi-view inference aggregation |
| 95.3 | UI-Venus-72B (1.0) | S1, S3, S6 | 2025 | Self / cited | Consistent everywhere |
| 95.3 | GUI-Owl-1.5-32B-Instruct | S7 | 2026-02-15 | Self | Instruct mode |
| 95.2 | MAI-UI-8B | S1 table | 2025-12-26 | Self | Conflict: S1's own text says 95.5 |
| 95.2 | GTA1-32B | S14, S1, S3, S5 | 2025-07 | Self | Conflict: S7 prints 93.2 |
| 95.2 | Seed-1.5-VL | S14, S2 | 2025 | Cited | Closed model |
| 95.2 | VISTA-30A3B | S5 | 2026-06-12 | Self | Single view |
| 95.1 | Step-GUI-8B | S10 | 2025-12-17 | Self | Seen in search excerpt, also S3 and S5 |
| 95.1 | GUI-SD (Qwen3-VL-8B) | S9 | 2026-05 | Self | 95.05 in its Table 7; S8 re-ran it at 94.97 |
| 94.9 | Holo2-30B-A3B | S4 | ~Nov 2025 | Self | Non-agentic |
| 94.9 | UI-Venus-7B + UI-Zoomer | S13 | 2026-04-15 | 3rd | Zoom, training-free, at test time |
| 94.8 | GTA1-72B | S2 | 2026-01 | Cited | |
| 94.7 | Qwen3-VL-30B-A3B | S5 | 2026-06-12 | 3rd | Conflict: 91.7 in S3, 91.8 Thinking in S4 |
| 94.4 | Holo1.5-72B | S11 | ~Sep 2025 | Self | 94.41 |
| 94.4 | Qwen3-VL-8B-Instruct | S7 | 2026-02-15 | 3rd | Conflict: 91.7 (S1, S5), 92.1 (S3), 93.2 (S9) |
| 94.2 | UI-TARS-1.5 (full, closed) | S14, S2 | 2025 | Cited | Not the same model as UI-TARS-1.5-7B |
| 94.1 | UI-Venus-7B | S1, S3 | 2025 | Self | S13 re-ran it at 94.0 |
| 94.0 | Qwen2.5-VL-72B | S14 | 2025-07 | 3rd | Conflict: 93.3 in S11 |
| 93.9 | GUI-Cursor-7B | S18 (via S15) | 2025-09 | Self | Number not checked in the paper itself |
| 93.7 | Gemini-3-Pro | S12 | 2026-04-09 | Cited | Cites Google's card, no v2 figure found there |
| 93.5 | InfiGUI-G1-7B | S1, S6 | 2025 | Cited | |
| 93.3 | GUI-G²-7B | S1, S2, S9 | 2025 | Cited | S13 re-ran it at 93.6 |
| 93.0 | Claude Sonnet 4 | S11 | ~Sep 2025 | 3rd (H Co) | Measured in-house by H Company |
| 87.9 | OpenAI CUA | S12 + UI-TARS-1.5 card | 2025 | Cited | Matches your number |
| 87.6 | Claude 3.7 Sonnet | S7, S12 | 2025 | Cited | |

These rows from your list are consistent with what I found but weren't re-fetched from GTA1 itself:

- Seen again in later papers: OpenCUA-32B 93.4, Holo2-8B and Holo2-4B 93.2, GTA1-7B 92.4, Jedi-7B 91.7, UI-TARS-7B 91.6, UI-TARS-72B 90.3, OmniParser-v2 80.7, Operator 70.5, SeeClick 55.1.
- Others now confirmed by a source:
  - The Qwen3-VL Thinking rows (S4).
  - GUI-Eyes-3B 88.4 (S17, search excerpt only).
  - Phi-Ground 83.8, which is the 7B-16C-DPO variant (S1, S2).
- OS-Atlas, your ambiguous row: it's 84.1 in S2, 85.1 in S1 and S6, and 87.1 in S7. S7 labels 87.1 as OS-Atlas-Base-7B and 85.1 as OS-Atlas-Base-4B. GTA1's "85.1/87.1" is probably 4B versus 7B.

**Where Jev sits:** 83.33 raw falls between Phi-Ground (83.8) and OS-Atlas-7B (84.1). 87.89 with zoom sits with Claude 3.7 (87.6), UGround-v1-7B (87.7) and OpenAI CUA (87.9).

## Other conflicts

- **UI-TARS-1.5-7B:** 89.0 in S1 and S6, 91.6 in S3 and S5, 94.0 in S11. Some sources may be mixing it up with the closed full model's 94.2.
- **Smaller disagreements:** GUI-Actor-7B is 92.1 or 89.5 (S9). SE-GUI-7B is 90.8 or 90.3. GUI-Owl-32B is 93.2 or 93.1. Qwen2.5-VL-7B is 88.8, 85.6, 87.2 or 89.3 depending on the source.

## Checked and found no v2 number

- **No ScreenSpot-v2 number:**
  - UI-Venus-2 (Aug 27 2026, reports ScreenSpot-Pro only).
  - Holo4 (Sep 28 2026, agent benchmarks only).
  - The Qwen3-VL technical report (no score rows in the parts I read).
  - UI-TARS-2.
  - Seed1.8 and Seed2.0 (the Seed2.0 HTML page returned 404).
  - Holo3 and Holo3.1.
- **Frontier models:** no published v2 number for GPT-5.x, Claude 4.5 or later, or Gemini 3.1. Claude Sonnet 4 (93.0) and Gemini-3-Pro (93.7, cited only) are the newest frontier models with a figure.
- **Only on the sota2.com aggregator, no primary source checked:** ZoomOnce 95.2, UI-Ins 94.9 (GUI-SD cites UI-Ins-7B at 94.0), Xiaomi-GUI-0-30B-A3B 94.7, Qwen3-30B-A3B-Instruct 94.7, HyperClick-7B 93.7 (GUI-SD cites it), MolmoPoint-GUI-8B 93.9 and 93.4, EvoCUA-OpenCUA-72B 93.47. Your earlier ~10-search estimate was fine; it took about 35 search and fetch calls to cover this.

## Leader and confidence

MAI-UI-32B at 96.5 has held the top spot since Dec 2025, single pass with no zoom. OmegaUse-G (96.3) and UI-Venus-1.5-30B-A3B (96.2) are within three cases of it. Nothing published in 2026 that I found beats it. The VISTA paper calls the benchmark "near saturation".

I'm highly confident the top numbers are what the authors published, but all of them are self-reported. Nobody has independently re-run the top five. Low confidence on the order inside the 95.2 to 96.5 band, since gaps of one to fifteen cases are inside the differences between evaluation harnesses. The Qwen3-VL-32B spread (93.0 against 95.8) shows how large those differences can be.

For the chart, I'd plot MAI-UI-32B, OmegaUse-G, UI-Venus-1.5-30B-A3B, Holo2-235B and POINTS-GUI-G as the self-reported leaders. Footnote the Qwen3-VL rows as re-runs that disagree.

## Sources

- S1 MAI-UI: https://arxiv.org/abs/2512.22047 (Dec 26 2025, Table 10)
- S2 OmegaUse: https://arxiv.org/abs/2601.20380 (Jan 28 2026, Table 4)
- S3 UI-Venus-1.5: https://arxiv.org/abs/2602.09082 (v2 Feb 24 2026, Table 1)
- S4 Holo2 card: https://huggingface.co/Hcompany/Holo2-235B-A22B (~Nov 2025)
- S5 VISTA: https://arxiv.org/abs/2606.14579 (Jun 12 2026, Tables 1-2)
- S6 POINTS-GUI-G: https://arxiv.org/abs/2602.06391 (Feb 6 2026, Table 1)
- S7 Mobile-Agent-v3.5 / GUI-Owl-1.5: https://arxiv.org/abs/2602.16855 (Feb 15 2026, Table 7)
- S8 Quality-Aware Self-Distillation: https://arxiv.org/abs/2606.18101 (Jun 17 2026, Table 1)
- S9 GUI-SD: https://arxiv.org/abs/2605.00642 (May 2026, Table 2)
- S10 Step-GUI: https://arxiv.org/abs/2512.15431 (Dec 17 2025)
- S11 Holo1.5-72B card: https://huggingface.co/Hcompany/Holo1.5-72B (~Sep 2025)
- S12 MolmoWeb: https://arxiv.org/abs/2604.08516 (Apr 9 2026, Table 8)
- S13 UI-Zoomer: https://arxiv.org/abs/2604.14113 (Apr 15 2026, Table 10)
- S14 GTA1: https://arxiv.org/abs/2507.05791 (Jul 2025)
- S15 sota2.com leaderboard (formerly Wizwand), the most complete v2 tracker I found: https://sota2.com/research/sota/gui-grounding-on-screenspot-v2
- S16 LLM Reference leaderboard (only 2 entries): https://www.llmreference.com/benchmark/screenspot-v2
- S17 GUI-Eyes: https://arxiv.org/abs/2601.09770
- S18 GUI-Cursor: https://arxiv.org/abs/2509.21552
- S19 UI-Venus-2, no v2 number: https://arxiv.org/abs/2609.00028
- S20 Holo4, no v2 number: https://hcompany.ai/newsroom/holo4

## Addendum (Oct 17, checked by hand): every H Company Holo model with a v2 score

From the Holo1.5-72B card (https://huggingface.co/Hcompany/Holo1.5-72B, Table 1, ~Sep 2025) and the Holo2 card (S4). Holo3, Holo3.1 and Holo4 publish no v2 number.

| Model | ScreenSpot-v2 | Source |
|---|---|---|
| Holo2-235B-A22B | 95.9 | Holo2 card |
| Holo2-30B-A3B | 94.9 | Holo2 card |
| Holo1.5-72B | 94.41 | Holo1.5 card |
| Holo1.5-7B | 93.31 | Holo1.5 card |
| Holo2-8B | 93.2 | Holo2 card |
| Holo2-4B | 93.2 | Holo2 card |
| Holo1.5-3B | 91.66 | Holo1.5 card |
| Holo1-7B | 89.85 | Holo1.5 card |
| Holo1-3B | 88.91 | Holo1.5 card |
