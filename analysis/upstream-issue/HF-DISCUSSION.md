<!-- DRAFT, not posted. Target: https://huggingface.co/datasets/OS-Copilot/ScreenSpot-v2/discussions/new
     Post after the GitHub issue exists, and replace https://github.com/OS-Copilot/OS-Atlas/issues/65. -->

**Title:** 4 wrong answer boxes and 1 duplicate case

Hi, I found a few labels in ScreenSpot-v2 that look wrong. Indices are 0-based positions in the json files, and boxes are [x, y, w, h]:

- mobile [458] "switch on automatic downloads using cellular data": the bbox [26, 1095, 267, 136] is a copy of mobile [455]'s and lands on empty space. The target is the toggle at about [1010, 2458, 150, 93].
- mobile [487] "switch the temperature display to Fahrenheit": the bbox marks the Notifications row. Fahrenheit is at about [509, 425, 490, 80].
- web [200] "log in by x account": the bbox marks the YouTube icon. v1 had the X icon, [1979, 475, 71, 62].
- web [202] "check the weather news": the bbox marks DelmarvaLife. v1 had Weather, [257, 306, 170, 109].
- web [182] and web [186] are the same case twice.

Details and screenshots are in the GitHub issue: https://github.com/OS-Copilot/OS-Atlas/issues/65

Since published scores use the current key, an errata file might be easier than editing the key in place. Thanks for the dataset.
