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
