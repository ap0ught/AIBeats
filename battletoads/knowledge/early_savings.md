# Early savings: the reserve before Level 12 (track EARLY, 2026-10-09)

Purpose: the published run `up14` is 2.50 s slower than the record once the clock stops at the right event (the cut to
Professor T. Bird, frame 47253; the record's cut is at frame 47103 on our clock). We need at least 151 frames, ideally
215 or more. This file ranks what can be saved before The Revolution, says what each item would cost downstream, and
gives build recipes for the best ones.

Everything here was measured on snapshots of the verified run (`cap14_f<N>` savestates plus `logs/up14.inputs.txt`).
**No route was assembled and nothing below has been verified from power-on.** None of the `early_*.py` scripts writes
memory.

## The short version

| | frames | status |
|---|---|---|
| Robo-Manus (Level 8's boss) the TAS's way, with Select re-rolls, plus a better arrival | **-414** | **proven on a snapshot**, replayed independently through the level's end into Terra Tubes |
| Intruder Excluder's climb | about -370 to match the record's climb; **-211 proven for the first 1,800 px** of 4,030 | whole climb measured against the record's video; lower half **proven on a snapshot**: -125 at 460 px, -226 at 1,400, -211 at 1,800, -167 at 2,200 (three lines, each replayed); the upper half of the tower is not searched |
| Karnath's Lair, the warp room (the record's line over the snake's head) | -76 in the record; nothing proven | his line read off the video; the climb and the crossing reproduced, his jump off the head not found |
| A / B alternating page mash at the eight level changes before Level 12 | **-18** (-10 for the four after Level 8) | **proven per boundary on snapshots** |

Item 1 alone moves the Terra Tubes placement from frame 17366 to **16952**. If every later segment could be re-fitted at
its present length the T. Bird cut would be at 46839 = **12:24.86** (record 12:29.25). The honest caveat is the Dark
Queen: `L13y0` (1,694 inputs) was a lucky roll, a normal re-solve is 1,830 to 1,861, so expect the cut near 46975 to
47006 = about 12:27.1 to 12:27.6, which still meets the 47040 target. The climb is margin on top: its proven part
(-211) and the fight were found separately on the same snapshot and have not been run one behind the other, but the
fight hangs on the frame the boss lands, not on the level clock, so they should add.

The surprise of this pass: Level 8 looked harmless in every earlier comparison (+1.1 s against the record) because two
large errors cancelled. Read off the record's video, his climb is 369 frames faster than ours and our boss fight is 302
frames faster than his. The 1-player TAS's fight (first hit to kill: 578 frames, ours 1,030) is 452 frames shorter
still; its one Up+Down frame is dice noise, which Select does legally.

## 1. Where the time is, level by level (the record's rule)

Level ends are the first black frame after each level (`early_black.py` on the `cap14` states, every frame
screenshotted; warps go black about 170 frames before the level byte changes; Terra Tubes has a 4-frame black blip at
27284 before the real black at 27304, the table uses 27304 like the earlier comparisons did). Record from
`knowledge/wr_splits.json`. Clock start 2074, 60.0988 frames per second. `python early_table.py` reprints it.

| level | our end frame | ours (s) | record (s) | behind (+) so far | this level: ours | record | difference (s) | frames |
|---|---|---|---|---|---|---|---|---|
| 1 Ragnarok's Canyon | 2299 | 3.74 | 3.53 | +0.21 | 3.74 | 3.53 | +0.21 | +13 |
| 3 Turbo Tunnel | 4732 | 44.23 | 47.18 | -2.95 | 40.48 | 43.65 | -3.17 | -190 |
| 4 Arctic Caverns | 9665 | 126.31 | 127.61 | -1.30 | 82.08 | 80.43 | +1.65 | +99 |
| 6 Karnath's Lair | 12267 | 169.60 | 168.81 | +0.79 | 43.30 | 41.20 | +2.10 | +126 |
| 8 Intruder Excluder | 17317 | 253.63 | 251.74 | +1.89 | 84.03 | 82.93 | +1.10 | +66 |
| 9 Terra Tubes | 27304 | 419.81 | 413.79 | +6.02 | 166.18 | 162.05 | +4.13 | +248 |
| 10 Rat Race | 29250 | 452.19 | 449.94 | +2.25 | 32.38 | 36.15 | -3.77 | -227 |
| 11 Clinger-Winger | 36129 | 566.65 | 563.11 | +3.54 | 114.46 | 113.17 | +1.29 | +78 |
| 12 The Revolution | 45057 | 715.21 | 706.63 | +8.58 | 148.56 | 143.52 | +5.04 | +303 |
| 13 Armageddon (T. Bird cut) | 47253 | 751.75 | 749.25 | +2.50 | 36.54 | 42.62 | -6.08 | -365 |

We enter Level 12 3.54 s (213 frames) behind. The levels where we lose add up to 630 frames before Level 12.

Level 8 split by the record's video (boss descent starts at video 239.77 = run 219.08 s; ours frame 15656 = 226.00 s):

| part of Level 8 | ours | record | difference |
|---|---|---|---|
| placement to the boss's descent (the climb) | 12488 to 15656 = 3,168 f | 193.20 to 239.77 = 2,799 f | **+369** |
| boss's descent to the kill | 15656 to 16877 = 1,221 f | 239.77 to about 265.1 = about 1,523 f | **-302** |

The record's kill time is derived from his level-end black (272.43) minus the 440 frames the death takes; his "10000"
pops between 265.0 and 266.0 on the 2-second sheet, so the split is good to about 20 frames.

Against the TASes (frames of play, level byte to level byte): Level 10 equal (1,925 / 1,924); Level 11 +207, all of it
the Buzzball (kill at 774 frames after it appears, the TAS 564); Level 9 +652; Level 8's boss +452 (see item 1).

## 2. Ranked table

Frames are savings at the point named. "Refit" is what has to be redone behind the change. Every change before Level 12
re-rolls the dice of every later level (section 6), so the whole tail (rngfit of 9, 10, 11, 12 and a queen re-solve) is
paid **once per batch**, not per item. Do all chosen items in one batch, upstream first.

| rank | item | level | frames | status | difficulty | refit behind it |
|---|---|---|---|---|---|---|
| 1 | Robo-Manus by jump-smashes only, Select re-rolls, stand at x 183 for the arrival | 8 | **-414** | proven on a snapshot, replayed to the Terra Tubes placement | low: tool exists (`early_l8fight.py`, about 40 min) | rngfit L9c, L10t, L11r, L12g; queen re-solve |
| 2 | Intruder Excluder climb re-searched (36 idle frames at the start, 617 frames of stalls) | 8 | about -370 (record parity), more is plausible; **-211 proven for the first 1,800 px** | whole climb measured against the record; the first 1,800 px proven and replayed: 1,432 frames against 1,643 (-211); 2,200 px: -167; the upper 1,800 px not searched yet | medium: the search exists (`early_l8climb.py`), hours of machine time | none extra if done with item 1 (the boss search is re-run from the new arrival) |
| 3 | A / B alternating mash on every briefing and warp page | all | **-18** (2, 2, 2, 2, 3, 2, 3, 2); -10 for the four boundaries after Level 8 | proven per boundary on snapshots | trivial | none extra where the next level is being re-fitted anyway |
| 4 | Karnath's warp room: jump onto the snake, over its head while it rises, fly to the ledge | 6 | -76 in the record; 0 proven | the jump-grab, the faster climb and the crossing of the rising head are reproduced; the jump off the head that the flight needs is not (section 4) | medium to high | Level 8 on (free inside the item 1 batch: the climb is not random) |
| 5 | Karnath room 1, last snake: the jump from the head's edge to the exit ledge | 6 | about -50 (2-player TAS reaches the ledge 50 frames before us) | measured, not attempted | medium | as item 4 |
| 6 | Buzzball at the TAS's 45-frame rhythm | 11 | -100 to -210; 0 proven | five earlier attempts failed; tried again here: ten hits by +453 (up14 +588), then the ball comes off the wall and the last three hits cost it all back (section 5) | high | rngfit L12g; queen |
| 7 | Terra Tubes: the record's line over the staircase into the tank and the star corridor | 9 | -250 to -600 | unsolved; three new facts (section 5) | high | the rest of Level 9 re-solved, then L10 to L13 |
| 8 | Arctic Caverns: the lift before the warp | 4 | about -30 against the record (215 frames from the last barrier to black, the record 180) | parked (beam found nothing better than 240 to 244) | medium | everything from Level 6 |
| 9 | Arctic Caverns: the record's straight fall through the spike pit | 4 | about -90 | parked (never reproduced) | high | everything from Level 6 |
| 10 | Level 8 entry wait alone | 8 | 0 to -36 | part of item 2: shifted old inputs never reach the second floor | - | - |
| 11 | Level 1 | 1 | -13 against the record | parked (staged scan found nothing) | - | Turbo Tunnel's skip must be re-aligned: do not touch |
| 12 | Turbo Tunnel gauntlet by the TAS's line | 3 | about -75 | parked (its two sprint jumps need Left+Right) | - | the bike skip's sub-pixel alignment: do not touch |
| - | Rat Race | 10 | 0 | already the TAS's own inputs; 227 frames ahead of the record | - | - |
| - | Clinger-Winger ride and turns | 11 | 0 | the whole +207 against the TAS is the Buzzball | - | - |

## 3. Build recipes for the top three

### Recipe 1: Robo-Manus (-414)

What changes. `up14` lands in the arena at x 118, is walked to x 128 by the arrival cutscene, runs 96 px to the boss and
lands 21 smashes plus the last blow in 1,030 frames because he relocates seven times. New line:

1. Arrival. Replace up14 frames 15597 to 15789 (`L8c` inputs from index 3113): hold Right+A for 16 frames (the last
   climb jump steered right; lands at x 189 on frame 15623), keep Right until the toad is at x >= 200, release. The
   cutscene then starts with the toad at x 229 and hands control back on frame 15789 at **x 183** instead of 128.
   Do not go further right: a toad at x >= 234 when the cutscene starts is flattened by the descending boss (animation
   85/86, health reads 0 for about 120 frames, control only at 15823). File: `logs/fix/early_l8arrive_best.json`.
2. Fight. Only the jump-smash (toad animation 38 then 87) keeps him where he is; punches (24, 28, 29), kicks (30, 31)
   and the ram (49) knock him across the room. Which one B gives is a dice roll and **one Select press on an earlier
   frame re-rolls it** (`early_l8probe.py`: Select on frame 6, 7, 11 or 15 of the wait turns a punch into the smash).
   Rhythm: direction+B on the first frame after landing, direction held 5 more frames, hit 9 frames after the press,
   26 frames a cycle. He takes off about every 165 frames: a smash right at take-off knocks him back down; when he is
   already high use direction+A for 1 to 3 frames, then direction+B (the smash from a hop). Coming out of a run,
   release the direction for one frame before direction+B or the ram comes out. Last blow: anything.
3. Tool: `python early_l8fight.py 10 100 <out> <seed> logs/fix/early_l8arrive_best.json` (hit-by-hit beam on savestates,
   width 10, 100 randomised cycles per node, about 40 minutes on one emulator). Result used here:
   `logs/fix/early_l8fight_e.json`: blows at +26, 52, 80, 126, 152, 178, 204, 230, 256, 282, 308, 340, 372, 398, 426,
   488, 514, 544, 588, 614, 646 and the kill at +674 from control (up14: 1,087; the TAS: 599). 0 Left+Right, 0 Up+Down,
   0 Start; 41 frames carry Select.
4. Check already done (`early_l8verify.py`, a fresh replay from `cap14_f15000`): kill on frame **16463** (up14 16877),
   level byte leaves 7 on 16906 (17318), toad placed in Terra Tubes on **16952** (17366) with the A/B mash, 16955 with
   up14's A/- mash; health 47, lives 3, score 143600, all equal to up14's.

Build:
- Segment `L8d` = `L8c` inputs [0:3113] + the 193 arrival inputs + the 674 fight inputs + 300 empty frames + A, B
  alternating until the toad is placed in Terra Tubes (the segment must end on the placement frame like `L8c` does;
  expected length 4,469 against 4,883). If items 2 to 5 are taken, build them first and re-run step 3 from the new
  arrival state instead (the fight itself is tied to the frame the boss lands, not to the route).
- `assemble.py <fresh name> L1b L3u L3skipu L4c5 L6c L8d` to get the replay-exact Level 9 entry bookmark, then
  `fitchain.py L8d_end0 0 <tag> L9c L10t L11r`, `rngfit.py L12g <L11x>_end0 <L12x>`, `l13solve.py <L12x>_end0 0 <fresh
  L13 name>` (fresh name: it caches sections), assemble and verify twice.
- Risks: the result depends on the seed (seed 5, width 10: 674 frames from control; seed 7, width 12: 748, after a
  relocation at blow 17), so run three or four seeds and keep the best; the 62-frame gap after blow 15 in the 674 line
  says there are 30 to 60 frames more; `L12g` has never been re-fitted by `rngfit` (L12d to L12r was, with 6
  re-rolls); the queen.

### Recipe 2: Intruder Excluder's climb (about -370 by the record; -211 proven for the first 1,800 px)

Evidence. The record is placed at video 193.20 and his boss starts down at 239.77 (2,799 frames); ours 12488 to 15656
(3,168). Side by side (`logs/fix/wr_l8climb_1.jpg`, `wr_l8climb_2.jpg` against `up14_l8climb_1.jpg`, `up14_l8climb_2.jpg`)
we are 0.8 s behind at the placement, 2.6 s at the first long teal platform (up14 frame about 12980), 4.0 s after the pink
floors with the yellow balls (13300), 4.7 s in the 1UP room (13500), 7.7 s at the pink block column (14300), 6.9 s at the
boss. In up14 the first jump comes 68 frames after the placement (the record's about 45) and there are ten stretches of
45 to 77 frames without any height gained (617 frames in all, starting at frames 12488, 13117, 13249, 13333, 13577,
14215, 14417, 14492, 14703, 15121). The climb was solved once (journal 008) by `l4s.py` in `climb` mode: seven 600-px
sections, 4-frame macros, states ranked by height alone, behind a 36-frame entry wait that only kept old inputs in
phase.

What does not work: the old inputs started k frames sooner never get past the first floor unhurt
(`early_l8entry2.py`, k = 20 to 36); `l4s.py ... climb` with `L4S_MACRO=2` (with and without `L4S_RANKGROUND=1`) hops under
the first ceiling for 300 frames, because the height-only rank fills the beam with hop states and cuts the walkers.

What works: `early_l8climb.py`, an earliest-arrival search by LANDING instead of by frame. Node = the toad standing
somewhere unhurt, with the frame count that got it there. Candidates from a node = stand 6 to 40 frames / walk or run
8 to 48 / wait, run and jump (A held 4 to 32, one air direction); kept when the toad stands again, unhurt and not
lower. The node with the smallest frame count is always expanded next (at most 3 per 16-px height band, 32-px x
bucket and 48-frame slice), so the first node at a height is the earliest arrival the candidate family allows.
Proven on the up14 snapshot (root = frame 12488, the placement; all numbers are frames since the placement):

| height above the start | best line | up14 | saved | run |
|---|---|---|---|---|
| 200 px | 190 | 263 | 73 | seed 3, 100 candidates a node |
| 460 px | 369 | 494 | 125 | the same, and seed 2 with 120 (replayed) |
| 600 px | 467 | 563 | 96 | the same |
| 800 px | 681 | 836 | 155 | b: resumed at 600, 160 a node |
| 1,000 px | 798 | 1,004 | 206 | b |
| 1,200 px | 935 | 1,152 | 217 | b |
| 1,400 px | 1,092 | 1,318 | **226** | b (replayed: frame 13580, 1,408 px up, health 47) |
| 1,600 px | 1,227 | 1,471 | 244 | d: resumed from b at 1,400, 140 a node, with the standing move |
| 1,800 px | 1,432 | 1,643 | **211** | d (replayed: frame 13920, 1,856 px up, health 47) |
| 1,900 px | 1,466 | 1,689 | 223 | d |
| 2,000 px | 1,614 | 1,805 | 191 | c: seed 3's line resumed at 1,800 with the standing move |
| 2,200 px | 1,714 | 1,881 | **167** | c (replayed: frame 14202, 2,208 px up, health 47) |
| 2,300 px | 1,807 | 2,026 | 219 | c |

The arena floor is about 4,030 px up (up14: 3,135 frames to stand at 4,000). All lines: 0 Left+Right, 0 Up+Down, 0 Start.

The 460-px piece was replayed independently (`early_l8climb_verify.py`: 369 inputs, toad standing 480 px up on frame
12857, health 47 throughout, 0 banned presses). Because `cap14_f12000` comes from a power-on replay of up14, these
pieces are valid for any route that keeps up14's Levels 1 to 6.

Recipe:
1. `python early_l8climb.py 4000 140 <seed> [milestone.json]` (goal in px above the start; 140 candidates a node; the
   optional fourth argument resumes from a saved milestone; `EARLY_TAG=x` keeps parallel runs' files apart). Milestones
   are written every 200 px as `logs/fix/early_l8climb_mark<px><tag>.json` = the full input list from frame 12488.
   Speed here: about 100 px every 2 to 3 minutes on a loaded machine. Run two or three seeds; more candidates per node
   gave the better line (160 a node: -226 at 1,400 px; 100 a node: -159).
2. Where it stops: the first version, without a standing move, died out at 1,900 px: the column of red fliers, where
   up14 itself waits 74 frames (14215 to 14289) for their sparks. With the standing move and 48-frame time slices in
   the cell key it gets through (2,300 px reached) but the queue grows to 400 to 1,100 nodes and it slows to about
   100 px in 8 minutes; I stopped both runs at 2,300 and 1,900 px. The upper 1,700 px have not been searched. To
   finish it: drop queue entries dominated in (height, frame), keep the wide candidate count, and check whether the
   record takes a hit on the way up (every search here drops a hurt toad; one spark costs 24 of 47).
3. At the top, steer the last jump as in recipe 1 step 1 (stand at x 200 to 232 when the cutscene starts), then run
   recipe 1 step 3 from the new control frame. The boss appears when the camera reaches the top, so his timeline moves
   with the arrival; nothing in the fight is tied to the level clock except the platforms' cycles in the climb itself.
4. The new Level 8 = `L8c` inputs [0:5] (to the placement) + the climb piece + arrival + fight + tail, then the same
   downstream chain as recipe 1. Nothing else is added to the refit.

### Recipe 3: A / B alternating page mash (-18, or -10 after Level 8)

A press only counts when it is fresh, so up14's one-button mash (B before Levels 3 and 4, A elsewhere, every other
frame) can miss the first accepting frame. Two buttons on alternate frames give a fresh press every frame.
`early_mash.py` replaced only the transition inputs at each boundary and measured the placement frame:

| boundary | up14 | A,B,A,B | gain |
|---|---|---|---|
| 1 to 3 (warp) | 2516 | 2514 | 2 |
| 3 to 4 | 4778 | 4776 | 2 |
| 4 to 6 (warp) | 9888 | 9886 | 2 |
| 6 to 8 (warp) | 12483 | 12481 | 2 |
| 8 to 9 | 17366 | 17363 | 3 |
| 9 to 10 | 27353 | 27351 | 2 |
| 10 to 11 | 29298 | 29295 | 3 |
| 11 to 12 | 36177 | 36175 | 2 |

Never put Start in the pattern: on the three pages after Levels 8, 9 and 11 it costs 47 to 66 frames. A held button
never skips (440 to 512 frames). The per-button rate is the same 30 presses a second up14 already uses.
Build: in every segment that is rebuilt or re-fitted in the batch, replace the tail mash by `A`, `B`, `A`, `B`, ... from
the frame the level's last real input ends (windows used: 2313, 4733, 9665, 12281, 17239, 27226, 29251, 36034 in up14
frames) and cut the segment on the placement frame. `rngfit.py` step 4 already searches mash patterns: add this one.
Each changed boundary changes the next level's dice, so only do it where that level is re-fitted anyway (with recipe 1:
the four boundaries from Level 8 on, -10). Leave 1 to 3 alone unless Turbo Tunnel is being rebuilt: the bike skip needs
five sub-pixel bytes equal.

## 4. Karnath's Lair (rank 4 and 5)

The record's warp room, read from his video at 0.05 to 0.1 s steps (`logs/fix/wr_karnath_1.jpg`, `_2.jpg`, `_3.jpg`).
Clock r = frames since up14 frame 11910 (the toad appears in the room); the snake's head starts to rise at r+71, 2 px a
frame; the record's frames map to r = 101 + (video - 186.5) x 60, from the snake's height in his picture (good to
about 6 frames).

| | record | up14 |
|---|---|---|
| leaves the floor | r+113: jumps at the snake and hangs on about 60 px up at r+119 | r+106: starts climbing from the floor (2.4 px/f) |
| at the head | level with its top at r+173 | 32 px under it at r+176, stays under it |
| past the head | goes over / through the head while it still rises, out on its right side at r+176 to 185 | waits for the head to turn (r+228), runs along the body, drops off at x 200 (r+262) |
| on the portal's ledge | about r+265 | r+332 |
| black | r+281 | r+357 |

His flight passes about 55 px above the first star (world x 231, H about 7647) and then drops under the next two (x 316
and 351, H about 7677) onto the ledge (H 7518). The 2026-10-02 searches looked for a toad standing on the head, or held
Right for the whole flight, which dies on those stars.

Reproduced on a snapshot (`early_l6vault2.py`): from x 84 press Right+A for 16 frames at r+98: the toad grabs the body in
the air and is 16 px under the head's coordinate at r+135 (up14: 54 under). From there a one-frame beam (it mostly just
holds A, which climbs faster than alternating Left+A / Right+A) is level with the head at r+160 and 18 px above its
coordinate at r+186; holding Right(+A) there walks the toad **over the still-rising head** to x 128 on its right side in
14 frames (r+200, H 7723). Before that height nothing gets past the head (`early_l6vault.py`, `early_l6eject.py`:
528 let-go trials from up14's own climb, none crosses before the head turns).

But that is only half of his line. From the walk-over the toad has no upward speed: a flight beam from there
(`early_l6vault3.py`, 800 wide, every air control) falls into the spikes at x 285 to 287, about 60 px short of the
ledge; a plain fall from the head's height covers about 150 px and the ledge is 230 away. The record's toad RISES after
it has passed the head (about 15 px relative to the head in the 6 frames of the crossing, then 3.3 px a frame
sideways): a real jump, started on the snake's left side with its top about 5 px under the head's top, that takes it
through the head's sprite. I did not find that jump: from the 8 highest states of every layer between r+146 and r+170
(16 px under to 8 px over the head's coordinate), releasing A / Right / Left for 1 to 3 frames and pressing Right+A
again for 3 to 32 frames never jumps, it only walks over 30 frames later (`early_l6vault5.py`, stopped at r+170). A
wider scan from six heights (16 under to 20 over the head's coordinate; 0 to 13 more climb frames, a release of 1 or 2
frames on five pad states, then nine different presses including Up+A, Down+A and B: 8,820 sequences,
`early_l6vault6.py`) found no press that lifts the toad more than its climbing does and none that moves it right.
**Proven gain in this room so far: none.** What is new and reusable: the jump-grab (38 px higher than up14 at r+135),
climbing by holding A, and the fact that the head can be crossed before it turns. Still untried: grabbing the snake
right under the head from the jump itself, so that the toad arrives at the top with its jump speed
(`early_l6vault4.py` scans that; written, not run), a sprint (double tap) into that jump, and reading his 60 fps frames
between video 187.70 and 187.85 one by one for the toad's pose.

Room 1 (rank 5): frames since the level byte is set, the 2-player TAS (`tas/watch_log.txt`) against up14 (`cap14.ram`):
equal through snakes 1 and 2; the TAS's third snake runs 5 to 13 frames ahead of ours and the TAS is on the exit ledge
(366,179) at 1,865, we at 1,915; both then stand 128 frames. Its author's note: a precise jump onto the edge of the
snake's head and from there to the exit hole. Not attempted here.

Refit for either: Level 6 itself is not random (0 re-rolls every time), the Level 8 climb replays behind any Level 6
(with its entry wait) and the boss is searched anyway, so inside the item 1 batch this costs nothing extra.

## 5. The harder items: what is new

**Buzzball (rank 6).** Positions at each hit, TAS against up14 (frames since the ball appears):

| hit | TAS: frame, toad x, ball x, ball h | up14: frame, toad x, ball x, ball h |
|---|---|---|
| 3 | 122, 1743, 1774, 91 | 124, 1749, 1774, 93 |
| 6 | 249, 1744, 1777, 48 | 246, 1765, 1778, 52 |
| 8 | 339, 1745, 1778, 48 | 356, 1762, 1764, 54 |
| 10 | 429, 1751, 1778, 47 | 588, 1774, 1771, 54 |
| 13 | 564, 1764, 1782, dead | 774, 1702, 1661 |

From hit 6 on the TAS kicks the ball only when it is back on the floor (h 47 to 48) from 30 to 34 px away, every 45
frames. Hits 4 to 8 are `Left`, `Left+Right`, `B`: the banned press is what keeps its toad at x 1744 (a kick with no
step forward). Its last five are the legal `Right`, `B` and creep 3 px each. We kick at 40 to 42 frames with the ball
still 20 to 35 px up, from 12 to 16 px, and creep; at hit 8 the toad is 2 px from the ball and it gets out. A legal
version needs about 11 kicks with at most 28 px of creep, or one retreat (about 30 frames).
Tried once more with the hit-by-hit beam (`early_l11fight.py`, root = up14 frame 35036, after the second hit): waiting
for the ball to come down and kicking with `Right`, `B` holds the TAS's 45-frame rhythm with the ball pinned (hits 3 to
8 at +128, 170, 212, 257, 302, 347) and has ten hits at +453 where up14 needs +588. Then the same thing happens as in
every earlier attempt: the toad has crept to x 1761 to 1765, the ball comes off the wall, and the last three hits
(chase policy) cost everything back: the thirteenth lands at +775 (up14 kills at +774) and is a weak one, the ball
keeps 13 health. No gain proven. What is left to try is an endgame search from the ten-hit state (`logs/fix/early_l11fight_a.json`: toad x 1765,
ball (1775, 71), 47 health left = three kicks), or a rhythm that retreats 3 px after every kick.

**Terra Tubes (rank 7).** New facts, all from the up14 snapshot at frame 25186 (toad at (759, 6534)):
- The two bugs (0x74 at x 824 and 840, 26 to 32 px above the staircase top) do not chase and involve no dice (Select
  changes nothing): they grab whatever passes under them slowly. Walking or crouch-walking is always grabbed at x 818
  to 822; **leaving the left block at sprint speed (tap, gap, hold: 3 px a frame) passes both without a grab** (144 of
  1,476 variants, `early_tt_run.py`). That is why the 1-player TAS is not grabbed and up14 is.
- Once grabbed nothing lets go: A, B, Down, Up, Select and every mash keep the toad hanging (B only punches); Left and
  Right steer it between x 780 and 915 (`early_tt_carry.py`).
- Behind the bugs is not the tank but a pink shaft with a star mine and spikes (`logs/fix/tt_hurt.jpg`): every drop at
  x 871 to 895 is hurt at H 6462, x 915 at H 6414; the ledge at (884 to 904, 6406) can be reached unhurt (Left for 12
  frames from x 888, landing on frame 62) with both bugs still at home, but 483 of the 484 ways off it that I tried are
  hurt and the last one just stays there (`early_tt_run2.py`, `early_tt_run3.py`). Jumps from the left block do not land on a roof (`early_tt_roof.py`).
- The record (`logs/fix/wr_tt_1.jpg`, `wr_tt_2.jpg`, video 412 to 419.5) comes along the duck channel, runs up the
  three steps and along the top without stopping, drops off the right end into the blue tank (in the water by 416.0)
  and swims down-right under the star chain. Where that tank is in our coordinates is still not pinned down: the blue
  area starts right of x 940 in our screenshots, beyond the shaft.
Parked again. The descent without the carry (250 frames against 424) and the corridor by the TAS's inputs stay as the
journal left them (net loss at our mine phases).

**Arctic Caverns (rank 8, 9).** From the "5000" of the last barrier to black: up14 215 frames, the record 180
(`logs/fix/wr_l4_lift.jpg`, `up14_l4_lift.jpg`). We reach that barrier 1.8 s ahead of him and end the level 1.3 s
ahead, so of Level 4's +99 frames about 30 are the lift and about 70 come before that barrier (not located in this
pass; the journal's candidate is the record's straight fall through the spike pit).

## 6. What a change costs downstream: the dice

Tested whether a changed upstream can be brought back onto the old dice so that later segments (above all the lucky
queen) replay verbatim. It cannot, by any knob I tried.
- Two entry bookmarks of the same level reached behind different upstream routes differ in RAM only by the score digit
  and its HUD sprite (`early_carry.py`), or by nothing at all two frames in (`L10c_end0` against `L10t_end0`), and
  still roll different dice 3 to 20 frames later.
- The difference is in the emulator core's state, not in RAM (`early_hidden.py`): program counter $872E against $8731,
  A, the flags and the frame timestamp, i.e. where the CPU stands inside the idle loop that scrambles $25 to $28
  (bank 0 $871F to $8756, 213 cycles a pass, seven writes to the dice per pass). It persists from frame to frame.
- Within one lineage, skipping a briefing page k frames later gives the identical dice for about a quarter of the
  delays (placements 0, 1, 4, 6, 7, 16, 26, 29, 30, 38, 57, 58, 63 and 82 frames late, of about 60 tried;
  `early_phase2.py`). Select or the choice
  of button on the page changes nothing.
- Across lineages (Rat Race `L10c` in place of `L10t` in front of `L11r`): **0 of 117** variants reproduce the dice
  (page delays 0 to 100, Select on 16 different frames of the last 1,800 inputs; `early_steer.py`).
So every item before Level 12 costs the same tail: rngfit of Levels 9 (3 re-rolls last time), 10 (0), 11 (3) and 12
(6 to 10), minutes each, and a queen re-solve (1.5 to 3 hours, 1,694 now, 1,830 to 1,861 typical: plan for +140 to
+170 frames coming back). Batch the items; build upstream first; end with one queen solve.

## 7. Files

Scripts (all new, all `early_*.py` in the harness root): `early_black.py`, `early_table.py` (section 1);
`early_l8boss.py`, `early_l8probe.py`, `early_l8arrive.py`, `early_l8arrive2.py`, `early_l8arrive3.py`, `early_l8fight.py`,
`early_l8verify.py` (item 1); `early_l8entry.py`, `early_l8entry2.py`, `early_l8climb.py`, `early_l8climb_verify.py`, `early_shots.py` (item 2); `early_mash.py` (item 3);
`early_l6fling.py`, `early_l6diag.py`, `early_l6vault.py`, `early_l6eject.py`, `early_l6vault2.py`, `early_l6vault3.py`,
`early_l6vault5.py`, `early_l6vault6.py` (Karnath; `early_l6vault4.py`, an earlier-jump scan, is written but was not run);
`early_l11fight.py` (Buzzball); `early_tt_carry.py`, `early_tt_run.py`, `early_tt_run2.py`, `early_tt_run3.py`, `early_tt_roof.py`,
`early_tt_shots.py` (Terra Tubes); `early_carry.py`, `early_hidden.py`, `early_phase.py`, `early_phase2.py`, `early_steer.py`
(dice); `early_b64.py` (decodes a contact sheet returned by the browser pane).
Outputs: `logs/fix/` (`early_*.txt`, `.tsv`, `.json`, `.out`; `wr_*.jpg` are sheets of the record's video, run time =
video time - 20.69 s, checked against his own timer; `up14_*.jpg` are ours; `early_tas1p_l8.txt` is the 1-player TAS's
Level 8 logged with FCEUX by `logs/fix/early_watch_l8.lua`).
Bookmarks made: `states/early_L8_p0.State` (up14 frame 12488), `states/early_hid_*.State`. The two failed `l4s.py` tries
left `knowledge/l4s_early_L8_p0_live.json` behind (nothing else of the old tools' files was touched).
Frame numbers throughout are up14 frames, 1-based as in `logs/up14.trace.txt`; `cap14_f<N>` is the state after N inputs.
The pieces a builder needs: `logs/fix/early_l8arrive_best.json`, `logs/fix/early_l8fight_e.json` (item 1);
`logs/fix/early_l8climb_mark1800d_v.json` (1,432 inputs from frame 12488, -211), `early_l8climb_1400b.keep_v.json` (-226 at
1,400 px), `early_l8climb_mark2200c_v.json` (-167 at 2,200 px) and the other `early_l8climb_mark<px><tag>.json` milestones
to resume from (item 2); `logs/fix/early_l6vault2_best.keep.json` (Karnath: the jump-grab and the walk over the head).
