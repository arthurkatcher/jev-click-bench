# By-eye check of the ScreenSpot-Pro candidates

Checked Oct 17 2026 against `CANDIDATES.md`. Data: HF likaixin/ScreenSpot-Pro at revision `210e78d3844251110bff86c95835ebd37a6930fa` (from `data/screenspot-pro/.revision`), 1,581 cases in 26 annotation files. Boxes are as stored: [x1, y1, x2, y2] in original pixels. Every case below was viewed as a crop with the stored box drawn; suggested boxes were measured by eye on a pixel grid. Figures: `make_figures.py` (red = stored key, green dashed = suggested fix, blue dashed = another element that also fits).

## Summary

| Candidate | Verdict | In the issue as |
|---|---|---|
| blender_windows_19 | CONFIRMED | Wrong answer box |
| matlab_macos_41 | CONFIRMED | Wrong answer box |
| inventor_windows_60 | CONFIRMED, reframed | Wrong English instruction (key matches the CN) |
| inventor_windows_60, y1 = -1 | CONFIRMED | Minor note |
| pycharm_macos_36 / _69 | CONFIRMED | Contradictory pair |
| matlab_macos_23 / _50 | REJECTED | Dropped: different screens, both keys right |
| quartus_windows_8 / _35 | REJECTED | Dropped: different screens, both keys right |
| autocad_windows_14 / _25 | CONFIRMED (near-duplicate) | Near-duplicate cases |
| inventor_windows_1 / _43 | CONFIRMED (near-duplicate) | Near-duplicate cases |
| (d) 12 wording cases | 11 CONFIRMED, 1 moved | Wording section (10 + inventor_68) |
| inventor_windows_64 | CONFIRMED loose, not a translation | Judgment-call count only |
| (e) byte-identical files | CONFIRMED, harmless | Optional one-line minor note |
| (f) judgment-call examples | CONFIRMED | 3 examples + counts |

## (a) Answer-key errors

**blender_windows_19** (blender_windows.json [19], `blender_windows/screenshot_2024-11-27_16-59-24.png`, 2560x1440). CONFIRMED.
- "Move the cone one the X axis by dragging it" / 拖动以在X轴上移动锥体。 Both languages say X.
- Stored [841, 399, 902, 419] covers the green arrow of the move gizmo, pointing left. The red arrow points right. The navigation gizmo on the same screenshot labels the red ball X and the green ball Y, and the header shows Global orientation with zero rotation, so green = Y.
- Suggested: [917, 399, 971, 419], the red arrow (shaft starts at x ≈ 919, tip at x ≈ 969), same height as the stored box. Figure: `fig_blender_19_x_axis.png`.

**matlab_macos_41** (matlab_macos.json [41], `matlab_mac/screenshot_2024-12-01_16-31-48.png`, 2560x1440). CONFIRMED.
- "edit font weight in plot" / 编辑绘图中的字体粗细 (字体粗细 = font weight). Both languages agree.
- Stored [1773, 547, 1921, 566] is exactly the FontSize field ("10") of the Property Inspector. The FontWeight row is directly below, with the bold "B" toggle.
- Suggested: [1772, 571, 1794, 593], the FontWeight toggle. Figure: `fig_matlab_41_font_weight.png`.
- Side note, not for the issue: the annotation tool's console is visible in this screenshot (and in matlab_macos_23 / _50), logging earlier instructions and boxes.

**inventor_windows_60** (inventor_windows.json [60], `inventor_windows/screenshot_2024-11-24_11-36-37.png`, 3840x1080). CONFIRMED, but it is the English instruction that is wrong, not the box (the coordinator's correction, which matches what the screenshot shows).
- "redo to a specific history point" / 撤销操作到某一历史记录. 撤销 means undo, so the Chinese says "undo the operation to a history record".
- Stored [135, -1, 151, 19] is the ▾ right of the Undo arrow (QAT: Undo icon x ≈ 117-132, its ▾ x ≈ 140-145; Redo icon x ≈ 154-169, its ▾ x ≈ 176-181). Key and Chinese agree; only the English says redo.
- Suggested fix: change the English to "undo to a specific history point" and keep the box. Only if "redo" was meant, the box would be Redo's ▾ at about [171, 0, 187, 19]. Figure: `fig_inventor_60_undo_not_redo.png`.
- y1 = -1: the box starts 1 px above the image. A scan of all 1,581 boxes finds no other box outside its image (no x1 < 0, y1 < 0, x2 > W or y2 > H), no copied box (no bbox value repeats), and no box with a side under 8 px. `img_size` matches the real image size in all 1,581 cases.

## (b) Contradictory pairs

All 20 pairs with the same app and the same English words were scanned. Only 5 have near-identical screens (0.04% to 2.2% of pixels differ, threshold 24 grey levels); the other 15 differ in 11% or more and are separate tests. Of the 5, two are the duplicates in (c) and three are the candidates here. Only one survives a look at the UI state.

**pycharm_macos_36 / pycharm_macos_69** ("show problem details" / 显示问题详情). CONFIRMED.
- Files `screenshot_2024-10-23_15-20-34.png` and `..._15-21-26.png` (5120x2880), md5 a3dd28a44424 vs 0a4bad8d994f, 52 s apart. Only 0.04% of pixels differ: the caret line (104 vs 114, also in the status bar), the Problems window's focus (grey vs blue tab underline, sidebar icon highlighted) and the menu-bar clock. Same tabs, same Server-Side Analysis content.
- _36 keys the "Problems" title of the tool window [116, 2004, 276, 2060]; _69 keys the "File 18" tab [290, 1998, 432, 2064]. No overlap, so one consistent answer can only match one of them.
- Defensibility: the File tab lists the open file's 18 problems, which fits "show problem details"; the title is the tool window's name label. Both are loose readings of the words. Suggest: accept both boxes in both cases, or align the two keys. Figure: `fig_pycharm_36_69_contradictory.png`.

**matlab_macos_23 / matlab_macos_50** ("brush data points"). REJECTED.
- Not the same state. In _50 (16-27-07) the figure's Tools menu is open and the key [1222, 586, 1406, 609] is its "Brush" item. In _23 (16-27-17) the menu is closed and the axes toolbar is showing; the key [1450, 485, 1467, 505] is its brush icon. The axes toolbar is not visible in _50.
- Each key is the brush control on its own screen. The 2.2% pixel difference is the open menu. Note for our audit: the OVERRIDE reason in `labels_audit_pro.py` ("twin #666 keys the data region") is wrong, #666 keys the Tools > Brush item.

**quartus_windows_8 / quartus_windows_35** ("Compilation Report"). REJECTED.
- Not the same state. In _8 (18-46-19) the Processing menu is open and the key [229, 165, 550, 187] is its "Compilation Report Ctrl+R" item. In _35 (18-40-05, six minutes earlier) no menu is open and the key [775, 51, 799, 75] is the toolbar's Compilation Report button.
- Each key is defensible on its screen. The toolbar button is also visible in _8, so _8 has two valid answers at most, a judgment call rather than a contradiction.
- Effect on our audit: the TWIN group shrinks to the PyCharm pair. #639 and #1069 should get their model codes back (the batch reviewers gave PRECISION and MODEL SAMEGROUP).

## (c) Duplicate cases

Neither pair is byte-identical; both are re-shots a minute or two apart with the same UI state at the target. They test the same thing twice. CONFIRMED as near-duplicates (low stakes).

**autocad_windows_14 / autocad_windows_25** ("Threaded blind hole tool" / 螺纹盲孔工具). `screenshot_2024-12-05_11-04-49.png` vs `..._11-05-59.png`, 70 s apart, md5 f46e52121f64 vs 0596513211ad. The 孔 (Hole) flyout is open the same way in both, and both keys mark 螺纹盲孔 ([123, 122, 199, 141] vs [121, 120, 201, 143], IoU 0.78). Only the drawing changed (a threaded hole was added; 2% of pixels differ). Figure: `fig_autocad_14_25_near_duplicate.png`.

**inventor_windows_1 / inventor_windows_43** ("Paste" / 粘贴). `screenshot_2024-11-23_11-01-55.png` vs `..._11-03-39.png`, 104 s apart, md5 faa7bc603f87 vs 1fa5e5dd5a30. Same ribbon (Tools tab, Clipboard group), both keys on 粘贴 ([704, 45, 766, 114] vs [704, 47, 759, 113], IoU 0.85). Only the sketch on the canvas changed (0.3% of pixels). Figure: `fig_inventor_1_43_near_duplicate.png`.

## (d) Wording and `instruction_cn`

For each case: the visible label or the key, then whether the Chinese or the English is at fault.

| Case | English | instruction_cn | Key / label on screen |
|---|---|---|---|
| inventor_windows_68 | Front view | 主视图 | 主视图 = Home View (house icon) |
| origin_windows_42 | import into excel | 导入到Excel | Import Excel (imports from Excel) |
| inventor_windows_54 | Draw a curve. | 画圆弧 | 圆弧 = Arc |
| powerpoint_windows_1 | Und | 撤销 | Undo (QAT) |
| vivado_windows_56 | open IP properties in vivado | 在Vivado中打开IP属性 | ? (help) of the open IP Properties pane |
| fruitloops_windows_21 | use smart fine tool | 使用智能精细工具 | Browser Search (magnifier) |
| solidworks_windows_18 | Shedding the shell | 抽壳 | 抽壳 = Shell |
| solidworks_windows_54 | Insert coordination | 插入配合 | Insert > 配合 = Mate |
| solidworks_windows_70 | Annotation size | 标注尺寸 | 智能尺寸 = Smart Dimension |
| autocad_windows_21 | Benchmark Identifier | 基准标识 | Datum identifier icon (framed A) |
| autocad_windows_30 | Extract Annotation | 引出注释 | 引线注释 = Leader Note |
| inventor_windows_64 | Place constraint | 放置约束 | Mate type button in the open dialog |

- **inventor_windows_68** (`screenshot_2024-11-24_12-35-54.png`, key [1147, 97, 1211, 122]). CONFIRMED. The Chinese is the exact label of the Home View button in View > Navigate. 主视图 also means "front view" in technical drawing, and the English took that sense; the ViewCube on the same screen shows its 前 (Front) face, so the English points at a different control. Chinese right, English wrong. Suggested English: "home view". Figure: `fig_inventor_68_home_view.png`.
- **origin_windows_42** (`screenshot_2024-12-05_16-55-42.png`, key [1300, 74, 1323, 95]). CONFIRMED. The key is Import Excel in the Import toolbar (Excel X with a red arrow into a worksheet grid, by app knowledge), which brings an Excel file into Origin. Both languages say "into Excel", so both reverse the action; the English is a literal copy of the Chinese. The key is still the best answer. Figure: `fig_origin_42_import_excel.png`.
- **inventor_windows_54** (key [156, 49, 195, 111]). CONFIRMED. Key = 圆弧 (Arc) in Sketch > Create. 画圆弧 = draw an arc, exact. "Draw a curve" is looser (splines are curves too). Chinese right, English loose. Figure: `fig_inventor_54_arc.png`.
- **powerpoint_windows_1** (English UI, key [45, 5, 80, 30]). CONFIRMED. Key = Undo in the QAT. 撤销 = Undo; "Und" is cut short and also reads as the start of Underline. Chinese right, English broken. Figure: `fig_powerpoint_1_und.png`.
- **vivado_windows_56** (English UI, key [1035, 773, 1052, 798]). CONFIRMED. The IP Properties pane is already open and the key is its ? button. Siblings on the same app say "open help of IP catalog in vivado" (vivado_windows_34) and "open help of source in vivado" (vivado_windows_59), keyed on the same kind of ? button. "help of" looks dropped, in both languages. Figure: `fig_vivado_56_help.png`.
- **fruitloops_windows_21** (English UI, key [49, 85, 67, 105]). CONFIRMED broken in both; direction UNSURE. Key = the Browser's magnifier, which the FL Studio manual calls Search (Ctrl+F); no "smart" tool is documented. "fine" is probably a typo for "find". 精细 means fine as in precise, so the Chinese reads like a literal translation of that typo, the opposite direction from the coordinator's reading. Figure: `fig_fruitloops_21_search.png`.
- **solidworks_windows_18** (key [608, 88, 665, 111]). CONFIRMED. Key = 抽壳 (Shell). Chinese exact; "Shedding the shell" is a word-for-word rendering. Chinese right, English literal. Figure: `fig_solidworks_18_shell.png`.
- **solidworks_windows_54** (key [340, 57, 537, 80]). CONFIRMED. The Insert (插入) menu is open and the key is 配合(M)... (Mate). The Chinese is the exact menu path; 配合 also means "coordinate" in everyday use. Chinese right, English literal. Figure: `fig_solidworks_54_mate.png`.
- **solidworks_windows_70** (key [55, 143, 219, 166]). CONFIRMED. Key = 智能尺寸 (Smart Dimension), top item of the open dimension dropdown. 标注尺寸 is a correct generic "add a dimension", not the label; "Annotation size" renders it word for word and reads as the size of an annotation. Chinese loose but right, English wrong. Note: solidworks_windows_13 has the same 标注尺寸 rendered as "Mark dimensions". Figure: `fig_solidworks_70_dimension.png`.
- **autocad_windows_21** (key [319, 69, 341, 92]). CONFIRMED. Key = the datum identifier icon in the 符号 (Symbols) panel, unlabelled; 基准标识 is its Chinese name (by app knowledge, AutoCAD Mechanical's Datum Identifier). "Benchmark" is the everyday sense of 基准. Chinese right, English literal. Figure: `fig_autocad_21_datum.png`.
- **autocad_windows_30** (key [87, 73, 149, 135]). CONFIRMED. The button reads 引线注释 (Leader Note). The Chinese has 引出注释, one character off; "Extract Annotation" renders 引出注释 literally. Both loose, the English more so. Figure: `fig_autocad_30_leader_note.png`.
- **inventor_windows_64** (key [550, 218, 578, 244]). Loose in both languages, not a translation problem: the Place Constraint (放置约束) dialog is already open and the key is its first Type button (Mate). English and Chinese say the same thing. Kept in the judgment-call count, out of the wording section.
- **linux_common_linux_35** ("split a new terminal tab" / 拆分一个新的终端标签页) and the other English-UI loose cases: both languages say "split", GNOME Terminal's button opens a new tab. Loose in both, key right. Judgment-call count only.
- Two more literal renderings, from a skim of all EN/CN pairs on these apps (keys checked by eye, both right): solidworks_windows_2 "Quality Attributes" / 质量属性 = Mass Properties (质量 means both mass and quality), and solidworks_windows_64 "Equidistant Entity" / 等距实体 = Offset Entities. Figures: `fig_solidworks_2_mass_properties.png`, `fig_solidworks_64_offset.png`. Not misses, so they are illustration only.

**Which way the translation went.** On the Chinese-UI apps many English instructions read like word-for-word renderings of the Chinese labels (above, plus, from the text only with keys not checked: "Stretch to crop" and "Stretch and cut" for 拉伸切除, Extruded Cut, and "Draw out the serial number." for 引出序号, Balloon). On English-UI apps the Chinese looks derived from the English: vivado_windows_73's Chinese keeps the English typo "viavdo", and fruitloops_windows_21's 精细 copies "fine". There is one counter-sign on a Chinese-UI app: inventor_windows_44's Chinese is "切换到switch to SAE6000-50.ipt", with the English left inside.

The paper settles the formal direction the other way: arXiv v1 says every task has "a Chinese instruction translated by GPT-4 and reviewed by the authors who are fluent in both languages" (checked in the arXiv HTML; the Sep 2025 version says the Chinese was "initially generated using GPT-4, then carefully reviewed and refined by the authors"). That fits what we see: the annotators typed English for Chinese labels, so the English is a word-for-word rendering of the on-screen Chinese, and the reviewed Chinese ended up matching the screen. A plain GPT-4 rendering of "redo", "Front view" or "Shedding the shell" would not give 撤销, 主视图 or 抽壳. So the issue does not say the English was translated from `instruction_cn`. It says the English reads like a word-for-word translation of the Chinese labels, and that where the two fields disagree the Chinese is usually the one that matches the screen. Rendering a label word for word may even help on a Chinese UI; it is only a problem where it changes the meaning (inventor_windows_68, inventor_windows_60) or names a different thing (solidworks_windows_70).

## (e) Byte-identical screenshot files

CONFIRMED: 23 groups, 30 extra copies, so 1,551 distinct images behind 1,581 image files (every case has its own file name; no file is shared). No group repeats an instruction, and no two keys in a group overlap except a 0.08 IoU sliver in vivado_windows_1 / _25 (two different instructions). So these are distinct tasks on the same screen saved twice, which is harmless for scoring.

Related count: the HF repo ships 1,585 PNG files, 4 of which no annotation uses: `common_windows/screenshot_2024-11-06_19-40-32.png`, two byte-identical 12 KB Stata files (`stata_windows/screenshot_2024-12-05_20-25-06.png` and `..._20-25-24.png`), and a byte copy of the used `common_mac/Screenshot 2024-11-07 at 1.58.03 PM.png` whose name has a narrow no-break space (U+202F) before "PM". That explains why `eval.yaml` (written by HF staff, HF PR #3) says "1,585 annotated images" while the annotation files hold 1,581 cases. Left out of both drafts.

Does it matter? A little: the paper says ScreenSpot-Pro "includes 1,581 instructions, each in a unique screenshot" (arXiv v1, checked), and 1,551 distinct images contradict that. Scoring is unaffected. The issue keeps it to one line under minor notes, which Arthur can cut.

## (f) Judgment calls

Examples checked by eye, all CONFIRMED as fair judgment calls (opinions, the key can stay):
- **matlab_macos_70** "create a filled area plot for selected variables": the open plot gallery shows the same "area" command twice, under FAVORITES [about 256, 111, 325, 172] and under MATLAB LINE PLOTS (the key, [478, 213, 547, 274]). Figure: `fig_matlab_70_area_twice.png`.
- **matlab_macos_13** "add a new script": key = the "New" dropdown [111, 54, 149, 123]; the "New Script" button at the left edge of the same group [about 5, 54, 42, 123] does it in one click. Figure: `fig_matlab_13_new_script.png`.
- **eviews_windows_26** "choose use the same proxy server for both": key = the 13 x 12 px checkbox square [1066, 676, 1079, 688]; its label [about 1081, 674, 1256, 691] toggles the same Win32 checkbox. Figure: `fig_eviews_26_checkbox_label.png`.
- **vivado_windows_73** "generate bitstream in viavdo": key = the toolbar's Generate Bitstream icon; "Generate Bitstream" is also in the Flow Navigator under PROGRAM AND DEBUG. Not used in the issue.

Counts for the issue, from the current audit (they may still move by a case or two): of the 905 missed cases, 24 two valid answers, 18 partial control, 18 loosely worded. The issue lists inventor_windows_68 (one of the 24) and 10 of the 18 loose ones (#101, #110, #364, #485, #751, #823, #1097, #1133, #1149, #1296) in its wording section, so its judgment-call line says 23 / 18 / 8.

## Dropped, with reasons

- matlab_macos_23 / _50 and quartus_windows_8 / _35: different UI states; each key is right for its own screenshot.
- inventor_windows_64, linux_common_linux_35 and the other loose English-UI cases: loose in both languages, not label errors; counted among the judgment calls only.
- Byte-identical files: kept as a one-liner only, since they do not affect scoring (but they do contradict the paper's "each in a unique screenshot").
- The 4 unused image files and the eval.yaml count: repo hygiene, left out.
