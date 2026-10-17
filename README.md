# jev-click-bench

How well does Jev 1.14's `box` tool click? I ran it on both standard click benchmarks, ScreenSpot-v2 and ScreenSpot-Pro, with the official scoring code: 2,853 clicks, every request and response logged. On ordinary screens it hits 84%. On pro apps at 4K it hits 19%. A zoomed second look takes Pro to 43% and a third to 60%, with the same model and nothing trained.

Write-up: [Teaching Jev's box to click 3x better, benchmarked: my 5 rules](https://arthurkatcher.com/blog/teaching-jevs-box-to-click-3x-better), also [on X](https://x.com/arthurkatcher/status/2111499108733038723).

![Cover: Jev can click(?). 84% on ScreenSpot-v2, 60% on ScreenSpot-Pro with harness updates, over a grid of pro-app screenshots with the answer key in green and Jev's box in orange.](docs/img/cover.jpg)

| Benchmark | Setup | Calls per click | Score | Cost per 1,000 clicks |
|---|---|---|---|---|
| ScreenSpot-v2 (1,272) | Jev box | 1 | 84.36% | $0.15 |
| ScreenSpot-v2 | + 2x zoom | 2 | 87.89% | $0.30 |
| ScreenSpot-Pro (1,581) | Jev box | 1 | 18.66% | $0.16 |
| ScreenSpot-Pro | + 2x zoom | 2 | 42.76% | $0.32 |
| ScreenSpot-Pro | + 4x zoom, post-hoc | 3 | 60.15% | $0.48 |

- Raw is one call on the whole screenshot. Raw and zoom rows are the same run, so each zoom row is the same cases seen again. A separate raw pass scored 83.33% (v2) and 19.17% (Pro), the same within noise.
- The 4x step was designed after the 2x result, and its prediction was committed before it ran ([`analysis/zoom4x/prediction.txt`](analysis/zoom4x/prediction.txt)): 63.2%, range 59.7 to 66.2. It is a labelled extra. 42.76% stays the clean Pro number.
- Every score uses the official eval code and answer key, including the cases where the label audit thinks the key is wrong.
- Costs are what OpenRouter billed, logged on every record. The key balance matched the logs to the cent.

## The 5 rules

The harness I would ship from these runs. Each rule rests on a measured result below.

1. Send the screenshot with one box question and click the centre of the box.
2. Ask again on a crop half the width and height around that box, and map the answer back.
3. Skip the second look on phone screens, where the misses are wrong picks.
4. Trust zoomed answers at 0.9 confidence or more. Send the rest to a check or a stronger model.
5. On dense 4K apps, add a third look at a quarter crop.

## The runs in pictures

### Where Jev lands on ScreenSpot-Pro

![Chart titled Zoom puts Jev next to grounding specialists: published ScreenSpot-Pro scores from GPT-6 Astra at 92.7 down to Claude Sonnet 4 at 19.1. Jev's three bars are orange: 18.66 with one call, at the bottom next to Claude Sonnet 4, 42.76 with a 2x zoom second call, between Phi-Ground-7B at 43.2 and GUI-Actor at 42.2, and 60.15 with the post-hoc 4x third call, between UI-TARS-1.5 at 61.6 and POINTS-GUI-G-8B at 59.9.](docs/img/fig01-leaderboard.jpg)

Jev's three bars are orange. One call sits at the bottom, next to Claude Sonnet 4. The other two bars are the same model with nothing trained; only the harness changed. Other scores are as published, each with its own setup (single-shot, zoom, tools or thinking). Sources: [`analysis/leaderboard/screenspot-pro.md`](analysis/leaderboard/screenspot-pro.md).

### What it costs

![Chart titled Zoom moves Jev up without leaving the cheap end: ScreenSpot-Pro score against cost per 1,000 clicks on a log scale. Jev's measured points go from 18.66% at $0.16 with one call to 42.76% at $0.32 with two and 60.15% at $0.48 with three. Estimated floors for other models sit between about $1 and $43 per 1,000 clicks.](docs/img/fig02-cost.jpg)

Jev's points are billed costs. The other models' floors are estimates from image tokens and list prices, in [`analysis/leaderboard/cost-latency.md`](analysis/leaderboard/cost-latency.md).

### A v2 task and a Pro task

The two benchmarks on the same 2,560 x 1,440 screen size. On v2 the target is a link, 0.71% of the screen, and Jev hits it on the first call:

![Screenshot titled A v2 task: change password. A 2,560 x 1,440 store account page with the answer key around the Change Password link, 330 x 79 px, 0.71% of the screen. Jev's box lands inside it on the first call.](docs/img/task-v2.jpg)

On Pro the target is a toolbar icon, 0.025% of the screen, about 20 x 17 px in the image Jev gets. The box lands just below it:

![Screenshot titled A Pro task: select the eyedropper tool. A 2,560 x 1,440 Photoshop screen. The answer key is the 33 x 28 px eyedropper icon in the left toolbar, 0.025% of the screen, about 20 x 17 px in the image Jev gets. A detail strip enlarges the toolbar: Jev's box lands just below the icon, and the click misses.](docs/img/task-pro.jpg)

### The zoom step

![Figure titled A second look at 2x turns a near miss into a hit: a Microsoft Word screenshot with the task redo. Call 1 sends the whole screen and its box lands next to the target, so the click misses. Call 2 sends a 2x crop around that box and the click lands on the target. A detail strip below shows both answers against the answer key.](docs/img/fig03-zoom-step.jpg)

The crop goes in at the same image size as the full screenshot, so a small target arrives twice as big at the same token cost.

### What the second look adds

![Chart titled 2x zoom adds 3.5 points on ScreenSpot-v2 and 24 on Pro: bars for the same cases in the same run. ScreenSpot-v2 goes from 84.36% raw to 87.89% with 2x zoom. ScreenSpot-Pro goes from 18.66% raw to 42.76% with 2x zoom, and 60.15% with a post-hoc 4x step, inside a prediction band of 59.7 to 66.2 with the predicted 63.2% marked.](docs/img/fig04-zoom-gains.jpg)

On v2 the second look fixed 95 misses and broke 50 hits. On Pro it fixed 436 and broke 55, about seven times the v2 gain. On v2, zoomed answers at 0.9 confidence or more were right 98.7% of the time.

### Why Pro gains seven times more

![Chart titled The bigger the target, the more Jev hits it: Jev's hit rate on ScreenSpot-Pro by target size in the image it was sent, rising from 2% under 10 px to 5%, 19%, 37%, 53%, 73% and 85% above 80 px. Markers show the typical target at 21 px raw, 43 px with 2x zoom and 88 px with 4x zoom.](docs/img/fig05-target-size.jpg)

Size decides most of it. Pro is still harder at the same apparent size, by 20 to 35 points against v2: dense toolbars of icons with no text, and 295 cases that ask in English about a Chinese interface.

### Where zoom stops

![Chart titled Zoom fixes clicks that land close, not wrong picks: of the 905 cases 2x zoom still missed, the 4x step fixed 290 of 514 where Jev clicked close to the target (56%), 37 of 326 where it clicked something else (11%), and 13 of 65 where the answer key looks wrong (20%).](docs/img/fig06-misses.jpg)

Looking closer at the wrong spot rarely helps. The misses were sorted by AI reviewers in the label audit ([`analysis/LABELS-audit-pro.md`](analysis/LABELS-audit-pro.md)).

### Every chapter

![Chart titled Zoom lifts every chapter except mobile: raw, 2x and 4x hit rates per chapter. On ScreenSpot-v2, mobile text goes from 93.1 to 93.8 and mobile icon from 84.4 to 82.5, while desktop and web icons gain 7.1 and 7.9 points. On ScreenSpot-Pro every chapter rises, from Office text at 85.9 after 4x down to Scientific icons at 30.9, with all text chapters above all icon chapters.](docs/img/fig07-chapters.jpg)

Mobile never moved. Its misses are wrong picks, a median 95 px away on text and 228 px on icons, against 10 to 19 px on desktop and web. A half crop of a phone screen also often cuts off the row label that names the target.

## Benchmark bugs found on the way

Looking at every miss turned up label problems in both benchmarks. They were reported upstream, and none of them changes a score here.

| Benchmark | Misses with a label issue | Broken tasks | Reported |
|---|---|---|---|
| ScreenSpot-v2 | 43 of 271 | 4 wrong keys, 1 duplicate case | [OS-Atlas #65](https://github.com/OS-Copilot/OS-Atlas/issues/65) |
| ScreenSpot-Pro | 65 of 905 | 3 wrong labels, 1 contradictory pair, 2 near-duplicates | [Issue #32](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/issues/32), [HF #5](https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/discussions/5) |

The 271 are every v2 case at least one run missed, and the 905 every Pro case the second look still missed. On Pro the label problems are worth at most 2.3 points, so the misses there really are the model. Details: [`analysis/LABELS-audit.md`](analysis/LABELS-audit.md), [`analysis/LABELS-audit-pro.md`](analysis/LABELS-audit-pro.md).

## What this does not show

- One model version, `jev-1.14-20261014`, and box is a preview feature. The next version could move every number.
- Jev is not deterministic. On v2 the same request twice returns the same box only 30% of the time, though the click moves a median 4.8 px.
- No other model was re-run. Their scores are as published, and their costs are estimates.
- ScreenSpot is one click on a still screenshot. A real agent also has to notice when the target is missing, and box always returns a box.

## Run it yourself

1. Python 3.10+, `pip install requests pillow`.
2. Get the data from Hugging Face into `data/`: [OS-Copilot/ScreenSpot-v2](https://huggingface.co/datasets/OS-Copilot/ScreenSpot-v2) into `data/screenspot-v2/`, [likaixin/ScreenSpot-Pro](https://huggingface.co/datasets/likaixin/ScreenSpot-Pro) (revision 210e78d) into `data/screenspot-pro/`. Screenshots are not in this repo.
3. Copy `.env.example` to `.env` and put in an OpenRouter key.
4. Run the offline tests, then a pass. A full v2 pass costs about $0.19 and a Pro stage about $0.25, so any number here can be checked for under a dollar.

```
python3 tests/test_offline.py                                  # no API calls
python3 screenspot.py run --pass 1 --workers 4                 # ScreenSpot-v2, raw
python3 screenspot.py run --pass 2 --zoom --max-cost 0.40      # raw + 2x zoom in one run
python3 screenspot.py --bench pro run --pass 2 --zoom --workers 4 --max-cost 0.60   # ScreenSpot-Pro
python3 screenspot.py report results/pass1.jsonl
```

Every command, the frozen protocol and the zoom rules are in [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

## What's in here

- `jev.py`: the Jev call (OpenRouter decisions API, model pinned to `typesafe/jev-1.14`). The key is never logged.
- `screenspot.py`: runner, official scoring, report, compare and the zoom stages.
- `results/`: one JSON line per click with Jev's raw response, box, click, hit and cost, plus the run logs.
- `analysis/`: the deep audits ([v2](analysis/AUDIT-run2.md), [Pro](analysis/AUDIT-pro-run2.md)), the label audits, sourced leaderboards, cost research, the 4x prediction and the figure scripts.
- `REPORT.md`: the running report, every number with where it comes from.
- `docs/PROTOCOL.md`: protocol, layout and commands. `docs/img/`: the figures above.
- `tests/`: offline tests against a mocked API, no spend.

## License

Code: MIT. Datasets: ScreenSpot-v2 (Apache-2.0, OS-Copilot) and ScreenSpot-Pro (MIT, Li et al.), not included here. The result records and figures quote their instructions, answer boxes and a few screenshots. The official eval code the scoring copies (SeeClick, OS-Atlas, ScreenSpot-Pro-GUI-Grounding) is not redistributed.

By Arthur Katcher, [@arthurkatcher](https://x.com/arthurkatcher) on X and [arthurkatcher.com](https://arthurkatcher.com).
