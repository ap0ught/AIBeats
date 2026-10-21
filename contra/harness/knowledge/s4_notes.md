# Stage 4 (Base 2) - solver notes (2026-10-11)

Solver: `contra/stages/s4.py` = the stage 2 driver (`s2.py`, `base_room.py`, `base_plan.py`) with its own boss
(`base_boss4.py`). Mechanics: `knowledge/base_mechanics_notes.md`. Emulator: BizHawk 2.11.1 / NesHawk.

Segment = the stage's first frame with `$2C` = 4 to stage 5's first frame with `$2C` = 4. **Record: 5,761 frames.**

**Everything here starts from `states/dbg/s4_pre` (a RAM-poked debug state; stage first frame 578 saved as
`states/s4/dbg_L`, `$1A` = 46, `$34` = 60, weapon `$13`, 2 spare lives). Nothing built on it is part of a run;
it shows what the solver does, not a segment of the final movie.**

## Result

| run | start condition | segment | against the record | checked |
|---|---|---|---|---|
| `logs/s4/p0.inputs.txt` (= `v1`) | `s4/dbg_L` | 5,551 | 210 ahead | open-loop replay on a second emulator instance + `check_inputs.py` PASS |
| `logs/s4/p6.inputs.txt` = **`logs/s4/best.inputs.txt`** | same state, 6-frame pause before the first room (the 6 pause rows are in the segment) | **5,528** (5,522 without the pause rows) | **233 ahead** | `check_inputs.py` PASS; replay: see the end of this file |
| `logs/s4/p37.inputs.txt` | same state, 37-frame pause | 5,546 (5,509 without the pause rows) | 215 ahead | `check_inputs.py` PASS; replay: see the end of this file |

The shortest legal segment is the one with the 6-frame pause: the pause costs 6 frames and the boss search then
happened to find a fight 24 frames shorter. That is search noise, not a use for pauses.

Weapon carried out: `$13` (Spread + Rapid). No death. About 21 lag frames in each segment (boss-room load and the
stage change; 0-1 in the rooms).

Spread over the three start conditions (p0 / p6 / p37), last core hit T per room: 179/179/179, 464/465/464,
231/231/231, 324/324/323, 442/443/443, 305/305/305, 322/317/322, 322/320/319; platings gone 224/216/204 frames
into the boss room, boss fight 603/579/564. With the odd-length pause the cores of room 2 opened one frame later
(147 and 259): the opening draw waits a frame when the frame-counter parity is the other way. So the rooms are
the same within a frame or two except room 7 (jump timing, 5 frames) and the boss search (39 frames).

## Per-room table (run p0)

| room | what it is | load | core open T | first hit T | last hit T | floor | cleared T | next room T | frames | re-plans | onset, ours | record's | ahead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | plated core (23 hits), 2 turrets | 1 | 33 | 45 | 179 | 143 | 238 | 374 | 374 | 0 | 214 | 292 | +78 |
| 2 | 4 cores in a row (inner 146, outer 258), Y 112 | 375 | 146 / 258 | 146 | 464 | - | 522 | 658 | 658 | 2 | 873 | 1000 | +127 |
| 3 | 2 plated cores side by side, turret | 1033 | 33 | 36 | 231 | 143 | 290 | 426 | 426 | 0 | 1298 | 1482 | +184 |
| 4 | 2 cores side by side (Y 112), high turret | 1459 | 258 | 259 | 324 | 293 | 382 | 518 | 518 | 2 | 1817 | 2030 | +213 |
| 5 | 2 cores far apart, centre turret | 1977 | 258 | 258 | 442 | - | 500 | 636 | 636 | 4 | 2453 | 2785 | +332 |
| 6 | core, rollers | 2613 | 258 | 258 | 305 | 293 | 363 | 499 | 499 | 0 | 2952 | 3279 | +327 |
| 7 | "jump room": core at Y 88, turret | 3112 | 258 | 263 | 322 | 318 | 380 | 516 | 516 | 1 | 3468 | 3852 | +384 |
| 8 | big core (16 HP), 3 turrets | 3628 | 242 | 242 | 322 | 317 | 380 | 516 | 516 | 9 | 3984 | 4406 | +422 |
| boss | 3 platings, then 2 helmets | 4144 | platings 133 (+8 lag) | | defeated flag at row 4747 | | | | 603 | | 4747 | 4963 | +216 |
| exit | | | | | | | | | 804 | | 5551 | 5761 | +210 |

Gain per room against the record: +78, +49, +57, +29, **+119** (his bad room 5), -5 (room 6: he was 5 faster),
+57, +38; the boss **loses 206** and the exit loses 6.

Notes per room:
* Room 1 and 3 (plated): the plating can be hit from T = 33 but Bill is still in the air (stage-start drop until
  T = 32, walk-in hop until T = 50); airborne shots do reach the wide plating box, and the planner uses them (first
  hits at T 45 and 36). The floor of 143 needs a full hose from T = 33, which cannot exist that early: the only
  things that split bullet groups before then are the plating hits themselves.
* Room 2: the two inner cores take one hit each from one press (pellets 5 px either side of centre), the outer
  cores are 48 px apart at the wall, which is 128 px of walking, so they are killed one after the other; a grenade
  launcher soldier walks in front of the last core and has to be shot first. Crouch shots only (Y 112).
* Room 5: the same problem with two cores 48 px apart; killed left then right.
* Room 7: the core (Y 88) can only be hit by shots fired between frames 14 and 36 of a jump; five presses fit in
  one jump, so two jumps (the "two-jumper"): last hit T = 322 (317 in the pause-6 run), floor about 317.
* Rooms 6 and 4: only one or two things to split groups with before T = 238, so 12 and 31 above the floor.

## Boss
* Platings: HP 10 each from 133 frames after the enemies appear (8 lag frames at the room load first). Beam
  search: all three gone 224 frames after the room's first frame.
* Helmets: vulnerable 64 frames later (row 286) for 32 frames. The first run kills the right one with a jump
  attack from underneath (dead 60 frames after it opens: the search found a timing that hits it on the frame its
  timer runs out, so it stays open - the known bug), then **has to wait a whole cycle** (the left helmet reopens
  195 frames after the first dies) and kills it the same way: 603 frames in all. The record does the fight in
  about 397 by the same measure, i.e. he gets both helmets in the first opening.
* A second version of the search (`base_boss4.solve_boss`, `try_glitch`) looks for attacks on the first helmet that
  also leave the second one open while split, and then tries to finish it before it closes. **It found none**:
  not among the 135 ordinary attacks, and not among 450 attacks with a dedicated full spray from the ground under
  the right helmet (fire held for 28 frames, one spray timed over 15 frames; its outer pellet should reach the
  left helmet). Not understood yet; a version that holds fire for 55 frames (so five slots are really free) is in
  the code but was NOT run. The fight is therefore still two openings long.

## What is verified and what is not
* Verified by open-loop replay from `states/s4/dbg_L` on another emulator instance, all three segments (5,528 /
  5,551 / 5,546 rows): each reaches stage 5's first frame on exactly its last row, no death, weapon `$13`, 2 spare
  lives. `check_inputs.py` at its defaults: PASS for all three (B about 350 presses, fastest second 12, all 2 frames).
* The savestates `states/s4/room1..room8`, `boss`, `boss_dead`, `next_stage` are from run **p0** (5,551), not from
  the pause run that is `best`.
* NOT verified: anything from a real stage-4 start (none exists yet); the cap across the stage boundary.
* The driver changed slightly after these three runs (death handling: other standing spots for the same plan,
  "shoot the soldiers early" after a death); stage 4 was not re-run with it. Stage 2 was.
* The record's per-room numbers are from video (+/- 2 frames each).

## Tried and failed
* Beam search for the helmets (greedy score: HP minus bullets on their way): did not kill both in 700 frames in any
  of three parameter sets - it spreads hits over both helmets and neither dies in a window. Replaced by the
  scripted jump attack with a parameter search.
* Standing on the ground in the middle so the two inner pellets hit both helmets: each press then wastes three
  pellets that hold their slots for about 50 frames (they leave by the top of the screen); not tried in the
  emulator, rejected on the slot arithmetic.
* Planning the outer cores of rooms 2 and 5 from the middle: impossible, the pellet fan is 20 px wide at the wall.

## What a faster press cap would have gained (computed, not measured)
Plated cores are 23 hits each: 110 frames of hits at one per 5 frames, about 62 at the slot limit (one per 2.8).
Rooms 1 and 3 would each be roughly 45 frames shorter, the six 8-HP rooms about 15 each (more in rooms 2 and 5 with
their 32 and 16 hits), room 8 about 33: on the order of 250-300 frames (4-5 s) for the eight rooms.

## Remaining ideas (estimated frames)
1. Both helmets in the first opening (what the record does): about 200 frames.
2. End the fight further left / on the ground: the exit took 804 frames here against 784-786 in stage 2 and 798
   in the record: up to 20.
3. Rooms 4 and 6 at the floor (needs more group splits before T = 238: steer during the hop to reach the first
   soldier earlier): 31 + 12. Room 1 and 3: unknown, the plan depends on how fast a hose can be built from nothing.
4. Rooms 2 and 5: walk toward the second core while still killing the first: tens of frames each, not explored.

# Second pass (2026-10-12): the boss planned on an offline model - both helmets in the first opening

The rooms are the first builder's driver, unchanged. The boss is new: `contra/stages/base_bsim.py` (an exact
offline model of the boss screen), `base_bplan.py` (beam search on it) and `base_bfight.py` (settings, the closed-loop
executor); `s4.py` calls it through `s2.planned_boss(...)` and falls back to the first builder's search
(`base_boss4.solve_boss`) if it fails. The mechanics the model is built on are in `base_mechanics_notes.md`
("Second pass: the two boss screens"). Still everything starts from the RAM-poked debug state `states/s4/dbg_L`:
**nothing here is part of a run.**

## Result (three start conditions, each replayed open-loop on a fresh emulator by `tools/s2_verify.py`)

| run | start | rows | vs record | rooms (frames each) | boss room row | boss rows | platings gone | final part open | parts dead | exit | lag | lost pad reads | plans (s) | replay |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| q0 | s4/dbg_L (fc 46, rng 60) | 5268 | +493 | 374/658/426/518/636/499/516/512 | 4140 | 325 | 188 | 252 | 322/325 | 804 | 21 | 3 | 1348 (offline model plan) | OK, check_inputs PASS |
| q6 | s4/dbg_L + pause 6 (fc 46, rng 60) | 5276 | +485 | 373/659/425/519/637/499/512/513 | 4144 | 329 | 192 | 256 | 326/329 | 804 | 21 | 2 | 1218 (offline model plan) | OK, check_inputs PASS |
| q37 | s4/dbg_L + pause 37 (fc 46, rng 60) | 5309 | +452 | 373/658/426/517/637/500/516/513 | 4178 | 328 | 191 | 255 | 327/328 | 804 | 22 | 1 | 1831 (offline model plan) | OK, check_inputs PASS |

("boss rows", "platings gone", "final part open", "parts dead" are boss rows: counted from the row on which the
boss room appears, that row being 1. q6 and q37 contain their 6 / 37 pause rows: 5,270 and 5,272 without them.)

Old (first builder) for the same three conditions: 5,551 / 5,528 / 5,546. Record: 5,761.
The whole gain is the boss; the rooms came out as before within a few frames (room 8: 318 against 322).
`logs/s4/best.inputs.txt` is still the first builder's 5,528: the new files are `logs/s4/q0.inputs.txt` (5,268),
`q6.inputs.txt`, `q37.inputs.txt`; states of q0 in `states/s4/q0/` (room1..room8, boss, boss_dead, next_stage).

## Boss timeline (run q0)

| boss row | what |
|---|---|
| 10 | first frame with game logic; Bill is in the forced hop and is steered from here (the first builder waited until row 77 for the landing) |
| 102 | wall cannon opens (HP 8) |
| 109 - 128 | cannon hit 8 times from one jump under it: destroyed on row 128 (it would open again on row 292) |
| 142 / 143 | platings can be hit |
| 143 - 187 | 30 plating hits; the third wreck is drawn on row 188 (first builder: 223) |
| 252 | both helmets can be hit (= last plating hit + 65) |
| 254 | first helmet hit |
| 283 | a hit on BOTH helmets on the last frame of the merged window (delay byte $0538+slot reads 1 after the helmet's routine): both stay hittable while split |
| 322 / 325 | left helmet's parts-left decrement / right helmet's and the boss-defeated flag (first builder: 347 and 604) |
| 1129 | stage 5's first frame (exit 804, fixed) |

The helmets take 73 frames from the first frame they can be hit (73 in all three runs; first builder
317: one per opening; the record holder's fight is about 100 by the same measure).

## Helmet facts (bank0.asm `boss_gemini_routine_*`, all reproduced by the model and seen in the emulator)
* Created with the room in slots 14 (X 104) and 13 (X 152), Y 48, real HP 10 in ENEMY_VAR_4 ($05E8 + slot),
  ENEMY_HP is 1. Routine 1 waits for 3 destroyed platings, then counts 64 frames; on the frame the count ends the
  bullet collision is switched on and the helmet can be hit on that same frame.
* Merged window: the delay byte ($0538 + slot) is set to 32 and counts down once per frame (in routine 2 when the
  helmet was not hit on the previous frame, in routine 3 when it was). When ROUTINE 2 takes it from 1 to 0 the
  collision is switched off: 32 hittable frames. When routine 3 does (= the helmet was hit on the frame the byte read
  1 after its routine, the 32nd frame), nothing switches it off: the helmet splits and stays hittable until the far
  rest (48 px out, 96 moving frames later) has run its own 32-frame count - unless it is hit on that count's last
  frame too. This is docs/Bugs.md #3; "delay reads 2" there is the value at the frame's start.
* A hit: next frame routine 3 (HP - 1, delay - 1, no movement), and the bullet test runs again on that frame: one hit
  per frame per helmet is possible, and a helmet that is hit every frame does not move.
* Split: offset from the merge point +0.5 px per frame it is not hit; drawn (and hittable) at X0 + offset on even
  frame-counter frames, X0 - offset on odd ones. Both helmets run the same count, so the "double glitch" needs a
  bullet inside each box on one and the same frame.
* The 10th hit: routine 3 next frame, routine 4 the frame after (parts left - 1; at 0 the boss-defeated flag): flag =
  last hit + 2.
* The helmets fire bubbles 160 un-hit frames after they open (the model stops there; the fight is over long before).

## Where the pellets can go (model, `tools/s4_map.py`: one full spray, hits on left/right helmet)
* The helmets are 129 px above the standing muzzle and 67 px above the muzzle at the top of a jump: the 5 pellets
  (11.25 degrees apart) are 13-25 px apart up there. No position puts more than 2 pellets into one helmet.
* Standing or jumping anywhere from x 96 to 160 and firing straight up: one pellet in each helmet.
* **In the air at x 128, air frames 15-42, cannon destroyed: the +-1 and the +-2 pellets hit, two in each helmet (4
  of 5; the centre pellet flies on between them).** x 132: the same on air frames 21-39.
* **With the cannon alive it swallows the centre and the +-1 pellets of such a shot** (it sits at (128, 80), box 22
  wide): 2 of 5 from x 128, 3 of 5 from x 124 or 132. And its second volley (row 295) comes straight down the
  middle about 85 frames after the helmets open. So the cannon is destroyed in its first opening, while the
  platings are still shut: from the first builder's boss state the platings were gone on boss row 195 either way, and the flag came on
  row 355 with the cannon alive, on row 332 with it destroyed (23 frames).
* While split (offset 14-18 px) all five pellets of a shot from x 128 can hit: the centre one hits the inner
  phantoms of both helmets on alternate frames.
* Supply is the limit, not the press cap: a pellet that hits holds its slot for flight (20-26 frames) + 7 frames, so
  two full sprays (8 hits) per 30 frames at best and only while Bill is high in a jump (28 of every 60 frames).
  20 hits therefore take two jumps and a bit: 70-75 frames. "10 hits each on consecutive frames inside the first
  window" (research.md) would need 20 pellets to arrive within 32 frames: not reachable with ten slots.

## How the fight is planned
* Phase A (platings + cannon): beam search over frames on the model; a node = model state + press history of Left,
  Right, Up, A, B (so every plan obeys the input rules). Rank inside a frame: HP left after the bullets in the air
  have landed (a rollout of the model) + 0.01-0.03 x slot-frames still busy + a term for HP far from Bill; the frame
  keeps the best few of every (x, airborne phase, which parts are damaged) bucket. Six settings in six processes
  (the "portfolio"), best plan wins: 176-199 frames between settings.
* Phase B (helmets): Bill walks to a standing x (128, 126, 130, 129) during the 64-frame wait and fights from there;
  a helmet that would close with HP left counts 30 extra HP and the line is dropped when it happens; the bucket key
  also says how many slots a line will have free at the frame the "last frame" shot must be fired (opening + 9).
  Without these two the search filled up with lines that had spent their slots early and could not keep the helmets
  open (best 106-130 frames after opening, half of the settings found nothing).
* Execution: one frame at a time; before a frame on which the buttons change the emulator state is saved, and if the
  game then did not read the pad (2-4 times per fight) the frame is taken back and the plan is shifted by a frame,
  repaired by a quick search near the old path, or re-planned. Plans keep 2 px between Bill and a cannon bullet (with
  1 px a lost pad read at boss row 154 was fatal in a test).

## What was tried and did not pay (measured)
| tried | result |
|---|---|
| one beam for everything with free movement in the helmet phase (ranking: HP after rollout + busy slots) | flag 96-130 frames after the helmets open; 3-5 of 6 settings found no kill at all |
| the same with the cannon left alive, Bill fixed at x 128 | every line dies about 92 frames after the opening (the cannon's second volley comes down the middle) |
| helmets with the cannon alive, best standing x (124), free to move after the window | 106 frames after the opening (cannon destroyed: 73-75) |
| 1 px safety margin to cannon bullets | plating phase 3 frames shorter, but a lost pad read killed Bill once: 2 px kept |
| other portfolio settings for the platings (alpha 0.04-0.08, bucket size 1 or 3 with the old tie-breaking) | 207-306 frames against 191-192 for the kept ones (from the first builder's boss state) |
| ending the fight further left (first builder's idea for the exit) | nothing to gain: the exit is 804 frames from the flag with Bill waiting at the left edge 29 frames early; it is the stage, not the position |
| rooms 4 "31 frames above the floor" | not real: the two cores are 16 px apart, a press hits both only with at least 3 pellets (centre, +4, -5), so the hose is three 3-pellet groups per 28 frames = one double hit per 9.3 frames; 258 + 7 x 9.3 = 323, we have 323-324 |

## What is verified and what is not
* Verified by open-loop replay on a fresh emulator (`python tools/s2_verify.py 4 <tag> s4/dbg_L`): the three row
  counts above, each reaching stage 5's first frame on exactly its last row, no death, weapon `$13`, 2 spare lives,
  `check_inputs.py` at its defaults PASS.
* The model against the emulator: every frame of every fight is compared while it is played (0-1 re-loads per
  fight, on the frame the room loads).
* NOT verified: anything from a real stage 4 start (none exists yet); the press cap across the stage boundary (no
  history file for stage 4 yet; the code path is the one stage 2 uses with `--hist`, which is exercised there).
* Assumed: that the helmets' 20 hits cannot be delivered much faster than 70 frames (slot arithmetic above, not a
  proof).

## Left on the table (estimates)
1. Plating phase: 176-185 planned frames depending on the setting and start (30 hits from row 141; the arithmetic
   floor is about 141 + 40): maybe 5-10 frames with a better search or a hand-made opening.
2. Helmets: 70-73 frames; a plan from an idealised start (Bill standing at x 128 when the platings go) gave 75 in the
   model, so there is no obvious gain left without a new idea.
3. Lost pad reads cost 1-3 frames per fight (each shifts the plan by a frame).
4. Rooms: room 6 (305 against 293) and room 7 (322 against 318) by steering during the 50-frame hop: at most
   12 + 4. Rooms 1 and 3 (plated, 179 and 231 against a 143 press-cap floor that the ten slots do not allow):
   unknown, not looked at. Rooms 2, 4, 5: at what the slots allow (see the table above for room 4).
5. Solve time: rooms about 26 minutes, boss 13 minutes alone (20-25 when three solves share the machine).

## How to run (both base stages)
* `python tools/s2_solve.py <2|4> <state> <tag> [--pause N] [--hist inputs.txt] [--states DIR]` as before; it must be
  started as a script (the boss planner spawns worker processes: `BASE_BOSS_PROCS`, default 6; `tools/s2_queue.py`
  sets 4 and runs several solves side by side, each followed by its replay).
* `python tools/s2_verify.py <2|4> <tag> <state> [--hist inputs.txt]`: open-loop replay on a fresh emulator, boss
  timeline, check_inputs with the history tail in front. `python tools/s2_summary.py <2|4> <tag> ...`: the tables above.
* Do not edit `base_bsim.py`, `base_bplan.py` or `base_bfight.py` while a solve is running: its workers import them
  when the boss room is reached.
* Model development: `tools/s4_simcheck.py` (model against a RAM capture), `tools/s4_hzcheck.py` (cannon-bullet
  deaths), `tools/s4_planx.py` (plan one phase offline from a capture frame), `tools/s4_map.py` / `s4_map2.py`
  (which pellets of a spray hit what from where), captures `logs/s2|s4/x_cap_*.npy`.

# Third pass (2026-10-12, finished 2026-10-16): the rooms with base_room3, and boss plans probed on the emulator

The third pass was stopped on 2026-10-12 before its report; it was resumed and finished on 2026-10-16. What it
changed: the rooms are driven by `contra/stages/base_room3.py` on the planner `base_plan3.py` (Bill's entry x
chosen during the previous room's clear, the 50-frame hop steered, walking shots, lost controller reads re-planned
from the row they happen with everything before kept; mechanics in `base_mechanics_notes.md`, "Third pass"); the
first builder's driver (`base_room.py`) is the fallback for a room base_room3 cannot do. The boss executor is
`base_fight3.py` (lost-read repair, and since 2026-10-16 PROBING: the portfolio's candidate plans are played
open-loop on the emulator from the current state before one is chosen, because which button changes the game does
not read depends only on the inputs; the chosen plan's known losses are then expected, not repaired).

State found on 2026-10-16: `base_room3.py` was complete and consistent (last written 10:26, before the verified
`T4r` solve started at 10:48; the announced "rewrite in full" had not begun, no partial file). `T4r` (5,154) was
made by the current `base_room3`, `base_plan3`, `base_bfight` (10:48), `base_bplan`, `base_eye` and an earlier
`s2.py`; `s2.py` and `base_fight3.py` were changed at 11:36-11:37 and had never run. All of it compiled and imported.
Re-solved from scratch with the code as found (`U4r`): 5,154 rows again, room for room and row for row.

Changes made on 2026-10-16 (both kept as `.backup_pass3a`):
* `base_fight3.py`: the probing above (`PROBE`, `PROBE_SLACK` = 8, `probe()`, `plan()` keeps every candidate).
* `base_room3.py`: a room is given to the first driver after `MAX_DEATHS` = 10 death attempts. From `s4/dbg_L`
  (no pause) room 4 died 32 times at x 127, one frame later each time (a bullet aimed at Bill), for 18 minutes before
  the 30 re-plans ran out; the verified runs needed at most 4. Same rows as before, solve 4,139 s -> 2,539 s.

## Result (each replayed open-loop on a fresh emulator by `tools/s2_verify.py`: next stage's first frame on the last
## row, no death, weapon `$13`, `check_inputs.py` with rule v2 windows PASS)

| start | before (second pass) | third pass, code as found | final code | final file |
|---|---|---|---|---|
| `s4/real_c1` (REAL, chain1; history `chain1/runs/through_s3.inputs.txt`) | 5,269 (chain1) | 5,154 (`T4r`, `U4r`) | **5,153** (`W4r` full solve; `V4r` = U4r's boss re-played, same rows) | `logs/s4/W4r.inputs.txt` |
| `s4/dbg_L` | 5,268 (`q0`) | 5,163 (`U4d0`) | 5,164 (`W4d0`) | `logs/s4/U4d0.inputs.txt` |
| `s4/dbg_L` + pause 6 | 5,276 (`q6`) | 5,171 (`U4d6`; 5,165 without the pause rows) | not re-run | `logs/s4/U4d6.inputs.txt` |
| `s4/dbg_L` + pause 37 | 5,309 (`q37`) | 5,195 (`U4d37`; 5,158 without) | not re-run | `logs/s4/U4d37.inputs.txt` |

Record: 5,761. The real start is now 608 frames under the record's segment. Lag 22-23 in every run (8 at the boss
room's load, 1-2 in room 6, the rest at the stage change). Weapon `$13`, lives 4 (real) / 2 (debug). Rule v2 across
the boundary: `check_inputs.py` on the last 2,000 rows of `through_s3` + `W4r`/`V4r`: PASS (B 312 presses, fastest
second 12). States of the final real run: `states/s4t/W4r/` (room1..8, boss, boss_dead, next_stage).

## Per room, real start (`s4/real_c1`): last hit T and frames, second pass (chain1) -> third pass (`W4r`)

| room | what | floor (last hit T) | last hit T before -> after | frames before -> after | gain |
|---|---|---|---|---|---|
| 1 | plated core, 2 turrets | 179 (slot limit, base_mechanics third pass) | 179 -> 179 | 374 -> 374 | 0 |
| 2 | 4 cores in a row, Y 112 | - (two kills 48 px apart) | 464 -> **417** | 658 -> 612 | 46 |
| 3 | 2 plated cores | 206 (planner, beams 12,000 and 50,000 agree) | 232 -> **206** | 426 -> 401 | 25 |
| 4 | 2 cores 16 px apart, Y 112 | 323 (three 3-pellet groups per 28 frames) | 323 -> 324 | 517 -> 519 | -2 |
| 5 | 2 cores far apart | - | 444 -> **403** | 639 -> 597 | 42 |
| 6 | core, rollers | 293 (press cap) | 305 -> 305 | 501 -> 500 | 1 |
| 7 | core at Y 88 (jump shots) | 317-318 | 317 -> 318 | 512 -> 512 | 0 |
| 8 | big core (16 HP) | 317 | 319 -> 317 | 513 -> 512 | 1 |
| boss | 3 platings + cannon, 2 helmets | | flag on boss row 325 -> 322 | | 3 |
| total | | | | 5,269 -> 5,153 | **116** |

The other starts give the same rooms within 1-3 frames (room 2: 417-420, room 5: 403-409), except room 4 from
`dbg_L` without a pause: base_room3 died there 10+ times and the first driver did it (323, 517 frames - 2 better than
base_room3's 324/519 everywhere else).

## Boss (real start; boss row = segment row - 4027, as `tools/s2_verify.py` counts: the boss room appears on segment row 4028)

| | second pass (chain1) | `U4r` (as found) | `W4r` (probing) |
|---|---|---|---|
| plan A (platings + cannon), model frames | | 174 (a lost read around boss row 138, re-planned: 3 frames lost) | 175, chosen by probing: the two 174-frame plans lose a button change around boss row 137 and do not end the phase on the emulator; the 175 one loses one on row 40 that changes nothing |
| platings gone (third wreck drawn) | 188 | 187 | 185 (segment row 4212) |
| helmets can be hit | 252 | 251 | 249 (row 4276) |
| boss-defeated flag | 325 | 323 | 322 (row 4349) |
| exit | 804 | 804 | 804 |

Probing in numbers (each a re-play of the same boss state with the same rows before, so the only difference is
the executor; flag rows): real 323 -> 322, stage 2 v2 351 -> 347, stage 2 v3 348 -> 345; from `dbg_L` the full solve
gave 325 against 324 (probing picked a 178-frame phase A that ends at Bill x 117 and the helmet plan from there was 2 frames
longer: it compares phase A only).

## Not done / left (estimates)
* Room 4: the first driver's plan is 2 frames shorter (517 against 519, measured from `dbg_L`); playing both drivers
  for that room (as `s2.solve` does for lag rooms) would take it. Not done: it needed another full validation round.
* Rooms 6-8 were not worked on beyond what base_room3 gives (room 6: 305 against the cap floor 293; 7 and 8 at
  their floors). Room 6 needs more group splits before T 238 than the room has targets for.
* Probing compares one phase; ranking phase A plans by phase A + a quick phase B estimate could avoid the `W4d0` case.
* Not re-run with the final code: the two pause variants (their numbers are the code as found).

Files: `logs/s4/{U4r,V4r,W4r,U4d0,W4d0,U4d6,U4d37}.inputs.txt`, `_report.json`, `_solve.out`, `_verify.out`;
`tools/s2t_bossprobe.py` (re-play only the boss of a finished solve from its saved boss state, for A/B tests of
the executor); queue logs `logs/s4t/queueU.out`, `queueW.out`.
