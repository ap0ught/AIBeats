# Stage 2 (Base 1) - solver notes (2026-10-11)

Solver: `contra/stages/s2.py` (driver) on `base_common.py` (session, input rules), `base_plan.py` (room model and
planner), `base_room.py` (room driver), `base_boss.py` (boss beam search). Mechanics the solver relies on:
`knowledge/base_mechanics_notes.md`. Emulator: BizHawk 2.11.1 / NesHawk. Run it with
`python tools/s2_solve.py 2 ref_s2 <tag>` (about 30 minutes), table with `python tools/s2_table.py 2 <tag>`.

Segment = the stage's first frame with `$2C` = 4 to stage 3's first frame with `$2C` = 4. **Record: 3,716 frames.**

## Result (final driver; start state `states/ref_s2`: a real state from power-on, frame 4562, `$1A` 176, `$34` 210)

| file | start condition | segment | against the record |
|---|---|---|---|
| **`logs/s2/best.inputs.txt`** (= `f0`) | the state as it is | **3,636** | **80 ahead** |
| `logs/s2/f5.inputs.txt` | 5-frame pause before the first room (pause rows are in the segment) | 3,680 (3,675 without them) | 36 ahead |
| `logs/s2/f37.inputs.txt` | 37-frame pause | 3,683 (3,646 without them) | 33 ahead |
| `logs/s2/alt3634.inputs.txt` | the state as it is, an earlier driver version | 3,634 | 82 ahead |

All four: open-loop replay on a second emulator instance reaches stage 3's first frame on exactly the last row with
no death, weapon `$13` (Spread + Rapid), 3 spare lives; `check_inputs.py` at its defaults PASS (B about 200 presses,
fastest second 12, every press 2 frames). States of the best run: `states/s2/room1..room5`, `boss`, `boss_dead`,
`next_stage`.

## Per-room table (best run; "load" = rows after the stage's first frame; T counts from the room's load)

| room | load | core open T | first hit T | last hit T | floor (5-frame cap) | cleared T | next room T | frames | lag | re-plans | wall-explosion onset, ours | record's | ahead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 258 | 258 | 300 | 293 | 358 | 494 | 494 | 0 | 0 | 335 | 372 | +37 |
| 2 | 495 | 258 | 258 | 293 | 293 | 351 | 487 | 487 | 0 | 2 | 822 | 867 | +45 |
| 3 | 982 | 258 | 259 | 294 | 293 | 352 | 488 | 488 | 0 | 0 | 1310 | 1358 | +48 |
| 4 | 1470 | 258 | 259 | 294 | 293 | 352 | 488 | 493 | 5 | 7 | 1803 | 1871 | +68 |
| 5 | 1963 | 242 | 243 | 318 | 317 | 376 | 512 | 512 | 0 | 3 | 2315 | 2398 | +83 |
| boss | 2475 | platings 133 (+8 lag) | | defeated flag at row 2851 | | | | 376 | 8 at load | | 2851 | 2932 | +81 |
| exit | | | | | | | | 785 | | | 3636 | 3716 | +80 |

"Onset" = the wall-wide explosion: ours is last hit + 34 (+ lag); the record's is its video frame x 60.0988/60 after
its medals frame (`record_events.json`, +/- 2). Gain per room against the record: +37, +8, +3, +20, +15; the boss
is level with him (-2) and the exit is the same fixed 784-786 frames.

Floor = core open + 5 frames x (HP - 1): 293 for an 8-HP core, 317 for the 16-HP one. Rooms 2-5 are within one
frame of it; room 1 is 7 above because it has no turret and only one soldier before T = 224 to split bullet groups
with (model: 300 is the best with what is in that room).

## Spread over start conditions (f0 / f5 / f37)
Last core hit T: 300/300/300, 293/293/294, 294/293/293, 294/293/293 (lag 5/7/7), 318/317/320. The rooms are
scripted and come out the same within 1-3 frames whatever the frame-counter phase. The boss is where the spread
is: 376 / 412 / 380 frames (the driver runs the beam with three parameter sets and keeps the best; single runs
ranged from 368 to 456).

## What is verified and what is not
* Verified by replay (above): frame counts, no death, weapon out, lag (26 frames in the best segment: 5 in room 4,
  8 at the boss-room load, the rest at the stage change).
* NOT verified: the press cap across the stage boundary (the solver takes `hist` = the rows before the segment;
  these runs used an empty history, and the first B press of the segment is over 100 frames in).
* `ref_s2` comes from a fitted TAS stage 1, so a real run will arrive with another frame-counter phase and RNG; the
  pause variants are the only test of that so far. One failure on the way: with the 5-frame pause an earlier
  driver version could not get through room 5 (Bill kept being shot while standing up to fire; 19 re-plans). Fixed
  by (a) retrying the same plan from other standing spots and (b) after a death, demanding that every soldier on the
  back wall is shot within 45 frames of appearing - their bullets come straight down where Bill has to stand.
* The record's per-room numbers are from video (+/- 2 frames each).

## Tried and failed / things that cost time
* Fitting a Japanese-ROM TAS through the base (day 1): wrong tool; replaced by the planner.
* "Press as fast as allowed once the core opens" with no preparation: last hit T = 317 (the two 5-pellet groups
  come back together). All the gain over that is group splitting before the core opens.
* The fence trick: no gain (same next-room frame as Up on the frame after `$37` = 1), and Bill died doing it.
* Crouching while firing at a Y-104 core: crouch shots pass under it (arrival Y 116). Only room 3's core (Y 112)
  takes crouch shots.
* Boss: a greedy beam search (score = HP left minus bullets already on their way). It works but is noisy (368-456
  frames between parameter sets) and does nothing clever; the record's fight is about 374 by the same measure.
* Forbidding a press time after every death (first death handling): led to 19 re-plans and no solution in room 5
  under one start condition.

## What a faster press cap would have gained (computed from the model, not measured)
With 10 bullet slots and a 28-frame slot cycle the hose cannot go below one hit per 2.8 frames whatever the press
rate. Per 8-HP core: 5-frame cap 35 frames of hits, 4-frame cap 28, slot limit about 20. So against a 30 Hz TAS the
"no turbo" cap costs about 15 frames in each of rooms 1-4 and about 33 in room 5 (16 HP): roughly 1.5 s over the
five rooms, plus the boss, where our supply is one pellet per frame (5 per press) against 2.5.

## Remaining ideas (estimated frames)
1. Boss: plan the platings with jump-diagonal shots and attack the Eye with a scripted, parameter-searched jump
   (as for the stage 4 helmets): 40-100 frames.
2. Room 1: steer during the hop / reach the first soldier earlier for a third split before T = 238: up to 7.
3. Room 4 lag (5-8 frames): fewer wasted pellets while the rollers are out.
4. Steering during the 50-frame hop is not used anywhere (the driver starts moving at T = 51).

# Second pass (2026-10-12): the boss planned on an offline model, runs from the legal start

The rooms are the first builder's driver, unchanged. The boss is new and shared with stage 4:
`contra/stages/base_bsim.py` (exact offline model of the boss screen), `base_bplan.py` (beam search on it),
`base_bfight.py` (settings and the closed-loop executor); `s2.BOSS` now is `planned_boss(...)` with the first
builder's emulator beam as the fallback. Mechanics: `base_mechanics_notes.md`, "Second pass: the two boss screens";
method and the helmet-specific parts: `s4_notes.md`, "Second pass".

## Result (each replayed open-loop on a fresh emulator by `tools/s2_verify.py`; record 3,716)

| run | start | rows | vs record | rooms (frames each) | boss room row | boss rows | platings gone | final part open | parts dead | exit | lag | lost pad reads | plans (s) | replay |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L0 | s1/s2_start_legal (fc 109, rng 43) | 3610 | +106 | 495/488/488/495/512 | 2479 | 346 | 211 | 275 | 346 | 786 | 28 | 3 | 1291 (offline model plan) | OK, check_inputs PASS |
| L2 | s1/s2_start_legal_v2 (fc 106, rng 234) | 3604 | +112 | 494/488/488/492/512 | 2475 | 344 | 212 | 276 | 344 | 786 | 25 | 3 | 3547 (offline model plan) | OK, check_inputs PASS |
| g0 | ref_s2 (fc 176, rng 210) | 3613 | +103 | 494/487/488/493/512 | 2475 | 353 | 215 | 279 | 353 | 786 | 26 | 3 | 2863 (offline model plan) | OK, check_inputs PASS |
| g37 | ref_s2 + pause 37 (fc 176, rng 210) | 3666 | +50 | 495/488/488/495/514 | 2518 | 363 | 210 | 274 | 363 | 786 | 28 | 2 | 1444 (offline model plan) | OK, check_inputs PASS |

("boss rows" and the three columns after it are boss rows: counted from the row on which the boss room appears,
that row being 1. g37 contains its 37 pause rows: 3,629 without them.)

* `states/s1/s2_start_legal` and `_v2` are real states from power-on (stage 1's inputs
  `logs/s1/s1_w0_full.inputs.txt` / `s1_w0v2_full.inputs.txt`); their last 40 rows were passed as `--hist` and
  `check_inputs.py` was run on history tail + segment: PASS. The history path is exercised now, but it is a weak test:
  stage 1 ends with empty rows (score screen), so no press is anywhere near the boundary.
* First builder, for comparison: 3,636 / 3,680 / 3,683 from `ref_s2` with pauses 0 / 5 / 37.
* New files: `logs/s2/L0.inputs.txt` (legal start; states of this run in `states/s2/L0/`), `L2`, `g0`, `g37`.
  `logs/s2/best.inputs.txt` is still the first builder's file.

## Boss timeline (run L0)

| boss row | what |
|---|---|
| 10 | first frame with game logic; Bill is steered in the forced hop from here |
| 102 / 106 | the two wall cannons open / fire (they are not attacked: 16 HP for nothing; their bullets are in the model and avoided) |
| 142 / 143 | platings can be hit (upper middle and left on 142, lower middle and right on 143: two tile draws per frame) |
| 143 - 210 | 40 plating hits; fourth wreck drawn on row 211 (first builder: 236) |
| 275 | the Eye can be hit (= last plating hit + 65), X 128, moving right 1.25 px per frame it is not hit |
| 279 - 344 | 16 hits; boss-defeated flag on row 346 (first builder: 376 in his best run) |
| 1132 | stage 3's first frame (exit 786: fixed, 784-786 depending on lag) |

## The Eye (bank0.asm `boss_eye_routine_*`, reproduced by the model)
* Real HP 16 in ENEMY_VAR_1, box 22 x 22 at Y 64. Like the helmets: a hit costs it its next frame (no movement, no
  attack count), so one hit per frame is possible and a stream freezes it.
* It fires a ring 32 un-hit frames after it appears, then every 40. The ring leaves from the Eye toward where Bill
  is at that moment (direction quantised: `quadrant_aim_dir_01`, speed 1.74 px/frame), becomes solid at Y 72 and
  then has 2 HP and a 34 x 34 bullet box: it flies down the line our bullets fly up and swallows two of them. It
  also kills on touch. All of this is in the model (it explained the two frames of the first builder's fight the
  model had wrong before).
* Where pellets can go: the Eye is 51 px above the muzzle at the top of a jump. Only on air frames 20-38 (Bill within
  5 px of the top) and only from straight below do the centre and both +-1 pellets hit (3 of 5; the +-2 pellets
  miss and hold their slots for 37 frames); from anywhere else one pellet per press. So 16 hits are about six
  sprays from the top of two or three jumps plus single hits in between: 68-89 frames executed (first builder's
  fights: 76 in the best run). The "one hit per 5 frames = 80 frames" floor of the brief is beaten only by
  those 3-hit sprays; two bullets on consecutive frames from the ground are not possible (one pellet per press
  reaches it).

## Platings (40 HP)
* Lower three at Y 144 are 22 px above the standing muzzle: a spray from the ground straight under one puts all 5
  pellets in it. The upper middle one (Y 96) is hidden behind the lower middle one from below, but the muzzle is
  above the lower one near the top of a jump: all 5 pellets of a spray from x 128, air frames 20-36, hit the upper
  one. Diagonal sprays from 24-48 px to the side put 4-5 pellets into a lower plating (`tools/s4_map2.py 2`).
* Plans: 190-211 frames from boss row 10 between settings and start conditions; executed (with 0-3 lost pad
  reads): fourth wreck on boss row 210-215.

## What changed where (boss rows)
| | first builder (f0, from `ref_s2`) | this pass: g0 (same start) | L0 | L2 | g37 |
|---|---|---|---|---|---|
| platings gone | 236 | 215 | 211 | 212 | 210 |
| Eye can be hit | 300 | 279 | 275 | 276 | 274 |
| boss-defeated flag | 376 | 353 | 346 | 344 | 363 |
| Eye alone (flag - open) | 76 | 74 | 71 | 68 | 89 |

So the platings give 21-26 frames and the Eye 2-8, except in g37 where the Eye phase was 13 WORSE than the first
builder's best (a lost pad read on boss row 249, then a re-plan that needed two more jumps). The Eye search is the
weak part; the spread over start conditions is 344-363 boss rows against the first builder's 376 / 412 / 380.

## Tried and did not pay / failures
* First test fight from the first builder's boss state died on boss row 344 with 2 HP left on the Eye: the model
  kept only the last cannon's bullets when two cannons fired on the same frame, so the plan walked into a bullet of
  the left cannon. Fixed (`fired` is a list now); `tools/s4_hzcheck.py 2 x_fight_f0_partial` shows the model now
  dies on the same frame.
* Other planner settings for the platings (bucket 2 px / 2 frames with 4 nodes, alpha 0.005-0.015, no far-HP term):
  199-210 frames against 196-206 for the kept portfolio: no gain.
* The Eye with free movement and six settings: 122-295 frames from the last plating between settings (the search
  is much noisier here than for the helmets; the portfolio takes the best).
* Quick "search near the old path" repairs after a lost pad read are sometimes much worse than a full re-plan (216
  against 193 frames once); they are only accepted when they cost at most 2 frames.

## Verified / not verified
* Verified by replay: the row counts in the table, no death, weapon `$13`, 3 spare lives, check_inputs PASS (with the
  history tail for the legal starts).
* Not verified: a start with a press close to the stage boundary.

## Left on the table (estimates)
1. Platings: the plans need 61-70 frames for 40 hits from row 141; eight full sprays are 35 frames plus flight, so
   10-15 frames may be there for a search that plans the four platings as a whole (the beam is greedy in the first
   20 frames).
2. Eye: 68-89 frames; a dedicated planner like the helmets' (fixed lead positions, slots saved for the 3-hit sprays)
   should make it 65-70 from every start: 5-20 frames.
3. Lost pad reads: 3-4 per fight, each 1 frame or a re-plan.
4. Room 1 is 7 frames above the floor from every start tried (300 against 293); steering during the hop is still
   not used.
5. Solve time: 28-32 minutes alone (rooms 14, boss 14-18); the boss part was 40-50 minutes when three solves
   shared the machine.

# Third pass (2026-10-12, finished 2026-10-16): base_room3 rooms, boss plans probed on the emulator

Same code as stage 4 (see `s4_notes.md`, "Third pass", for what changed, the state the interrupted pass left and the
two changes of 2026-10-16: probing in `base_fight3.py`, the death cap in `base_room3.py`). For stage 2 the third
pass's room driver gives NOTHING: the five rooms come out exactly as in the second pass (they were already within
0-1 frames of the press-cap floor except room 1), and room 4 is still the first driver's plan (fewer lag frames).
What changed is only the boss executor.

## Result (each replayed open-loop on a fresh emulator, `tools/s2_verify.py`: stage 3's first frame on the last row,
## no death, weapon `$13`, 3 spare lives, `check_inputs.py` with the rule v2 windows PASS)

| start | second pass | third pass, code as found (2026-10-16) | final code | final file |
|---|---|---|---|---|
| `s1/s2_start_legal_v3` (rule-v2 stage 1, `logs/s1/s1_w0v3_full.inputs.txt`; `$1A` 108, `$34` 137) | - (new start) | 3,608 (`U2L3`) | **3,605** (`W2L3` full solve; `V2L3` = U2L3's boss re-played, same rows) | `logs/s2/W2L3.inputs.txt` |
| `s1/s2_start_legal_v2` (`s1_w0v2_full.inputs.txt`) | **3,604** (`L2`) | 3,611 (`U2L2`) | 3,607 (`W2L2` full solve; `V2L2` = U2L2's boss re-played: the same 3,607) | `logs/s2/L2.inputs.txt` stays the best for v2 |

Record: 3,716. Lag 25-26 (4-5 in room 4, 8 at the boss-room load, the rest at the stage change).
Rule v2 across the boundary (last 2,000 history rows + segment): PASS for the v3 start (B 219-220 presses). For the
v2 start it FAILS, but only inside the v2 stage 1 history itself (110+ presses per 600 frames from history row
545; the v2 stage 1 predates rule v2): the stage 2 segment adds nothing near a limit. Use the v3 start.

## Per room (v3 start, `W2L3`; the v2 start is the same within a frame)

| room | floor (last hit T, 5-frame cap) | last hit T, second pass (L2) -> third pass | frames | lag |
|---|---|---|---|---|
| 1 | 293 | 300 -> 300 | 494 -> 494 | 0 |
| 2 | 293 | 294 -> 294 (v2: 293) | 488 -> 488 | 0 |
| 3 | 293 | 294 -> 294 | 488 -> 488 | 0 |
| 4 | 293 | 293 -> 293 (first driver kept: 492 rows with 5 lag against base_room3's 495 with 8) | 492 -> 492 | 4-5 |
| 5 | 317 | 317 -> 318 | 512 -> 512 | 0 |

## Boss (boss row = segment row - 2474, as `s2_verify.py` counts; the boss room appears on row 2475)

| | L2 (second pass, v2) | U2L2 (as found, v2) | V2L2 (probing, v2) | U2L3 (as found, v3) | W2L3 (probing, v3) |
|---|---|---|---|---|---|
| platings gone | 212 | 216 | 208 | 214 | 213 |
| Eye can be hit | 276 | 280 | 272 | 278 | 277 |
| flag | 344 | 351 | 347 | 348 | 345 |
| Eye alone (flag - open) | 68 | 71 | 75 | 70 | 68 |
| lost reads that cost frames | 3 | 2 re-plans (8 + 3 frames) | none (1 expected) | 1 re-plan | none |

* Probing worked as meant: in W2L3 the 202-frame plating plan loses two button changes on the emulator and does
  not end the phase; the 203-frame one is clean and is played (U2L3 played the 202 one, lost a read around boss
  row 162 and needed a 3-minute re-plan: platings 1 frame later). From the v2 start it picked a clean 198 (U2L2 lost 8 frames there).
* The Eye phase is now the noise: 68-75 frames from its opening, depending only on where the plating phase leaves Bill
  (x 102 in the air for V2L2: 75). The six Eye settings spread 132-178 frames from the platings' end; the
  prepared-jump planner (`base_eye.py`) gave 152 against the portfolio's 132 from W2L3's state and was not used.

## Not done / left (estimates)
* Eye: choose the plating plan by plating + Eye together (the probe compares one phase): the v2 start shows 4-7
  frames between plating plans of equal length. The Eye planner itself (tighter Eye, item 1 of the remaining list)
  was not worked on in this session.
* Room 1: 7 above the cap floor, as before (steering the stage-start drop did not help: base_room3 finds 300 too).
* Room 4 lag: unchanged (4-5 lag frames; the "play both drivers" rule picks the first driver's plan).
* Stage 2 platings: not worked on (203 / 198 model frames from row 9).

Files: `logs/s2/{U2L2,V2L2,W2L2,U2L3,V2L3,W2L3}.inputs.txt`, `_report.json`, `_solve.out`, `_verify.out`; states of
the final v3 run in `states/s2t/W2L3/` (room1..5, boss, boss_dead, next_stage).
