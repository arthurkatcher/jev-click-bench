# Were these ScreenSpot-Pro label errors already reported?

Checked Oct 17 2026. Short answer: no. Nobody has reported any of our candidates (the wrong labels, the contradictory and near-duplicate pairs, the wording cases or the byte-identical screenshots, including the two pairs VERIFY.md later rejected), and nobody has published a corrected ScreenSpot-Pro. The annotations have not changed since the first upload, and every mirror and copy we found carries the same keys. The only earlier work on ScreenSpot-Pro label quality is an aggregate estimate in the VenusBench-GD paper, which lists no cases.

## Where we looked

| Place | What was checked | Result |
|---|---|---|
| likaixin2000/ScreenSpot-Pro-GUI-Grounding issues | All 23 issues, open and closed, bodies and every comment | No label, bbox or data error report |
| Same repo, gaps in numbering | #8 (deleted), #24 (moved to the site repo) | Not about data |
| Same repo PRs | All 6 PRs (#4, #19, #25, #28, #29, #31) | Model adapters and leaderboard entries |
| Same repo files | Full tree of main | Code only: no data, errata or issue templates |
| gui-agent/grounding-leaderboard | Issues, PRs and the leaderboard page | None filed, no errata or data notes |
| HF likaixin/ScreenSpot-Pro discussions | All 4, read in full | Parquet bot, 2 metadata PRs, 1 empty PR |
| HF likaixin/ScreenSpot-Pro history | All 9 commits, annotation blob hashes | Annotations unchanged since Dec 22 2024 |
| HF dataset search | 22 queries, 18 Pro mirrors and subsets found | 15 with annotations compared: all unchanged |
| Annotation copies on GitHub | Phi-Ground, UI-Ins, MAI-UI | Same boxes and wording as upstream |
| GitHub issue search | About 230 issues naming ScreenSpot-Pro, 10 strings | No label error report |
| GitHub code and repo search | 10 instruction strings, 5 ids, 3 image names | Copies of the json, one id list |
| Papers | Pro paper (2 versions), VenusBench-GD, 5 others | One aggregate estimate, no cases |
| Web search | English and Chinese queries | Nothing case-level |
| OpenReview forums of the paper | 2 forums | Not readable (bot check) |

## Findings worth knowing

- **There is no upstream fix to diff against.** The annotations were uploaded once, in commit ad1a3ed (Dec 22 2024). The six later commits only touch the README, the task category and eval.yaml. Our revision 210e78d (Mar 18 2026) is still the latest on main, and all 26 local annotation files match its blobs byte for byte.
- **VenusBench-GD (arXiv 2512.16501, Dec 2025) is the only quantitative check of ScreenSpot-Pro labels.** In a blind review of 500 random cases it rated 4.6% inaccurate: 2.2% inaccurate localization (box too large or too small), 1.8% ambiguous reference (more than one valid element) and 0.6% semantic mismatch (box on no element that matches). It lists no cases, and the examples in its Figure 4 come from other benchmarks. Its categories map onto ours: semantic mismatch = our wrong keys, ambiguous reference = our two-valid-answer cases, inaccurate localization = our partial-control cases.
- **Other papers treat the key as correct.** Phi-Ground (arXiv 2507.23779, Section 6.2) analyzes its failures on 1,534 ScreenSpot-Pro samples and attributes none of them to labels. UI-Ins (arXiv 2510.20286) reports a 23.3% instruction flaw rate, but for training sets (OS-Atlas, AMEX, Widget Captioning), not ScreenSpot-Pro. BAMI, GUI-Primitives and "Learning from Reliable Negatives" say nothing about Pro labels. Searches pairing ScreenSpot-Pro with GTA1, UI-Venus, GUI-G2, InfiGUI-G1, Holo1.5, GroundCUA or OSWorld-G found nothing either.
- **Every mirror and copy keeps our cases as they are.** Compared field by field (all 1,581 cases unless noted): lmms-lab, TIGER-Lab (two identical splits), lscpku, jdubkim, HongxinLi (normalized boxes), Voxel51 and its copy ZhuOnR, harpreetsahota (adds GUI-Actor heatmaps), aggfda and fcxfcx (byte-identical json), mlfoundations-cua-dev easyr1 (normalized boxes) and its 4MP version (original boxes kept, trailing spaces stripped from 16 instructions), pbcong (10 rows), aliaagheis (256 rows). On GitHub, the copies in Tongyi-MAI/MAI-UI and alibaba/UI-Ins are identical. microsoft/Phi-Ground's `benchmark/new_annotations/screenspot_pro` keeps 1,573 cases with the same boxes and wording (8 dropped, none of ours) and adds GPT-4o and o4-mini planner text. Not compared: Bin12345 (arrow files), advaitgupta (a multiple-choice reformulation), andersonbcdefg (images only).
- **gsarch/ScreenSpot-Pro-Lite** (Aug 2026, a 500-case subset for lmms-eval) keeps five of our cases unchanged: matlab_macos_41 (wrong key), matlab_macos_23, pycharm_macos_36, pycharm_macos_69 and inventor_windows_1. Its card says cases that every anchor model failed are downweighted "to reduce the risk of selecting ambiguous annotations".
- **Side evidence for blender_windows_19.** In Phi-Ground's planner file, GPT-4o and o4-mini both describe the target of "Move the cone one the X axis by dragging it" as the red X arrow. That matches our reading; the stored box is on the green arrow.
- **What the paper and cards say about counts.** Both versions of the paper say ScreenSpot-Pro "includes 1,581 instructions, each in a unique screenshot". The data has 1,581 distinct file names but only 1,551 distinct file contents (23 groups of byte-identical files, 30 extra copies), so the byte-identical files contradict a stated claim. The HF card gives only a per-app table (it sums to 1,581: 977 text, 604 icon). The eval.yaml line "covering 1,585 annotated images" was written by HF staff (HF PR #3, Mar 2026). 1,585 is the number of image files in the repo: the 1,581 in use, three unused ones (`common_windows/screenshot_2024-11-06_19-40-32.png` and two 12 KB Stata files) and a second copy of `common_mac/Screenshot 2024-11-07 at 1.58.03 PM.png` whose name has a narrow no-break space (U+202F) before "PM".
- **How the two instruction fields were made, per the paper: the Chinese is the translation.** arXiv v1, Appendix A: "every task in the benchmark also includes a Chinese instruction translated by GPT-4 and reviewed by the authors who are fluent in both languages." The newer version on the author's site (Sep 2025), Appendix A "ScreenSpot-Pro-CN": "The Chinese instructions were initially generated using GPT-4, then carefully reviewed and refined by the authors to ensure the meaning, tone, and intent matched the English version." The experts typed the instructions in a capture tool while working, "allowing experts to label the bounding boxes and provide instructions directly".
- **The paper's own quality rules, which our cases touch.** Site version, Section 3.3: "Each instance in the dataset is reviewed by at least two annotators to ensure its correctness. Specifically, we removed instructions that caused ambiguity: each instruction must refer to, and only to, a single area in the image." And: "the annotations are required to tightly encompass all parts of interactable regions." arXiv v1 says "Ambiguous instructions are resolved, guaranteeing only one target" and "Annotators precisely verify the interactable regions of the GUI elements, excluding irrelevant areas." The annotators were experts with at least five years in each app.
- **The maintainer answers and fixes things.** likaixin2000 usually replies within a day or two. The eval bug in #21 was fixed in code ("We've addressed this issue in the latest commit"), the leaderboard entry in #27 was renamed within a day, and HF PRs #2 and #3 were merged. Nobody has asked for a data correction yet, so there is no precedent for how label fixes are handled. The repo has issues on, discussions off and no templates. The leaderboard page only gives an email address for result submissions.

## Effect on the draft

- Nothing is already reported, so there are no "already reported in #N" references, and a new issue (not a comment) is the right form. ISSUE.md is a new issue.
- Wording section: the paper says the Chinese was produced from the English by GPT-4 and then refined (the arXiv v1 quote was re-checked), so "the English appears translated from `instruction_cn`" would contradict the paper. ISSUE.md instead says the English reads like a word-for-word translation of the Chinese labels on screen, and that where the two fields disagree the Chinese is usually the one that matches the screen.
- Byte-identical screenshots: the paper's "each in a unique screenshot" (re-checked in arXiv v1) makes this worth one line, and ISSUE.md has it under minor notes. The eval.yaml "1,585 annotated images" line is HF's text and is left out of both drafts.
- Errata: ISSUE.md's scope paragraph now says an errata keyed by `id` would also reach the mirrors, which copy the key as it is.
- Left out, Arthur's call: the VenusBench-GD context line (about 4.6% inaccurate in a 500-case sample, no cases listed), and quoting the paper's rules ("each instruction must refer to, and only to, a single area in the image"; "tightly encompass all parts of interactable regions") next to the contradictory pair and the judgment calls.
- Not used in the drafts: the Phi-Ground planner text on blender_windows_19 (model output, not evidence for maintainers) and gsarch/ScreenSpot-Pro-Lite carrying five of the cases.

## Links

- https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/issues
- https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/pulls
- https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/issues/21 (eval bug, fixed in code)
- https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/issues/27 (leaderboard entry renamed)
- https://github.com/gui-agent/grounding-leaderboard and https://gui-agent.github.io/grounding-leaderboard/
- https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/discussions
- https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/commits/main
- https://arxiv.org/abs/2504.07981 (paper, arXiv v1, Apr 2025)
- https://likaixin2000.github.io/papers/ScreenSpot_Pro.pdf (newer version, Sep 2025)
- https://arxiv.org/abs/2512.16501 (VenusBench-GD, Table 1 and Figure 4)
- https://arxiv.org/abs/2507.23779 (Phi-Ground, Section 6.2)
- https://github.com/microsoft/Phi-Ground/tree/main/benchmark/new_annotations/screenspot_pro
- https://arxiv.org/abs/2510.20286 (UI-Ins)
- https://github.com/alibaba/UI-Ins/tree/main/evaluation/SSpro_annotation
- https://github.com/Tongyi-MAI/MAI-UI/tree/main/MAI-UI/evaluation/grounding/data/ScreenSpot_Pro_data
- https://huggingface.co/datasets/gsarch/ScreenSpot-Pro-Lite
- https://huggingface.co/datasets/lmms-lab/ScreenSpot-Pro
- https://huggingface.co/datasets/Voxel51/ScreenSpot-Pro
