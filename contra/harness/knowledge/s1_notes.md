# Stage 1 (Jungle) - builder's notes

Stage 1/5 builder, 2026-10-11. Emulator: BizHawk 2.11.1 / NesHawk. "measured" = seen in the emulator;
"code" = read in the disassembly notes; "assumed" = not checked.
t = frames after stage 1's first frame L (first frame with `$2C == 4`; the medals are seen on L + 1).

## Result

| start condition | L (frame) | `$1A` / `$34` at L | stage 1 (L to stage 2's first frame) | record | weapon out | verified |
|---|---|---|---|---|---|---|
| title_wait 0 | 591 | 62 / 187 | **3903** | 3907 | $13 | `assemble.py`: two fresh-launch replays MATCH; check_inputs PASS |
| title_wait 1 | 591 | 62 / 111 | 3904 | | $13 | replay after a core reboot (`tools/s1_finish.py w1`); check_inputs PASS |
| title_wait 37 | 627 | 98 / 142 | **3901** | | $13 | `assemble.py`: two fresh-launch replays MATCH; check_inputs PASS |

All three were produced by `python -m contra.stages.s1 s1/pre_w<k> w<k> --open logs/s1/open_w<k>.inputs.txt`
with no hand edits: no death, no lag frame in play, 16 lag frames while stage 2 loads (fixed). Spread 3 frames.

Files of the run to hand on (title_wait 0):
- `logs/s1/s1_w0_full.inputs.txt` - 4,493 rows from power-on to stage 2's first frame, in the harness's
  convention (row k = frame k+1 of a fresh launch). `python assemble.py x logs/s1/s1_w0_full.inputs.txt` replays it:
  stage 1 first frame 591, stage 2 first frame **4494**, weapon $13, 3 lives, `$1A` = 109, `$34` = 43 there.
- `logs/s1/w0.seg.json` (= `w0_3903.seg.json`): the stage segment alone (3,904 rows; row 1 = frame L).
- `states/s1/s2_start_legal.State` (stage 2's first frame, frame 4494), `s2_pre_legal.State` (one frame before),
  `s1_first.State` (L), `s1_boss.State` (auto-scroll starts), `s1_kill.State` (core HP 0),
  `pre_w0 / pre_w1 / pre_w37.State` (one frame before L for each title_wait).
- Same for the other two: `logs/s1/s1_w1_full.inputs.txt`, `s1_w37_full.inputs.txt`, `w1.seg.json`, `w37.seg.json`.
- First completion, kept: `w0_first_legal_3937.seg.json`.

**A trap found on the way:** `tools/s1_open.py` / `s1_finish.py` record after a core reboot (bridge `reset`), where
the first row is frame 1; a fresh launch gives the bridge control only after frame 1. So
`open_w<k>.inputs.txt` (590 rows, first row empty) is the reboot version and `open_w<k>_poweron.inputs.txt`
(589 rows) the fresh-launch version; both reach the same state (same `$1A`, `$34`, same end of stage 1).
Feeding the reboot version to `assemble.py` shifts everything by one frame and the run dies - seen once.

## Opening (measured)
- Fresh launch: frames 2-10 nothing, `Select` on frames 11-12, `Start` on 12-13 (both held 2 frames: legal),
  then nothing. Stage 1's first frame is 591, `$1A` = 62.
- 1-player mode and no Konami code, read from RAM at L: `$22` = 0, `$1D` = 1, `$24` = 0, `$3F` = 0, 2 spare lives.
- Three press patterns (Select+Start overlapping; Start, 3 off, Start; Select then Start) all give L = 591: the
  jingle timer (328 frames from the first press) decides.
- **`title_wait` moves L in steps of 2.** The jingle timer counts on even `$1A` only: title_wait 1 gives the same
  L and `$1A` as 0 but another `$34`; title_wait 37 gives L = 627, `$1A` = 98 (+36). An odd wait only re-rolls
  the luck; the global timer can be shifted by even amounts only (unless a lag frame or pause changes parity).

## Timeline (title_wait 0) against the record
Record values = video frames after the medals x 60.0988/60; the video shows an event one frame after RAM, like
our "seen" frame, so they compare directly with t.

| event | ours (t) | record | note |
|---|---|---|---|
| M picked up | 314 | 310 | not needed (see Weapons) |
| S picked up | 1436 | 1598 | ours: straight-down shot in the jump onto the top ledge |
| S + Rapid ($13) | 2870 | 2661 | ours: item collected in a jump that is needed anyway |
| boss auto-scroll starts | 3075 | - | zero-loss would be 3057; 17 route frames + 1 |
| core created / HP 0 | 3091 / **3199** | first explosion seen 3203 (lethal hit about 3201-3202) | 124 frames after the auto-scroll starts |
| control lost (`$2C` = 9) | 3363 | scripted jump seen at 3400 = `$2C` 9 at about 3366 | H + 164, fixed. The video shows the script 33-34 frames after `$2C` = 9 (its 32-frame delay) |
| Bill hidden (`$3B` = 2) | 3500 | - | 137 after control is lost (ledge trick; 141 from the ground) |
| level byte changes | 3660 | black at 3663 | 160-frame delay, fixed |
| stage 2's first frame | **3903** | 3907 | 243 frames, fixed (16 lag) |

So: about 3 frames gained at the core's death, 1-2 at the exit.

## The stage in numbers (measured)
- Scroll needed to start the boss auto-scroll: 2976 px. Bill spawns at X 48 and a direction first acts on t = 2,
  so with no loss the auto-scroll would start at t = 3057.
- Every jump costs 1 frame (the A frame has no X movement). **Every landing after walking off a ledge costs 1
  frame too** (no progress on the landing frame; seen in the fitted TAS and in all our runs). This contradicts
  code_player_mechanics.md ("walking off a ledge is free") and agrees with the SDA page. Landing from a jump is free.
- Route = the 1-player TAS's (movie 4623M, read with `tools/s1_trace_ref.py`): 14 jumps + 3 ledge landings before
  the boss. Jump positions as world X (screen*256 + scroll + x): 743, 802 (bridge 1), 1049, 1108 (bridge 2),
  1439 (up to the top ledge), 2032, 2271, 2365, 2431, 2500, 2557, 2782, 2894, 2966. The TAS's 15th jump (3052, on
  the flat ledge before the boss) is not needed.
- Collision map: `logs/s1/map_s1.txt` (16-px cells; standing Y = cell top - 12).
- The NesHawk controller glitch: the game ignored the pad on 21 (w0) / 13 (w37) play frames; every press is
  held 2 frames and the policy is closed-loop, so nothing was lost to it.

## Weapons (measured)
| item | carrier | what the solver does |
|---|---|---|
| M | pill box, screen 0 | opened by a down-right volley at the sniper below it; the item pops up into Bill's path: picked up at t = 314, no detour. Harmless (replaced by S) |
| R | capsule, screen 0 | shot, item left behind (S would clear it anyway) |
| **S** | capsule, screen 4: created at scroll 4.96, moves +0.5 px/f on a scrolling screen, sine of about +-30 px in Y | it is under Bill during the jump at world X 1439: one straight-down volley (free: in the air the direction persists without Right) and the item spawns inside pickup reach. **S at t = 1436, 0 frames lost** |
| F | pill box, screen 5 | never opened: before every volley the aim logic projects the five pellets (and the capsule's motion) and refuses an aim that would hit an M / F / L carrier |
| S | pill box, screen 8 | not needed |
| **R** | capsule, screen 9 (created at scroll 9.16) | hovers within 30 px of Bill around world X 2640-2720. One planned up-right volley, chosen by simulating every row / aim whose fan covers the capsule on the recorded pass and keeping the one after which the item is collected soonest: shot at about t = 2700-2717, item caught on the way without an extra jump. **$13 at t = 2870 (2869 and 2915 for title_wait 1 and 37), 0 frames lost** (all three runs reach world X 3090 on the same row, 3061) |
| L | capsule, screen 9 (flies low, Y 145-205) | not shot while it is ahead of Bill; if it is behind him by 24 px or more a straight-down volley in a jump may kill it (the item then falls behind and cannot be reached). When its item ends up in the path anyway the repair search jumps it (cost 2 frames; did not happen in the three final runs) |
- `$AA`: $00 -> $01 (M) -> $03 (S) -> $13. Order matters as the brief says (S, then R).
- **The record's M and its first R are habit, not speed.** M costs nothing and gives nothing (replaced 1,100
  frames later; the default gun at 12 presses/s is at least as good before that); the screen-0 R is cleared by
  S. The record's fourth pickup is the screen-9 R (the only way to $13 without the base's red soldier).

## Boss wall (measured, `tools/s1_boss.py`, `tools/s1_bombs.py`)
- Core = enemy type $11, 32 HP, created 16 frames after the auto-scroll starts at screen X 240, slides to X 161,
  Y 176; bullet box +-11 px. Vulnerable from creation (hits registered while it slides in).
- Point blank = prone at the right end of the ledge at Y 164 (screen X 96..127): 5 pellets on 5 consecutive
  frames. From X 118 on that ledge only about half the pellets connect. From the ground at the wall (X 136)
  up-right volleys also connect point blank.
- Hazards: two bomb turrets (type $10, 16 HP, Y 128; first bomb 32 frames after each is created, then every 40:
  bombs at auto-scroll + 40, 64, 80, 104, 120), the sniper on the wall (type $06), the rotating gun on the ground
  at world X 3120 (type $04, usually alive with 5-6 HP).
- **Bombs** are enemy bullets with collision code 5: launched at Y 128 with (vx, vy) = (-0.64, -0.38),
  (-1.08, -0.62) or (-1.61, -0.94) px/f (three of the four speeds chosen by `$34 & 3` were seen; which value
  gives which was not checked), gravity 1/16 px/f^2, plus -1 px/f while the screen scrolls. The first bomb crosses the middle step (the ledge at
  Y 132) 26-33 frames after its launch - exactly when Bill walks down the two steps. A slow bomb lands on the
  prone spot about 45 frames after its launch.
- What works: **jump from the top ledge (Y 100) at world X 3113-3125 straight down onto the Y 164 ledge**
  (72 frames in the air, above the bombs, landing at the ledge's right end as the scroll ends; 1 frame for the
  jump instead of 2 for the two ledge landings), then the beam search over 5-frame steps (run / prone / jump,
  aim per volley), scored by core HP minus volleys on their way, plus a penalty for a bomb whose path ends on
  the firing spot (that makes the search prefer a firing phase with a harmless bomb speed). Six variants
  (jump position, firing phase, width) run on the three emulators; kill rows for title_wait 1 and 37:
  3198-3210, best 3198-3201. (The title_wait 0 run was made one version earlier with three variants - the two
  steps, jump at 3121, jump at 3125: kill rows 3233, 3200, 3207 - and was not re-run, so that the hand-over
  states stay those of the delivered input list.)
- What failed: walking down the two steps. With the same search the core died at t = 3229-3233 (the search
  keeps falling back from dead ends) - 30 frames slower, in every try.
- After the core's last hit H: `$3B` = 1 on H + 1, control lost on H + 164 (measured in every run).

## Exit (measured)
- The script waits 32 frames after control is lost, walks right to X >= $90, jumps (1 frame without X
  movement), walks until hidden at X >= $F8.
- From the ground at the wall (X 136-144): hidden 141 frames after control is lost.
- **Ledge trick: 137 frames.** Stand at the right end of the Y 164 ledge (X 127) and press Right 1-6 frames
  before control is lost: Bill is falling off the ledge when the script starts (a ledge fall is not a jump, so
  the script does not wait for a landing) and drifts right during the 32-frame wait. All of d = 1..6 gave the
  same 137. If the fight ends on the ground the solver walks back under the ledge and jumps up through it first.
- Jumping before control is lost, or stopping elsewhere: 141 or worse (searched: 80 variants).
- From hidden to stage 2's first frame: 403 frames (160-frame delay, then the load and score screen).

## How the solver works (`contra/stages/s1.py`)
1. Run phase (L -> world X 3090): `Route` (jump positions) + legal fire cadence (press 2 frames, release 3) +
   auto-aim, under `Repair` (see s5_notes.md). Deadlines: S by world X 1560, $13 by 3080 - a missed deadline is a
   failure like a death. In the three final runs the run phase needed 1-2 repairs (a death near world X 2725
   fixed by holding fire for 10 frames; the planned R shot).
2. Boss: six beam-search variants in parallel, best kept.
3. Exit: small search (ground / ledge with d / jump with d / stop at X), best kept; then empty rows.
Time per solve: 9-10 minutes on 3 emulators.

## What was tried and failed
- A cautious "do not fire near a capsule" rule: firing was blocked for about 100 frames while both screen-9
  capsules hover near Bill, and the red turret at world X 2768 killed him. Replaced by the pellet-path test.
- "Shoot the R capsule as soon as possible from row r": the item is then rarely on the path. Replaced by the
  single planned volley.
- Repair that demanded survival for 110 frames after any fix: one unplanned jump made later planned jumps
  misfit and every candidate "failed"; it then chose 48-frame stops. Replaced by "reach a point 110 px further
  soonest", plus the local beam search.
- A press tracker that allowed a new press only 6 frames after the last (off by one): the first runs fired at
  10 presses/s. Fixed; `Pad` is unit-tested against `check_inputs.check`.
- Boss approach by the two steps (above). Boss search without the bomb penalty: many dead ends, up to 7 minutes.

## Theoretical floor and what stands in the way
| part | ours | floor | what is in between |
|---|---|---|---|
| L -> auto-scroll | 3075 | 3057 + jumps and ledge landings the terrain forces (17 on this route) | whether a route with fewer than 17 exists was not searched; 1 more frame is lost somewhere before the boss (not located) |
| auto-scroll -> core HP 0 | 124 | 16 + 32 = 48 if every frame from its creation scored (impossible: range) | Bill reaches point blank about 88 frames in; before that only 3-4 pellets of the volleys fired in the jump can connect; at point blank the cap gives 0.93 HP/frame; bombs force moves |
| core HP 0 -> stage 2 | 704 | 704 | fixed, with the ledge trick |

Top ideas: more hits before the landing or a cleaner 35 frames on the ledge (5-10 frames); route with fewer
jumps (0-3, unknown); the stray frame (1).

---

# Second pass (2026-10-11 / 12, second-pass optimiser)

Same conventions as above. The first-pass solver is kept as `contra/stages/s1.py.backup_v1`, these notes' first-pass
version as `knowledge/s1_notes.md.backup_v1`.

## Result: no real gain in stage 1

| start condition | first pass | second pass | record | verified |
|---|---|---|---|---|
| title_wait 0 | 3903 | **3900** | 3907 | `assemble.py`: two fresh-launch replays MATCH (RAM sha1 0d961bbe5a7d, trace 0d2109b89eeb); check_inputs PASS |
| title_wait 1 | 3904 | 3904 | | `assemble.py` MATCH (a928a7d812fc / 57f7dd9e04fe); check_inputs PASS |
| title_wait 37 | 3901 | 3901 | | `assemble.py` MATCH (d9c2c48a8ff6 / d7f66466a209); check_inputs PASS |

The 3 frames of title_wait 0 are NOT a second-pass improvement: they come from the boss variant (width 8, delay 3,
jump 3113) that the first pass's final solver already had - its title_wait 0 run had been made one solver version
earlier and not re-run. Everything tried in this pass for stage 1 (below) either did not pay or cost too much
solve time; the only solver change left in is one boss variant swapped ((8, 0, 3125), which never won, for
(8, 1, 3113)). No death, no lag frame in play, weapon out $13 in all three.

New files (the first pass's `s2_start_legal`, `s1_w0_full.inputs.txt` etc. are untouched):
- `logs/s1/w0v2.seg.json`, `w1v2.seg.json`, `w37v2.seg.json` (stage segments), `solve_w<k>v2.log`
- `logs/s1/s1_w0v2_full.inputs.txt` (4,490 rows, power-on to stage 2's first frame = frame **4491**; `$1A` 106,
  `$34` 234 there), `s1_w1v2_full.inputs.txt` (4,494; frame 4495), `s1_w37v2_full.inputs.txt` (4,527; frame 4528),
  each with `.report.json`; `logs/s1_w<k>v2_asm.report.json` = the assemble.py reports
- `states/s1/s2_start_legal_v2.State` (stage 2's first frame of the title_wait 0 run), `s2_pre_legal_v2.State`
  (one frame before), `s1_boss_v2.State`, `s1_kill_v2.State` (`tools/s1b_states.py w0v2 v2`)
Solve time unchanged (9-10 minutes).
Which solver version made what: the three v2 segments were solved with the variant list (8,3,3113), (8,0,3113),
(8,0,3109), (8,1,3109), (8,0,3121), (8,1,3113); the final list replaces the two 3109 variants (time limit in the
title_wait 1 solve) by the first pass's (8,2,3117) and (10,0,3121). The final solver was re-run for title_wait 0
(`logs/s1/w0v2c.seg.json`): rows identical to `w0v2`. For title_wait 1 and 37 it was NOT re-run; that it gives
the same rows is inferred from the per-variant kill rows in the logs (the winning variant (8,3,3113) is first in
both lists and no replacement variant beat it in the first pass's logs).

## Running part: nothing to take (measured, `tools/s5b_loss.py 1 ...`, `tools/s5b_path.py`)
- Frame-by-frame loss of the title_wait 0 run before the boss: exactly 17 frames = 14 jump frames (world X 743, 802,
  1049, 1108, 1439, 2032, 2271, 2365, 2431, 2500, 2557, 2782, 2894, 2966) + 3 ledge landings (1908, 2238, 2676).
  **There is no stray frame**: world X = t + 47 - (frames lost), the scroll reaches 2976 px on t = 3074 and the
  auto-scroll timer `$75` is first non-zero on the next frame, t = 3075. "3057 + 17 + 1" was that one-frame
  convention, not a lost frame.
- A route with fewer than 17 was looked for on the map (by hand, with the measured take-off / landing list of
  `tools/s5b_path.py`; no route search was run in the emulator) and not found. Computed, not measured: the
  bridges need two jumps each (bank0.asm:2264-2399: section k of a bridge loses its floor about 5 + 46k frames
  after Bill comes within 24 px - the code notes call these timings "derived" - so one jump cannot be in the
  air both over section 0 and when section 1 goes). From X 2032 on, every step between the platforms is either
  +32 / +48 px up (a jump) or a drop (a jump or a ledge landing, one frame either way), and the gaps on one
  level are 64 px while a flat jump lands 59 px further (61 at most, computed from the landing rule: the test is
  made at the start of a falling frame). So the fitted TAS's 14 + 3 looks minimal; no proof.

## Boss wall: where the frames are and what was tried
Timeline of the best fight (title_wait 0, kill row 3197; a = frames after the auto-scroll starts;
`tools/s1b_trace.py s1/w0_boss logs/s1/lab_boss_best.json 3061`):

| a | what |
|---|---|
| 0 | auto-scroll starts, Bill at world X 3105 on the top ledge (Y 100) |
| 8 | jump from world X 3113 (72 frames in the air) |
| 16 | core created (world X 3233, Y 176, box +-11), hittable |
| 36, 54, 62 | the only three hits before the landing |
| 81 | lands on the ledge in front of the core at world X 3185 (14 px short of its end), HP 29 |
| 84 | first prone volley (3 frames late: the search's 5-frame steps do not fall on the landing frame) |
| 86-121 | 29 hits in 36 frames (14 per 15 would be 31); walks off the ledge at a = 106 and finishes while falling in front of the core (prone-height and standing-height shots both hit there) |

**Where the pellets of the approach go (computed from the geometry, consistent with the trace).** A down-right
volley in the jump is five pellets at 22.5, 33.75, 45, 56.25 and 67.5 degrees below horizontal from (X + 15,
Y + 15). The line to the core needs 38 degrees 5 frames into the jump, 45 at 10, 53-60 from frame 18 to 59, 51 at
60, 39 at 65, 10 at 70. So for most of the jump exactly ONE pellet of a volley (the 56.25 degree one, pellet 2 or
3 of the five) is on the core, 34-40 frames of flight away, and the other four fly on to the screen edge for
45-60 frames. With 10 slots that is two volleys in flight and then nothing: 2-4 hits whatever is pressed. Only in
the last 12 frames of the jump (2-3 pellets per volley hit, short flight) is a volley efficient, and those pellets
then hold the slots the first prone volleys need. From the top ledge before the jump the 33.75 degree pellet of a
standing down-right volley is on the core from world X 3099 to 3131 (36 frames of flight): that is where the
first hit (a = 36) comes from. No position gives a firing line with more than one pellet on the core before
world X 3185: the core is 12 px lower than the ledge in front of it and every other floor is 32-76 px higher.
- Point blank cannot be reached before a = 81: Bill is at world X 3104 + a at best and needs X >= about 3185.
- Floor for the fight from there: 29 HP at 14 hits per 15 frames = 31 frames, a = 113; we are at 121-125.

Tried (title_wait 0 boss state, `tools/s1b_lab.py`; first-pass search = kill row 3197):
| idea | result |
|---|---|
| scripted fight (`boss_script`: jump at X, stop firing in the air after n frames, prone + step right, walk off after m frames), 240 parameter sets | 31 survive the bombs, best kill row 3201 |
| planned volleys in the jump at the frames the geometry favours (10, 20, 60, 65 and five other sets), search after the landing | 3198-3202 (HP at the landing unchanged: 29-30) |
| earlier jumps (world X 3105, 3109: landing 4-8 frames sooner, further from the ledge's end) | 3198 twice with title_wait 0; None (time limit, 420 s) or 3200 with the others |
| hill climbing on the solved fight's rows (`refine_rows`: every press 1-2 rows earlier / later, a direction held longer / shorter, a B press dropped; 420 changes a pass) | 3197 -> 3196 in 3 minutes, nothing in the second pass; with block shifts (everything after row r 1-3 rows earlier): nothing. Off by default (`solve(refine=0)`) |
The outcome is dominated by the bombs (speed = RNG & 3 at each launch; any change of input changes the RNG): the
kill row of one variant moves by 3-6 frames between start conditions, and local changes of a solved fight mostly
die. A real gain needs a model of the fight (pellets, core, bombs) like the UFO's in stage 5
(`contra/stages/s5_ufo_sim.py`): estimated 3-6 frames (3 lost at the landing, 5 dead frames of the prone phase,
1-3 more hits in the jump's last frames), not done.

## Left on the table (estimates)
| part | ours | floor | note |
|---|---|---|---|
| L -> auto-scroll | 3075 | 3075 | 17 forced frames on this route; no better route found |
| auto-scroll -> core HP 0 | 121-125 | about 113 | see above; 3-6 of it look reachable with a model-based search |
| core HP 0 -> stage 2 | 704 | 704 | fixed (ledge trick included) |


# Rule v2: the press budget (2026-10-12 solves, verified and written up 2026-10-16)

Rule v2 (`project_rules.md`): besides the 5-frame rule, at most 109 new presses of one button in any 600 frames and
246 in any 1,800, across stage boundaries; `check_inputs.py` checks it at its defaults. The second pass's stage 1
mashed B the whole way (633-637 presses, 120 in 600 frames, 360 in 1,800): it broke both limits.
The previous agent's work was stopped on 2026-10-12 before it wrote this section; everything below was re-checked
on 2026-10-16 from the files on disk (solver logs, `logs/s1c_queue.log`, assemble reports, check_inputs re-run).

## Result

| start condition | second pass | rule v2 | change | B presses (old -> new) | most B in any 600 / 1,800 frames (old -> new) | lag frames (old / new) | verified |
|---|---|---|---|---|---|---|---|
| title_wait 0 | 3900 | **3902** | +2 | 633 -> 100 | 120 / 360 -> 50 / 76 | 16 / 16 | `assemble.py` two fresh-launch replays MATCH (RAM sha1 9f2dfe872bfd, trace 548f9294c485); check_inputs PASS at its defaults |
| title_wait 1 | 3904 | **3900** | -4 | 637 -> 91 | 120 / 360 -> 41 / 69 | 16 / 16 | `assemble.py` MATCH (6c4f8fa52ace / 65dbddafb9b8); PASS |
| title_wait 37 | 3901 | **3898** | -3 | 636 -> 95 | 120 / 360 -> 41 / 68 | 16 / 16 | `assemble.py` MATCH (57634ed49d31 / d0d19e13aaba); PASS |

Frames = stage 1's first frame to stage 2's first frame. Stage 2's first frame from power-on: 4493 / 4491 / 4525.
The counts are from power-on (stage 1 is the first stage, so the history is the title screen: no B). Rule v2 costs
nothing measurable here: the run phase reaches the boss on the same row (3061) in all three, with 0 lag frames in
play, and the -4..+2 spread is the boss fight's usual 3-6 frame scatter with the bomb RNG (second-pass section
above), not the budget. The budget never refused a press (`presses refused by the budget 0`, `press plan refused
on 0 rows`): the run phase used 67-75 presses (at most 29-30 in 600 rows) and left 84-90 of room for the core.
Other buttons: Down 61-66 presses (at most 12 in a second), all far inside the windows.
No death, weapon $13 at the hand-over in all three. Spare lives at stage 2: 2 (the second pass had 3; assumed,
not checked: fewer kills, so the score's extra life is not reached in stage 1).

## What changed in the solver (`contra/stages/s1.py`, `s1_common.py`, `s1_engine.py`; before: `*.backup_v2`)
- `s1_common.Pad` carries the press budget (start rows of every button's presses over the last 1,800 rows;
  `Pad(windows=((600, 109), (1800, 246)))` by default). `can_press()` / `legal()` refuse a press that would break a
  window; `rate_ok()` is the 5-frame rule alone; `count()` / `budget_ok()` / `room()` are the planning forms;
  `Pad.from_rows(history[-2000:])` is what a solver is given (12 rows of history are no longer enough).
- `s1_common.Fights`: the press plan (here: 34 presses kept for the core fight from world X `BOSS_FROM`).
- The run phase no longer mashes: it presses B for the two pickups, at an enemy ahead when a volley fired now is
  predicted to hit it and the bullets in flight do not cover its HP (`pick_shot`, `pending_on`), and on rows the
  repair search marked `fire` / `aim`. `s1_engine.Repair(engage=...)` looks ahead before the first shot at each
  enemy (once never firing, once firing; 26-28 verdicts a run, 12-14 of them "pass"). Among repair edits that
  arrive on the same row, the one with fewer B presses wins.
- The core fight is unchanged (fast fire under the hard budget); three more firing-phase boss variants.

## Unit test of the Pad against the checker (`python tools/s1c_padtest.py`; `--quick` for a 2-minute version)
On every row of random and adversarial sequences (fastest mash, mash-then-idle to the exact row a press leaves a
window, 1-frame toggles, random hold / release lengths, presses 4-7 frames apart, random; with rule v2's windows
and with small windows (60, 7), (200, 15) that bind often), each Pad decision - may b be newly pressed now, may a
held b be released now - is compared with `check_inputs.check` at its command-line defaults (read from the
checker's source) on the rows so far plus the candidate row. Result 2026-10-16: **all decisions agree exactly**
(259,241 decisions, 53,606 of them a press refused by a window, 4,614 of those with rule v2's own windows; `logs/s1/padtest_exact.log`), `legal()` returns exactly the row those decisions give, every
sequence passes check_inputs as a whole, a Pad rebuilt from the last rows decides like the original, and a mash
fills the windows exactly (109 / 246).

## Files
- Segments `logs/s1/w0v3.seg.json`, `w1v3.seg.json`, `w37v3.seg.json`; solver logs `solve_w<k>v3.log`.
- From power-on: `logs/s1/s1_w0v3_full.inputs.txt` (4,492 rows; stage 2's first frame = frame 4493, `$1A` 108,
  `$34` 137), `s1_w1v3_full.inputs.txt` (4,490), `s1_w37v3_full.inputs.txt` (4,524); `.check_v2.json`,
  `.report.json`; `logs/s1_w<k>v3_asm.report.json` = the assemble.py reports.
- Hand-over for the next chain: `states/s1/s2_start_legal_v3.State` (stage 2's first frame of the title_wait 0
  run), `s2_pre_legal_v3.State` (one frame before), `s1_boss_v3.State`, `s1_kill_v3.State`.
- The second pass's files (`*v2*`) are untouched.
