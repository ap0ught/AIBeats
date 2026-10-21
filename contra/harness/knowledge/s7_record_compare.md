# Stage 7 (Hangar): the record's run measured section by section, against ours

Second-pass builder, 2026-10-12. Record = Angrylanks 9:48.183 (https://www.youtube.com/watch?v=YgtFCclM1jM).
Machine-readable: `knowledge/s7_record_landmarks.json` (the record's camera position every 8 px, its stops, our
runs' rows). Tools: `tools/s7_record_compare.py`, `tools/s7_write_compare_md.py`, `tools/s7_tr.py`.

## How the record was measured

* The video is 60.000 fps; every image is two NES frames woven together (one per field). In the browser the video
  was paused and muted, each frame n was shown by seeking to (n + 0.5) / 60 and drawn to a canvas in the page.
* For every video frame 28250..32500 the background's horizontal shift against the previous frame was found from
  one field (49 scan lines x 256 columns, sum of absolute differences over shifts -1..6 px). The running sum of
  the shifts is the camera position (world x of the left screen edge). **Check: the sum reached 3,583 when the
  boss screen stopped; the true value is 3,584.** No frame had to be repeated (no stale reads, no timeouts).
* Offsets below are video frames counted from the stage's first medal frame (video frame 28262); NES frames =
  video x 60.0988 / 60 (+0.16 %). Tolerance of a landmark: +/-2 frames. Bill is at camera + 128 while he runs.
* What he does at each stop was looked at in magnified stills (6 per screenshot). Not measured: his exact inputs,
  his Barrier pick-up frame to better than about +/-5 frames, his bullets.
* Nothing was downloaded; the tab was closed afterwards.

## The record's stage 7 in one paragraph

lower route on screen 1 (under the five claws), cart 624, rising walls by wall-top jumps, ledge with the three tall walls (shot while walking), lower floor under the claws 1270..1398, cart 1424, B grab, floor, step 1632, ledge 1696, cart 1824, floor, pit 2320 onto the cart 2376, Heartbreak Alley on the LOWER floor WITHOUT STOPPING (Barrier: invincible), trio shot down, six claws with two waits, gunners (one duck), boss.
Alley: camera 2304 -> 2560 in 258 video frames: no stop at all. He is on the lower floor under the seeking claws (seen at video 2420).
Carts: camera px gained against 1 px/frame: cart 624 about 11, cart 1424 about 13, cart 1824 about 14, cart 2376 about 18.
Boss: reveal scroll starts (camera 3488) at video 3638, ends 3733; he is in the air firing forward at 3650, 3690 and 3720 (jump shots at the core's height during the scroll), on the ground at about x 140 at 3745 and walks to the right cap aiming up-forward (x 160 at 3765, 173 at 3784); first explosion 3788 = 150 video frames after the scroll starts, 55 after it ends, about 94 after the door is created (56 frames into the scroll).
Pauses: none seen: every stop of 7+ video frames is one of the stops listed.
After the door: control lost at video 3984, first black 4226, stage 8's medals 4481 = **4,488 NES frames**.

### His stops (every stretch of 7+ video frames without scrolling)

| from video frame (NES) | frames | camera / Bill's x | what he does |
|---|---|---|---|
| 872 (873) | 13 | 792 / 920 | two rising walls on the step: he is already past both (in the air at x 895, y 81 at video 846: the second jump, from the top of wall 1), shoots a soldier on the ledge, lands on the step at x 920 and is held by the ledge's side wall while his third jump rises |
| 1223 (1225) | 21 | 1129 / 1257 | stands on the lower floor (x 1257) waiting for the claw at 1270; the rolling cart is shot (explosion ahead of him at 1232) |
| 1536 (1539) | 19 | 1433 / 1561 | B GRAB: on the cart 1424 from video 1404 (boarded by a late jump), jumps from it at about 1438 to the small ledge (y 144, x 1504), jumps again at about 1492 over the pill box (x 1552, y 96) and shoots it from above (it explodes at about 1530), lands on the pill box's own ledge (x 1561), flashing = Barrier by about 1550, and drops THROUGH that ledge (Down+A: the game holds Bill's X for 17 frames - that is the stop) |
| 2659 (2663) | 14 | 2568 / 2696 | trio of rising walls: stands at x 2696 next to wall 1 firing; wall 1 blows up at 2662, he jumps, walls 2 and 3 blow up at about 2698 and 2710 (shot from the air). By the code's timer his Barrier ends at about video 2700; whether wall 1 died by touch or by bullets was not resolved |
| 2974 (2979) | 12 | 2871 / 2999 | waits for the 8-segment claws at 3014.. |
| 3032 (3037) | 19 | 2918 / 3046 | waits again between the claws (3046) |
| 3216 (3221) | 14 | 3083 / 3211 | ducks a gunner's shot under the low roof (prone at 3224) |

Sum of his stops: 112 frames. He never waits in Heartbreak Alley.

### His camera every 128 px

| camera px | Bill's x | video frame | NES frame |
|---|---|---|---|
| 0 | 128 | the camera rests until about 82 | 82 |
| 128 | 256 | 211 | 211 |
| 256 | 384 | 340 | 341 |
| 384 | 512 | 470 | 471 |
| 512 | 640 | 590 | 591 |
| 640 | 768 | 714 | 715 |
| 768 | 896 | 847 | 848 |
| 896 | 1024 | 989 | 991 |
| 1024 | 1152 | 1116 | 1118 |
| 1152 | 1280 | 1265 | 1267 |
| 1280 | 1408 | 1394 | 1396 |
| 1408 | 1536 | 1509 | 1511 |
| 1536 | 1664 | 1659 | 1662 |
| 1664 | 1792 | 1790 | 1793 |
| 1792 | 1920 | 1899 | 1902 |
| 1920 | 2048 | 2028 | 2031 |
| 2048 | 2176 | 2154 | 2158 |
| 2176 | 2304 | 2283 | 2287 |
| 2304 | 2432 | 2394 | 2398 |
| 2432 | 2560 | 2523 | 2527 |
| 2560 | 2688 | 2652 | 2656 |
| 2688 | 2816 | 2792 | 2797 |
| 2816 | 2944 | 2920 | 2925 |
| 2944 | 3072 | 3076 | 3081 |
| 3072 | 3200 | 3203 | 3208 |
| 3200 | 3328 | 3347 | 3353 |
| 3328 | 3456 | 3477 | 3483 |
| 3456 | 3584 | 3604 | 3610 |
| 3583 (scroll over) | - | 3733 | 3739 |
| door core's first explosion | - | 3788 | 3794 |
| stage 8 medals | - | 4481 | 4488 |

## Section by section: record, first pass (`ph90`, 4631), second pass (`f_chain66`, 4407)

Rows = frames from the stage's first frame. "in it" = frames spent in the section; "at its end" = row at which the
camera reaches the section's end; in brackets the difference to the record at that point (negative = we are ahead).

| camera px | section | record: frames in it / at its end | ph90: in it / at its end (vs record) | f_chain66: in it / at its end (vs record) | f_chain100: in it / at its end (vs record) |
|---|---|---|---|---|---|
| 0-128 | start (Bill drops in; the camera starts when he reaches x 128) | 211 / 211 | 209 / 209 (-2) | 209 / 209 (-2) | 209 / 209 (-2) |
| 128-352 | screen 1, lower floor under five claws | 227 / 439 | 226 / 435 (-4) | 226 / 435 (-4) | 226 / 435 (-4) |
| 352-512 | step 480, cart 624 | 152 / 591 | 154 / 589 (-2) | 150 / 585 (-6) | 150 / 585 (-6) |
| 512-688 | floor, claws 742/758, step 800 | 174 / 765 | 179 / 768 (+3) | 172 / 757 (-8) | 172 / 757 (-8) |
| 688-832 | two rising walls, ledge 928 | 162 / 928 | 176 / 944 (+16) | 161 / 918 (-10) | 161 / 918 (-10) |
| 832-1088 | three tall walls | 255 / 1183 | 256 / 1200 (+17) | 256 / 1174 (-9) | 257 / 1175 (-8) |
| 1088-1280 | ledge end 1216, lower floor, claws 1270..1398 | 213 / 1396 | 202 / 1402 (+6) | 194 / 1368 (-28) | 195 / 1370 (-26) |
| 1280-1456 | cart 1424, B pill box 1552 | 184 / 1581 | 177 / 1579 (-2) | 176 / 1544 (-37) | 176 / 1546 (-35) |
| 1456-1664 | floor / step 1632 / ledge 1696 | 212 / 1793 | 210 / 1789 (-4) | 211 / 1755 (-38) | 211 / 1757 (-36) |
| 1664-2048 | cart 1824, hanging walls | 365 / 2158 | 368 / 2157 (-0) | 364 / 2119 (-38) | 364 / 2121 (-36) |
| 2048-2192 | floor to the pit 2320 | 146 / 2304 | 161 / 2318 (+14) | 145 / 2264 (-40) | 145 / 2266 (-38) |
| 2192-2272 | pit, cart 2376 | 67 / 2371 | 69 / 2387 (+16) | 65 / 2329 (-42) | 66 / 2332 (-39) |
| 2272-2448 | Heartbreak Alley 2406..2566 | 171 / 2542 | 292 / 2679 (+137) | 172 / 2501 (-41) | 172 / 2504 (-38) |
| 2448-2528 | step 2592, ledge 2656 | 83 / 2625 | 81 / 2760 (+135) | 82 / 2583 (-42) | 81 / 2585 (-40) |
| 2528-2688 | trio of rising walls 2708..2772 | 171 / 2797 | 174 / 2934 (+137) | 164 / 2747 (-50) | 162 / 2747 (-50) |
| 2688-2976 | floor, six claws 3014..3094 | 316 / 3112 | 300 / 3234 (+122) | 299 / 3046 (-66) | 299 / 3046 (-66) |
| 2976-3232 | rising wall 3124, low roof, gunners 3296/3344 | 272 / 3385 | 269 / 3503 (+118) | 264 / 3310 (-75) | 264 / 3310 (-75) |
| 3232-3488 | last step 3360, gunners 3480/3566 | 259 / 3644 | 258 / 3761 (+117) | 258 / 3568 (-76) | 258 / 3568 (-76) |
| 3488-3584 | reveal scroll (96 px) | 95 / 3739 | 95 / 3856 (+117) | 95 / 3663 (-76) | 95 / 3663 (-76) |
| - | door core HP 0 (record: first explosion) | - / 3794 | - / 3935 (+141) | - / 3711 (-83) | - / 3711 (-83) |
| - | stage 8 first frame = the segment | 694 / 4488 | 696 / 4631 (+143) | 696 / 4407 (-81) | 696 / 4407 (-81) |

## Where he was faster than the first pass, and what was done about it

| section | first pass lost to him | why | second pass |
|---|---|---|---|
| Heartbreak Alley (camera 2272-2448) | 121 frames (137 behind after it) | he is INVINCIBLE there: he takes the Barrier from the pill box at x 1552 and simply runs under the five "seeking" claws; the first pass had no Barrier and baited / waited at every claw | same route: cart 1424 by a "Chariot Hop", small ledge, a jump over the pill box with a down-forward shot, the item caught in the air, drop through the ledge; the alley is then a straight run (and no longer depends on `$1A` mod 256) |
| pit and floor before it (2048-2272) | 17 | a sniper and the cart, handled by repair jumps | free with the Barrier; the pit jump is chosen to land on the cart's rear edge |
| two rising walls (688-832) | 14 | same wall-top jumps as his, but with a 4-frame pull-back and a later jump to the step | jump to the step from x 762 (the first point clear of the claw at 758), no pull-back: equal to him |
| boss (scroll start to door dead) | 25 (his 150 frames, ours 175) | he jumps during the reveal scroll and fires level with the core; the first pass's beam search never jumped | scripted fight found by a grid: one jump timed so that Bill falls through the core's height as the scroll ends, then up-forward volleys while walking to the cap: 143 frames in the two chain solves shown here, 143-155 over all solves |
| carts | about 15 over three carts | he lands on the rear edge of each cart | rear-edge landings chosen by trial on all four carts |

Everything else (screen 1, tall walls, claw corridor, six claws, gunners) the first pass already did as fast as
he or faster: he waits 21 frames at the claw corridor, 31 at the six claws, 14 at the gunners; we use 5-frame
pauses over the claws' trigger frames.

## Where the second pass is ahead of him (f_chain66)

At the door's death we are -83 frames against the record (3711 against 3794);
the 696 frames after the kill are fixed by the game (his: 694).
The lead comes from: the claw corridor (no wait at this phase against his 21 frames), the cart 1424 and the B
grab (the forced 17-frame drop, nothing else: 8 frames less than he needs there), the trio (4 frames lost against
his 11: volleys timed so that walls 2 and 3 are dead on arrival; wall 1 is broken by touch while the Barrier
still runs), the six claws (two 5-frame pauses against his two waits of 12 and 19), the gunners (shot from
further away, one duck), the door (143 frames against 150), rear-edge cart landings, and almost no lag in play
(3 lag frames before the load).
