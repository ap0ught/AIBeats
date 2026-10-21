# Stage 3 (Waterfall) - builder's notes

Emulator: BizHawk 2.11.1 / NesHawk. Development state: `states/dbg/s3_pre` (debug: stage and weapon `$13` written
into RAM by `tools/mk_stage_state.py`; first frame L = 573). Nothing below is part of a run from power-on.
Files: `contra/stages/s3.py` (solver), `s3_model.py` (exact movement model), `s3_plan.py` (search on the model),
`s3_climb.py` (the search with every node validated in the emulator), `s3_exec.py` (closed-loop player),
`s3_boss.py` (boss and exit), `s3s8_engine.py` / `s3s8_lib.py` (shared with stage 8), `tools/s3_*.py`,
`knowledge/s3_map.json` (collision map).

## 1. Result

Best legal segment: **`logs/s3/best.inputs.txt` / `.seg.json` (= run v3): 3,540 rows from the stage's first frame
to stage 4's first frame; the record's stage 3 is 3,934 (394 frames = 6.6 s ahead).** No death, weapon out `$13`
(Spread + Rapid), `check_inputs.py` at its defaults: PASS. The solver replays the finished rows open-loop from the
stage state and checks that the next frame is stage 4's first (`$30` = 3, `$2C` = 4): yes. States:
`states/s3/stage_start_dbg` (= `dbg/s3_pre`), `best_climb_end` (top floor), `best_mouth_minus70` (70 rows before
the mouth opens), `best_next_pre` (one frame before stage 4's first frame). All of debug lineage.
Earlier legal runs kept: v1 = 3,875 (`best_legal_v1.*`, dragon killed in its second window), v2 = 3,570.

Timeline in rows from the stage's first frame (row r produces frame L + r), record = video frames after the
medals x 1.00165:

| event | ours (v3) | record |
|---|---|---|
| standing after the drop-in | 40 | |
| top floor (row -108) | 1,977 | (human 5-skip climb: 2,347 to "standing on the boss ledge") |
| boss scroll starts (A >= 1,872) | 1,995 | |
| scroll ends | 2,059 | about 2,589 ("boss screen reached", +-24) |
| mouth first hittable | 2,702 (707 after the scroll start) | |
| dragon dead (boss flag) | 2,827 (125 after the opening) | 3,274 (first explosion) |
| control lost | 2,983 (flag + 156) | 3,377 |
| stage 4's first frame | **3,540** (flag + 713) | **3,934** |

Lag: 41 frames: 25 in the level (firing Spread at the mouth), 16 in the transition. The climb itself has 0 lag
frames (it does not fire). Ignored-pad frames in the climb are absorbed by validation.

Start conditions (debug states made by `tools/s3_mkvariants.py`: the opening waits k frames on the title screen;
k = 1 changes only `$34`, k = 37 also the frame counter), each solved from scratch by `python -m contra.stages.s3`:

| state | `$1A` / `$34` at L | rows | top floor | scroll | mouth open | dragon dead | lag (level) | skips | emulator trials | wall time |
|---|---|---|---|---|---|---|---|---|---|---|
| `dbg/s3_pre` (k = 0) | 44 / 54 | **3,540** | 1,977 | 1,995 | 2,702 | 2,827 | 41 (25) | 13 | 1,574 | 10 min |
| `s3/var1_pre` | 44 / 187 | **3,526** | 1,961 | 1,981 | 2,688 | 2,814 | 39 (23) | 13 | 1,713 | 11 min |
| `s3/var37_pre` | 80 / 15 | **3,497** | 1,951 | 1,971 | 2,677 | 2,782 | 36 (20) | 13 | 1,546 | 11 min |

Spread 43 rows; all three: no death, weapon out `$13`, 0 rule violations, `check_inputs.py` PASS
(`logs/s3/var1.*`, `logs/s3/var37.*`). The differences come from the enemies (which proposals survive) and from
the 8-frame rule below.

## 2. Geometry (measured)

* A vertical "screen" is **240 px** (`$65` wraps at `$F0`), not 256. A = `$64`*240 + `$65` = pixels climbed.
* Collision cells are 16 px; world row `q = (Y + 16 - A) // 16` under the player point; standing on row q means
  `Y = A + 16*q - 12`. The whole map (rows 12 .. -108; only floor cells, no solid cell anywhere) was dumped with
  `tools/s3_dumpmap.py` (debug fly-through). Start floor = row 12, boss floor = row -108: **120 rows = 1,920 px**.
* The boss scroll starts on a scroll frame with A >= 7*240 + `$C0` = **1,872** and then runs 64 px by itself
  (A = 1,936). The only floor on the boss screen is row -108 (standing Y 196); from it one more jump is always
  needed to start the scroll (it starts 20 rows after the A press).
* Floating rocks (type `$10`): spawn at A = 736 (X 80, 0.5 px/f left, between X `$50` and `$B0`), A = 848 (X 112,
  0.75 px/f right, `$70`-`$C0`), A = 1,320 (X 128, 0.75 px/f). Standing on a rock = rock Y - 27. Rock 2 stands
  exactly 64 px above row -50 and 32 px below row -56 (reached with a skip jump from row -50, row -52 is not
  needed); rock 3 stands 40 px above row -81 and 40 px below row -86. Rows -52 -> -56 and -81 -> -86 cannot be
  passed without them (64-80 px up and 65+ px sideways).
* Bridge = row -37, full width, two flames (type `$11`, created at A = 595 at X 80 and 176, 0.5 px/f between X
  `$48` and `$B8`). A flame kills a standing Bill within 11 px. They cross in the middle about 96 frames after
  they appear and are at the two ends 112 frames later. The floor below (row -34, X 0-63) only lets Bill land on
  the bridge at X <= about 104, left of where the flames meet.

## 3. The ledge skip - mechanism as verified in the emulator

Model = `contra/stages/s3_model.py`; `tools/s3_verify_model.py` compares it frame by frame with the emulator
(X, Y, `$94`, A). Result: 40 of 40 ordinary jumps identical; with Y and `$94` set to random values after the A
frame (debug pokes, to exercise the scroll phase) every jump identical except landings on a floating rock, lag
frames (the game skips its logic for that frame) and jumps after the boss scroll. A planned 14-jump climb with
six 64-px skips then replayed with every landing equal to the model in X, Y, `$94` and A, and the final route's
39 jumps were all proposed by the model.

What the code does each airborne frame (bank7.asm `handle_jump`, `set_vertical_level_frame_scroll`,
`calc_player_x_vel`):

1. velocity += `$0023` (start `$FBF0`): 29 rising frames whose whole-pixel rises are 4 x7, 3 x8, 2 x7, 1 x7 = 73 px
   if no carry is ever counted; the true sum of the velocity is 58.3 px - the difference is the carries of `$94`.
2. If Y < `$50` and rising: `$94` += low byte of the velocity; **scroll = whole rise - carry**, Y does not move.
   Otherwise the same add moves Y.
3. Then X: if Bill moves right this frame (and X < `$E6`), step 2's scroll routine runs **a second time**:
   `$94` += low byte again and the scroll is recomputed from the second carry only. Left / no direction = one add.
4. **The frame Y crosses below `$50` while moving right gets both**: Y has already moved (step 2 took the "not
   scrolling" branch) and the second call scrolls a whole extra frame's rise (3-4 px).

Numbers (model, confirmed by replay), under our input rules (direction runs >= 2 frames, same-direction starts
>= 5 frames apart; the latch keeps a direction when nothing is held):

| take-off | best total rise | lands 64 px up? |
|---|---|---|
| standing Y < `$50` (every rising frame is a scroll frame) | 65 px for 172 of 256 values of `$94`, 64 px for the other 84 | **never** |
| standing Y 80..about 103, moving right on the crossing frame | 67-69 px | yes, when `$94` allows it |
| no right movement at all (single adds) | 58-59 px | no |

* **A landing h px higher needs a total rise of at least h + 3** (the landing test only runs once the fall speed is
  >= 1 px/frame: 9 frames and 5.3 px after the top): +48 needs 51, **+64 needs 67**. So "65 px per jump" (the code
  notes' figure) is NOT enough for a skip; the skip exists only because of the crossing-frame bonus (item 4),
  i.e. from a take-off between Y 80 and about 103 with rightward movement. This disagrees with
  `code_player_mechanics.md` section 3 ("65 px ... enough to reach ledges a normal jump misses") and explains the
  human rule "jumps to the right must be full right".
* Rows from the A press to standing (A frame included): +64: 40-41; +48: 40 (lowest rise) to 44; +32: 46-48;
  +16: 53. A skip is as fast as a +48 jump and gains 16 px more; a lower rise lands sooner AND leaves Bill higher
  on the screen (Y near 80) for the next skip, so the search prefers the most carries that still reach.
* The last moving platform "moves 3 frames and rests 1" = 0.75 px per frame, as measured.

## 4. The route: 40 steps, 13 skips, 2 rocks

`logs/s3/best.report.json` has the chain (row, X, Y, `$94`, A, rows). Floor rows and the row count at each landing
(* = reached with a 64-px skip): 10@116, 8@166, 6@214, 2*@268, -2*@308, -6*@348, -8@395, -11@435, -15*@475,
-18@515, -21@555, -24@595, -28*@635, -32*@675, -34@721, -37 (bridge; 66 frames waited on the floor below)@834,
-41*@921, -43@968, -47*@1008, -50@1048, rock 2*@1088, -56@1138, -59@1178, -63*@1218, -65@1265, -68@1305, -70@1352,
-73@1392, -77*@1432, -78@1487, -81@1527, rock 3@1576, -86 (48 frames riding)@1690, -90*@1730, -92@1777, -95@1817,
-98@1857, -102*@1897, -105@1937, -108@1977.

Why not more skips: a skip needs (a) a floor exactly 64 px up within about 40 px sideways, (b) a take-off with
standing Y between 80 and about 103 - after a +32 or a slow +48 jump Bill stands lower on the screen (Y 107-122
in this route) and the next jump cannot skip, (c) a `$94` and X displacement the rise table can serve. The first
four floors (12 -> 10 -> 8 -> 6) are 32 px apart with Bill still at the bottom of the screen (no scrolling at
all below Y 80), and both rocks force +32/+40 steps. Humans manage 5 skips, published TASes 6-7 (different ROM
timing, 30 Hz inputs); this route has 13 because the search treats every 64-px pair of floors as a candidate.

How it is found (`s3_climb.py`): a layered beam over floor rows. For every standing node (a real savestate) the
model proposes jumps: walk 0.. frames, then a rise taken from a table of every achievable (carries, X displacement)
under the input rules, then an exactly simulated fall. Proposals are played in the emulator from the node's
savestate (about 1,300 trials, 5 minutes on 3 emulators) and kept only if Bill stands on the higher floor, alive,
weapon unchanged, and survives 8 more frames there. So every node carries its true row count (lag, waits, lost
presses included). Rounds with waits (4-192 frames) and with firing are used only where nothing else survives.

What is random and how it is steered: the climb never reads `$34`; enemies (mortar shells of the scuba divers,
turret bullets, soldiers, boulders) simply kill some proposals and the next best one is taken. Firing is avoided
(section 6). The bridge and the rocks are timing puzzles, not luck: more arrival nodes are generated there (the
right-most landings delayed by 0-126 frames; 6-126 more frames riding a rock).

## 5. The dragon

* Timers, measured with `tools/s3_framerule.py` (debug: Bill kept alive by a poke, 10 runs with the trigger jump
  delayed 0-9 frames; rows after the scroll start): scroll ends +63, palette fade ends +183..190, the hands (HP 16
  each) appear 4 frames later and finish extending 122 frames after that, **the mouth is first hittable 700-707
  rows after the scroll start**, open 112 frames, closed 222 frames with both arms alive (second opening +334).
* **The 8-frame rule is real**: the fade ends on a multiple of 8 of the frame counter, so the opening comes at
  `700 + ((6 - frame counter at the scroll start) mod 8)`: starting the scroll 1 frame later moved the opening by
  0 frames in 7 cases of 8 and by 8 frames in the eighth (measured: delays 0, 1, 2 -> the same opening frame;
  delays 3..10 -> 8 frames later). Run v3 has 707: one frame saved anywhere in its climb would be worth 8.
* The mouth: X 128, Y 63, HP 32 (the byte shows 32 on the opening frame). Six frames after opening it drops three
  fireballs; the middle one falls straight down at X 128 at 1.7 px per frame and kills anything within 11 px of
  that line about 60 frames later. **X 116 is the nearest spot it misses**; from there one jump straight up with B
  at the legal cadence landed 23 hits (first jump, started 4 frames before the opening) and the second jump the
  other 9: dead 124 rows after the opening, inside the first window (112 game frames + 22 lag frames).
  Standing shots from the floor land about 1 pellet per press (0.15 HP per frame).
* Arms were left alone: a test that shot the right hand from X 181 took it from 16 to 3 HP in 290 frames (it moves
  away after 60 frames) - too slow to be worth the lag. So the freeze of docs/Bugs.md #4 (left hand's last hit on
  the frame before its arm finishes extending) cannot occur; the solver also treats a lag streak of 12 frames as a
  failure, which would catch it.
* Waiting for the mouth: stand still, repair deaths by lookahead (a soldier crosses the floor about 100 frames
  after the scroll starts: one jump; two more jumps for arm bullets).
* Exit (measured from the boss flag): control lost +155; stage 4's first frame +711 standing at X 120-136, +716
  at X 116, +727 at X 152, +729 at X 104. Nothing to gain beyond standing in the middle.

## 6. Lag and lost presses

* Firing Spread during the climb makes lag: 29 lag frames in two jumps of an early run (10 bullets + 11-16 enemy
  slots live). Without firing the same climb had 0. Firing at the mouth: 22 lag frames in 124 rows.
* The DMC/controller conflict: a few ignored-pad frames per climb; validation absorbs them.

## 7. Start conditions

See section 1.

## 8. What was tried and failed

* Following a model-only plan open-loop: fails at the first ignored-pad frame and at the bridge flames; replaced
  by per-node validation.
* Firing modes as the first answer to a death in the climb: 29 lag frames; now the last resort.
* Barrier capsule of screen 2 (rises at X 80 from the bottom of the bridge screen): not collected - on this route
  Bill is on the right side of the bridge when it comes up; not needed with validation.
* Dragon: arms first (above); killing from under the mouth (X 123, 17-19 hits per jump but the centre fireball
  and the arm bullets kill every second jump there); a generic hill climb on the fight schedule (never killed in
  the first window). What worked was the jump-by-jump greedy scored by damage per row at X 116.
* Row -77 was unreachable at one timing (a diver's mortar shell lands on row -73 two frames after Bill): fixed by
  requiring 8 safe frames after every landing.

## 9. Floors and remaining ideas

* Climb on the model alone (no enemies, no flames, rocks ignored): start -> row -50 in 931 frames after the
  landing (ours 1,008), row -56 -> -81 in 386 (ours 389), row -86 -> -108 in 287 (ours 287). Known slack:
  **the bridge about 80-100 frames** (66-frame wait under it so that Bill lands right of the left-going flame;
  hopping that flame from the bridge is coded - `bridge_hops` - but produced no surviving proposal),
  **rock 3 about 60 frames** (1,527 -> 1,690 for 80 px: 48 frames riding it to the right before the jump),
  the first four floors about 30 (32-px steps with Bill at the bottom of the screen).
* Boss: 700-707 rows from scroll start to the first opening (8-frame rule); the kill took 105-126 rows against a floor
  of 32 + lag; firing only near the top of the jumps (fewer stray pellets holding slots) might save 20-40.
* Killing both arms would cut the closed gap from 222 to 62 frames, but the first window is now enough.

## 10. Second pass (2026-10-12) - what was tried, what it measured, what was kept

Same debug start states as section 1. Files added: `contra/stages/s3s8_fight.py` (beam + polish, shared with
stage 8), `tools/s3_bridge_trace.py`, `tools/s3_bridge_grid.py`, `tools/s3_mouth_dev.py`, `tools/s3_polish_dev.py`,
`tools/s3_arms_probe.py`, `tools/s8_verify_p2.py`; the first builder's modules are kept as `*.py.backup_pass1`.

### 10.1 Result

| state | first pass | second pass | top floor | boss scroll | mouth open | dragon dead (after the opening) | lag (level) |
|---|---|---|---|---|---|---|---|
| `dbg/s3_pre` | 3,540 | **3,521** (`logs/s3/p2_v1.*`) | 1,973 (1,977) | 1,992 (1,995) | 2,694 (2,702) | 2,806 = +112 (was +125) | 35 (19) |
| `s3/var1_pre` | 3,526 | **3,513** (`logs/s3/p2_var1.*`) | 1,964 (1,961) | 1,982 (1,981) | 2,688 (2,688) | 2,798 = +110 (was +126) | 35 (19) |
| `s3/var37_pre` | 3,497 | **3,494** (`logs/s3/p2_var37.*`) | 1,939 (1,951) | 1,959 (1,971) | 2,661 (2,677) | 2,782 = +121 (was +105) | 42 (26) |

Record 3,934. All three: no death, weapon out `$13`, 0 rule violations, `check_inputs.py` PASS, and an open-loop
replay on a fresh emulator (`tools/s8_verify_p2.py`) reaches stage 4's first frame on the expected row.
The gain is small and uneven (-19 / -13 / -3) because the dragon fight is luck-dependent (see 10.4): var37 gained
16 rows at the mouth's opening and lost 16 in the fight against the first pass's lucky +105. The var37 result
is the boss part run a second time on the same climb (`--reuse-climb`) after two fixes; the first complete run
of that state gave 3,532, worse than the first pass (kept as `logs/s3/p2_var37_first.*`).

### 10.2 The climb is gated three times (measured)

* **Bridge flames.** Both flames are created on the row the scroll passes A = 595 (row 654 in v3), at X 176 going
  left and X 80 going right, 0.5 px/frame: X = 176 - t/2 and 80 + t/2, they cross at t = 96 and turn at t = 208
  (X 72 / 184). Nothing else drives them (no timer: position only), so the phase at Bill's arrival is fixed by
  the route: he stands on row -34 at t = 67 and could land on the bridge at t = 113 (X <= 105; the floor below
  ends at X 63). The left-going flame is within 12 px of that landing spot from about t = 124 to t = 175:
  `tools/s3_bridge_grid.py` (v3's own two jumps replayed with the wait changed): every wait from 44 to 64 frames
  dies 3 frames before the landing; 66 is the first that lives. Landing before the flame (no wait) works - the
  first pass already had that node (X 103 at row 769) - but Bill is then on the left of a flame that walks toward
  him, and the only way past it is a full jump on the bridge. **Hopping the flame does not pay (an argument from
  the measured positions, not played in the emulator):** a jump from the bridge (standing Y 93) scrolls the
  screen about 46 px, Bill then stands at about Y 139, and a 64-px skip needs a take-off between Y 80 and 103.
  Without the skip the way on is +32, +32, +32 (rows -39, -41, -43, 47 rows each): row -43 at about 969 against
  968 with the wait. So the 66-frame wait is the price of the skip to row -41, not a search failure. The first
  pass's `bridge_hops` never ran a trial: the planner proposes no same-row landings.
* **What was gained there:** the wait rounds stepped by 6 frames; with every frame tried around the first waits
  that live (`bridge_extra`), row -41 came at 901 instead of 921 in the dbg state (var1 already had 902, var37 891).
* **Rows -73 -> -77**: row -77 was reached on row 1,432 in both dbg runs although row -73 came 10 rows sooner in
  the second: whatever blocks that skip (the first pass names a diver's mortar shell) absorbed the bridge gain.
* **Rock 3** (X between 112 and 192, 0.75 px/frame, created when the scroll passes A = 1,320, so its phase follows
  the route as well): Bill lands on it while it moves left (it turns about 35 rows later); a jump to row -86
  (X >= 192) needs the rock's centre at about 133 or more, i.e. about 28 rows after the turn. dbg: landing 1,575,
  turn 1,611, earliest take-off about 1,639, row -86 at about 1,683 at best; first pass 1,690, now 1,686
  (`refine_waits`: a node found through a wait round is retried with the wait shortened by 1..15 frames). To catch
  the rock on its previous pass Bill would have to be about 40 rows earlier.
* After rock 3 the climb equals the model's floor (287 rows), so **only rows saved at rock 3 or later reach the
  top**; they are worth 8 each time they cross the dragon's 8-frame boundary (dbg: 3 rows -> 8; var37: 12 rows ->
  16; var1: 1 row lost, same boundary).
* Neither the flames nor the rocks have a timer: both move between two bounds from their spawn frame on, and the
  spawn frame is the row the scroll passes a fixed height. "Arriving on a better phase" therefore means reaching
  that height sooner or later, and the stretch between spawn and use is at the model's floor already.

### 10.3 Kept in the solver

* `s3_climb.bridge_extra`: single-frame waits around the first surviving arrivals.
* `s3_climb.refine_waits`: shorter waits for nodes that came out of a wait round (rows -86, -93, ...).
* `s3.solve`: the trigger jump is tried from each of the six earliest top-floor nodes and the one whose boss scroll
  starts first is taken (a node standing higher on the screen can beat one that is a row earlier).
* `s3_boss.polish_mouth`: hill climbing on the finished dragon fight, seeded with the greedy's own overrides
  (480 trials: single presses left out, jumps moved by 1-4 rows, 2-6 row steps left / right; cost = kill row, ties
  by HP summed over the rows). Measured: v3's fight 125 -> 109 / 110 rows after the opening; other seeds 114 ->
  111 / 112, 142 -> 121 (the last after an "escape" segment, whose overrides are now part of the seed).
* `s3_boss` exit: when Bill is in the air on the kill row, the walk to the exit spot starts on the landing row (a
  direction held in the air stays latched; that had cost 15 rows in one run).
* `--reuse-climb` (development): only the boss part again for an existing `<out>_climb_end` state.

### 10.4 The dragon - measured, and what did not work

* **Arms and the mouth's timer** (`tools/s3_arms_probe.py`, DEBUG: the destroyed-arms counter `$85` poked to 0 / 1 /
  2 from the end of the scroll, Bill kept alive by a poke; the arms themselves were NOT shot): first opening
  702 rows after the scroll start in all three cases; open 112; closed 222 / 142 / 62 frames. So destroyed arms
  cannot bring the first opening forward; they only shorten the later gaps (the wiki's "cycles faster"), which the
  run never reaches. Whether really destroying an arm does anything the counter does not was not measured.
* **Why 32 HP take 105-125 rows.** Bullet box of the mouth: code 3 around (128, 63) = X 112..145, Y 47..80. The
  jump peaks at Y 137, the upward muzzle is then at Y 121: 41 px below the box (12 frames of flight), 89 px from
  the floor (25 frames). The spread is +-11 and +-22 degrees: all five pellets fit only from 39 px or less, which
  is never reached; from X 116 (the nearest spot the centre fireball misses) three of five can hit, from X 120-128
  four. With 10 slots, 12-25 frames of flight, 7 frames after a hit and 30-47 for a miss, the fight runs at
  about 0.3 HP per frame, plus 18-26 lag frames. That is the weapon's geometry, not the press cap (the box sizes
  are read from the code tables; the pellet counts per X are computed from them, not counted in the emulator).
* **Boss beam on the mouth (`s3_boss.beam_mouth`, off by default): failed.** From X 122, W 8: 10 hits 62 rows after
  the opening, then every lineage died under the centre fireball; from X 116: 12 hits after 65 rows; with a charge
  for busy slots in the ranking it stopped firing. The greedy (20 hits after 69 rows) is better. The ranking
  counts a pellet predicted to hit as a hit whatever its flight time, which works at the stage 8 wall and not
  here, where waiting for the top of the jump is the point; and firing before the opening makes lag, which moves
  the opening.
* The fight is luck-dependent: arm bullets and soldiers kill different jumps at different timings (var37: every
  second-jump candidate died, an escape cost 73 rows before the polish). Several seeds (different first jumps,
  each polished) would cost about 5 minutes each; not done.

### 10.5 What is left (estimates)

* Dragon: 5-15 rows per start state by polishing more than one seed; a ranking that discounts long flights
  might make the beam work.
* Rock 3: about 3 rows (1,686 against a bound of about 1,683 in dbg), worth 8 only when it crosses a boundary.
* The climb search moves the top floor by +-4 rows between runs of the same state (order of the trials); var1
  lost 3 rows that way.
* Solve time: 15-17 minutes on 3 emulators (was 10-11); the polish is 5 of them.

### 10.6 The `--prior` path, replays, files

* `--prior` exercised for the first time with a non-empty history (`logs/s8/p2/prior_test.inputs.txt`, 12 rows
  ending with Right + Up held and a B press on its first frame): `python -m contra.stages.s3 dbg/s3_pre --prior
  ...` -> 3,517 rows (`logs/s3/p2_prior.*`; top floor 1,973, mouth 2,694, dragon dead 2,805 = +111), 0 violations
  counted with the history, history + segment passes `check_inputs.py`
  (`logs/s3/p2_prior.withprior.inputs.txt`), replayed on a fresh emulator. This is also the only complete run
  of the dbg state with the final code; it differs from `p2_v1` (3,521) only in the dragon fight and the exit.
* `logs/s3/best.*` and `states/s3/best_climb_end`, `best_next_pre` are now the second pass's `p2_v1` (3,521); the
  first pass's are `best_pass1.*` / `*_pass1.State`. `states/s3/best_mouth_minus70` still belongs to the first pass
  (the second pass's is `states/s3/s3_p2_v1_m70`).
* Order of the runs behind the table in 10.1: dbg and var1 were solved before the escape-seed and exit fixes of
  10.3; var37's boss part was run again after them. dbg and var1 used no escape. Their exits took 715 rows from
  the boss flag; the `--prior` run above, made with the final code, took 712, so those two would probably come
  out about 3 rows shorter with the final code. They were not run again.
