# Acts 5-6 legal stages (agent a56) - notes

## STATUS (read first)

* 2026-10-23 06:00 ROUND 5 PAUSED by the owner (usage limit); all r5 jobs stopped. **New verified: 6-4a TAS +52
  (`logs/a56_6-4a_r5f1`, was +77, PASS, in logs/results.json).** 6-2 reaches room 40 on Mesen 33918 (~4 f ahead of the
  record's ~33922); 6-3 room 43 to wpos 844 at Mesen 36007 (TAS lag ~76); NOTHING else verified. Resume: Round 5 end.

* 2026-10-23 05:30 (round 5, in progress): **6-4a Masked Devil now TAS +52** (`logs/a56_6-4a_r5f1`, r4m1 + one Fire
  Wheel throw found on Mesen, NesHawk verified, PASS; was +77). Mesen tools in `work/r5/` (Round 5 section at the END).

* 2026-10-23 04:10 (round 4): **6-4b Jaquio now ~7 f AHEAD of the record's split** (`logs/a56_6-4b_r4k2`, TAS +145,
  verified, PASS; ROM hit rules + a model planner `work/r4/jqplan2.py`); 6-4a improved to TAS +77 (`a56_6-4a_r4m1`).
  6-2 room 36 is legal at TAS pace; 6-3 room 42 and 5-2 rooms 23/24 have hand lines; no new complete level stage.
  Round 4 section + results table + NEXT at the END of this file.

* 2026-10-20 08:00 (round 3): latest results table and NEXT list are at the END of this file ("Round 3 results").
  Jaquio is deterministic (no RNG); 6-2 room 37 "wall" = camera not engaged (fixed); 6-4b now logs/a56_6-4b_r3k1 (TAS +401).

* 2026-10-19 07:40: analysis done; own TAS-guided legal beam search written (`ng/stages/a56_beam.py`,
  driver `ng/stages/a56_solve.py`); first runs (5-1, 6-1) from the TAS stage-start states in progress.
* 09:00: 6-1 SOLVED from the TAS start = TAS time (load 31487, +0, `logs/a56_6-1_c8.inputs.txt`, PASS).
  5-1 first legal solution +376 f vs the TAS (`logs/a56_5-1_c8`, fallback; re-search running).
  Running: chain A (5-1 .. 5-4 from the TAS 5-1 control state), chain B (6-2 .. 6-5 from my 6-1 end state).
* Results table (filled in as stages finish) is at the bottom.
* 11:50: boss work: legal slash cancel found (below), Jaquio/demon targets mapped (below). 6-2 is stuck at a
  wall-clip spot (room 37, abs x 782, y 48: the TAS climbs inside a wall with U+D+L); chain B stopped there.

## Stages owned

`$6D` 12..21 = 5-1, 5-2, 5-3, 5-4 (Bloody Malth), 6-1, 6-2, 6-3, 6-4a (Masked Devil), 6-4b (Jaquio), 6-5 (Demon).
Rooms: 5-1 = 22; 5-2 = 23-26; 5-3 = 27-33; 5-4 = 34; 6-1 = 35; 6-2 = 36-40; 6-3 = 41-44; 6-4a = 45; 6-4b = 46;
6-5 = 47.

TAS 4751M frames (bk2 numbering): control / next load.

| stage | control | next load | control->next control | record (s -> f) |
|---|---|---|---|---|
| 5-1 | 22125 | 24276 | 2303 | 40.93 s = 2460 |
| 5-2 | 24428 | 26457 | 2181 | 40.90 s = 2458 |
| 5-3 | 26609 | 29108 | 2651 | 49.67 s = 2985 |
| 5-4 | 29260 | 29911 | 803 | 13.40 s = 805 |
| 6-1 | 30063 | 31487 | 1576 | 26.37 s = 1585 |
| 6-2 | 31639 | 34410 | 2923 | 52.47 s = 3153 |
| 6-3 | 34562 | 37126 | 2716 | 48.47 s = 2913 |
| 6-4a | 37278 | 37935 | 809 | 13.63 s = 819 |
| 6-4b | 38087 | 38781 | 846 | 16.60 s = 998 |
| 6-5 | 38933 | END seen 39530 | 597 | 12.57 s = 755 |

## Where the TAS breaks our rules (frames from `logs/tas4751.trace.csv`, `work/a56/analyse_tas.py`)

| stage/room | L+R frames | U+D(+dir) frames | notes |
|---|---|---|---|
| 5-1 (22) | 19 (23056, 23098-99, 23112-26, 23280) | 0 | few; mostly press cap (75 one-frame A/B holds) |
| 5-2a (23) | 1 | 64 (24641-61, 24821-73) | U+D+L wall wobble |
| 5-2b (24) | 28 (24899-24938) | 0 | entry L+R |
| 5-2c (25) | 0 | 12 (25806-17) | |
| 5-2d (26) | 93 (25860-90, 26065-83, 26134-76) | 2 | |
| 5-3a (27) | 0 | 76 (26705-51, 26940-66, 27001-12) | |
| 5-3b/d/f (28/30/32) | 33 each (room-entry L+R clip, same pattern) | 0 | |
| 5-3c/e (29/31) | 4 / 0 | 12 / 27 | |
| 5-4 boss | 0 | 0 in the fight (87 U+D only during the tally) | Jump & Slash: 16 HP in 16 frames from ONE B press |
| 6-1 (35) | 0 | 0 | press cap only (30 one-frame A/B) |
| 6-2b-e (37-40) | 26 / 14 / 28 / 33 | 16 / 0 / 0 / 22 | |
| 6-3b-d (42-44) | 7 / 1 / 330 | 22 / 21 / 1 | 6-3d: 288 frames of L+R 36829-37116 |
| 6-4a Masked Devil | 0 | 0 in the fight | sword Down+B every 2 frames (12 hits), Fire Wheel 2 hits |
| 6-4b Jaquio | 0 | 33 in the fight (U+D+L between slashes) | 16 sword hits, Down+B every 2 frames |
| 6-5 Demon | 1 | 0 | 16 sword hits in 30 frames (39054-39084), Down+B every 2 frames |

## Boss facts (TAS trace)

* One sword swing = 1 HP of boss damage; the TAS re-swings (slash cancel, Down+B) every 2 frames and every swing
  hits. Our cap: one B press per 5 frames -> 16 hits need >= 75 frames of contact (TAS: 30). Expected loss vs
  the TAS: Masked Devil ~ +30-40 f, Jaquio ~ +40-60 f, demon ~ +45-80 f (the demon's heart is only reachable in
  the air: a jump gives ~35 frames of contact -> about 7 hits per jump).
* Items are CLEARED after every boss tally (item 0, ninpo 0 at 6-4b and 6-5 starts): Jaquio and the demon are
  always sword fights. 5-4 uses Jump & Slash (item $85 = 133; one B press, 1 HP per frame).
* HP carries within an act (5-3 starts with 3 HP in the TAS!); boss stages start at 16 (refill).
* TAS items: 5-2 start Windmill ($82) 40 ninpo; 5-3 start Jump&Slash ($85) 40; 5-4 start J&S 5; 6-2 start
  ninpo 5; 6-3 start Windmill 15; 6-4a start Fire Wheel ($80) 5.

## Mechanics found while legalizing (Acts 5-6)

* A 1-frame release cannot be copied (release >= 2): the TAS's very first 5-1 row pattern (Right at control,
  released 1 frame) has no exact legal equivalent; being 1 frame early/late changes the 5-1 bird boost.
* Legal single-wall climb (5-1 wall at abs x 1499 after the bird boost, measured from TAS frame 23094): the cycle
  [Left+A, Left+A, Right x 8] (wall jump away, drift back at 0.5 px/f, re-grab, jump again; A every 10 frames)
  rises ~1.4 px/f and clears the wall top ~18 frames later than the TAS's L+R climb (2 px/f).
  [Left+A x2, Right x3] (5-frame cycle) does NOT re-grab in time and falls. These cycles are beam macros
  ("^", d1, d2, k) in `a56_beam.py`.
* Time-shifted copies of the TAS rows can re-join the TAS path exactly (5-1 re-joined at lag +72); the beam's
  "lazy" mode then follows the reference at the cost of one emulation per chunk.

## LEGAL SLASH CANCEL (measured 2026-10-19 at Jaquio, `work/a56/jaq_probe5.py`, `jaq_probe6.py`)

* A sword swing ($80/$81/$82/$83 = 06 02 01 07 on its first frame) hits ONLY on its first frame here; if it is
  not cancelled it runs 04 xx 27 (3 frames) and 06 xx 08 with a 16-frame countdown, during which B is ignored:
  plain B presses every 5 frames give ONE hit per ~20 frames.
* The cancel: the swing must be started with **Down+B**, and on the next frame **Down must be released** (B still
  held, any of none/Left/Right/Up+Left...): the state returns to 05 02 03 10 (jump) at once and the next B press
  starts a new swing. Holding Down on that frame (or starting the swing with B alone) does NOT cancel. (A on the
  frame after the hold also cancels one frame later.)
* Legal 5-frame cycle (passes check_inputs): `Down | Down+B | B | - | -` (+ a held direction on every frame if
  wanted). Down is held 2 frames (the frame before and the swing frame), B 2 frames (swing frame and the cancel
  frame). Measured from the TAS's Jaquio position (frame 38132): hits on 38134, 38139, 38144 (one every 5 frames)
  until Ryu drops out of reach. The TAS (U+D+L between swings) hits every 2 frames.
* Boss HP at Jaquio / the demon: 16 hits -> at least 75 frames of reach at our cap (TAS 30-55).

## Boss targets (TAS replay, enemy slots: id $0400+s, x $0460+s, y $0480+s, HP $0490+s)

* Jaquio (6-4b): slot 7 (id 37), y 96, walks LEFT about 1.4 px/f (x 207 at 38098 -> 70 at 38188). The TAS's
  hits all came with Jaquio 45-60 px to the right of Ryu and Ryu 16-22 px lower (at a jump apex, y 112-118).
  Ryu cannot follow him legally (the TAS keeps facing right while moving left with U+D+L), so every hit window
  is one jump apex: about 3 hits per window at our cadence.
* The demon (6-5) has TWO targets: slot 6 (id 38, x 125, y 168, 16 HP) must be hit down first (the TAS does it
  during its first jump, 39011-39043, while the HP display $66 still shows 16), then slot 7 (id 40, the heart,
  x 168, y 120 -> 168, shown in $66) from 39054. 31-32 sword hits in total. A search that scores only $66 sees
  no progress for the whole first phase (my first 6-5 runs did exactly that).

## Method

`ng/stages/a56_common.py` (Enforcer: every emitted row legal by construction, carries the press history across
stages), `a56_beam.py` (beam: candidates = TAS rows at offsets -1..+2 of the node's TAS pointer, legalized, plus
9 macros (R, L, none, R+A, L+A, A, R+B, L+B, B) of `chunk` frames; score = TAS progress k - 2*dist(px) with
penalties for HP / ninpo below the TAS's and a different item; dedupe by RAM hash; drop deaths; boss stages:
boss macros + 8 frames per boss HP above the TAS's, and the kill is fast-forwarded through the tally to the next
load (6-5: to END seen)). `a56_solve.py` = driver + open-loop verify.

Additions (09:00): chunk 8 with 16 macros (incl. wall-jump cycles), lazy following of the reference while Ryu is
within 3 px of it (one candidate per chunk), backtracking when every child dies (10 generations kept, width x2),
and go-explore around an obstacle when the lag grows by more than half the elapsed time over 10 steps (archive
of (room, x/8, y/8) cells, random macros, until the score passes the stuck score + 24).
`a56_chain.py` chains stages (history carried, 150 blank load rows between stages, states saved per stage).

Further additions (12:00-12:40): boss chunk 5 with the legal slash-cancel cycles as macros; the demon scored on
slot 6 + slot 7 HP; Jaquio scored with a "hitting spot" term (Jaquio 45 px right, Ryu 18 px lower); after a boss
kill or a stage-end cinematic the beam plays on with nothing held and skips the cinematic with ONE Start (held 2
frames, retried every 5 frames until the script-end code runs), result cached per (kill frame, timer, sub-timer,
ninpo) WITH its rows (a first version cached only the frame count and lost the Start press: 5-4 b9 / 6-4b b9 did
not verify and were moved to states/tmp/a56_invalid/). No explore for bosses (the "stuck" test fires by design).

Segment convention: my input files start at the frame after the start state and end at the next stage's load
frame (the 151 load frames that follow need no input; the chain fills them with blank rows).


## Results (2026-10-19, end of the 10-hour time-box) - all from the TAS's own stage-start states

Every file below replays open-loop from its start state to the logged frame (`verified`), and passes
`python check_inputs.py <file>` (the file alone; the TAS history before a TAS start state is not legal anyway).
"vs TAS load" = our next-stage load frame minus the TAS's (same start state, same start frame).

| stage | file | start state | our load | TAS load | vs TAS | record (stage s -> f) | notes |
|---|---|---|---|---|---|---|---|
| 5-1 | logs/a56_5-1_c8.inputs.txt | ref4751/12_5-1_control | 24652 | 24276 | +376 | 2460 f = TAS +157 | first beam version; lost the 5-1 bird boost (1-frame release at control cannot be copied) and ~140 f at the wall climb (x 1499) |
| 5-2 | - | - | - | - | - | +277 | not solved (no compute left; wall stage) |
| 5-3 | - | - | - | - | - | +334 | not solved |
| 5-4 | logs/a56_5-4_b13.inputs.txt | ref4751/15_5-4_control | 29913 | 29911 | +2 | +2 | Jump&Slash kill, cutscene skipped by one 2-frame Start |
| 6-1 | logs/a56_6-1_c8.inputs.txt | ref4751/16_6-1_control | 31487 | 31487 | 0 | +9 | legalized TAS rows re-sync exactly (lazy follow) |
| 6-2 | - | tmp/a56_6-1_c8_next (chain B) | - | - | - | +230 | stuck: room 37, abs x 782, y 48 (TAS climbs inside a wall with U+D+L); explore failed 6+ times |
| 6-3 | - | - | - | - | - | +197 | not attempted |
| 6-4a | logs/a56_6-4a_b11.inputs.txt | ref4751/19_6-4a_control | 38099 | 37935 | +164 | +10 | Masked Devil: sword only at the 5-frame cancel cadence |
| 6-4b | logs/a56_6-4b_b15.inputs.txt | ref4751/room46_6-4b (+151 blank rows in the file) | 39321 | 38781 | +540 | +152 | Jaquio: sword at the cancel cadence, ~3 hits per jump apex; far behind the record |
| 6-5 | logs/a56_6-5_b16.inputs.txt | ref4751/room47_6-5 (+151 blank rows in the file) | END seen 40184 | END seen 39530 | +654 | +162 | END PROVEN: P = 40177 (first $63 == 0), TIMER-001 drawn on 40183, TIMER-000 first drawn on 40184 (`knowledge/a56_clock_end_b16.json`, `shots/clock/end_timer_4018*.png`); Ryu ended with 2 HP |

Totals: of the 10 stages, 6 are solved (5-1, 5-4, 6-1, 6-4a, 6-4b, 6-5); only 5-4 and 6-1 are at or under the
record's split. NO chained legal run exists yet: the Acts 3-4 agent never published an end state, and my own Act 6
chain stopped at 6-2.

## NEXT (coordinator direction received 12:55, not yet acted on - out of time)

Stop forcing the TAS line where it depends on banned tricks; use the record holder's route as the reference and
score each stage against min(legalized TAS, record route):
* 5-1: the bird boost on the pillar (TAS 22375) and the wall at abs x 1499 (TAS 23081-23126) -> copy the record's
  route there (record video `dl/record_video/`, room/stage times `knowledge/record_events.json`).
* 6-2 room 37 (abs x 782, y 48): the TAS's in-wall U+D+L climb; take the record's way up.
* Bosses: check the record's sub-weapons/ninpo for the Masked Devil, Jaquio ("plate kill") and the demon
  (record 6-4b = TAS +152, 6-5 = TAS +162) instead of sword cadence only. The demon needs ~32 hits (slot 6 then
  slot 7); the sword alone at 1 hit / 5 frames cannot match the record.
* Tools ready for that: `a56_solve.py --ref <our own legal solution json>` accepts any legal reference trace, so a
  record-route reference (hand-built rows) can drive the same beam; `--prefix` re-searches a window only.

## Round 2 (2026-10-19 afternoon; coordinator: use the record holder's route where the TAS line is banned)

### Record route extraction (done 13:00-13:40) -> `knowledge/record_route_a56.md`
* Video cut + tracked per image: room, background scroll, Ryu's screen x/y (`work/a56r2/record_trace.py`;
  calibration RAM x = video x - 2, y = video y + 9). Per-column TAS-vs-record-vs-ours tables `work/a56r2/rec/cmp_*.txt`.
* Record references for the beam: `logs/a56r2_rec5{1,2,3}.json`, `logs/a56r2_rec6{2,3}.json` (`mk_recref.py`).
* Found: 5-1 wall at x 1499 = two-wall chimney (blue pillar + wall); round-1 c8 loses to the record at x 1152-1216
  (-55 f) and x 2752-2816 (-98 f). 6-2 room 37 = single-wall climb of the tall pillar's right face. Masked Devil =
  Windmill thrown in the air at the orb (multi-hit, ~75 f fight). Jaquio = stand on the middle pedestal ("plate")
  and jump straight up repeatedly. Demon = jump straight up at x ~75-82 (pod) then at x ~113 (heart).

### Boss planner (new): `work/a56r2/jplan.py <demon|jaquio|mdevil>`
Beam over whole jumps: (walk w frames L/R/none) + jump (A 2 f) + air direction (R / none / R-except-on-B-frames / L)
+ legal slash cycle `Down|Down+B|B|-|-` from offset o (or Up+B throw); each step plays until Ryu lands/clings or the
target dies. Target = $66 (boss display, it reads 0 on the kill frame) + the demon's pod (slot 6 while id 38).
Score = frames + 6 x target HP + 0.7 x px outside the target's hitting zone (demon). Rows go through the Enforcer.
Round-1 lesson: a beam on 5-frame chunks with TAS-time position scoring wasted 366 f on the pod alone.

### Resources
Free RAM was 1.8-2.2 GB from 13:00 (other agents run 6 EmuHawks); my jobs wait in `work/a56r2/runq.py`
(starts a job only at >= 2.5 GB, 1 job if a HOLD_FARMS file exists); PIDs in `logs/a56r2_pids.txt`.
* 13:00-15:15 NO emulator could start: free RAM 0.2-2.2 GB the whole time (other agents' 6 EmuHawks + the owner).
  15:15-16:45 planner debugging (j1-j4, d1-d3, m1 discarded): (1) steps that never left the ground scored best
  (fixed: a step must jump), (2) 3-frame "hops" from ledges/clings (fixed: < 8 air frames and no damage = no step),
  (3) the global visited-cell pruning also counted nodes that were NOT kept in the beam, so later good children were
  pruned and the beam collapsed (j3 Jaquio reached 8 HP left at 263 f then died out; m1 collapsed after its kill).
  Fixed 16:45 (only beam nodes enter `visited`). Planner speed on the shared PC: 2-7 s per candidate jump.
* m1 (Masked Devil, TAS start state with the Fire Wheel, buggy pruning): kill at 37437 = TAS kill (37339) + 98
  (round 1 b11: about +164). Rows `states/tmp/a56r2_mdevil_m1.inputs.txt`, finish/verify queued.
* 17:30 **6-4a r2m1** (`logs/a56_6-4a_r2m1.inputs.txt`, from ref4751/19_6-4a_control, Fire Wheel like the TAS):
  next load 38029 = TAS +94 (round 1 +164; record +10). Verified open-loop, check_inputs PASS (windows 600:109,1800:246).
* 18:20 **6-5 r2d4** (`logs/a56_6-5_r2d4.inputs.txt`, from ref4751/room47_6-5 incl. 151 blank load rows, history
  6-4b b15): demon killed at 39321 (control 38933 + 388), END seen 39758 = TAS +228 (round 1 +654; record +162,
  i.e. 66 f behind the record). Verified, PASS. Pod and heart both by straight-up jump-slashes like the record.
* Selection fix 18:15: Pareto front (frame vs target HP) gets half the beam: plain score lost the nodes that had
  already hit Jaquio (they need ~40 f to the next hit window).
* 19:50 **6-5 r2d5** (`logs/a56_6-5_r2d5.inputs.txt`; width 6, hpw 9, Pareto selection): demon killed at 39249
  (control + 316), END seen **39686 = TAS +156** vs the record's TAS +162: about 6 f AHEAD of the record's 6-5 split
  (the record's split has +/-3 f of video uncertainty). Verified open-loop, check_inputs PASS. Ryu ends with 12 HP.
* 5-1 r2a (record reference, c8 prefix 760 rows): level with the record to x ~1560 (t 1160), then lost ~110 f at
  x 1850-1890 (y 58) and died at 24085 after spending HP (the record reference had no HP floor). Retry r2b queued:
  prefix to 23285 (`states/tmp/a56r2_51_prefix1160.inputs.txt`), reference with an HP floor of 6
  (`logs/a56r2_rec51h.json`).
* 20:45 Jaquio j7 (width 6, hpw 12, Pareto): no kill in 2.5 h; best lines 7 HP left at 383 f / 10 HP left at 366 f
  (the record kills at ~259 f after control, the TAS at 101). Continuation j8 queued from the j7 partial
  (`states/tmp/a56r2_j8_prefix.inputs.txt`). Jaquio in the TAS-start state walks left at y 96 (TAS line); the record's
  plate cycle (Jaquio swooping down onto/over the middle pedestal) did not appear in our searches: his pattern may
  depend on RNG / entry timing that the TAS state fixes.
* 5-1 r2b (HP floor) reproduced the r2a line to x 1891 (lag +111 vs the record) and fell further behind (+276 at
  x 2779): killed; round-1 c8 stays the best 5-1. The record passes x 1700-1930 HIGH (Ryu at the top of the screen,
  video 25696-25720, apparently a bird damage boost) and lands on the long upper platform; our beam climbs to y 58 and
  stalls there ~110 f. Next: copy that boost (bird timing = RNG/spawn manipulation) - not done.
* 6-2 r2a (record ref from the TAS control) was +313 behind the record still in room 36 (the record reference in a
  LEFTWARD first room is badly calibrated: killed). Hybrid r2b queued: round-1 rows to room 37 (990 rows from
  tmp/a56_6-1_c8_next) then the record reference (pillar climb).

### Round 2 results (end of the time-box, 2026-10-19 ~21:45) - all from the TAS's stage-start states

| stage | best file | vs TAS (next load / END seen) | record vs TAS | vs record | change vs round 1 |
|---|---|---|---|---|---|
| 5-1 | logs/a56_5-1_c8 (round 1) | +376 | +157 | -219 | none (r2a/r2b record-reference runs were worse) |
| 5-4 | logs/a56_5-4_b13 (round 1) | +2 | +2 | 0 (tie) | - |
| 6-1 | logs/a56_6-1_c8 (round 1) | 0 | +9 | +9 ahead | - |
| 6-4a | **logs/a56_6-4a_r2m1** | +94 | +10 | -84 | 70 f better (round 1 +164) |
| 6-4b | logs/a56_6-4b_b15 (round 1) | +540 | +152 | -388 | none finished (round-2 partial: 7 HP left at control+383 vs round-1 kill ~control+640) |
| 6-5 | **logs/a56_6-5_r2d5** | +156 (END seen 39686) | +162 | **+6 ahead** | 498 f better (round 1 +654) |
| 5-2, 5-3, 6-2, 6-3 | - | - | - | - | unsolved (record references built; no compute) |

Both new files: open-loop verified from their start states, `check_inputs.py --period 5 --hold 2 --release 2
--windows 600:109,1800:246` PASS. The "vs record" column uses the record's stage splits from `record_notes.md`
(+/-3 f each) - not a record claim.

NO chained Act 5-6 run: 5-2, 5-3, 6-3 have no solution and 6-2 stops at room 37 (the Acts 3-4 agent has no 5-1 end
state either). Compute: from 13:00 to 21:45 free RAM was below 2.5 GB except ~3 h; at most 3 of my searches ran at
once and the shared PC gave 2-7 s per planner candidate.

### NEXT (round 3)
1. Jaquio: the record's plate kill did not appear from the TAS state; check whether Jaquio's swoop pattern depends on
   `$BF` / the 6-4b entry frame (if so, the 6-4a kill/tally timing chooses it). Continue from
   `states/tmp/a56r2_jaquio_j7_partial.inputs.txt` with `jplan.py jaquio --prefix ... --hpw 12 --width 6`.
2. Masked Devil: the record uses the Windmill (multi-hit); route 6-3 so Ryu keeps the Windmill (the TAS enters 6-3
   with Windmill/15 and picks up the Fire Wheel), then `jplan.py mdevil --modes slash,throwslash`
   (`mdevil_wm` = the same with a DEBUG RAM poke, research only, never a deliverable).
3. 5-1: copy the record's high route at x 1700-1930 (bird damage boost to the top of the screen); our beam climbs to
   y 58 and stalls ~110 f there.
4. 6-2 room 37: run the hybrid (round-1 rows to room 37, then `logs/a56r2_rec62.json`) - queued but never started.
5. Record references for leftward first rooms (5-2 room 23, 6-2 room 36) need a better calibration than "TAS position
   at entry+40 = record position at first picture+17".
6. Demon: r2d5 is ~6 f ahead of the record split; more width/hpw variants could gain more (the TAS kills at +151).
* 21:50 queue stopped (j8 Jaquio continuation never got RAM >= 2.5 GB); no a56r2 process left running.

## Round 3 (2026-10-19 evening/night; agent a56 round 3)

### Jaquio answer (disassembly, `dl/NinjaGaidenNES/prg/bank07.asm` $D357-$D43C) - NO RNG, NO swoop
* Jaquio's AI is fully deterministic and never uses `$BF`: `jaquio_enter` puts him at x $C0 (192), y $60 (96), speed
  1.5 px/f; `jaquio_pace` turns him at x >= $D0 (208) or x < $30 (48), faces Ryu, and every $78 (120) frames (first
  after $80) spawns two homing fireballs (id $27) 32 px left/right of him. His y NEVER changes (96). Entry frame /
  `$BF` cannot change his pattern; the round-2 "swoop" idea was wrong. Model: x(t) = 192 + 1.5 t up to 208 (t ~ 11),
  then left to 48 (t ~ 117), right to 208 (t ~ 224), ... (t = frames after control; TAS: x 207 at 38098, 70 at 38188).
* The record's "plate" strat is just geometry: Ryu's straight-up jump from a pedestal top (y ~160) reaches y ~104-120
  (the floor y ~208 is too low to reach y 96). Record Ryu track (`states/tmp/a56r2_vid/jaq_track.txt`, RAM = video
  x - 2, y + 9) against the model x(t): the record's ENEMY-bar drops come with |Jaquio x - Ryu x| ~ 20-52 px and Ryu
  y <= ~122, facing Jaquio. His hit windows (t): 54-60 (from the left-pedestal jump, Ryu x ~98), 96-102, 122,
  144-156 (plate, Jaquio left), 210-228, 252-270 (plate, Jaquio right). Plate jump: ~46 f airtime, ~25 f near apex.
* Implication: with the plate at x ~123, Jaquio is in the band at t ~33-55 (right side, moving left), ~81-102 and
  ~132-153 (left side), ~180-201 and ~233-254 (right side). At our cap (1 hit / 5 f) a fully used window gives ~4
  hits, so a kill near t ~200 (record ~265-270) is the target if Ryu gets onto the plate by t ~30.

### Round 3 tools / compute log
* New planner `work/a56r3/jq3.py` (Jaquio): beam over pedestal jumps; candidates ranked by the deterministic model
  above (Jaquio x extrapolated from RAM with the pacing rule, Ryu's measured straight-jump y profile, band
  |dx| in [b0,b1], Ryu y <= ymax, facing toward him) and only the best `--verify` per node emulated. Fixes round 2's
  missing option: a 2-frame direction tap at the jump to FACE Jaquio without leaving the pedestal (jplan.py's only
  air options were hold R / hold L / none, so from the plate Ryu could not turn without drifting off).
* `work/a56r3/jq_geom.py` (hit-band calibration data), `work/a56r3/runq.py` (copy of the round-2 queue, PIDs in
  `logs/a56r3_pids.txt`), jobs in `work/a56r3/jobs.txt` (jq3 q1, geom, 6-2 hybrid r3h).
* 22:10 -> 02:30: NO job could start: free RAM 0.2-2.3 GB the whole time (owner's/other agents' processes; one
  process alone held ~3.1 GB), never >= 2.5 GB.
* 05:05 RAM came back (4.6 GB free); jobs ran 05:11-08:00.

### 6-2 room 37: the round-1 "wall" at abs x 782 is the SCREEN EDGE (camera never engaged) - found 06:05
* Replay of round 1's rows (`states/tmp/a56_best_6-2_snap.inputs.txt` from tmp/a56_6-1_c8_next,
  `work/a56r3/replay_rooms.py`): room 37 entered at row 1061 (frame 32698 = control + 1059; TAS + 125, record ~+66
  ahead of us), Ryu clings at the entry (abs 859, screen x 91, y 231, wall on his RIGHT), climbs the pillar at abs
  842 to y 82 (round 1 did that fine) and walks LEFT on its top (y 96) to abs 783 = screen x 15 and stops: the scroll
  stayed at 768 (`$51` 0, `$52` 3) and `$4C` (scroll_flags) stayed 128.
* TAS trace: the leftward camera of room 37 only starts once Ryu has reached screen x 127 ($4C 128 -> 129 at 32640);
  the TAS walks RIGHT from screen x 91 to 127 first (with L+R), the record too (record track `r62.json`: screen x
  93 -> 131 at scroll 0, t 1062-1084, THEN the scroll runs). Round 1 went left at once, so the camera never moved and
  the screen's left edge blocked Ryu at abs 783. Every "climb/explore" attempt there (rounds 1-3, `pillar62.py`,
  504 cycle variants: min y 48, min abs x 782) was doomed.
* To do: from the entry cling (row 1085), get on top of the entry wall on the RIGHT and walk to screen x >= 127
  (record: jumps off left to screen x ~74, comes back right over the wall top at RAM y ~192, t 1017-1084), then go
  left (pillar climb at abs ~842 = record scroll -56). Plain Left+A from the cling only rises ~15 px (y 231 -> 216);
  [Left+A x2, Right x6/7] cycles rise to y ~199 then stall at y 210 (`work/a56r3/try62.py`); cycle sweep
  `work/a56r3/sweep62.py` (see below).
* 6-2 FIX VERIFIED (06:20, `work/a56r3/try62.py`): from round 1's row 1125 (Ryu clinging to the pillar face in the
  entry chimney, abs 842, y 186): Right+A x2, Right x38 lands on the entry wall top (y 192) and reaches screen x 131;
  then Left: `$4C` = 129, Ryu stays at screen x 129 and the camera scrolls left. Prefix
  `states/tmp/a56r3_62_pre1125.inputs.txt` (1167 rows). Beam `a56_solve.py ... --ref logs/a56r2_rec62.json --prefix
  that --prefix-frames 1167 --tag r3c`: PAST the old blocker (abs 740 at f 32964, 646 at 33044, 431 at 33204, lag vs
  the record reference +35..+66), then stuck at abs 391 y 176 (f 33284+, exploring; TAS passes 395 at y 208).

### Jaquio calibration (06:20-06:45, `work/a56r3/jq_cal.py`, `jq_cal2.py`, data `logs/a56r3_jq_cal*.jsonl`)
* Ryu's jump from a pedestal top (A 2 f): y 160 -> 112 (apex 48 px up), 44 frames in the air; a jump from a wall
  cling is only ~15 px.
* Sword hits (legal cancel cycle, one swing per 5 f): EVERY swing hit when Ryu faced RIGHT (`$84` = 4 or 22),
  Jaquio x - Ryu x in [24, 58] and Ryu y in [78, 119]; none outside that band. Facing left (`$84` bit 3, e.g. 12/15)
  with Jaquio on the right: never.
* Jaquio on Ryu's LEFT: no hit measured at all (52 runs from the middle pedestal): Jaquio passes over the pedestal
  first and his body knocks Ryu back (`$84` bit 6 set = knockback: 71/79/72/76; HP 16 -> 13). The planner's
  left-facing predictions all got 0 (39 of 39). Next round: time the plate jumps so that Jaquio is already left of
  Ryu by > ~20 px before Ryu rises (the record's t 96-102 / 144-156 windows), and measure the left band.
* The first planner runs (q1-q4) used a symmetric band and wasted most verifications on left-facing jumps; q5-q7 use
  the right-only band (`--b0 24 --b1 58 --ymax 119`, right-only prediction).

### Jaquio result (06:55)
* q3 (`jq3.py --width 6 --verify 8 --b0 12 --b1 58 --ymax 128`, left pedestal mostly) reached 3 HP left at t 461 and
  stopped (depth limit 14, raised to 40 afterwards); continued with `work/a56r2/jplan.py jaquio --prefix
  states/tmp/a56r3_j9_prefix.inputs.txt` (= the q3 partial) -> kill at 38608 (t 522).
* **logs/a56_6-4b_r3k1.inputs.txt** (from ref4751/room46_6-4b, 151 blank lead rows, history 6-4a b11): next load
  39182 = TAS +401 (round 1 b15 +540; record +152 -> still 249 f behind the record). Open-loop verified, check_inputs
  PASS (600:109, 1800:246). Ryu ends 6-4b with 8 HP before the refill.
* 6-2 r3c next blocker (07:00): best rows `states/tmp/a56r3_62_r3c_best.inputs.txt` (prefix + beam, from
  tmp/a56_6-1_c8_next, 2127 rows; NOT legal-checked/verified as a deliverable). Ryu reaches abs 404 on the floor at
  f 33222 (record reference lag ~+60) and then clings to a wall face at abs 392, y 160-196 (its right side). Walking
  left along the floor (y 208) under it is open (the TAS walks 395 -> 373 at y 208), but at abs ~388 something
  knocks Ryu back to the right (anim 11; `work/a56r3/try62c.py 1590 "Right+A*2,Right*20,-*14,Left*60"`): probably an
  enemy the TAS kills first. Next: kill/avoid it (sword or the Windmill: item 130 is held, ninpo 0) or pass over the
  wall top.
* 07:16-08:00 6-2 r3d (`a56_solve.py ... --prefix states/tmp/a56r3_62_pre_r3d.inputs.txt`: r3c rows to 1590 + the
  floor pass with one knockback): abs 339-344 at f 33415-33631, lag vs the record reference +230..+311, HP 7, then
  stuck/exploring (abs 344, y 83). Research only; 6-2 is still unsolved and this line is far behind the record split.

### Round 3 results (2026-10-20 ~08:00, end of the time-box) - TAS stage-start states

| stage | best file | vs TAS | record vs TAS | vs record | change |
|---|---|---|---|---|---|
| 5-1 | logs/a56_5-1_c8 (round 1) | +376 | +157 | -219 | none (not worked on: no compute) |
| 5-4 | logs/a56_5-4_b13 | +2 | +2 | tie | - |
| 6-1 | logs/a56_6-1_c8 | 0 | +9 | +9 ahead | - |
| 6-4a | logs/a56_6-4a_r2m1 | +94 | +10 | -84 | none (Windmill strat needs a solved 6-3) |
| 6-4b | **logs/a56_6-4b_r3k1** | +401 | +152 | -249 | 139 f better (round 1 b15 +540) |
| 6-5 | logs/a56_6-5_r2d5 | +156 (END seen 39686) | +162 | ~+6 ahead | - |
| 5-2, 5-3, 6-3 | - | - | - | - | unsolved, not started (no compute) |
| 6-2 | - | - | - | - | unsolved; room-37 "wall" explained (camera) and passed; next blocker abs 392 / 344 |

r3k1: open-loop verified (next load 39182), `check_inputs.py --period 5 --hold 2 --release 2 --windows
600:109,1800:246` PASS. Compute: no emulator could start from 22:10 to 05:10 (free RAM 0.2-2.3 GB); about 3 h of
search in total.

### NEXT (round 4)
1. Jaquio: plan with the measured band (face right, Jaquio 24-58 px to the right, Ryu y 78-119) and AVOID body
   contact (Jaquio passing over the pedestal Ryu stands on knocks him back). The record's line (left pedestal -> jump
   up-right with hits at t ~54-60 -> middle pedestal -> straight jumps) still has its left-side hits unexplained:
   measure a left-facing swing with Jaquio 20-50 px to the LEFT (Ryu must be on the middle/right pedestal and rise
   after Jaquio has passed). `jq3.py` (right-only model, depth 40) + `jplan.py --prefix` for the end game; q7's
   partial (`states/tmp/a56r3_jaq_q7_partial.inputs.txt`) had 4 hits at t 113-119.
2. 6-2: start from `states/tmp/a56r3_62_pre1125.inputs.txt` (camera engaged). Re-search room 37 from there with HP
   kept high (the r3c line lost 4 HP), handle the enemy at abs ~388 (the TAS passes 395 -> 373 at y 208), then rooms
   38-40 with the record reference. The record's room-37 time is ~700 f; our entry is ~66 f behind it already
   (round-1 room 36): room 36 needs a re-search too to beat the record's split.
3. 5-2 / 5-3 / 6-3 / 5-1 high route: untouched in round 3 (see round 2 NEXT). Leftward first rooms (5-2 room 23,
   6-2 room 36): remember the camera rule found here - a leftward room's camera may need Ryu at screen x 127 first.
4. Masked Devil Windmill: still needs a 6-3 solution that keeps the Windmill.
* Last runs (07:35-08:01): q7 (`jq3.py` right-only model, width 5) reached 9 HP left at t 163 (7 hits, about the
  record's pace: the record had ~8-9 hits by t 156), then no hit until its deadline (from the left pedestal the next
  right-side window is t ~297-320). Continuation `jplan.py jaquio --prefix states/tmp/a56r3_j10_prefix.inputs.txt`
  (= q7 partial, t 163) found 5 HP left at t 279 on the middle pedestal (x 116, y 160) at depth 1 but lost that
  line at depth 2-3 (children died / knocked back); no kill before the time-box. Partial:
  `states/tmp/a56r2_jaquio_r3j10_partial.inputs.txt`. This is the most promising line for round 4: a kill from it
  around t 330-380 would be ~140-190 f better than r3k1 (t 522), still behind the record (~t 265).
* 08:01 queue stopped (`# STOP` in work/a56r3/jobs.txt); no a56r3 process left running.

## Round 4 (2026-10-22 evening; agent a56 round 4, also owns the 4-x parts of legal_a34_notes.md)

### Jaquio hit rules from the ROM (community hitbox Lua + bank07 `sword_hit` $DEC8, `hurt_ryu` $E144)
* The round-3 "facing" reading was wrong: `$84` bit 6 ($40) = facing LEFT, bit 3 = attacking, bit 2 = in the air
  (the values 12/15 called "facing left" in round 3 were air+attack). Left-facing hits work exactly like right ones.
* Sword (row of the Down+B press, `$83` == 7): hit iff Ryu y <= 119 (Jaquio y 96 is above Ryu's feet by < `$91` = 24)
  and (J.x - 28 - R.x) in [0, 31] facing right / (R.x - 28 - J.x) in [0, 31] facing left, i.e. F*dx in [28, 59]
  (Jaquio's x radius 28 from table $B300 at pose $43F = 112). The Lua box [-28, 60] is wider than the ROM's unsigned
  compare. Every hit/miss in the round-3/4 traces fits (58 used as the safe upper bound).
* Body contact (hurt_ryu): |dx| < 28 and Ryu y in (24, 121). So hits never need contact.
* **Slash cancel needs NO direction on the Down rows**: `Down | Down+B | B(+dir) | dir | dir` cancels; any Left/Right
  held on the Down or Down+B row (e.g. `Down+Right, Down+B+Right, B+Right`) does NOT cancel (pose $27, B ignored for
  16 rows). Round 3's planners held directions there, which is why many planned swings never happened.
* In the air the facing is fixed at takeoff; holding the facing direction moves 1.5 px/f, the other 0.5 px/f; no
  momentum (release = stop). Pedestal tops (Ryu x, y 160): L 27..71, M 92..136, R 189..232; walls x 24 / 236; a
  pedestal jump: y 160 -> 112 (rows 19-25), lands at row +43; y <= 119 on rows +13..+30 (18 rows, <= 4 hits/jump).
* Fireballs: every 120 rows from row 129 (rows after the 6-4b control state), two at J.x(prev row) +-32, y 64, homing
  by +-1/16 px/f^2 on x and y toward (Ryu x, Ryu y - 8), no speed cap, removed outside x 8..247 / y 48..247; one
  sword hit kills (box x radius 16, y radius 8). `work/r4/fbsim.py` reproduces the emulator exactly on the
  calibration traces (logs/r4/fb_idle.jsonl, fb_p5.jsonl) incl. the stale sub-pixel bytes of the reused slots.
* Planner `work/r4/jqplan.py` / `jqplan2.py` (pure model, numpy; v2 adds fireballs + defensive swings) and
  `work/r4/jqrows.py` (plan -> rows -> emulator check).
* More measured rules (round 4): a ground slash (B on a pedestal) has its blade on row r+6 and locks Ryu until r+16;
  a jump before r+16 cancels the slash but that jump CANNOT attack at all (pose stays non-7). After r+16 all normal.
  Walking into a jump with the same direction held: the takeoff row also moves 1.5 px. A 1-row release of a direction
  is illegal (release >= 2), so plans must not leave 1-row gaps (the planner tracks the last held direction row).
  Landing on the middle pedestal at x 135 fails (falls) although walking keeps him on it to x 136: planner pedestal
  ranges L 31..67, M 96..132, R 193..228.
* The kill is `$66` == 0 (slot 7's HP byte $497 stays 1 on the killing hit: enemy_dies does not decrement it).
* The boss tally after the kill takes longer when more timer is left: an earlier kill gains only part of the frames
  at the next load (6-4b: kill 263 rows earlier -> load 251 earlier; 6-4a: 35 earlier -> 17 earlier).

### Round 4 results
* **6-4b Jaquio: `logs/a56_6-4b_r4k2.inputs.txt`** (from ref4751/room46_6-4b, 151 blank lead rows, history 6-4a b11):
  kill on row 254 after tmp/a56r2_64b_control (r3k1: 522; the record ~265), next load **38926 = TAS +145; the record
  is TAS +152 -> about 7 f AHEAD of the record's 6-4b split** (record split +/-3 f). Open-loop verified (finish.py),
  `check_inputs.py --period 5 --hold 2 --release 2 --windows 600:109,1800:246` PASS. Ryu ends with 16 HP.
  Route (rows after the control state): floor jump with Right drift onto the left pedestal, jump right from its edge
  (1 hit at t ~51), land on the middle pedestal, two left-facing straight jumps (4 + 4 hits, t 88-103, 132-147),
  ground slash facing left at t 170 (kills the first fireball pair's threat), two right-facing jumps (3 + 3 hits,
  t 201-211, 244-254). Plan json logs/r4/jq_plan_q9.json + variant search work/r4/jqvar.py (first-jump timing).
  Earlier r4k1 (same plan, kill 259): load 38931 (TAS +150).
* **6-4a Masked Devil: `logs/a56_6-4a_r4m1.inputs.txt`** (from ref4751/19_6-4a_control, Fire Wheel state like
  the TAS): same planner with the orb model (`BOSS=mdevil NEED=14 python work/r4/jqplan2.py md1 40 60`: orb x 135
  y 120, x radius 16 -> facing right Ryu x in [88, 119], Ryu y in (104, 144)): floor jump onto the left pedestal,
  jump right toward the middle pedestal (4 hits), two straight jumps from the middle pedestal at x 96 (7 + 5 hits);
  kill row 124 (r2m1: 159), next load 38012 = TAS +77 (r2m1 +94; the record +10 -> still 67 behind; the record's
  Windmill strat needs the Windmill kept through 6-3). Verified, PASS.
* **6-2 room 36 = TAS pace, legally**: the TAS's room-36 rows break no rule except 1-frame A/B presses; legalized
  (A/B held 2 frames, Enforcer) from our 6-1 end state tmp/a56_6-1_c8_next they reach room 37 on **32573 = the TAS's
  frame** (`work/r4/tasleg.py tmp/a56_6-1_c8_next 31637 1100 logs/a56_6-1_c8.inputs.txt`; also from
  ref4751/17_6-2_control). Round 1 entered room 37 on 32698 (+125) and the record on ~32632, so we are now ~60 f
  AHEAD of the record at room 37's entry. First divergence 32601 (the TAS's L+R climb out of the entry chimney).
* Room 37 from there: grafting round 3's rows (pre1125 / r3c, found 125 f later) at the room entry works (room entries
  are fixed points): `work/r4/graft62.py 32573 states/tmp/a56r3_62_r3c_best.inputs.txt 1060 1600 r4_62_g2`: chimney
  -> entry wall top (y 192) at 32667, camera engaged (screen x 129) ~32685, pillar top (y 96) ~32787, hp 15 until
  ~32880 (abs 684); later r3c rows run into enemies (hp 15 -> 9). Prefix kept to 32880: `logs/r4/r4_62_g3`
  (1243 rows from tmp/a56_6-1_c8_next); A* `r4_62_g4` from there to room 38 (exit wpos 120, y 80).
* Legalized TAS rows from the TAS stage starts (`work/r4/tasprefix.py <state> - <k0> <k1> <out>`): 6-3 stays on the
  TAS line to 34972 (room 41 nearly to its exit, TAS 34990; hp 11 like the TAS) -> prefix `logs/r4/r4_63_t1`;
  5-3 to 26728 (t 119; hp 3 like the TAS) -> `r4_53_t1`; 5-2 to 24628 (t 200) -> `r4_52_t1`. Each is continued with
  the A* to the next room (r4_63_a1, r4_52_a1, r4_53_a1). Pure A* from the stage start (round 4 r4_52a_x1, 1500
  expansions, no goal; r4_63c/r4_53c chains) was far worse and was stopped.
* 6-2 room 37 continued (hand rows after A* `r4_62_g5` = floor at abs 346 on 33118): ground slash (kills the id-5
  walker coming from the left), walk left, jump at abs ~298, second jump the moment he touches the small platform
  (y 160, abs ~268), air slash (B) before landing on the y-128 ledge (kills what sits there), walk left, jump at abs
  ~155 to the exit: **room 38 on 33287** (TAS 33170 = +117; the record's room 38 is ~33331 -> ~44 f AHEAD of the
  record). Rows `logs/r4/r4_62_h2` (1650 rows from tmp/a56_6-1_c8_next). Rooms 38-40: `tasrepair.py` (r4_62r).
* `work/r4/tasrepair.py`: follow legalized TAS rows (tasprefix), and at each divergence run the A* to the TAS's
  position ~25 frames later (a standing point, or the room change), re-align to that TAS frame and follow again.
  Jobs for 6-3 (from r4_63_a1), 5-2, 5-3, 4-2, 5-1, 4-3 in work/r4/jobs.txt.
* 6-2 rooms 38-39 (tasrepair r4_62r / r4_62s from r4_62_h2): room 38 (vertical shaft) by A* C8 x11 -> room 39 on
  33407 (TAS 33268 +139; the record ~+192 here); room 39 then lost ~110 more in two A* repairs (lag 249 at abs 551
  on 33870, the record is about +192..+210 in room 39/40) -> stopped: 6-2 cannot beat the record's split on this
  line without a better room-39 run. Best 6-2 rows: `logs/r4/r4_62s_p1` (2248 rows from tmp/a56_6-1_c8_next, room 39
  abs ~560 on 33885; NOT a finished stage).
* 6-3: legal TAS rows (room 41) + A* JORA28 -> **room 42 on 34992 (TAS 34990, +2)**: `logs/r4/r4_63_a1` (from
  ref4751/18_6-3_control). Room 42 (TAS 155 f with an in-wall chimney climb at x 215-235 and U+D+L; the record 216 f
  going LEFT along the y-208 ledge to x ~64, climbing to y ~91 at x ~79, then right along the top to the exit at
  x 184, y 75): note our entry is 2 frames later, so TAS-relative timings shift +2. Hand rows (wait, Right 2 to touch
  the entry wall, Left+A wall jump, C8 re-grab, Left+A, drift left onto the y-208 ledge at x 149, jump, Right ->
  the y-160 platform at x 158 on 35065 (TAS 35046, +19)): `r4_63_k1` (platform) / `r4_63_k2` (ledge, 35041).
  A* from both (k1a: TAS-side exit; k2a: the record's left climb). Earlier A* runs from the TAS-side positions
  (r4_63_b1 2000 exp, r4_63_c1) never climbed above y ~116.
* **6-3 room 42 on the record's line (by hand): room 43 on 35212** (TAS 35145 +67; the record's room 43 is ~35228,
  so ~16 f AHEAD of the record there): from the y-208 ledge walk left to x ~99, jump left to the column's right face
  at x ~73 (cling), 4 C8 cycles (Right+A x2, Left x6), Left onto its top (y 128), jump right onto the y-96 platform,
  jump right into the exit (x ~179, y 74). Rows `logs/r4/r4_63_h4` (650 rows from ref4751/18_6-3_control).
  A first hand line (left to the outer wall at x 24, 9 C8 cycles) reached room 43 only on 35297 (r4_63_h1).
  Rooms 43-44 with tasrepair (r4_63t).
* 5-2 (tasrepair r4_52r -> hand rows -> r4_52s): room 23 on the TAS line to 24628, A* repairs (lag 25 at 24750), the
  exit by the record's line (slash the walker on the y-192 floor, walk left to the wall at x ~24, 7 C8 cycles, jump
  right into the exit): **room 24 on 24982** (TAS 24874 +108; the record ~24948, i.e. ~34 f behind the record):
  `logs/r4/r4_52_h2` (554 rows from ref4751/13_5-2_control). Room 24's entry chimney (Ryu appears at x 43, y 232
  between walls at x ~24 and ~44; the TAS climbs it with L+R to the y-160 platform at x 73): C8 on the right wall
  stalls at y ~167 (its top corner); A* r4_52s_a0 / r4_52_e1 had not solved it at the end.
* 6-3 room 43 (tasrepair r4_63t from r4_63_h4): TAS line followed 35231-35829 at lag 85 (600 rows in sync), repairs
  at 35883 (lag 88) and 36007 (lag 136, hp 5); the record is ~+83 at room 43's entry and ~+155 at room 44's.
  Later repair 36050 -> lag 207 (hp 5): now behind the record's ~+155 at room 44 -> 6-3 on this line is not a record
  split; continuing to room 44 only for a complete legal 6-3.

### Round 4 results (2026-10-23 ~03:45) - from the TAS stage-start states

| stage | best file | vs TAS | record vs TAS | vs record | change |
|---|---|---|---|---|---|
| 6-4b Jaquio | **logs/a56_6-4b_r4k2** | +145 (load 38926) | +152 | **~7 f ahead** | was +401 (r3k1): 256 f better; verified, PASS |
| 6-4a Masked Devil | **logs/a56_6-4a_r4m1** | +77 (load 38012) | +10 | -67 | was +94 (r2m1); verified, PASS |
| 6-5 | logs/a56_6-5_r2d5 | +156 | +162 | ~+6 ahead | - |
| 6-1 | logs/a56_6-1_c8 | 0 | +9 | +9 ahead | - |
| 5-4 | logs/a56_5-4_b13 | +2 | +2 | tie | - |
| 5-1 | logs/a56_5-1_c8 | +376 | +157 | -219 | none (tasrepair: TAS line to 22362, the bird-boost target unreachable) |
| 6-2 | (prefix) logs/r4/r4_62s_p1 | - | +230 | - | room 37 at TAS pace (32573), room 38 33287 (record ~33331), room 39 33407; lag 249 by abs 551 in room 39 -> behind the record |
| 6-3 | (prefix) logs/r4/r4_63t_* | - | +197 | - | room 42 +2, room 43 35212 (record ~35228), lag 207 mid room 43 |
| 5-2 | (prefix) logs/r4/r4_52_h2 | - | +277 | - | room 24 on 24982 (record ~24948); room 24's entry chimney unsolved |
| 5-3 | - | - | +334 | - | TAS line legal only to 26728 (hp 3 there); not continued |

All prefixes are legal by construction (Enforcer / A* greedy_legal) but are NOT finished stages; finish them with
`work/r4/finstage.py <stage idx> <start state> <rows> <tag>` (cuts at / plays to the next load, Start-skips the
cinematic, a56_solve.finalize) and judge with check_inputs.py.

### NEXT (round 5)
1. 6-3: room 43's repairs lose ~120 f (36007-36257: A* with hp 5); hand-solve that spot (the TAS walks left along
   y 128 from abs 739 to 674 in 43 f) and room 44 (TAS 288 L+R frames) -> a complete 6-3; the record's split needs
   room 43+44 at <= TAS +195 in total.
2. 5-2: room 24's entry chimney (x 24/44 walls, platform y 160 at x 73), then tasrepair rooms 24-26.
3. 6-2 room 39: the A* repairs lost ~110 f; a hand line through room 39 at the record's pace (+20 over the TAS)
   would make 6-2 a record split (we are ~44 ahead of the record at room 38's entry).
4. Jaquio margin: the planner optimum for this plan family is kill row 254 (q9/q10). A better first jump (2 hits
   instead of 1, model-predicted kill 249) needs the floor-jump/walk rows tuned on the emulator (work/r4/jqvar.py).
5. Mesen fastcore (`ng/fastcore.py`, 2x NesHawk) is not used yet by these tools; the A* (a34r2_astar via
   work/r4/astar.py) is the slow part (5-20 s per expansion with 3 emulators running).
* (04:05) 5-2 room 24's entry chimney SOLVED by hand: 5 C8 cycles on the right wall (x ~44, to y ~183), Left+A to the
  left wall (x 24, cling y ~169), one C8m cycle (Right+A x2, Left x6), then Right+A and Right: over the wall top onto
  the y-160 platform (x 75 on 25098; TAS 24941 -> lag 157; the record is ~+156 at room 25's entry). Rows
  `logs/r4/r4_52_h3` (from ref4751/13_5-2_control). The TAS line is legal from there for ~190 frames (tasrepair
  r4_52t: 24941 -> 25134 in sync).
* 6-3 after r4_63u (hand jump over the knock-back spot at abs ~700 -> lag 138, then tasrepair: lag 175 at abs ~480,
  hp 3, repair to abs 358 failed): stopped; best prefix `logs/r4/r4_63u_a0` (from ref4751/18_6-3_control).
* 5-2 r4_52t: after the chimney the TAS line held to 25134, then one A* repair (to abs 401, y 128) cost ~76 f: lag 233
  on 25392 (the record ~+156 at room 25) -> stopped. Prefix `logs/r4/r4_52t_p1` (from ref4751/13_5-2_control).
* 04:15 all round-4 jobs stopped (work/r4/jobs.txt `# STOP`); no r4 process left. Deliverables re-replayed in a fresh
  emulator: 6-4b r4k2 load 38926, 6-4a r4m1 load 38012 (both as in finish.py). logs/results.json did not exist.

## Round 5 (2026-10-23 from 04:10; agent a56 round 5)

### Tools (Mesen = ng/fastcore.py; every result is a candidate until replayed on NesHawk)
* `work/r5/mboot.py <out> tas:<F> rows:<file>[:n] blank:<n> ...` power-on replay -> `states/mesen/r5/<out>.mst` (+.frame);
  `tas:F` uses the TAS's NesHawk pad bytes (exact). `work/r5/mext.py <mst> <rows> <skip> <n> <out>` extends a state.
* `work/r5/runbeam.py <mst> <prefix> R|L <goal> <out>`: beam for run rooms (hold the direction, A / B / Up+B / stop
  variants per 8-frame chunk; score = progress - hp penalty - |y - TAS y at that x| (`--ref k0:k1 --refw`); deaths
  = pit (y >= 241), hp refill, room reset). Writes `logs/r5/<out>.inputs.txt`, `<out>_part` every 5 steps, end state.
* `work/r5/mastar.py` = the a34r2 A* unchanged on MesenEmu (start = .mst, prefix '-', `--hist` rows).
* `work/r5/mplay.py <mst> <hist rows> "<spec>" k [--save out]` (playspec on Mesen), `work/r5/nhcheck.py`
  (NesHawk or `--mesen` replay listing), `work/r5/tasview.py f0 f1 [step]` (TAS line + banned frames),
  `work/r5/md_search.py fw|wm` (6-4a), `work/r5/gate.py <log> <cmd>` (waits for < 3 emulators on the machine).
* Contention: the other agents ran 3-4 emulators most of the time; my jobs wait in gate.py.

### Round 5 results (2026-10-23 06:00, paused by the owner)
* **6-4a: `logs/a56_6-4a_r5f1.inputs.txt`** = r4m1 + one Fire Wheel throw (Up+B overlaid on a slash cycle; Mesen
  `md_search.py fw`: kill row 113 vs 123). NesHawk open loop (`work/r4/finstage.py 19 ref4751/19_6-4a_control
  logs/r5/r5_md_fw_best.inputs.txt r5f1`): load 37987 = **TAS +52** (record +10 -> -42; r4m1 was +77), check_inputs PASS.
* 6-2 (all Mesen, NOT NesHawk-verified; start = tmp/a56_6-1_c8_next = `mboot r5_62_a1 tas:30063 rows:a56_6-1_c8
  blank:150 rows:r4_62r_a1`): room 39 run `logs/r5/rb62_39d` (runbeam, TAS y-ref) to wpos 628 at 33868 (lag 196, a
  knock-back at ~500 cost ~40), exit A* `ma62_40` (R2 JRR0 C8 C7 C8) -> **room 40 on 33918** (TAS +206; record ~+210).
  Combined rows `logs/r5/r5_62_40in` (2281 rows after tmp/a56_6-1_c8_next). Room 40: entry by hand (3 C8 at the entry
  wall, Left+A, Left) -> y-192 ledge x 99 at 33994 (`logs/r5/r5_62_40g`, state states/mesen/r5/r5_62_40g.mst); then
  the TAS goes left to the wall at x ~72 (y 160 floor at x 69-104), climbs it (U+D+L in the TAS) to y ~112 and drifts
  right onto the y-96 platform at x 128 (TAS 33864), then runs right to x 747 (TAS 34285). Room 40 must cost <= TAS +24.
  A* from the entry (ma62_40w) climbed the wrong (right) wall; the ledge A* ma62_40x was stopped at the start.
* 6-3 (Mesen; start ref4751/18_6-3_control = `mboot r5_63_h4 tas:34562 rows:r4_63_h4`): room 43 entry chimney by hand
  = 3 C8 cycles (Left+A x2, Right x6) + Left+A x2 + Left -> y-192 ledge x 1909 at 35285 (`logs/r5/r5_63_e3`, only ~6 f
  lost vs the TAS's L+R/U+D climb). runbeam to 1127 at 35814 (`r5_63_m1`), wide beam through the knock-back spot
  (~950) to 844 at **36007 (`r5_63_m2`, hp 8, lag ~76; the record is ~+83 at room 43's entry and ~+155 at room 44's)**.
  Next obstacle: a wall face at x ~743 (top y ~128): the TAS clears it with a jump from x ~786 (apex 127); runbeam
  now has a "CL" wall-jump variant. Room 44 = run right (the TAS's 288 L+R frames are only backward-facing running at
  1.5 px/f; holding Right is as fast). Masked Devil Windmill idea: the TAS keeps the Windmill until the Fire Wheel
  lantern in room 44 (x ~956, TAS 37085) and gets +10 ninpo at 36767; skipping that lantern keeps the Windmill for
  6-4a (research mode `md_search.py wmi 10`, never run).
* 5-2: not started (boot `mboot r5_52_h3 tas:24428 rows:r4_52_h3` queued, not run).

### Resume (round 6), from the project root; one job at a time while others hold emulators (`work/r5/gate.py`)
1. 6-3: `python work/r5/runbeam.py states/mesen/r5/r5_63_m2.mst r5_63_m2 L room:44 rb63_43d --W 40 --C 8 --buck 2
   --ref 35231:36437 --refw 0.3 --hpw 6 --throw 1` (then room 44: runbeam R, `--ref 36437:37126`), finish on NesHawk with
   `work/r4/finstage.py 18 ref4751/18_6-3_control <rows> <tag>` + check_inputs.
2. 6-2: `python work/r5/mastar.py 6-2 states/mesen/r5/r5_62_40g.mst - pos:40:128:96:6 ma62_40x --hist r5_62_40g
   --w 1.3 --max-exp 600` (env A34_AIRRUN/HMAX/SWITCH/FINE=1), then runbeam R to x 747, then
   `work/r4/finstage.py 17 tmp/a56_6-1_c8_next <rows> <tag> --hist logs/a56_6-1_c8.inputs.txt`. Improving room 39
   (re-run runbeam rb62_39d with --vars wide / larger W around x 480-560) gives margin.
3. 5-2: the boot above, then runbeam R from the room-24 platform (`--ref 24941:25361`).
4. 6-4a: `python work/r5/md_search.py wmi 10` (Windmill research, DEBUG poke) if 6-3 can keep the Windmill.

## 5-1 lock round (first) (2026-10-26; agents l51a = control -> X-1,504 wall, l51b = wall -> stage end)

On the locked chain `logs/l44p_r1920_c2_poweron.inputs.txt` (5-1 control row 22,629 = blank, `$BF` 78 after it; our frame =
TAS + 504 at equal pace). Details, files and states: `knowledge/LOCKED_CHAIN.md` "Agent notes (5-1)" / "Candidates (5-1)".

### l51a: control -> the wall (tools `work/l51a/`)
* Prep's head start (`work/l51p/pre51_22490.txt`) grafts unchanged: X 601 on 22,994 (TAS +1.3), hp 15 (tosser-1 body boost), np 20.
  NesHawk takes the tosser-1 hit 1 frame earlier (22,878) and re-converges by 22,893.
* X 760 -> 1,104: legal TAS rows at lag 505 are hit at X 880 (the X-773 type-11 bird, from behind). Fix (greedy repair
  `fix.py`, then hill climb `hc.py`): the TAS jumps at 22,644 / 22,687 / 22,730 each 3 frames later + Left x2 in the air at
  22,697-98 (dodges the X-940 walker). Both +5 lanterns (X 864, 944) are free (slashes in the air cost nothing). The 22,755 slash
  must kill the X-773 bird and the t13 (TAS does the same). Cost: lag 505 -> ~508 by the wall. Hill climbs (single shifts,
  local adds) and a 3-jump x air-turn grid found nothing faster with the bird constraint.
* Legal TAS rows at lag 509 then pass tosser 2 with no hit (lag 511 is hit at X 1,221) and reach the TAS's exact X,y at the wall.
* **Wall bird = spawn-table re-use** (bank 7 `spawn_enemies` $E560): the scan compares `($96),y` with `$00` = screen column
  (scroll/16); while the camera moves LEFT it uses column - 13 and mirrors the x. The wall bird is the X-773 bird's entry
  (column 45) brought back by a 1-px camera move left at screen column 58 (scroll 928-943); the entry is free only if that
  bird died (the 22,755 slash). The TAS's air Left at 22,793 makes the move at scroll 929 -> 928. The same Left x2 3 frames
  later on our line (TAS-eq 22,796) spawns it at (1,136, 64) on 23,302 for free; a turn at scroll 922 instead re-spawns the
  X-940 walker (column 44). Any enemy killed or scrolled off can come back this way: check camera moves left near spawn columns.
* NesHawk pad-read conflicts exist on this line: a Left x2 at TAS-eq 22,801 (our 23,306) is read as Right on NesHawk.
  Check every candidate with `work/l51a/nhchk.py`.

## 5-1 lock round (second) (2026-10-26; agent l51b = X-1,504 wall -> X ~2,596; tools `work/l51b/`)

Axis: our frame = TAS frame + 504 + lag. Every search ran on Mesen (fastcore, ~250 f/s per core here) and every handed-over
line was replayed on NesHawk (`work/l51b/nhchk.py`, `nhcmp.py` per-frame incl. enemy slots, `ramdiff.py` full-RAM diff).

### What the second half of 5-1 depends on
* **Two type-11 birds do all of the TAS's boosts**: the wall bird (spawn-table entry #9, re-spawned by the TAS's air Left at
  22,793) gives the 23,081 wall hit, the 23,714 hit onto the y-96 platform AND the 23,905 hit onto pillar B; entry #19
  (spawns at X ~2,000 at scroll 1,824) trails. Birds are a bang-bang pendulum around Ryu (x accel 1/16 px/f^2, y 1 px/f),
  so their phase is set by everything Ryu did since they spawned; only waits and jump heights steer them.
* **Geometry (dmap):** y-96 platform X 2,336-2,431 is one-way from below; under it the y-160 step X 2,336-2,367; pit
  X 2,432-2,511 (no floor); a jump from the step peaks at y 112, so the platform needs a hit near the apex (+29 px), from either
  side. The y-128 platform X 2,208-2,303 is out of reach from the floor (apex 160). From the floor at X 2,512-2,783 the way up
  is pillar B (X 2,656-2,687, top y 128, floating) via a hit, or the wall at X 2,784 (single-wall climb, slow).
* **Mesen != NesHawk after the tosser-1 transient** (prep's head start: NesHawk hits 1 frame earlier): slot-5 x/y fractions
  ($47D, $485) differ, and every later slot-5 enemy inherits them. Visible effect: the tosser-3 type 15 (slot 5) bounces 1 px
  differently and hits Ryu at TAS-eq 23,578 on NesHawk only. Fixed by patching Mesen with NesHawk's RAM (first's
  `l51a_p23100N.mst`). Rule: before trusting a Mesen state, `ramdiff.py` it against the NesHawk state.
* NesHawk pad-read conflicts: an A press at 24,172 on one of my lines was read 1 frame late. Check every candidate.

### Pieces found (all NesHawk-checked unless marked)
| piece | result | cost vs TAS | file |
|---|---|---|---|
| wall climb after the bird hit (w2a, hit 23,589) | beam, chimney-ish A+L/A+R switches: X 1,530 on 23,663 | +21 (lag 509 -> 530) | `work/l51b/gb_w2a.inputs.txt` |
| wall climb macros [A+L, R x n], [A+L, A+R, R x n] (6,552 variants) | >= 23,677 | +35 or worse | `wc2.py` |
| no-bird climb (w1) | beam 23,673; macro 'R:10 [A+L:2 R:6]x8' 23,689 | +36 / +52 | `gb_w1b`, `cl0.txt` |
| TAS rows 23,134 -> 23,670 at lag 530 | exact TAS sync; the 23,355 slash kills the wall bird (it is AHEAD of Ryu on our line) | 0 | `fol.py` |
| tosser 3 (type 15, NesHawk) | TAS jump 23,544 moved to 23,546-47 (any 23,546-51) | 0 | `t15.py` |
| y-96 platform | wait 24 blank rows on the step, A+Right: #19 bird hits (hp 12 -> 9), lands 24,272 | +24 (lag 554) | `p96.py` (966 variants; no wait < 22 works) |
| Windmill / health | ONE Up+B on TAS-eq 23,738-39 + jump 23,739-40: health 9 -> 15, t8 dead, no hit | 0 | `thr4.py`, `thr5.py` |
| keep the #19 bird for the 23,905 boost | every throw that spares it lets it (or the t8) knock Ryu into the pit | - | `thr5.py` (405 variants) |
| end without a bird (TAS state, research) | X 2,760 y <= 100 at TAS-eq 24,014 | +51 | `gb_nh850` |

Handover v2 (to first's end beams): X 2,596 y 208 at 24,404 (= TAS 23,850 + 554), hp 15, np 35, Windmill
(`work/l51b/s_v2_24404.txt`, NesHawk `states/l51b_v2_24404`). With first's end (e4 + e5) = candidate c1, trigger 24,779,
5-2 control 25,059 = **record -29**.

### Dead ends (don't repeat)
* Faster climbs change the wall bird's phase: of 74 beam climbs (23,665-23,668) followed by TAS rows, all but gb_w2a get hit
  or killed (`evcl.py`); first's cla (23,658) gets hit at 23,695 and a no-hit repair costs 20+ f (`gb_clk`, `gb_cla1`).
* Keeping the wall bird alive (no 23,355 slash) + a TAS-path beam to the platform: lag > 560 (`gb_wb1`).
* Prep's `b_e23` end beam doesn't transfer to another `$BF` (it was built on c 86).
* Staying high (wall bird alive, geometric beam `gb_hi1` from TAS-eq 23,330, width 250, 440 f): no platform by 24,300.
* Killing the #19 bird (slash near TAS-eq 23,550) + a camera-left move at column 127 (`resp.py`, 696 variants): the bird
  re-spawns BEHIND Ryu at (2,117-2,126, 208), and the detour brings the tosser-3 type-15 hit back (hp -2). No gain found.

### Open
* The real prize is a bird near Ryu at TAS-eq ~23,690-23,714 (saves the 24-f wait) and again at ~23,880-23,905 (saves most of
  the end's +71). Ideas: re-spawn entry #19 by a 1-px camera move left at screen column 127 (scroll 2,032-2,047, TAS-eq
  ~23,555) after killing it; a climb variant whose wall bird stays BEHIND Ryu (then the TAS's own boosts apply).
* Wall climb: a beam from w2a 23,575 (`gbeam.py`, h = max((1530-X)/1.5, (y-96)/2)) gets on top at 23,658 (TAS + 525, 5 f
  better than l51b's 23,663). But the wall bird then catches Ryu from behind at 23,695. The bird is a bang-bang pendulum
  around Ryu (bank 7 $C735: y +-1/f toward Ryu, x accel 1/16 px/f^2, no cap); TAS amplitude ~70 px, period ~210 f. Killing
  it after the climb costs ~14 f. Waits on the wall top don't re-phase it cheaply. Second's line (top 23,663) is the one where
  the TAS's 23,355 slash kills it.
* Mesen vs NesHawk: the tosser-1 transient leaves $47D/$485 (slot-5 fractions) different, and that later changes a slot-5
  enemy (tosser 3's type 15). Use the RAM-patched base `states/mesen/l51a_p23100N.mst` (zero game-RAM diff to 23,588) and
  compare the full RAM on every handover (`nhchk.py` prints it).

### End piece (l51a) and candidates
* Without a bird at 23,905, Ryu must get onto the y-96 block (X 2,784-2,911, pit below) from the floor. Beams cling-loop at
  the X-2,784 wall face. **Single-wall climb of the X-2,656 pillar** (left face, top y 128) from the floor state X 2,596
  (24,404): Right x17, A+Right x2, Right x18, [A+Left x2, Right x6] x3, A+Right x2 -> on top 24,502 (TAS 23,919 + 583), no hit.
  Then beam e8: X 2,801 y 52 on 24,573. Beam e9 to the trigger 24,738: the X-3,008 type-14 hits once (15 -> 12).
* **c4 (best)** `logs/l51_a_c4_poweron.inputs.txt`: c3 with a 2-f faster pillar climb (top 24,500): 5-2 control 25,017, record -71, hp 15 / np 35 / Windmill; MATCH, PASS.
* **c3** `logs/l51_a_c3_poweron.inputs.txt`: = c2 with a no-hit end (beam e10): 5-2 control 25,019, record -69, exit hp 15 / np 35 / Windmill; MATCH, PASS.
* **c1** `logs/l51_a_c1_poweron.inputs.txt`: 5-2 control 25,059, record -29 (hit-assisted pillar, 24,615 at X 2,800).
  **c2** `logs/l51_a_c2_poweron.inputs.txt`: 5-2 control 25,018, record -70, exit hp 12 / np 35 / Windmill; verify finish +
  chain MATCH, judge PASS.
* Where the rest is (vs TAS +87 in c2): the climb at X 1,504 (+21), the 24-f wait for the #19 bird, the 23,905 bird boost
  missing (~+50 incl. the pillar climb), and the start (+5). A wall bird kept alive past 23,355 would recover most of it.

## 5-1 lock round (third: bird phase) (2026-10-27; agent l51c; tools `work/l51c/`)

Results (all NesHawk = Mesen on every frame, judge PASS, chain MATCH, locked rows identical):
* **c3b = 5-2 control 25,004 (c4 - 13, record -85), exit hp 15 / np 35 / Windmill** (c3a = the same prefix on c2's end, hp 12);
* **c3d = 24,998 (c3b - 6, record -91), exit hp 12 / np 35 / Windmill** (a bird boost at pillar B; costs 3 hp).
Both NesHawk = Mesen on every frame, judge PASS, chain MATCH.
Details in `knowledge/LOCKED_CHAIN.md` "Candidates (5-1)".

### What sets a bird's phase (bank 7 `bird` $C735, `hurt_ryu` $E144) - exact, verified
* Spawn (`bird_rise`): x speed 0. Then every frame (`bird_home`): y += 1 if Ryu's y ($8A) >= bird y else -1; x velocity
  (16-bit signed, $450/$448) -= 1/16 if bird screen x >= Ryu screen x ($86) else += 1/16; position += velocity. **No `$BF`, no
  slot index, no randomness.** All enemies freeze for the frame when a scroll column is pending (`$4C` bit 6, i.e. each
  time the camera crosses a 16-px column).
* So a bird is a bang-bang pendulum around Ryu's x(t); its phase depends ONLY on Ryu's x/y path since its spawn (spawns are
  camera-column triggered, so running at full speed always reproduces the same bird path). Jumps steer y only. The only
  x-controls are **stands (blank rows)** and Left moves; both change the orbit energy by 1.5 x (bird speed at start - at end)
  (Left moves: 3 x, but each Left frame costs about 2 f).
* Hit test: |bird x - Ryu x| < 10 and the bird between 25 px above Ryu's feet ($90 = $19; $11 in actions 2/4) and 8 px
  below. Knockback: vy -3, 1 px/f AWAY from the enemy (a hit from the left pushes right), 60 f invulnerable, d-pad ignored.
* Simulator `work/l51c/bsim2.py` (+ `recbase.py` path recording) reproduces the emulator's bird x/x-sub/velocity/y
  EXACTLY on every frame (checked 23,664-23,885) given Ryu's recorded X, y, camera (incl. `$50`) and the freeze flag.
  `sgrid2.py` (one stand + a step stand) and `sgrid3.py` (numpy, any two stands, both birds, crude slash kill) search
  stands in seconds; every hit they predict was confirmed in Mesen (`etest.py`).

### The find
* On c1/c2 the 23,355 slash kills the wall bird because it is ~35 px AHEAD of Ryu (orbit amplitude ~44 vs the TAS's ~70).
  **A 9-f stand before row 23,875 (TAS-eq 23,345, Ryu on the y-96 ground at X ~1,850) makes the bird pass the slash, and
  with 1 more blank row on the y-160 step it gives the TAS's own 23,714 boost from the LEFT** (hit 24,254 X 2,400 y 132,
  pushed right onto the y-96 platform 24,268 X 2,415). That replaces the 24-f step wait: X 2,436 on 24,282 (c1 24,295).
* Search sizes (sim, then Mesen): one stand anywhere on the ground 23,664-24,200 x 0-30 f + 0-30 f on the step (~16,600
  stand pairs): cheapest success cost 10 (all at our 23,871-23,880). Any two stands with total <= 8: 587,120 combos, 0
  successes; total 9: 754,605 combos, successes only with the bird on the RIGHT (Mesen `23735:2,23875:7`: hit 24,253 but
  pushed LEFT, lands X 2,392, 15 f worse); total <= 11 with a left hit: all hit at X 2,402 on the same frame as c3a.
  **So 10 f is the floor for the 23,714 boost by stands; c3a is optimal in that family.**
* Rest of c3a/c3b: c1's Windmill/health rows shifted -13 (health 24,383, floor X 2,596 on 24,391 vs 24,404); the end rows
  of c2 (c3a) or c4 (c3b) from 24,405 graft unchanged.
* The faster climb `cla` (on the y-96 top at 23,654-56, = the TAS path at lag 525, half a pixel ahead of c1): bird state
  recorded with the bird removed for the path (`recbase2.py`), then `sgrid3.py` (two stands <= 16 f): **cheapest left-side
  23,714 boost = 15 f of stands** -> the same lag 540 as c3b. No gain from the faster climb.

### Pillar-B (TAS 23,905) bird on the c3a prefix -> c3d
* c1's single Windmill (Up+B ~24,279) breaks the health lantern but also kills BOTH birds (and the bat). Throw grid from
  the platform state 24,270 (`thrA.py`, jump 24,274-91 x throw a-4..a+7 x optional 2nd throw: 2,200 of 4,986 run; `thrA2.py`,
  one throw 24,298-24,329: 575): **one LATE throw, Up+B 24,311-13 with the jump at 24,274-76, breaks health (24,371),
  kills the bat and keeps both birds**, X 2,596 on 24,391 as c3a, np 35. (Two throws can too, but np 30.)
* With both birds alive, c4's/c2's end rows get hit repeatedly. Stand + jump grid on the floor (`pilB2.py`, 1,846: stand
  at 24,400/24,424 x 0-33 f x jump delay 0-27): best = **a 3-5 f stand, jump ~24,432 -> bird hit from the left at y ~164
  (hp 15 -> 12) -> on pillar B's top at X 2,694 on 24,481-82** (c3b's climb: 24,487). Then a beam (`gbeam.py`, goal
  `$5C`=0, width 200, 260 f) dodges both birds to the trigger 24,718 (c3b 24,724). Gain 6 f for 3 hp.
* NesHawk pad-read conflict: with the stand on 24,425-27, NesHawk read the Right on 24,428 as blank (Mesen did not).
  c3d uses the 4-f stand (24,425-28), whose Mesen state equals NesHawk's at 24,481 (`ramdiff`: stack only).

### Dead ends / not found (sizes)
* Single stands of 1-8 f anywhere on the ground 23,664-24,200 (+ a step stand) never give the 23,714 boost (sim, ~16,600
  combos); two stands totalling 9 give it only from the right (pushed back, 15 f worse in Mesen).
* The wall bird on the TAS's exact orbit (amplitude ~70) needs ~57 f of stands (sim, best 23,808 + 57): too costly.
* Pad input during the knockback does nothing (28 Mesen variants).
* 2-throw pillar line (np 30): on top 24,485 at X 2,694 and the birds still hit later; dropped for the np 35 line.

### Open
* hp vs time: c3d is 6 f faster than c3b for 3 hp (exit 12 vs 15). 5-2's TAS takes 9 hp of boosts (12 -> 3).
* The stand costs are now the bird-phase price: 10 f (23,714 boost) + 4 f (pillar B). Bird phase is fixed by Ryu's
  path; anything that changes Ryu's x(t) earlier (climb, wall hit) shifts it, so re-run `sgrid3.py` on any new climb.
* For 5-2 / 6-x: type-11 birds follow the same rules; record a bird-free path (`recbase2.py`) and search stands with
  `sgrid3.py` before beaming.

## 5-3 prep (agent l53p, 2026-10-27; plan in LOCKED_CHAIN.md "Next: 5-3 plan"; tools `work/l53p/`)

Room layout (from the `$300` maps, `work/l53p/roommap0.py`). Tile kinds -> `ground_flag` $E782:
* 1 = $0C (wall, no floor);
* 2 = $03;
* 4 = $1C;
* 7 = $10 (floor);
* 8 = $15 (floor + walls);
* 9 = $20 (steps / ladder face);
* 13 'M' = exit.

* **Leftward rooms 27 / 29 / 31 end the same way.** There is a wall column at X 96-127 (left half '9' = ladder, right half
  '1') from y 80 to 191, open underneath at y 192. Its top is the exit tile 'M' (X 96-111, y 64-79) next to an '8' cap
  (X 112-127). The '84' pillar (X 160-191, top y 128) stands to its right.
* **Rightward rooms 28 / 30 / 32 start the same way**: an entry shaft X 64-95 between the '21' column (X 32-63, '84' top
  y 192) and the '91' column (X 96-127, '84' top y 160). Ryu appears at X 91 y 232 against the ladder.
* **The exits of rooms 28 / 30** are the ladder face of the right column (X 672) climbed from the left.
* **Room 32's exit** is a jump from the y-112 platform into the 'M' at X 320 y 64.

Mechanics (bank07):
* `touch_walls` $E677 does nothing at y < 72: no wall check, floor check or exit check. Its two touch points are
  (X + 5, y - 5 / y - 1) and (X - 9, y - 5 / y - 1). The exit fires when one of them is in a tile of kind >= 10, at y >= 72.
* `direction_action` $F087: d-pad nibbles 3 (L+R), 7, 11-15 (incl. U+D+L = $0E) go to `ctrl_idle`. That means no turn and
  no speed change, but `move_ryu` $E833 still steps Ryu by the pad's Right/Left bit. **Moonwalk** = full speed against the
  facing.
* Legal air control against the facing = `drift_speed` 0.5 px/f.
* Wall jump-off $EC34 needs `$28` exactly $81 (wall on the left) / $82 (wall on the right). It sets vy -2 (~14 px rise in
  ~9 f), flips the facing away from the wall and writes `touching` = $C0.
* `hurt_ryu` $E144: Ryu turns toward the enemy and is pushed away at 1 px/f, vy -3 (~28 px). **If he touches a wall at
  y >= 72 the next frame, he clings again**: a hit on a clinging Ryu gives no lift (`axe31bf.py`).
* Thrower $C33C: timer = `$BF >> 1` at every walk state. Axe $CAE9: x speed = (`$BF` & 1) + `$BF`/256, y frac = `$BF`,
  vy -4.

Results:
* **Room-27 exit, legal (beam `b_ex27b`)**: from TAS 26,900 (X 254 y 208), walk left under the wall, jump at X ~90, climb
  the '9' face with `[A+Left x2, Right x6]` x 6 -> room 28 on **27,059 = TAS +46**, hp 3, 0 spins. Rows
  `work/l53p/b_ex27b_h3n35i133.txt` (from TAS frame 26,901).
* **Rooms 29 / 31 exits, the same method**: `b_ex29` (from TAS 27,800) -> room 30 on 27,975 = **TAS +54**; `b_ex31` (from TAS 28,540) -> room 32 on 28,692 = **TAS +63**. Both hp 3.
* **Room-27 pit, open.** The TAS crosses it with jump-offs + U+D+L. Legal drift is too slow to reach the next wall, and the
  gap X 512-527 is a pit. Tested:
  * beams `pit27`, `pit27b` stall at the X-543 pillar;
  * the ladder of the X-672 column was never grabbed (`pitgrid.py` 576 cases; beam `plat27`; `diag.py` shows touch $80
    only at X 679-684, y >= 160).
  The record is on the y-112 platform here, only ~+17 behind the TAS.
* Spin necessity (`spintest.py`, TAS line, hp 3): each of the 11 spins replaced by nothing or by a pure Down+B slash ->
  hit or death in 10 of 11. (Down+B+Left still spins: nibble 6 = `ctrl_left`.)
* Throwers (`bf53.py`): see the LOCKED_CHAIN table. Raw: `bf28a.out`, `bf28b.out`, `bf31.out`.
* Head start `pre53_26704.txt` (97 rows from the control row) = TAS on Mesen and NesHawk. It is arrival-independent for
  `$BF` / hp / ninpo / invincibility. Junk in the enemy slots changed 2 of 5 trials at the first t0 spawn (26,651).

## 5-2 lock round (room 23) (2026-10-27; agent l52a; tools `work/l52a/`)

On the locked chain `logs/l51_c3d_poweron.inputs.txt` (5-2 control row 24,998; our frame = TAS + 571 at the control).
Handover and states: `knowledge/LOCKED_CHAIN.md` "Agent notes (5-2)".

### Result
* **Room 24 on 25,495 = TAS +50** (TAS 24,874 + 571 = 25,445; record ~+72; old fallback r4_52_h2 +108), hp 12,
  np 50, J&S. Rows `work/l52a/d3_stage.txt` (power-on `logs/l52a_d3_poweron.inputs.txt`; c1 25,499 and c2 25,496 are the earlier
  versions; d1 = 25,493 with one J&S spin, np 45); NesHawk = Mesen every frame; judge PASS on the power-on file.
* Splits on this line: prefix (199 rows) = TAS exactly; the block climb (`b_r23a`) +12; the free +10 lantern (B 25,218-19, mid-air,
  np 40 -> 50, 0 f); walk off the y-96 platform instead of the TAS's jump to the wall; J&S pickup costs 2 blank rows in the air;
  floor + left shaft.
* Arrival for rooms 24-26: from the room change our frame = TAS + 621 (room-24 control row 25,518 = TAS 24,897); Ryu's state equals
  the TAS's (only np, `$BF`, timer, `$87/$89` and dead-slot junk differ; scripted rows give identical paths on both).

### Why the TAS's over-the-wall exit is not legal (bank 7 `touch_walls` $E677, `player_control` $EB7B, `ryu_body` $EFF1)
* `touch_walls` returns at once while Ryu's y < $48 (72): no wall flags, no facing update, no exit check above y 72.
  The touching byte `$8C`: bits 2/3 = wall on the left (`ground_flag` $0C of kind 1 at x-9), bits 0/1 = wall on the right
  (kind 2/3/5/6/8 at x+5), bit 5 = steps (kind 9 at x+5), bit 4 = floor, **bit 7 = "let go"**: set by a jump-off ($C0) or when a
  wall tile is overlapped from its passable side; while bit 7 is set and Ryu still overlaps any wall tile, NO wall bits are added,
  so he passes through. Kind 1 (the X-96 wall) blocks only from its right side; kind 2/9 (the X-48 column) only from its left.
* Facing: set LEFT by the wall-on-left flag at each check (y >= 72), right by $02/$20; a jump-off flips it (`eor #$40`) and sets
  run speed; in the air facing never changes otherwise. **In the air, holding the direction you face = run speed 1.5 px/f, holding
  away = drift 0.5 px/f** (`ctrl_left`/`ctrl_right`). U+D+L (pad $0E) maps to `ctrl_idle` (direction table $F087), which keeps
  the speed while `move_ryu` still steps left: that is the TAS's 1.5 px/f leftward flight while facing right. Legal Left (or
  Up+Left/Down+Left, $02/$0A/$06) always calls `ctrl_left` = drift when facing right; only frames with a NEW A or B press skip
  the speed write (they keep, never raise, it).
* The exit needs y in 72-84 with x-9 or x+5 inside the exit column (X 48-63), i.e. X <= 72 coming from the right. From the X-96
  wall's right face (clinging x ~120), that is ~48 px, so ~32 f at 1.5 px/f, while y must stay < 72 over X 105-120. Every legal way to
  be above y 72 there is a wall jump-off from that face, which always leaves Ryu FACING RIGHT (the check that frame set facing left,
  the jump-off flips it) -> 0.5 px/f -> ~96 f for 48 px; a jump-off rises 14 px and is ~30 px below its start 32 f later. A ground
  jump from the y-96 platform (left edge X 189) crosses y 72 coming down at X ~133 and y 84 at X ~131 (48 px rise, 1.5 px/f): 58 px short.
* The "grab inside the wall" case (Ryu back at y >= 72 at X 105-106, both checks inside the wall: flags $8C) turns him to face left
  and releases him next frame (bit 7), but with y speed 0 at y >= 72: he is at y >= 116 by X 72 (exact: Mesen test from TAS 24,848,
  Left / A+Right x2 / Left: X 90 at y 83).
* Only a knockback could break this: a hit from the right while Ryu clings at y 72-74 makes the next frame's grab happen at y < 72
  with stale wall flags and facing RIGHT, so the next A+Right jump-off flips him to face LEFT at run speed. Even that reaches
  X 72 only at y ~100 (jump-off at ~70, needs <= 54), and room 23 has no enemy that can reach the wall top (the waiting ghoul's long
  hop peaks at y 144; batters stay on the y-96 platform). So the record's line (left shaft) is the only legal exit.
* Search sizes behind this: prep's 3 beams from 24,820 (220 f) and `en23x.py` (4,638 legal cases), plus the code paths above.

### Other facts found
* **+10 lantern X 352: free** (any 2-3 f B in 25,217-25,223 on `b_r23a`, mid-air).
* **J&S lantern (X 144 y 112)**: sword breaks need Ryu y in 105-135 and the lantern 0-31 px in front (`slash_lantern` $DAA2); the
  power-up falls with gravity and is caught at |dx| < 12, |dy| < 17 (`take_powerup` $DB89). Walking off the y-96 platform, a slash
  breaks it but Ryu passes 1-2 px too low/early; 2 blank rows (25,351-52) + B 25,360-61 -> pickup 25,388 (cost 2 f; grid
  `jstest3.py`, 1,386 legal variants: no 0-blank catch, 1 blank breaks the Left-release rule).
  The Windmill (Up+B) never breaks it on this line (67 throw frames tested; on the platform a throw stops Ryu ~16 f).
* The waiting ghoul (type 16, `lurker_*` $CA2E) on the shaft floor X 77 wakes when Ryu is within 40 px and hops at him (long hop
  vy -4 when within 32 px). Running into it costs a hit from the left (pushed back right). c1 jumps over it at once from X 129.
* Left-shaft climb: contact-frame wall jumps on the left wall (X ~24) while facing right (drift back 0.5 px/f) climb ~12-13 px
  per 6-8 f; then a jump right onto the X-48 steps (kind 9, Up = 1 px/f) and a step jump-off into the exit tile at X 43 y 84.
* Block climb (25,180-25,240): the block's right face (X 376) and the X-400 column form a 19-px chimney; a hop gains 14 px, the
  floor jump peaks at y 144 and the block top needs y <= 128 at X 376, so two jump-offs are needed (`b_r23a`); a fresh beam
  (`b_blk1`, width 200) was not faster.

## 5-2 lock round (rooms 24-26) (agent l52b, 2026-10-27; PAUSED; tools `work/l52b/`, handovers in LOCKED_CHAIN "Agent notes (5-2)")

* Rooms start fresh at the load: the room-25 control state on our line equals the TAS's (x/sub/y/vy/action/facing/touch), so
  room searches from TAS states transfer exactly once the line JOINS the TAS state exactly (`sync.py` / `menum.py --tasjoin`).
  **Half-pixel phase matters**: a line 0.5 px off the TAS run dies at the room-24 X-616 jump; fixing the phase in the air costs
  2 Left frames (-4 px). Joins must include vy/vy_sub when airborne.
* Ladder-face ('9') climbs: legal best `[Right, Right, Left, A+Left, A+Right]` (wall on the right) = 1.6 px/f (TAS taps 2 px/f).
  A '9' face tops out at y ~178 under an '8' cap (no cling on '8'); Up climbs a '9' at 1 px/f. The chimney (rooms 24 and 26 entries):
  cross to the left wall first, climb it, wall jump right over the cap = room 24 +37 exact join (best of 2,872 macro cases + beams).
* A wall jump-off needs only TOUCHING (pad exactly A+away), not a cling: falling along the ledge wall in room 26 (X 372-376, y 176-188)
  then `A+Right x2` passes under the '2' column (y 64-159) and lands on the y-192 floor at X 415-421 (tested, enemies removed).
* After a hit from the left Ryu faces left; in the air Right is only 0.5 px/f (spins/slashes do not change facing). The TAS's L+R
  after its 26,061 bird boost is worth ~17 f; our beam line takes the same boost and is on the ledge ~TAS +20.
* Room 25 exit: the under route (walk under the X-48 column, jump at X ~70, climb the '9' face from the left) = TAS +17 with a
  bullet hit on the face (hp -2), +27 without; over-the-top beams +31..+36 (facing right above y 72 = 0.5 px/f drift).
* Spins: the room-24 spin-break and both room-25 spins are needed (dropping any = hits/death; a pure Down+B misses the lantern).
* **Result (candidate e1, d3): 5-3 control 27,397 = record -59; rooms 24/25/26 = TAS +43/+24/+101; exit hp 6 / np 35 / J&S; NesHawk = Mesen every frame.**
* Room 26 thrower: on d3 it spawns at `$BF` 60 (inside the prep's TAS-row band); on our rows it only matters at the ledge end, where a
  jump/fall line avoids its axe. Ground slashes freeze Ryu ~12 f (anim 3), so ground lantern breaks are expensive.
* **Round 2 (e4): 5-3 control 27,360 = record -96, hp 3 / np 45.** The exit bird (spawns when the camera reaches the '5774' platform)
  boosts Ryu into the exit if Ryu stands 4 f on the way (Mesen grid; 0-3 f stands fail): 31 f for 3 hp. A slower, spin-free fall
  from the ledge to the wall-jump spot exists (beam s26c) and was even 4 f faster than the spin line.

## 5-3 room 27 (pit) (2026-10-27; agent l53a; tools `work/l53a/`)

On the 5-2 candidate e4 (`logs/l52b_e4_poweron.inputs.txt`, 5-3 control row 27,360, hp 3 / np 45 / J&S). Handover and states:
`knowledge/LOCKED_CHAIN.md` "Agent notes (5-3)".

### Result
* **Room 28 on 27,835 = TAS +70** (TAS room change 27,013 = stage row 406; record ~+110), **hp 3, 0 hits**, np 45 -> 35 (2 spins),
  rows `work/l53a/ch1_rows.txt` (476 stage rows, row 1 = Left on the control row). With both +5 lanterns: room 28 on 27,839 (+74), np 45
  (`ch1_both_rows.txt`). NesHawk = Mesen on every frame for both (from `l52b_e4_27360`), end RAM equal; judge PASS on the power-on files
  `work/l53a/e4_ch1_poweron.inputs.txt` / `e4_ch1_both_poweron.inputs.txt`. Same rows on e1 (control 27,397, hp 6): identical path.
* Splits vs pure 1.5 px/f leftward running (the TAS is ~3 f behind that at X 400): **the X-672 ladder climb ~+27, the exit ladder ~+46**,
  nothing else. The room-28 arrival state equals the TAS's in position; the same legalized TAS room-28 rows give the same path (`cmp28.py`).

### How the pit is crossed (and what the record does)
* **Record (from `work/a56r2/rec/r53.json`, camera vs TAS camera; video RAM x = video x + cam - 2, y = video y + 9):** his camera starts
  scrolling at t 75 (TAS t 31) and then moves at exactly 1.5 px/f without a stop; he is above the y-112 platform at X 549 at t 135 and runs on
  it to X 445 (t 203). So he climbs the X-672 column's ladder face first (lag 44 from the first move) and the pit itself costs nothing.
  Prep's "~+17" was a misread; his pit costs ~+40.
* **Grab rule** (`touch_walls` $E677): Ryu clings to a '9' (steps, $20) tile when `$8F` = kind at (x+5, y-1) is steps; if `$8E` (x+5, y-5)
  enters a wall/steps tile first (rising from below) the let-go bit 7 of `$8C` is set and he passes through until both touch points
  leave all wall tiles. So: rise under the column while moving LEFT (let-go set), get x+5 out of the tile (x <= 666), then A+Right/Right back
  in -> grab. On steps only A+Left ($82) jumps off (vy -2, facing flips to LEFT, run speed 1.5); Up climbs 1 px/f; Down climbs down;
  anything else holds (`player_control` $EB7B lEBF1..lEC2D).
* **Line:** Left, A+Left at once (stage row 2), rise under the column moving left (`$8C` = $80), A+Right at X 665 y 163 -> grab at X 667
  (stage row 17); climb with jump-off/regrab cycles mixed with Up (`Left+Up x2, Up x5, Left, A+Left, A+Right, Right x2`, ~1.3-1.6 px/f);
  jump-off A+Left at y ~129 (row 43) -> flies left at 1.5 px/f onto the y-112 platform at X ~640 (row 60). Beams: `b_lad1` (width 200),
  `b_cl1` (width 400, goal = landing, rank f + (X-446)/1.5: 0.33 f better = same frame), `b_cl2` (width 900, stopped for RAM).
* **Platform walker:** the room's only enemy near the pit is a type-0 walker on the y-112 platform (spawns X 511 at TAS 26,650,
  wanders X 475-537). A ground slash stops Ryu ~16 f (Mesen); jumping into it gives a hit. The free fix is **a jump + J&S spin at stage row
  123-124 (X ~543)**: kills it, 0 f, -5 np. A no-spin line is 15 f slower (beam `b_pl3`, alphabet without B+Left: X <= 400 on 27,634 vs 27,619).
* Then run off the platform's left end (X ~444), land at X 393 (row 224) = the TAS at lag 24; legalized TAS rows at lag 24 (incl. the TAS's
  26,855 spin) to TAS-eq 26,900, then prep's exit `b_ex27b` (under the wall, '9' ladder at X 96, ~1.6 px/f) unchanged.

### Ruled out (search sizes)
* **Crossing the pit below the platform** (`pitx.py`, TAS state 26,607, hp 12; 2,394 legal cases, 96 more skipped as illegal):
  G1 ground jumps A+Left at every frame of 66 (X 643-545): 0 crossings, all stop at the X-528 pillar's face (min X 543);
  G2/G3 = G1 + one J&S spin or a Down+B slash 1-33 f after takeoff (1,122 each): 0 crossings, min X 543;
  G4 from the pillar cling (prep's head start): wait 0-11 f, A+Right jump-off, then Left / no input / Right / new-press keep-speed
  patterns (`B+Left, -, A+Left, -, -` and `B+Left x2, -, A+Left x2`) (84): 0 crossings, min X 528, 36 deaths in the pit.
* **Why (code):** a ground jump peaks at y 160; the pillar ('1', X 528-543) has wall flags at y-1 >= 160, so Ryu clings or barely clears
  it and then falls 40+ px before X 520, into the pit (X 496-527, no wall at y 192-207 to catch him). After a wall jump-off he faces right,
  so Left = `drift_speed` 0.5 px/f. `speed_x` is a stored magnitude: frames with a NEW A/B press skip the speed write, so Left + new press steps
  at the stored 1.5, but any plain Left frame stores 0.5 again; with one new press per button per 5 f that is at most 0.6 px/f.
  A J&S spin (action 7) writes no speed and gravity (`player_control` $EB7B) is unconditional: no air-physics change.
* **Knockback:** the only live enemy near the pit is the platform walker at y 104-123 (the other slots are dead junk that move with the
  camera); its hit box needs it within 25 px above Ryu's feet, and below the platform Ryu's feet are at y >= 146. No boost exists there.

### Lanterns (room 27, both y 160)
* **+5 X 400: 2 f** (insert `Down+B x2` before stage row 213-217, in the fall off the platform: plain slash, caught at once). A J&S spin
  there (B+Left) breaks and catches it for 0 f but costs the 5 it gains.
* **+5 X 240: 2 f** (A+Left x2 at stage rows 298-299, `Down+B x2` inserted 9-15 rows later).
* Both: room 28 on 27,839 (+4 f), np 45 at room 28 instead of 35 (`lantx.py`: 17 / 702 / 560 cases).
* Down+B is the only plain slash in the air with J&S (B with Left or alone spins); it costs the 2 frames without Left (release rule).

### Room 28 phase (for l53b)
* Thrower x = (F + L) mod 256 with F = 27,360 and L = lag at the spawn: L = 70 (no lanterns) -> x 38; L = 74 -> x 42. On TAS rows thrower #1
  wants 155-255 / 0-29 and #2 123-255 / 0-7: both bad. Fix in room 28 (re-scan with legal rows) or accept a k-f wait.

## 5-3 rooms 28-30 (agent l53b, 2026-10-27/28; tools `work/l53b/`; rooms 31-33: l53c below)

Result (handover in LOCKED_CHAIN "Agent notes (5-3)"): **v1c** = `work/l53b/v1c_poweron.inputs.txt` (stage rows `v1c_stage.txt`, row 1 =
27,360), on l53a's 'both' room-27 line: room 28 27,839 -> 28,326 (**TAS +15**), room 29 -> 28,822 (**TAS +60**), room 30 -> 29,313
(**TAS +18**); hp 3 throughout (0 hits), np 45 -> 5, J&S. NesHawk = Mesen every frame, judge PASS, verify chain MATCH.

### HP
* Damage per touch = ROM table `enemy_damage` ($B560 bank00, by type; `hurt_ryu` $E144 subtracts it): 1 for thrower, axe, batter,
  soldiers, bat, dog, jetpack ninja + shuriken, machine-gun shot; 2 for ghouls and thrown knives; **3 for bird, stone man and its ring**.
  So hp 3 is enough when no bird / stone man touches; rooms 28-30 need no hit at all.

### Room 28 (rightward) and the thrower phase
* The TAS's rows on the real e4 arrival (Ryu state = TAS 27,035 exactly) take the thrower-#1 axe at TAS-eq 27,158, as prep said.
* **On legal rows the phase is harmless: beams (minhp 3) pass both throwers with 0 hits and no wait** (`r28a`, then `r28c` to the exit).
  But the outcome is very phase/entry dependent: the same beam from a TAS-joined but 17 f slower entry (`ent3d`, lag 852) needed +56 f
  (`r28f`, 28,382) - the throwers force waits there. Thrower = walk timer `$BF>>1`, toss, hold 12 f, repeat; axe x speed `$BF&1` + `$BF`/256.
* **Entry (rooms 28/30/32 share it)**: the TAS taps up the ladder at 2 px/f and moonwalks (L+R) off the left ledge. Legal best found:
  a chimney start (A+Left off the ladder, wall jump-offs on the left column, `b_led28.txt`: on the ledge at control + 36 = TAS +7), Right
  (turn), A+Right, land on the column top, A+Right again (`b_ent28g.txt`): X 200 at TAS-eq +9. Climb cycles: `[A+Left x2, Right x6]` (c2)
  and `[Left, A+Left, A+Right, Right, Right]` (c1, 1.6 px/f) only jump off at y 198/211 or 202/210 (13 or 8 px steps) and the ledge needs
  a jump-off at y <= ~206, so pure climbs cost +20 (c2) / +24 (c1) (grid `ent3.py`: 3 cycles x 32 climb lengths x tails x 7 x 2 x 3).
* np: 5 spins and both lanterns (+5 X 288, +10 X 496): 45 -> 35 (TAS 3 spins, net 0).

### Room 29 (leftward)
* Entry: `[A+Left x2, Right x6] x 5, A+Left x2, Left` -> floor X 600 at TAS +10 (grid `ent29.py`, 557 legal variants; a beam found nothing
  faster); then the legalized TAS rows follow at lag 10 with 0 divergence to TAS 27,800 (no `$BF` reader in this room).
* Exit = prep's under-the-wall + '9'-face climb; beam `ex29f` (prep's ex29 rows to 27,930 + width-300 beam) is 4 f faster than prep's:
  room 30 at TAS 27,971 + 10. Wider/earlier beams (ex29b/c/d, minhp 2 allowed) found nothing faster (damage boosts from the soldiers near
  the wall push Ryu away from the face).
* np: 5 spins (TAS 3). Spin tests (`spint.py`): the TAS's 27,803 spin can be a pure Down+B slash with no hit, and then no further spin is
  needed (`b_r29s.txt`, np +15) but the line is **16 f slower** (room 30 on 28,838). With l53c's price list (np 15 at room 31 saves 14 f,
  np 20 saves 16) that is break-even, so v1c keeps the 5-spin line.
* **Ninpo vs time, measured (all hp 3):** room 28 re-beamed from v1c's 27,943 state with a ninpo weight: np 45 at room 29 on 28,339
  (**+13 f for +10 np**, `r28g`), np 50 on 28,351 (+25 f for +15, `r28h`); r28d np 40 +6 f. Room 29 slash line +16 f for +15 np. l53c's
  room-31 price (np 15 saves 14 f, np 20 saves 16) makes none of these worth more than ~1 f, so **v1c (np 5 at room 31) stands**.

### Room 30 (rightward)
* Same entry as room 28 (the ledge rows transfer: ledge at control + 36), beam `ent30a` to the y-192 block (TAS +10), beam `r30b` to the
  exit (Windmill X 464 / Star X 624 traps avoided by filtering `$C9` != 133): **TAS +18**, 2 spins + the +5 X 336 (as the TAS; both spins
  needed, `spint.py`).
* **Slot junk matters**: the same room-30 rows after a different room 29 (`r29s`) take a bird hit, because the spawned enemies inherit
  x-sub junk from their slots (bird 1 px off). Re-beam room 30 after any room-29 change (`r30c`: 29,331).

### NesHawk pad-read conflicts
* NesHawk drops a pad change on some frames (DMC fetch); Mesen does not. They are **not at fixed frames** (a probe with Select toggled on
  every other row found 16 different ones; they follow the sound effects). Found and repaired in v1: 27,878 (room-28 chimney) and 28,368
  (room-29 ladder). Repair tool `fixnh.py`: beam over the rows before the conflict with that row forced equal to the previous one, tracking
  the original trajectory, until Ryu's full state (X, x-sub, y, vy, vy-sub, facing, touch, scroll) equals the original at a later frame;
  then the rest of the rows stay valid. `nhconf.py` lists conflicts (NesHawk `$2A` != row).

### Tools
`bm.py` (beam from .mst or TAS frame; `--hist`, `--prefix`, `--fix f` = row f must equal row f-1), `chain.py`, `ent2.py` / `ent3.py`
(rightward-entry grids), `ent29.py`, `join.py` (first exact join with the TAS), `spint.py`, `trf.py`, `runst.py`, `asm.py`, `mkst.py`,
`nh53.py`, `nhconf.py`, `nhpad.py`, `fixnh.py`, `g.py` (RAM gate), `lb.py`.

## 5-3 rooms 31-33 + 5-4 (agent l53c, 2026-10-27; tools `work/l53c/`)

Built from TAS states (Mesen `states/mesen/l53p_tas<f>.mst`); rooms start fresh at each load, so the rows carry over to our real
arrival (Ryu's state at the room-31 control equals the TAS's; only `$BF`, np, hp and the timer differ). Handover in LOCKED_CHAIN
"Agent notes (5-3)". Frames below are on the TAS axis (our frame = TAS frame + D, D = our lag at the room-31 change).

### Splits (rows `work/l53c/c53_tas3.txt` from TAS 28,418 = room-31 control row; chain `c53.py`; NesHawk (`nh31.py`, TAS rows from
`ref4751/14_5-3_control`, np poked 20, hp 3) = Mesen on every frame 28,418-29,970, end RAM equal)
| piece | TAS | ours | vs TAS | record | vs record |
|---|---|---|---|---|---|
| room 31 (change -> change) | 235 | 288 | +53 | 304.5 | -16.5 |
| room 32 | 215 | 220 | +5 | 234.4 | -14.4 |
| room 33 + transition (change -> 5-4 control) | 416 | 415 | -1 | ~409 | ~+6 (prep: timing noise) |
| 5-4 (control -> 6-1 load) | 651 | 651 | 0 | | |
| 6-1 load -> 6-1 control | 152 | 152 | 0 | | |

Total from the room-31 change to the 6-1 control: TAS + 57.

### Room 31 (`b_r31h.txt`, 265 rows from the room-31 control row = change + 24 (TAS 28,418: the first row that moves Ryu))
* Rows 28,418-28,527 = the TAS's rows legalized (Up x2, A+Left x2, run, jump 28,470, **J&S spin 28,508** kills the waiting ghoul):
  TAS positions on every frame (`legtas.py`).
* Floor run under the '84' pillar at full speed needs **one more spin (28,564)** for the bird/axe; beam `r31c` (width 200): X <= 114
  on 28,617 = pure 1.5 px/f, with np -5 or -10 (same frame). Without that spin (beam `r31g`, keep np >= 10): 28,651 = +34 f; so on the
  TAS phase the 2nd spin is worth 34 f. On `$BF` 81 the floor beam also found a no-extra-spin run at 28,617 (phase-dependent).
* **Exit = jump under the wall + the '9' face from the left (beams `r31d` width 300: 28,683; `r31h` width 500: room 32 on 28,682 = TAS +53)** (prep `b_ex31` +63).
  A+Left at X 113 y 208 (28,618): rising under the wall with the let-go bit set, out of the wall at X 90, A+Right regrab, then a
  **new 7-f wall cycle `[A+Right x4, A+Left, Left, -]`**: the A is pressed on the A+Right frames (no jump-off: pad $81 with the
  wall on the right), the A+Left frame (A still held, Left new) is pad $82 = jump-off, Left keeps the 2-f hold, then the blank
  and drift right at 0.5 px/f bring x+5 back to the face: ~13 px per 7 f = **1.86 px/f** (the 8-f `[A+Left x2, Right x6]` = 1.63).
* **Thrower (`$BF`), on these rows (`bfscan.py`, all 256): v = `$BF` after the row before the room-31 control (TAS 234).
  Good: 237 of 256. Bad (one axe hit, hp -1, line broken): v = 73, 74, 77, 78, 81, 82, 85, 87, 88 (hit at 28,620-625 under the
  wall) and 197, 198, 201, 202, 205, 207, 208, 211, 212 (hit 28,558-563), 226.** I.e. D = v - 234 mod 256: bad D = 95-110
  (9 values), 219-234 (9 values), 248. **Re-beamed with those phases (floor `r31c_bf81/205` + climb `r31h_bf81/205`): room 32 on
  28,680 (`$BF` 81) and 28,682 (205): a bad phase only needs a re-beam, no time lost.** Re-beam on the real arrival anyway (~45 min).
* Ninpo: 2 spins (TAS 1). The +5 lantern X 64 y 144 is left of the climb (untested).

### Room 32 (`r32_c2_16_13_1_d0.txt`, rows from the room-32 control = change + 24)
* Entry (grid `ent32.py`, 3,350 cases): `[A+Left x2, Right x6]` x 2 (16 rows), A+Left x2 (jump-off onto the left ledge),
  Left x13, **Right x1 then A+Right x2** (Right held 3 f: a 1-f ground turn; Right x2 first = +2 f) -> lands on the right column top
  (X 122.5 y 160) on TAS 28,719 (TAS 28,714 with the L+R moonwalk). Then the TAS's rows from 28,715 legalized (2-f A/B; incl. the
  **J&S spin 28,782**, needed) shifted +5: room 33 on 28,849 = **TAS +5**. **`$BF`-free** (`bfscan`, 256 of 256 same).
* Tried and slower/no result: Up-only climb (28,730+), a 7-f cycle start (`ent32d`, 392 cases: none land), beam `r32a` to the left
  ledge (width 300: 28,687, grid 28,684). Grids `ent32.py` / `ent32c.py` / `ent32e.py`: 1,777 + 1,568 + 456 cases.

### Room 33 + the 5-3 -> 5-4 transition
* Room-33 control row = room change + 23. **Right held from the control row -> trigger (`$5C` 2 -> 4) on change + 255 at X 381**
  (TAS +256: its blank row 29,098 costs 1 f). Right held earlier changes nothing.
* **The stage end waits for Start.** With no Start, Ryu stands in bank 4 forever (tested to trigger + 400). Start on trigger + 5
  or + 6 -> room 34 on trigger + 8; + 1..+ 4 do nothing; + 7 -> + 9. (The TAS: Start on + 6.)
* **5-4 control row = trigger + 160** (the first row on which Left moves Ryu 176 -> 174.5).
* HP refill to 16 on the transition (any hp in 5-3 is fine for 5-4).

### 5-4 (Bloody Malth)
* `logs/a56_5-4_b13` from our control: Left on the control row + b13's rows (TAS 29,261 on) without its Starts: **one J&S spin
  (control + 40), boss HP 0 on control + 54 (timer 149)**, identical for every `$BF` 0-255 (`r54h.py`, 256 of 256).
* **6-1 load (`$6D` 16): one Start (2 f) on kill + 594 -> load on kill + 597.** Earlier Starts do nothing (84 Starts tested every
  7 f through the tally, `r54m.py`: no effect). **6-1 control row = load + 152** (Starts after the load do nothing; `r61.py`). b13's Starts (29,906,
  then 29,911 by the 5-f rule) lost it 2 f: **legal 5-4 = TAS +0** (control -> load 651 f, as the TAS).
* **Timer phase:** `$62` at the 5-3 trigger (frozen through the transition) <= 55 -> load on kill + 597; 56-63 -> earliest Start
  kill + 597, load kill + 600 (**+3 f**) (`r54i/j.py`, all 64 values). `$62` falls 1 per frame of play (TAS 20 at its trigger;
  ours 19 on the TAS-state chain). If the real line lands on 56-58, a 1-2 f wait before the trigger is cheaper than the 3 f.
* np at the 5-4 control must be exactly 5 (one spin; leftover costs 3 f/pt at the tally); `$C9` = 133.

### On l53b v1's arrival (room-31 control row 29,337, `$BF` 129, hp 3, np 5) - Mesen
* State `states/mesen/l53c_v1_29336.mst` (`mkarr.py`). The TAS-state rows transfer exactly (room 32 on 29,601 = 29,313 + 288).
* Ninpo price list (np at the room-31 control -> 5-4 control row): **20 -> 30,236; 15-19 -> 30,238** (room 32 without its spin: `b_r32n`,
  +2 f, no hit, `$BF`-free); **5-14 -> 30,252** (room 31 with 0 spins: beam `r31n1` (minhp 1) takes two 1-hp hits, X <= 114 on 29,550
  vs 29,536 with 2 spins; climb `r31cn1`: room 32 on 29,615; then `b_r32n`); 5 with no hits -> 30,266 (`r31n0` + `r31cn0`). A single
  spin (np 10, no hits, `r31s1`): X <= 114 on 29,562, no better than 0 spins.
* Spare ninpo can be burned in room 33 for 0 f: one jump + J&S spin per ~45 f on the run, no lanterns there (`r33burn.py`, 4 spins).
* `$62` at the trigger: 21 (np 20 line), 5 (np-5 line): both <= 55.
* **Handover on l53b v1c** (same room-31 state as v1): `work/l53c/v1c_cn1_poweron.inputs.txt` (judge PASS), the np-5 version:
  5-4 control row 30,252 (record -93), kill 30,306, 6-1 load 30,903, 6-1 control 31,055. **NesHawk from `l53b_v1c_29313` = Mesen on
  every frame 29,337-30,905**, end RAM equal (NesHawk states `l53c_29600`, `l53c_30251`, `l53c_30903`). np-15 variant verified in Mesen
  on the same arrival (np poked): 5-4 control 30,238.

## 6-1 / 6-2 prep (agent l61p, 2026-10-27; plan in LOCKED_CHAIN.md "Next: 6-1 / 6-2 plan"; tools `work/l61p/`)

Room layout (TAS dump maps, `work/l61p/roommap.py`):
* **6-1 = room 35**, one leftward room X 1,968 -> 23 (exit at the left edge, y 144). No climbs.
* **Room 36** (leftward, X 1,512 -> 120): runs and jumps; exit (120, 84) at the top left after a hit boost (hp 16 -> 15 on
  32,560, also on our line).
* **Room 37** (leftward): Ryu appears at (860, 232) at the bottom of a chimney between the tall pillar ('1' X 816-831, right
  face at Ryu X ~841, top y 96) and a block (X 864-895, ladder-face tiles on its left side, top y 192). **The leftward camera
  only starts once Ryu reaches screen x 127 = X 895** (`$4C` 128 -> 129). Then over the pillar top and down-left to the exit
  (120, 80).
* **Room 38**: a one-screen shaft, ladder face X 96 from y 240 up to the exit 'M' (X 96, y 64); Ryu climbs at X 89-91.
* **Room 39** (rightward): Ryu appears at (91, 232) against the X-96 face; the y-160 ledge (X 96-143) on top of it; then a run
  along y 128 / 96.
* **Room 40** (rightward): entry at (153, 232); the TAS goes LEFT over the y-160 floor (X 64-104), up to the y-128 ledge
  (X 32-63) and onto the y-96 platform (X 96-127), then right along the top and down to X 747 y 208.

Mechanics found:
* **`$3E` (`status_i`, bank07 `refresh_status` $F7FC) is a 6-frame counter** that picks which status-bar field is redrawn
  each frame (score / time / health / ninpo / boss / lives, different CPU cost). It runs during play and the boss tally, and is
  frozen through the cutscene. It is part of the 6-1 arrival: on NesHawk, an arrival from a 5-4 kill 5 frames later
  (`$3E` 2 instead of 1) fails the head start even with `$BF` poked to the TAS value, and poking only `$3E` back to the
  TAS value fixes it (`nh_arr2.py --groups`).
* The act-end cutscene also leaves Start-time-dependent bytes (`$394`, `$3C4`, `$3C7`, `$621`; `nh_late.py`). **NesHawk and
  Mesen disagree on some real arrivals**: with real Start delays k (TAS 5-4), Mesen `run_batch` (`kscan.py`) calls k 4 / 10 / 24
  (c 88 / 94 / 108) good, NesHawk calls them bad; k 3 / 17 / 28 fail differently. 28 of 31 k values agree. **Judge the 6-1
  arrival only on NesHawk.**
* `$BF`-poke scans (Mesen) agree with NesHawk `$BF` pokes (6/6 spot checks) but not always with real Start delays (above).
* Enemy-slot history: poking `$BF` after the room-36 throwers (TAS 32,200 / 32,300) gives 256/256 good; the bad room-36 values
  need the full replay from the 6-1 control (leftover axe-slot bytes decide later spawns).
* Fully random junk in `$400-$4A7` at the 6-1 control wrecks the run (NesHawk: Ryu stuck at X 1,759; Mesen crashed); not a
  realistic arrival. Realistic arrivals (5-4 kills delayed d = 2 / 5 / 11) differ in 7-18 slot bytes; copying those slot bytes
  alone into the TAS state changes nothing (Mesen, each byte and all together).
* With J&S held, any B in the air without Down spins (5 ninpo) when ninpo >= 5; with ninpo < 5 it is a plain slash. The TAS's
  air B rows in 6-1 (31,051 / 31,065 / 31,134 / 31,155 / 31,230) therefore become spins if the 6-1 J&S is taken.
* Room-40 U+D+L (33,795-33,816): Ryu faces LEFT and moves left at ~0.45 px/f (the 1-f Right on 33,794 set the drift speed; the
  idle pad keeps it). Legal equivalent: Left 2 / blank 4 duty (0.5 px/f average).

Results (all from TAS states unless marked; files in `work/l61p/`):
* **Head start `pre61_32595.txt`** (2,533 rows, 6-1 control -> room 37 row 2,511 = TAS, J&S + 20, hp 15): Mesen = NesHawk at
  the TAS arrival and at 6 poked c values; PASS. Free lanterns +10 X 1,024 (jump 6 f earlier + air slash) and +5 X 240.
* **Arrival:** Mesen `$BF` scan: 136/256 good (classes H61 36, H36 65, J36 19; `bf_pre61_full.out`, `cls.py`). **NesHawk real
  Start-delay scan from the TAS 5-4 kill (`nh_late.py`, k = 0-60, c = 84 + k): good only for k 0, 1, 5, 8, 14, 16, 20, 34, 49, 53,
  55, 59, 60** (`nh_kscan.out`, `nh_kscan2.out`); Mesen `kscan.py` on the same k: also good at k 4, 10, 24 (`kscan_0_30.out`).
* Mesen `$BF`-poke classes (c = `$BF` on the 6-1 control row; G = TAS-equivalent):
  * G 136: 1-2, 4, 6-7, 9-14, 17-22, 24-29, 32-36, 38, 40-43, 45-72, 74, 77, 81, 84-85, 88-89, 92, 94, 98, 100, 104, 108, 118, 130, 133, 137, 139, 143-144, 147-148, 150-158, 162, 165-166, 169, 176-195, 197-198, 201, 203-204, 207-208, 211-212, 230, 233-234, 237, 240, 243-244, 247-248, 251, 254
  * H36 65: 0, 105, 109, 114, 119, 123, 127, 131, 136, 141-142, 145-146, 149, 159-161, 163-164, 167, 170-175, 196, 199-200, 202, 205-206, 209-210, 213-229, 231-232, 235-236, 238-239, 241-242, 245-246, 249-250, 253, 255
  * H61 36: 73, 75-76, 78-80, 82-83, 86-87, 90-91, 93, 96-97, 99, 101-103, 106-107, 110-111, 113, 116-117, 120-121, 124-125, 128-129, 132, 134-135, 138
  * J36 19: 3, 5, 8, 15-16, 23, 30-31, 37, 39, 44, 95, 112, 115, 122, 126, 140, 168, 252
* **6-1 J&S fix** (`pre61js_32595.txt`: B+Left 31,015-16 breaks the J&S lantern X 528, extra B+Left 31,057-58): Mesen, all 36
  H61 c values clean to 31,487. NesHawk real arrivals k 0-30 (`nh_kscan_js.out`): 6-1 passes for 29/31 k, then room 36 is hit at
  row ~1,924 (TAS-eq 31,986, the dogs t9) for every k - it needs a room-36 repair.
* Room 37: entry (record's way, `r37_pre_cl.txt`) pillar cling 32,696 (TAS +31..33); pillar cycle `[Right, A+Right, A, A+Left,
  A+Left, Left] x 6` + Left; together `r37_top_32763.txt`: pillar top 32,763 = TAS +60. The TAS rows after it at lag 58 are hit
  by the t5 soldiers (TAS 32,992); not repaired (beam `b_r37x` stalled at X 231 y 169).
* Room 38: `[Left, A+Left, A, A+Right, A+Right, Right]` repeated -> room 39 on 33,284 = TAS +16 (`cyc_r38.out`).
* Room 39 entry: `[Right, A+Right, A+Right, A+Right, A+Left, Left] x 5` + Right -> X >= 148 on the y-160 ledge on 33,375 =
  TAS +23 (`cyc_r39e.out`).
* Room 40 entry: `[Left, A+Left, A, A+Right, Right, Right] x 4` + A+Left held -> X <= 128 y <= 185 on 33,777 = TAS +15
  (`cyc_r40e2.out`, 4,081 legal cases); legalized TAS rows die in the pit; a Left-tail grid (3,675) and an 80-f beam found nothing.
* Room 40 platform: `r40_plat_33863.txt` -> y-96 platform X >= 123 on 33,863 = TAS +2 (`r40g.py`, 1,092 cases); the TAS rows
  after it (lag 1-4) meet the room-40 bird at 33,928 or fall: needs a short repair.
* Ruled out / not found: room-37 ladder climb with Up (41 cases) and plain cycles + Right (4,410 cases) never reach the block
  top (the record's wall-jump route is the way); a `-X` beam for the room-37 rest (260 f, width 80) stalls.
* 5-4 -> 6-1: earliest Start = kill + 594 (kill + 595 for the 29,317 kill), control = load + 152 = kill + 749/750.

## 6-3 / 6-4 prep (agent l63p, 2026-10-28; plan in LOCKED_CHAIN.md "Next: 6-3 / 6-4 plan"; tools `work/l63p/`)

Room layout (TAS dump, `tasview.py`, `roommap.py`):
* **Room 41** (rightward, X 33 -> 667): runs along y 208 / 160; the exit (667, 81) is reached from the y-128 ledge (X ~605-660) that
  the TAS gets onto through a bird/axe knockback at (601, 162) on 34,941 (hp 12 -> 11).
* **Room 42** (one screen): Ryu appears at (155, 232) in a narrow two-wall gap (faces X ~149 / ~155), the y-160 platform (X ~152-200)
  above it, a two-wall chimney X ~215-235 on the right up to y ~70, the exit at the top left (184, 75). The record goes the other way
  (left along the y-208 ledge, the X-73 column, the y-96 platform, exit jump from the left).
* **Room 43** (leftward, X 1,976 -> 113): entry chimney at X 1,945; long run; two faces climbed by the TAS with 1-f wall-jump taps:
  X ~762 / 746 (top y 128, 35,982-36,007) and X ~569 (top y 128, 36,121-36,141); exit (113, 84).
* **Room 44** (rightward, X 92 -> 1,003): entry chimney X 92-106 (the TAS moonwalks over its right wall at y ~172), run, wall pair
  X 552 / 572 (36,790-36,829, top y ~96), then the 288-f L+R run to the exit (1,003, 208).
* 6-4a (room 45): pedestals as in round 4 (L 27-71, M 96-132, R 189-228; tops y 160); the orb at (135, 120).

Mechanics found:
* **J&S air B:** with ninpo >= 5, B in the air spins, **also Down+B with Left/Right held** (TAS rows legalized with Down added and the
  direction kept still spun at 34,689 / 35,245 / 35,312). Only Down+B with no direction is a plain air slash. With ninpo < 5 every air
  B is a slash: the TAS's 6-3 rows then play TAS-exact with J&S (np 0 poked: rooms 41, 43 35,231-35,982 and 36,008-36,121, 44
  36,540-36,791).
* **The TAS's Windmill star persists across the room change**: `$C8` = 1 from the 36,426 throw (room 43) until 37,084 (room 44) and
  kills what would hit Ryu at 37,042 / 37,097; it also breaks the +10 X 528 lantern (36,767). Item 133 poked at 36,850 -> hit on 37,042.
* **J&S spin on the Masked Devil's orb: at most 11 hits** (16 -> 5) per spin on the arc from the left pedestal (2,376 cases, `mdjs2` /
  `mdjs3`; the round-1 NesHawk experiment's 13 was with a different arc). The second spin from a straight jump on the middle pedestal
  (x 108) finishes it 4 frames after it starts.
* **Tally / Start / END rules** and the timer: see LOCKED_CHAIN "Transitions". `$3E` decrements every frame of play and tally.
* The demon: the pod (type 38) falls and rolls on the floor after a few hits; its timing and the type-41 objects (the demon's shots)
  depend on `$BF`: with `$BF` 0 (poked at control - 1) `r2d5` is hit by the rolling pod on 39,039 and never kills.

Results (files in `work/l63p/`; all from TAS states):
* Room 41 legal +2 (`r41_34992.txt`), arrival classes (NesHawk `nhbf.py`, 256 values): 69 TAS-equal; reader = the thrower (type 2)
  spawning on 34,785 (first slot divergence), then the hit timing. No no-boost route found (`sg_r41n` 312 cases, beam `b_r41n`).
* Room 42 TAS side: entry `[Right, Left, Left, A+Left, A+Right] x 4` + Right: +9 (`r42e_35056.txt`); the chimney climb is legal
  (beam `b_r42y` = TAS heights to y 66 on 35,128) but the exit over the X-208 wall needs the TAS's U+D+L (left at 1.5 px/f facing
  right): facing right Ryu drifts at 0.5 px/f and clings to the X-208 face (y 57-72); 3 beams + 2,360 cycle/grid cases found no legal
  exit. The record's line (a56 `r4_63_h4`) = 220 f, `$BF`-independent (NesHawk 16/16).
* Room 43: entry C8 +6 (`r43e_35238.txt`); X-762 face beam +24 (`r43w_36031.txt`; score -y - 0.2X; the cycle
  `Left x5, [A+Right x3, Left x9] x5` = +50); X-569 face beam +4 (`r43w2_36145.txt`: `A+Right x2, A+Left, Left x12, A+Right x2, Left x4,
  A+Right x2, Left x2`; A held 3 rows while the direction flips). J&S np 0: hit at X 287 (36,319); beam `b_r43j` avoids it (X 134 on
  36,421, ~+3) but misses the exit (the TAS wall-jumps at (133, 128) on 36,422; 649 jump-pair cases after the beam: none).
* Room 44: entry `[A+Right x2, A+Left, Left, -] x5` + Right ~+20 (`r44e_36567.txt`; beam none); wall beam +17 (`r44w_36867.txt`);
  +10 X 528 on J&S: air B+Right 36,772-73 (0 f); end on J&S: hits at X 891 / 974; a spin on 37,040 (jump A+Right 37,039) clears the
  first (beam `b_r44k`, np 15 -> 10); the second still hits and the knockback lands Ryu on the y-192 step at X 1,004 without the
  trigger. Windmill X 880 TRAP near the jumps there.
* 6-4a: `md_js10.txt` (J&S + 10, kill control + 74, hp 16, `$BF`/`$3E`-free; NesHawk: Start 37,943 = K + 591, load 37,946, 6-4b
  control 38,098 = 6-4a control + 820), `md_js5.txt` (J&S + 5, + 89).
* Tally Start constant: earliest Start = K + 3T + 3np + c with c = 146 (TAS 6-4a / 6-4b kills), 147 (`md_js10`, 5-4), 148 (l61p's
  29,317 kill); `$62` / `$3E` poked after the kill do not change it.
* 6-4b: `r4k2` kill control + 253 for all `$BF` / `$3E` (Mesen 256 + 6, NesHawk 7); its Start is 2 f late (earliest = K + 146 + 3T).
* 6-5: `r2d5` kill control + 316 only for 75/256 `$BF` (Mesen `bf_65_r2d5.out`; NesHawk `nhbf_65.out`); `$3E` 0-5 no effect.
* Head start `pre63_35212.txt` (room 41 legal + room 42 on the record's line, 652 rows from the 6-3 control row, room 43 on
  F + 651 = TAS +67; judge PASS; NesHawk). The TAS rows after the room-43 C8 entry do not re-join at lag 73 (`chain_43a.txt`).
