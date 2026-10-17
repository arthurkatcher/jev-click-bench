<!-- DRAFT, not posted. Target: https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/discussions/new
     The GitHub issue is up (#32) and its link is filled in below. Needs Arthur's go before posting. -->

**Title:** 3 wrong labels, 1 contradictory pair and 2 near-duplicate cases

Hi, I found a few labels in ScreenSpot-Pro (revision 210e78d) that look wrong. Ids are as in the json files, and boxes are [x1, y1, x2, y2] as stored:

- blender_windows_19 "Move the cone one the X axis by dragging it": the bbox [841, 399, 902, 419] is the green (Y) arrow of the gizmo. The red X arrow is at about [917, 399, 971, 419].
- matlab_macos_41 "edit font weight in plot": the bbox [1773, 547, 1921, 566] is the FontSize field. The FontWeight toggle is at about [1772, 571, 1794, 593].
- inventor_windows_60 "redo to a specific history point": the bbox [135, -1, 151, 19] is Undo's history dropdown, which matches instruction_cn (撤销, undo). The English should probably say undo. The box also starts at y = -1.
- pycharm_macos_36 and pycharm_macos_69 "show problem details": the same screen, but one keys the "Problems" title and the other the "File 18" tab.
- autocad_windows_14 / autocad_windows_25 and inventor_windows_1 / inventor_windows_43 are each the same case twice, re-shot a minute or two apart.

Some English instructions on the Chinese-UI apps also read like word-for-word translations of the Chinese labels, and a few point at something else, for example inventor_windows_68 "Front view" for 主视图, which is the Home View button. Where the English and instruction_cn disagree, the Chinese is usually the one that matches the screen. Details and screenshots are in the GitHub issue: https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/issues/32

Since published scores use the current key, an errata file might be easier than editing the key in place. Thanks for the dataset.
