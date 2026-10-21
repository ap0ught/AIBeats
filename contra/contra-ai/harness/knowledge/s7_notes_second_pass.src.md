
---

# Second pass (2026-10-12)

Second builder. Everything below was measured in the emulator (BizHawk 2.11.1 / NesHawk) unless it says "assumed"
or "estimate". Start states are DEBUG states as before (stage and weapon poked, or the end state of a stage 6 solve
that started from one), except `s7/real_c1_s7_pre`, which comes from the integrator's real run from power-on. The
first pass's text above is left as it was; where the two disagree this section is the newer measurement.

## Result - stated plainly

**Stage 7 now beats the record's segment (4,488) from every start that was solved with the final code: @@NPHASES@@
starts, best @@BEST@@, median @@MEDIAN@@, worst @@WORST@@ frames (first pass: 4,631 best, 4,700 in the chain
position, 4,783 worst).** Every number is a full solve by `contra/stages/s7.py`, replayed open-loop twice with
identical traces, no death, weapon `$13` out, `check_inputs.py` PASS at its defaults. The three rows whose start
state is `s6/..._end` are chain positions (the state a stage 6 segment ends in); `s7/real_c1_s7_pre` is the real
run's state; "+ n-frame pause" = the phase was set by a pause on row 40, which is not counted.

@@TABLE@@

The first pass's best state (`s7/ph90`, `$1A` 152): 4,631 -> **@@PH90@@**. 26 more verified solves made with earlier
code versions of this pass (4,414..4,487; one failure, fixed) are in `knowledge/s7_phase_table.json` under
`solves_with_earlier_code_versions_of_the_second_pass`; the final code is 8 frames faster than those at the door.

**Chained with stage 6 (stage 7 solved from the state a stage 6 segment ends in):**

@@CHAINS@@

Record for the two stages: 4,143 + 4,488 = 8,631. The best chain was also replayed as ONE input list from the stage
6 start state (`s6/ph66` + 8,439 rows: two replays identical, no death, stage 7's first playable frame at row
4,032, the frame after the last row is stage 8's first playable frame with weapon `$13`; the same for the `ph100`
chain, 8,462 rows; `check_inputs.py` PASS on both lists, `logs/s7/chain_*.inputs.txt`, `tools/s7_check_chain.py`,
`tools/s7_j_chainreplay.py`).

**From the real run.** The integrator's first complete run from power-on (`chain1/`, made with the FIRST-PASS
stage 7 solver: 4,831 frames for stage 7) left the state one frame before stage 7's first frame
(`chain1/states/s7_pre.State`, `$1A` 224 on the first frame; copied to `states/s7/real_c1_s7_pre.State`, not a
debug state). The second-pass solver from that state: **4,428 frames** (`logs/s7/real_c1.inputs.txt` /
`.seg.json`: two replays identical, no death, weapon `$13`, `check_inputs.py` PASS, lag 26) - 403 fewer than the
first pass's solver from the same state and 60 under the record's segment. The press history of the rows before
the state was not passed to this solve (the chain's glue does that; stage 6 ends with idle rows).

## Where the record was faster, and the fix (details: `knowledge/s7_record_compare.md`)

The record's stage 7 was measured from the video frame by frame (camera position every 8 px,
`knowledge/s7_record_landmarks.json`). Against the first pass's best run he lost nothing until camera 2048, then:

* **Heartbreak Alley: he does not stop at all** (camera 2304 -> 2560 in 258 frames). He has the Barrier: the pill
  box at x 1552. The first pass lost 121 frames there (and 17 more before it, 3 at the trio).
* Boss: 150 frames from the start of the reveal scroll to the door's death; first pass 175.
* Rising walls: 14 frames faster than the first pass's best run (which had a local beam there), about 6 faster
  than the first pass's scripted jumps. Carts: about 15 frames over three carts.
* He is slower than the first pass at the claw corridor (waits 21), the six claws (12 + 19) and the gunners (14).

## The route now (changes in bold)

Start, lower floor under five claws, step 480, **jump from the step at 550 onto the rear edge of the cart 624**,
**one aimed volley from the cart that destroys the F capsule so that its item lands behind Bill**, claws 742/758,
**jump to the step 800 from x 762**, the two rising walls by wall-top jumps **without a pull-back**, the three tall
walls, off the ledge at 1216, **claw corridor 1270..1398 by the cheapest plan of waits and pauses, the rolling cart
shot with one volley, the cart 1424 kept alive**, **"Chariot Hop" onto the cart 1424, ride to its front, jump to the
small ledge, jump over the pill box with a down-forward shot, the Barrier caught in the air, drop through the pill
box's ledge**, step 1632, ledge 1696, **a jump from the ledge at 1741 onto the rear edge of the cart 1824**, floor,
**the pit jumped from 2306 onto the rear edge of the cart 2376**, **Heartbreak Alley straight through**, step 2592,
**the trio: wall 1 broken by touch while the Barrier lasts, walls 2 and 3 shot with volleys whose phase and
starting point are chosen by trial**, six claws (two pauses), **gunners shot from 130 px**, last step, **door: one
jump timed into the end of the reveal scroll, then up-forward volleys while walking to the cap**.

## What each change gained (measured)

| change | frames | how measured |
|---|---|---|
| Barrier grab + alley straight | about -137 at the trio | camera 2528: row 2760 (first pass ph90) -> 2601 (n4), of which 16 were gained earlier |
| cost of the Barrier grab itself | +17 against riding the cart and walking on, 0 against plain walking | 182 rows from x 1392 to the floor at x 1574 (the forced 17-frame drop through the ledge; the 29-frame cart ride pays for it) |
| cart 624: jump at 550 instead of walking off the step | -8 | 176 -> 168 rows to x 700 (boards at 613 instead of 625: 27 frames on the cart instead of 15) |
| step 800 from x 762, wall-top jump without pull-back | -6 | on the ledge with the tall walls (x 959) at row 928 -> 922 |
| cart 1824: jump from the ledge at 1741 | -3 | 203 -> 200 rows to x 1920 |
| pit: jump at 2306 instead of 2318 | -8 | 175 -> 167 rows to x 2470 (rear edge of the cart 2376) |
| trio: timed volleys, stop 17 px before a live wall, wait for a dying wall to vanish | -13 | 17 lost -> 4 lost (193 rows for 189 px) |
| gunners: fire range 130 instead of 60 | -5 | row 3337 -> 3332 at the last step (the second volleys are never fired; the first one of each gunner cannot be prevented: it leaves 7 frames after the gunner scrolls in) |
| door: scripted fight (grid) instead of the beam search | -20..-32 | scroll start to door HP 0: 175 frames (first pass) -> 143 in the chain solves, 143..155 over all solves (record 150) |
| no shots while invincible | lag 37 -> 13 (the 13 are in the load) in the best cases | lag rows of the traces |
| claw corridor by plan instead of repair + local beam | 9..47 lost -> 0..24 lost, by phase | the solves' logs |

## Mechanics measured in the second pass

* **Jump**: rises 59 px in 30 frames; 62 frames on level ground; 46 frames when it lands 44 px higher (cart ->
  small ledge), 49 when 32 px higher, about 66 when 32 px lower.
* **"Chariot Hop"**: A pressed on the floor 15-17 px left of a stationary cart's centre puts Bill ON the cart two
  frames later, at its rear edge. With Right held he then rides 29 frames at 1.72 px/frame (50 px). A jump from a
  rolling cart can land on the same cart again (it rolls on at 0.75 px/frame). With the Barrier on, landing on a
  cart still works (the cart is not destroyed).
* **The Barrier item cannot be collected from the floor.** Shot from below, the item flies up 72 px, bounces off
  the pillar at x 1584 and comes back down onto the pill box's own ledge (rests at x 1545, y 106). Pick-up needs
  |dx| < 12 px. The pill box (created when the camera reaches 1312) has HP 1 from 49 frames later, for 81 frames.
* **Dropping through a ledge (Down+A)**: Bill's X is held for 17 frames, then he falls and steers normally.
  That is the record holder's 19-frame stop at the pill box and ours.
* **Barrier**: `$B0` = 144 at pick-up, minus 1 when `$1A & 7 == 0`: 1,145..1,152 frames. Picked up at about row
  1512..1519, it ends 10 frames after Bill reaches the first wall of the trio: wall 1 is broken by touch, walls 2
  and 3 (22 and 54 frames later) are not.
* **At most one bullet damages an enemy per frame, and the other pellets stay alive inside its box** (seen at the
  walls and the door: a volley's pellets are used up one per frame). Point-blank volleys at a rising wall do only 1
  damage (the pellets spawn behind its centre); from 25-45 px they do 4-5.
* **A destroyed rising wall stays lethal for 3 more frames** (walking into it on the frame its HP reaches 0 kills).
* **Rising walls on the step 800**: landing on the SECOND wall kills at any time tried (also when it is complete);
  the top of the first wall ends at x 864 and a jump from there lands on the step at 920, 3 px short of the ledge;
  shooting the first wall down with down-forward shots takes about 115 frames from landing on the step (40 lost).
  With the wall-top jumps the section (camera 688..832) takes 161 frames now; the record takes 162, the first
  pass took 168..176.
* **Door**: its box reaches about 16 px left of and 24 px below its centre. A jump rises 59 px, the core is 36 px
  above Bill: level shots hit only for about 10 frames on the way up and 11 on the way down. Up-forward volleys
  from the ground hit well only while Bill walks through x 153..175 (about 0.75 HP per frame); standing at the
  cap gives 0.3-0.4. Up+Right cannot be held without walking, so Bill cannot stand in that zone (hovering by two
  frames of Left between volleys was tried: no gain on the best line).
* **Soldier waves and lag**: with 12-14 enemies on screen (five soldiers, two flying capsules, the cart, claws,
  walls) every second frame is a lag frame as soon as 5-10 of our bullets are in flight, and about one frame in
  ten without bullets. One solve had 81 lag frames before the trio. The waves are random (the random number is
  advanced by the idle loop); a two-frame aim tap in the alley changes them (the solver tries 19 taps and keeps
  the one with the fewest rows: 44 -> 14 lag frames in the worst case seen).
* **The F capsule** (flies right at 1.5 px/frame, overtakes Bill at the first cart and stays in the line of fire
  for about 250 frames): a stray pellet releases the F item into the wall-top jump path. It is now shot on purpose
  from the cart (Up+Right, frame 0-6 of the ride): the item lands 40-48 px behind Bill.
* **A leading pause on the stage's first row is ignored by the game**; on row 40 it is taken. `ph80` + a 10-frame
  pause reproduces `ph90`'s marks (same rows after subtracting 10, same `$1A` at every mark) to within one frame.

## Lag

13 lag frames are in the load after the stage (rows about 4180 and 4380). In play: 0-3 when no soldier wave
meets our shots, up to about 40 when one does (table above, column lag).

## Phase

With the Barrier the "seeking" claws no longer matter, so the stage should depend on `$1A` mod 128 only (from the
code). Test with the final code, starts 128 apart: `$1A` 72 / 200: 4,439 / 4,408; 112 / 240: 4,443 / 4,425; 96 / 224
(the real chain state): 4,418 / 4,428. So the pairs are NOT equal: they differ by 10-31 frames. In each pair the
rows agree up to the ledge with the tall walls (row 923 / 918 at x 959); the difference comes after it, from the
claw corridor's plan (a random soldier walks into it or not: cost 10 / 0, 0 / 16, 10 / 10) and from the
soldier-wave lag (20 / 16, 52 / 23, 15 / 26 lag frames). Read the table as: phase decides about +-15 frames,
random soldiers another +-15. What still depends on
the phase: the five claws of screen 1 (0, 5 or about 19 frames), the claws 742/758 (0 or 5), the claw corridor
before the cart (0..24), the six long claws (5 or 10), and through the Barrier's timer (`$1A & 7`) the trio by a
few frames. The random soldier waves add 0..40 frames of lag on top, which is not a function of the phase.

## Tried, did not pay (with the measurement)

* Barrier from below (shoot the pill box from the floor at x 1482..1498, collect the item on the floor): the
  item lands back on the pill box's ledge (above).
* One jump over both rising walls: dies in the second wall's zone from every jump point 818..836.
* Landing on the second rising wall, 36 combinations of jump point and wait: all die.
* Shooting the rising walls down while running (forward, down-forward, both): wall 1 dies 115 frames after Bill
  lands on the step: about 40 frames lost, twice what the wall-top jumps lose.
* Door: two or three jumps (187+ rows against 178 for one jump); the first pass's beam search continued from the
  scripted fight's state at scroll frame 60, 90 and 110 (179: no gain); hovering in the up-forward zone (176
  against 175 on the best line; it helps lines without a jump: 199 -> 183).
* Stage 6 boss (side job): the first pass's beam with width 32 instead of 16 gives the same 561 rows (kill 141
  frames after creation). See the end of this section.
* A jump as a remedy against a claw: it "passes" and then puts the next scripted jump into the rising walls (two
  phases failed that way); claws are now answered by a pause or a stop only.

## The solver (`contra/stages/s7.py` + `contra/stages/s7b.py`)

Runner route as before, with scripted procedures for the hard places. Each procedure plays a small grid of
parameters on save states from the state it is given and keeps the best; results are memoised by (row, `$1A`,
random number, position), because the runner replays the route for every remedy trial. A remedy trial that
reaches an unsolved procedure alive stops there and counts as passed. A remedy is charged the frames it really
loses (a jump into a hanging wall was booked as 1 frame and cost 37). One full solve takes 6-10 minutes on one
emulator (first pass: 16-20).

Procedures: `capsule_proc`, `walls2_proc`, `precart_proc` (claw corridor), `bgrab_proc`, `jump_choice` (cart
1824, pit), `alley_proc`, `trio_proc`, `boss_proc2`. Parameters of `solve()`: `lead_pause` (phase scans),
`b_step`, `a_cart`, `e_fire_range`, `boss_beam` (1 = the first pass's beam search).

Failures on the way, stated plainly: the first phase scan had two failed phases (72, 80: a jump remedy under a
claw) and one (144: a soldier in the claw corridor, where the procedure did not shoot); three "phases" of that
scan (168, 184, 240) were the same solve because the leading pause was ignored. All fixed and re-run. One chain
start (`s6/ph1_end`) lost about 60 frames because a gunner's bullet killed every scripted door fight in its first
15 frames; the hand-over point to the door procedure was moved 40 frames later (after that fix the same tail
is 19 frames shorter; the full solve was re-run: see the table).

## Files (second pass)

`contra/stages/s7.py` (first pass: `s7.py.backup_pass1`), `contra/stages/s7b.py` (procedures),
`contra/stages/s7lab.py` (experiment helpers), `contra/stages/s6run.py` (two opt-in additions: `progress_check`,
`_in_trial`; first pass: `s6run.py.backup_pass1`), `tools/s7_phase_scan.py`, `tools/s7_phase_table.py`
(first pass: `.backup_pass1`), `tools/s7_scan_show.py`, `tools/s7_record_compare.py`,
`tools/s7_write_compare_md.py`, `tools/s7_trace.py`, `tools/s7_tr.py`, `tools/s7_trace_view.py`, `tools/s7_pano.py`,
`tools/s7_part.py` + `s7_j_part.py` (partial solves from checkpoints), `tools/s7_job.py`, `tools/s7_workers.ps1`,
`tools/s7_solve_bg.ps1`, `tools/s7_scan_bg.ps1`, `tools/s7_stop_solve.ps1`, `tools/s7_solve_w.py` +
`s7_j_solve1.py` (solves on a worker), `tools/s7_check_chain.py`, `tools/s7_j_chainreplay.py`,
`tools/s7_write_notes.py` (this section = `knowledge/s7_notes_second_pass.src.md` + tables),
`tools/s7_patch*.py` (the edits, in order; 23 = the stage 6 wipe-out recovery), `tools/s7_j_*.py` and
`tools/s6_j_*.py` (experiment jobs),
`logs/s7/scan_<fc>.inputs.txt` / `.seg.json` (final code, one per start phase), `logs/s7/scan/F1..F3.jsonl`,
`final.jsonl` (final-code results), the other `.jsonl` there (earlier code versions),
`logs/s7/f_chain66.*`, `f_chain100.*`, `f_chain1.*` (chains), `logs/s7/real_c1.*` (from the real run's state),
`logs/s7/chain_*.inputs.txt` (stage 6 + 7 as one list), `logs/s7/n4_ph90.*`, `n5_ph90.*` (earlier solves),
`logs/s6/real_c1_live.*` (stage 6 from the real state),
`states/s7/ph<d>.State` (start states, `$1A` = 62 + d), `states/s7/<run>_<mark>.State` (checkpoints),
`knowledge/s7_record_compare.md`, `knowledge/s7_record_landmarks.json`, `knowledge/s7_phase_table.json`,
`shots/s7cmp/` (panorama of the stage with a world-x ruler).

## Left to do, with estimates

1. Soldier-wave lag (0..40 frames by luck): aim taps at more places than the alley, or a tap search over the
   whole Barrier stretch (nothing can kill Bill there, so it is cheap to simulate). Estimate: -10 on average, -30
   in the bad cases.
2. Claw corridor (0..24 by phase, about 10 on average): combinations of a short wait and one pause are only
   partly in the plan list. Estimate -3 on average. Choosing the start phase removes it.
3. Door: 143-147 frames after the scroll starts (record 150) against about 130 if the damage were continuous
   from the first possible hit. Estimate -5..-10 with a search over the firing frames (not just the phase).
4. Rising walls: 19 lost. Nothing found that beats the wall-top jumps; the published runs destroy "one more
   wall" for 5 frames.
5. The first gunner's shot under the low roof: a 6-frame duck. A jump is blocked by the roof. Estimate -3.
6. Screen 1 at the worst phases: a local beam (19 lost) where a pause or one wait should do. Estimate -10 at
   those phases only.
Sum: about 25-40 frames at a typical phase; a segment of about 4,390-4,400 looks reachable.

## Side job: stage 6 boss - not made faster; one robustness fix ported

**Fix ported to the live solver.** The integrator reported (`knowledge/shared_requests.md`, `chain1/FIXES.md`) that
from the real stage 6 state (`$1A` 33) the boss beam search died to its last line at depth 37 and `solve()`
failed; the cure existed only in the chain1 snapshot. Its wipe-out recovery (`beam_search` keeps the beams of
the last 17 depths, goes back 8 then 17 depths and doubles the width, at most five times) is now in the live
`contra/stages/s6run.py` (`tools/s7_patch23.py`; the file before it: `s6run.py.backup_before_wipeout_fix`).
Checked: the live stage 6 solver from that real state (`states/s6/real_c1_s6_pre.State`, a copy of
`chain1/states/s6_pre.State`): **4,050 frames**, two wipe-outs recovered (width 16 -> 32 -> 64), two replays
identical, no death, `check_inputs.py` PASS (`logs/s6/real_c1_live.inputs.txt` / `.seg.json`) - the same 4,050 the
integrator's snapshot produced. The cause (a jump that comes down on the boss scores best) is NOT cured, only
caught. By construction a fight that never wipes out is searched exactly as before; that was NOT re-measured on a
debug start after the port (the 561 rows from `final_ph66_b_last` below were measured just before it).

Speed: only one experiment: the first pass's beam search from `s6/final_ph66_b_last` with width 32 instead of 16: the
same 561 rows (kill 141 frames after the boss is created). Reading the fight's trace: the boss is created at
screen X 240 while Bill is held at X 128 by the reveal scroll; damage starts 22 frames after creation and runs
at 0.57 HP per frame until the scroll ends (33 HP in 58 frames), then 0.92 per frame. With the rule measured
here (one bullet per enemy per frame) and the 10-bullet limit, the damage at range is bounded by 10 pellets
per flight time: about 0.3 HP per frame at 112 px, 0.6 at 56 px, 1.0 from 35 px. So the opening is already near
what the weapon allows; the 20-25 frames estimated in the first pass look too optimistic (ESTIMATE: 5-10 with
perfect pellet use, not verified).
