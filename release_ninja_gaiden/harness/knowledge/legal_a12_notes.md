# Legalizer (ng/legal.py) and Acts 1-2 notes (agent a12)

## STATUS (read this first)

* 2026-10-23 06:00 ROUND 5 (c5, PAUSED): chain unchanged; 2-2 room 6 partial -33 f (Mesen + NesHawk replay), see "Round 5 (chain)" at the end.

* 2026-10-23 04:35 ROUND 4 (toolkit agent "tk"): VERIFIED power-on chain to **3-3 control, frame 15,140**:
  `logs/tk_to33.inputs.txt` (two power-on replays MATCH, check_inputs PASS), state `states/tk_3-2_c1_end`
  (hp 8, ninpo 23, Fire Wheel). New 1-1 = the coordinator's fastcore 1-1 (-44 f); 1-2 and 2-1 rows replay unchanged
  after it; 2-2 / 2-3 / 3-1 / 3-2 new (table in knowledge/toolkit.md, details in "Round 4 (tk)" below). 3-3 NOT solved.
  The old 2-2 control state `states/a12r3_2-1_v1_end` (frame 6,393) is superseded by `states/tk_2-1_s11_end` (6,349).

* 2026-10-20 08:50 ROUND 3 (PAUSED by the owner): verified chain now reaches 2-2 control (frame 6,393): `logs/a12r3_to22.inputs.txt`, state `states/a12r3_2-1_v1_end`; 2-1 = 2,964 f (record +59). NO 3-1 control state yet. See "Round 3 STATUS" at the end.
* 2026-10-20 01:15 ROUND 2: no new verified stage; see "Round 2 STATUS" at the end (partial 2-1 to room 5,
  record-route tools, hybrid reference). The verified chain below is unchanged.

* 2026-10-19 14:55 - VERIFIED: power-on -> 2-1 control, legal: `logs/a12_chain.inputs.txt` (= intro + 1-1 v5 +
  1-2), assembled as `logs/a12_act1.inputs.txt` (assemble.py: two power-on replays MATCH, RAM sha1 a0f72e689e24,
  trace sha1 c660d2773483; check_inputs.py PASS). Stage files: `logs/a12_intro.inputs.txt`,
  `logs/a12_chain_1-1.inputs.txt` (= a12_1-1v5), `logs/a12_chain_1-2.inputs.txt`; end states
  `states/a12_chain_<stage>_end.State`.

  | stage | ours (control->control) | TAS | record | vs TAS | vs record |
  |---|---|---|---|---|---|
  | 1-1 (v5, keeps 10 ninpo) | 2,417 | 2,294 | 2,309.8 | +123 | +107 |
  | 1-1 (v1, 0 ninpo; not used) | 2,361 | 2,294 | 2,309.8 | +67 | +51 |
  | 1-2 | 838 | 834 | 841.4 | +4 | -3 |
  | 2-1 control (from power-on) | frame 3,429 | 3,302 | ~3,325 | +127 | ~+104 |

  1-1 v1 is faster but arrives at 1-2 with 0 ninpo; a sword-only Barbarian took 360+ frames and was still at
  boss HP 10 (`ng/stages/a12_boss.py` beam, stopped), so v5 (+56 in 1-1, ninpo 10, two Jump & Slash spins
  at Barbarian like the TAS) is the chain's 1-1.
* 2-1 .. 2-3: NOT solved. The chained 2-1 (from `states/a12_chain_1-2_end`) reached row 1,059 and then every
  continuation died (room 2 -> 3 climb); a resume showed the Repair's "lag" there was bogus (it reported ~-20
  while Ryu was really ~350 reference frames behind in X: the loose/exact sync matched a wrong reference
  frame). Suspect: `Segment.match` / sync on the long flat run of 2-1 room 2. Must be fixed before 2-1/2-2
  are worth running. A TAS-state 2-1 attempt got to row ~1,840 (lag ~37 by its own, possibly also wrong,
  measure) before breaking. Partial rows: states/tmp/a12_chain_2-1.partial.inputs.txt,
  states/tmp/a12_2-1.partial.inputs.txt.
* `ng/legal.py` API as documented at the top of the file (open loop project/enforce/Legality; closed loop
  effects_resolve/Segment/Repair). Repair is SLOW (about 100 emulated frames/s; 1-1 took 35-60 min) and
  gets worse the further it falls behind the TAS (enemies act on the frame counter, so a late Ryu meets
  different enemies).

* `ng/stages/` is a folder WITHOUT `__init__.py` on purpose: `ng/stages.py` (the stage table module) must keep
  winning `import ng.stages`. Scripts in the folder add the project root to sys.path themselves.
* Power-on -> 1-1: `logs/a12_intro.inputs.txt` (intro_human rows 1-173 + Right on 174) gives EXACTLY the
  TAS's 1-1 control RAM (state `states/a12_intro_174`, 0 bytes differ), so a 1-1 solved from
  `ref4751/00_1-1_control` is already a power-on solution.

## API stability promise

Names in the module docstring of ng/legal.py stay; new keyword arguments get defaults. Behaviour fixes may change
the exact rows produced (never their legality).

## What L+R and U+D do in this game (from the ROM code, bank 7; disassembly dl/NinjaGaidenNES)

Ryu's control picks a handler from the jump table at `$F087`, indexed by the four direction bits of `$28`
(Right 1, Left 2, Down 4, Up 8):

| held | handler | | held | handler |
|---|---|---|---|---|
| none | idle | | Up | up (Up+B = sub-weapon) |
| Right / Down+Right / Up+Right | right | | Down | down (crouch, air: no speed write) |
| Left / Down+Left / Up+Left | left | | **L+R, U+D, U+D+L, U+D+R, D+L+R, U+L+R, all four** | **idle** |

* The handlers write the facing (on the ground only) and the x speed: `run_speed` 1.5 px/f when moving the way
  Ryu faces, `drift_speed` 0.5 px/f when holding the other way in the air. **idle writes no speed.**
* The movement itself is done separately by `move_ryu` (`$E833`) from the RAW bits: Right bit first, then Left.
* So every banned combination = "move with the raw Right (or Left) bit, at whatever speed is stored, while the
  handler is idle": no facing change, no speed write, no walk/jump action change.
  - **L+R in the air facing left** = move RIGHT at the stored 1.5 px/f while still facing left (TAS 2-1 rooms
    3-4, 2-2: e.g. frames 4354-4387, 5125-5198). Legal Right there = 0.5 px/f (drift). Legal options: turn
    on the ground before the jump (facing = travel direction), or accept the 1 px/f loss, or a different
    wall sequence. No exact legal equivalent exists.
  - **U+D+Right on the ground** (1-1, 2-1, 2-2: every other frame) = the same movement as Right but with the
    idle animation (anim 0 instead of 1). Positions identical (measured: 600 frames of 1-1, no position
    difference). Legal: Right. (The RAM differs only in the animation bytes; the Repair sync ignores `anim`.)
  - U+D+L on a wall = move toward the wall at the stored speed with no handler (the "wobble").
* The legal wall climb used by the TAS itself (2-1 room 3, 4299-4330): "Right+A, Left+A, -, -, -" repeated
  every 5 frames climbs at -2 px/f. Its A presses are already at the legal rate (period 5, hold 2, release 3) but
  its Right/Left are 1-frame presses; legal holds need 2 frames each ("R+A, R+A, L, L, -" fits exactly in 5).

### Walls (bank 7 `$EBD8`-`$EC58`, read 2026-10-19)

* When `touching` ($8C) & $2A says Ryu is on a wall, the direction table is NOT used. Instead the HELD pad
  (`$28`, not the new-press byte) is compared with ONE exact value: wall on his right -> `$82` (A+Left),
  wall on his left -> `$81` (A+Right). Equal = **jump off** (vy = -2 with fraction 0, facing flipped,
  `run_speed` 1.5 px/f away from the wall, touching = $C0). Anything else = "hold on" (cling).
* So a jump-off needs no new press, only the exact held combination; A can stay held through a whole climb.
* After a jump-off Ryu faces away from the wall; pressing back toward it in the air = drift 0.5 px/f, while the
  TAS's U+D+toward (idle handler + raw move) comes back at the stored 1.5 px/f. That is the wall "wobble".
* Legal climb cycle (wall on the right), 5 frames: `A+Left, A+Left, Right, Right, Right` (1.5 px out, 3 x 0.5
  back, cling, jump off again: about -2 px/f, the same rate as the TAS's `R+A, L+A, -, -, -`). Every press is
  2+ frames, every button period 5. A can also be held throughout (`A+L, A+L, A+R, A+R, A+R`): pad $81 on the
  wall on the right is "hold on", $82 the next frame jumps off. Mirror for a wall on the left.
* The Repair beam has these two cycles as macros.

## Acts 1-2 log (agent a12)

* Record per stage (control -> next control, NES frames, from record_events.json `control_est_cum_nes`):
  1-1 2,309.8 | 1-2 841.4 | 2-1 2,904.8 | 2-2 3,101.1 | 2-3 833.3 (sum 9,990.4).
  TAS 4751M: 2,294 | 834 | 2,802 | 2,895 | 830 (sum 9,655).
* 1-1 v1 (logs/a12_1-1_v1.inputs.txt, 10:25): legal, verified open-loop, 2,361 f (+67 vs TAS, +51 vs record).
  Losses: the pole double jump-off at TAS frame 799-802 (about 22 f: the TAS's `L+A, R+A, U+D+L, R+A` gives two
  jump-offs from the "GO" sign pole; no legal sequence reproduces the second one - brute force of 500 legal
  8-frame continuations after `L+A, L+A, R+A`: none reaches the shop roof (X >= 867, y 144) within 30 frames);
  then enemies differ because we are 25+ frames late (they act on the frame counter $BF), +37 f near the end
  (a boxer blocks the way, the beam climbs the sign poles), and it spent all ninpo on Jump & Slash (ninpo 0
  at 1-2 instead of the TAS's 10) -> ninpo deficit now costs 3 f/point in the Repair score.
* The record's 1-1 route at that spot is different: it stays on the "Sale" shop roof and goes over the tall
  grey building at the top of the screen (record video 36-40 s), i.e. no pole trick.
* Route-agnostic attempts at the 1-1 pole (coordinator: use the record's route): a 16-wide, 50-step beam from
  TAS frame 624 scored only by progress along X (`Segment.progress_mode = "axis"`) runs into the wall at
  X 859 (dead end, lag +60); with a bonus for height (`height_w` 0.2) it climbs the wall and gets over at
  lag +36. Neither finds the record's roof route on its own; that route needs a reference path (waypoints from
  the record video), not done yet.
* Ninpo matters for 1-2: the TAS arrives with 10 ninpo and kills Barbarian with two Jump & Slash spins (86 f
  after control). 1-1 v1 arrives with 0 ninpo (it missed the +5 lantern at TAS frame 1882 being 28 f late,
  and spent the rest); a chained 1-2 from it was 86+ f behind before the kill (stopped). Repair now scores a
  ninpo deficit (default 3 f/point, run_stage `--ninpo-cost`).
* Repair loop bug (fixed 13:25): a repair could rewind to the same checkpoint forever; now later repairs never
  rewind past the end of the previous repair (`_floor`), and a repair that ends at the divergence point is
  followed by a beam "walk" from there.

## How to use the tools (a12)

* One stage from the TAS's state: `python ng/stages/run_stage.py --stage 1-1 [--width 6 --step 5 --horizon 16]
  [--ninpo-cost 3 --ninpo-floor 10 --esc-lag 8] [--prefix partial.inputs.txt]` -> logs/a12_<stage>.inputs.txt,
  .stage.json (verify = open-loop replay from the start state, legal = check_inputs rules with history).
  Partial solutions are dumped to states/tmp/<out>.partial.inputs.txt after every repair; `--prefix` resumes.
* From any state: add `--start <state> --history <inputs from power-on>` (see the chained 2-1 resume).
* Chain: `python ng/stages/a12_chain.py --from 1-2 --to 2-3` (reuses logs/a12_chain_<stage>.inputs.txt).
* Boss without a TAS line: `ng/stages/a12_boss.py` (beam scored by boss HP; worked but too slow sword-only).
* Analysis: `ng/stages/a12_compare.py <stage> <inputs>` (room/item/hit events vs the TAS),
  `ng/stages/a12_probe4.py` (try hand-written legal patterns from a TAS frame), `a12_brute.py` (enumerate
  short legal segment sequences), `a12_view.py` (TAS rows + trace fields).

## Lessons / what to do next (a12)

* Following the TAS works while we stay within ~10 frames of it; once 25+ frames late, enemies (driven by
  the frame counter) differ and the TAS rows stop helping. So the first big legal loss (1-1 pole) poisons the
  rest of the stage. Fixing the big losses with the RECORD's route (reference waypoints from the video) is the
  next real gain; the generic beams (TAS-nearest, X-axis, height bonus) did not find it.
* Keep ninpo for the boss (1-1 -> 1-2: 10 needed). Use `--ninpo-floor`.
* Repair cost: near edits ~1 min, beam ~2-4 min, beam2 ~5-8 min per divergence at ~100 frames/s.
* Bug found 15:40 (fixed): the loose sync required equal HP, so after one hit the TAS never took, Ryu could
  never be "in sync" again; every later repair then guessed the reference index from position only, that
  guess drifted (window +15 per repair) and the logged lags became meaningless (the chained 2-1 stood still at
  X 315 for 240 frames while the log said it was ahead of the TAS). Now HP is only scored (hp_cost), not part
  of the loose sync. The 1-1/1-2 results above were made before this fix.
* 16:05: chained 2-1 rerun after the HP fix: reached row 1,960 (room 3/4 wall climbs) at about +145 reference
  frames behind the TAS, then "stuck" (every continuation dies or stalls). Partial rows:
  states/tmp/a12_chain_2-1.partial.inputs.txt. Time-box over; 2-1, 2-2, 2-3 remain unsolved.

## Round 2 (agent a12r2, 2026-10-19 16:05 -> ; coordinator: beat the record's split per stage, use the record's route
## where the TAS line is banned)

### Record route extractor (done) -> `knowledge/record_route_a12.md`
* Frames cut with `states/tmp/a12r2_vid/extract.sh`, traced with `work/a12r2/rtrace.py` (agent a56's tracker reused,
  HUD mask 60) -> `work/a12r2/rec/r11/r12/r21/r22/r23.json`.
* `ng/legal.py` NEW (API addition, nothing changed): `Waypoints(rec_json, stage)` (calibrated RAM-coordinate route,
  facing-corrected x, camera rule for Ryu off-screen, `.time_map()` DTW to the TAS), `waypoint_ref(wp, f0)` (a
  StageBeam reference in record time). Driver `ng/stages/a12r2_solve.py` (a56's StageBeam, read-only import;
  `--rec` = record ref, `--tasref` = TAS ref; `--prefix`; legal 7-frame wall-climb macros), go-explore
  `ng/stages/a12r2_goex.py`, probes `work/a12r2/*_probe.py`, job queue `work/a12r2/runq.py` (RAM >= 2.5 GB).
* Per-column tables: `work/a12r2/rec/cmp_r11.txt, cmp_r21.txt, cmp_r22.txt` (`work/a12r2/cmp.py`).

### Findings
* 1-1: the record is TAS +0..4 to X 704, loses ~19 f at X 640-704 (roof hop instead of the pole double jump-off),
  then runs level with the TAS (+19) to the exit. To beat its split a legal 1-1 needs the roof crossing within
  ~15 f of the TAS. Attempts: record-ref beam (w1) +34 after the roof, then lost more on the flat part (+148 at
  f 1830; killed); go-explore g2-g5 (value = lag vs the record) all stall at X ~740 y 112 on the shop's top slab
  (a club enemy on the slab, `shots/a12r2_roof_1.png`; the record slashes it, t ~480). Not solved; round 1's
  1-1 v5 (2,417) stays in the chain.
* 2-1 room 2: the legalized TAS rows replay in sync even 127 frames late (StageBeam lazy follow with the TAS
  reference: whole room 2 at TAS pace, `--tasref`). Record-ref beam there lost ~40 f: use the TAS reference where
  the TAS line is legal.
* 2-1 room 3 start (pillar): TAS and record take the same line: climb the hazard pillar's left face, wall-jump
  left onto the small ledge (x ~110, y 160), jump right onto the pillar top (x ~170, y 128). The TAS's last jump
  is L+R (moving right while facing left); legal = land, hold Right 2-3 frames (turn), then Right+A.
  The 5-frame climb cycles (A+away x2, back x3) do NOT re-grab this wall; 7-frame (A+away x2, back x5) is the
  fastest that does (~1.1 px/f; TAS 2 px/f). Brute force (`work/a12r2/r3_brute.py`): pillar top on frame 4596
  (chain numbering; record pace + ~17, TAS +79). `states/tmp/a12r2_r3_best.inputs.txt` (1,167 rows after
  a12_chain_1-2_end, legal).
* 2-1 room 3 X ~363: the TAS jumps over a thin post to the big hazard block (X 391, y 128); a beam that
  falls short clings to the post (y 145) and stalls (t5 run lost 140 f there, `shots/a12r2_t5_3.png`,
  `shots/a12r2_tas21b_0.png`).
* 2-2 room 6: TAS rows followable (lazy) to the room exit; the exit uses L+R in the air (TAS 6709-6712): the
  record simply drops at x ~82-84. Room 7 start: the TAS goes left with L+R; the record goes right/up first
  (cols 13-15) - a TAS-ref beam stalls at X 834 y 82.
* 2-1 room 4 (chimney, TAS 5101-5199): TAS = wall jump-off left from the right wall at the entry (L+A), lands on a
  small ledge (x 134, y 215), jumps STRAIGHT up (A) and moves right with L+R (facing left, 1.5 px/f) to the right
  wall (157, 160), L+A to the left wall (118, 112), L+R+A / L+R to the exit at the top right (155, 80). Legal
  problems: turning right on the ledge walks off it (ledge too small), and a straight jump + Right drifts at
  0.5 px/f only. The record instead wall-jumps from the left wall at (122, 209) with A+Right (facing right, 1.5
  px/f): entry needs upward momentum from room 3's exit (the record enters rising at y 220; a beam that enters at
  y 232 with no momentum only gets a 15-px hop from the right wall and falls past the left wall).
  Exit: walk right along the top to x 155 (room change); the record's trace stands still there for 32 f during
  the fade (Waypoints now drops such trailing still points; they made the beam wait at the exit).
* StageBeam "lag" numbers (f - k) are NOT reliable after explores (the pointer k can stick); compare first-reach
  times per column instead. Real numbers for the chained 2-1 (frame numbers from power-on): room 3 entry ~4450
  (record 4452 = level), pillar top 4596 (record 4579), room 4 entry ~5478 (record 5313: +165, lost in room 3
  cols 2-17), room 5 entry 5656 (record ~5447: +209).

### Round 2 STATUS at the end of the time-box (2026-10-20 01:15)
* NO new verified stage. The verified chain is still round 1's: power-on -> 2-1 control (frame 3,429),
  `logs/a12_chain.inputs.txt` / `logs/a12_act1.inputs.txt` (1-1 2,417 = record +107, 1-2 838 = record -3).
  No 3-1 control state to publish.
* Best partial 2-1 (legal by check, NOT finished, not open-loop verified to the stage end):
  `states/tmp/a12r2_2-1_room5.inputs.txt` = 2,229 rows after `states/a12_chain_1-2_end` (history
  `logs/a12_chain.inputs.txt`), reaching 2-1 room 5 (the last room) on frame ~5,656 = about +209 behind the record
  at the same point (record ~5,447). Rooms 2 (TAS lazy follow: record pace) and the pillar (brute force) are good;
  the losses are room 3 cols 2-17 (~150 f, beam) and room 4 (the chimney).
* Next command (queued, never started: free RAM stayed < 2.5 GB from 20:48 to 01:14):
  `python -u ng/stages/a12r2_solve.py 2 a12_chain_1-2_end --history logs/a12_chain.inputs.txt --rec work/a12r2/rec/r21.json --hybrid --prefix states/tmp/a12r2_2-1_room5.inputs.txt --prefix-frames 2229 --width 8 --chunk 8 --explore 4000 --hours 1.5 --tag w10`
  (room 5 is a TAS-legal leftward run; the hybrid reference makes it a lazy TAS follow), then 2-2 with `--hybrid`
  from its end state, then 2-3 (boss beam, `--tasref`; needs J&S + >= 10 ninpo, the 2-1 partial has J&S/10-15).
* Can the record's splits be beaten here? 1-1: only if the roof crossing is within ~15 f of the TAS (record +19;
  our best attempts +34..+53). 2-1: the record is TAS +103 but its route through room 3/4 is already the
  human-optimal legal one; our beam is ~+200 behind it, so the remaining work is room 3 (cols 2-17, plain
  running/jumping where TAS rows could be followed lazily if the beam resynced to the TAS line after the pillar)
  and room 4 (enter rising: jump at room 3's exit, wall-jump right from the left wall at (122, 209) with A+Right).
* Lessons: (1) where the TAS line is legal, the TAS reference + lazy follow is far better than the record
  reference (exact positions, ~1 emulation per chunk); use the record only around L+R / wall tricks (`--hybrid`).
  (2) Short hard spots (pillar, post, chimney) are solved faster by a small brute force over press timings
  (`work/a12r2/r3_brute.py`, `jump_brute.py`, `press_search.py`) than by the beam's explore. (3) Do not trust the
  beam's printed lag after an explore; measure first-reach times.

## Round 3 (agent a12r3, 2026-10-20 ~01:40 ->)

### Round 3 STATUS
* (in progress) 01:40 queue `work/a12r3/runq.py 3 work/a12r3/jobs.txt` (PIDs -> `logs/a12r3_pids.txt`) started with w10
  (2-1 room 5, `--hybrid`, `--pfx a12r3`: `a12r2_solve.py` has a new `--pfx` option for the output names). Free RAM
  at start 0.9-1.4 GB (mnm 3.2 GB + other agents' EmuHawks): the job waits for >= 2.5 GB.

### Round 3 log* 01:40-03:16: free RAM 0.4-1.4 GB the whole time (mnm ~3 GB, Memory Compression up to 3 GB, chrome/claude ~4 GB;
  the a56r3 / a34r3 queues are waiting too). Nothing started. Prepared while waiting:
  - `work/a12r3/tasfollow.py` (replay legalized TAS rows from TAS frame k0 after our rows; prints the first frame
    that leaves the TAS line), `work/a12r3/wbrute.py` (all length combinations of a small input grammar, Enforcer-
    legalized, earliest goal frame).
  - 2-1 room 3 analysis (TAS trace): between the pillar top (TAS 4388) and the room exit (5072) the TAS line is
    LEGAL except a 1-frame Left at TAS 4530 (X 379, y 144, the thin post before the big block; a legal Left is held
    >= 2 frames -> desync; this is round 2's "post" loss) and the exit's L+R (5075/5079). Round 2's t5 (TAS ref) was
    in lazy sync from the post to X ~1170 (f 4972-5372). So: pillar (r3_best, chain f 4596 = TAS 4388 + 208)
    + legalized TAS rows + a brute-forced post window + the record's rising room-4 entry should give room 4 entry
    ~5290 (record 5313).
  - 2-2 room 7 (TAS 6744-6852): after the start the TAS climbs with Right+A jump-offs and U+D+Left in the air
    (idle handler + raw left move at 1.5 px/f): not legal (legal Left in the air = 0.5 px/f drift).* 05:11 RAM freed (3.9 GB); jobs ran 05:11-07:00.
* **2-1 v1 SOLVED + verified open-loop (finish_stage.py): `logs/a12r3_2-1_v1.inputs.txt` (2,964 f, control 3,429 ->
  6,393; record 2,904.8 -> +59; TAS +162), end state `states/a12r3_2-1_v1_end` (hp 16, ninpo 0, J&S item 133),
  legal with history `logs/a12_chain.inputs.txt`.** Built from:
  - rows 0-1166 = round 2's pillar brute force (`states/tmp/a12r2_r3_best`, pillar top f 4596 = TAS 4388 + 208);
  - `work/a12r3/r3_pipe.py`: legalized TAS rows from the pillar with a brute-forced jump at the post (stage 1: jump
    on TAS 4511, hold 2) and a post window (stage 2 `(0,0,0,2,6,2)`): in sync with the TAS (+209) to TAS 5068 = f 5277
    (`states/tmp/a12r3_r3_exit209`). Round 2's beam lost ~190 f in the same stretch.
  - room 3 exit (`wbrute.py`): Right 4, A+Left 2, Right 4, A+Left 2, Right 3, A+Left 2 = three wall jump-offs from the
    room's right edge (the legal climb), room 4 at f 5302 (TAS 5080 + 222). `states/tmp/a12r3_r3x`.
  - room 4: round 2's room-4 rows grafted unchanged (room 4 has no enemies; same start state after the fade):
    5302 -> room 5 at 5488 (186 f; TAS 120). `states/tmp/a12r3_r4graft`.
  - room 5: legalized TAS rows from TAS 5222 (after the fade, +289): IN SYNC to the stage end (load 6241).
* Ninpo: ours 0 at 2-1's end (TAS 10): the TAS's +10 pickups at TAS 3880 (room 2) and 4449 (room 3) do not happen for
  us (we are late; we get +5, +5, +5) and the 4 J&S spins in room 3 are needed: dropping any of the 3 room-3 spins
  (rows 1520, 1695, 1737) kills Ryu or stalls him (tested, `states/tmp/a12r3_21js_*`).
* Room 4 is now the biggest 2-1 loss (186 f vs the TAS's 120). Findings (`work/a12r3/stage_jumps.py`, probes
  `work/a12r3/dbg.py`): room 4 starts after a 22-frame fade standing on a floor at (155, 232) against the right wall;
  momentum is NOT carried over from room 3 (vy reset). A+Left on the first control frames = weak wall jump-off
  (15 px); Up climbs the wall 1 px/f (TAS 2 frames of Up, then A+Left: lands on the ledge at (136..139, 215)).
  From the ledge: A + Left reaches x ~115 at y ~169 with no wall there; A+Right on the same frame as the jump keeps
  facing left (0.5 px/f drift); Right on the ledge at x 134 lifts Ryu to y 208 and hangs there (no jump possible);
  the right-side platform is at (>= 153, 160). No legal sub-120 line found yet; round 2's beam line (186) stays.* 08:35 VERIFIED chain power-on -> 2-2 control: `logs/a12r3_to22.inputs.txt` (= a12_chain + a12r3_2-1_v1, 6,393 rows;
  assemble.py: two power-on replays MATCH, RAM sha1 457c236f89be, trace sha1 de65a822350d; check_inputs.py PASS with
  --period 5 --hold 2 --release 2 --windows 600:109,1800:246). 2-2 control state `states/a12r3_2-1_v1_end` (frame 6,393).
* 2-2 (from our 2-1 end, +289 vs the TAS): the TAS rows desync at once (2-2 starts 3 px further right than the TAS's,
  then an enemy the TAS killed with a J&S spin hits us: we have 0 ninpo). Beam h1 (`--hybrid`): room 6 took 845 f
  (TAS 619), hp 16 -> 12, no ninpo pickups; stuck at room 7's start (840, 128) like round 2.
  `ng/legal.py` hybrid_ref got a new keyword `ud=False` (API addition; True = also splice the record's route around the
  TAS's U+D+direction rows in the air, which a legal row cannot copy: room 7's start climbs with them), solver flag
  `--ud`. h2 = h1's room 6 rows + `--ud`.* 08:50 PAUSED by the owner (usage limit). All a12r3 jobs and the queue were killed.

### Round 3 STATUS (2026-10-20 08:50, paused)
* VERIFIED: power-on -> 2-2 control, `logs/a12r3_to22.inputs.txt` (6,393 rows; two replays MATCH; check_inputs PASS).
  Stages: 1-1 2,417 (record +107), 1-2 838 (-3), 2-1 2,964 (+59; `logs/a12r3_2-1_v1.inputs.txt`, .json).
  2-2 control state `states/a12r3_2-1_v1_end` (hp 16, ninpo 0, J&S). History file `states/tmp/a12r3_hist22.inputs.txt`.
* NO 3-1 control state to publish yet.
* 2-2 partial (legal, not verified to the end): `states/tmp/a12r3_2-2_partial.inputs.txt` = 1,766 rows after
  `a12r3_2-1_v1_end` (h1 room 6 + h2 room 7) reaching room 7 X ~102 y 116 at f ~8,159, hp 12, ninpo 5. Room 6 cost 845 f
  (TAS 619) and room 7's start ~300 f: 2-2 will NOT beat the record (3,101) on this line.
* Resume (queue: `python -u work/a12r3/runq.py 3 work/a12r3/jobs.txt`, gate 2.5 GB):
  1. `python -u ng/stages/a12r2_solve.py 3 a12r3_2-1_v1_end --history states/tmp/a12r3_hist22.inputs.txt --rec work/a12r2/rec/r22.json --hybrid --ud --prefix states/tmp/a12r3_2-2_partial.inputs.txt --prefix-frames 1766 --width 8 --chunk 8 --explore 4000 --hours 2 --tag h3 --pfx a12r3`
     -> `logs/a12r3_2-2_h3.inputs.txt`, state `states/a12r3_2-2_h3_end`.
  2. 2-3: `python -u ng/stages/a12r2_solve.py 4 a12r3_2-2_h3_end --history <to22 + 2-2 rows> --tasref --width 8 --chunk 8 --hours 1 --tag b1 --pfx a12r3`
     (sword-only if ninpo < 5).
  3. `python assemble.py a12r3_to31 logs/a12r3_to22.inputs.txt logs/a12r3_2-2_h3.inputs.txt logs/a12r3_2-3_b1.inputs.txt --serial` + check_inputs.py.
* Improvement leads: 2-1 room 4 (186 f vs TAS 120; graftable, no enemies, but room 5 / 2-2 must be redone after);
  2-2 room 6 (TAS rows sync from the TAS state but not from ours: enemies + 0 ninpo); 1-1 club enemy (not started).
* Tools: `work/a12r3/tasfollow.py`, `wbrute.py`, `r3_pipe.py`, `stage_jumps.py`, `dbg.py`, `rooms.py` (room/ninpo
  trace), `finish_stage.py` (to control + verify + save).
## Round 4 (tk, 2026-10-22 from 19:58)

* 2-2 room 6 loss analysed (`python -m ng.solve.compare a12r3_2-1_v1_end states/tmp/a12r3_2-2_partial.inputs.txt --col 64`):
  level with the TAS to X 896 (t 11), then +182 between X 896 and X 640 (ours t 364, TAS t 180): a knife thrower
  (type 2) on the platform at X ~740 and a jetpack ninja (type 18) above it; the TAS kills them with a J&S spin
  (ninpo 10 -> 5 at t 140), the record arrives with 15 ninpo + the Windmill and kills the thrower with it (video ~7896).
  We arrive with 0 ninpo, J&S. The first lanterns of room 6 are +5 at X 672 and +10 at X 608 (ROM tables,
  `python -m ng.solve.items 2-2`), i.e. after that spot.
* 2-2 room 7: ours t 846 -> X 768 at t 1234 (388 f) vs TAS 619 -> 722 (103 f; the TAS goes left at the top with
  L+R / U+D+L) and the record ~+110 vs TAS.
* 2026-10-23 00:20 coordinator: adopt the fastcore 1-1 (`logs/fcv_s11.inputs.txt` rows 175-2405, exit 44 f earlier).
  Done, all NesHawk open loop + judge (ng.solve.verify finish, logs/results.json):
  - `logs/tk_1-1_s11.inputs.txt` 174 -> 1-2 control 2,547 (2,373 f, TAS +79, record +63; hp 11, ninpo 10, J&S),
    state `states/tk_1-1_s11_end`;
  - `logs/tk_1-2_s11.inputs.txt` = round 1's 1-2 rows UNCHANGED (Barbarian is deterministic): 2-1 control 3,385
    (838 f), state `states/tk_1-2_s11_end`;
  - `logs/tk_2-1_s11.inputs.txt` = a12r3's 2-1 v1 rows UNCHANGED: they still replay without a desync 44 f earlier
    (no new NesHawk conflict hurt them): 2-2 control 6,349 (2,964 f), state `states/tk_2-1_s11_end`, hp 16, ninpo 0,
    J&S. Power-on history to 2-2: `states/tmp/tk_hist22n.inputs.txt` (6,349 rows; NesHawk trace logs/tk_hist22n.trace.csv).
* 2-2 on the new line (rows after `tk_2-1_s11_end`, all legal by construction, judged on the full list):
  - room 6 thrower: `work/tk/slashsearch.py` from the TAS-follow rows (t1 partial rows 0-99, X 825 in the air):
    B at +0 (kills the jetpack ninja), keep Left to +20, B at +38 (kills the knife thrower), jump at +30 ->
    X <= 680 on the platform at f 6,556 (t 207, TAS t 205), hp 16: `states/tmp/tk_n22r6_ssa.inputs.txt` (207 rows).
    The old line lost 170 f here.
  - room 6 rest: beam (TAS ref, lazy follow) -> room 7 at t 722 (TAS 619): the beam took 4 hits and broke no ninpo
    lantern (lazy following does not copy the TAS's lantern slashes); J&S kept.
  - room 7 (the TAS goes left at the top with U+D+L / L+R; the record drops RIGHT to the lower floor and runs left):
    A* `pos:7:960:192:30` = ['JOLA20','JLR8','JRR0','JNR20'] (144 f after entry), then the old line's record-ref
    beam rows grafted (in sync to X ~200), record-ref beam to the exit chimney, A* `room:8` from a cling on the left
    wall at (59, 101) = ['C8','C9'] -> room 8 at f 7,953.
  - room 8 start: Ryu starts clinging in a chimney (x 48-79) left of a pillar (x 64-95, top y 160); the camera only
    scrolls once Ryu has been at screen x >= 127 (the TAS crosses the pillar inside it with L+R to get there).
    Legal: A* `pos:8:1900:192:12` = ['JOLA20','R4','JOLT4','C8' x5,'JORA12','R16','R8','JRN0'] + Right x16 -> camera
    engaged at f 8,126 (TAS 7,456). Rows `states/tmp/tk_n22_r8cam.inputs.txt` (1,777 rows after tk_2-1_s11_end).
  - room 8: hybrid-ref beam (m2) from the engaged camera to the stage end: **2-2 VERIFIED `logs/tk_2-2_m2.inputs.txt`
    6,349 -> 2-3 control 9,797 (3,448 f, TAS +553, record +347), hp 10, ninpo 0 (the lazy TAS follow copies the
    TAS's J&S spins and spends the two +5 pickups; the +10 at X 1088 was never broken: a slash/jump grid
    `work/tk/slashsearch.py --np 10` from X 1184 found no way to get it), state `states/tk_2-2_m2_end`.
* 2-3 Bomberhead sword-only (0 ninpo): slot 7 (type 24, pose 74/75, half-width 10, height 40, HP = $66) walks right
  0.5 px/f; the sword reaches him from 11-41 px away without contact. `work/tk/bh2.py` grid (approach Left w, then
  [crouch slash cycle Down|Down+B|B|-|- x m, Right x r, Left x 2] repeated to back off as he walks in): best w 60,
  m 1, r 9 -> boss 0 at row 371 -> **2-3 VERIFIED `logs/tk_2-3_bh2.inputs.txt` 9,797 -> 3-1 control 10,902 (1,105 f,
  TAS +275, record +272)**, hp 16, ninpo 0, no weapon, state `states/tk_2-3_bh2_end`, history
  `states/tmp/tk_hist31n.inputs.txt`. With J&S + 10 ninpo the TAS-pace kill exists (boss 0 at +81 rows,
  `states/tmp/a56r2_tk_2-3_tasprobe.inputs.txt`, RNG-independent): getting 10 ninpo in 2-2 room 8 is worth ~270 f.
* Lessons (round 4): (1) every room of 2-2 has a spot where the TAS uses L+R / U+D or a ninpo spin and the generic
  beam stalls for 100-400 f; small targeted searches (slashsearch / wbrute grammars / A* with a near goal) solve
  them in minutes once the geometry is read (`work/tk/tiles.py` prints the $300 collision map around Ryu,
  `work/tk/snap.py` the hitboxes); (2) camera engagement: in rooms entered at a scroll limit the camera only follows
  after Ryu reaches screen x ~127 (2-2 room 8); (3) A* goals far away are slow (5-15 s per expansion); give it the
  nearest stable spot past the obstacle; (4) the lazy TAS follow copies the TAS's sub-weapon spins (ninpo drain) and
  never its lantern slashes once out of exact sync - plan ninpo explicitly (items.plan) and force lantern breaks.

## Round 5 (chain) (agent c5, 2026-10-23 04:45-06:00, PAUSED by the owner)

* STATUS: verified chain unchanged (3-3 control 15,140). NesHawk trace of it: `logs/c5_to33.trace.csv` (pads for
  exact Mesen boots: `python work/c5/mboot.py logs/tk_to33.inputs.txt logs/c5_to33.trace.csv <frame> <name>`).
  Mesen states: `states/mesen/c5_22c` (2-2 control 6349), `c5_22t207` (6556), `c5_r6c` (6753), `c5_33c` (15140),
  `c5_33m1` (15139, one row before 3-3 control).
* 2-2 room 6: segga (`work/c5/segga.py`, goal X<=384) from t 207: X<=384 at t 404 (old 437, TAS 392, -33 f), hp 16,
  ninpo 5 (breaks the +5 lantern). Rows: `states/tmp/c5_p22_prefix.inputs.txt` (404 rows after tk_2-1_s11_end);
  NesHawk replay matches -> `states/c5_22t404` (frame 6753), history `states/tmp/c5_h6753.inputs.txt`.
* Room 6 rest (X 384 -> room 7) is crowded (types 07/01/11); the OLD rows do not get through from the earlier time.
  segga with X progress was at X 65 after 10 min (no room 7 yet); the NesHawk hybrid beam from c5_22t404 (tag c5b)
  was at t 724 room 6 X 89 when stopped. Both killed at the pause; nothing kept.
* Loss map 2-2 vs TAS (trace first-reach): room 6 +12 at X640, +45 X384, +78 X128, +103 room 7; room 7 +252 (start
  detour right/down: entry -> X 704 takes 347 f, record ~250); room 8 +198 (record ~+75). Ninpo for 2-3: room 8
  +5 (1616) +5 (1552) are on the line; do not spend them (no Up+B).
* Resume: `python -u work/c5/segpipe.py work/c5/p22_spec.json` (run with run_in_background; segments room:7,
  x:7:le:704, room:8, x:8:le:1664, x:8:le:1024, x:8:le:384, stage; ~3 h) and/or
  `python -u -m ng.solve.beam 2-2 tk_2-1_s11_end --history states/tmp/tk_hist22n.inputs.txt --prefix
  states/tmp/c5_p22_prefix.inputs.txt --prefix-frames 404 --ref hybrid --width 8 --chunk 8 --hours 1.5 --tag c5b`;
  then `python -m ng.solve.verify finish 2-2 tk_2-1_s11_end states/tmp/tk_hist22n.inputs.txt <rows> c5_2-2_x`,
  2-3 = graft `states/tmp/a56r2_tk_2-3_tasprobe.inputs.txt` (needs J&S + 10 ninpo; press Left on the last
  pre-control row like the TAS), then re-beam 3-1 / 3-2 (enemies follow the global frame counter: old rows desync).
* Free frame per stage: the TAS already holds the direction on the last pre-control row (Ryu moves 1.5 px before
  control); our to_control tails leave it blank.

## 1-1 lock round (repair) (agent "repair", 2026-10-23 21:00-23:10)

**Result: `logs/l11_rep_r1_poweron.inputs.txt` (power-on, 2,474 rows) = 1-2 control 2,474, 1-1 = 2,300 f = TAS +6,
record -9.8 (old best 2,373 / +63).** Exit hp 15, ninpo 10, J&S (133). NesHawk `verify finish` + `verify chain
l11_rep_r1_chain` (two power-on replays MATCH, RAM sha1 f9dd2f174249) + judge PASS. Stage rows `logs/l11_rep_r1.inputs.txt`,
end state `states/l11_rep_r1_end`, results.json entry. Look-ahead: `logs/tk_1-2_s11` replays unchanged from it
(`verify stage 1-2 l11_rep_r1_end ...`): 838 f, 2-1 control 3,312, hp 16.

### Where the old line (tk_1-1_s11, TAS +79) lost (Mesen first-reach per 32 px vs the TAS)
| segment | old | new (r1) | why |
|---|---|---|---|
| X 0-960 | +0 | +0 | identical to the TAS (legalized rows) |
| pole 1, X 960-1104 (TAS t 618-719) | +24 | +4 | TAS: pole double jump-off with 1-frame L / U+D+L. Legal: B slash at 784 (rflags 12 lets Ryu pass INTO the pole), Right to 798, Left 2 (cling at 801 on the pole's right side), Right+A 1 frame = jump-off (held pad must be exactly A+Right), Left 4 (drift back, re-cling), A+Right = 2nd jump-off -> clears the building top (y 144) |
| X 1104-1536 | +2 (hit at pole 2) | +1 | pole 2 (TAS 1166-1167, 1-frame L+A then R+A): Left 2, A+Right 1, B+Right 2 (kills the enemy the TAS slashes) |
| X 1536-2784 | +0..+1 | +1 | legalized TAS rows in sync; X ~2185: a type-3 club guy on the y-80 roof hits a 6-f-late Ryu -> jump 3 f earlier (relative) + retimed jumps (mbrute) |
| X 2784-exit | +52 (3 hits; only 10 ninpo left, the old line spent 2 extra spins at X 2185 / 2435) | +0 | arrive with 20 ninpo; two J&S spins like the TAS (brute-forced timings) |
| exit -> 1-2 control | 279 f | 279 f | fixed (127 f timer tally + load + cutscene) |

### How it was built (all on Mesen, then NesHawk)
1. Pole 1: `work/rep/mbrute.py` (Mesen grammar brute force, Enforcer-legal) from `states/mesen/rep_760.mst`
   (= base rows to frame 760): `Right:20;A+Right:2;Right:1;B+Right:2;Right:13;Left:2;Right:1;A+Right:1;Left:4;A+Right:1;
   Right:26;A+Right:2;Right:2;B+Right:2;Right:33;B+Right:2` -> X>=1104 at 897 (TAS 893), np 30.
2. Legalized TAS rows from TAS 891 (`work/rep/mfollow.py`) in sync to pole 2; pole 2 mbrute from frame 1138
   (`Right:13;A+Right:2;Right:16;Left:2;A+Right:1;B+Right:2`); TAS rows from TAS 1184 to frame 1600.
3. 1600-1823: mbrute over 4 jump timings (`Right:18;A+Right:2;Right:46;A+Right:2;Right:38;A+Right:2;Right:62;A+Right:2`),
   X 2480 at 1823 (TAS 1817), hp 15, np 20. TAS rows from TAS 1816 to frame 2030.
4. 2030-exit: mbrute `Right:11;A+Right:2;Right:20;B+Right:2;Right:22;A+Right:2;Right:22;B+Right:2` (two spins), X 3031 at 2190,
   exit 2195 (TAS 2189). NesHawk conflicts at 925, 941, 1476, 1595, 1596, 2008: all harmless (NesHawk = Mesen, every frame).
* Tools (new, `work/rep/`): `mbrute.py` (grammar brute force on FastPool; keep `--chunk` <= 48: chunk 64 x 230 rows HUNG
  both Mesen workers idle), `mrand.py` (random window search), `mfollow.py` (legalized TAS rows after power-on rows,
  first divergence, `--keep N --out`), `tryseq.py` (print a fixed sequence's trace with coll/rflags), `gram.py`,
  `trace.py` (first-reach table vs TAS), `sbs.py` (side by side from trace csvs), `mtiles.py` (collision map +
  enemies at a frame), `nhcmp.py` (NesHawk trace vs Mesen replay + conflict list).
* Wall facts measured here: `coll` 128 = Ryu overlapping the pole (no grab); grab (coll 12, anim 10) comes on the 2nd
  frame of Left from just right of the pole; jump-off (coll 192) on the frame the held pad is exactly A+Right. The
  TAS's 2-frame double jump-off cannot be legal (Left/Right/A periods 5): 2nd jump-off >= 8 f after the 1st.
* Remaining loss (+6 vs TAS): pole 1 +4 (legal jump-off spacing), pole 2 +1, +1 near X 1920. A segga run (10 min,
  `rep_pole9`) found nothing faster for pole 1. Any earlier frame saved shifts `$BF` for everything after it and
  needs steps 2-4 redone (~1 h with these tools).
* Resume: `python -u work/rep/mbrute.py <hist> <mst> "<grammar>" "x:0:ge:<X>" <tag> --minhp 15 --npmin 20 --chunk 32`
  per segment; `python -u work/rep/mfollow.py <power-on rows> <TAS k0> <n> [--keep n --out f]`; finish with
  `python -u -m ng.solve.verify finish 1-1 a12_intro_174 logs/a12_intro.inputs.txt <1-1 rows> <out>`.

## 1-1 lock round (roof) (agent "roof", 2026-10-23; stopped by the coordinator: 1-1 locked on repair's 2,300 f line)

Nothing verified or recorded: everything here was found on Mesen only. Tools are in `work/l11r/`:
* `trace.py`: column first-reach times compared with the TAS.
* `look.py` / `amap.py`: the $300 collision map in absolute X. Ring column = (X//16)%32, and $5F = 6*((scroll//16)%32) (checked). The map starts at y 64.
* `try.py`: plays row specs like 'RA:2 R:10' on top of a base file, legalized.
* `mkseed.py`: writes the history file, the Mesen state and a seed.
* `segga.py`: the c5 GA with a new goal `z:GX:YMAX[:YMIN]` (X >= GX and y <= YMAX; progress counts both x and height), and an adaptive chunk size.
* `segpipe.py`: the l11 copy of the c5 segment pipeline.

Index t below = row index after 1-1 control (BASE = logs/tk_1-1_s11, which is TAS-identical to t 619).

**Mesen batch crash:** keep each worker's run_batch reply under about 64 KB (record='all' with about 600 rows per worker). Above that, Mesen closes the socket (WinError 10054) or hangs idle. `lib.run_all` sizes the chunks for this.

**Geometry (absolute X)**
* Sale sign platform: y 160, X 672-703. Ryu can stand on it with x 656-720.
* Hanging block: X 656-671, y 96-127.
* Shop roof: y 96, X 704-831. Ryu walks off it at x ~848.
* Pillar: kind 1, X ~880-895, y 64-191. There is a passage under it at y 208.
* GO sign top: y 128, X 944-959.
* Platform: y 144, from X 992.
* Lanterns: +10 ninpo at X 656 y 144 (the TAS slashes it at t 399). A Star at X 752 y 80 sits above the roof (don't pick it up).

**Movement facts**
* The jump is a fixed 48 px. Holding A longer does nothing.
* Reversing direction in the air moves Ryu at ~0.5 px/f.
* A ground slash freezes Ryu for ~12-16 f. An air slash costs nothing.
* Pressing A on the frame Ryu touches a wall face (RAM `coll` != 0) is an instant wall-kick of ~15 px. No visible cling is needed.

**Roof route (Mesen)**
1. t 421: R+A from the ground.
2. Land on the sign at x ~684 (t ~438), then L+A.
3. R+A kick off the block face at x ~682, y 134 (t 448), and again at x 680, y 117 (t 456).
4. Land on the roof at X 703 at t 470 (record ~466, TAS passes X 703 at 446).
   Rows: `work/l11r/b_r2.txt` (rows from control, GA r2).

**Club enemies on the roof**
* Club 1 (slot 5, type 3) is at X ~742. Jump at t 476 (R+A) and press B at 478: an air slash kills it with no stop.
* Club 2 (slot 4/7) is at X ~817 at t 521. A second jump at ~519 with B at once also kills it, but landing after that slash froze Ryu at X 776 for t 521-534 (~13 f lost). Avoid that landing.

**Pillar**
* A jump from the roof end lands on nothing; Ryu falls to y 208 (the TAS's low route).
* Jumping at x ~838-847 (apex y 48) bumps the pillar top at x 892, y 74 (anim 10). Holding there is a dead state where A does nothing.
* R+A on the contact frame (t 612 in `b_r4`) wall-kicks over the top and lands on the GO sign at x 949, y 128 (t 651; record ~630).
* Walking on from there reaches X 1003 at 687 and X 1024 at 701 (TAS 649 and ~663).

**Conclusion:** the roof line costs about +24 vs the TAS just to climb onto the roof (X 703 at t 470 vs 446). After that the record runs at a constant 1.5 px/f, so even with no stalls the roof line ends at about TAS +19 at X 1003. The repair agent's legal pole jump-off (TAS +6) beats it. Not worth resuming.

## 1-2 lock round (agent l12, 2026-10-24)

Start: locked 1-1 `logs/l11_rep_r1_poweron.inputs.txt` (1-2 control 2,474, hp 15, ninpo 10, J&S, `$BF` 161). Baseline
`logs/tk_1-2_s11` = 838. Tools: `work/l12/` (`lib.py` Mesen pool at the 1-2 control from NesHawk pads of
`logs/l12_base.trace.csv`; `g1.py` one-jump grid, `g2.py` landing-frame inputs, `g3.py`/`g4.py` grids with Right on
the last locked rows, `nhtry.py` NesHawk trace of Mesen candidates, `mkstate.py` NesHawk state from a power-on file).

* Post-kill is fixed: kill -> cutscene flag (cs) 593 f (timer tally = 3 f per remaining timer second, the timer was 149
  in both runs), then Start. The old rows pressed Start 3 f after the first skippable frame; `verify finish` on the
  same kill rows picks the earliest one -> **836** (`logs/l12_s1_poweron.inputs.txt`, verified, judge PASS).
* Kill floor with the locked rows: the J&S spin first hits Barbarian at Ryu x >= 140, i.e. offset 72 (Ryu walks from
  x 32 at the control frame, 1.5 px/f, no faster way); one jump's spin gives at most 12 hits (the vertical window;
  jump 30-55 x B 58-77 grid), so two spins with one landing frame between them: 72 + 16 = kill at 88. No landing-frame
  input combination (2,448 candidates) hits on the landing frame. -> 836 is the floor without touching 1-1.
* The TAS's last 2 f: it holds Right on 1-2 control-1 and control (gmode 7 still, Ryu already moves), our locked 1-1
  file has blanks there. With Right on rows 2473-2474 (same control frame, same `$BF`, Ryu x 35): first hit at 70,
  kill at 86, **834 = TAS** (`logs/l12_v2_poweron.inputs.txt`, verified, judge PASS). Needs the coordinator to accept
  changing those 2 locked rows. Note: the first variant (turn Left on offset 79) hit a NesHawk DMC conflict on frame
  2,553 (Left read as Right -> no second spin); turning on offset 78 avoids it.
* Both exits: hp 16 (2-1 start), ninpo 0, J&S (two spins = 10 ninpo; a 5-ninpo kill needs 4 sword hits after a 12-hit spin, not tried - it cannot beat kill 88/86). Look-ahead: 2-3
  Bomberhead needs 10 ninpo, available on the 2-2 TAS line (room 6 +5/+10, room 7 +10, room 8 lanterns).
  `$BF` at 2-1 control: 226 (836) / 224 (834).

## 2-1 lock round (wall) (agent "wall", 2026-10-24 00:55-04:30)

**Result (both NesHawk `verify finish` + `verify chain` two replays MATCH + judge PASS, in logs/results.json):**
* `logs/l21_wall_w1_poweron.inputs.txt`: 2-2 control **6,130**, 2-1 = **2,822 f = record -82.8, TAS +20**, hp 16, ninpo 5, J&S, `$BF` 230.
* `logs/l21_wall_w2_poweron.inputs.txt`: 2-2 control 6,131, 2,823 f = record -81.8, hp 16, **ninpo 10**, J&S, `$BF` 231
  (w1 + one J&S spin that breaks room 3's +10 lantern; 2-3 Bomberhead wants >= 10).
* Room 2 is the follow agent's `work/l21f/s_f2.txt` (room 3 change at 4,280 = TAS +9). Rooms 3-5 are mine.

### Legal climb rhythms (measured on Mesen, `work/w21/cycles.py` = every repeating cycle with runs >= 2, A/Up patterns)
All 2-1 climbs (room 2's exit wall, room 3's pillar and exit, room 4's start) are LADDER tiles (kind 9; coll 32 =
"steps"; on steps only the held pad A+Left = $82 jumps off, Up climbs 1 px, anything else holds on).
| cycle (ladder on the right) | px/f | note |
|---|---|---|
| TAS `R+A, L+A, -, -, -` (1-frame R/L: banned) | 2.0 | re-grab frame = R, jump-off next frame, never clings |
| **`R, R+U, R+U, A+L+U, A+L`** (or `U+R, U+L, A+L, A+R, R`) | **1.8** | legal; the grab frame (A+L+U) also climbs 1 px; 9 px / 5 f |
| `L, A+L, A+R, R, R` | 1.6 | grab frame = L (hold on), jump-off frame does not rise |
| C8 `A+L x2, R x6` | ~1.55 | |
| old 7-frame (`A+away x2, back x5`) | ~1.1 | |
* Why not 2.0: the frame after a jump-off must still hold Left (hold >= 2) unless Left started on the grab frame; a
  grab frame with Left = "hold on", and the jump-off frame after a hold-on frame does not move vertically.
* The ladders end below their platform: room 4's ladder stops at y 178 (platform y 160), the pillar's at ~146 (top y 128):
  a jump-off at the top rises only ~7-15 px, so both rooms still need the TAS's floor/ledge detours.
* The contact-frame wall kick (1-1 roof lead) is the same jump-off: held pad exactly A+away on the frame `touching` is set.

### Room by room (frames vs TAS; our line arrives in room 3 at TAS +9)
| part | rows | vs TAS | how |
|---|---|---|---|
| room 3 pillar (room change -> pillar top X 170 y 128) | 124 (`work/w21/p3c2_best.txt`) | +7 | 19 blank, `R RU RU ALU AL` x9, Left 24 to the ledge (118,160), R 1 (turn), A+R, R (`work/w21/p3c.py` grid; starts/ninpo variants `p3d.py`, `p3e.py` found nothing faster) |
| room 3 rest | 683 legalized TAS rows from TAS 4388 (`work/w21/r3f_rows.txt`) | +0 | in sync to TAS 5071 (2 px behind from X ~390, harmless; the thin post is passed) |
| room 3 exit ladder | 13 (`work/w21/p3x_best.txt`) | +4 | `RU:2 ALU AL R RU:2 ALU AL R RU:2 ALU` (`work/w21/p3x.py`) |
| room 4 (no enemies; graft at room change +20) | 105 (`work/w21/r4_rows.txt`) | +6 (old 186 = +67) | `-:3 U:2 A+L:2 L:13 R A+R:2 R` -> right platform (159,160) at row 43; `L A+L:2 L:27 -:2 R:4 A+R:2 R` -> y-128 floor, turn, jump right -> room 5 at row 105 (`mbrute` r4a/r4b) |
| room 5 | legalized TAS rows from TAS 5199 (`work/w21/r5f_rows.txt`) | +0 | in sync to the exit |
* Room 2's exit climb from the TAS state at 4206 (`work/w21/p2k.py`: jump, pole kick `L:3 A+R:1`, U-cycle) reaches
  room 3 at TAS +7; the follow agent's own room 2 does it at +2 from the same point, so theirs is used.
* Ninpo: the TAS's Up+B spin on the pillar ladder (4296) is what later breaks room 3's +10 lantern at X 272 (at TAS
  4419); without it we exit 2-1 with 5. A spin is legal only without Left/Right on its frame; in the U-cycle every
  frame needs a direction, so w2 places it at pillar rows 122-123 (`Up+B`, `Up+B+Right`) just before the pillar-top
  landing (-1.5 px) and replays TAS rows from 4387 (one row earlier) to stay in sync: +1 f, ninpo 10 at the exit.
  Any other placement lost 2 px and hung on the thin post at X 363.

### Tools (`work/w21/`)
`try.py` (play a spec 'RA:2 -:3' from a .mst, per-frame trace), `amap.py` (collision map on screen columns via $E7CC +
$5F, absolute X), `cycles.py` (climb-cycle enumeration), `wlib.py` (spec/legalize/search helpers), `follow.py`
(legalized TAS rows after a .mst, first divergence, `--out f --all`), `mk.py` (power-on rows [+ NesHawk trace] -> .mst),
`mktas.py` (TAS state .mst), `mkst.py` (play rows, save .mst), `fullsim.py` (2-1 rows from control: room changes),
`p3c.py`/`p3x.py`/`w2build.py` (pillar / exit / spin variant), `fbfs.py` (frame-level legal BFS: works but too slow
for whole rooms, ~150 evals/s, and Mesen occasionally drops the socket; prefer grammars).

### Resume (a different room-3 arrival, e.g. a faster room 2)
1. `python work/w21/mk.py <power-on rows to the room-3 change> <its NesHawk trace|-> states/mesen/x_r3.mst`
2. `python -u work/w21/p3c.py states/mesen/x_r3.mst <hist> work/w21/x_p3.txt` (edit the `pre` list to -:18..-:20)
3. play it (`mkst.py`), then `python -u work/w21/follow.py <hist+p3> <mst> 4388 683 --out x_r3f.txt --all` (try k0
   4386-4389 if not in sync), `p3x.py` for the exit, then 20 blank rows + `work/w21/r4_rows.txt`, then
   `follow.py ... 5199 625` for room 5; drop a trailing 1-frame Up; `python -m ng.solve.verify finish 2-1 ...` and
   `verify chain`.

## 2-1 lock round (follow) (agent "follow", 2026-10-24 00:20-04:55)

**Results (both NesHawk verify finish + verify chain MATCH + judge PASS):** `logs/l21f_fol_v4_poweron.inputs.txt` = 2-1 in
**2,822** f (2-2 control 6,130, record -82.8, TAS +20), exit hp 16 / ninpo 10 / J&S, `$BF` 230. Faster but ninpo 0:
`logs/l21f_fol_v3_poweron.inputs.txt` = 2,818 (6,126, record -86.8, `$BF` 226).

| segment (TAS frames) | lag vs TAS at the end (start lag 6) | record - TAS | how |
|---|---|---|---|
| room 2 to the club guy (3302-3560) | 7 (+1) | 0..+8 | legalized TAS rows (`work/l21f/follow.py`) + mbrute jump/B (club guy) + 2nd B for the +5 lantern |
| room 2 to the pole (-4205) | 7 | | TAS rows in sync |
| pole double jump-off + exit wall (4205-4271) | 9 (+2) | | pole: `L+A, L+A, A+R` (segga), wall: `fbeam` room:3 (room 3 at 4,280); NesHawk-clean at width 128 |
| room 3 start climb + ledge (-4354) | | | `fbeam --score tas` (cycle `A+L, L, -, B+R, A+B+R` = 2 px/f); first beam (4,362) hit a harmful NesHawk DMC conflict at 4,319, re-beamed at other widths: clean landing 4,364 |
| ledge turn + pillar jump (-4388) | 13 (+4) | | legal turn needs `Left*4, Right*2, A+Right` (TAS jumps on the landing frame with L+R); v4 adds Up+B at 4,400 (+10 lantern) and +1 Right |
| room 3 TAS rows (4388-5071) | 14 | +54..+100 | in sync (J&S spins as the TAS) |
| room 3 exit (-5080) | 20 (+4..+6) | | fbeam room:4 `--npmin 10` (B-cycles here spend spins) |
| room 4 (5080-5199) | 26 (+6) | +103 -> +118 | 125 f from the room change (beam rows v3 / wall agent's rows v4) |
| room 5 (5199-5825) + tally | 26 | constant | TAS rows in sync |

* Biggest remaining losses: room 4 (+6, two legal turns on ledge edges), room-3 ledge turn (+4), room 3 exit (+4..6),
  room 2 end climb (+2). Mesen DMC conflicts: slashes play DMC samples, so conflicts cluster in B-heavy climbs.
* Tools `work/l21f/`: `lib.py` (Mesen core at 3,308 from NesHawk pads `logs/l21f_base.trace.csv`), `follow.py`
  (prefix + legal TAS rows, divergence), `fbeam.py` (frame beam; see LOCKED_CHAIN agent notes), `mkst.py` (Mesen state +
  history at a row), `addg.py`/`cat.py`/`variant.py`/`troom.py`, `nhseg.py` (NesHawk segment check from a NesHawk state:
  conflicts + first diff; states `l21f_f2_972`, `l21f_k5_1757`), `nhcheck.py` (from power-on).
* Resume: `python -u work/l21f/fbeam.py <hist> <mst> room:4 tag --zt 1179:80 --width 96 --npmin 10`;
  `python -u work/l21f/follow.py <stage rows> <TAS k0> <n> --out f`; `python -u work/l21f/nhseg.py <rows> <n0> <NesHawk state>`;
  finish with `python -u -m ng.solve.verify finish 2-1 l12_v2_end logs/l12_v2_poweron.inputs.txt <rows> <out>`.

## 2-2 lock round (follow) (agent "follow", 2026-10-24 ~05:00-07:10, PAUSED by the owner)

**No verified 2-2 candidate yet.** Confirmed partial (Mesen + NesHawk power-on trace `logs/l22f_p3b.trace.csv`: 0 DMC
conflicts, NesHawk = Mesen): `work/l22f/p3b.txt` = 711 stage rows from 2-2 control 6,130 -> frame 6,841 = TAS 6813 + 28,
hp 16, ninpo 5, J&S, top of the room-7 tower (X 842, y 80). Room 7 spawn at frame 6,772 (row 642).

| segment (TAS frames) | lag vs TAS (start 26) | how |
|---|---|---|
| room 6 (6104-6707) | 28 (+2) | legalized TAS rows from TAS **6102** (TAS 6102 has our X: the TAS already moves on its pre-control row) replay in sync, both spins and the +10 lantern as the TAS (`work/l22f/f0.txt`) |
| room 6 exit (6707-6723) | 28 (+0) | `work/l22f/s_r6k.txt` (41 rows from row 580): fbeam with air slashes B+Left/B+Right (keep facing left) dodging the type-7 jumper |
| room 7 start (6723-6813) | 28 | legalized TAS rows in sync (U+D+L on the ground legalizes fine) |
| room 7 top (6814-) | open | TAS rows U+D+L in the air clip through the wall corner at X 836 / ceiling at y 64 (raw move): no legal copy. My beams (`r7a`, `r7b`, `r7t` logs) stall at X 836 (over the top) and X 839 y 128 (under the wall) |

* Room 6 exit mechanics (RAM pokes): the exit tile needs screen x ($86) >= 93 on the frame Ryu reaches y 240 while facing
  LEFT; facing right at x >= 93 grabs the ladder (right shaft wall; from a grab at y 240, Down x11 still exits alive).
  Walking off the y-160 edge, Right does not turn Ryu (0.5 px/f drift). In a fall or jump Ryu cannot turn; only a ground
  turn turns him. Fallback (+17): ground turn + slash on the platform kills both jumpers (`work/l22f/s_r6xk.txt`).
* Tools (`work/l22f/`, copies of `work/l21f/` retargeted to 2-2: `lib.py` HIST = `logs/l21f_fol_v4_poweron.inputs.txt`,
  Mesen boot from NesHawk pads `logs/l22f_base.trace.csv`, TAS_CTL 6104): `fbeam.py` now also prunes deaths (dead flag on
  any frame, item 0, lives drop - the death respawn also sets room 7, so "room:7" alone is not a goal) and has `--ek W`
  (penalty per active enemy, $73); `trial.py` (play a grammar, print states), `tiles.py` (Mesen collision map),
  `ramcmp.py`, `mkst.py`, `follow.py`, `nhcheck.py`, `nhseg.py`, `enem.py`.
* Resume: room 7 from the tower top: `python work/l22f/mkst.py work/l22f/p3b.txt 711 r7t`, then a beam/brute to the TAS
  landing (X ~770, y 128 at TAS 6876 = frame 6904 if lag 28), e.g.
  `python -u work/l22f/fbeam.py work/l22f/h_r7t.inputs.txt states/mesen/l22f_r7t.mst g:7:740:778:128 r7t --score wp --wps <...>`
  (or build room 7 from the spawn at row 642 on the record's route). Then
  `python -u work/l22f/follow.py <rows> <TAS frame> 400` for the rest of room 7 / room 8, `python work/l22f/nhcheck.py
  <rows> <tag>` on NesHawk, and finish with `python -u -m ng.solve.verify finish 2-2 states/l21f_v4_end
  logs/l21f_fol_v4_poweron.inputs.txt <rows> <out>` + `verify chain` + check_inputs.

## 2-2 lock round (puzzle) (agent "puzzle", 2026-10-24 04:35-06:55, PAUSED by the owner)

Nothing NesHawk-verified, no candidate recorded. All numbers are Mesen. Tools and rows in `work/l22p/`.

### Puzzle 3: room 6 exit (TAS 6709-6712 L+R in the air)
* The exit pit is narrow: Ryu only reaches room 7 alive if he crosses y ~240 at x >= ~92 (screen) with no leftward speed.
  At x <= ~86 he lands on the y-192 block left of the pit or clings to its right face. A room-7 change can still happen
  after a DEATH in the pit (lives -1, item `$C9` 0, ninpo 2, Ryu frozen at the room-7 spawn): always check `$C9`/lives ~25 f
  after the change (l22f's first `p1.txt` had this).
* Legal: no input in the air = no horizontal movement (no momentum), so walking off the platform edge (x ~92) and
  releasing Left falls straight into the pit at no cost vs the TAS. On our `$BF` two type-7 enemies at the pit hit Ryu
  there (knock-back to the left = death); the follow agent's `work/l22f/p3.txt` rows 1-638 get through alive (room 7 at
  row 638 = frame 6,768, TAS +45, hp 16, np 5, J&S).
* The room-6 exit x sets the room-7 spawn x (spawn = same screen x, y 88, next to the ladder).

### Puzzle 1: room 7 top (TAS 6744-6876)
* The TAS's line over the right pillar (X 800-831, y 64-144) is NOT possible legally: U+D+L in the air moves Ryu left at
  1.5 px/f while facing right, and walls only block in the facing direction, so the TAS passes through the pillar top.
  Tested and failed: ladder kick A+L from the highest ladder point (Up to y 85; y 84 exits back to room 6) peaks at y 70
  and stops at X 835 (needs ~64); the pillar face is grabbable only from y 81 (the corner tile rows 64-79 make Ryu slide),
  its A+R kick peaks at 66; Left drift does not pass the wall; air slashes (`g_r7b.py`, 288 cands) do not help.
* Legal = the record's route: down the ladder, right on the y-128 floor, walk off its right end (X ~972), land on y 192,
  run left under the right pillar, climb the gap between the pillars (left pillar X ~747-778, top y 128) with a ground jump
  + 2 wall kicks. Real arrival (p3[:638] + 23 blank = spawn+3, frame 6,791):
  `D:9 R:74 L:115` (198 rows, `work/l22p/s7a.txt`, X 828 y 192) + `L:25 AL:2 L:8 AR:2 R:11 AL:2 L:14` (64 rows,
  `work/l22p/x_r7d2.txt`, 2,079-candidate grammar `g_r7d2.py`) -> standing on the left pillar top at frame 7,053 (TAS 6,873:
  lag 180; room 7 top costs TAS +135, about the record's loss there).
* Rest of room 7: `pbeam.py --score tas --lag 180` followed the TAS line exactly (score 0.5) to the exit climb:
  `work/l22p/fb_r7e.inputs.txt` (484 rows) -> room 8 change at frame 7,537 (TAS 7,353 +184), hp 16, np 5.
* Full 2-2 rows control -> room 8 change (Mesen only, 1,407 rows): `work/l22p/p22_to_r8.txt`.

### Puzzle 2: room 8 start (chimney, camera, platform)
* Map (screen = X - 1792 at the start): chimney between the left building wall (x 0-31, from y 128 down) and a pillar
  x 64-95 (top y 160); its left face is a LADDER (kind 9, y 176-240); floor y 192 at x 96-207; one-way platform y 96 at
  X ~1776-1966; ladder at X 1984 (y 80-191). Ryu grabs the chimney ladder by himself 1 frame after spawn.
* Camera: engages once Ryu's screen x >= 127. Fastest legal found (TAS state 7376 = spawn+2, `g_r8a.py`, 912 cands):
  `work/l22p/x_r8a.txt` = `R:2 (RU:2 ALU AL R) x7 RU:2 ALU AL:2` + Right: ladder U-cycle to y 168, kick, drift right onto
  the pillar top, run -> x >= 127 at row 100 (TAS 80: +20; old legal ~+70). Equal option: 6 cycles, kick left to the
  chimney wall (x 39), A+R kick on contact (+21).
* Getting onto the y-96 platform: the TAS (7516) and apparently the record take a DAMAGE BOOST from the type-8 bird (hp -1,
  knocked up from y ~118). Without it only the X-1984 ladder works (~+110). This part needs the real arrival (bird =
  `$BF`-dependent): not done.

### Resume
0. The follow agent's newer room 6 `work/l22f/p3b.txt` (room 7 spawn at row 642, frame 6,772, TAS +28) is 16 f faster than
   p3: rebuild room 7 on it first (re-run `g_r7a2.py` / `g_r7d2.py` with `xsearch.py`, then the `pbeam.py --score tas` run).
1. Mesen state at the room-8 change: `python work/w21/mkst.py states/mesen/l22p_ctl.mst work/l22p/p22_to_r8.txt
   states/mesen/l22p_r8chg.mst` (`l22p_ctl.mst` = 2-2 control from NesHawk pads `logs/l22p_base.trace.csv`), then add 22
   blank rows (fade; the beam drops nodes while `dead` bit 7 is set for 2 f after the spawn).
2. Chimney: `python -u work/l22p/xsearch.py <hist> <mst> work/l22p/g_r8a.py r8real`, then the platform with
   `python -u work/l22p/pbeam.py <hist> <mst> e:1800:90:100 r8b --score r8 --width 64 --frames 200` (score r8 = go to
   screen x 127, then left/up; it hung once at width 96: watch Mesen CPU) or a grammar that waits under the bird.
3. Rest of room 8: `pbeam.py ... stage tag --score tas --lag <lag>`; then `python -u -m ng.solve.verify finish 2-2
   states/l21f_v4_end logs/l21f_fol_v4_poweron.inputs.txt <rows> l22_puz_<tag>` and `verify chain`.
* Tools: `try.py` (spec trace with scroll), `play.py` (rows trace), `xsearch.py` (grammar search with a python goal file),
  `pbeam.py` (l21f fbeam + scores r7/r8/py, goals dx/e), `mapat.py` (ring map: column offset is wrong, use
  `work/w21/amap.py`), `tasdump.py`/`tasrooms.py` (TAS trace).

## 2-2 lock round (art) (agent "art", 2026-10-24 12:20 ->; owns the art/ninpo side and room 8 from the platform)

**Best verified (17:33):** `logs/l22_art_w10_poweron.inputs.txt` -> 2-3 control **9,167** (3,037 f, record -64.1, TAS +142),
exit hp 15 / **J&S (133) + exactly 10**, `$BF` 195; with the last 2-2 row = Left + `logs/l23_t12_va.inputs.txt`:
`logs/l22_art_w10_to31_poweron.inputs.txt` -> **3-1 control 9,993** (bar t12+va 9,998). All verify finish / verify chain
MATCH / judge PASS. = main's `work/l22c/w10.txt` (X 968 at 8,264, J&S/30) + art X-900 beam + exit beam. Earlier: t12 9,172
(t9 prefix), v9b 9,171 (3-1 9,997), v9m 9,169 (3-1 9,995).

### Findings
* **Room 6 that keeps J&S (0 f):** move p3b's Star spin from rows 478-479 to 489-490 (`work/l22a/jedit.py <in> <out>`).
  The spin is there to kill the type-1 walker at the landing (no spin = 2 hits); at X 242 it misses the Star lantern
  (X 256). Positions are identical to the Star line to the room-8 change (NesHawk-checked, `work/l22a/s5j.txt`).
  **But it is the worse base:** with J&S held every needed air B in rooms 6-7 (rows 581/605, 1142, 1272, 1334/1359) is a
  spin, so room 8 starts with J&S/0 instead of Star/20. On J&S/0 the room-8 beam dies at X ~1215 (no spin left for the
  enemy the TAS spins at TAS 7937). Stripping B presses only moves the spin to the next press.
* **Spin rules (bank07 $EC7B/$EE55):** the B handler depends on the d-pad: no direction / Left / Right (also Down+Left,
  Up+Left) in the air = J&S spin while ninpo >= 5; **Down alone + B in the air = the normal sword (free)**; Up alone + B =
  sub-weapon. With ninpo < 5 a B is a normal slash.
* **Room 8 ninpo route (Star line):** free Star air slashes break +5 X 1616 and +5 X 1552 (30). J&S lantern X 1312: the
  `item:133` beam breaks it at X ~1321 y 109 and catches it at frame 8,035 (X 1320). Then the beam spends 7 spins (X 1210,
  1098 [+10 X 1088 caught next frame], 925, 810 [+5 X 800], 645, 511, 366) = 30 + 15 - 35 = **10 at X 366, kept to the
  exit**. The Fire Wheel lantern (X 944) is never caught (the beams prune `$C9` != 133). Exit X 40 at 8,891 (TAS 8718
  +173; X 1399 was TAS +171, so room 8 from X 1400 costs 2 f); 2-3 control 281 f later (TAS 280).

### Tools (`work/l22a/`)
* `abeam.py` = l22f fbeam + art rules: `--items 129,133 --jsby X` (Star or J&S only; J&S required left of X),
  `--keepitem 133` (default), `--need 10` (prune when ninpo + untaken ninpo lanterns ahead < 10; `--lant` list),
  `--npeq 10` (goal ninpo), goal `item:133`, `--npw` (prefer ninpo), writes `fb_<tag>.inputs.txt` or `fb_<tag>_part`.
* `var.py` (play rows with edits, print item/ninpo events), `cmp.py` (two lines, first position difference),
  `ramdiff.py`, `strip.py` (strip B from row ranges), `jedit.py`, `cat.py`, `mkst.py` (-> `states/mesen/l22a_<tag>.mst`).

### Resume
* New prefix (faster rooms 6-8 start) that reaches room 8 near X 1400 with Star/30:
  `bash work/l22a/r8pipe.sh <prefix rows> <tag> [lag]` (J&S pickup beam, X 900 beam, exit beam with ninpo exactly 10;
  ~25 min) -> `work/l22a/<tag>_full.txt`; check the judge on power-on + rows, `python work/l22f/nhcheck.py <rows> <tag>`,
  then `python -u -m ng.solve.verify finish 2-2 l21f_v4_end logs/l21f_fol_v4_poweron.inputs.txt <rows> l22_art_<tag>`
  (start name WITHOUT `states/`), power-on file = history + `logs/l22_art_<tag>.inputs.txt`,
  `python -u -m ng.solve.verify chain <name> <power-on file>`.

## 2-2 lock round (r78: room 7 + room-8 camera/bird) (agent "r78", 2026-10-24 11:10-16:00)

Continues the follow + puzzle rounds above on the follow agent's room 6 (`work/l22f/p3b.txt`, Star line). Room 8 from
X ~1400 is the art agent's. All rows below are 2-2 stage rows from control 6,130, NesHawk power-on traces match Mesen
(`nhcheck.py`), judge PASS. Best prefix: **`work/l22c/w9.txt`** (X 1400 at 7,976, Star + 30, hp 15) /
**`work/l22c/w10.txt`** (+ legal TAS rows through the J&S catch: X 968 y 192 at 8,264, J&S + 30). First verified 2-2
candidate (art, on my older t9): `logs/l22_art_t12_poweron.inputs.txt` = 3,042 f (record -59.1).

| part (TAS frames) | lag at the end (start 26) | 2-2-local vs TAS | record - TAS (local) | how |
|---|---|---|---|---|
| room 6 (6104-6744 spawn) | 28 | +2 | ~+5 | follow's p3b (TAS rows + exit fbeam) |
| room 7 top: spawn -> left pillar top (6744-6876) | 137 | **+109** | ~+110..131 | `R:1 DR:1 D:9 R:28 AR:2 R:41 L:101` (x_c7a2: jump at X ~900 so Ryu turns on the floor block's corner at X 967 and lands on y 192 running left; X 828 at spawn+183, the old run took 199) + gap-climb beam 58 rows (`fb_c7b`, grammar best 64) |
| room 7 rest (6876-7353) | 141 | +4 | | legal TAS rows in sync; the type-1 walker at X ~341 killed by B on TAS-follow rows 280-281 (from TAS 6877); fbeam `--freeze 7315` (NesHawk DMC conflict ate an A press) +1; exit ladder 38 rows (TAS uses A presses 3 apart: +3) |
| room 8 start: spawn -> y-96 platform (7374-7543) | 165 | +24 | +165..197 at entry | chimney U-cycle (no blank rows after spawn) + run right to X 1926 (engages the camera) + bird damage boost, `x_w8.txt` |
| room 8 to X 1400 / X 968 (7543-8098) | 166 | +1 | ~+200 constant | TAS rows (lag 165-166) + fbeam past the X-1477 hit (no loss) + TAS rows through the J&S catch |

### Room 7 top (why +109 is about the floor)
* The TAS crosses the right pillar (X 800-831, top y 64) moving left at 1.5 px/f while FACING RIGHT (kick A+R off the
  pillar face at 6816 with U+D+L keeping the old x speed): walls only block the facing direction. Legal leftward motion
  while facing right is only the 0.5 px/f back drift (too slow) or a knock-back, and no enemy exists near the pillar
  (checked: none spawn while Ryu waits at X 839 for 200 f). So the record's route under the pillar is forced: X 859 ->
  ~967 -> 828 at full speed is ~177 f minimum + the ladder; we use 183, then 58 for the 64-px climb (2 kicks).
* Phase-1 trick: jump on the y-128 floor at X ~900 (R:28 after the ladder) and switch to Left in the air: Ryu touches
  the floor block's right corner at X 967 (coll 4), turns, and drops to y 192 already running left (12 f faster than
  running off the edge; a wall kick off the right wall X 988 is slower).
### Room 8 bird boost (mechanics, measured on our arrival)
* The type-8 bird spawns when the scroll reaches 1776 = when Ryu, with the camera engaged, crosses X 1903 leftward. It
  spawns at X 1791, ~12 px ABOVE Ryu's y at that moment, at the top of its sine (amplitude ~36 px, period ~46 f) and flies
  right ~0.9 px/f. Knock-back goes AWAY from the enemy, so the bird must hit from Ryu's right; the hit must be at feet
  y <= ~125 so the 29-px boost clears the y-96 platform.
* Recipe (TAS geometry): engage the camera on the floor at X ~1926, turn, jump (A+L) so Ryu crosses X 1903 near the jump
  peak (y ~151), land on the pillar top (y 160), jump again at once: the bird rises into Ryu at X ~1827 y ~115, 46 f after
  it spawned. `R:62 L:1 AL:2 L:32 AL:2 L:53` after the chimney (grammars `work/l22c/g_c8b.py`, `g_c8d.py`, `g_c8e.py`).
  Without the engagement detour there is no bird; jumping from the floor at X < ~1924 makes it spawn too low (no boost).
* Remaining +24 = the legal engagement detour (TAS walks through the pillar with L+R and reverses in the air).
### Room 7 exit ladder
* Needs three A presses (wall kick at X 72 y 112 on the contact frame, ladder grab, jump off the ladder top); legal
  spacing 5 (TAS 3-4). Any A press in the air before the kick (the beams like them) delays the chain: the 38-row spec has
  none. `L:3 AL:2 L:17 RU:2 ALU AL - BR BRU ALU:2 L R RU ARU AR` from X 108 y 160; the B+Right slash after the kick is
  required (without it the grab fails).
### NesHawk notes
* DMC pad-read conflicts after slashes ate an A press twice (7,315 in room 7, 7,914 in room 8): re-beam that segment with
  `--freeze <frame>`. A 1-frame button at the end of a beam segment fails the judge (hold >= 2): extend it one row.
### Tools (`work/l22c/`)
`tr.py` (compact spec trace), `ev.py` (first row meeting a goal, many specs), `en.py` (enemies along a spec, `--short`),
`tasen.py` (enemies on the TAS), `bslash.py` (TAS rows with B added on given rows), `addspec.py`, `join.py`, `fbeam.py`
(l22f fbeam + `--item N` keep the art, `--prunenp` with `--npmin`), `r8tail.sh` (art pipeline stages b+c).
### Resume
1. Prefix through room 7: `work/l22c/w3b.txt` (1,385 rows = to the room-8 spawn, frame 7,515).
2. Bird: `python work/l22f/mkst.py <rows> <n spawn> tag; python -u work/l22p/xsearch.py work/l22f/h_tag.inputs.txt
   states/mesen/l22f_tag.mst work/l22c/g_c8e.py tag` (the same rows have worked on 4 different arrivals).
3. `python -u work/l22f/follow.py <rows> 7543 400` (try k0 +-2) to X ~1490, then
   `python -u work/l22f/fbeam.py ... x:8:le:1400 tag --score tas --lag <lag> --minhp 15 --npw 2`, `nhcheck.py`, then
   follow TAS from 7810 through the J&S catch, then the art agent's room 8 (`work/l22a/r8pipe.sh` stages b+c).
* Lessons (16:00-17:30): (1) the exit goal must be **landed** at X 40 (`g:8:0:40:192`): reaching X 40 in the air (y 144)
  waits for the landing and cost 14 f at 2-3 control (`l22_art_v9`). (2) The beam's spins are greedy: with exactly-10 the
  room has only 7 spins after the J&S; on v9 the beam spent one on the X-800 lantern (X ~833) and then lacked one at the end
  (X ~265-330) -> `--needs 816:30` (no spin before the X-800 lantern pickup) fixed it. Heavier `--npw` or a per-ninpo quota
  (`--npq`) made the beam fall into the pits at X ~650/505. (3) `--ymax 193` prunes nodes falling into the pits (no floor is
  below y 192 after the chimney). (4) The J&S pickup beam (`--score tas`) is width-sensitive (v9: width 64 none, 48 caught);
  r8pipe now retries 64/48/80/32; main's plain legal TAS rows through the catch also work (w10). (5) Compare 2-2 candidates by
  the 3-1 control frame (2-3's tally depends on `$62`, see "Next: 2-3"). (6) TaskStop on a background beam leaves the python
  + Mesen workers running: kill them by PID.
