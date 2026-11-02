# Acts 3-4 legal stages (agent a34) - notes

## STATUS (read first)

* 2026-10-23 06:00 ROUND 5 (a56 agent): no 4-x work done this round (time went to 6-2/6-3/6-4a, see
  legal_a56_notes.md "Round 5"); 4-3 on the record's line from 4-3a and 4-2's exit remain open. The new Mesen tools
  (`work/r5/runbeam.py`, `mastar.py`, `mboot.py`) work on any stage: boot with `mboot <name> tas:<control frame> rows:<prefix>`.

* 2026-10-23 06:00 ROUND 5 (c5, PAUSED): 3-3 still unsolved on the chain; cause of the graft failure found; plan = >= 30 ninpo at 3-3 (see "Round 5 (chain)" at the end).

* 2026-10-23 04:35 (toolkit agent tk): Act 3 ON THE CHAIN: 3-1 (`logs/tk_3-1_a2`, 1,638 f, record +35) and 3-2
  (`logs/tk_3-2_c1`, 2,600 f, record +272) verified; chain at 3-3 control frame 15,140 (`states/tk_3-2_c1_end`, hp 8,
  ninpo 23, Fire Wheel). 3-3 NOT solved (see "Act 3 on the chain" at the end).

* 2026-10-23 04:10 ROUND 4 (by the a56 agent, 4-x only): 4-3 pillar section + room c done by A* (room d entered
  20716 = TAS +219, the record ~+127 there -> 4-3 cannot beat the record on this line); 4-2 tasrepair worse than
  r2d. No new verified 4-x stage. Details in "Round 4" at the end.

* 2026-10-20 08:55 ROUND 3 PAUSED by the owner (usage limit); all a34 jobs killed. No new verified stage file.
  Best 4-3 legal prefix now `logs/a34/r3_43c0_g2` (check_inputs PASS):
  4-3b exit 19804 (was 19820), pillar top 19951 (was 19966). Stage table below unchanged. No chained 3-1 state
  from the Acts 1-2 agent existed, so no chained 5-1 state was published. Resume steps at the end of "Round 3".

* 2026-10-20 01:35 END OF ROUND 2 (details in "Round 2" at the bottom): **4-1 solved and under the record's split
  (record -7, `logs/a34/4-1_r2c`)**; 4-2 solved but record +27 (`4-2_r2d`); 4-3 NOT finished (legal prefix to
  room 19 at 19966, `r2_43c_a1`; stuck at the pillar / stepped-block section, TAS ~20030-20130); 3-3 not improved
  (still record +67); 3-1/3-2/4-4 unchanged. No chain: no chained 3-1 state from the Acts 1-2 agent yet.

* 2026-10-19 16:20 END OF SESSION: 3-1, 3-2, 3-3, 4-4 solved from TAS states (table below); 4-1/4-2/4-3 not
  finished (legal prefixes and the blocking spots are listed). No chained run (no Acts 1-2 chained state yet).
* 2026-10-19 ~08:00: analysis done; tools written (`ng/stages/a34_core.py`, `a34_sync.py`, `a34_follow.py`,
  `a34_beam.py`); first beam run on 3-1 (from the TAS state, legal exact-sync prefix to 10321) in progress.
* Results table at the bottom (filled in as stages finish). Output files: `logs/a34/<name>.inputs.txt`.

## Stages owned

`$6D` 5..11 (ng/stages.py; the task text said "6-12", the table says 5-11): 3-1 (room 10), 3-2 (11),
3-3 Basaquer (12), 4-1 (13-15), 4-2 (16), 4-3 (17-20), 4-4 Kelbeross (21).

| stage | TAS control | next load | control->next control | record (s -> NES f) |
|---|---|---|---|---|
| 3-1 | 9829 | 11282 | 1605 | 26.67 -> 1603 |
| 3-2 | 11434 | 13589 | 2307 | 38.73 -> 2328 |
| 3-3 | 13741 | 14417 | 828 | 15.17 -> 912 |
| 4-1 | 14569 | 16530 | 2113 | 36.47 -> 2192 |
| 4-2 | 16682 | 18808 | 2278 | 38.33 -> 2304 |
| 4-3 | 18960 | 21202 | 2394 | 42.55 -> 2557 |
| 4-4 | 21354 | 21973 | 771 | 13.07 -> 785 |

## Where the TAS breaks our rules (counted on the TAS rows of each stage, check_inputs semantics)

| stage | L+R frames | U+D frames | other violations |
|---|---|---|---|
| 3-1 | 0 | 0 | 46 one-frame holds (A 21, B 20, Up 5), 5 Right releases of 1 frame (sub-weapon throws) |
| 3-2 | 32 (12685-12717) | 0 | 50 one-frame holds, 4 short releases |
| 3-3 boss | 0 | 19 (scattered) | mashing: 280 period, 418 hold, 205 release, 12 x 109/600 window |
| 4-1 | 59 (15814; 16086-16106; 16132-16199 = room c) | 0 | 68 period, 101 hold |
| 4-2 | 42 (18067-18108, 18679) | 1163 (U+D+Right while running, 16692-18591) | 43 hold |
| 4-3 | 166 (19039-72, 19101-60, 19319-31, 19768-800, 20095-125, 20613-45) | 23 (20580-601) | 44 period, 98 hold |
| 4-4 boss | 103 (21358-79, 21588-602, 21681-774) | 131 (14-frame bursts every 32 f) | small |

## Findings

* U+D+Right on the ground (4-2) = Right with the idle animation: positions identical, only `$80-$83`/OAM differ
  (measured over 100 frames, agrees with legal_a12_notes).
* **Sub-weapon throw needs NO left/right on the Up+B frame** (Up+B+Right does not throw: measured at 10329,
  ninpo stays). The TAS releases Right for exactly 1 frame per throw; legal = 2 frames released, i.e. one frame
  (1.5 px) lost per throw while running/in the air, unless the throw is placed where Ryu does not move anyway.
  3-1 has 5 throws (Fire Wheel pickup + ninpo/timer phase for 3-3), so a straight copy loses ~5 f.
* Exact (zero-loss) repairs work for one-frame A/B holds: 11 of 11 in 3-1 before the first throw re-synced to
  the TAS RAM exactly (`a34_sync.py`, legal prefix `logs/a34/sync_3-1.inputs.txt` = TAS state at 10321).
* After any real loss, open-loop TAS rows collapse within ~300 frames (hits, pit) - closed loop is needed
  everywhere after the first loss: `a34_beam.py` (TAS-guided beam: follow-the-TAS action + primitives,
  lateness by position match to the TAS path).
* The RNG `$BF` gatekeeper: the 3-2 tosser (TAS notes); a chained run arrives with another `$BF`, so the
  3-2 solution must be re-searched from the chained state.

## 3-3 Basaquer (measured)

* The boss path is FIXED (does not depend on Ryu; checked: TAS rows vs no input vs Left give the same boss x/y
  for 200 frames): jump right->left, lands x=43 y=208 on 13795, sits to 13817, jumps back right (x 208 at
  ~13872), sits ~20 f, jumps left again (~13895-13950).
* Fire Wheel = 5 ninpo, up to 3 hits per throw, 20 ninpo at 3-3 start = 4 throws. **Only one wheel at a time:**
  if a flame of the previous throw is still alive, Up+B plays the throw animation (anim 8, Ryu locked ~16 f on
  the ground) but spends nothing and throws nothing. Up+Left+B = sword slash, not a throw (direction must be
  released; a legal 2-frame Left to turn means the throw comes 1 frame after the turn ends).
* TAS: wheels at 13761/13777/13788/13822 (9+3 hits) + 4 air slashes every 2 f (13814-20) -> dead 13824. The
  U+D+L at 13762-66 moves Ryu left 1.5 px/f in the air (legal Left = 0.5 px/f): the throw-2 position is then
  7 px off and its 3rd flame misses, which blocks throw 3. Fix found by sweep: stop running right at 13753
  (instead of 13758), throws at 13759/13776/13788 -> 8 HP left at 13792 (TAS 7).
* Legal sword cadence (B every 5 f) gives 2-3 hits in the 13795-13817 window -> ~5 HP left when the boss leaves;
  the kill then needs its next pass.
* Blind searches did badly here: beam with position/time scoring (no kill in 600 f), mutation hill-climb.
  Structured parameter sweeps (a34_b33.py, states/tmp/a34_scratch/p13-p16) worked.

## 3-2 pillar (12646-12718)

* The TAS throws (1-frame Right release) then at 12674-12717 wall-jumps and crosses to the top of the tall
  pillar with L+R (1.5 px/f to the right while facing left). The plain TAS-path beam lost 73 f there.
* A goal beam (a34_beam.py `goal`: score = t + distance to the TAS position of frame 12718 / 1.5, plus the
  legal wall-climb macros "R+A,R+A,L,L,-" / mirrored) reached that position at 12728 = +10 incl. the throw.

## Coordinator note (13:50): use the record's route where the TAS line needs a banned trick

* 3-3 record (video frames 15600-15780, contact sheet shots/tmp_a34/rec/r33.png): Ryu stays left/centre and
  burns the Fire Wheels while the boss sits on the RIGHT side (second pass, ~13872-13895 in TAS frame terms);
  kill ~166 f after control (TAS-relative ~13907).
* Ground slashes never hit Basaquer at x=43 (720-candidate sweep p24: 0 sword hits in 13788-13817): the sword
  must reach his upper body -> jump slashes (Down+B in the air), as the TAS does.
* 4-4 Kelbeross (TAS): 5 ninpo + Jump&Slash; ONE spin slash at 21361 kills both dogs' 16 HP in 16 frames
  while Ryu drifts right facing left (L+R = no handler, raw Right bit moves at stored speed). Legal sweeps of
  jump/drift/slash timing got to 3 HP left (p25); wider sweep p26 running.
* 4-1 wall at 15706 (TAS: Left+A every 4 frames = chimney climb, legal period is 5): 1,458 two-cycle legal
  climb candidates (p23) never reached the top -> use a different (record) line over that block.

## 4-1 block at 15700 (record route)

* Legal wall climbing at 15705 is impossible: 288 periodic patterns (cycle 5-8, every A/direction combination,
  p27) never raised Ryu above his start y=160. The TAS needs A every 4 frames there.
* The record stays high: from the y=96 platform, a Right+A jump at 15596 lands on the middle block (y=96,
  wpos 1689 at 15687) and walks onto the target block (TAS reaches wpos 1761 y=128 at 15732; we ~15735).
  Prefix `logs/a34/b41_pre` (sync to 15540 + TAS rows + that jump), then the beam.
* 4-2 (18160-18232): the TAS runs with U+D+Right = moving with the idle (crouch-height?) animation; the legal
  beam got knocked around there (green ninja / birds) and stalled for 100+ frames; not solved yet.

## Legal wall climbing (found 14:30)

* Same-side repeated wall jumps never gain height at the legal A period (p27 at 4-1 15705, p32 at 4-3a: 0 of
  ~900 periodic single-cycle patterns climbed). What works is ALTERNATING the wall-jump direction every
  5-frame cycle ("L+A,L+A,-,-,-, R+A,R+A,R,R,R" or with the R+A delayed one frame): p33.
  - 4-1b shaft (room 14, from TAS room entry): exits to room 15 at 16142 (TAS 16107, +35).
  - 4-3a (room 17, from TAS 19036): exits to room 18 at 19089 (TAS 19076, +13).
  These are beam macros Z1/Z2/Z1m/Z2m in a34_beam.py.
* The pit prune y >= $F0 was wrong for rooms that start low (4-1b starts at y=232): now y >= $F8.

## Results

All from the TAS stage-start states (states/ref4751/<n>_control); files in logs/a34/<file>.inputs.txt = our rows
from the state's next frame through the next stage's load frame (incl. the earliest legal Start skip); each was
replayed open-loop from the start state (same load frame) and passes check_inputs.py on its own. End states:
states/tmp/a34_end/<file>.State. "vs record" = our stage time minus the record's stage time (record_notes.md s.6,
TAS stage + record diff).

| stage | file | next load (TAS) | vs TAS | vs record | notes |
|---|---|---|---|---|---|
| 3-1 | beam_3-1_v2 | 11287 (11282) | +5 | +7 | Fire Wheel + 10 ninpo like the TAS; 5 throws cost 1 f each |
| 3-2 | 3-2_tas3 | 13632 (13589) | +43 | +22 | sync to 12642, goal beam over the pillar (12728, +10), beam |
| 3-3 | 3-3_p2 | 14567 (14417) | +150 | +67 | plan sweeps (wheels 13759/13776/13788/13820, jump slashes) to 13904, boss beam; kill ~13980 |
| 4-1 | - | - | - | - | NOT DONE. Legal prefix to room 15 exists: `b41_pre2` (record-route jump over the 15700 block, beam to room 14 entry 16020, alternating shaft climb -> room 15 at 16152 = +45 vs TAS 16107). Room 15 (4-1c, TAS L+R 16132-16199 "train" section): beam stalls at x=123 y=151 losing HP (solve_4-1_p5.out) |
| 4-2 | - | - | - | - | NOT DONE: auto-goal passed the L+R spot (18158, +14); stalls ~18195 (green ninja / birds where the TAS crouch-runs with U+D+Right) |
| 4-3 | - | - | - | - | NOT DONE: 4-3a legal climb exits at 19089 (+13, b43_pre); 4-3b entry at x=104 needs the TAS's L+R in-wall exit - legally Ryu does not move (p34); the record leaves 4-3a another way (right side), not reproduced |
| 4-4 | 4-4_p2 | 21973 (21973) | 0 | -14 | Jump&Slash kill on 21376 like the TAS |

Chained runs: the Acts 1-2 agent's chained end state did not exist during this session (its notes list 1-1/2-1
only). A chain from our own 3-1 end (a34_chain.py, tag c1) was started and stopped: in 3-2 the chained RNG/
position made the beam stall near TAS 11730-11750 (130+ f) - not usable.

Lessons: v1 of 3-1 reached the load 1 frame EARLIER than the TAS (11281) but skipped the Fire Wheel pickup
(ended with the Throwing Star, 12 ninpo) - the beam now penalises item/ninpo differences from the TAS path.

## Round 2 (2026-10-19, from 16:20)

Record route extraction: `knowledge/record_route_a34.md` (method of the a56/a12 agents reused; tools
`work/a34r2/`, frames `states/tmp/a34r2_vid/`). Outputs of round 2: `logs/a34/r2_*.inputs.txt`, logs
`logs/a34r2/`, scratch states `states/tmp/a34r2_x/`.

* **Correction of round 1: single-wall climbing IS legal and fast.** Sweep of all 310 legal 5-8 frame cycles
  (`work/a34r2/climbsweep.py`) at the 4-1c wall: best `Left+A, Left+A, Right x6` (wall on Ryu's right) = 1.54 px/f
  (the record's ~8-frame rhythm); at the 4-3b gap 1.45 px/f with the 9-frame variant. Beam macros `C8` / `C8m`
  added to `a34_beam.py` (backup `.backup`). ROM reason: jump-off needs pad == A+away exactly, re-grab needs one
  frame with no wall tile touched, the air drift back is 0.5 px/f (bank 7 $EB7B-$EC5A, $E677, $EFF1).
* 4-1c geometry (RAM): floor entry x 123 y 232 (16173 with b41_pre2); the branch stub on the wall's left face is a
  platform at y 128 (x ~96-124); the wall top is y 96. Wall-jumping off the wall while clinging at y <= 143 lands on
  the branch; from the branch a normal jump (48 px) clears the wall top. Clinging stops at y ~113 (the top corner):
  the climb alone cannot get over the top (that is where round 1's beam stalled).
* 4-3b: the entry (x 91 y 232, clinging to the box's left face) is the record's too; the gap to the left wall is
  a chimney; L+A jumps off toward the left wall, the C8 cycle climbs it (round 1's "Ryu doesn't move" = it never
  tried to jump off).
* 3-3: b33_pre2 (round 1) leaves Basaquer at 4 HP at 13822 and Ryu just walks under him while he crosses to the
  right (boss path: x 58 y 182 at 13822 -> apex y 128 at x 118-130 (13842-46) -> lands x 211 y 208 at 13874, sits
  to ~13895). Boss beam from 13822 (W 30) running.
* 19:50 tools: `ng/stages/a34r2_astar.py` = A* over stable states (standing/clinging) with legal macros (C8/C9 climb
  cycles, wall jump-offs JO*, runs, waits, jumps with held/switched direction, jump+air-slash J*S, ground slashes);
  f = t + |dx|/1.5 + climb/2.4. It solves the spots where the TAS-guided beam stalls (local optima of the
  position score) at the cost of ~5-15 s per expansion on the shared PC.
  - 4-1b shaft: C8 instead of the round-1 alternating climb: room 15 at 16146 (TAS 16107, +39; round 1 +45);
    rows `logs/a34/r2_41c_entry2` (to the room-15 floor, 16167).
  - 4-1c: A* (`r2_41c_astar`): C9, C8 x4, jump off onto the branch, jump right onto the wall top: standing on the
    top at wpos 185 on 16296 (TAS there ~16219; the record ~5 f later than us by the scroll-72 point).
  - 4-3b: A* (`r2_43b_astar`): from the entry (19110) onto the box top (x 95, y 160) at 19165 (record ~19157).
    The box top is y 160; the face climb tops out at y ~163-167 (corner tile), so the box needs a jump from the
    left ledge (y 208) or the A*'s JO/C9/jump sequence.
* 3-3 measured: sword hits on the crossing boss ARE possible (the record ground-slashes it as it descends toward
  the right, video 15722-15730); sweeps s33 (wheel 4 early) and s33b (wheel 4 at the crossing from the right side)
  gave 0 extra hits (wheel 3's flames still alive block wheel 4 before ~13820). s33c (record plan) running.
* 21:00 **4-1 SOLVED (legal, verified open-loop, check PASS) but +2 vs the record**: `logs/a34/4-1_r2b.inputs.txt`
  (b41_pre2 4-1a/shaft entry, C8 shaft climb, A* climb onto the wall top, A* run to wpos 623, beam finish):
  next load 16611 = TAS +81 (record +79). Room entries: b +11 (record +11), c +39 (record +42); the room-c climb
  costs us +38 (record +37) and the run along the top 3 more. Needs >= 3 f; a finer-macro A* of the climb is running.
* 4-2: weighted A* (`--w 2`) from the exact TAS sync (18029) past the round-1 stall: wpos 2380 at 18254
  (`r2_42_astar1`, TAS +24, record +14 here); the TAS-guided beam then stalls again at 18296 (hits) -> A* chunk to
  wpos 3013 running.
* 4-3: A* chunks: box top 19165 -> top of the tall block (wpos 441, y 96) at 19454 (`r2_43b_astar2`, TAS +72; the
  record is +79 there after losing ~36 f on that climb) -> next chunk to wpos 723 running.
* 3-1 "no throw" beam (A34_NOTHROW=1, keep ninpo for more 3-3 wheels) stalls at 10592: the TAS breaks the +10
  ninpo and Fire Wheel lanterns with its thrown stars (10485-10554); without throws they must be slashed. Dropped.
* 22:50 **4-1 BEATS THE RECORD'S SPLIT: `logs/a34/4-1_r2c.inputs.txt`** (from ref4751/08_4-1_control, 2034 rows):
  next load 16603 = TAS +73 = record -6; open-loop verified, check_inputs PASS; end state
  `states/tmp/a34_end/4-1_r2c.State`. Route: b41_pre2 4-1a, C8 shaft (room 15 at 16146), fine-macro A* climb
  (`A34_FINE=1`: JNS, JOLT4, C8 x5, C9, C7, JOLT2 onto the branch, JLR0 jump onto the wall top at 16288, wpos 185),
  A* run along the top (R2, JRR0, JRR16, JRS (kills the bird), R16, JRR0 x3, R16: wpos 623 at 16582), beam finish.
* 23:50 **4-2 complete (legal, verified, PASS) but behind the record**: `logs/a34/4-2_r2b.inputs.txt`: load 18875 =
  TAS +67 = record +41. Route: exact TAS sync to 18029 (TAS +0, i.e. 14 f ahead of the record), weighted A* chunks
  (18254 +24, 18386 +48, 18534 +40), tail A* w 1.2 (exit wall reached 18744), beam waits out the stage end. The
  losses are in 18029-18386 (enemies: green ninja, birds, knife thrower; the record runs along the brown ledges at the
  top of the screen there) - a finer A* of that part is running. Earlier version 4-2_r2a: load 18917 (+109).
* 00:30 4-2 improved: fine A* (A34_FINE=1, A34_ENEMYKEY=1, w 1.2) from the sync 18029 to wpos 2555 y 192 at 18355
  (`r2_42_b1`, was 18386), A* w 1.3 to the exit wall (18726) -> `logs/a34/4-2_r2c.inputs.txt`: load 18861 (a34_verify;
  a34_solve printed 18863 = the row after) = TAS +53 = record +27. PASS. The exit-wall part (wpos 2971 at 18635 ->
  exit) still loses ~25 f to the TAS: the TAS takes a damage boost at 18659 to cling high on the exit wall.
* Independent replays (a34_verify, logs/a34r2/verify_all.out): 3-1 beam_3-1_v2 11287 (+5), 3-2 3-2_tas3 13630
  (+41), 3-3 3-3_p2 14567 (+150), 4-1 4-1_r2c 16602 (+72), 4-2 4-2_r2c 18861 (+53), 4-4 4-4_p2 21973 (+0); all
  check_inputs PASS. (a34_verify's "load" = first traced frame with the new $6D = the TAS_LOAD definition; a34_solve's
  json "load" is sometimes 1-2 frames later.)

### Round 2 results (per stage, from the TAS stage-start states; load = first frame with the next $6D, a34_verify)

| stage | file (logs/a34/) | next load (TAS) | vs TAS | vs record | status |
|---|---|---|---|---|---|
| 3-1 | beam_3-1_v2 (round 1) | 11287 (11282) | +5 | +7 | verified, PASS |
| 3-2 | 3-2_tas3 (round 1) | 13630 (13589) | +41 | +20 | verified, PASS |
| 3-3 | 3-3_p2 (round 1) | 14567 (14417) | +150 | +67 | verified, PASS; round-2 sweeps s33/s33b/s33c/s33d found no faster kill |
| 4-1 | **4-1_r2c** | 16602 (16530) | +72 | **-7** | verified, PASS (NEW) |
| 4-2 | **4-2_r2d** (= 4-2_r2c) | 18861 (18808) | +53 | +27 | verified, PASS (NEW, first legal 4-2) |
| 4-3 | r2_43c_a1 (prefix only) | - | - | - | legal prefix (PASS) to room 19 wpos 207 at 19966 (TAS 19824: +142; record ~+75 there) |
| 4-4 | 4-4_p2 (round 1) | 21973 (21973) | 0 | -14 | verified, PASS |

vs record = vs TAS - (record - TAS) with record - TAS = 3-1 -2, 3-2 +21, 3-3 +83, 4-1 +79, 4-2 +26, 4-3 +163,
4-4 +14 (record_notes.md s.6). End states: states/tmp/a34_end/<file>.State.

Next steps (not done): 4-3 from r2_43c_a1 (the A* with --w 2 stalled at x 128 y 60-150 near wpos ~505: look at the
geometry at TAS 20016-20096 first; the record climbs the round pillar's right face and jumps onto the stepped block
with a Windmill throw at the gunner, video 22184-22280), then rooms c/d; 4-2's exit wall (TAS damage boost at 18659,
~25 f); 3-3 (needs 2 more hits by ~13906, or more ninpo: the record arrives with 27, we with 20 - the TAS breaks the
3-1 lanterns with stars, a no-throw 3-1 stalls); then the chain from the Acts 1-2 agent's 3-1 state.

## Round 3 (2026-10-20, from ~02:00)

Queue `work/a34r3/runq.py 3 work/a34r3/jobs.txt` (copy of a56r3's: starts a job only with free RAM >= 2.5 GB,
1 at a time if a HOLD_FARMS exists; PIDs in `logs/a34r3_pids.txt`). Logs `logs/a34r3/`, rows `logs/a34/r3_*`.
At the start free RAM was ~1 GB (another program held 3 GB), so nothing could start for a while.

Offline findings (TAS RAM `tas_ram.npy`, record video frames):
* **4-3 loss breakdown** (vs the record): room b entry -8 (we are ahead), box top -8, tall block -7, then wpos 441
  -> 723 +13 and the end-of-room-b climb +22 (TAS room change 19711 with a bird damage boost hp 13->11 at the exit
  wall; ours 19820, record ~19793): **we are +27 behind the record at room c's entry**, and room c's start (entry ->
  wpos 207) costs 38 more (ours 123 f, TAS 92, record ~85). Room c is not a loss of a weighted A*; both parts are
  being re-solved (r3_43b_x1 from 19454 to room 19 unweighted; r3_43c_x1 the pillar section).
* 4-3c pillar section, record (video 22160-22300): from the floor left of the round pillar he jumps (Ryu is drawn in
  front of the pillar = the pillar is background), throws a Windmill (ninpo 10->05) at the ninja right of the pillar
  in the air, lands on the floor by the stepped block's LEFT face (~22210), climbs that face (C8-type single-wall
  climb, ~22216-22258), throws the second Windmill (05->00) at the gunner at the top-left corner (22264) and stands
  on the block at ~22276. A* macro set now has optional throws (`A34_THROW=1`: TH, J?T4/J?T10).
* **4-2 exit**: the stage-end trigger is Ryu at the exit wall at wpos 3035 y 84 (then a fixed 128 frames to the
  load). TAS trigger 18680 (bird, slot 5, hits it at 18660 at x ~210 y ~130 while it flies at the wall: a boost up
  the wall), ours 18733. A sweep `work/a34r3/s42x.py` (cut points 18585-18640 of r2_42_b2, run/jump timings, closed-
  loop C7/C8/C9 climb, optional hold at the wall for the bird) is queued.
* **3-3 ninpo**: record HUD: 3-1 00 -> 10 -> 07 (ONE Throwing Star) -> 17 (+10) -> Fire Wheel; 3-2 17 -> 27 (no
  throw). The TAS (and our 3-1) throws FIVE stars (10329, 10345, 10485, 10501, 10554) and ends 3-1 with 10. Every
  star not thrown = +3 ninpo at 3-3; 2 fewer throws = 26 = a 5th Fire Wheel. `a34_beam.py` now takes
  `A34_NOTHROW_FRAMES=lo-hi,...` (drops the TAS's throws only there and penalises spending the saved ninpo);
  job `3-1 --tag r3nt1` drops 10329/10345.
* 05:11 RAM freed, jobs started. A* changes (`a34r2_astar.py`, backup `.backup_r3`): progress lines print wpos;
  `A34_HMAX=1` = h = max(dx/1.5, climb/2.4) (the round-2 sum over-estimates when a jump goes right and up at once,
  so round 2's "optimal" A* answers were not); `A34_SWITCH=1` = jumps switch direction at m = 0,4,..,24;
  `A34_THROW=1` = Up+B throws (standing and in jumps). Unweighted searches are too slow on the shared PC (4-30 s per
  expansion, 8 EmuHawks running): use --w 1.2-1.6 and `--only` macro subsets.
* **4-3b end improved: `r3_43b_x3` (A* w 1.5 HMAX SWITCH from r2_43b_astar3, 19656): room 19 at 19804 (was 19820;
  TAS 19711, record ~19793)** -> we are +11 behind the record at room c's entry instead of +27.
  An unweighted A* from 19454 (r3_43b_x1, old heuristic) found nothing in 700 expansions.
* 4-2: s42x sweep found nothing better (best trigger 18742 vs 18733). Record's 4-2 end (video 20630-20723): from the
  tree trunk on the left he drops to the short post, jumps right from the post to the brick exit wall and climbs it
  (~4 C8 cycles), trigger ~TAS-frame 18706 (TAS 18680, ours 18733). No boost. A* runs from 18355 were too slow
  (28 s per expansion with ENEMYKEY) and were stopped for 4-3 work.
* 3-1 `r3nt1` (drop the throws at 10329/10345, from sync_3-1): level with the TAS to 10580 (late -2) but stalled at
  the Fire Wheel pickup (~10594) and fell 80 f behind; stopped (4-3 first). Not resolved.
* Geometry learning from TAS states (the room entries are fixed points, so a route found from the TAS state can be
  grafted onto our prefix with `work/a34r3/graft.py`):
  - **room c after the block (TAS 20126, wpos 632 y 128) -> room 20: A* `r3_43q_tas1` 383 f (TAS ~374)** =
    ['JRR0','JRS','JRR0','JRR0','JNR4','JRR0','JNR4','R16','R8','JRR12'], room 20 at 20509.
  - pillar section (TAS 19826 pillar top -> block top wpos 632): `r3_43p_tas1` running (reached the block face wpos
    603 at 20095 = TAS pace).
  - room d (entry -> stand at wpos 748 y 208): `r3_43d_tas1` (w 1.2) no goal in 600 exp; `r3_43d_tas2` (w 1.6) running.
* 08:20 Room entries from below: the TAS enters 4-3c and 4-3d with an upward LAUNCH (rflags 0x54) because it
  leaves the previous room during a damage boost (bird/enemy hit at the exit wall, hp -1/-2). Our 4-3b exit
  (normal cling) gives no launch: Ryu just lands on the gap floor y 232 (probe `work/a34r3/probe43c.py`,
  `logs/a34r3/probe43c.out`); left of x ~147 is a pit (y 248). C8 on the pillar face climbs 1.5 px/f.
  A* option `A34_AIRRUN=1` (allow Left/Right holds while airborne) added for launched entries.
* Graft (`work/a34r3/graft.py`) of round 2's room-c route onto r3_43b_x3: **`r3_43c0_g2` = pillar top (wpos ~200,
  y 128) at 19951** (TAS 19826 +125, record ~+75 -> we are ~50 behind the record there).
* Room c after the block: `r3_43q_tas1` (from the TAS state 20126) reaches room 20 in 383 f (TAS ~374) incl. a
  boost at the exit (hp 11->10) -> graft it once our run stands on the block top (wpos 632 y 128).
* Room d A* from the TAS state: the heuristic pulls right but the route goes LEFT first (TAS stairs/wall to wpos
  70-114 y 84, then right): use the intermediate goal pos:20:182:128 (TAS 20685) first (`r3_43d_tas4`, killed
  before it started).

### Round 3 result / resume
* Kept: `r3_43b_x3` (4-3b exit 19804), `r3_43c0_g2` (pillar top 19951). Both from ref4751/10_4-3_control.
* Not done: pillar section, room d, 4-3 finish; 4-2 exit (record line: post -> brick wall, no boost); 3-1 fewer
  throws (r3nt1 stalled at the Fire Wheel pickup ~10594); chain.
* Resume (queue: `python -u work/a34r3/runq.py 3 work/a34r3/jobs.txt`, append lines like):
  1. `set A34_THROW=1&& set A34_AIRRUN=1&& set A34_HMAX=1&& set A34_SWITCH=1&& python -u ng/stages/a34r2_astar.py 4-3 ref4751/10_4-3_control r3_43c0_g2 pos:19:632:128:10 r3_43p_x1 --only J,R,W2,W6,W12,C8,C9,TH,L2,L4,L8 --w 1.4 --max-exp 700`
     (was at exp 50 when killed; f ~20264 = TAS +138 at the block top)
  2. `python -u work/a34r3/graft.py ref4751/10_4-3_control r3_43p_x1 r3_43q_tas1 r3_tas43_to20126 r3_43q_g1 20 -1 0 0`
  3. `set A34_AIRRUN=1&& set A34_HMAX=1&& set A34_SWITCH=1&& python -u ng/stages/a34r2_astar.py 4-3 ref4751/10_4-3_control r3_43q_g1 pos:20:182:128:14 r3_43d_x1 --w 1.3 --max-exp 600`
     then pos:20:748:208:4, then `python -u ng/stages/a34_solve.py 4-3 --prefix <last> --tag r3a` (finish, verify, check).
  4. 4-2: `set A34_AIRRUN=1&& set A34_HMAX=1&& set A34_SWITCH=1&& python -u ng/stages/a34r2_astar.py 4-2 ref4751/09_4-2_control r2_42_b1 pos:16:3035:84:6 r3_42_x3 --w 1.3 --max-exp 600`

## Round 4 (2026-10-22 evening; the 4-x parts, by the Acts 5-6 agent a56 round 4)

Queue `work/r4/runq.py 2 work/r4/jobs.txt` (PIDs logs/r4_pids.txt, logs logs/r4/). `work/r4/astar.py` = a34r2_astar
on ANY stage (rows in/out under logs/r4/); `work/r4/chainrooms.py` = A* leg by leg (room goals).
* 4-3 pillar section (resume step 1): `r4_43p_x1` (A* THROW/AIRRUN/HMAX/SWITCH, w 1.4, from r3_43c0_g2) reached the
  stepped block's top (wpos 622, y 128) at **20263** (TAS 20126 -> +137; the record is about +82 at room c's entry
  and +127 at room d's entry). Route: JRR4, R16, JRS, JRR4, JRS, JRS, JRR0, C8 x3, R2, R4, R16 (no Windmill throw).
* Resume step 2 (graft of r3_43q_tas1, found from the TAS state) FAILED on our run: the enemies differ (hp 11 -> 5,
  no room change; logs/r4/graft_43q_g1.out). Room c's end is re-searched from our state instead: `r4_43q_x1`
  (goal room:20:1179:79, the TAS's exit point).
* `r4_43q_x1` (A* from r4_43p_x1 to room:20:1179:79): **room 20 (4-3d) entered on 20716** (TAS 20497 -> +219; the
  record is about +127 at room d's entry) with hp 5 -> 4-3 cannot beat the record's split on this line (the record
  ends 4-3 at TAS +163; we are already +219 at d's entry). Rows `logs/a34/r4_43q_x1.inputs.txt` (from
  ref4751/10_4-3_control; legal by construction, not yet finished/verified as a stage). Room d not searched.
* 4-2 by `work/r4/tasrepair.py` (legalized TAS rows + short A* repairs, from ref4751/09_4-2_control): follows the TAS
  to 18108 exactly (+0), but the repairs then lose time (lag +69 at 18291, +129 at the exit wall ~18788) -> worse
  than round 2's `4-2_r2d` (+53, record +27). Stopped. The record's exit line (post -> brick wall, ~4 C8 cycles) is
  still the open item for 4-2.

## Act 3 on the chain (toolkit agent tk, 2026-10-22/23)

* NOT started on the chain: the verified power-on chain reached 2-3 control (frame 9,797, `states/tk_2-2_m2_end`,
  ninpo 0, J&S) by the end of the time-box; no chained 3-1 state exists yet. See legal_a12_notes.md "Round 4 (tk)".
* Basaquer (3-3) does not depend on `$BF` (DEBUG research `work/tk/rngtest.py`: `$BF` +37 / +101 poked at
  `ref4751/07_3-3_control`, `logs/a34/3-3_p2.inputs.txt` replayed: boss x/y/HP identical to the kill; +101 shifts
  one HP-display frame at the very end). The stage start is a fixed point, so `3-3_p2` (Fire Wheel, 4 wheels = 20
  ninpo, 978 f control->control, record 911.5) can be grafted onto the chain whenever Ryu arrives at 3-3 with the
  Fire Wheel and >= 20 ninpo: `python -m ng.solve.verify finish 3-3 <chained 3-3 control> <history> logs/a34/3-3_p2.inputs.txt tk_3-3_g1`.
  The a56 jump planner (`python -m ng.solve.boss 3-3 ...`) did worse than a34's sweeps here (Ryu gets hit; 14 HP
  left after 97 f).
* Ninpo plan for 3-3 (ROM lantern tables, `python -m ng.solve.items 3-1 3-2`): on the TAS line 3-1 offers
  +5 (x 336), +5 (432), +10 (576), +10 (1152) at ~1 f each and +10 (1328, y 96) for ~15 f; 3-2 offers +5 (352),
  +10 (448), +5 (1504), +5 (2192), +10 (2368) at ~1 f and +10 (2832) ~8 f, +10 (1152) ~18 f. Weapon lanterns:
  3-1 Star (768) AVOID if the Fire Wheel is already held, Fire Wheel (1184, y 96); 3-2 Windmill (1008, 2624)
  AVOID, Fire Wheel (1680). The record: 3-1 00 -> 10 -> Star -> one throw -> 07 -> 17 -> Fire Wheel; 3-2 -> 27.
  Every star NOT thrown in 3-1 is +3 at 3-3; 25 ninpo = a 5th wheel.
* 2026-10-23 03:50 (tk): **3-1 on the chain VERIFIED: `logs/tk_3-1_a2.inputs.txt`** (`python -m ng.solve.beam 3-1
  tk_2-3_bh2_end --ref hybrid --width 8 --chunk 8`): 3-1 control 10,902 -> 3-2 control 12,540 = 1,638 f (TAS +33,
  record +35), hp 14, ninpo 13, Fire Wheel (item 128), state `states/tk_3-1_a2_end`, history
  `states/tmp/tk_hist32n.inputs.txt`. The chain arrived at 3-1 with 0 ninpo and no weapon; the beam took the Star
  and the Fire Wheel like the TAS.
* 2026-10-23 04:15 (tk): **3-2 on the chain VERIFIED: `logs/tk_3-2_c1.inputs.txt`** (`python -m ng.solve.beam 3-2
  tk_3-1_a2_end --ref hybrid --width 8 --chunk 8`): 12,540 -> 3-3 control 15,140 = 2,600 f (TAS +293, record +272),
  hp 8, ninpo 23, Fire Wheel, state `states/tk_3-2_c1_end`, history `states/tmp/tk_hist33n.inputs.txt`.
* 3-3 graft of `logs/a34/3-3_p2` onto that state FAILS (Ryu is hit at once, 3 wheels gone by +60 rows, no kill):
  the `$BF` test above was not enough - something else that differs on the chain (hp 8 vs 16? time since power-on /
  another timer) changes the fight. Basaquer must be solved from the chained state itself (jobs d1/d2/d3 below).

## Round 5 (chain) (agent c5, 2026-10-23, PAUSED)

* Why the 3-2 graft failed: NOT Basaquer (his path is identical on the chain, measured slot by slot) but Ryu's
  start: the TAS holds Right on the pre-control row (x 51, speed 1.5 at control; ours x 48, 0), and leftover enemy
  slots 0-2 (type $11) from 3-2 move the falling-rock ($1A) spawn from his first landing to his second.
* Mechanics (Mesen, `work/c5/hbwatch.py`): boss box xr 24, yr 40 sitting / 56 jumping; first-pass timeline from
  control: in the air to row ~54 (lands x 43), sits 54-76, jumps right (lands x 211 ~132), sits to ~152, jumps left.
  A wheel throw locks Ryu ~16 f on the ground (B ignored); a ground slash takes ~16 f (wind-up 6 f to the hit pose),
  so ground slashes give 1 hit per sit; air slashes are needed for more.
* Best on the chain (23 ninpo = 4 wheels): boss 16 -> 8 by row 51 (3 wheels), -> 5 with wheel 4 + 1 slash; NO kill
  in 230 rows (`states/tmp/c5_b33grid1.inputs.txt`, `c5_b33ga1/2`; grid log `logs/c5/b33grid1.out`).
* Plan: arrive with >= 30 ninpo (6 wheels x up to 3 hits = 18 >= 16: kill by wheels during the first pass, ~row
  90-100, TAS +83, record ~+166). 3-2 offers +10 at x 2832 (~8 f) and x 1152 (~18 f) beyond the beam's pickups.
  Otherwise kill on the second pass with jump slashes like the record (boss sits right, rows ~132-152).
* 3-2 loss map vs TAS (trace): +40 at X 256-384, +97 at X 1024-1152, +57 X 1152-1280, +64 at the pillar X 1920-2048.
* Resume 3-3 search: `python -u work/c5/b33ga.py <hist to control-1> <mesen state at control-1> <out> --seed <rows>
  --H 230 --workers 2` (state = `python work/c5/mboot.py <chain> <trace> <control-1> <name>`).

## 3-1 lock round (tas5) (2026-10-24, plan (a): TAS line, 5 Star throws)

Result: **`logs/l31_tas_c1b_poweron.inputs.txt`** (power-on to 3-2 control 11,604; stage rows `logs/l31_tas_c1b.inputs.txt`,
1,611 f = TAS +6 = record +8.3; end state `states/l31_tas_c1b_end`; exit hp 16, ninpo 15, Fire Wheel; `$62` 45 at 3-2
control). verify finish legal, `verify chain l31_tas_c1b_poweron` two replays MATCH (RAM sha1 de128d9ffd61), judge PASS.
(`logs/l31_tas_c1` = same rows with a 1-frame B at 10,510: judge FAIL, superseded.)

Facts:
* 3-1 is pure running at 1.5 px/f to X 2011 (play end; 3-2 control = +281). The TAS loses exactly 1 f per throw and
  nothing else. Our start is 1 f behind the TAS phase (lag 165). Floors: no throws 11,594; 1 throw 11,596; 5 throws
  11,604 (each legal throw = 2 frames without Right; Right+Up+B does not throw, measured). The mod-5 ninpo rule allows
  0 or 5 throws only, so plan (a) is finished.
* Enemies on `$BF` 251 vs the TAS: same types and nearly the same places; the differences are a few px, so the TAS's
  slashes miss in 3 places (type-3 walker X ~240, type-11 flier X ~670, type-1 X ~1290) and a type-3 walker hits at
  X ~1938; all fixed at 0 cost by B timing or small beams. The type-9 dog (from X ~356, faster than Ryu) and the knife
  thrower (type 2, X ~811 y 160) are handled by the TAS's own jumps and its first throw once the rows are in sync.
* Mesen tool bug (see LOCKED_CHAIN agent notes): a core idle > ~1 s inside the server callback dies. `work/l31t/fcka.py`
  (keepalive) fixes it; `work/l31t/tbeam.py` uses it and also rebuilds dead cores by replaying node rows.

Tools (`work/l31t/`): `lib.py` (Mesen state `states/mesen/l31_ctl.mst` = 3-1 control), `mkst.py` (rows -> Mesen state +
history), `follow.py` (legal TAS rows, divergence), `tfol.py` (TAS rows + one Right-released row after each throw),
`sync.py` (B-timing edits that keep TAS sync), `tbeam.py` (beam with 3-1 item rules: --starby/--fwby/--fwbrk/--gotby,
scores tas/tx, keepalive), `cmpen.py` (enemies ours vs TAS), `defi.py` (frames behind the TAS along a rows file),
`mkctl.py` (NesHawk power-on -> state + trace). TAS Mesen state at 3-1 control-1: `states/mesen/l31t_tas9828.mst`.

Rebuild of c1b (all Mesen, then NesHawk):
1. `b1p.txt` rows 0-399 (beam `b1`, in sync, +5 X 336, +5 X 432, +10 X 576) -> `b2p.txt` (beam `b2` from row 400: type-11
   dodge) -> `q440.txt` = b2p[:440]; `python work/l31t/follow.py work/l31t/q440.txt 10268 150 --out work/l31t/r517.txt`
   (TAS rows through throws 1-2) + one `B+Up` row = `r518.txt` (in `cand1b` row 517 is `B+Up`: B held 2 f).
2. `python work/l31t/tfol.py work/l31t/r518.txt 10345 820 --out work/l31t/r830.txt --cut 830`;
   `python work/l31t/sync.py work/l31t/r830.txt 10654 200 "B:10-10" --tol 2 --out work/l31t/r1030.txt`;
   `python work/l31t/tfol.py work/l31t/r1030.txt 10854 600 --out work/l31t/r1250.txt --cut 1250`.
3. `python work/l31t/mkst.py work/l31t/r1250.txt 1250 r1250`; `FB_NW=2 python -u work/l31t/tbeam.py
   work/l31t/h_r1250.inputs.txt states/mesen/l31t_r1250.mst x:10:ge:2011 e1 --score tx --yw 0.05 --minhp 16 --width 96
   --frames 120 --alpha "Right|A+Right|B+Right|A+B+Right|-|A"` -> `cand1b.txt` = r1250 + fb_e1 (row 517 = B+Up).
4. `python -u -m ng.solve.verify finish 3-1 lock_31_ctl logs/l22_art_w10_to31_poweron.inputs.txt work/l31t/cand1b.txt
   l31_tas_c1b`; `python -u -m ng.solve.verify chain l31_tas_c1b_poweron logs/l22_art_w10_to31_poweron.inputs.txt
   logs/l31_tas_c1b.inputs.txt`.

## 3-1 lock round (alt) (agent alt, 2026-10-24 17:38-20:20)

Plans (b) 1 Star throw and (c) 0 throws on the locked chain (3-1 control 9,993, `$BF` 251).
* **Result: `logs/l31_alt_b2r_poweron.inputs.txt` = 3-2 control 11,595** (1,602 from 9,993, record -0.7), hp 16, FW/12,
  `$62` 54, Ryu x 35 moving at control. Effective 11,601 with the +6 f residue at the 3-3 tally (12 mod 5 = 2).
  Uses row 9,993 = Right (the free control-frame row, coordinator 20:00) and the last 2 pre-control rows = Right.
  NesHawk verify finish + `verify chain l31_alt_b2r_chain` (MATCH, RAM sha1 8a74b015f3e5) + judge PASS.
* Plan (c) impossible (FW lantern y 96 needs Ryu's feet y < 120 at X 1152-1216; floor jumps peak at y 125; the towers
  there are background). 1 throw is the best item plan (see LOCKED_CHAIN.md "Agent notes (3-1)", alt 20:20).
* Tools (`work/l31alt/`): `lib.py` (Mesen core at 3-1 control; `L31_PRE=1` = control-1 state `states/mesen/l31alt_pre.mst`,
  frame 9,992), `tmod.py` (prefix rows + legalized TAS rows at piecewise lags `--lags row:lag,..`, throws not in `--keep`
  become Right, `--slash` adds B), `tscan.py` (scan one extra B/spec row, first hit + end X), `ev.py` (events along a
  rows file), `thr.py`/`thr2.py` (Star-throw sweeps), `beam.py` (item-phase beam; myopic, not used for the result),
  `pretest.py` (NesHawk pre-control Right test), `nhprobe.py` (NesHawk probe from the TAS state), `mkbase.py`.
  States: NesHawk `lock_31_ctl` (9,993), `lock_31_pre` (9,992); Mesen `states/mesen/lock_31_ctl.mst`, `l31alt_pre.mst`.
* Resume / rebuild:
  `L31_PRE=1 python work/l31alt/tmod.py logs/l31_alt_b1.inputs.txt 0 1400 --slash 503,535,780,864 --keep 657 --lags 1:164,727:161 --out work/l31alt/cand_b2.txt`
  then `python -u -m ng.solve.verify finish 3-1 lock_31_pre work/l31alt/h9992.inputs.txt <rows (first 1,331, last 2 pre-control rows Right)> <out>`
  and `python -u -m ng.solve.verify chain <name> <power-on file>` (power-on = locked rows 1-9,992 + the stage rows).

## 3-2 lock round (first) (agent "first", 2026-10-24 from 21:00; first half = 3-2 control to X ~1252, then help)

Start: locked 3-2 control 11,595 (`logs/l31_alt_b2r_poweron.inputs.txt`), x 35 moving, hp 16, np 12, FW, `$BF` 61.
States: NesHawk `states/lock_32_ctl` (+ trace `logs/l32_base.trace.csv`), Mesen `states/mesen/lock_32_ctl.mst`.
Tools `work/l32a/` (README.txt there).

Findings:
* **Legal TAS rows at lag 160 (our frame = TAS frame + 160) track the TAS exactly from control to the pillar edge
  (X 965 at 12,215, d 0, +10 at X 441 taken): no repairs at all.** (The prep's row-160 divergence was on c1b's x-32 start.)
* Tosser 1 (spawn BF 170) only walks at Ryu (first axe +85 f): the TAS rows get hit by its BODY at X 1041 (12,266) and
  knocked LEFT. Knockback goes away from the enemy (1 px/f, +29 px).
* **Body damage boost (new):** walk off the pillar (Ryu leaves its top at X ~968, 12,218), land at X 1013 (12,247) and
  jump on the landing frame (A+Right on stage rows 651-652; it is the ONLY jump frame that works: earlier = no jump, later
  = Ryu passes over without a hit), come down behind the tosser: its body hits Ryu at X 1067 y 170 (12,283, hp 15) and the
  knockback carries him RIGHT onto the ladder at y 141 (no-axe line: y ~177). The knockback state lasts ~21 f (wall
  jump possible at 12,304), wall-jump left onto the branch (12,315), jump right onto the top (X 1101 y 80, 12,336), beam
  past tosser 2 (air slash) -> X 1252 at 12,439 (no-axe line 12,445, hp 16). Body hits need Ryu's feet >= 168 (tosser
  box y 168-192), so the boost peak is >= y 139: the branch (snap needs ~y 135, the TAS's axe boost) is out of reach;
  the ladder + branch step is required. Pillar jumps (rows 618-622) come down in front of the tosser (hit, knocked left).
* After X 1252 legal TAS rows at **lag 188** track exactly to the pillar (X 1831 at 12,825 = TAS 12,637).
* **Free +5 at X 1504:** air slash B on stage rows 990-991 (lantern breaks at ~X 1473-1490 y ~90), the +5 is collected
  at row 1,019 (X 1515 y 113) with no change to the line -> np 27 at the pillar; + the TAS's +5 X 2192 = 32 at the exit.

Rebuild (all from `states/mesen/lock_32_ctl.mst` / NesHawk `lock_32_ctl`):
1. `python work/l32a/tmod.py - 0 619 --out work/l32a/p619.txt` (legal TAS rows, lag 160); + `work/l32p/noaxe_full179.txt`
   = `work/l32a/n850.txt` (v1, X 1252 at 12,445, hp 16).
2. `work/l32a/bo698.txt` = n850[:650] + A+Right x2 + Right to row 698; `python work/l32a/mkst.py work/l32a/bo698.txt 698 bo698`;
   `FB_NW=2 python -u work/l32a/abeam.py work/l32a/h_bo698.inputs.txt states/mesen/l32a_bo698.mst z:1100:96 top1 --score h2
   --width 200 --frames 70 --alpha "Right|A+Right|Left|A+Left|-|A|Right+Up|Left+Up|A+Left+Up|Up|A+Right+Up"` -> top1_full.txt (741 rows);
   `python work/l32a/mkst.py work/l32a/top1_full.txt 741 top1`; beam `r1` (`x:11:ge:1252 --score x --minhp 15 --width 128
   --alpha "Right|A+Right|B+Right|A+B+Right|-|A"`) -> `work/l32a/b844.txt` (v2).
3. `python work/l32a/comp.py work/l32a/b844.txt 844 1260 --lags 845:188 --slash 990,991 --out work/l32a/c_s990.txt`;
   first 1,230 rows = `work/l32a/q1230.txt` (NesHawk `states/l32a_q1230`, frame 12,825, X 1831, np 27).
4. NesHawk checks: `python work/l32a/nhplay.py <rows> [--n N] [--save name] [--lag 188 --from 840]`.
5. Pillar (no wheel, lag 187 kept): from r1229 = `work/l32a/r1229.txt` (w843 + legal TAS rows lag 187, B on 989-990):
   `python work/l32a/comp.py work/l32a/r1229.txt 1229 2100 --lags 1230:187 --set "1273=Left,1276=Right,1277=A+Right,1278..1302=Right,1303=B+Right,1304=B+Right,1305..1311=Right" --out work/l32a/nt2.txt`
   (spell out every row in --set; `work/l32a/nhvar.py` takes ranges `1278-1302=Right`). Facts: the TAS's L+R at the pillar
   is needed only because it jumps from the branch FACING LEFT (it lands there from the wall jump); one standing frame with
   Right on the branch turns Ryu right and a plain Right jump clears the pillar's left face (TAS +0 in frames, Ryu 1 px
   behind). The pillar-top type 3 must then be slashed (B rows 1,289-1,295 or 1,302-1,306), else it hits.
   With the wheel thrown legally (Up+B 2 rows) it is TAS +1 (lag 188) instead.
6. End: on the TAS line the end type-3 walker (X ~2948 at our 13,600) touches Ryu because he is 1 px behind the TAS
   (the TAS clears it by 1 px); beam `e5`: `python work/l32a/mkst.py work/l32a/nt2.txt 1900 nt1900`;
   `FB_NW=2 python -u work/l32a/abeam.py work/l32a/h_nt1900.inputs.txt states/mesen/l32a_nt1900.mst x:11:ge:3035 e5 --score x
   --minhp 15 --width 300 --frames 170 --npset 32 --npx 2200 --alpha "Right|A+Right|B+Right|A+B+Right|-|A|B"` (X 3035 at 13,649).
7. Candidate = nt2[:1900] + ab_e5 + Right x5 + blanks to stage row 2,333 + Right, Right (control 13,930) = `work/l32a/cB.txt`;
   `python -u -m ng.solve.verify finish 3-2 lock_32_ctl logs/l31_alt_b2r_poweron.inputs.txt work/l32a/cB.txt l32_a_cB`;
   `python -u -m ng.solve.verify chain l32_a_cB_poweron logs/l31_alt_b2r_poweron.inputs.txt logs/l32_a_cB.inputs.txt`.
   cC (np 37) = cB with rows 989-990 Right and 1,589-1,590 B+Right. NesHawk end check: `python work/l32a/nhend.py l32_a_cB_end`.

Results: cA 13,931 (+8.2, np 37, wheel thrown), **cB 13,930 (+7.2, np 32)**, cC 13,930 (+7.2, np 37); all chain MATCH + judge PASS.
Where the frames go vs the TAS (2,307): tosser wall +27 (body boost; floor: the hit cannot come before 12,283 and the
knockback state always lasts ~21 f), pillar +0 (+1 px), end +1 (that 1 px). vs the record: he loses ~17 at the tosser
wait but boosts, and his pillar bird boost (from a bird carried from far back; not reproducible, see "second" notes) is
7 f faster than the TAS: net we are +7.2.

## 3-2 lock round (second) (agent "second", 2026-10-24 21:00 - 2026-10-25 ~00:40; second half = X ~1252 to 3-3 control)

Result: `logs/l32_b_c4r_poweron.inputs.txt` = 3-3 control **13,936** (record +13.2), hp 16, np 32, FW, x 51 moving,
`$73` 0x80, `$BF` 98, `$62` 60 / timer 149 at control; judge PASS, `verify chain l32_b_c4r_chain` MATCH (RAM sha1
53775bb7a277). Built on first's HANDOVER v1 (X 1252 at 12,445), so 5-6 f behind first's cB/cC (13,930), which use the
better 12,438 base; the second-half parts are equivalent (pillar TAS +0, end +1..+2).

Findings:
* **Record's pillar = bird damage boost** (video 14,494-14,556; life 13 -> 10): a type-11 bird hits Ryu from the left at
  his jump peak off the X-1760 platform (~X 1824), knock-back 1 px/f right lands him on the branch (~X 1864), jump to the
  top. The bird is an OLD one carried from far back (two big birds on screen at Ryu X ~1430, video 14,240). Not
  reproducible from X 1252: the X-1314 bird (bang-bang homing, exact model `work/l32b/bmodel.py` = Mesen frame for frame:
  x speed +-1/16 px/f^2 toward Ryu's screen x, skipped on the 16-px scroll frames, freed at screen x < 8 or >= 248) is
  freed at its first left turn in a pure run (~Ryu X 1455); keeping it costs >= 8 f of stops and getting its
  left-to-right pass at X 1800-1830 costs >= 35 f (`bsearch2.py`); the X-1557 bird spawns at screen x 16 and needs ~10+ f
  of standing. A future attempt would have to keep the record's earlier bird alive in the FIRST half.
* **Legal pillar without boost = TAS +0** (`pbeam.py` with `--cell 4 --cap 3`: spatial diversity was essential; a plain
  score beam sat on the vine top y 116): grab the vine ~y 144, `A+Left` wall jump, `A+B+Left+Up` cling, land on the branch's
  right end (X 1882 y 128), `A`, Right to the top (X 1923 y 96 = TAS 12,718/12,719). FW throw optional (first's cB kills the
  pillar-top type 3 with an air slash instead).
* After the pillar, legal TAS rows track exactly to X ~2941 with two repairs: the bird at X ~2620 (air B 6 f after the
  TAS's; earlier B breaks the **Windmill X 2624 -> item 130**) and the free +10 X 2368 (air B ~TAS 13,002). The end
  (X 2941-3035: bird + type-3 walker 6 px right of the TAS's + dog) costs +1..+2 f; brute force of one jump + 2 slashes
  (`scan3.py`, 4,953 + 5,715 candidates) never passes without a hit; beams (`pbeam.py`, first's `abeam.py`) do.

Resume (Mesen, from first's handover states):
1. `python work/l32b/mk.py states/mesen/l32a_h1252.mst work/l32a/h_h1252.inputs.txt p12820 --tas 194 375`
2. `python -u work/l32b/pbeam.py work/l32b/h_p12820.inputs.txt states/mesen/l32b_p12820.mst f2 --goal 1922:96 --width 240
   --cell 4 --cap 3 --frames 140 --npset 17,22 --minhp 13 --alpha 'Right|A+Right|-|Left|A+Left|A|B+Right|Up+B|Up+Right|A+Up+Left'`
   (on first's r1229 base: same with `work/l32a/h_r1229.inputs.txt states/mesen/l32a_r1229.mst f3 --npset 22,27` -> X 1923 at 12,906)
3. `python work/l32b/follow.py <mst> <hist> <pillar rows> 194 860 <out> --edit 13374:B+Right` (lag 188 on r1229 with
   `--edit 13190:B+Right,13191:B+Right,13368:B+Right,13369:B+Right`), end beam `pbeam.py ... --goal 3035:192 --hgx 3035
   --hgy 192 --cell 3 --minhp 16`, then one Right to the play end, blanks, last 2 rows Right; `python -u -m ng.solve.verify
   finish 3-2 lock_32_ctl logs/l31_alt_b2r_poweron.inputs.txt work/l32b/c4r_stage.txt l32_b_c4r`, then `verify chain`.
Tools: `work/l32b/xp.py` (play + enemy dump), `scan.py` (row edits), `gt.py` (ground truth with `$84` bit 1 poked),
`bmodel.py`/`bsearch*.py` (bird phase), `lagrun.py`, `mk.py`.

## 3-3 lock round (agent l33, 2026-10-25 00:30-03:40, on the 3-2 candidates cB / cC)

Start: 3-3 control 13,930 (cB np 32 / cC np 37), hp 15, FW, x 51 moving, `$BF` 92, `$62` 7, timer 150, `$73` 0x80
(slots 0-2 empty: no 3-2 leftovers). NesHawk start = `states/l32_a_cB_end` / `l32_a_cC_end`; Mesen
`states/mesen/l33_cB_ctl.mst` / `l33_cC_ctl.mst` (`python work/l33/mk.py cB`: lock_32_ctl.mst + the 3-2 stage rows; key
RAM identical to NesHawk). Tools in `work/l33/`.

**Result: `logs/l33_p4t_poweron.inputs.txt` (cB): 4-1 control 14,866 = 936 f (record +24.5, TAS +108), kill row 191
(on the timer tick), timer 146, np 2 left, hp 13; judge PASS, chain MATCH (RAM sha1 18e6d0df5c57).** p4 = same line
killing on row 190 (14,868); fallback `l33_f1` 14,873. cC (37) is worse: p4t's rows on cC = +15 f (np 7 left) and a
7th wheel finds no slot.

Mechanics measured (Mesen, `work/l33/bpath.py`, `wtest.py`, `geo1.py`, `geo2.py`):
* Boss slot 7 (type $19), x/y at `$467`/`$487`, 3 px/f. Path from control (fixed): row 1 x 202 y 196 rising, apex y 127
  rows 24-28, lands x 43 y 208 row 55; sits 55-76; jumps right (rises 77-~104, apex x ~127, lands x 211 row 133); sits
  133-152; jumps left from 153 (passes x ~100 at row ~190).
* Volley: 3 shots (type $1A in slots 4-6) spawn at rows 76 and 153 with control `$BF` 92 (bit 7 set there). They are
  what hits a Ryu standing near x 70 at row 78 (not rocks). Same for any control `$BF` 52-103. After ~row 87 two of
  them CRAWL RIGHT at 2 px/f (y 208 and y 192; the third stays at x 47 y 176): a Ryu running right at 1.5 px/f is
  caught at ~row 127 (x ~132) and knocked back until ~row 165 -> that is why p4 misses the boss's 2nd sit. Every
  `--minhp 15` beam (no hit allowed) that pulled Ryu right died at rows 127-140: the shot has to be killed or let past
  (move left / stand) before running right.
* Fire Wheel flames: 3 flames at Ryu +4 px, x 4 px/f, y -6/-4/-2 px/f (a fan), live until hit / off screen; the next
  wheel needs all 3 gone (`$C8` = 0). Ground throw = anim 8 lock 16 f; air throw = no lock, but an air slash (anim 6)
  blocks Up+B until it ends.
* **The sitting boss is almost wheel-proof**: any throw at him during rows 55-76 lands <= 1 hit (geo1, 1,858 throws).
  Wheels land 3 hits when his box is big and close: his first descent (rows ~29-53: 3+3+1..3), his rise (a ground
  wheel from x ~70 at row 74 hits 3 at row 77), his second descent (rows ~105-132). The first-pass kill (TAS row 84,
  illegal 2-f slash mashing) would need ~6 sit hits from air slashes with Ryu low (sword vertical reach: Ryu y >= ~184)
  while dodging the row-76 volley and the rising body (rows 77-90): not found (best 6 HP left at row 85).
* Tally: 4-1 control = 13,930 + kill row + 3 x (timer + ninpo) + 301 (NesHawk = Mesen M + 301). Timer ticks at rows
  `$62`+1 + 61k (cB: 8, 69, 130, 191); `$62` at the kill carries into 4-1.

Searches: frame beams `bbeam.py` / `bbeam2.py` (flame-damage projection by a 20-row blank rollout, classes by projected
HP, `--wv` wheel-potential, `--xgoal` pull toward the boss's next sit) are greedy and only good on short windows; event
GA `ga.py` stalled at 6 HP; the result came from GA opening (`work/l33/pre67.txt`) + `bbeam2 --wv 0 --xgoal 180
--xfrom 90 --xw 0.04`.

Re-apply on a new 3-2 candidate (the fight is arrival-independent for control `$BF` 52-103; only the timer phase moves):
1. Add it to `CANDS` in `work/l33/lib.py` (power-on file, 3-2 stage rows, NesHawk end state); `python work/l33/mk.py <tag>`.
2. Replay p4t's rows (`work/l33/p4t.txt`, 191 rows to the kill; the fight does not depend on the arrival for control
   `$BF` 52-103): `python work/l33/probe.py <tag> work/l33/p4t.txt 200`. Then re-time the tail to the new tick (row
   `$62`+1+183 = the 4th tick): `python work/l33/tail.py <tag> work/l33/p4t.txt 166 170 <out rows>` (jump rows 166-167,
   last wheel rows 170-171; shifts both, prints the best M = kill + 3 x (timer + np), saves the best).
3. Search again: `python -u work/l33/bbeam2.py <tag> <out> --prefix work/l33/pre67.txt --width 300 --q 30 --frames 200
   --roll 20 --wv 0 --extra 6 --xgoal 180 --xfrom 90 --xw 0.04` (~15 min, 2 Mesen) -> `work/l33/bb_<out>.inputs.txt`.
4. `python work/l33/fix.py <tag> work/l33/bb_<out>.inputs.txt <rows>` (adds the Enforcer's forced hold rows after the kill
   row; without it the last 1-frame B fails the judge), then `python -u -m ng.solve.verify finish 3-3 <NesHawk 3-3 state>
   <power-on file> <rows> l33_<tag>` and `python -u -m ng.solve.verify chain l33_<tag>_poweron <power-on file>
   logs/l33_<tag>.inputs.txt`.
### Round 2 (2026-10-25 03:45-05:40, hits allowed; coordinator: 3-2 locked = cB)

**Result: `logs/l33_q4_poweron.inputs.txt`: 4-1 control 14,848 = 918 f (record +6.5, TAS +90), kill row 170, timer 147,
np 2, hp 11.** Line: p4t rows 1-89 (opening, W4 at the rise), then beam `q4`: `python -u work/l33/bbeam2.py cB q4
--prefix work/l33/pre89.txt --width 400 --q 25 --frames 210 --roll 20 --wv 0 --extra 4 --kbw 2.5 --kbfrom 95
--nothrow 121-148 --xgoal 150 --xfrom 135 --xw 0.06` (`--kbw` = penalty for being in knockback (anim 11), `--nothrow` =
no wheel while he sits). Ryu waits at x ~87 while the two crawling shots pass him (rows ~107-117), follows them right
(x 133 at row 145, boss 4), keeps the 6th wheel for his 3rd jump and finishes him while he rises (row 170).

Facts found:
* **His 2nd sit is immune to slashes too** (`work/l33/sit2.py`: ground and air slash patterns from x 141-185 during rows
  133-152: 0 hits; 1 hit only at row 130-131 while he lands). Damage happens only while he jumps (descents, rises),
  so a "2nd-sit kill" does not exist; the earliest real window after the first pass is his 3rd rise (row 153+).
* The crawling shots are not homing (x = 2 x row - 127 at y 192 and 2 x row - 147 at y 208) and slashes do not remove
  them. Ryu cannot pass them going right (2 px/f > 1.5 px/f); letting them pass while standing at x ~87 and following
  them costs nothing important, a hit costs ~38 rows of knockback (always a full arc).
* Ninpo residue: cB's 32 = 6 wheels + 2. The 2 cannot be spent (a wheel costs 5), so +6 f is fixed by the locked 3-1/3-2.
* Running right from row 64 (skipping the rise wheel) reaches x 171 at row 124 unhurt but the landing boss hits Ryu at
  row 127 (x >= ~172) and the plan lacks damage (beam `q2`: boss 2 at row 188).

(Round 1 text, superseded by round 2: the 2nd sit is immune.) Open: a 2nd-sit kill (rows 133-152, ~row 145) would be ~45 f better (record ~-18): Ryu must be at x ~156-187 (sword
reach on the sitting boss x 211) by row ~140 with the boss at <= 2 HP, AND survive the crawling volley shot (~row 127).
Beams with an x pull either got hit by it (p4-p8) or, with `--minhp 15`, stayed back at x ~100-150 (p9, boss 1 HP at
row 186 = no gain). Next idea: kill/let past the shot on purpose (slash it, or stand still until it passes ~row 100-110)
then run right, and use the macro beam `work/l33/mbeam.py` (walk/jump/turn/wheel steps, run from saved node states via
`sw.Ctx.run_from`) from that point. Also untested: arriving with the first-volley shots avoided by killing the boss's
`$72`=1 condition (another enemy alive) - not available in 3-3.

## 4-1 lock round (agent l41, 2026-10-25 03:20-06:05, PAUSED by the owner; rebased onto q4 at the end)

Start (q4, 3-3 LOCKED): 4-1 control 14,848, `$BF` 240, `$62` 19. **The control row 14,848 must be Right** (q4's file has a
blank there; Right on it gives x 33 at control like the TAS: no free frames). States: NesHawk `lock_41q_pre` (14,847) and
`lock_41q_ctlR` (14,848 after the Right), history `work/l41/hq14847.inputs.txt`; Mesen `states/mesen/l41q_ctl.mst`
(`python work/l41/mkq.py`). Tools in `work/l41/` (lib.py now on q4: F0 = 14,848; p4t versions: `lib_p4t.py.backup`).
Rows files `work/l41/*.txt` are STAGE rows after the control row (row i -> frame 14,848 + i); `verify finish` files
`s_*.txt` = [Right] + those rows, from `lock_41q_pre`.

**Result: only a fallback is verified: `logs/l41_c2a_poweron.inputs.txt`, 4-2 control 17,056 (2,208 f, record +16.4),
J&S / 0 / hp 16, judge PASS, verify finish OK, verify chain NOT run.** The same rows on Mesen reach the stage end (X 636)
at 16,856 = 4-2 control ~17,008 (**record ~-31**); NesHawk loses ~48 f to two eaten presses in the room-14 ladder climb.

What was found (all frames below on the q4 axis = p4t axis - 18 = TAS axis + 279):
1. **NesHawk misreads**: on some frames NesHawk's game keeps last frame's pad (`$2A` = previous value); Mesen never does.
   They only matter on frames where the row changes. They depend on the path (not a fixed timeline), ~1 per 50-400 f.
   `python work/l41/nhcmp.py <rows>` lists them ("eaten") and the first NesHawk/Mesen divergence; the fix is to move
   that press/release by 1 frame (Mesen re-check + NesHawk re-check). On q4 the r2c X-1442 spin B (15,787) was eaten:
   fixed by B on 15,786-87 (c2a). Still eaten in c2a: **16,355 and 16,402** (ladder cycle releases) -> fix next.
2. **Block (15,700 TAS)**: a plain jump from the y-96 platform cannot reach the middle block (lands ~X 1,640, block edge
   ~1,656); the type-8 bird knockback is required (r2c's route). Grid `work/l41/blkp.py` (jump frame x air-B spin):
   best = r2c's jump (TAS 15,596) with **pure Right afterwards** (no block-exit fiddle): X >= 1,767 y 128 4 f earlier
   than r2c_fix. A spin kills the bird but then Ryu falls into the pit. Then **legalized TAS rows at TAS lag +4 stay in
   sync (<= 1 px) to room 14**: room 14 at TAS 16,009 + 4 (`work/l41/graft.py <prefix> <P> <d> <end>`).
3. **Room 14 and 15 are LADDER tiles (kind 9) on Ryu's right**: the 2-1 ladder cycle `R, R+U, R+U, A+L+U, A+L` (1.8
   px/f) replaces r2c's C8: room 15 at TAS 16,107 + 12 (r2c +39) (`work/l41/ladp.py`, `work/l41/nhroom.py` scans).
4. **Room 15**: the ladder top is y ~100 (no way onto the y-96 top from the ladder); r2c lands on the branch (y 128,
   X 96-127) and jumps right through the one-way y-96 platform. The bird (type 11) hits the climber at y ~130. Local beam
   `r15b` from 16,468 (q4 axis) found: spin (B, np 5 -> 0) kills the bird, top at X 161 y 96 at 16,532 (q4) = 20 f
   better than r2c; then beams `top1`/`top2` (pure-run pace minus ~7 f, no ninpo for the X-341 enemy). End: no jump
   on the last tile (a jump at X 636 freezes the end trigger).
5. Mesen speed here is ~250 frames/s per core; frame beams with an X score fail on knockback routes (block) and on
   cyclic climbs; parametric grids (`work/l41/psearch.py` + blkp/r15q) and short local beams work.

Resume (q4):
1. `python -u work/l41/nhcmp.py work/l41/c2a.txt` -> eaten 16,355 / 16,402; shift the ladder presses there (or pick another
   cycle phase from `python -u work/l41/ladp.py work/l41/c2a.txt 16292 <out>`; Mesen room 15 at 16,400) and re-check
   until NesHawk room 15 = 16,400/16,401 and the room-15 rows (r15b/top1/top2) replay; then
   `python work/l41/ed.py ...` / build `s_<tag>.txt` = [Right] + rows and
   `python -u -m ng.solve.verify finish 4-1 lock_41q_pre work/l41/hq14847.inputs.txt work/l41/s_<tag>.txt l41_<tag>`,
   power-on = hq14847 + logs/l41_<tag>.inputs.txt, then `python -u -m ng.solve.verify chain l41_<tag>_poweron
   logs/l41_<tag>_poweron.inputs.txt` and the judge.
2. Then improve: keep np 5 through the room-15 climb (beam `--np "np>=5"`) so the top run can spin at X ~341 (pure run,
   ~7 f); re-beam room 15 with the bird as a boost (TAS does it); the block grid with neutral pulses (`blkp.py b`).

### 4-1 lock round, resumed (l41, after the pause)

**c3b verified: `logs/l41_c3b_poweron.inputs.txt`, 4-2 control 17,020 = 2,172 f = record -19.6 (TAS +59), J&S / 0 / hp 16,
judge PASS, `verify chain l41_c3b_chain` two replays MATCH (RAM sha1 ba7fe3e2afd4).**
* The "+48" of c2a was not the ladder misreads: NesHawk = Mesen frame-for-frame through the whole line
  (`python -u work/l41/nhcmp.py work/l41/c2a.txt`: no divergence; the eaten edges 16,355 / 16,402 are harmless).
  It was the **4-1 -> 4-2 cutscene**: Ryu reaches X 636 at 16,856, the cutscene starts at 16,857 (`$BE` = 4, gm 0),
  and Start skips it only from 16,864 (Mesen) / **16,865 (NesHawk)**; verify's to_control pressed Start much later.
  Rule for every 4-1 candidate: end the play rows at the stage end, then blanks, **Start x2 at stage end + 9**
  (check on NesHawk with `work/l41/nhgoal.py l41q_c3_16800 120 "stage==9" <rows...>`).
* Split per room (q4 axis, TAS axis + 279): room 13 = TAS +4 (block knockback route + legal TAS rows, lag 4: frozen,
  grid `blkp.py a|b` (jump frame, air spin, neutral pulses) finds nothing better); room 14 = ladder cycle, room 15
  entry TAS +14; room 15 (climb + top run) = TAS +46 at the stage end; cutscene skip.
* NesHawk-matched states on c3b: `l41q_c3_16150`, `l41q_r14` (16,292), `l41q_r15` (16,400), `l41q_r15b` (16,468),
  `l41q_c3_16800`; Mesen `states/mesen/l41_q16030/16292/16400/16468/16330.mst`; histories `work/l41/hq_<f>.inputs.txt`.
* Re-verify: `python -u -m ng.solve.verify finish 4-1 lock_41q_pre work/l41/hq14847.inputs.txt work/l41/s_c3b.txt l41_c3b`,
  power-on = hq14847 + `logs/l41_c3b.inputs.txt`, `python -u -m ng.solve.verify chain l41_c3b_chain logs/l41_c3b_poweron.inputs.txt`.

### Room 15 + top run (agent r15, 2026-10-25 12:20-; on c3b's room-15 entry 16,400)

**Result: `logs/l41_r15_a_poweron.inputs.txt`, 4-2 control 17,000 (2,152 f, record -39.6, TAS +40), J&S / 0 / hp 16 at
control; verify finish + `verify chain l41_r15_a_chain` (MATCH, RAM sha1 50ab6cb39513) + judge PASS.** 20 f better than c3b.
* Room 15 = c3b's ladder cycle (max legal rate; y 143 at 16,475), wall jump A+Left 16,476, **Down+B 16,478-79 (regular air
  sword, 0 ninpo) kills the bird as it passes**, snap onto the branch (y 128) at 16,486, standing jump A+Right
  16,487-88, over the X 128-143 block at y <= 96 (X 140 at 16,506 vs c3b 16,518), top y 96 X 163 at 16,521.
* Why no bird boost: the column (ladder X 128-143 + solid block y 96-111 on top) separates Ryu from the one-way top.
  Knockback is 1 px/f right + up to 29 px; a hit in the air left of the column ends when Ryu touches it (clings at y
  122 or 114), and the bird's only early pass (16,478-81, homing on Ryu's x from the room appear) finds Ryu at y >= 134,
  so a boost cannot reach y 96. Hits while clinging give no knockback. The TAS's boost needs its L+R zip (Ryu ends right
  of the column under the one-way top). The record's bird contact on the branch is a loss, not a boost.
* Kill side effect: a new bird spawns at X 16 (16,489) and catches the running Ryu at ~X 250 (16,581) -> the top run's
  J&S spin (B+Right 16,645-46, np 5 -> 0) kills it and the y-160 walker; the beam `topA` runs at exact pure pace
  (X = 163 + 1.5 (f - 16,521)), stage end X 637 at 16,837, Start 16,846-47 (end + 9 = NesHawk's earliest skip), control
  17,000 = room-15 entry + 600.
* Graft: `work/r15/r15a_after16400.txt` (frames 16,401-16,847 relative to the room-15 entry 16,400). Room 15 has no `$BF`
  reader; the bird spawns at the room appear and homes on Ryu's x, so the rows should shift with an earlier entry.
* Re-verify: stage rows `work/r15/s_topA.txt` (= [Right] + `work/r15/st_topA.txt`):
  `python -u -m ng.solve.verify finish 4-1 lock_41q_pre work/l41/hq14847.inputs.txt work/r15/s_topA.txt l41_r15_a`,
  power-on = hq14847 + `logs/l41_r15_a.inputs.txt`, then `verify chain l41_r15_a_chain logs/l41_r15_a_poweron.inputs.txt`.
* Room 14 is at its floor for us: the 1.8 px/f cycle gives room 15 at TAS +14 from a TAS +4 room-14 entry (TAS climbs at
  2.0 with illegal L+R); every start frame / phase variant ties (16,400 q4). A wider `work/w21/cycles.py --up` run on
  `states/mesen/l41_q16330.mst` crashed after ~50 min (that script has no fcka keepalive: import work/l31t/fcka first).
  Room 13 is frozen at TAS +4. **What's left in 4-1 is room 15** (second agent): the bird boost and a climb that keeps
  5 ninpo for the top-run spin (c3b's top run is ~7 f slower than pure running).
* **Update (r15, 14:40): `logs/l41_r15_c_poweron.inputs.txt` = 4-2 control 16,998 (record -41.6), verified (chain MATCH
  76035d5f3074, judge PASS).** The room 14 -> 15 transition rows (16,401-16,421) do nothing in game, so the room-15 cycle
  can start with A+Left+Up on the appear frame 16,422 (3 f earlier than c3b's phase). NesHawk misreads 16,429 (and
  16,418) on this path: a plain 5-f cycle from 16,422 breaks on NesHawk (Ryu loses the wall and falls), a 6-f first
  cycle (R+U on 16,425-27, A 16,428) moves 16,429 to a harmless edge; net -2 f. Departure A+Left 16,473-74 from y ~148,
  Down+B 16,476-77, jump 16,485, top beam `topC` at pure pace, freeze 16,835, Start 16,844-45. Stage rows
  `work/r15/st_topC_16844.txt` (verify file `work/r15/s_topC_16844.txt`), graft `work/r15/r15c_after16400.txt`.
* Floor of this route (room 15): the ladder cycle is max-rate, the branch snap needs a wall jump from y <= ~148, the
  standing jump is the only way over the block, and the top run is pure pace; the remaining gap to the TAS in room 15
  is the L+R zip (illegal). Gains for 4-1 now come only from earlier room-15 entry (rooms 13-14).

## 4-2 lock round (agent l42a, 2026-10-25 13:55-20:30; control -> X ~2,950, on r15_c = 4-2 control 16,998)

**Result:** my line `work/l42a/b2_k3.txt` (stage rows, row 1 = Right on the control row 16,998) reaches **X 2,950 at
18,932 (TAS ~+11), hp 15, np 10, J&S**; the wall agent finished it -> `logs/l42_w_k932a_poweron.inputs.txt` = **4-3
control 19,299 (record -2.8)**, verified. My own fallback `logs/l42_a_rough1_poweron.inputs.txt` (19,358, record +56).

How the line is built (all Mesen-checked, NesHawk = Mesen except the harmless misread at 17,074):
1. Legal TAS rows at lag 316 track the TAS exactly from control (Right on the control row) to X 1,310; the throwers
   (`$BF` 81) need the J&S spin 12 f earlier (17,828); then exact sync again through the TAS's L+R jump (drop its 1-f Left,
   Right instead of L+R) to X 2,312 at 18,496 (= prep `work/l42p/s42_to18180.inputs.txt`, 2 f ahead of the TAS).
2. **X 2,336 = forward damage boost**: no jump at 18,479; the trailing type 13 (alive because the TAS's rear slash needs
   L+R) hits from behind at 18,493 (hp -1), knockback +1 px/f right and up over the birds, invincibility through them;
   beam `k1` (TAS-distance, lag 325) -> X 2,560 at 18,672 (TAS +9, hp 15).
3. Beam `k3` (pure pace, +10 X 2,784, no spin) -> X 2,950 at 18,932.

Facts measured here (details in LOCKED_CHAIN "Agent notes (4-2)"):
* Facing is fixed in the air (`$84` bit 0x40); Left in the air only stops x. A ground Left-turn jump drifts ~0.7 px/f.
* With J&S and ninpo >= 5 every air B spins, **Down+B included**. A lantern broken by a spin gives net 0 (+5 X 784 at
  17,465). Ground slashes do not reach y-160 lanterns and freeze 14-16 f.
* A spin anywhere 18,391-18,521 with 5 ninpo keeps TAS pace to X 2,708 (hp 16), but the budget needs 15 ninpo by X 1,310
  (thrower spin + the 18,242 slash that becomes a spin + this one); only +5 X 704 is on the line -> not affordable.
* The TAS's air slash at 18,242 is required (it stops the type-13 jumper at X 1,957); no-B jump variants all get hit.
* The gap X 2,503-2,550 (no floor) makes lines that arrive late at X ~2,480 lose 40+ f (prep's beam line to X 2,500
  falls into it).

Tools `work/l42a/`: `lib.py`, `tmod.py` (legal TAS rows at a lag + edits), `ed.py` (row edits + TAS divergence),
`tr.py` (per-frame trace with enemies vs TAS), `beam.py` (TAS-distance beam), `beam2.py` (diversity beam: `--tas LAG`
or progress score, `--npmin`, `--nospin`, `--keep slot:type`), `nhchk.py` (NesHawk vs Mesen + misreads + state save),
`np5.py` / `spin5.py` (ninpo-poke experiments), grids `g1-g5.py`, `glan.py`, `g784.py`.

Resume:
* `python -u work/l42a/beam2.py work/l42a/b2_k1.txt 1675 2950 <tag> --width 120 --frames 300 --tas 325 --npmin 10 --nospin 1 --keep 5:11`
  (bird-alive continuation for the wall boost; `b2_kb1` = first try, bird hits from the front at 18,844).
* States: NesHawk `l42a_k18880`, `l42a_k18932` (b2_k3), `l42a_b18760` (b2_kb1, bird alive, 54 px behind),
  `lock_42_pre/ctl/ctlR`; Mesen the same names under `states/mesen/`.
* Verify: `python -u -m ng.solve.verify finish 4-2 lock_42_pre work/l42a/h16997.inputs.txt <rows> <out>` (rows start with
  the control-row Right), then `python -u -m ng.solve.verify chain <name> <power-on file>`.

## 4-2 lock round (wall agent "wall", 2026-10-25 14:25-22:15; exit wall X ~3,000 -> stage-end trigger)

**Result: `logs/l42_w_k932b_poweron.inputs.txt` = 4-3 control 19,297 (2,299 f, record -4.8, cum -204.8), hp 15 / np 10 /
J&S, verify finish + `verify chain l42_w_k932b_chain` (MATCH, RAM sha1 2ca737481fff) + judge PASS.** = agent a's
`work/l42a/b2_k3.txt` rows to 18,932 (X 2,950) + wall rows `work/l42w/wall_k932c.inputs.txt` (trigger 19,017 = TAS +21).
Earlier: `l42_w_k932a` 19,299 (record -2.8, ladder-cycle climb, trigger 19,019).
* **Geometry:** the exit wall is a LADDER column (kind 9) at X ~3,040, y 80-191, exit tile above; floor y 192; the short
  post (ejecting block, top y 176) at X ~2,977-2,999 is the only higher footing. Trigger = first frame with `$5C` = 0
  (Ryu X 3,035, y <= ~84); 4-3 control = trigger + 280 on the verify axis. Running into the post's side stops Ryu at
  X 2,971 (you must jump onto it).
* **Best no-boost wall:** land on the post, A+Right off it at X ~2,999 (2 f hold), Right; the jump apex (y 128) meets the
  ladder at X 3,035 (pure pace). Climb: either the 1.8 px/f ladder cycle `A+L+U, A+L, R, R+U, R+U` (trigger = contact +
  28) or, 2 f better, a wall-jump climb found by a bounded frame beam: A+Right just before the contact, A+Left on the
  contact frame, then A+Left x2 every 6 f with Right between (`wb_k932c`). From TAS 18,596 the same structure gives TAS
  +14 (`we_t596_h16`).
* **Bird boost: LEGAL** (write-up `knowledge/technique_4-2_bird_boost.md`): on the TAS state the TAS's own approach
  (A+Right off the post, Right only) takes the type-11 bird's hit from behind in the air at X 3,025 (hp -3); the
  knockback (+1 px/f toward the wall, y -3/-2 px/f, 60 f invincibility) lifts Ryu to y 106 at the ladder; legal climb
  -> trigger TAS +2 (`work/l42w/wb_t596d.inputs.txt`, judge PASS, NesHawk = Mesen). The TAS's L+R / 1-f presses are only
  in its climb after the contact. A 522-position bird-poke map (`map620.tsv`): only hits from behind with Ryu airborne
  at X 3,014-3,029 boost (trigger TAS +1..+13); front hits push Ryu away from the wall.
* **On our chain the boost is not reachable at a gain**: the bird's ~250-f homing swing (fixed by its spawn near X 1,600
  and the line's lateness) has it in front of Ryu at the post on every line we have; keeping it alive costs hits
  (18,738-43, 18,839-43) or the +10 X 2,784; waiting at the post (2-42 f, 7,094 jump variants) only meets the trailing
  type 13, which never boosts. Search table in the technique file.
* Tools `work/l42w/`: `wenum.py` (2-stage: approach jumps/waits until the ladder contact via Mesen stop conditions, then
  climb patterns; writes `we_<tag>*.inputs.txt` + `_top.json`), `nhpick.py` (NesHawk check of the top results),
  `wbeam.py` (frame beam: `--bound` for exhaustive-ish climbs, `--contact`, `--goalx`, `--alive <slot>`, `--hpmin`; skips
  L+R/U+D children - the prep beam's Leg.emit can force-hold one direction while the other is chosen), `wpause.py`
  (wait-for-the-enemy search), `wmap.py` (bird-poke map), `nhwall.py` (NesHawk vs Mesen + trigger), `nhtas.py`,
  `mkwall.py` (TAS-line Mesen states 18,596/620/642). Mesen here runs ~300 fps per core: keep enumerations < ~5k runs.
* Pipeline lesson: cut wall rows at the trigger leave the last press 1 f long -> judge FAIL; repeat the last row once.
  NesHawk misreads appear on some lines (rough r18963 line: 19,019 eaten) - always `nhwall.py`/`nhpick.py` first.
* Re-verify: `python -u -m ng.solve.verify finish 4-2 lock_42_pre work/l42a/h16997.inputs.txt work/l42w/s_k932b.txt
  l42_w_k932b`, power-on = `work/l42a/h16997.inputs.txt` + `logs/l42_w_k932b.inputs.txt`, then
  `python -u -m ng.solve.verify chain l42_w_k932b_chain logs/l42_w_k932b_poweron.inputs.txt`.
* The wall from any new arrival: `python -u work/l42w/wenum.py <mst> <frame> --hist <power-on history> --j1 0:30 --h 100
  --holds 2,12 --pause 0 --tag <t>`, `python -u work/l42w/nhpick.py <neshawk state> work/l42w/we_<t>_top.json`, then the
  climb beam from ~3 f before the contact: `wbeam.py <mst> <frame> --hist <h> --prefix <rows to contact-3> --width 5000
  --frames 40 --hpw 0 --bound <best trigger> --br 2.5 --alpha 'Right|Right+Up|A+Left|A+Left+Up|-|Up|A|A+Up|Left|Left+Up|A+Right|A+Right+Up'`
  (~1.5 h).

## 4-3 lock round (agent l43, 2026-10-25 21:30 - 2026-10-26 ~04:00; rooms 17-18 + room-19 entry on k932b)

Split with agent r1920 at 00:05: **r1920 owns rooms 19-20 on the chain** (block, room-19 second half, exit, room 20,
trigger), built from my prefix `work/l43/s_m19.txt` rows to 20,480. I own rooms 17-18 and the room-19 entry.

**Result (my part):** stage rows `work/l43/s_m19.txt` (row 1 = Left on the control row 19,297; legal PASS on the
k932b history; NesHawk = Mesen, 0 differing frames to 20,710 incl. the pb continuation, `work/l43/nhchk.py`):

| segment (frames) | rows / how | entry state (Mesen / NesHawk) | vs TAS (lag) |
|---|---|---|---|
| 19,297-19,446 room 17 | prep `pre2` rows 1-150 (room-17 legal climb) | base `states/mesen/l43_k932b19296.mst` / `states/l43_k932b19296.State` | room 18 at 19,427 (+13) |
| 19,447-19,551 room-18 entry | `d*4, (R+U, A+L+U, A+L, R, R+U)*5, R...` chimney left wall <-> box (2 px/f), box top 19,485 | - | X 218 at lag 364 (+26; record ~+38) |
| 19,552-19,643 | legalized TAS rows 19,188-19,279 at lag 364 (exact; +5 X 272 spin-break, net 0) | `l43_s19598` (Mesen) / `l43_pb_19598` | exact |
| 19,644-19,709 chimney + lip | beams ch1 (TAS distance) + lip3 (progress): single-wall C8 on the X 346 wall; the climb carries Ryu over the lip | `l43_s19709` | X 368 y <= 96 at 19,709 (+38) |
| 19,710-20,065 | legalized TAS rows from 19,351 at lag 376 (exact from 19,763; spin on +10 X 592 -> np 15) + spin at TAS-eq 19,655 (kills the type-19 flyer and the blade, np 10) | - | exact to X 881 |
| 20,066-20,091 exit | beam ex1: exit LADDER (y 80-111) climb, no boost | `l43_s20091` / `l43_pb_20091` | room 19 at 20,091 (+42) |
| 20,092-20,225 room-19 entry | beam e19 (ladder at y 232 -> floor -> box -> grounded turn -> jump onto the pillar) + run to X 212 | `l43_s20225` | X 212 at 20,225 (+58) |
| 20,226-20,480 | legalized TAS rows 19,830-20,084 at lag 396 (exact; TAS spins 19,930 / 20,027 -> np 0) | `l43_s20480` / `l43_pb_20480`, history `work/l43/h20480.inputs.txt` | X 593 y 165 at 20,480 (+58) |

Findings:
* **4-3 control on k932b is really row 19,296** (Left there moves Ryu x 224 -> 222 on 19,296; `verify finish` reports
  control + 1, as for k932a 19,299 vs 19,298). The whole l43 prefix replayed from `states/mesen/l43_k932b19295.mst` with
  Left on 19,296 is identical one frame earlier (room 19 at 20,090). Amending locked row 19,296 (blank -> Left,
  pre-control, like the 1-1 amendment) saves 1 f for free.
* Legal chimney limit at X 346: best legal 5-7 f cycles climb 44 px in 30 f (`work/l43p/cycles.py` on `l43p_tas19290`,
  `work/l43/log/cyc18b.out`) vs the TAS's 48 px in 25 f; with the lip, the chimney costs +12/+13 vs the TAS.
* The TAS's room-18 exit boost needs the type-19 flyer ~35 px behind Ryu at the platform end. The flyer is released
  by the type-4 walker (spawned when the camera reaches scroll 193 = Ryu X 320) 138-139 f after its spawn and flies at
  1.82 px/f at y 82; our 13-f chimney loss puts it 25 px closer, it hits at X 881 (20,051) in the last jump and Ryu
  falls into the pit. Killing the t4 removes the flyer (no boost either). Options measured: spin (np -5, used), absorb
  the hit + ladder (`nb18`: hp 13, np 15, ~22 f later), ground slash (~14+ f). So np 15 at room 19 costs >= 14 f.
* Room-19 type-17 flyers spawn only while the type-1 gunner (X 930 y 128) lives; the block's type-20 flyer respawns
  when it leaves the screen (see LOCKED_CHAIN agent notes).

Resume:
* Rebuild/replay: `python work/l43/tr.py work/l43/s_m19.txt 19297 20480 20 e` (Mesen trace vs TAS; `--save <name>`).
* NesHawk check: `python -u work/l43/nhchk.py <stage rows> <save frames|-> <tag>`.
* Re-graft if 4-2/4-3 control changes: set `L43_CHAIN`, `L43_CTL`, `L43_BASE` (env) and replay the rows: room 17 has
  no enemies; the segments are TAS-row syncs at fixed lags (re-run `work/l43/sync.py` / `follow.py`) and beams
  (`work/l43/beam.py <prefix> <N> <tag> ...`, see the commands in `work/l43/log/*.out` headers) - the floor enemies,
  the t4/t19 flyer and the throwers move with the arrival.
* Finish a stage candidate: `python -u -m ng.solve.verify finish 4-3 l43_k932b19296 work/l43/h19296.inputs.txt <rows> <out>`
  then `python -u -m ng.solve.verify chain <name> <power-on file>` and
  `python check_inputs.py <power-on file> --period 5 --hold 2 --release 2 --windows 600:109,1800:246`.

## 4-3 lock round (rooms 19-20) (agent r1920, 2026-10-25 21:25 - 2026-10-26 ~09:00)

Owner of rooms 19-20 on the chain (from l43's `work/l43/s_m19.txt` / `s_p19.txt` rows to 20,479). Frames below are on the
coordinator's 1-frame-earlier axis: **4-3 stage row 1 = Left on 19,296** (history = k932b rows 1-19,295, base Mesen
`states/mesen/l43_k932b19295.mst`, NesHawk `states/l43_k932b19295.State`); every l43/r1920 stage-rows file replays
identically one frame earlier (checked: 0 differences over 1,558 rows).

**Result: `logs/l44p_r1920_c2_poweron.inputs.txt` (power-on to the row before 5-1 control): 4-3 trigger 21,578, 4-4 control
21,857 (2,561 f = record +3.8), 5-1 control 22,629 (best tosser band), v = `$62` 13, hp 14 / np 5 / J&S.** NesHawk = Mesen
(nhchk 0 differing frames), verify finish OK, `verify chain l43_r1920_c2_chain` MATCH (d4e9ccff650f), judge PASS.
c1 (`logs/l44p_r1920_c1_poweron.inputs.txt`, 4-4 control 21,863) is the same line with the +5 X 656 ninpo plan.

| segment | how (tools `work/r1920/`) | frames (new axis) | lag vs TAS |
|---|---|---|---|
| room-19 entry -> X 593 | l43 s_m19 (no launch) | 20,090 / 20,479 | 380 / 395 |
| stepped block | beam `blkR` (`gb_blkR`): C8-type kicks off the face, drift over the top at 0.5 px/f facing left, no spin (np 0) | top X 612 at 20,523 | 411 |
| block top -> X 871 | beam `r19S` (TAS distance at lag 412, hits allowed, item kept) | 20,706 | 420 |
| X 871 -> last roof X 1,088 | beam `r19U` | 20,853 | 420 |
| exit | grid `exitgrid2` (jump at once, Right 37, ladder cycle `R RU RU ALU AL`; a thrower-blade hit from behind at y ~160 lifts Ryu ~30 px) | room 20 at 20,962 | 465 |
| room-20 entry | grid (ladder cycle x3 -> y-192 step -> y-160 step -> turn on the y-128 step -> y-96 step) | pillar X 168 at 21,143 | 467 |
| -> X 392 | legalized TAS rows 20,677-20,820 (exact) | 21,287 | 467 |
| X 392 chimney | zigzag grid: Left into pillar A's right face (cling, vy>=0), A+Right kick, Right to pillar B (cling), A+Left kick back, cling A, A+Right kick over B | B top X 428 at 21,346 | ~486 |
| -> trigger | c2: beam `r20B` (+10 X 464 taken, ONE spin -> np 5 at the y-96 platform X 571, 21,459) + jump at once; c1: np 0 then jump/pause/slash for +5 X 656 | trigger 21,578 (c1 21,584) | 504 |

Findings:
* Entry pillar (rooms 19/20, X 160-207, top y 128): the ladder face tops out at a cling y 148; a jump-off peaks ~y 133 ->
  the top is not reachable from the face. Room 20's y-160 step -> pillar jump misses by 1 px (X 155 at y 129).
* Facing is fixed in the air; backward air control = 0.5 px/f. Wall kicks: A + direction away from the wall on a
  contact frame; a cling (an 10) only happens moving INTO the wall with vy >= 0, and holds still until the next kick.
* Room-19 gunner (type 1, X ~930 on the y-128 platform) walks into Ryu; slashing it removes the type-17 flyers (= no TAS
  exit boost, l43's finding); keeping it alive (beams `r19V/W/W2`) cost 30+ f in hits. The thrower's blade (type 18)
  can lift Ryu toward the exit ladder when it hits from behind.
* `gbeam.py` must keep the art: an early beam caught the room-19 FW X 816 trap (now `--keep` + item check built in).
* Mesen vs NesHawk: a jump pressed on a landing frame (c3 at 21,427) jumps on Mesen but not on NesHawk -> always run
  `work/l43/nhchk.py` (with `L43_CTL=19296 L43_BASE=states/mesen/l43_k932b19295.mst`).
* Unfinished (c3): beam `r20C` from the zigzag reached the trigger at 21,570 (np 5, 4-4 control 21,849 = record -4.2) on
  Mesen, but NesHawk diverges at that landing-frame jump (21,427); `work/r1920/c3c.txt` delays it 1 f (NesHawk = Mesen)
  and needs a re-beam from 21,429 (`gb_r20D`, `states/mesen/r20_c3c_21429.mst`).

Resume:
* State on any stage-rows file: `python work/r1920/mkst.py <stage rows> <n> <name>` (frame 19,295 + n; history file
  `work/r1920/h_<name>.inputs.txt`).
* Beams: `python -u work/r1920/gbeam.py <mst> <F> --hist <h> [--prefix rows] --goal EXPR --h EXPR --rank EXPR --keep EXPR`
  (examples with exact arguments: first lines of `work/r1920/*.out`); grids: `work/r1920/grid.py <mst> <F> "<cond>" "<spec with {n:lo:hi}>"`.
* Candidate: stage rows -> nhchk -> `python work/l44p/graft.py <4-3 power-on> <mst on path> <F> <tag>` ->
  `python -u -m ng.solve.verify finish 4-3 l43_k932b19295 work/r1920/h19295.inputs.txt <stage rows> <out>` ->
  `python -u -m ng.solve.verify chain <name> logs/l44p_<tag>_poweron.inputs.txt` + check_inputs.
* Biggest remaining losses vs the TAS: exit of room 19 (+45: no boost), room-19 block (+16, np 0), X 392 chimney (+19),
  room-19 entry without the launch (+16, l43).
