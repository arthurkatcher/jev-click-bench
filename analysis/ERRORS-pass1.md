# Errors in pass1 (Jev 1.14 box, ScreenSpot-v2)

212 misses of 1272 scored. Distance = from Jev's click point to the nearest edge of the true box, in pixels of the image Jev saw (sent px) and as % of the screen diagonal.

| Cell | n | misses | median dist (sent px) | <=10 | 10-25 | 25-50 | 50-100 | 100-300 | >300 | median % diag | box covered target centre |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mobile text | 290 | 21 | 95 | 3 | 4 | 0 | 4 | 8 | 2 | 5.5% | 6 |
| mobile icon | 211 | 36 | 228 | 3 | 0 | 4 | 6 | 8 | 15 | 13.3% | 13 |
| desktop text | 194 | 14 | 15 | 5 | 3 | 5 | 0 | 0 | 1 | 1.0% | 9 |
| desktop icon | 140 | 31 | 10 | 16 | 6 | 3 | 1 | 3 | 2 | 0.8% | 9 |
| web text | 234 | 47 | 13 | 22 | 9 | 3 | 5 | 4 | 4 | 0.7% | 30 |
| web icon | 203 | 63 | 19 | 23 | 14 | 9 | 6 | 9 | 2 | 1.0% | 31 |
| **all** | 1272 | 212 | 24 | 72 | 36 | 24 | 22 | 32 | 26 | 1.4% | 98 |

## Systematic offset (all scored cases)
Mean offset of the click from the target centre, in target widths (x) / heights (y). Positive = right / down.

| Cell | mean x | mean y | hits mean x | hits mean y |
|---|---|---|---|---|
| mobile text | -0.10 | -0.03 | -0.03 | -0.01 |
| mobile icon | -0.18 | +0.36 | -0.02 | -0.00 |
| desktop text | -0.12 | +0.02 | -0.09 | -0.02 |
| desktop icon | -0.14 | +0.04 | -0.03 | +0.03 |
| web text | -0.07 | +0.09 | -0.06 | +0.01 |
| web icon | -0.36 | +0.01 | -0.07 | +0.01 |
| all all | -0.16 | +0.08 | -0.05 | +0.00 |

Direction of misses: left 109, down 42, right 27, up 16, down-right 8, down-left 6, up-left 2, up-right 2

## Two kinds of miss
- **Too-wide box (98 of 212, 46%)**: Jev's box contains the target's centre, but the box is a median 1.75x wider than the target (it boxes the whole search bar, toolbar or row the icon sits in), so the box centre lands beside the target. 49 of these land left of it. Examples: #744 "next page" (target 62x112 sent px, Jev box 1176x61), #331 "search games" (61x52 vs 649x78), #1095 "search result" (77x66 vs 580x62).
- **Off target (114 of 212)**: the box does not contain the target centre; its size is about right (median 0.94x the target width) and it sits a median 40 sent px away, i.e. Jev picked a neighbouring or wrong element. Mobile icon misses are mostly this kind and far away (median 228 sent px).

## Every miss

| # | Cell | Instruction | Target (sent px) | Dist (sent px) | Dir | Conf |
|---|---|---|---|---|---|---|
| 464 | mobile text | show more awards | 167x53 | 2 | up | 0.67 |
| 342 | mobile text | turn off rule-based mode | 255x61 | 4 | down | 0.5 |
| 407 | mobile text | show softwares | 170x50 | 4 | down | 0.59 |
| 11 | mobile text | check shared files | 86x86 | 11 | left | 0.76 |
| 278 | mobile text | switch the map style to satellite | 317x227 | 15 | left | 0.23 |
| 374 | mobile text | display more information | 186x45 | 18 | down | 0.32 |
| 247 | mobile text | switch to show link attributes | 884x58 | 22 | down | 0.51 |
| 297 | mobile text | apply the smooth filter | 128x184 | 72 | left | 0.25 |
| 127 | mobile text | set focus time to 60 mins | 141x139 | 74 | left | 0.44 |
| 98 | mobile text | view shared | 102x92 | 83 | left | 0.27 |
| 37 | mobile text | open the app store | 121x152 | 95 | left | 0.3 |
| 487 | mobile text | switch the temperature display to Fahrenheit | 326x53 | 106 | down | 0.86 |
| 227 | mobile text | change mode | 221x204 | 107 | left | 0.29 |
| 86 | mobile text | view library | 99x94 | 133 | left | 0.28 |
| 61 | mobile text | choose last 10 days data details of battery | 307x54 | 140 | left | 0.5 |
| 224 | mobile text | tap continue button | 284x112 | 153 | left | 0.36 |
| 194 | mobile text | use dark mode display | 327x518 | 169 | left | 0.36 |
| 88 | mobile text | shuffle the music list | 308x91 | 183 | left | 0.34 |
| 91 | mobile text | view more information about classical christmas | 91x46 | 235 | up-left | 0.5 |
| 473 | mobile text | update Google chrome | 138x56 | 409 | left | 0.26 |
| 314 | mobile text | search for the privacy report of a website | 624x85 | 871 | up | 0.36 |
| 262 | mobile icon | remove maps from the desktop | 36x39 | 3 | right | 0.67 |
| 264 | mobile icon | remove chrome from the desktop | 39x37 | 3 | right | 0.74 |
| 346 | mobile icon | open night mode | 80x38 | 5 | down | 0.43 |
| 25 | mobile icon | search in this note | 51x44 | 26 | left | 0.89 |
| 12 | mobile icon | add an event | 48x46 | 38 | left | 0.71 |
| 118 | mobile icon | favorite the music | 69x76 | 43 | left | 0.45 |
| 18 | mobile icon | adjust the voice | 93x190 | 46 | left | 0.71 |
| 281 | mobile icon | choose watercolor brush style | 63x137 | 54 | right | 0.22 |
| 341 | mobile icon | display public ip address | 88x71 | 63 | right | 0.64 |
| 431 | mobile icon | View AirPods playback setting | 64x64 | 64 | down | 0.51 |
| 411 | mobile icon | tap a button to open table lamp in bedroom | 71x88 | 76 | left | 0.71 |
| 226 | mobile icon | click power on | 441x199 | 84 | up | 0.11 |
| 202 | mobile icon | change battery setting for better performance | 244x139 | 99 | left | 0.27 |
| 340 | mobile icon | display phone files | 108x97 | 107 | left | 0.19 |
| 218 | mobile icon | show week steps recordings | 167x133 | 107 | left | 0.41 |
| 5 | mobile icon | select source language | 61x76 | 159 | left | 0.68 |
| 169 | mobile icon | start the stopwatch | 181x125 | 177 | left | 0.46 |
| 398 | mobile icon | Set to use the largest font size | 66x78 | 214 | left | 0.2 |
| 385 | mobile icon | add a emoji | 99x111 | 242 | left | 0.19 |
| 331 | mobile icon | search games | 61x52 | 269 | left | 0.25 |
| 298 | mobile icon | open additional options | 69x78 | 274 | left | 0.17 |
| 437 | mobile icon | play next song | 118x118 | 332 | left | 0.46 |
| 121 | mobile icon | play next song | 63x68 | 345 | left | 0.29 |
| 228 | mobile icon | raise air conditioner temperature | 218x197 | 357 | left | 0.3 |
| 129 | mobile icon | customize focus time | 159x146 | 400 | left | 0.5 |
| 387 | mobile icon | tap the icon for displaying more functional | 82x82 | 489 | down | 0.6 |
| 94 | mobile icon | view ore details | 51x52 | 547 | down-left | 0.26 |
| 455 | mobile icon | switch to uppercase input | 177x90 | 596 | down-right | 0.2 |
| 4 | mobile icon | view the menu | 53x44 | 689 | right | 0.36 |
| 461 | mobile icon | Adjust the camera focus | 46x377 | 724 | right | 0.1 |
| 457 | mobile icon | view the calandar  | 405x181 | 772 | down-right | 0.04 |
| 89 | mobile icon | view more information | 53x53 | 833 | down | 0.5 |
| 458 | mobile icon | switch on automatic downloads using cellular data | 151x77 | 840 | down-right | 0.66 |
| 406 | mobile icon | show all downloading apps | 75x97 | 1298 | down | 0.07 |
| 27 | mobile icon | get more information | 51x51 | 1331 | down-left | 0.09 |
| 196 | mobile icon | return upper page | 101x99 | 1380 | down | 0.41 |
| 827 | desktop text | do not save this file | 129x31 | 1 | down | 0.84 |
| 589 | desktop text | go to the desktop | 145x22 | 1 | down | 0.3 |
| 563 | desktop text | switch to english | 299x64 | 5 | down | 0.59 |
| 816 | desktop text | click to restart the computer | 164x19 | 5 | up | 0.45 |
| 564 | desktop text | open the file | 282x28 | 10 | down | 0.51 |
| 688 | desktop text | switch to device | 143x34 | 10 | left | 0.62 |
| 799 | desktop text | switch to apps | 227x39 | 12 | left | 0.82 |
| 814 | desktop text | open google drive | 51x48 | 19 | down-left | 0.89 |
| 658 | desktop text | check microphone | 334x54 | 29 | down | 0.29 |
| 727 | desktop text | view firewall | 139x46 | 35 | left | 0.45 |
| 623 | desktop text | view the game for me | 132x34 | 40 | down | 0.53 |
| 625 | desktop text | click to choose shapes | 42x67 | 45 | down | 0.27 |
| 718 | desktop text | switch to privacy | 146x46 | 46 | left | 0.68 |
| 719 | desktop text | switch to alerts mode | 212x186 | 309 | left | 0.4 |
| 774 | desktop icon | rotate title box | 49x43 | 0 | down | 0.54 |
| 752 | desktop icon | back to previous folder | 59x44 | 0 | right | 0.84 |
| 805 | desktop icon | enlarge the font | 62x65 | 1 | left | 0.76 |
| 783 | desktop icon | select python interpreter | 833x44 | 1 | down | 0.49 |
| 535 | desktop icon | maximize window | 41x33 | 1 | left | 0.95 |
| 746 | desktop icon | back to previous page | 55x59 | 2 | left | 0.63 |
| 591 | desktop icon | input a url | 1267x29 | 2 | down | 0.25 |
| 502 | desktop icon | minimize this window | 36x30 | 2 | down | 0.57 |
| 527 | desktop icon | undo | 32x30 | 2 | down | 0.87 |
| 524 | desktop icon | view the personal account | 40x32 | 3 | down | 0.69 |
| 821 | desktop icon | center the selected text | 24x20 | 4 | up-right | 0.58 |
| 600 | desktop icon | set the second photo as wallpaper | 81x84 | 6 | left | 0.8 |
| 518 | desktop icon | open settings | 41x39 | 6 | right | 0.83 |
| 501 | desktop icon | close this window | 44x34 | 8 | left | 0.87 |
| 618 | desktop icon | click the "back to previous page" button | 41x30 | 9 | right | 0.82 |
| 533 | desktop icon | fill in red | 17x17 | 10 | left | 0.7 |
| 817 | desktop icon | add current webpage to favourites | 18x17 | 15 | right | 0.61 |
| 515 | desktop icon | network and internet settings | 33x44 | 17 | left | 0.38 |
| 707 | desktop icon | add a device | 51x47 | 19 | right | 0.51 |
| 779 | desktop icon | debug | 40x40 | 19 | left | 0.64 |
| 731 | desktop icon | delete this email | 74x87 | 21 | left | 0.7 |
| 760 | desktop icon | save file | 56x56 | 22 | down-right | 0.52 |
| 580 | desktop icon | adjust the volume | 30x36 | 25 | left | 0.49 |
| 606 | desktop icon | click to play the next track | 31x52 | 27 | left | 0.89 |
| 647 | desktop icon | rotate left | 39x44 | 29 | right | 0.41 |
| 649 | desktop icon | view in youtube | 66x56 | 58 | left | 0.77 |
| 833 | desktop icon | adjust the options of  "show previous" | 140x29 | 142 | left | 0.39 |
| 640 | desktop icon | insert an image | 40x36 | 186 | left | 0.19 |
| 734 | desktop icon | view attachment | 90x52 | 212 | up-right | 0.11 |
| 740 | desktop icon | open the image in memo | 1183x736 | 482 | up | 0.34 |
| 744 | desktop icon | next page | 62x112 | 542 | left | 0.22 |
| 1114 | web text | open wikidata article upon earth item | 97x25 | 1 | up | 0.59 |
| 848 | web text | create a new issue | 116x43 | 1 | left | 0.68 |
| 920 | web text | use filters | 124x42 | 1 | down | 0.75 |
| 1194 | web text | sign in the website | 69x29 | 1 | left | 0.84 |
| 1093 | web text | look into wikidata | 84x20 | 2 | down | 0.76 |
| 1070 | web text | check the direction of "slight left onto hancock s | 442x70 | 2 | down | 0.72 |
| 1252 | web text | view the community of minecraft | 114x59 | 2 | left | 0.87 |
| 1134 | web text | open 'retrospect and prospect in computer-based tr | 507x34 | 3 | down | 0.67 |
| 870 | web text | switch to groups view | 86x56 | 4 | left | 0.83 |
| 1155 | web text | switch to talk column | 49x32 | 4 | left | 0.86 |
| 1109 | web text | open wikispecies | 110x22 | 4 | down | 0.81 |
| 1087 | web text | start mapping | 206x50 | 4 | left | 0.64 |
| 1234 | web text | choose downloading docker in mac-apple silicon | 283x40 | 5 | up | 0.78 |
| 1228 | web text | view more information about the airpods item | 64x31 | 6 | left | 0.59 |
| 1092 | web text | download in apple app store | 146x48 | 6 | left | 0.4 |
| 1063 | web text | check communities | 126x32 | 7 | left | 0.89 |
| 886 | web text | view supported cloud | 296x57 | 7 | up | 0.68 |
| 1265 | web text | check shoes under 50 dollars in "shop deals in fas | 127x114 | 8 | left | 0.51 |
| 1224 | web text | install a steam desktop application | 96x25 | 8 | down | 0.85 |
| 1221 | web text | view drama books | 123x18 | 9 | up | 0.91 |
| 989 | web text | check the profile of user knittedjedi | 73x36 | 9 | right | 0.75 |
| 1110 | web text | open mediawiki | 111x24 | 9 | down | 0.66 |
| 1148 | web text | open keras | 73x24 | 11 | down | 0.81 |
| 894 | web text | switch to create | 126x102 | 13 | left | 0.83 |
| 1217 | web text | Click the current date | 200x46 | 14 | left | 0.9 |
| 1096 | web text | check wikipedia | 84x22 | 18 | left | 0.61 |
| 841 | web text | switch to explore projects | 92x59 | 18 | left | 0.78 |
| 1060 | web text | need help | 48x34 | 20 | down-right | 0.42 |
| 953 | web text | page 5 | 28x48 | 21 | left | 0.81 |
| 1051 | web text | export the map data | 85x40 | 21 | down-left | 0.19 |
| 1142 | web text | switch to the discussion page | 122x28 | 25 | left | 0.85 |
| 1074 | web text | goto openstreetmap france | 176x20 | 30 | up | 0.63 |
| 1072 | web text | change the area bounding numbered "42.3768" | 132x52 | 32 | down | 0.5 |
| 1084 | web text | select the html as share format | 75x43 | 38 | left | 0.66 |
| 1038 | web text | follow sadie gurman | 80x34 | 52 | left | 0.9 |
| 1141 | web text | return the homepage of mediawiki | 298x82 | 64 | down | 0.63 |
| 986 | web text | view the comments of the first book | 115x29 | 68 | up | 0.45 |
| 1075 | web text | click the "starbucks" located in auburn street | 92x27 | 79 | down-right | 0.76 |
| 1147 | web text | open arsenal f.c. records and player records webpa | 383x32 | 93 | left | 0.42 |
| 1264 | web text | Click to send the verification code to the specifi | 157x49 | 115 | left | 0.51 |
| 954 | web text | details about dead sea collection salt | 89x62 | 139 | left | 0.21 |
| 1219 | web text | switch the payment option to upgrade program | 275x152 | 176 | left | 0.21 |
| 1216 | web text | add wikipedia to wishlist | 116x33 | 195 | up | 0.28 |
| 1037 | web text | check the weather news | 144x64 | 366 | left | 0.44 |
| 869 | web text | check my followers | 135x44 | 400 | right | 0.31 |
| 1097 | web text | goto france wikipedia | 92x23 | 649 | down-right | 0.4 |
| 1031 | web text | create a new page | 182x53 | 1022 | right | 0.21 |
| 1249 | web icon | upvote MagicJoshByGosh's reply | 48x19 | 0 | up | 0.88 |
| 983 | web icon | support the second book | 35x30 | 1 | down-right | 0.38 |
| 1033 | web icon | close the ad banner | 26x22 | 1 | down | 0.61 |
| 1069 | web icon | close the location labels on the map | 22x22 | 1 | right | 0.39 |
| 1082 | web icon | Click on the marker already added to the map | 32x34 | 1 | right | 0.85 |
| 1153 | web icon | change page language | 208x38 | 2 | down | 0.78 |
| 1052 | web icon | locate to my position | 43x50 | 2 | left | 0.61 |
| 899 | web icon | comment to administrator | 43x32 | 2 | left | 0.41 |
| 936 | web icon | delete carnation breakfast essentials nutritional  | 46x56 | 2 | left | 0.57 |
| 1258 | web icon | Follow the Twitter account of 'Ask PayPal' | 72x29 | 2 | left | 0.83 |
| 1002 | web icon | toggle the open external links in the new tab opti | 27x27 | 3 | right | 0.92 |
| 836 | web icon | view my account profile | 68x42 | 3 | down | 0.69 |
| 904 | web icon | copy the http link | 40x43 | 4 | left | 0.75 |
| 1262 | web icon | View my shopping cart | 38x27 | 4 | left | 0.73 |
| 1196 | web icon | check the information about the first item | 232x321 | 4 | down | 0.16 |
| 1112 | web icon | switch language of current page | 109x35 | 5 | down | 0.88 |
| 1206 | web icon | go to the second page | 14x18 | 5 | right | 0.64 |
| 863 | web icon | Click the thumbs down icon on this issue | 67x39 | 6 | left | 0.91 |
| 1214 | web icon | Switch the language that needs to be translated to | 75x23 | 6 | down-left | 0.25 |
| 1256 | web icon | View the comments on the first article about Musk  | 53x27 | 7 | left | 0.73 |
| 1237 | web icon | Modify the display font size | 62x43 | 8 | left | 0.59 |
| 1186 | web icon | check the price changes for the first item | 29x24 | 8 | up-left | 0.65 |
| 1235 | web icon | Click to mark Anna's comment as unhelpful | 53x23 | 8 | left | 0.68 |
| 1004 | web icon | don't show post previews | 27x28 | 11 | right | 0.94 |
| 1233 | web icon | switch off "keep me logged in" setting | 22x20 | 12 | right | 0.74 |
| 897 | web icon | enable static application security testing | 29x31 | 12 | right | 0.86 |
| 896 | web icon | switch to private visibility level | 34x28 | 13 | right | 0.83 |
| 903 | web icon | copy the ssh link | 39x41 | 14 | left | 0.78 |
| 993 | web icon | choose tag | 756x79 | 16 | down | 0.23 |
| 1188 | web icon | switch the product arrangement to a 2*2 grid | 56x49 | 16 | left | 0.6 |
| 1172 | web icon | confirm leaving the shopping cart | 69x45 | 18 | left | 0.64 |
| 843 | web icon | fork the a11y project | 51x36 | 19 | right | 0.29 |
| 1036 | web icon | share to facebook | 31x29 | 19 | right | 0.77 |
| 853 | web icon | full screen display | 45x40 | 22 | left | 0.33 |
| 1192 | web icon | check the second image | 118x121 | 22 | left | 0.85 |
| 1200 | web icon | rate this product with four stars | 19x34 | 24 | left | 0.64 |
| 1161 | web icon | select to search in all area | 32x37 | 25 | left | 0.24 |
| 1159 | web icon | delete the 'article' tag for searching | 34x34 | 26 | left | 0.78 |
| 1243 | web icon | click to close the privacy information bar | 49x32 | 28 | left | 0.54 |
| 864 | web icon | reply to emoticon | 41x42 | 34 | left | 0.75 |
| 940 | web icon | go to next page | 50x44 | 36 | left | 0.85 |
| 1236 | web icon | Choose to sort from oldest to newest | 20x22 | 39 | right | 0.9 |
| 1179 | web icon | add the creole seasoning to favorites | 37x29 | 40 | left | 0.86 |
| 951 | web icon | sort from largest to smallest | 43x40 | 40 | left | 0.61 |
| 839 | web icon | go to personal homepage | 295x115 | 43 | down | 0.22 |
| 910 | web icon | has question about scope | 58x58 | 50 | left | 0.59 |
| 1248 | web icon | Close the pop-up window in the bottom right corner | 22x22 | 54 | left | 0.57 |
| 856 | web icon | click the icon to sort by created date | 41x42 | 61 | left | 0.66 |
| 860 | web icon | delete the byte blaze assignee | 39x31 | 63 | left | 0.27 |
| 1024 | web icon | check the third result | 1379x130 | 64 | up | 0.39 |
| 972 | web icon | add comment | 686x173 | 70 | down | 0.26 |
| 1035 | web icon | log in by x account | 43x36 | 74 | left | 0.37 |
| 1009 | web icon | close the message box | 28x28 | 113 | left | 0.39 |
| 1195 | web icon | search the products about football | 49x42 | 122 | left | 0.71 |
| 926 | web icon | go to next page | 55x43 | 126 | left | 0.74 |
| 1165 | web icon | show content of reinforcement learning | 57x26 | 135 | left | 0.74 |
| 1073 | web icon | Click the button to inspect map features and view  | 55x57 | 165 | up | 0.57 |
| 1135 | web icon | let website remember account information for no lo | 35x35 | 184 | right | 0.38 |
| 1160 | web icon | input keyword in the searchbar | 919x43 | 231 | up | 0.6 |
| 1095 | web icon | search result | 77x66 | 236 | left | 0.38 |
| 1058 | web icon | click the button to navigate to boston | 48x42 | 249 | down-left | 0.19 |
| 865 | web icon | click to view more information of this issue | 48x48 | 302 | left | 0.21 |
| 1240 | web icon | View the next page of the browse by category secti | 36x91 | 730 | left | 0.33 |
