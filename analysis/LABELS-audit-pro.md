# Label audit of the zoom answer's misses (ScreenSpot-Pro, Jev 1.14 box)

Oct 17 2026. A side note to REPORT.md and `AUDIT-pro-run2.md`. **The score is always the official answer key. Nothing here re-scores anything.**

Question (Arthur, Oct 17): the same look as on v2. How many of the misses are label problems, what are the rest, and does Pro have broken tasks like v2 had?

Reproduce: `python3 analysis/labels_audit_pro.py` prints the counts, checks, scans and every quality-pass change. `python3 analysis/pro_label_figures.py cases`, `lang` and `zoom CASE CX CY SIDE OUT` make the figures.

## Method

- **Scope:** all 905 cases the zoom answer B missed, out of 1,581. A1 (pass 1) and A2 (pass 2, the same raw request again) are shown as context, and the code describes B's answer. On v2 the audit covered every case any run missed. On Pro that would be 1,386 cases, so it covers B, the number that counts.
- **By eye.** 14 reviewer agents each took a batch of apps and worked from one written code list (`analysis/label-audit-pro/INSTRUCTIONS.md`).
  - Each case image shows the full screenshot with the key and all three answers, a crop around the key and a close-up (`analysis/label-audit-pro/cases/`, not in git).
  - Closer views were made wherever the image was not enough.
  - Icons were judged with app knowledge, marked "by app knowledge" in the note.
- **One line per case,** `case | code | tag | named | lang | note`, in `analysis/label-audit-pro/verdicts/`. The script checks that every B miss has exactly one verdict and that every field is valid.
- **UI language for all 1,581 cases,** read from contact sheets (`lang/`). The two independent language looks (verdict line and language sheet) agree on all 905 B misses.
- **My quality pass,** printed by the script as overrides:
  - **Typos:** 24 verdicts recoded. As on v2, a plain typo whose meaning is clear is not a label issue, so the case keeps the model code the reviewer gave or named. The batches had applied this unevenly.
  - **New group:** 4 recoded into "same request, two different keys" (below).
  - **Two valid answers:** 2 recoded into it. #1493, and #759 as a blend box over both valid controls, like v2's #563.
  - **Origin columns:** 6 recoded from PRECISION to MODEL. The batch 07 reviewer coded the same Origin pattern MODEL in four cases (754, 755, 765, 770) and PRECISION in these six (711, 728, 730, 738, 739, 758). The pattern is a full-height column box whose centre lands mid-screen, about 1,000 px from the toolbar target. That is not a click slightly off, so all ten are now MODEL.
- **Spot-check:** 30 random verdicts (seed 20261017) were re-checked by eye.
  - 25 agree as coded, 2 agree after the typo rule (568, 591) and 1 after the twin rule (1025).
  - #225 is a boundary call. B boxed the label in the target's own row, which the written PRECISION code covers ("the bar, row or group holding it"), so it was kept.
  - One disagreed: #738, which led to the six Origin recodes.
- **The 55 breaks:** the reviewers' codes match the deep audit's own classes in 48. The other 7 are boundary calls between "right element, click just off" and "neighbour" (26, 333, 746, 857, 1071, 1091, 1279).
- **Automated scans** run over all 1,581 keys, not only the missed ones.

## Result: 67 of B's 905 misses have a label issue

| Group | B misses | A2 also missed | A1 also missed | Text | Icon |
|---|---|---|---|---|---|
| Answer key and instruction disagree | 3 | 2 | 3 | 1 | 2 |
| Two valid answers | 24 | 23 | 23 | 17 | 7 |
| Same control, key covers part of it | 18 | 18 | 17 | 16 | 2 |
| Loose or broken wording, key still the best | 18 | 18 | 18 | 8 | 10 |
| Same request, two different keys | 4 | 4 | 4 | 2 | 2 |
| Cannot verify | 0 | 0 | 0 | 0 | 0 |
| **Label issues** | **67** | **65** | **65** | **44** | **23** |
| Wrong element (model error) | 462 | 442 | 442 | 176 | 286 |
| Right element, click off | 376 | 343 | 340 | 200 | 176 |
| Zoom crop cut the naming label | 0 | 0 | 0 | 0 | 0 |
| **Label-fine** | **838** | **785** | **782** | **376** | **462** |
| All B misses | 905 | 850 | 847 | 420 | 485 |

What it means:
- **Labels are not why Pro is hard.**
  - 67 of the 905 misses (7.4%) have a label issue, against 35 of B's 154 on v2 (23%).
  - If every one of them went Jev's way, B would gain at most 36 hits (2.28 pp): 45.03% at the very most, against 42.76%. The 36 are:
    - 17 two-answer cases where B's click is on the other valid element;
    - 18 same-control clicks that would work on a real screen;
    - 1 key error where B is on the right control (#657).
- **Per case, Pro has more label issues than v2:** at least 4.2% of all cases, vs 2.8%. They are swamped by 838 real model errors.
- **Jev reads these cases the same way every time.** All three runs miss 64 of the 67, as on v2.
- **The model errors split into two kinds of about equal size:**
  - the wrong element, 462 (51% of B's misses);
  - the right element with the click off, 376 (42%).
- **No crop misses (v2: 14).** The zoom window never cut the label that names a target.

## The 67 cases

### 1. Answer key and instruction disagree (3)
- **#133** Blender, "Move the cone one the X axis by dragging it" (Chinese: 拖动以在X轴上移动锥体, the same).
  - The key box is on the green arrow of the move gizmo, which is Y. X is the red arrow, and the corner gizmo shows red +X to the right.
  - All three runs miss; B is at the gizmo centre.
- **#491** Inventor, "redo to a specific history point".
  - The key is the dropdown next to the Undo arrow, which lists the undo history. Redo's dropdown is the next one.
  - The dataset's Chinese instruction reads 撤销操作到某一历史记录, "undo to a history point". So the key matches the Chinese, and the English translation turned undo into redo.
  - The key box also starts at y = -1, the only box in the dataset outside its image. All three miss.
- **#657** MATLAB, "edit font weight in plot" (编辑绘图中的字体粗细, the same).
  - The key marks the FontSize field ("10"). B clicks the FontWeight "B" toggle just below it, the control the instruction names.
  - A2's raw box was too wide and happened to hold the key, so A2 scored a hit on a wrong key and B's correct click scored a miss. This is one of the 55 breaks.

### 2. Two valid answers (24): the instruction fits B's element about as well as the key's
B's click is on the other valid element in 17:
- **#5** Android Studio, "stop the bilibili download": key = pause; B clicks the row's X (cancel), which also stops it.
- **#20** "open device manager": key = the toolbar icon; B picks the Device Manager stripe button on the right edge.
- **#121** Blender, "Transform the size of y axis": key = Dimensions Y; B picks Scale Y.
- **#184** Blender, "Toggle viewpoint shading": all four shading buttons share the "Viewport Shading" tooltip, and the key is one of them.
- **#199** DaVinci, "zoom": key = the viewer zoom dropdown; B picks a timeline zoom button.
- **#257** EViews, "close": key = the dialog's Close button; all three runs pick its title-bar X.
- **#629** MATLAB, "add a new script": key = the New dropdown; B clicks New Script, which does it in one click.
- **#686** MATLAB, "create a filled area plot": key = the area tile in the plot gallery; B clicks the same tile under FAVORITES.
- **PowerPoint:**
  - #869 and #890 "Add (new) comment": key = New Comment in a menu or pane; B picks Insert > Comment on the ribbon.
  - #877 "more font settings": key = the Font dialog launcher; B picks Font... in the open context menu, the same dialog.
- **#937** Premiere, "focus on V6 for editing": key = V6's source-patch slot; B clicks V6's track-targeting toggle.
- **Vivado:**
  - #1255 "click language temnplate": key = the lightbulb icon in the editor; B clicks Flow Navigator's "Language Templates".
  - #1297 "click reports": key = the Reports tab; B clicks the Reports menu.
  - #1313 "generate bitstream": key = the toolbar icon; B picks Flow Navigator's "Generate Bitstream".
- **Windows:**
  - #1443 "cancel the file search": key = the X in the search box; B clicks "Close search" in the command bar.
  - #1467 "enter downloads folder": key = Downloads in the Start footer; B clicks Downloads in Explorer's nav pane.

In the other 7, B aims at the other valid element and lands just beside it:
- **#499** Inventor, "Front view" (主视图). In drafting, 主视图 is the front view, and that is how the English reads. In Inventor's Chinese UI, 主视图 is the Home View button, which the key marks. B boxes the ViewCube's front face (前), with the click on the cube's top edge.
- **#539** Ubuntu Files, "go back to home dir": key = Home in the sidebar; B boxes the Home crumb in the path bar, with the click just below it.
- **#679** MATLAB, "create a histogram": key = the tile in the gallery; B goes for the same tile under FAVORITES, with the click in the gap beside it.
- **#759** Origin, "select the scattor plot" (选择散点图).
  - Two scatter controls are on screen: the gallery button, and the item in the open fly-out (the key).
  - B's box spans both, with its centre on the fly-out header: a blend box, like v2's #563.
  - A1 and A2 hit, so this is one of the 55 breaks.
- **#838** PowerPoint, "Add new comment": key = New Comment in the open menu; B's box spans Action and Comment on the ribbon, with the centre on Comment's edge.
- **#977** PyCharm, "add new run configurations": key = the "Add new..." link; B's box spans the toolbar + and -, with the centre in the gap.
- **#1493** Windows, "go back to volumn D": key = the Data (D:) crumb; B aims at Data (D:) in the nav pane, with the click just below it.

### 3. Same control, the key box covers only part of it (18)
On a real screen, B's click would work.
- **A checkbox or toggle clicked on its own caption:** #56 (Android notification dot), #255 (EViews proxy), #285 (Excel "(blank)"), #375 and #382 (FL Studio), #967 and #981 (PyCharm Amend), #1264 and #1267 (Vivado).
- **A field or bar clicked beside the part the key marks:**
  - #157 (Blender name field), #378 (Kontakt MIDI channel value), #384 (FL Studio plugin slot);
  - #586 (Chrome tab strip next to +), #637 (MATLAB section header), #696 (MATLAB workspace row).
- **The key box stops a few px short of the real control:** #237 (EViews Font button), #243 (EViews Edit menu), #1456 (Windows "Show more options" row).

### 4. Loose or broken wording, the key is still the best answer (18)
Pro stores a Chinese instruction (`instruction_cn`) next to the English one. On the Chinese-UI apps, the English often reads as a literal translation of it:
- **#101** AutoCAD, "Benchmark Identifier" for 基准标识, which is the datum identifier.
- **#110** AutoCAD, "Extract Annotation" for 引出注释: the key is the Leader Note button (引线注释).
- **#1097** SolidWorks, "Shedding the shell" for 抽壳 (Shell).
- **#1133** SolidWorks, "Insert coordination" for 插入配合 (Insert Mate).
- **#1149** SolidWorks, "Annotation size" for 标注尺寸: the key is Smart Dimension.
- **#1117** SolidWorks, "jump to the selection" for 转到选中项: the key is Go To.
- **#485** Inventor, "Draw a curve." for 画圆弧, "draw an arc": the key is Arc.

Loose in both languages:
- **#495** Inventor, "Place constraint": names the open dialog, while the key is one constraint type.
- **#751** Origin, "import into excel" (导入到Excel): the key imports from Excel.

On English UIs:
- #268 EViews "expand the file structure";
- #364 FL Studio "use smart fine tool" (also in the Chinese: 智能精细);
- #376 "scrolls to reach time markers";
- #381 "change the size" (of what?);
- #536 "split a new terminal tab" (GNOME Terminal has no split);
- #563 "preview the image I'm editing" (it is a video);
- #823 PowerPoint "Und" (cut short; the Chinese reads 撤销, Undo);
- #952 Premiere "media browser tag" (tab);
- #1296 Vivado "open IP properties" (the key is that pane's help button).

### 5. Same request, two different keys (3 pairs, 4 of B's misses)
Each pair has the same app, the same words and a near-identical screenshot (under 2/255 mean grey difference), with two keys that do not overlap. Both keys are defensible, so a model that answers the same way twice can score only one of each pair.
- **#639 / #666** MATLAB, "brush data points": one key is the brush icon in the axes toolbar, the other a region of the plotted data. B misses #639 and hits #666.
- **#992 / #1025** PyCharm, "show problem details": one key is the Problems tool-window title, the other its "File 18" tab. B misses both.
- **#1042 / #1069** Quartus, "Compilation Report": one key is the item in the open Processing menu, the other the toolbar button. B hits #1042 and misses #1069.

## Recurring error patterns (for the write-up)

What B confused the target with, on its 325 MODEL misses:

| Tag | MODEL misses | Example |
|---|---|---|
| No visible relation | 110 | #406 empty canvas beside the toolbar |
| Same toolbar or panel, another item | 69 | #1046 another Quartus toolbar icon |
| Related: label, parent, field, opposite | 63 | #971 the plugin logo, not Install |
| Same words in the wrong place | 39 | #1371 markdown source, not the link |
| Look-alike icon or control | 34 | #911 Source monitor, not Program |
| The selected or highlighted item | 10 | #842 the selected Home tab |

- **Unlabelled icons.**
  - 423 of B's 485 icon misses have no visible text that names the target. Text misses: 36 of 420.
  - Over all codes, 60% of the wrong-element misses are unnamed, against 42% of the click-off ones.
  - Finding these needs knowing the app's icons.
- **The first look went to the wrong region.**
  - In 151 of B's misses (17%), the key centre was not inside B's window at all, because A2's answer was elsewhere. 136 of these are MODEL.
  - No crop can fix them; they need a different first step.
- **Boxes too wide (WIDE 252, the biggest click-off code).** B's box spans the target and its neighbours, and the centre lands beside the target, often on the line between two buttons. Examples: SolidWorks (#1083, Sketch and Evaluate tabs), Vivado (#1291, Libraries and Compile Order), Photoshop tool-column strips (#772, #784).
- **Full-height columns.**
  - 15 of B's boxes are at least half the screen tall, 11 of them on Origin. Only 1 hits. A2 has 30 of them, 18 on Origin.
  - On Origin, 27 of the 62 keys sit in the bottom 10% of the screen (the plot toolbars). B hits 3 of those 27 (A2 1) and 8 of the other 35.
- **Same words elsewhere:**
  - FL Studio's hint bar repeats the hovered control's name, and B picks the hint (#368, #385, #396);
  - Photoshop tooltip previews (#811, #818);
  - a tooltip that repeats the instruction (#857);
  - a Finder preview line quoting the instruction itself (#1358).
- **Selected-state pull:** in PowerPoint, Quick Access Toolbar targets are answered with the selected Home tab below them (#842, #853, #878).
- **Neighbour swaps:** Quartus Save instead of Save All (#1045, #1066).
- **The wrong one of two look-alike panels:** Premiere's Source monitor instead of the Program monitor (#911, #935, #955).
- **App frame vs content:**
  - Android Studio emulator controls are looked for on the phone screen instead of the emulator toolbar (#15, #31, #55, #73);
  - AutoCAD targets are looked for in a WPS document window open beside it (#89, #96, #100).

## UI language (all 1,581 cases)

| UI language | n | A2 raw % | B zoom % | B 95% CI | Text B % | Icon B % |
|---|---|---|---|---|---|---|
| English | 1286 | 21.0 | 45.6 | 42.9-48.4 | 60.7 | 20.9 |
| Chinese | 295 | 8.5 | 30.2 | 25.2-35.6 | 40.4 | 14.5 |

- **295 cases ask in English about a Chinese interface:** AutoCAD 34, Inventor 70, Origin 62, SolidWorks 77 and Stata 49, plus one case each in PowerPoint (#837), PyCharm (#999) and Windows (#1453).
- **Zoom adds about the same in both:** +24.6 pp on English UIs and +21.7 on Chinese ones.
- **Language and app cannot be separated.** Each of the five apps is entirely Chinese.
  - The Chinese apps score 17.7-34.3 after zoom: Origin 17.7, AutoCAD 32.4, Stata 32.7, SolidWorks 33.8, Inventor 34.3. All five are below the English-app median of 41.2.
  - But 6 of the 21 English apps score as low: Premiere 25.0, Windows 28.4, Quartus 28.9, Illustrator 29.0, Excel 32.8, DaVinci 34.1.
  - Within a group: CAD's English app Vivado 48.8 vs its Chinese ones 32.4-34.3. Scientific: MATLAB 60.2 and EViews 74.0 vs Stata 32.7 and Origin 17.7.

## Dataset scans (all 1,581 keys)

- **Duplicate cases, 2 pairs:** #94 / #105 (AutoCAD "Threaded blind hole tool") and #432 / #474 (Inventor "Paste"). Each pair has the same words, near-identical screenshots and overlapping keys (IoU 0.78 and 0.85). B hit one and missed the other in both pairs.
- **Same request, two different keys, 3 pairs:** the pairs in section 5. 15 more same-app, same-words pairs sit on clearly different screens, which is fine.
- **Byte-identical screenshots, 23 groups.** The 1,581 files hold only 1,551 distinct images: 30 files are exact copies of another case's screenshot under a different name. Harmless for scoring, but "one screenshot per case" is not quite true.
- **One key box outside its image:** #491, `[135, -1, 151, 19]` on 3840x1080 (also case 1 above).
- **Other checks:** no key box is reused on a different screenshot (v2 had one copied box), and no key box is under 8 px on a side.

## Compared with v2

| | v2 | Pro |
|---|---|---|
| Audited | 271 (any run missed) | 905 (B missed) |
| Label issues among B's misses | 35 of 154 (23%) | 67 of 905 (7.4%) |
| Answer-key errors | 4 | 3 |
| Two valid answers | 18 | 24 |
| Same request, two keys | 0 | 3 pairs |
| Duplicate cases | 1 | 2 |
| Crop misses | 14 | 0 |
| Most label issues by platform/group | web | CAD, Creative, Scientific |

## Limits

- Only B's misses were audited. Ambiguous instructions that B happened to hit are not counted, so 67 is not a dataset-wide error rate.
- 14 reviewer agents plus one quality pass, by eye. The codes are judgment calls, mostly at the borders: two valid answers vs model error, and neighbour vs click off. Every case has its reason written down, so anyone can disagree case by case.
- The key is the same for every model, so published comparisons stay fair: every model loses the same 3 key-error cases.

## Upstream

A draft report for the dataset authors is in `analysis/upstream-issue-pro/`. Nothing is posted without Arthur's go.
