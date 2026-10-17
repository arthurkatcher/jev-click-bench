# Were these ScreenSpot-v2 label errors already reported?

Checked Oct 17 2026. Short answer: no. Nobody has reported any of the four key errors, the duplicate or the edge box, and nobody has published a corrected ScreenSpot-v2.

## Where we looked

| Place | What was checked | Result |
|---|---|---|
| OS-Copilot/OS-Atlas issues | All 58 issues, titles and bodies, open and closed | No label or bbox error report |
| OS-Copilot/OS-Atlas issues | Comments on #23, #38, #39, #60, #63 | Eval and repro questions only |
| OS-Copilot/OS-Atlas PRs | All 6 PRs (#42, #43, #48, #49, #54, #55) | Eval scripts and README updates |
| HF OS-Copilot/ScreenSpot-v2 | Both discussions, read in full | Format and load_dataset questions |
| HF dataset search "screenspot" | 55 datasets, v2 mirror READMEs scanned | No errata (details below) |
| njucckevin/SeeClick | All 63 issues and 4 PRs | Only #14, about the finetune data |
| GitHub issue search | 8 queries, incl. instruction strings | No hits |
| GitHub code search | 3 case strings and #458's image name | Copies of the json, no errata |
| Web search | Label noise, errata, re-annotated, strings | Only the OS-Atlas paper's own v1 notes |

## Findings worth knowing

- **ScreenSpot v1 had #1035 and #1037 right.** In SeeClick's ScreenSpot (HF mirror KevinQHLin/ScreenSpot), "log in by x account" has bbox [1979, 475, 71, 62], on the X icon. "check the weather news" has [257, 306, 170, 109], on Weather. v2 changed both boxes, to YouTube and DelmarvaLife. Between v1 and v2 only 9 boxes changed for the same image and instruction, and these are 2 of them. The other 7 are small moves, plus #1110 "open mediawiki" (which we had flagged only as a partial-control judgment call).
- **#455, #458, #487 and #449 are new in v2.** Their screenshots are not in v1, so the #458 copy error was introduced with the new cases.
- **The duplicate is new in v2.** v1 has "open the menu" on web_e22bd6de once. v2 has it twice (web [182] and [186]).
- **likaixin/ScreenSpot-v2-variants** (by the ScreenSpot-Pro author, May 2025) silently re-boxes 14 desktop cases (desktop indices 88, 119, 308, 309, 312, 313, 315, 318, 319, 322, 324, 327, 328, 332) and swaps one instruction (desktop [330] "insert a new slide" becomes "insert a picture"). None of them is one of ours, the README does not mention the changes, and the four key errors are unchanged there. It is a variant with extra instruction types, not an errata.
- **microsoft/GUI-Actor verifier/ScreenSpot-v2-new** (Jun 2025) is a pure format conversion (xyxy): all 1,272 boxes match the original, errors included.
- **James-Fountain/Version-Benchmark-Test bad_cases.csv** lists #458's screenshot. Its model caption describes the key box as the "Wireless Data" row. That is a personal experiment log, not a report upstream.
- The OS-Atlas paper says v2 fixed about 11.32% of v1 (typos, missing targets, ambiguity, near-duplicates, wrong boxes). No independent re-audit of v2 was found.

## Effect on the draft

Nothing was already reported, so no "also reported in #N" references. ISSUE.md now says that v1 had #1035 and #1037 right and suggests restoring the v1 boxes. It also says that #458, #487 and the duplicate came in with v2.

## Links

- https://github.com/OS-Copilot/OS-Atlas/issues
- https://huggingface.co/datasets/OS-Copilot/ScreenSpot-v2/discussions
- https://github.com/njucckevin/SeeClick/issues
- https://huggingface.co/datasets/KevinQHLin/ScreenSpot (v1 metadata/screenspot_web.json)
- https://huggingface.co/datasets/likaixin/ScreenSpot-v2-variants
- https://github.com/microsoft/GUI-Actor/tree/main/verifier/ScreenSpot-v2-new
- https://github.com/James-Fountain/Version-Benchmark-Test/blob/main/bad_cases.csv
- https://arxiv.org/abs/2410.23218 (OS-Atlas paper, v2 description)
- https://docs.voxel51.com/dataset_zoo/datasets_hf/screenspot_v2.html
