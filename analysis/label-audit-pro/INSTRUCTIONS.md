# Reviewer instructions: ScreenSpot-Pro label audit (by eye)

You are auditing Jev 1.14's misses on the ScreenSpot-Pro GUI-grounding benchmark, by eye, for a write-up. Repo: `/home/bionics/jev-screenspot`. You only read files, run the zoom helper below, and write your two output files. Never run `screenspot.py` or anything that calls an API, and never edit any other file.

## Background
Each case is one screenshot of a professional app plus one English instruction. Jev answers with a box; the click is the box centre; it is a hit if the click is inside the answer-key box. Every case has three answers:
- **A1** (red) = raw pass 1, **A2** (purple) = raw pass 2 (the same request again),
- **B** (orange) = the zoom answer: a second call on a 2x crop around A2's box, mapped back to the full screenshot. **Grey** = B's crop window.
- **Green** = the answer key, drawn 3 px outside its box so it does not hide the target.

Every case in your list is one where B missed. The official key stays the score: this audit is a side note to understand the misses and to find label problems.

## Step 1: the misses
Your case list is `analysis/label-audit-pro/batches/batch_NN.tsv`: one row per case, with the instruction, the key box and each run's click in ORIGINAL screenshot px.

For every case, in order, Read `analysis/label-audit-pro/cases/case_NNNN.jpg` (4-digit case number). Layout:
- Header: case, group / app, type, screen size, each run's result and confidence, the instruction.
- Left: the whole screenshot with every mark and the two zoom panels outlined. Under it are hints: each run's distance from the key box (px in the image Jev saw for the full screenshot), whether B's box is too wide (it holds the key centre), whether the key centre was inside B's window, and the key's size.
- Middle: the area around the key.
- Right: the area around the farthest missing answer (B first, then A2, then A1), or a close-up of the key when every answer is near it.

If you cannot tell what the key element or B's element is, take a closer look:
`python3 analysis/pro_label_figures.py zoom CASE CX CY SIDE OUT.jpg`, with CX, CY and SIDE in original px from the TSV (SIDE about 200-400) and OUT in `/tmp/claude-1000/-home-bionics-Desktop-MillionMyLife/70513a22-bb79-46e4-91f0-355ab37e7dde/scratchpad/zoom/`. Then Read OUT. Use it only when the case image is not enough.

Write one line per case to `analysis/label-audit-pro/verdicts/batch_NN.txt`:

    case | code | tag | named | lang | note

**code**: exactly one. It describes B's answer; a label issue overrides a model error.

Label issues:
- `KEYERROR`: the key box sits on the wrong element or on empty space.
- `ARGUABLE`: the instruction fits B's element about as well as the key's (two valid answers).
- `SAME`: B's element is the same control, and the key box covers only part of it. The click would work on the real screen.
- `VAGUE`: wording loose, broken or misspelt, but the key is still the best answer.
- `UNSURE`: cannot be verified from the screenshot.

Model errors (the label is fine):
- `MODEL`: B's element does not fit the instruction and is not next to the target (wrong element).
- `NEIGHBOUR`: B's click is on the control right next to the target.
- `WIDE`: B's box spans the target and its neighbours (or a whole group or row), and its centre lands beside the target.
- `EDGE`: B is on the right element, with the click a few px outside the key box.
- `PRECISION`: B is on the right element or the bar, row or group holding it, with the click off it, and neither WIDE nor EDGE fits.
- `CROP`: B's crop cut the label or context that names the target (the grey window edge cuts the target or its label), so B picked something else.

**tag**: what B confused the target with. Only for MODEL, ARGUABLE and CROP; write `-` for every other code.
- `SAMETEXT`: B's element shows the instruction's word(s), the same text in the wrong place.
- `LOOKALIKE`: B's element looks like the target (similar icon or control).
- `RELATED`: functionally related: the named object's label instead of its control, a parent menu, tab or panel, the field instead of its button, or the opposite action.
- `SAMEGROUP`: the same toolbar, menu or panel as the target, a different item (not adjacent).
- `SELECTED`: the currently selected or highlighted item.
- `OTHER`: no visible relation.

**named**:
- `Y`: visible text at or right next to the target names it, in any language (a button reading "Insert" or "插入", a menu item with the instruction's word).
- `N`: no visible text names the target (an unlabelled icon, a slider, a spot on a canvas). Finding it needs knowing what it looks like or does in this app.

**lang**: the interface language around the target: menus, buttons and labels, not document content. `EN`, `ZH` or `OTHER` (say which in the note).

**note**: one line, under 160 characters. Say what the key is and what B picked (and A2, if different and telling). For a label issue, give the reason.

### Examples
From the v2 audit (same codes):
- `4 | ARGUABLE | view the menu: key = sidebar toggle; Jev picks the dropdown chevron, which also opens a menu`
- `5 | SAME | select source language: key = chevron only; Jev boxes the whole language pill (same control)`
- `37 | MODEL | open the app store: all three pick 'Apple Store' (look-alike name) instead of App Store`

From Pro, already reviewed (use them as they are):

    3 | MODEL | LOOKALIKE | N | EN | collapse all TODO: key = collapse-all icon of the TODO tool window; B picks the same collapse icon in another panel's toolbar (key outside B's window)
    28 | WIDE | - | Y | EN | filter to warm: key = Warm tile; B's box spans Enhance + Warm, centre between them; A1/A2 hit
    81 | NEIGHBOUR | - | Y | ZH | Insert Block: key = 插入 (Insert) button; B clicks the next button 编辑属性; A1/A2 on a drawing tab far off
    431 | NEIGHBOUR | - | Y | ZH | Mark dimensions: key = 尺寸 (Dimension) button; B clicks a constraint icon in the 约束 group next to it
    1119 | WIDE | - | Y | ZH | drop down for moving the entity: key = small arrow beside 移动实体; B's box spans the 3-item group, centre on 线性草图阵列
    1294 | WIDE | - | N | EN | group by repository: key = group-by icon; B's box covers it and the Status header below, centre on the key's bottom edge

### Judgment rules
- Be strict with label issues. KEYERROR only when the key clearly marks something the instruction does not ask for (or nothing). ARGUABLE only when B's element genuinely fits the instruction as well as the key's. When torn between ARGUABLE and MODEL, pick MODEL and say why in the note.
- Use what you know about the app (icons, menus, tooltips) to judge icon targets. Write "by app knowledge" in the note when you rely on it.
- A1 and A2 are context; the code describes B's answer.
- When the hint says the key centre is OUTSIDE B's window, B could not see the target. Still code what B did (usually MODEL or NEIGHBOUR); the geometry is recorded separately.

## Step 2: UI language for every case of your apps, hits included
Read the language sheets listed in your TSV's first line. Each sheet shows 16 cases, with the case number at each tile's top left; green = the key, and each tile shows the UI around the key. For every case number in your apps' ranges (also in the TSV's first line), write one line `case | lang` to `analysis/label-audit-pro/lang/batch_NN.txt` (EN, ZH or OTHER, defined as above). Skip tiles of other apps on the boundary sheets.

## Output files
Each file starts with its comment line:
- verdicts: `# ScreenSpot-Pro label audit, batch NN (apps ...): every case the zoom answer B missed, viewed by eye. Format: case | code | tag | named | lang | note.`
- lang: `# ScreenSpot-Pro UI language, batch NN (apps ...), from analysis/label-audit-pro/lang_sheets. Format: case | lang.`

Append your lines as you go, about every 10 cases (Bash: `cat >> FILE <<'EOF'` ... `EOF`), so nothing is lost. Every case must appear exactly once. Before you finish, check the counts against the TSV.

## Final reply
Plain text, under 300 words:
- counts by code;
- every KEYERROR, ARGUABLE, SAME, VAGUE and UNSURE case, with a short reason;
- the error patterns you saw repeatedly, with case numbers;
- the UI-language split of your apps (counts).
