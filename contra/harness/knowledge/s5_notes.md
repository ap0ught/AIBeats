# Stage 5 (Snow Field) - builder's notes

Stage 1/5 builder, 2026-10-11. Emulator: BizHawk 2.11.1 / NesHawk. Developed on DEBUG states (stage number and
weapon $13 written into RAM: `states/dbg/s5_pre`, `states/s5/pre_w<k>`), so every number here is a per-stage
fact, not part of a run. t = frames after stage 5's first frame L (first `$2C == 4`).
"measured" = seen in the emulator; "code" = from the disassembly notes; "assumed" = not checked.

## Result

| start state | `$1A` / `$34` at L | stage 5 (L to stage 6's first frame) | record | lag frames in play | UFO X |
|---|---|---|---|---|---|
| `dbg/s5_pre` (= `s5/pre_w0`) | 62 / 224 | **6082** | 6125 | 3 (t = 2066, 2072, 2081) | 128 |
| `s5/pre_w1` (title wait 1) | 62 / 45 | **6081** | | 2 (t = 4276, 4289) | 128 |
| `s5/pre_w37` (title wait 37) | 98 / 4 | **6081** | | 0 | 128 |

All three: solved by `python -m contra.stages.s5 <state> <name>` (final solver version) with no hand edits,
replayed open-loop on a fresh emulator by `tools/s5_finish.py` (same end frame), `check_inputs.py` PASS at its
defaults, weapon $13 at stage 6's first frame, no death. Spread 1 frame. The fitted 30 Hz TAS stage
(reference_run.md) is 6027. Earlier solver versions gave 6135 (first completion), 6092 / 6101 / 6091.
Segments: `logs/s5/d0.seg.json` (= `d0_6082.seg.json`, state `dbg/s5_pre`), `logs/s5/w1.seg.json`,
`logs/s5/w37.seg.json`; `.inputs.txt` and `.report.json` next to them. Kept: `d0_first_legal_6135`, `d0_6092`.
States (from the 6082 run, DEBUG lineage): `states/s5/s5_first` (L), `s5_tank1`, `s5_tank2` (tank created),
`s5_boss` (auto-scroll starts), `s5_ufo` (UFO created), `s6_pre_dbg`, `s6_start_dbg`;
`states/s5/pre_w0 / pre_w1 / pre_w37` are the three debug start states (`tools/s5_mkstates.py`).

## Timeline of the best run from `dbg/s5_pre` (6082) against the record

Record values = video frames after the medals x 60.0988/60 (record_events.json); the video shows an event one
frame after RAM, like ours, so they compare directly with t.

| event | ours (t) | record | note |
|---|---|---|---|
| tank 1 created (scroll reaches screen 9.0) | 2409 | - | zero-loss arrival would be 2385 |
| tank 1 stops / destroyed | 2526 / 2602 | - | 117 to stop, 76 to kill |
| tank 2 created / stops / destroyed | 3425 / 3542 / 3618 | - | 117 / 76 |
| boss auto-scroll starts (5024 px) | 5120 | - | fitted TAS: 5089 |
| UFO created / can be hit | 5215 / 5317 | "appears" about 5328 | fixed: +95, +102 |
| UFO HP 0 | 5398 | body breaks up at about 5491 (lethal hit up to 27 earlier) | 81 frames for 32 HP |
| `$3B` = 1 | 5493 | - | H + 95, fixed |
| control lost (`$2C` = 9) | 5543 | walk seen at 5622 = control lost at about 5589 | H + 145, fixed. The video shows the walk 33 frames after `$2C` = 9 (the script's 32-frame delay) |
| Bill off screen (`$3B` = 2) | 5666 | - | 123 after control is lost, standing at the cap X 160 |
| level byte changes | 5826 | black at about 5798-5810 | 160-frame delay, fixed |
| stage 6's first frame | **6082** | 6125 | 256 frames of load + score screen, fixed |

We are about 46 frames ahead of the record when control is lost and 43 at the end.

## Where the frames are (measured)
- **Running, start to tank 1: 24 frames lost** (2409 against 2385): 17 planned jumps + 1 ledge landing + 3 extra
  jumps and 3 frames inside the two local searches. The planned jumps are the fitted TAS's; several are there
  for grenades and turret-man bullets, not terrain. Not pruned yet.
- **Tanks: 193 frames each from creation to destruction** (117 to the stop, 76 to the kill). Floor under the
  press cap: 97 (drive-in at 1.5 px/f) + 76 (71 HP at 0.93 HP/frame) = 173; the fitted TAS (30 Hz) needs about 170.
- **UFO: 81 frames from "can be hit" to HP 0.** Floor 32.
- Everything after the UFO's last hit is fixed (684 frames) once Bill stands at X 160 in time.

## Mechanics measured here
### Running section
- Hazards are created by scroll position and then run on their own timers, so stopping BEFORE a trigger changes
  nothing; only time spent between a trigger and the hazard shifts the phase.
- First screen: turret man 2 (created at world X 496, 10 HP) fires his first bullet 22 frames after he
  appears; it flies at Y 124 and reaches Bill exactly as he lands from the jump over grenade 2 (t = 384). It
  cannot be prevented under the press cap (4 volleys in 22 frames at 110 px: 4-5 hits). A standing or freshly
  jumping Bill is hit; prone is safe (prone box 4 px tall at foot level) and so is the top of a jump.
  The local beam search's answer costs 2 frames less progress than the best single stop (9 frames faster).
- Trench at world X 576-736 (floor 48 px lower, solid walls): walking into the far wall is a stall, not a death;
  the solver treats 4 frames without progress as a failure ("wall").
- Pill box M on screen 1 (world X 624, Y 160): its item must not be collected (it would replace S and clear
  Rapid). The aim logic refuses volleys whose pellets would open an M / F / L box; when the box is opened anyway
  the repair search jumps the item.
- Walking off a ledge costs one frame at the landing, like in stage 1.
- Lag: 3 lag frames in the w0 run around t = 2066-2081 (screens 7-8: pillars, sniper, pipe-joint sprites), none in
  the other two. Not investigated further; nothing was done to avoid them.

### Tanks (`tools/s5_tank.py`)
- Created when the scroll reaches screen 9.0 / 13.0, at a virtual X of 304 (9 bits: while it is off screen its
  state byte is $85 and the X byte counts down through 0). It drives in by `TANK_AUTO_SCROLL` (`$77`) = 1 px on
  odd frame-counter frames (0.5 px/f) plus the player's own scroll: 1.5 px/f while Bill scrolls at X 128.
  Left alone it needs 290 frames (measured); scrolled all the way it would need 97.
- It stops when its X is below 160 (X 159); HP becomes 71 on that frame and `$77` goes to 0.
- Touching it is death: standing box X +-45; jumping box X +-44 and from Y 108 down (its Y is 144). So Bill
  cannot stay at X 128 once it is nearer than X 173 and has to be at X <= 113 when it stops; only the top ~10
  frames of a jump (Y < 108) are above the box. That is why the drive-in costs about 20 frames more than 97: for
  the last 14 px the tank comes alone at 0.5 px/f while Bill backs off. A jump over those frames does not
  pay: Y < 108 lasts 10 frames and Bill must be 15 px further left when it ends. In the scripted grid (85
  scripts: scroll until row s, optionally jump on row j) the best is no jump, back off from row 88: 193 frames
  in all three start conditions; the best jump script 194; the beam search 197-199.
- Kill: standing at X = tank X - 46 facing it, firing forward: 71 HP in 76 frames (first volley timed to the
  stop). The tank's first bullet comes about 56 frames after it stops and misses Bill at that spot.
- After the kill the wreck keeps the 0.5 px/f auto-scroll until it has left the screen (free scroll).
- "2-frame rule" (TAS notes): the auto-scroll moves only on odd frame-counter frames, so the arrival comes in
  2-frame steps. Seen, not exploited (all three start conditions: stop 117 frames after creation).

### UFO (`tools/s5_ufo.py`)
- Created 95 frames after the auto-scroll starts; X = 64 / 96 / 128 / 128 by `$34 & 3`, set a few frames after
  creation; first appearance at Y 48. Hittable 102 frames after creation (state bit 7 clears), 32 HP, bullet
  box +-17 px. No player collision (state bit 0): jumping into it is safe. Its bombs / small saucers start about
  30 frames after it opens; about 9 in 10 scripted fights survive them.
- **Its X does not matter for the time**: between the kill and the loss of control there are 145 frames, enough
  to walk to X 160 from anywhere. Nothing was done to steer it (X 64 once, X 128 five times in six solves).
- Why it is slow under the cap: from the ground (muzzle Y 137, 72 px under the box) only the centre pellet and
  sometimes the two inner ones hit; the outer pellets fly on to the top of the screen and hold their slots for
  about 30 frames, so later volleys come out with 2-3 pellets. Near the top of a jump (muzzle 25-40 px under
  the box) 3-5 pellets of a volley hit: 0.6-0.7 HP/frame there, 0.2-0.4 elsewhere.
- Search used: scripted grid (stand dx px from its X, fire straight up, jump j frames before it opens and
  again on landing, press phase, optionally fire only when close): best 80-83 frames from opening to HP 0 in all
  three runs (dx 0..-8, j 18-26). Firing only when close gained 2 frames. The beam search needed 93.
- After the last hit H: `$3B` = 1 on H + 95, control lost on H + 145 (measured in all runs).

### Exit
- Cap X 160 on the boss screen. Standing there when control is lost: off screen 123 frames later. Jumping
  before the loss of control or stopping short is slower by 1-4 frames (searched: 21 variants).

## How the solver works (`contra/stages/s5.py`)
1. Run phases (start -> tank 1 -> tank 2 -> boss): `Route` of jump positions in world X + legal fire cadence
   (press 2 frames, release 3) + auto-aim (forward / up-right / down-right at the nearest target, never through
   an M / F / L pill box) under `Repair`: on a death / pit / wall / wrong weapon it goes back and looks for the
   change that gets Bill 110 px past the failure point soonest: single free edits (aim, hold fire, move or drop
   a planned jump), one extra jump, a short stop, or a local beam search over run / jump / duck / wait.
2. Tanks: the scripted grid (85 scripts on 3 emulators, 40 s); beam search over 5-frame steps as a fallback.
3. UFO: the scripted grid above (280 scripts, 3 minutes; beam search as a fallback).
4. Exit: a small search over where to stand / jump when control is lost; then empty rows to stage 6's first frame.
Time per solve: 13-14 minutes on 3 emulators.

## What was tried and failed / was not done
- Repair with single edits only: no single change gets past the first screen's grenade + bullet combination
  (every candidate died at the same world X). The local beam search fixed that.
- Tank beam with 3-frame steps and tank-distance scoring: worse (203 frames). Tank beam with 5-frame steps:
  197-199. The "jump toward the tank and pull back" of the TAS notes: 1 frame slower than no jump under our cap.
- UFO beam search: 93 frames (myopic: it prefers certain hits from the ground to the jump).
- NOT done: pruning the planned jumps; the 2-frame rule; steering the UFO's X; avoiding the 2-3 lag frames;
  pauses (none used).

## Theoretical floor and what stands in the way
| part | ours | floor | what is in between |
|---|---|---|---|
| start -> tank 1 created | 2409 | 2385 + needed jumps (about 12-18) | which of the 17 jumps are needed is unknown; hazards force some |
| each tank | 193 | 173 (cap) / 168 (30 Hz) | backing off for the last 14 px (20 frames): the tank is a lethal wall 45 px wide on each side |
| tank 2 dead -> auto-scroll | 1502 | about 1490 | 9 planned jumps + 1 repair jump |
| UFO | 81 | 32 | reach: Bill cannot get closer than 25 px under its box, and only for about 16 frames per jump |
| after the UFO | 684 | 684 | fixed |

Top ideas, with estimates: jump pruning in the running sections (5-10), UFO with a better jump schedule or
diagonal volleys from the side (10-20, uncertain), a way to keep scrolling during a tank's last 14 px (up to
2 x 18, none found), lag (2-3).

---

# Second pass (2026-10-11 / 12, second-pass optimiser)

Same conventions as above ("measured" = seen in the emulator, "code" = read in `dl/nes-contra-us`, "model" =
computed by the offline model, "assumed" = not checked). Still DEBUG start states: nothing here is part of a run.
The first-pass solver is kept as `contra/stages/s5.py.backup_v1`.

## Result

| start state | first pass | second pass | record | lag frames in play | UFO: hittable to HP 0 |
|---|---|---|---|---|---|
| `dbg/s5_pre` | 6082 | **6040** | 6125 | 0 | 65 frames (first pass 81) |
| `s5/pre_w1` | 6081 | **6041** | | 0 | 66 (81) |
| `s5/pre_w37` | 6081 | **6041** | | 0 | 66 (83) |

All three: `python -m contra.stages.s5 <state> <name>` with no hand edits, then replayed open-loop on a fresh
emulator by `tools/s5_finish.py <state> <name>` (same end frame, no death, weapon $13 at stage 6's first frame),
`check_inputs.py` PASS at its defaults. Segments: `logs/s5/d0v5.seg.json`, `w1v5.seg.json`, `w37v5.seg.json`
(+ `.inputs.txt`, `.report.json`); solver logs `logs/s5/solve_<name>.log`; states `states/s5/<name>_tank1`,
`_tank2`, `_boss`, `_ufo` (tank / auto-scroll / UFO creation frames). The first pass's files and states were
not touched (`tools/s5_finish.py` was run WITHOUT `--keep`, so `s6_start_dbg` etc. are still the first pass's).
Solve time: about 12 minutes on 3 emulators with the machine shared (was 13-14): run phases 7.5, tanks 2 x 1.2, UFO 1.5, exit 0.5.

Timeline of `d0v5` (t = frames after stage 5's first frame; first pass in brackets):

| event | t |
|---|---|
| tank 1 created / stops / HP 0 | 2406 / 2519 / 2594 (2409 / 2526 / 2602) |
| tank 2 created / stops / HP 0 | 3410 / 3523 / 3598 (3425 / 3542 / 3618) |
| boss auto-scroll starts | 5094 (5120) |
| UFO created / can be hit / HP 0 | 5189 / 5291 / 5356 (5215 / 5317 / 5398) |
| control lost / Bill off screen | 5501 / 5624 (5543 / 5666) |
| stage 6's first frame | **6040** (6082) |

## What each change gained (measured on `dbg/s5_pre`, frames at stage 6's first frame)

| change | gain |
|---|---|
| tanks: first volley on the stop frame, drive-in jump, kill jump | 23 (at the auto-scroll start: 5120 -> 5097) |
| UFO: slot-aware script (first step) | 8 (81 -> 73 frames from "can be hit" to HP 0) |
| UFO: offline model + planner + emulator hill climbing | 7-8 more (73 -> 65-66) |
| lag: hold-fire stretch found by the repair search | 3 (the three lag frames at t = 2066-2081) |
| leaving the last ledge before each tank by a jump instead of walking off, for a longer window (below) | -5 (6045): off by default | |

## Tanks

### What decides the stop (code: `tank_routine_01`, `tank_update_pos`, bank0.asm:6291-6388; measured)
- The tank is background tiles; its X (9 bits, starts at 304) drops every frame by `FRAME_SCROLL` (1 while Bill
  scrolls at X 128) plus `TANK_AUTO_SCROLL` (= frame counter & 1). It stops on the first frame its X is below
  160 (X 159 when the last pixels are not helped by Bill's scroll); on THAT frame `tank_stop` sets HP 71, and the
  bullet test of the same frame already counts (the enemy's routine runs before its collision tests), so a
  pellet inside its box on the stop frame scores. The first pass's first hit was one frame late (muzzle one
  pixel outside the box).
- `TANK_AUTO_SCROLL` scrolls the level without pushing Bill back (only the boss auto-scroll does that,
  bank7.asm:4278). So what counts for the stage's time is how many frames Bill is NOT scrolling: during the
  drive-in every such frame costs 2/3 of a frame, during the fight (tank stopped, no auto-scroll) a whole frame,
  after the kill (the wreck auto-scrolls until it has left the screen, 207 px) 2/3 again.
- Boxes of the tank (enemy Y 144, collision code 9; code: `collision_box_codes_01..04`, bank7.asm:7270-7342):
  standing Bill is hit at X >= tank X - 44, Y 101..191; **jumping Bill at X >= tank X - 44 only while his Y is
  108..177**; prone: X >= tank X - 51, Y 104..165 (Bill's Y is 164: prone is no way out, by 2 px). Bullets: X
  tank X - 43.. +42, Y 113..180. So Bill may stand at X <= 114 (tank at 159) and his muzzle (X + 16) is inside
  the bullet box from X 101 on: the fight is point blank anywhere in X 101..114.
- The player collision of the kill frame is still tested (it runs before the bullet test); from the next frame
  on the wreck is harmless.

### Hit rate (measured; it is exactly the slot arithmetic)
Point blank a pellet scores on the frame it is created or the next ones (one per frame, highest slot first) and
its slot is free 7 frames after its hit. With a press every 5 frames the volleys come out 5, 5, 4 pellets:
**14 hits per 15 frames, 71 HP in 76 frames counted from the first hit** - that is the floor under the cap, and
both passes are on it (first hit on the stop frame S, HP 0 on S + 75). Pressing later or from further away
only makes it worse (a pellet in flight holds its slot longer).

### The two jumps (the 1-player TAS does both; `tools/s5b_lab.py`, `logs/s5/mars_trace.txt`)
A jump from the tank's ground has Y < 108 for 9-12 frames (see sub-pixel below): for that long Bill may be
inside the tank's X range.
1. **Drive-in jump**: jump at row 58-66 after the tank's creation, keep scrolling above the box for 2-4 more
   frames after the tank has reached X 173 (where a standing Bill must stop), steer left for the rest of the
   window and all the way down; the tank stops at row 113 instead of 117 (window 9; the TAS, window 12: 109).
   Bill is still in the air when it stops: he fires down-right in 5-frame cycles (Right + Down + B two frames,
   Left three frames: every direction press is 2 frames long under our input rule), lands, turns, fires
   standing. No hit is lost against standing fire.
2. **Kill jump**: about 33 hits before the end jump straight up (no direction: Bill rises in place) still
   firing right while the muzzle is inside the box (Y >= 114), then hold Right + Down from the frame that puts
   him at X 115 exactly when his Y gets below 108, firing down-right (muzzle +15, +15: inside the box at any
   height). He is at X 123-125 instead of 113 when the tank dies and scrolls again 3-4 frames after the kill
   instead of 15. The timing is found by a grid over the HP at which the jump starts (too early = death: the
   window must cover the kill frame itself).
Net per tank: stop 117 -> 113, HP 0 193 -> 188 rows after creation, scrolling again about 15 frames sooner
(the wreck's auto-scroll makes that worth about 12 frames at tank 2's creation).
`tank_script2` (the script), `tank_fight3` (two-stage grid, 70-90 s per tank on 3 emulators; the first pass's
grid stays as the fallback).

### The Y sub-pixel decides the window (model, checked against the emulator)
`$94` is the low byte of Bill's 16-bit Y; it changes only in the air (by the sum of the frame velocities) and
carries from jump to jump. Jump from Y 164, frames with Y < 108 by `$94` at take-off: 0..13 -> 12 frames,
14..123 -> 11, 124..198 -> 10, 199..255 -> 9. A flat jump adds $4D. In all three runs the sub-pixel at tank 1
is $EF (window 9), then $3C for the kill jump (11).
Before each tank there is one ledge (world X 2271 / 3327, Y 132, drop to Y 164) that can be left by walking off
or by jumping off for the same one frame, and the two leave different sub-pixels ($EF / $6C at tank 1 from $39).
`jump_off_ledge` / `tank_windows` compute both and `policy()` can take the better one (`route.opts["ledge_jump"]`).
**Measured on `dbg/s5_pre`: slower (6045 against 6040), so it is OFF.** Reason, found with the traces: with the
11-frame window the best drive-in stops 2 frames earlier (row 111), but its jump starts later (row 64), Bill is
still in the air when the turret takes its first aim 8 frames after the stop, the turret already points at him
and **the tank's first bullet comes 56 frames after the stop instead of 104** (code: `tank_routine_02`,
bank0.asm:6409-6467: it fires only when the aim it computes equals the turret drawn, otherwise it turns and
waits $30 frames). The bullet is created at (tank X - 46, 124) and flies left: a jumping Bill with Y 114..125
is hit (his box is 12 px, a standing Bill is 40 px under it), and that is exactly where the kill jump is 56
frames after the stop. The kill jump then has to start 6-8 frames later and gives up what the earlier stop
gained. `tank_fight3` therefore tries several drive-ins (the earliest stop is not always the best fight; one
that lands before the turret aims is always among them) and a wide range of kill-jump timings.

### Tried and did not pay
- "Jump toward it and pull back" as the first pass scripted it (steer left for the whole flight): 1 frame
  slower than no jump, because Bill lands 95 px from the tank and cannot fire. The gain is in firing from the
  air after the stop, not in the jump.
- A press delay / a higher "do not fire above" limit in the kill jump (`dl`, `yf`): no effect once the rightward
  move starts before the window (down-right fire works at any height).
- Prone under the turret: the prone box reaches Y 165, Bill is at 164.

## UFO

### Why the first pass needed 81 frames (measured, `tools/s5b_cal.py`)
10 bullet slots. A pellet that hits keeps its slot until 7 frames after the hit, one that misses until it
leaves the screen (up to 38 frames from the ground). From the ground only the centre pellet and (with the
right X) the two inner ones can enter the box (X -16..+17, Y -16..+17 around (X, 48)); the first pass also
pressed B when no slot was free (a wasted press delays the next by 5 frames) and did not fire at all for the
28 frames around a landing.

### Offline model (`contra/stages/s5_ufo_sim.py`; checked frame by frame, `tools/s5b_simcheck.py`, `s5b_ufocmp.py`)
Per frame, in the game's order: fire (a new press fills the lowest free slots with pellets 0..4 = centre, +1,
-1, +2, -2; velocities for straight up, 1/256 px: (0, -892), (+-171, -878), (+-339, -826); muzzle X, Y - 16 in
a jump, X + 5, Y - 27 standing; the sub-pixel of a new pellet is whatever the slot's last pellet left; no move
on the creation frame) -> Bill's jump (velocity -1040/256, +35/256 per frame; lands when a falling frame
starts at Y >= 160) -> pellets move -> the UFO takes ONE pellet in its box (highest slot first) -> each bomb /
small saucer alive takes one pellet in its own box (-11..+10; bombs appear 32, 64, 96 frames after the UFO
opens at (X, 36) and fall 0, 0, 0, 1, 2, 3, 4, 5, 7, 8, 10, 12, 14, 16, 18, 21, 23, 26, 29, 32 px; saucers 48,
80 frames after, 20 px left / right) and is gone. With the bombs in, the model's HP curve equals the emulator's
on every frame of the planned fights (0 differing frames in the checks; without them the last pellet is lost
to bomb 2 and the kill comes 7 frames late).

### Planner and what it finds
Beam search in the model over "press B on this frame or not" (width 2000, 4 s per jump timing), for jump leads
22..35 frames before the UFO can be hit, jumping again on every landing. Every plan is replayed in the emulator
(the emulator decides), the best is refined there by hill climbing on single presses / jumps
(`UfoSchedule.refine`), and played. Model optimum 64-65 frames, emulator **65-66** (lead 27-29) for UFO X 128,
96 and 64 (`tools/s5b_ufox.py`: 65 / 65 / 66; the exit is 268 rows from HP 0 to "off screen" for all three, so
the UFO's X still does not matter). `ufo_fight4`; fallbacks `ufo_fight3` (the slot-aware script, 71-74) and the
first pass's grid. The planner runs in separate interpreters (`python -m contra.stages.s5_ufo_sim jobs.json`),
not `multiprocessing`: a caller without an `if __name__ == "__main__"` guard would otherwise re-run itself.

### The floor
One hit per frame is not reachable: every hit needs its slot for flight (7-24 frames, the jump's height) +
queue + 7, and there are 10 slots: about 0.5 hits per frame over a jump cycle, plus the two volleys already in
the box when it opens. The model's optimum for "jump on every landing" is 64; what could still lower it is
another jump schedule (not searched) or a way to stay near the top (none).

### Tried and did not pay
- Beam search in the emulator over the B presses, scored by HP minus pellets on their way, or minus the slots'
  remaining capacity: 81-84 frames (it fires from the ground too early; the score cannot see what a blocked slot
  costs later). Replaced by the model.
- Standing 3 px left of the UFO's X (so that both inner pellets fit from the ground): 1-3 frames worse than
  X once the presses are planned.

## Lag
The three lag frames of the `dbg/s5_pre` run (t = 2066, 2072, 2081, in the jump over screen 8's pillars) vanish
when B is not pressed on rows 2040-2064 (`tools/s5b_lagtest.py`: 3 px further at t = 2140, no death): they are
CPU load from the pellets. `Repair5` (s5.py) treats a lag frame of the main run as a failure whose candidates
are "accept it" (wins ties) and hold-fire / fixed-aim stretches before it; a trial that reaches the point
110 px further sooner replaces it. In the three final runs: one fix (`nofire` rows 2041-2065 in `dbg/s5_pre`),
no lag frame left in play in any of them.

## Running sections (measured, `tools/s5b_loss.py`, `s5b_path.py`)
Before tank 1 the run loses 21 frames: 20 jumps + 1 ledge landing (13 of the jumps are forced by the terrain -
every gap is 64 px and a flat jump covers 59, 61 at most (computed from the landing rule) - and 7 are for
grenades / turret-man bullets; read off the map and the take-off list by hand, no route search was run). The fitted TAS
loses 24 there. Not improved in this pass; a search over the first screen's four hazard jumps might save 1.

## Left on the table (estimates)
- Tank drive-in with a longer window (the TAS has 12 frames and stops the tank at row 109, we 113): up to 4
  frames per tank at the stop, but the earlier stop brings the tank's first bullet into the kill jump (above);
  whether both can be had (kill jump from further left, or after the bullet) was not searched. Estimate 0-3
  per tank.
- UFO: 1-2 (another jump schedule).
- Hazard jumps in the running sections: 1-3, uncertain.
- Tank kill and everything after the UFO's last hit: at the floor under the cap.

## Second-pass files
- `contra/stages/s5.py` (solver), `contra/stages/s5_ufo_sim.py` (offline UFO model + planner; also a worker:
  `python -m contra.stages.s5_ufo_sim jobs.json`), `contra/stages/s5.py.backup_v1` (first pass).
- Tools (experiments, one emulator or a farm of 3 each): `tools/s5b_lab.py` (tank / UFO scripts and traces),
  `s5b_cal.py` (RAM dump of a UFO fight), `s5b_simcheck.py` / `s5b_ufocmp.py` (model against emulator),
  `s5b_simscan.py` (model optimum by jump lead), `s5b_ufox.py` (the three UFO positions), `s5b_lagtest.py`,
  `s5b_loss.py` (every frame without forward progress, stage 1 or 5), `s5b_path.py` (take-offs / landings and
  the Y sub-pixel).
- Earlier second-pass solves, kept: `d0v2` (6051: tanks + UFO script), `d0v3` / `w1v3` / `w37v3` (6040 / 6041 /
  6041, before the wider tank grid), `d0v4` (6045, ledge jump on).


# Rule v2: the press budget (2026-10-12 solves; pre_w37 re-solved, all verified and written up 2026-10-16)

Rule v2 (`project_rules.md`): besides the 5-frame rule, at most 109 new presses of one button in any 600 frames and
246 in any 1,800, across stage boundaries; `check_inputs.py` checks it at its defaults. The second pass mashed B
the whole stage (1,002-1,006 presses, 120 in 600 frames, 360 in 1,800): it broke both limits.
The previous agent was stopped on 2026-10-12 while the `pre_w37` solve was running and before it wrote this
section; `pre_w37` was re-solved from scratch on 2026-10-16 with the unchanged solver, the rest was re-checked from
the files on disk.

## Result

| start state (history) | second pass | rule v2 | change | B presses (old -> new) | most B in any 600 / 1,800 frames, history counted (old -> new) | lag frames, in play / all (new) |
|---|---|---|---|---|---|---|
| `dbg/s5_pre` (none) | 6040 | **6042** | +2 | 1002 -> 145 | 120 / 360 -> 44 / 67 | 0 / 13 |
| `s5/pre_w1` (none) | 6041 | **6039** | -2 | 1006 -> 158 | 120 / 360 -> 46 / 70 | 0 / 13 |
| `s5/pre_w37` (none) | 6041 | **6041** | 0 | 1005 -> 145 | 120 / 360 -> 46 / 69 | 0 / 13 |
| `s5/c1_pre` = chain1's real stage 5 state (real history: `chain1/runs/prior_s5_c1.inputs.txt`) | 6041 (chain1) | **6040** | -1 | 1006 -> 156 | 121 / 361 -> 47 / 73 | 1 (row 1908) / 14 (chain1: 13) |

Frames = stage 5's first frame to stage 6's first frame (`L6` of the replay report). Verified for all four:
open-loop replay on a fresh emulator (`tools/s5_finish.py <state> <name>`: ends on stage 6's first frame, no death,
weapon $13, 3 lives (c1: 5)), `check_inputs.py` PASS at its defaults on the segment, and `tools/s5c_check.py`:
PASS on the last 2,000+ history rows + the segment (for c1; the debug starts have no history - assumed empty, which
is the real case only if stage 4 ended with no B presses in its last 1,800 frames; it will not, so the chain must
hand the real history to the solver, as for c1). For c1 the WHOLE chain1 history + segment fails rule v2 only on
history rows up to 3,783 (chain1's own stage 1, made under rule v1), never on a row of the new segment.
Rule v2 costs nothing measurable: -2..+2 frames, the usual scatter between start conditions (tank and UFO kill rows
move by 1-2 with the RNG). The budget never refused a press (`refused by the pad's budget 0, by the press plan on 0
rows`); the run phases used 102-114 presses and the tanks and UFO keep their fast fire. The one in-play lag frame of
c1 (row 1908, two volleys in the air) is the reason for the repair candidates noted in s5.py's rule v2 changes; it
was not removed there, but c1 is still 1 frame faster than chain1's stage 5. Other buttons: Down 51-58 presses (at
most 35 in 600 frames), A 37 (8 / 20), far inside the windows.

## What changed in the solver (`contra/stages/s5.py`; before: `s5.py.backup_v2`; `s5_ufo_sim.py` unchanged)
- The press budget lives in `s1_common.Pad` (see `s1_notes.md`, rule v2); the press plan `PLAN = Fights([(2432,
  22), (3456, 22), (5240, 18)])` keeps room for the two tanks and the UFO.
- The run phases no longer mash: B at an enemy ahead when a volley fired now is predicted to hit it and the
  bullets in flight do not cover its HP (`s1.pick_shot`), with the "let it pass" look-ahead of
  `s1_engine.Repair(engage=...)` (verdicts per run: 12-21, 1-8 of them "pass"), and on rows the repair search
  marked `fire` / `aim` (new repair candidates: cadence fire before the failure and before the enemies that appeared
  last).
- The wait for the UFO no longer fires (it mashed straight up for 19 presses for nothing); `wait_for_ufo` falls
  back to the policy, then cadence fire, if Bill dies.
- Optional try of the other tank parity (one extra jump before a tank), kept only if the scroll passes the tank
  sooner.

## Files
- Segments `logs/s5/d0_v3.seg.json`, `w1_v3.seg.json`, `w37_v3.seg.json`, `c1_v3.seg.json` (+ `.inputs.txt`,
  `.report.json` from the replay); rule v2 checks `logs/s5/<name>_v2check.inputs.txt` / `.json` (c1 also
  `_v2check_whole.json`); solver logs `logs/s5/solve_<name>.log` (`solve_w37_v3.log` is the 2026-10-16 re-solve;
  the stopped run's log was overwritten). Driver: `python tools/s1c_queue.py s5:<d0|w1|w37|c1>` (solve + verify).
- The second pass's `*v5*` files are untouched.
