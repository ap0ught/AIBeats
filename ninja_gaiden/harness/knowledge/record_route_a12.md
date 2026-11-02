# The record's route through Acts 1-2 (TheRetroRunner 11:32.183), extracted from his video

Agent a12, round 2 (2026-10-19). Same method as `record_route_a56.md` (agent a56), reused, not duplicated:

* Frames: `states/tmp/a12r2_vid/extract.sh` cuts every video frame of each stage from `dl/record_video/v1890225973.mp4`
  (game area 1200x900 at (600,140) scaled to 256x240, `flags=area`) to `states/tmp/a12r2_vid/s11, s12, s21, s22, s23`
  (file name = video frame index).
* Trace: `work/a12r2/rtrace.py` = `work/a56r2/record_trace.py` (room = black screens, background scroll since the
  room start, Ryu = densest Ryu-blue cluster) with the HUD mask lowered from y 72 to 60. Output
  `work/a12r2/rec/r11.json, r12.json, r21.json, r22.json, r23.json` (+ .txt samples).
  Control video frames used: 1-1 1705, 1-2 4011, 2-1 4851, 2-2 7751, 2-3 10847 (record_events.json, +-3 f).
* RAM coordinates: `ng/legal.py` `Waypoints(rec_json, stage)`:
  - X = TAS scroll at the room's first play frame (room change + 23) + the record's cumulative scroll + screen x + xoff;
    y = screen y + yoff. Offsets fitted automatically on the first 60 frames (mode of TAS - record while both stand
    on the ground): 1-1 xoff -1 / yoff 9, 2-1 0 / 8, 2-2 -8 / 8 (2-2 starts facing left).
  - Ryu's sprite is asymmetric: the tracked centre is ~7 px further left when he faces left; facing = sign of the
    tracked motion, corrected relative to the calibration's facing.
  - Camera rule: while the background scrolls, Ryu is near the screen centre; a detection far from it (a sign that
    scrolls past, an enemy) is replaced by x 129 with y interpolated. Needed in 1-1 t 556-622, where Ryu jumps along
    the top of the tall grey building and is OFF THE TOP of the screen (the tracker had locked onto a scrolling sign).
  - Check: at DTW-matched TAS frames, median TAS X - record X = 0 in 1-1, 2-1, 2-2 (72-78 % of points within 3 px).
* `waypoint_ref(wp, f0)` makes it a beam reference; `.time_map()` = dynamic time warping record time -> TAS frame
  (used to offer the TAS rows of the same route point as candidates). `work/a12r2/cmp.py <stage> <rec json>` prints
  the per-column table (`work/a12r2/rec/cmp_r11.txt, cmp_r21.txt, cmp_r22.txt`).

Times below: t = NES frames after the stage's control frame; "col" = 64-px column of absolute X in the room;
record room entries are its first picture (~22 f after the TAS-style room change frame).

## 1-1 (record 2,309.8 = TAS +16; round 1: 2,417)

| cols (X) | TAS t | record t | record - TAS |
|---|---|---|---|
| 0-10 (0-704) | 0-405 | 3-408 | 0..+4 |
| 11 (704-767) | 447 | 466 | +19 |
| 12-47 (to the end) | 490-1995 | 510-2014 | +16..+23 (constant ~+19) |

* The only place the record loses to the TAS is X 640-704 (t 405-466): where the TAS does the "GO"-sign pole double
  jump-off (banned: needs L+A, R+A, U+D+L), the record hops up onto the "Sale" shop roof (y 207 -> 172 -> 155 -> 95,
  t 400-460), runs along it and then along the very top of the tall grey building (t 556-622, Ryu above the top
  edge of the screen) and drops back down at X ~950 (t 630). From there to the exit he is level with the TAS +19.
* So a legal 1-1 that copies the record's roof line and otherwise keeps TAS pace is TAS +~19 = record pace; beating
  the record needs the roof hop a few frames faster than his.

## 1-2 Barbarian (record 841.4, TAS 834, round 1: 838 = already under the record)

Not re-solved; tracking inside the boss room picks up the boss (Barbarian is blue too).

## 2-1 (record 2,904.8 = TAS +103)

Rooms (TAS ids): 2 (rightward, long), 3 (rightward, wall climbs), 4 (short climb), 5 (leftward).

| part | TAS t | record t | record - TAS |
|---|---|---|---|
| room 2, cols 0-22 | 0-917 | 1-922 | 0..+8 (level) |
| room 3 entry (first picture) | 972 (room change 969) | 1023 | +51 |
| room 3, cols 1-17 | 1045-1709 | 1099-1782 | +54..+100 (wall section cols 8-13 costs ~+30) |
| room 4 (climb) entry / exit | 1778 / 1897 | 1884 / 2018 | +103 / +118 |
| room 5, cols 14 -> 0 (leftward run) | 1900-2495 | 2018-2597 | ~+100 constant |

* Losses: ~30-50 f entering room 3 (the room 2 exit / room 3 entry), ~45 f in room 3's wall section (TAS L+R
  climbs), ~15 f in room 4; room 5 is level.

## 2-2 (record 3,101.1 = TAS +206)

Rooms: 6 (leftward), 7 (starts at X ~830, goes right/up then left), 8 (leftward, long).

| part | TAS t | record t | record - TAS |
|---|---|---|---|
| room 6, cols 15 -> 1 | 0-564 | 5-568 | 0..+8 (level) |
| room 7 entry | 619 | 652 | +11 after the black |
| room 7 cols 13 -> 12 | 640-722 | 652-832 | +110 (the record first goes RIGHT/up to cols 14-15, the TAS goes straight left with L+R) |
| room 7 cols 11 -> 2 | 774-1158 | 898-1289 | ~+125..+131 |
| room 8 entry, cols 28-24 | 1270-1573 | 1435-1770 | +165..+197 |
| room 8 cols 23 -> 0 | 1616-2599 | 1814-2806 | ~+200 constant |

## 2-3 Bomberhead (record 833.3, TAS 830)

* TAS: arrives with Jump & Slash (item 133) and 10 ninpo, walks left from x 208, jumps at t ~32 and lands two J&S
  spins (ninpo 10 -> 5 -> 0) at t 64 and 79: boss HP 0 at t 82.
* Record (video 10847-10933, contact sheet `states/tmp/a12r2_vid/s23_sheet.png`): arrives with the Windmill Star
  and 10 ninpo, jumps left from the right side, throws the Windmill (ninpo 10 -> 05) toward Bomberhead (the star
  hits on the way out and back), then slashes him at close range; ENEMY bar empty at t ~86.
* Both need 10 ninpo on arrival: 2-1/2-2 must pick up the item + ninpo (TAS: J&S + 10 at 2-1's end).

## Round 3 (a12r3) notes
* 2-1 legal line used (v1, 2,964 f): pillar brute force, then the TAS line legalized (in sync from the pillar to room 3's exit with one brute-forced post jump), room 3 exit = 3 legal wall jump-offs, room 4 = round 2's beam rows (186 f; the record ~134, the TAS 120), room 5 = TAS rows in sync. Room 4 is where the record's split is lost.

