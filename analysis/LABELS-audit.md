# Label audit of the missed cases (ScreenSpot-v2, Jev 1.14 box)

Oct 16 2026. A side note to REPORT.md. **The score is always the official answer key. Nothing here re-scores anything.**

Question (Arthur, Oct 16): some ScreenSpot-v2 instructions fit more than one element, like #1095 "search result". How many of Jev's misses are like that?

Reproduce: `python3 analysis/labels_audit.py` (counts, checks, scans) and `python3 analysis/label_figures.py sheets` / `full CASE ...` (figures).

## Method

- **Scope:** every case at least one run missed, 271 of 1272. The runs are A1 = pass 1, A2 = pass 2 (same request again) and B = the zoom answer.
- **Two sets, by distance.** The wrong-element set (151 cases) has at least one click more than max(25 px, half the target's short side) outside the key box. In the near set (120 cases), every miss is closer than that.
- **By eye.** Every case was drawn with the key and all three answers (`analysis/label-audit/sheets/`), and every one was looked at. Full-screen views were made wherever the tile was not enough. For the Wikipedia portal tiles, the live wikipedia.org HTML was checked: each tile is one link that holds the icon, title and tagline.
- **One code per case, with a one-line reason:** `analysis/label-audit/verdicts_wrong_element.txt` and `verdicts_near.txt`. The script checks that every missed case has exactly one verdict.
- **Automated scans** run over all 1272 answer keys, not only the missed ones.

## Result: 43 of the 271 missed cases have a label issue

| Group | Cases | A1 misses | A2 misses | B misses | All three miss |
|---|---|---|---|---|---|
| Answer-key error | 4 | 4 | 4 | 4 | 4 |
| Two valid answers | 18 | 18 | 16 | 14 | 13 |
| Same control, key covers part of it | 12 | 12 | 11 | 8 | 7 |
| Loose wording, key still the best | 8 | 8 | 7 | 8 | 7 |
| Cannot verify | 1 | 1 | 1 | 1 | 1 |
| **Label issues** | **43** | **43** | **39** | **35** | **32** |
| Wrong element (model error) | 105 | 78 | 83 | 69 | 44 |
| Right element, click off | 109 | 90 | 77 | 36 | 20 |
| Zoom crop cut the naming label | 14 | 1 | 0 | 14 | 0 |
| **Label-fine** | **228** | **169** | **160** | **119** | **64** |
| All missed cases | 271 | 212 | 199 | 154 | 96 |

What it means:
- About one miss in five sits on a label issue: 43 of A1's 212, 39 of A2's 199, 35 of B's 154.
- Jev reads these cases the same way every time. All three runs miss 32 of the 43. In the wrong-element set, all three miss 18 of the 20 two-answer and same-control cases. That makes them a consistent alternative reading, not noise.
- Web has most of them (28), then mobile (12) and desktop (3).
- The 4 key errors cost Jev 2 hits in A1, 2 in A2 and 3 in B (0.16 to 0.24 pp): with a corrected key those answers would be hits. That correction is not applied.
- The other 228 are real model errors. Against its own first answer (A2), zoom fixes most of the "right element, click off" misses (77 down to 36). It barely touches the wrong-element ones (83 down to 69), and it adds the 14 crop misses.

## The 43 cases

### 1. Answer-key errors (4). All three runs miss each one.
- **#458** "switch on automatic downloads using cellular data" (mobile). The key box is a copy of #455's box (a keyboard key on a different screenshot) and lands on empty space beside the Wireless Data icon. All three answers are on the Automatic Downloads toggle under Cellular Data, which is right.
- **#487** "switch the temperature display to Fahrenheit" (mobile). The key is on the Notifications row. All three answers are on "Fahrenheit F".
- **#1035** "log in by x account" (web). The key is on the YouTube icon, and X is two icons to the left. The other two keys on this screenshot are right. Jev lands on the f/X pair, none of the answers cleanly on X.
- **#1037** "check the weather news" (web). The key is on "DelmarvaLife", and the Weather menu item is two to the left. B lands on Weather; A1 and A2 land between News and Weather.

### 2. Two valid answers (18). The instruction fits Jev's element about as well as the key's.
- #4 "view the menu": key = sidebar toggle; Jev picks a dropdown chevron, which also opens a menu.
- #89 "view more information": key = the ... menu; Jev picks the MORE link. On the same screenshot, #91's key is that MORE link.
- #94 "view ore details" (typo): key = the ... circle; Jev picks "Learn More".
- #342 "turn off rule-based mode": the key is the already-selected Rule-based radio. Turning it off means picking another mode, and that is where A1 and A2 land.
- #387 "tap the icon for displaying more functional": key = the (+) top right; Jev picks the "More" app icon.
- #455 "switch to uppercase input": key = the "abc" key; A2 and B press Shift, which also gives uppercase.
- #461 "adjust the camera focus": key = the focus slider; A1 picks the tap-to-focus square, which fits. A2 and B pick the shutter, which does not.
- #563 "switch to english": two English entries (UK and US); A1 and A2 box both of them.
- #623 "view the game for me": key = the "Games for you" header; Jev picks the first game in that section.
- #734 "view attachment": two paperclips; Jev picks the one in the message header.
- #869 "check my followers": B picks the Followers profile tab, which also lists followers.
- #972 "add comment": fits both the comment box (the key) and the Post button, which B picks.
- #1031 "create a new page": all three pick the sidebar link "Create new page", the exact wording. The key is the "Create this page" button.
- #1058 "click the button to navigate to boston": A1 and A2 pick the Boston search result, which also moves the map there.
- #1070 "check the direction of slight left onto hancock street": steps 4 and 5 have exactly that text.
- #1160 "input keyword in the searchbar": two search bars; Jev picks the one in the header.
- #1165 "show content of reinforcement learning": A1 and A2 pick the article link, the key is its [show] toggle. Weak: "show" matches the toggle.
- #1214 "Switch the language that needs to be translated to Chinese": reads as either the source or the target side. B picks target-side Chinese at confidence 0.80; the key is the source side.

### 3. Same control, the key box covers only part of it (12)
Jev clicks a part of the same control that the key box leaves out. On a real screen, the click would work.
- Radio buttons and checkboxes clicked on their label: #896, #897, #1135, #1233, #1236.
- #5 "select source language": the key covers only the chevron of the language pill; Jev boxes the whole pill.
- #1075 "the starbucks located in auburn street": the whole result is one link, and the key marks only its first word.
- #1093, #1109, #1110 (Wikidata, Wikispecies, MediaWiki portal tiles) and #1096 (the Wikipedia footer logo): each is one link, and the key marks only the title.
- #1217 "click the current date": the line reads "Wednesday September 25", and the key marks only "September 25".

### 4. Loose or broken wording, the key is still the best answer (8)
- #314 "search for the privacy report of a website": the wording names the visible Privacy Report card. The key is the address bar.
- #856 "click the icon to sort by created date": A1 and A2 pick the "Created date" dropdown that the wording names, not the sort-direction icon.
- #910 "has question about scope": all three pick the Scope dropdown, not its ? help icon.
- #986 "view the comments of the first book": there are no books on the page, only relationship posts.
- #1095 "search result": Jev boxes the search field, the key is the search button. This is the case that started the audit.
- #1097 "goto france wikipedia": the page is the Wiktionary portal, so its Francais link opens French Wiktionary. Jev picks the footer Wikipedia link instead.
- #1186 "check the price changes for the first item": no price-history control exists. The key is the Add to Compare icon.
- #1188 "switch the product arrangement to a 2*2 grid": no 2x2 icon exists. The key is the List view icon; Jev picks Grid view.

### 5. Cannot verify (1)
- #281 "choose watercolor brush style": the icons do not say which tool is watercolor.

## Recurring error patterns (for the write-up)

| Pattern | Cases | A1 | A2 | B |
|---|---|---|---|---|
| Picks the option that is already selected | 15 | 13 | 14 | 13 |
| Previous instead of next, left neighbour | 4 | 4 | 4 | 4 |
| Picks the named noun, not its control | 10 | 8 | 9 | 5 |
| One box over two candidates | 3 | 3 | 2 | 2 |
| Boxes a whole group or quantity | 2 | 2 | 2 | 2 |

- **Selected-state pull:** #11, #61, #127, #129, #194, #218, #668, #688, #719, #799, #841, #1120, #1142, #1155, #1192. Example: #127 "set focus time to 60 mins", where all three runs pick the highlighted 30 mins.
- **Previous/next:** #121 and #437 "play next song" pick previous. On #926 and #1240 "next page", A1 and A2 pick the page field or a tile, and B picks the previous arrow.
- **Label-name pull:** #1038 "follow sadie gurman" picks the author name, not Follow; #860 and #1159 pick the chip text, not its x; #1195 and #1264 pick the field, not its button. The others: #856, #906, #907, #910, #1009 (#856 and #910 are also in the loose-wording group).
- **Blend boxes:** #563, #869, #986, all on label-issue cases where two candidates are on screen. **Group boxes:** #1200 "rate with four stars" boxes the first four stars; #953 boxes the page group.
- Zoom helps on label-name pulls (9 misses in A2, 5 in B) and not on selected-state pulls (14 in A2, 13 in B).

## Dataset scans (all 1272 keys)

- 730 screenshots, 358 of them with more than one case.
- One key box is used on two different screenshots: #455 and #458. #458's copy lands on empty space (key error 1 above).
- No two different instructions on the same screenshot share a key box or have overlapping ones (IoU 0.3 or more).
- One duplicate test case: #1017 and #1021 have the same screenshot, instruction and key.
- No empty key boxes. One key box runs 1 px past the right edge of its screenshot (#449); all three runs hit it.
- Typos: #457 "calandar", #235 "massages", #94 "ore details", #385 "a emoji", #407 "softwares", #833 "show previous" (previews), #247 "link attributes" (Ink).

## Limits

- Only missed cases were audited. Ambiguous instructions that Jev happened to hit are not counted, so 43 is not a dataset-wide error rate.
- One auditor, by eye. The codes are judgment calls, mostly two valid answers vs model error. Every case has its reason written down, so anyone can disagree case by case.
- The key is the same for every model, so published comparisons stay fair: every model loses the same 4 key-error cases.

## Corrections to what was said earlier in the session

- "Every one of the 1,272 cases has a target that really is on the screen, with a true box" (18:38 UTC) was wrong for 4 cases. #458's key sits on empty space, and #487, #1035 and #1037 mark the wrong element.
- "ScreenSpot-v2 is already the OS-Atlas cleanup of v1" is true, but ambiguity is left: 43 of the 271 missed cases.
