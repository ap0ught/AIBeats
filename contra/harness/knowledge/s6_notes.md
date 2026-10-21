# Stage 6 (Energy Zone) - builder notes

Emulator BizHawk 2.11.1 / NesHawk, `Contra (USA).nes`. Everything below was measured in the emulator unless it says
"assumed" or "estimate". All start states are DEBUG states (stage and weapon poked: `states/dbg/s6_pre`,
`states/s6/ph<d>`), so nothing here is part of a run yet; the solver is what goes into the run.

Segment = this stage's first frame with `$2C == 4` to stage 7's first such frame. **Record: 4,143 frames.**

## Result

| start state | `$1A` on the first frame | segment | vs record | lag | replay | check_inputs |
|---|---|---|---|---|---|---|
| `s6/ph66` (title delay 66) | 128 (phase 0) | **4,032** | -111 | 15 | two replays identical, no death | PASS |
| `s6/ph100` | 162 (34) | 4,055 | -88 | 14 | same | PASS |
| `s6/ph1` | 63 (63) | 4,065 | -78 | 15 | same | PASS |
| `s6/ph70` | 132 (4) | 4,067 (boss beam width 8) | -76 | 17 | same | PASS |
| `dbg/s6_pre` | 62 (62) | 4,087 (older parameters) | -56 | 22 | same | PASS |
| `s6/ph37` | 99 (99) | 4,112 | -31 | 22 | same | PASS |

Best legal segment: `logs/s6/ph66.inputs.txt` (4,032 rows; facts in `logs/s6/ph66.seg.json`). Weapon out `$13`
(Spread + Rapid), no death, 3 spare lives out (2 in + the 20,000-point life; a real run arrives with more).
"Verified" = the rows were replayed open-loop twice from the start state, the per-frame trace hashes match, Bill never
dies, and the frame after the last row is stage 7's first playable frame. Six starts (six phases, six random-number
histories) all finish; the first version of the solver failed from two of them (see "Failed / fixed").

## Timeline of the best segment against the record

Rows from the stage's first frame; record = video frames x 60.0988/60 from `record_events.json`.

| event | ours (ph66) | record | |
|---|---|---|---|
| top of the stairs (world x 365) | 328 | - | |
| on the bottom floor after the drop (x 565) | 529 | - | |
| past the L-box pit (x 1130) | 1,098 | - | |
| foot of tower 1 (x 1300) | 1,270 | - | phase here = start phase + 116 (mod 128) |
| top of tower 1 / floor behind it (x 1519) | 1,499 / 1,576 | - | 306 frames for 219 px |
| top of tower 2 / sniper ledge (x 1714) | 1,762 / 1,845 | - | one 5-frame pause |
| out of tower 3 (x 1892) | 2,061 | - | 791 frames from x 1300 = the no-stop time |
| past the "Leap of Faith" pit (x 2185) | 2,355 | - | no wait (random number steered, below) |
| on the last platform (x 2699) | 2,873 | - | |
| boss created (16 frames into the reveal scroll) | 3,293 | "appears" 3,370 +/- 6 | 77 ahead |
| boss HP 0 | 3,434 | first explosion 3,540 | 106 ahead |
| stage 7 first frame | 4,032 | 4,143 | 111 ahead |

After the boss's last hit the game needs 598 frames (ours) / 603 (record) to stage 7's first frame: explosions and
the door (about 110), scripted exit from the right cap X = 208, 160-frame delay, score screen 192, 48 draw frames
and 13 lag frames while loading. Nothing there can be shortened except standing at the cap when control is lost
(done).

## The map (screen coordinates, `knowledge/s6_map.json`, made by `tools/s6_map.py` with debug pokes)

Collision cells are 16 px; a floor cell whose top is at y gives a standing Y of y - 12. Bottom floor standing Y 196,
middle ledges 148, top ledges 100; the last platform and the boss floor 164. `ram.json`'s note "the game adds
VERTICAL_SCROLL to Y" matters: the collision rows in RAM are shifted 16 px against the screen.

* Stairs at x 272 / 304 / 336 (32 px each, a wall under each step). Three jumps are needed; the third is always
  blocked for about 7 frames (Bill cannot land on step 2 further left than x 320). Best first jump: x 226 (x 224 lands
  short; later ones are blocked longer). Floor: 3 frames for the jumps + 7 blocked = 10 lost.
* Top ledge 336..527, gap, then three levels. Route: walk off at 528 to the floor (free), jump at 659 up through the
  middle ledge 688..815 (the first floor gunner's shot passes under), jump at about 790 across the gap to the next
  middle ledge 848..975, walk off its end to the floor, jump the pit 1072..1119 from 1071, one more jump at 1143
  (the third pair of gunners fires along y 188 and y 140: the jump is timed between both shots and lands on the floor
  before the ledge at 1200). Every gunner ("turret man", 10 HP) fires its first shot about 22 frames after it
  scrolls in; a shot at Bill's level costs one jump (1 frame). Killing a gunner before it fires is not possible at
  12 presses a second (5 hits in those 22 frames at that range).
* Tower 1 (x 1408..1455 inside): wall 1360..1407 open only under y 176, platforms at standing Y 148, 100, 52, shaft
  at 1504..1519. Jump at x 1405 (the ceiling ends at 1408; 1404 hits it), three jumps of 40-41 frames, 27 px along
  the top, a 46-frame fall. 305 frames from x 1300 to the floor at 1519.
* Tower 2: the ceiling over the floor is at y 144 until x 1568, so the first jump is at 1568; step (164), platform
  116, top 68; then a jump from 1660 over the EMITTER of the DOWN jet at 1688 (Bill is above y 40 when he passes it)
  onto the sniper ledge (standing Y 52). 262 frames from the floor at 1519 to the ledge at 1714.
* Tower 3 (the "Exo" drop): walk off the ledge at 1824 onto the platform 68, Down+A to 116, Down+A to 164, walk out
  to the right at 1872 and fall to the floor. 216 frames from the ledge to the floor at 1892.
  This is the humans' fastest option; the "B grab" (down to the floor at 1664 and back up three platforms) was not
  played: it is two extra climbs of about 120 frames each against at most 2 pauses saved.
* After the towers: floor to the pit 2128..2175 (jump at 2126), floor to 2300, jump up through the middle ledge
  2304..2575, off its end to the floor 2592..2671, jump at 2650 onto the last platform (164).

## Hazard schedule (measured)

LEFT jets (type `$11`) ignite on the frame `$1A & $7F` equals their phase and are lethal while state bit 0 is clear:

| jet | where | phase | lethal from..to (`$1A & 127`) |
|---|---|---|---|
| tower 1 bottom, 13 segments, y 184 (floor level, reaches x 1344) | x 1448 | `$00` | 0..66 (full length at 25) |
| tower 1 middle, 5 segments, y 136 | x 1448 | `$20` | 32..66 |
| tower 1 top, 5 segments, y 88 | x 1448 | `$40` | 64..98 |
| tower 2 lower, 9 segments, y 152 | x 1608 | `$40` | 64..116 (derived from the 5- and 13-segment ones) |
| tower 2 upper, 5 segments, y 104 | x 1608 | `$60` | 96..130 |
| tower 3 upper ("Exo flame"), 9 segments, y 56 | x 1864 | `$40` | 64..116 |
| tower 3 lower, 5 segments, y 104 | x 1864 | `$20` | 32..66 |
| floor right of tower 2, 13 segments, y 200 | x 1768 | `$00` | not on our route |

A jet exists only while it is on screen (it is created 112 px ahead of Bill), so each tower sees one or two bursts.

No-remedy windows (phase on the frame Bill is at the named place; `logs/s6/scan_t2t3_noremedy.json` and the first
tower scan): tower 1 passes untouched for phase 92..119 at x 1300; tower 2 for phase 50..76 at tower 1's exit;
tower 3 for a 3-frame window. Tower 1 takes 305 frames = 49 mod 128, so the tower-1 window puts Bill at tower 2 on
phase 13..40: **the three windows never line up - there is no phase with zero remedies** (measured: best is one
pause). This is the "god pattern" question answered for our movement: at 12 presses a second and with the Exo drop
it needs one pause.

**Pause.** Under the press cap a pause is at least 5 frames (Start held 2, released 2, pressed again 5 frames after
the first press), not 2. A jet (or a claw in stage 7) whose trigger frame falls on a paused frame does not fire at
all - verified. So a pause removes a whole burst (34-66 lethal frames) for 5 frames. Waiting instead would cost
tens of frames (table: `wait_only_estimate`).

DOWN jets (type `$10`, proximity 32 px): they do NOT reach Bill on the bottom floor (x 1080, 1304, 2264, 2648 were
all walked or jumped under at floor level without a wait); they do kill on the middle and top ledges and they kill
a fall from the middle ledge at 1296. The "L flame" wait of the human route is not needed on our line (the pit
jump from x 1071 passes it).

RIGHT jets (type `$12`): the "Leap of Faith" jet at x 2104, y 152 (9 segments, reaches 2176) is created when Bill
is at x 1992; first burst 64 frames after creation (the wiki's 64 is right, the code note's 96 is wrong), burst
length 50 frames. **The gap to the second burst is `random & 63` taken on the frame the jet is CREATED, not when
the first burst ends** (changing the random number later never changed the gap; changing it before the creation
frame always did). In 20 trials the pit jump passed with gap 0 (= 256), 2 and 40 and failed with 4-36 and 42-49.
The solver changes the random number for free with a two-frame Up or Down aim tap while running, a few frames
before the jet is created (no frame lost); in all six solves one of the first tries worked. The first run stood
still for 50 frames here.

## Lag

13 lag frames are in the stage load (score screen etc.). In play the game lags when many enemy slots and many
bullets are alive at once: with the auto-aim firing at everything on screen, x 2270..2340 (two gunners, four jets
being created, ten bullets in flight) lagged on every second frame - 83 lag frames. Firing only at targets within
60 px (`fire_range`) leaves 1-9 lag frames in play. Each lag frame also shifts the global-timer phase by one.

## Boss

HP 88 with Spread (created 16 frames into the 96-frame reveal scroll, hittable at once). First move 49 frames after
creation; the move is `var1 & 3` (`$05B8+slot`): 0 jump, 1 disc (he stands for 32 frames), 2/3 walk; latched from
the random number at creation and at the end of every move. Touching him kills at |dx| <= 19. The fight is a beam
search (5-frame steps = one Spread volley per step, 10 actions, width 16) scored on damage plus the latched move;
because every action changes the random number the search finds lines where he throws discs and stands still.
Kills: 140-150 frames after creation (141 in the best segment). Point blank (Bill 21 px left of him) gives about
0.85-0.9 HP per frame; the first 60 frames give only 18 (range). Floor for the fight: 88 frames of hits + the
approach, perhaps 115-120 after creation.

## The phase table (`knowledge/s6_phase_table.json`, `tools/s6_phase_table.py`)

How the phases were made, honestly: (1) `tools/s6_mk_phase.py` makes start states by pressing the title-screen
buttons later, as a real run would: waiting before the first press (Select) moves the start only in steps of 2
frames (waits of 10, 14, 34 and 44 frames were used and work; one attempt with 66 idle frames ran into the attract
demo, and the limit was not mapped properly); the second press (Start, to select the game) can be up to 57 frames
late in 1-frame steps before the demo begins. Together these gave every start that was asked for (delays 0..100,
i.e. `$1A` 62..162); whether all 256 values are reachable was not checked. Six such states were solved in full.
(2) For all 128 phases the three-tower cluster (x 1300 to 1900) was solved from a checkpoint of a full solve with a
leading pause of k frames to set the phase (the pause is not counted); the jets were confirmed to move with it (the
remedies change with the phase exactly as the schedule says). The table adds the measured prefix (1,270 frames,
phase offset 116) and suffix. The six full solves agree with the table within 1 frame, except `ph37` where a random
soldier forced an extra jump before tower 1 and cost about 50 frames (random, not phase).

All 128 phases of the cluster were measured: it costs 4 to 46 frames over the 791-frame no-stop time (one to
seven pauses, now and then a 2-4 frame stop). In start-phase terms (start phase = phase at x 1300 - 116 mod 128;
predicted segment with the luckiest boss seen; the six full solves agree within 1 frame):

| start phase (`$1A & 127` on the first frame) | predicted segment |
|---|---|
| 0..10 (best: 5) | 4,028-4,031 |
| 105..127, 11..17 | 4,031-4,037 |
| 18..35, 95..104 | 4,036-4,045 |
| 36..51, 67..94 | 4,045-4,055 |
| 52..66 (worst: 66) | 4,054-4,070 |

**Best 4,028 (start phase 5), median 4,044, worst 4,070; add about 10 for a typical boss and up to 50 when a random
soldier interferes.** Pauses (5 frames each, 1 to 7 of them) are what buys this: with no pause at all the wait-only
estimate from the three windows is 10-137 frames for the cluster (`wait_only_estimate_cluster_cost`; an estimate,
not played), i.e. a pause is worth 0-130 frames depending on the phase.

## What is random and how it is steered

* Leap of Faith gap: aim taps before the jet's creation frame (above).
* Boss moves: chosen by the beam search through its own actions.
* Random soldiers (screens 1-3 and 6+): they are shot by the auto-aim or jumped; one of six starts lost about 50
  frames to one. Not steered.
* Gunner shots: fixed delay after they scroll in; dodged by a jump, or by ducking for 8 frames when a jet is
  overhead (found by the repair search).

## Failed / fixed / not done

* Fixed inputs do not transfer (as `reference_run.md` says): the solver is closed-loop on position and repairs
  deaths with save states.
* First solver version: failed from 2 of 5 phase states (a dodge jump landed on the ledge the next scripted jump was
  meant to reach; a gunner's shot under a lit jet where a jump is lethal). Fixed (jumps that are skipped when Bill
  already stands on their target level; 6-18 frame ducks among the remedies). All six starts now finish.
* A no-pause line through the towers: does not exist for this movement (windows above).
* B (Barrier) pill box at x 1680: not taken (it is below the route; the detour is longer than the pauses it saves).
* The top route before the towers and the bottom-floor line under the last DOWN jet were not compared frame by
  frame; the middle-ledge line is what the repair search settled on.
* The 128-phase table is for the tower cluster, composed with a measured prefix and suffix; only six phases were
  solved end to end.

## Floors and remaining ideas (frames)

* Stairs: 10 lost, floor for this technique. A jump that lands on step 2 at x <= 317 would save up to 7 (not found).
* Gunner dodges before the towers: 4 jumps (4 frames). Killing them first is impossible at this press rate.
* Towers: 791 no-stop + 5 at the best phases. A different climb order cannot shorten the vertical time.
* Boss: 141 after creation now; 115-120 looks reachable with a wider beam / a better opening (20-25 frames).
* End section x 1900..2700: 812 frames for 807 px (pit jump, ledge jump, one dodge, platform jump).
* Total floor estimate at the best phase: about 4,000.

## Files

`contra/stages/s6.py` (route, remedies, boss, `solve()`), `contra/stages/s6run.py` (runner: route steps,
death-driven best-first repair, beam searches, fire policy), `contra/stages/s6ctl.py` (frame controller that
enforces the press rules), `contra/stages/s6lib.py` (emulator wrapper, trace fields, collision reader),
`tools/s6_solve.py` (solve + replay check + check_inputs), `tools/s6_mk_phase.py`, `tools/s6_phase_table.py`,
`tools/s6_map.py`, `tools/s6_worker.py` / `s6_job.py` / `s6_submit.py` (a long-lived emulator for experiments),
`logs/s6/*.inputs.txt` + `*.seg.json`, `logs/s6/scan_cluster.json`, `states/s6/ph<d>.State` (phase start states),
`states/s6/<run>_{tower1,t1_out,t3_out,b_last,boss_dead,end}.State` (checkpoints; `_end` = one frame before
stage 7's first frame).
