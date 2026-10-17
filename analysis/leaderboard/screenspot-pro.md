# ScreenSpot-Pro published scores (collected Oct 17 2026)

Collected by a research agent from primary sources; numbers as published. Check each source before public use. Raw official leaderboard data: official-leaderboard-screenspot_pro.json.

## ScreenSpot-Pro leaderboard, verified as of Oct 17, 2026

**Leader, single-shot (no tools):** GPT-6 Astra at **92.7**. OpenAI self-reported it on Sep 3, 2026, and XPeng's GroundAnything paper re-ran it independently on Sep 30 and got **93.17** (thinking set to High). I'm highly confident in this one: it is the only frontier score that has been checked by a third party. Next come Claude Mythos 5 at 87.3, Qwen3.8-Max at 84.5 (Qwen's own run, setup not stated) and Claude Opus 4.8 at 82.3. The best open-weight grounding models on a single shot are Qwen-UI-Agent-27B (76.6), Indeed-UI (73.3 to 73.4), KV-Ground-8B (73.2), GUI-Owl-1.5-32B (72.9) and Duvo Eye-1 (72.9).

**Leader, with tools, zoom or agentic:** Claude Mythos Preview at **93.0**, using Python tools plus a cropping tool. It is a limited-access model. Among normally available setups, Mythos 5 scores 90.7 and Opus 4.8 scores 87.9, both with Python tools. Without tools, Astra's 92.7 already ties both of these. The best open harnesses are GroundCascade (85.1, an ensemble averaging about 2.57 model calls per sample), Indeed-UI-32B with zoom (82.7) and Qwen-UI-Agent-27B with zoom (81.5). My confidence here is medium-high: the tool setups differ by lab, so the numbers are not strictly comparable.

**The big catch in the list you collected:** llm-stats and BenchLM put different setups in one column. Astra's 92.7 is **no tools**. Opus 4.8's 87.9, GPT-5.2's 86.3, GPT-5.4's 85.4, Muse Spark's 84.1 and Gemini 3.1 Pro's 84.4 are all **with Python**. Gemini 3 Pro's 72.7 uses a screenshot-capture tool at "extra_high" resolution. Qwen3.7-Plus's 79.0 turns out to be a **zoom-in** score. For the chart, I'd plot no-tools and tools as separate series.

### Table

"Self" means the model's own team published the number; "3P" means someone else ran the model. Source keys are listed at the end.

| Score | Model | Setup | Type | Date | Src |
|---|---|---|---|---|---|
| 93.17 | GPT-6 Astra | Thinking High, direct | 3P (XPeng) | 2026-09-30 | S10 |
| 93.0 | Claude Mythos Preview | Python + crop tool, max effort | Self (re-eval) | 2026-06-09 | S4 |
| 92.8 | Claude Mythos Preview | Python tools, max effort | Self (original) | 2026-04-07 | S5 |
| 92.7 | GPT-6 Astra | No tools | Self | 2026-09-03 | S1 |
| 90.7 | Claude Mythos 5 | Python + crop tool, max effort | Self | 2026-06-09 | S4 |
| 87.9 | Claude Opus 4.8 | Python tools, adaptive max, 5 runs | Self | 2026-05-28 | S2 |
| 87.6 | Claude Opus 4.7 | Python tools, adaptive max | Self | 2026-04-16 | S3 |
| 87.3 | Claude Mythos 5 | No tools, max effort | Self | 2026-06-09 | S4 |
| 86.3 | GPT-5.2 Thinking | Python tool, xhigh | Self | 2025-12-11 | S6 |
| 85.4 | GPT-5.4 (xhigh) | With Python | Cited by Meta | 2026-04 | S8 |
| 85.1 | GroundCascade (Indeed-32B + KV-8B) | Cascade, 0.5 zoom, ~2.57 calls | Self (LB) | 2026-10-01 | S0 |
| 84.5 | Qwen3.8-Max | Setup not stated, in-house | Self | 2026-08-03 | S11 |
| 84.4 | Gemini 3.1 Pro (High) | With Python | Cited by Meta | 2026-04 | S8 |
| 84.1 | Meta Muse Spark | Thinking, with Python | Self | 2026-04 | S8 |
| 83.1 | Claude Opus 4.6 | Python tools, adaptive max | Self | 2026-04-16 | S3 |
| 82.7 | Indeed-UI-32B | Zoom-in | Self (LB+repo) | 2026-08-13 | S0, S20 |
| 82.4 | Claude Sonnet 4.6 | Python tools | Self | 2026-04-07 | S5 |
| 82.3 | Claude Opus 4.8 | No tools, adaptive max | Self | 2026-05-28 | S2 |
| 81.5 | Qwen-UI-Agent-27B | Zoom-in | Self | 2026-07-31 | S14 |
| 81.3 | GPT-5.6 Sol | Qwen in-house run | 3P (Qwen) | 2026-08-03 | S11 |
| 81.0 | Indeed-UI-8B | Zoom-in | Self (LB) | 2026-09-09 | S0 |
| 80.9 | KV-Ground-8B + Qwen3.5-27B router | 2-step zoom, ensemble | Self (LB) | 2026-04-13 | S0 |
| 80.7 | Seed 2.1 Pro | Zoom-in | 3P (Qwen-UI-Agent) | 2026-07-31 | S14 |
| 80.5 | KV-Ground-8B (GUI-Owl-1.5 base) | Zoom-in | Self (LB+card) | 2026-03-21 | S0, S21 |
| 80.3 | GUI-Owl-1.5-32B-Instruct | Crop/zoom 2-stage | Self | 2026-02-15 | S12 |
| 80.2 | Qwen-UI-Agent-35B-A3B | Zoom-in | Self | 2026-07-31 | S14 |
| 79.5 | Claude Opus 4.7 | No tools | Self | 2026-04-16 | S3 |
| 79.3 | Claude Mythos Preview | No tools (re-eval; was 79.5) | Self | 2026-06-09 | S4 |
| 79.0 | Qwen3.7-Plus | Thinking off; zoom-in per S14 | Self | 2026-06-03 | S13, S14 |
| 78.5 | Holo2-235B-A22B | Agentic, 3 steps | Self | 2025-11 | S15 |
| 77.8 | GUI-Owl-1.5-8B-Instruct | Zoom-in | Self | 2026-02-15 | S14 |
| 77.5 | MAI-UI-32B (MVP) | Multi-crop vote | Self (LB) | 2026-01-28 | S0 |
| 76.9 | GPT-5.6 Sol | No tools | Self | 2026-09-03 | S1 |
| 76.8 | AdaZoom-GUI-4B | Cond. zoom + Qwen3.5-397B refine | Self (LB) | 2026-03-28 | S0 |
| 76.6 | Qwen-UI-Agent-27B | No zoom, single-shot | Self | 2026-07-31 | S14 |
| 76.1 | Qwen-UI-Agent-35B-A3B | No zoom | Self | 2026-07-31 | S14 |
| 76.1 | Qwen3.6-27B | Thinking mode | Cited by Meta | 2026-08 | S9 |
| 75.96 | GroundAnything (XPeng) | Diffusion decoding | Self | 2026-09-30 | S10 |
| 75.9 | Gemma4-31B | Thinking mode | Cited by Meta | 2026-08 | S9 |
| 75.4 | Muse Glimmer-30B | High reasoning | Self | 2026-08 | S9 |
| 75.2 | Holo2-30B-A3B | Agentic | Self | 2025-11 | S15 |
| 74.1 | UI-Venus-2-27B | Single-shot | Self | 2026-08-27 | S16 |
| 73.5 | MAI-UI-32B | Zoom-in | Self | 2025-12-26 | S17 |
| 73.4 | Indeed-UI-8B | Single-shot | Self (LB) | 2026-09-09 | S0 |
| 73.3 | Indeed-UI-32B | Single-shot | Self (LB+repo) | 2026-08-13 | S0, S20 |
| 73.2 | KV-Ground-8B | Single-shot | Self | 2026-03-21 | S21 |
| 73.1 | Seed1.8 | Not stated | Cited by MAI-UI | 2025-12 | S17 |
| 73.0 | UI-Venus-2-9B | Single-shot | Self | 2026-08-27 | S16 |
| 72.9 | GUI-Owl-1.5-32B-Instruct | No crop | Self | 2026-02-15 | S12 |
| 72.9 | Duvo Eye-1 (Holo-3.1-35B + LoRA) | Single-shot, temp 0, no think | Self (LB) | 2026-06-22 | S0 |
| 72.7 | Gemini 3 Pro | Screenshot tool, extra_high res | Self | 2025-11-18 | S7 |
| 72.2 | Holo3-122B-A10B | Not stated | Self | 2026-03-31 | S18 |
| 71.5 | Holo3.1-35B-A3B | Not stated | Self | 2026-06-02 | S19 |
| 71.4 | Holo2-8B | Agentic | Self | 2025-11 | S15 |
| 70.9 | MAI-UI-8B | Zoom-in (LB shows 71.9) | Self | 2025-12-26 | S17 |
| 70.6 | Holo2-235B-A22B | Single-shot | Self | 2025-11 | S15 |
| 70.4 | Qwen3.5-122B-A10B | Not stated (H re-eval: 65.5) | Self | 2026-02-16 | S22 |
| 70.3 | Qwen3.5-27B | Matches S14's zoom number | Self | 2026-02-16 | S22 |
| 69.6 | UI-Venus-1.5-30B-A3B | Single-shot (74.8 with zoom) | Self | 2026-02-09 | S14, S23 |
| 69.3 | Qwen3.5-397B-A17B | H's own run | 3P (H) | 2026-03-31 | S18 |
| 69.1 | Gemini 3 Flash | ultra_high media resolution | Self | 2025-12-17 | S7b |
| 68.9 | Qwen3.7-Plus | No zoom | 3P (Qwen-UI-Agent) | 2026-07-31 | S14 |
| 68.6 | Qwen3.5-35B-A3B | Matches S14's zoom number | Self | 2026-02-16 | S22 |
| 68.4 | UI-Venus-1.5-8B | Single-shot | Self | 2026-02-09 | S23 |
| 68.2 | Qwen3.6-Plus | Not stated | Self | 2026-06-03 | S13 |
| 68.1 | Gemini 3.1 Pro | Qwen's run | 3P (Qwen) | 2026-06-03 | S13 |
| 67.9 | MAI-UI-32B | Single-shot | Self | 2025-12-26 | S17 |
| 67.6 | Holo3-35B-A3B | Not stated | Self | 2026-03-31 | S18 |
| 67.4 | GPT-5.4 (xhigh) | Qwen's run | 3P (Qwen) | 2026-06-03 | S13 |
| 66.8 | Fara1.5-27B | Two-step zoom (58.6 without) | Self | 2026-06-18 | S24 |
| 66.1 | Holo2-30B-A3B | Single-shot | Self | 2025-11 | S15 |
| 65.8 | MAI-UI-8B | Single-shot | Self | 2025-12-26 | S17 |
| 65.6 | Qwen3.5-397B-A17B | Not stated | Self | 2026-02-16 | S22 |
| 65.3 | Seed 2.1 Pro | No zoom | 3P (Qwen-UI-Agent) | 2026-07-31 | S14 |
| 65.0 | Claude Sonnet 4.6 | No tools | Self | 2026-04-07 | S5 |
| 63.9 | GroundGUI-8B | Single-shot | Self | 2026-10-13 | S25 |
| 63.6 | GTA1-32B | Single-shot | Self | 2025-07-08 | S26 |
| 63.3 | Holo1.5-72B | Single-shot | Self (LB) | 2025-09-17 | S0 |
| 62.6 | Step-GUI-8B | Single-shot | Self | 2025-12-17 | S27 |
| 62.0 | Qwen3-VL-235B-A22B-Instruct | Not stated | Self | 2025-11 | S22 |
| 61.9 | UI-Venus-Ground-72B | Single-shot (UI-Zoomer re-eval: 59.2) | Self | 2025-08 | S0, S28 |
| 61.8 | Qwen3-VL-235B-A22B-Thinking | Thinking | Cited by H | 2025-11 | S15 |
| 61.6 | UI-TARS-1.5 | Not stated | Self | 2025-04 | S26 |
| 60.9 | Seed1.5-VL | Thinking | Self | 2025-05 | S26 |
| 59.9 | POINTS-GUI-G-8B | Single-shot | Self | 2026-02-06 | S29 |
| 58.9 | Holo2-8B | Single-shot | Self | 2025-11 | S15 |
| 57.7 | Claude Opus 4.6 | No tools | Self | 2026-04-16 | S3 |
| 57.4 | MAI-UI-2B | Single-shot (62.8 with zoom) | Self | 2025-12-26 | S17 |
| 57.2 | Holo2-4B | Single-shot | Self | 2025-11 | S15 |
| 55.0 | Phi-Ground | Agent setting with planner | Self | 2025-07-31 | S30 |
| 51.9 | InfiGUI-G1-7B | Single-shot | Self | 2025-08-07 | S17 |
| 50.1 | GTA1-7B | Single-shot (LB's later 7B: 55.5) | Self | 2025-07-08 | S26, S0 |
| 47.5 | GUI-G²-7B | Single-shot | Self | 2025-07-21 | S31 |
| 47.3 | SE-GUI-7B | Single-shot (LB: 47.2) | Self | 2025-05 | S26 |
| 45.7 | Claude Opus 4.5 | Not stated | Cited by Qwen | 2026-02-16 | S22 |
| 43.2 | Phi-Ground | End-to-end, single-shot | Self | 2025-07-31 | S30 |
| 36.2 | Claude Sonnet 4.5 | Google API run | 3P (Google) | 2025-11-18 | S22, S7 |
| 28.7 | ZonUI-3B | Single-shot | Self (LB) | 2025-07-01 | S0 |

The older baselines from GTA1's Table 1 that you already had (Qwen2.5-VL-72B 53.3 down to GPT-4o 0.8) match the official leaderboard, apart from small differences: Qwen2.5-VL-32B is 47.6 vs 48.0 and Qwen2.5-VL-7B is 27.6 vs 26.8. ScreenSeekeR (OS-Atlas-7B going from 18.9 to 48.1 with search) comes from the ScreenSpot-Pro paper.

### Conflicts to know about

- **Qwen3.7-Plus 79.0:** this is a zoom-in number. Alibaba's own Qwen-UI-Agent paper lists it as 68.9 without zoom and 79.0 with zoom. The Qwen3.5 card numbers (27B at 70.3, 35B-A3B at 68.6) also match that paper's zoom column exactly, so treat them as zoom-in scores as well.
- **Qwen3.5 re-runs by H Company disagree in both directions:** 397B is 65.6 from Qwen vs 69.3 from H, and 122B is 70.4 from Qwen vs 65.5 from H.
- **GPT-5.4 and Gemini 3.1 Pro:** OpenAI's GPT-5.4 materials show no ScreenSpot-Pro number, and Google's Gemini 3.1 Pro evaluation document has none either. The 85.4 and 84.4 come only from Meta's Muse Spark table, with Python. Qwen's runs give 67.4 and 68.1, probably without tools.
- **GPT-5.6 Sol:** 76.9 in OpenAI's own table vs 81.3 in Qwen's in-house run.
- **Claude Opus 4.6:** 57.7 without tools, 83.1 with tools (Anthropic), and 49.5 in Qwen's run.
- **Gemini 3 Pro:** 72.7 needs a setting that was not in the API at launch. At "high" resolution Google itself reports 60.5.
- **Qwen3.6-27B:** 76.1 in Meta's table vs 65.2 in the UI-Venus-2 team's run.
- **Small leaderboard drifts:** MAI-UI-8B with zoom is 70.9 in its paper vs 71.9 on the official leaderboard (65.8 vs 65.7 single-shot). Mythos Preview without tools moved from 79.5 to 79.3 after Anthropic changed its prompt and re-ran it.
- **Not confirmed:** Kimi-K3 scored 25.36 in GroundAnything, but the authors themselves mark the prompt/protocol as uncertain.

### Coverage gaps

- **The official leaderboard** (gui-agent.github.io) lists overall scores for 99 models. It loads them from `results/screenspot_pro.json`, which I saved locally (the commit history gives a date for each entry). It has almost no frontier API models: only "GPT5-minimal (resized)" at 18.5 and "Claude (Computer Use)" at 17.1.
- **No ScreenSpot-Pro number found for:** UI-TARS-2 (not in its tech report), Claude Opus 5, Opus 5.5, Sonnet 5, Haiku 5.5 and Fable 5.1 (not in their system cards), and Gemini 3.5 to 3.8 Flash.
- **Not found at all:** GUI-Cursor and GUI-Eyes.
- **Read through third-party pages only:** openai.com, qwen.ai and ai.meta.com blocked direct fetches. The GPT-6 Astra, GPT-5.2, Qwen3.8-Max and Muse Spark rows come from search-index snippets of the official pages, or a page quoting Meta's table (jdhodges.com). Every Anthropic, Google, Hugging Face card and arXiv number was read from the primary document.

### Sources

- S0: https://gui-agent.github.io/grounding-leaderboard/ (data: .../results/screenspot_pro.json, updated 2026-10-01)
- S1: https://openai.com/index/gpt-6-astra/
- S2: https://www-cdn.anthropic.com/0b4915911bb0d19eca5b5ee635c80fef830a37ea.pdf (Opus 4.8 system card §8.12.5)
- S3: https://www-cdn.anthropic.com/037f06850df7fbe871e206dad004c3db5fd50340/Claude%20Opus%204.7%20System%20Card.pdf (§8.9.3)
- S4: https://anthropic.com/claude-fable-5-mythos-5-system-card (§8.16.9)
- S5: https://www.anthropic.com/claude-mythos-preview-system-card (§6.11.2)
- S6: https://openai.com/index/introducing-gpt-5-2/
- S7: https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_model_evaluation.pdf
- S7b: https://storage.googleapis.com/deepmind-media/gemini/gemini_3_flash_model_evaluation.pdf and https://blog.google/products-and-platforms/products/gemini/gemini-3-flash/
- S8: https://ai.meta.com/blog/introducing-muse-spark-msl/ (table as quoted at https://www.jdhodges.com/blog/meta-muse-spark-the-honest-scorecard-3-wins-out-of-20/)
- S9: https://developer.meta.com/ai/models/muse-glimmer/
- S10: https://arxiv.org/abs/2609.39600 (GroundAnything, Table 2)
- S11: https://qwen.ai/blog?id=qwen3.8
- S12: https://arxiv.org/abs/2602.16855 (GUI-Owl-1.5 / Mobile-Agent-v3.5, Table 4)
- S13: https://qwen.ai/blog?id=qwen3.7-plus and https://www.alibabacloud.com/blog/qwen3-7-plus-multimodal-agent-intelligence_603206
- S14: https://arxiv.org/abs/2607.28227 (Qwen-UI-Agent, Table 8)
- S15: https://huggingface.co/Hcompany/Holo2-235B-A22B
- S16: https://arxiv.org/abs/2609.00028 (UI-Venus-2, Table 4)
- S17: https://arxiv.org/abs/2512.22047 (MAI-UI, Table 2)
- S18: https://hcompany.ai/newsroom/holo3 (table image)
- S19: https://huggingface.co/blog/Hcompany/holo31 (table image)
- S20: https://github.com/intelligence-indeed/Indeed-UI
- S21: https://huggingface.co/vocaela/KV-Ground-8B-BaseGuiOwl1.5-0315
- S22: https://huggingface.co/Qwen/Qwen3.5-397B-A17B and https://huggingface.co/Qwen/Qwen3.5-122B-A10B
- S23: https://arxiv.org/abs/2602.09082 (UI-Venus-1.5)
- S24: https://arxiv.org/abs/2606.20785 (Fara-1.5, Table 6)
- S25: https://arxiv.org/abs/2610.19100 (GroundGUI, Table 4)
- S26: https://arxiv.org/abs/2507.05791 (GTA1)
- S27: https://arxiv.org/abs/2512.15431 (Step-GUI)
- S28: https://arxiv.org/abs/2604.14113 (UI-Zoomer)
- S29: https://arxiv.org/abs/2602.06391 (POINTS-GUI-G)
- S30: https://arxiv.org/abs/2507.23779 (Phi-Ground)
- S31: https://arxiv.org/abs/2507.15846 (GUI-G²)
- Aggregators used only for cross-checking: https://llm-stats.com/benchmarks/screenspot-pro, https://benchlm.ai/benchmarks/screenspot-pro, https://paperswithcode.co/benchmark/screenspot-pro

Files are in /tmp/claude-1000/-home-bionics-Desktop-MillionMyLife/70513a22-bb79-46e4-91f0-355ab37e7dde/scratchpad:
- `lb/sspro.json`: the official leaderboard's raw data, with per-app and per-group breakdowns.
- `lb/lb.txt`: all 99 leaderboard models sorted by score.
- `cards/`: the Anthropic system card PDFs.
- `arx/`: the arXiv PDFs and their extracted text.

## Addendum (Oct 17, checked by hand): every H Company Holo model with a Pro score

Holo1.5 card (https://huggingface.co/Hcompany/Holo1.5-72B), Holo2 card (S15), Holo3 (S18), Holo3.1 (S19), official leaderboard (S0). Holo4 (Sep 28 2026) publishes no grounding number.

| Model | Pro single-shot | Pro agentic | Source |
|---|---|---|---|
| Holo3-122B-A10B | 72.2 (setup not stated) | | Holo3 post |
| Holo3.1-35B-A3B | 71.5 (setup not stated) | | Holo3.1 post |
| Holo2-235B-A22B | 70.6 | 78.5 | Holo2 card |
| Holo3-35B-A3B | 67.6 (setup not stated) | | Holo3 post |
| Holo2-30B-A3B | 66.1 | 75.2 | Holo2 card |
| Holo1.5-72B | 63.25 | | Holo1.5 card |
| Holo2-8B | 58.9 | 71.4 | Holo2 card |
| Holo1.5-7B | 57.94 | | Holo1.5 card |
| Holo2-4B | 57.2 | 68.6 | Holo2 card |
| Holo1.5-3B | 51.49 | | Holo1.5 card |
| Holo1-7B | 26.06 | | Holo1.5 card |
| Holo1-3B | 23.66 | | Holo1.5 card |

The same Holo1.5 table has H Company's in-house run of Claude Sonnet 4: v2 93.0, Pro 19.1.
