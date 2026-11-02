# The record's route through Acts 5-6 (TheRetroRunner 11:32.183), extracted from his video

Agent a56, round 2 (2026-10-19). Source: `dl/record_video/v1890225973.mp4` (1080p60, one NES image per 2 video
frames). Frames were cut to `states/tmp/a56r2_vid/<seg>/fNNNNN.png` (game area 1200x900 at (600,140) scaled to
256x240, which is 1 NES px per px horizontally). Tools:

* `work/a56r2/record_trace.py` - per distinct image: room index (black screens), cumulative horizontal scroll since the
  room start (background shift, exact to 1 px: running = 3 px per image), Ryu's screen position (densest cluster of
  Ryu-blue pixels). Outputs `work/a56r2/rec/r51.json` .. `r63.json`.
* Calibration against the TAS trace at the 5-1 start: RAM x = video x - 2, RAM y = video y + 9 (the record's Ryu at
  t = 19 f after control is at x 94 y 93, the TAS's at x 94 y 96). Room starts: the record's position 17 f after the
  first picture of a room is matched to the TAS's position 40 f after its `$6D`/room change (same spawn).
* `work/a56r2/cmp_route.py <stage> <rec json> [our .ref.json]` - first time each 64-px column of each room is
  reached: TAS vs record vs our solutions (`work/a56r2/rec/cmp_r5x.txt`).
* `work/a56r2/mk_recref.py` - the record trace as a reference for `a56_solve.py --ref` (positions only, blank rows):
  `logs/a56r2_rec51.json`, `_rec52`, `_rec53`, `_rec62`, `_rec63`.
* Times: t = NES frames after the stage's control frame (video frame - control video frame, x 60.0988/60). The
  record's control frames are "timer digits shown - 6" (record_notes.md, +/-3 f). The record's room entries are its
  first picture after the 22-frame black, i.e. about 22 f after the TAS-style room-change frame.

## Room entry times (t after control; record entry = first picture, TAS = `$6D`/room byte change)

| stage | TAS rooms (t) | record rooms (t, first picture) | TAS next load | record last image |
|---|---|---|---|---|
| 5-1 | 22: 0 | 22: 19 | 2151 | 2263 |
| 5-2 | 23: 0, 24: 446, 25: 933, 26: 1390 | 23: 3, 24: 542, 25: 1111, 26: 1602 | 2029 | 2261 |
| 5-3 | 27: 0, 28: 404, 29: 876, 30: 1312, 31: 1785, 32: 2020, 33: 2235 | 27: 1, 28: 538, 29: 1051, 30: 1556, 31: 2060, 32: 2365, 33: 2599 | 2499 | 2832 |
| 6-2 | 36: 0, 37: 934, 38: 1531, 39: 1629, 40: 2073 | 36: 1, 37: 1015, 38: 1714, 39: 1840, 40: 2305 | 2771 | 2926 |
| 6-3 | 41: 0, 42: 428, 43: 583, 44: 1875 | 41: 4, 42: 472, 43: 688, 44: 2052 | 2564 | 2754 |

## 5-1 (record 40.93 s; TAS +157)

Column-by-column (cmp_r51.txt, t of first reach): the record equals the TAS to x 512 (t 267 vs 261), then loses
~75 f at the bird boost (x 512-576: TAS 305, record 380; our round-1 c8 365), then runs level with the TAS +80 f
to x 1500. **The wall at abs x ~1499 (video 25340-25450): the record lands between the blue pillar and the tall
wall and climbs the gap by bouncing between the pillar and the wall (two-wall chimney climb, ~90 f ground to top)**,
not a single-wall climb. Record +112 f over that column vs the TAS's +66.
Where our round-1 c8 lost to the record: x 1152-1216 (bucket 18-19: c8 107 f, record 52 f: -55 f) and x 2752-2816
(bucket 43-44: c8 142 f, record 44 f: -98 f), plus ~13 f at the chimney wall. End: c8 reaches x 3008 at t 2374,
the record at 2165 (-209).
Items: the record picks up ninpo (00 -> 55) and the orange weapon (Fire Wheel / J&S) in 5-1.

## 5-2 / 5-3 / 6-2 / 6-3

Room 23 (5-2a): the record runs left level with the TAS (x 0..640 at the same times) but loses ~95 f at the room
exit (the TAS's U+D+L wall wobble at TAS 24821-73). Rooms 24-26 are horizontal rightward: record +100..+130 per room.
6-2 room 37 (the round-1 blocker at abs x 782, y 48): the record enters bottom left, hops the small step, runs to the
tall pillar and climbs its RIGHT face with single-wall jumps (video 35726-35810, 84 frames ground to top), then goes
left over the top. Room 37 total: record ~700 f, TAS 597.
Full column tables: `work/a56r2/rec/cmp_r5x.txt`, `cmp_r6x.txt`.

## Bosses

### 6-4a Masked Devil (record 13.63 s = TAS +10; control ~video 40670, ENEMY bar empty 40744)
**CORRECTION 2026-10-24 (`ninpo_budget.md`):** the purple HUD icon is Jump & Slash, not the Windmill. The "Windmill
throw" below is a **J&S spin** in the air at the orb, which hits every frame, so 6-3 must keep **J&S** + 5.
The record leaves 6-2 with J&S/10 and 6-3 with J&S/05.
He walks right from the left door, wall-climbs the LEFT pillar (x ~70), jumps right toward the orb (slot 6, id 36,
x 135, y 120, 16 HP) at ~40716 and throws the **Windmill Star** (ninpo 05 -> 00 at 40722) at the orb in the air,
then slashes: the Windmill hits on many consecutive frames as it passes through and returns, the bar drains 37 -> 0
px between 40716 and 40746 (whole fight ~75 f after control). He entered 6-3 with Windmill/10 and kept it (no
Fire Wheel pickup in 6-3), arriving with Windmill/05. The TAS arrives with the Fire Wheel (one wheel already in
flight from 6-3 hits the orb twice at the start: free hits).

### 6-4b Jaquio (record 16.60 s = TAS +152; control ~video 41488, bar empty 41758, sword only)
Ryu (tracked, video coords): jumps onto the left pedestal (x 48, 41502), jumps off to the up-right (x 99, y 98 at
41532-41544: first hits on Jaquio as he descends top-centre-right, bar 38 -> 33 by 41548), then lands on the
**middle pedestal ("plate", video x ~125, y 154 = RAM x ~123, y ~163)** at 41562 and stays there: jumps STRAIGHT
UP from the plate again and again (y 154 -> 95 -> 154, 41562-41660, 41682-41760 at x 123-141), slashing Jaquio as he
passes over/through. Bar drops: 41542-48, 41584-90, 41610, 41632-44 (4), 41698-716 (4), 41740-758 (3): about 1.5
of Jaquio's swoop cycles ("beats him in 1 and a half cycles"). Fight ~265 f after control (TAS ~100).

### 6-5 The Demon (record 12.57 s = TAS +162; control ~video 42484, bar empty 42806, sword only)
Phase 1 (the pod, slot 6 id 38 at x 125 y 168, 16 HP; must die first): he walks right to video x ~77-84 (RAM ~75-82)
by 42520 and jumps straight up there 4 times (42524-42610), slashing the pod each time; the pod falls and rolls left
(42620-42670). Phase 2 (the heart, slot 7 id 40, x 168, y 120 -> 168 after the pod dies): he walks right to video
x ~115 (RAM ~113) and jumps straight up repeatedly (42684-42808), slashing; the ENEMY bar drains 42700 -> 42808.
Kill ~316 f after control (TAS ~151).

## Addendum (end of round 2)
* 5-1 x 1700-1930 (t 1300-1400, video 25690-25740): the record goes over the gap at the TOP of the screen (Ryu leaves
  the tracked area at video 25702 next to a bird, sword out, then lands on the long upper platform at x ~1917, y ~86
  at t 1395) - most likely a bird damage boost. Our beam (record reference) stalls at y 58 there and loses ~110 f.
* What the boss strategies gave us (TAS start states, legal 5-frame cancel cadence): demon straight-up jump-slashes
  at the pod then the heart -> END seen TAS +156 (record +162); Masked Devil with the TAS's Fire Wheel -> +94 (the
  record's Windmill strat not reproducible without the Windmill); Jaquio plate strat not reproduced (see
  legal_a56_notes.md, Round 2).

## Round 3 additions (2026-10-20)
* 6-2 room 37 entry (record t 1015-1084): Ryu enters clinging at the bottom of a two-wall chimney (screen x ~91,
  wall on his right); the record jumps off left to the pillar face (screen x ~74), wall-jumps RIGHT onto the entry
  wall's top (RAM y 192) and walks right to screen x ~131 BEFORE turning left. That walk is required: room 37's
  leftward camera only starts after Ryu has reached screen x 127 (`$4C` 128 -> 129). Legal rows that do it from
  round 1's chimney cling (row 1125 of `states/tmp/a56_best_6-2_snap.inputs.txt`): Right+A x2, Right x38, then Left
  (`states/tmp/a56r3_62_pre1125.inputs.txt`). He then climbs the pillar's right face at abs ~840 (record scroll -56)
  and walks left over its top (y 96), jumping off its left end at abs ~782 high toward the upper left.
* 6-4b Jaquio: the motion is deterministic (no RNG; see legal_a56_notes.md Round 3). Measured hit band (sword,
  legal cancel cycle): Ryu FACING RIGHT, Jaquio 24-58 px to his right (Jaquio x - Ryu x), Ryu y 78-119 (a jump from a
  pedestal top, y 160 -> apex 112, is in range for ~17 frames). With Jaquio on Ryu's left no hit was measured
  (every such test was ruined by contact damage when Jaquio passed over Ryu at |dx| < ~20); the record's left-side
  hits (t 96-102, 144-156 by the model) are not reproduced yet.
