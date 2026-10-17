# ScreenSpot-Pro label audit: quality-pass notes (Oct 17 2026, final at 11:15 CEST)

The working record of my pass over the 14 reviewer batches. The results are in `analysis/LABELS-audit-pro.md`, and every change below is in `analysis/labels_audit_pro.py` (OVERRIDE, KEY_FIX, ON_OTHER), printed on each run.

## Changes to the reviewers' verdicts (34)
- **Typo rule, as on v2 (24):** a plain typo whose meaning is clear is not a label issue, so the case keeps the model code the reviewer gave or named. Recoded from VAGUE: 322, 335, 480, 568, 591, 633, 656, 676, 726, 778, 796, 860, 975, 984, 1002, 1004, 1005, 1008, 1061, 1375, 1438, 1439, 1526, 1556. The batches had applied the rule unevenly.
- **Two valid answers (2):**
  - 1493: B aims at the nav pane's Data (D:), which also opens D.
  - 759: a blend box over both scatter controls, like v2's #563.
- **New group, same request with two different keys (2):** 992, 1025, the PyCharm pair #992/#1025. At first 639 and 1069 were in it too (pairs #639/#666 and #1042/#1069); the upstream check (Oct 17, `upstream-issue-pro/VERIFY.md`) found a menu open in one shot and closed in the other, with each key right for its own screen, so both keep their reviewers' codes (PRECISION; MODEL SAMEGROUP). Checked by eye. The batch 10 reviewer had coded the PyCharm pair VAGUE.
- **Origin full-height columns (6):** 711, 728, 730, 738, 739, 758, recoded PRECISION -> MODEL OTHER. Batch 07 coded the same pattern MODEL in 754, 755, 765 and 770. The box is a full-height column whose centre lands mid-screen, about 1,000 px from the toolbar key. 735 stays WIDE, because its column holds the key.

## Checked by eye
- **The 3 key errors:** #133 (green Y arrow for an X request) and #657 (FontSize for font weight).
  - #491: the key is Undo's history dropdown for "redo". The Chinese instruction says undo (撤销), so the English translation is the wrong part there.
  - KEY_FIX = {133: none, 491: none, 657: B}. A2's raw hit on #657 sits on the wrong key.
- **The 24 two-answer cases:**
  - B's click is on the other valid element in 17: 5, 20, 121, 184, 199, 257, 629, 686, 869, 877, 890, 937, 1255, 1297, 1313, 1443, 1467.
  - In the other 7 it lands beside it: 499, 539, 679, 759, 838, 977, 1493.

## Spot-check: 30 random verdicts, seed 20261017
- **Sample:** 62, 164, 225, 320, 340, 346, 354, 358, 462, 511, 568, 591, 738, 801, 818, 901, 912, 953, 966, 971, 985, 1025, 1032, 1035, 1046, 1083, 1202, 1291, 1376, 1440.
- **Agree as coded:** 25.
- **Agree after the typo rule:** 568, 591. **After the twin rule:** 1025.
- **Boundary call, kept:** 225. B boxed the label in the target's own row, which the written PRECISION code covers.
- **Disagree:** 738, which led to the six Origin recodes.
- **The 55 breaks:** the reviewers match the deep audit's classes in 48. The 7 others are precision vs neighbour boundary calls (26, 333, 746, 857, 1071, 1091, 1279).
