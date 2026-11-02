## Next: 6-1 / 6-2 plan (prep agent l61p, 2026-10-27)

6-1 = room 35 (one long room, runs LEFT, X 1,968 -> 23). 6-2 = rooms 36 (left), 37 (left), 38 (vertical shaft), 39 (right),
40 (right). Act VI starts after the 5-4 cutscene with hp 16, ninpo 0, no art; only `$BF` and `$62` carry over.
**Headline: 6-1 and room 36 have no banned inputs except 1-f A/B, so the legalized TAS rows ARE the TAS. A verified head start
covers all of 6-1 and room 36 (2,533 rows, = TAS frames, J&S + 20 ninpo at room 37), but it is arrival-dependent: on NesHawk only
13 of 61 real 5-4 Start delays (from the TAS kill) keep it TAS-exact, and there is no free way to shift the arrival, so check it
on the real 5-4 state (`nh_late.py`) and pay the smallest good delay. All of 6-2's banned inputs are in rooms 37-40; legal
versions now exist for room 37's entry + pillar (+60), room 38 (+16), the room-39 entry (+23), the room-40 entry (+15) and the
room-40 platform (+2), all from TAS states; the room-37 run to its exit and the chaining of the pieces are still open.**
Tools and data in `work/l61p/`:
* `dumps.py` -> `tas61_ram.bin` (NesHawk TAS RAM after rows 29,261-34,760: the 5-4 fight, cutscene, 6-1, 6-2, 6-3 start);
  `lib0.py` (`TM(f)`, `XY`; falls back to the l53p dumps); `lib.py` (Mesen helpers, `core_at(f)`, `legalize_tas`);
* `mkst.py` -> Mesen TAS states `states/mesen/l61p_tas<f>.mst` (29,258 ... 34,560; 0 RAM diffs vs NesHawk; Mesen `step()`
  is 1 f off in the act-end cutscene, so the differing bytes are re-synced from the dump at 29,911-30,062);
* `ev.py` -> `tas61_ev.txt`; `rle.py` -> `tas61_rows_rle.txt`; `brk.py` -> `brk61.out` (rule-break spans); `roommap.py`;
* `tf.py` (follow legal TAS rows), `b61.py` (beam), `cyc.py` (cyclic climb patterns, `--ks`), `chtest.py` (prefix + cycle grid),
  `shift.py` (prefix + legal TAS rows at a lag), `r40g.py` (room-40 grid), `r37seq.py`, `l1024.py` (lantern test), `js61.py` (6-1 J&S fix);
* `bf61.py` (arrival scan: `$BF` poked at 30,062, any rows file, `--junk`), `cls.py` / `band.py` (classify a scan by c);
* `nh_trans61.py` (NesHawk: 5-4 kill -> Start -> 6-1 control), `nh_trans62.py` (6-1 -> 6-2, 6-2 -> 6-3), `nhpre61.py` +
  `mpre61.py` (NesHawk / Mesen listings of a head-start file, pokes), `nhdiag.py` (NesHawk slots);
* **`nh_late.py` (NesHawk k-scan of the 5-4 Start delay with a head-start file; `--state NAME --kill K` for our real 5-4)**,
  `kscan.py` (Mesen twin; NOT reliable here), `nh_arr.py` / `nh_arr2.py` (real arrivals from delayed 5-4 kills, RAM diffs,
  `--groups` byte-range swaps), `arrtest.py` / `arrtest2.py` (Mesen byte-copy tests).

Frames are power-on rows on the TAS axis (NesHawk frame k = after row k). **TAS 6-1 control row = 30,063** (Left moves Ryu
x 176 -> 174). **`$BF` in Act VI = (f - 27) mod 256** (checked at 30,063 / 31,638 / 32,573). Let **c = `$BF` on our 6-1
control row = (F - 27) mod 256**, F = our 6-1 control row (TAS: c = 84).

### Transitions (NesHawk)

* **5-4 -> 6-1 (act-end cutscene)**: same as 4-4 -> 5-1. With timer T at kill + 1 (T 149 on every tested kill): **earliest
  Start = kill + 147 + 3T = kill + 594**, a fresh 2-f press; Start one row later gives the same load. **Load = kill + 597,
  6-1 control = kill + 749 = load + 152.** Tested on kills 29,314-29,322 (`nh_trans61.py`, TAS 5-4 rows delayed d = 0-8):
  8 of 9 behave so; **the kill on 29,317 (d 3) ignores the Start on kill + 594** (and a Start held across that row is
  blocked), it needs a fresh press on kill + 595 -> control kill + 750. Not a `$BF` effect (`$BF` poked +1/+2/+3 at 5-4: same).
  So: **press Start (2 f) on kill + 595**: it gives the same load as kill + 594 for all 9 tested kills and is the only one that
  works for the 29,317 kill (or check the real kill with `nh_trans61.py`). The TAS: kill 29,314, Start 29,909,
  load 29,911, control 30,063.
* **Is the Start free / does it shift `$BF` for free? No.** A Start on kill + 594 or + 595 gives the same load; every later row
  delays the 6-1 control by 1 and shifts c by 1 (1:1 cost). Left held from the load gives the same control row (Ryu cannot move
  earlier). A later 5-4 kill also moves everything 1:1. **The only way to choose c is to pay frames** (a later Start).
* **6-1 -> 6-2**: trigger = first `$5C` 0 = the frame after Ryu reaches X 23 (y 144) (TAS 31,359); load (`$6D` 17) = trigger + 128;
  **6-2 control = trigger + 279 (Left; TAS 31,638)**. Left held from trigger + 1 or from the control row = same; Left first on
  trigger + 280 = 1 f late. Start (31,380 / 31,630) does nothing. No free frames.
* **6-2 -> 6-3**: trigger = Ryu reaches X 747 y 208 in room 40 (TAS 34,282); load = trigger + 128; **6-3 control = trigger + 279
  (Right; TAS 34,561)**. Right from trigger + 1 = same; Right first on trigger + 280 = 1 f late. No free frames.
* Room changes inside 6-2: control resumes 23 f after the room change (TAS 32,596 / 33,193 / 33,291 / 33,735).
* `$62` is frozen through every transition and carries on (it only matters at the 6-4a tally; not for 6-1/6-2).

### Splits (room change = the first frame with the new `$6E`; record = first picture after the 22-f black, minus 22, +-3)

| | TAS frame | TAS t | record t | room: TAS | room: record | record loses |
|---|---|---|---|---|---|---|
| 6-1 control (room 35) | 30,063 | 0 | 0 | | | |
| 6-1 trigger | 31,359 | 1,296 | | | | |
| **6-2 control** | **31,638** | **1,575** | **1,584.6** | 1,575 | 1,584.6 | **+9.6** (one room; the record = TAS pace, no detail) |
| room 37 | 32,573 | 935 | 991.7 | 935 | 991.7 | **+56.7** (end of room 36: the record ~+45 at X 64-127) |
| room 38 | 33,170 | 1,532 | 1,690.8 | 597 | 699.1 | **+102.1** (entry chimney + pillar climb) |
| room 39 | 33,268 | 1,630 | 1,817.0 | 98 | 126.2 | **+28.2** (ladder shaft) |
| room 40 | 33,712 | 2,074 | 2,281.8 | 444 | 464.8 | **+20.8** (entry) |
| 6-2 trigger / 6-3 control | 34,282 / 34,561 | 2,644 / 2,923 | 3,153.2 | 849 | 871.4 | **+22.4** (room 40 incl. the transition) |
| **6-2** | | **2,923** | **3,153.2** | | | **+230.2** |

Record pace: **6-2 control <= F + 1,584; 6-3 control <= F2 + 3,153** (F2 = our 6-2 control). 5-4 -> 6-1: the record's 5-4 is
805.3 f (TAS 804; our `5-4_b13` = TAS +2), so the 6-1 control should be <= 5-4 control + 805.

### TAS rule breaks in 6-1 / 6-2 (`brk61.out`), split into legal and banned parts

| TAS rows | what | banned part | legal version / verdict |
|---|---|---|---|
| 30,063-31,358 (6-1) | run left, 30 jumps/slashes | 1-f A/B only | **legalized TAS rows = TAS positions exactly** (Mesen + NesHawk, head start below) |
| 31,638-32,595 (room 36) | run left, J&S 32,353, spins 32,428 / 32,483 | 1-f A/B only | **legalized = TAS** (room 37 on 32,573). The 1-f Right turn at 32,506 held 2 f puts Ryu 1 px ahead on 32,507-32,559; he re-joins by 32,560. Drop the 32,483 spin (it breaks + catches the Windmill X 256): **0 f, J&S kept** |
| 32,596-32,628 | room-37 entry chimney: 28 f L+R (moonwalk right up the block face onto its top y 192), then to X 895 (screen x 127 starts the leftward camera, `$4C` 128 -> 129) | L+R, 1-f | **legal: the record's way** - A+Left off the block face to the pillar face (X 839), A+Right wall jump back onto the block top, walk right to X 895, Left, jump to the pillar: rows `work/l61p/r37_pre_cl.txt` (b_r37e beam to 32,646 + `r37seq.py` grid, 450 cases): pillar cling (X 842 y 144) on **32,696 = TAS +31..33**. Pure ladder (Up x n, 41 cases) and cycle grids (`cyc_r37e.out`, 4,410 legal cases) never reach the block top: the face is not a ladder |
| 32,666-32,703 | pillar right face: A+Left/A+Right taps every 4 f (2 px/f), then U+D+L 15 f over the pillar top (y 96) | period 4, U+D, 1-f | **legal cycle `[Right, A+Right, A, A+Left, A+Left, Left] x 6`, then Left** (`cyc_r37p.out`, 3,560 legal cases from TAS 32,665): top (X <= 822, y 96) on 32,725 = **TAS +22** from the TAS cling. **Chained with the entry: `work/l61p/r37_top_32763.txt` (166 rows from TAS frame 32,596, `chtest.py` 112 cases) -> pillar top on 32,763 = TAS +60** (record: room 37 +102) |
| 32,704-33,170 | room 37 rest: run left over the top, down to the y-128 ledge, into the exit (120, 80) | 1-f only | legal TAS rows at lag 58 follow to TAS 32,992, then the crouching soldiers (t5, spawn by scroll) hit (`shift.py`). Needs a repair; old hand line `logs/r4/r4_62_h2` (a56 round 4: slash the walker, jump at ~298, platform y 160, air slash, ledge y 128, jump at ~155) is the model. A -X beam (`b_r37x`, 260 f) stalls at X 231 y 169 |
| 33,194-33,268 (room 38) | ladder shaft X 89-91, y 232 -> 84: 1-f A+L / A+R taps + L+R, 2 px/f | L+R, 1-f, period < 5 | **legal 6-f cycle `[Left, A+Left, A, A+Right, A+Right, Right] x ~25` -> room 39 on 33,284 = TAS +16** (`cyc_r38.out`, 1,091 legal pattern x rotation cases, from TAS 33,193). Record +28, old A* +22 |
| 33,291-33,332 (room 39 entry) | ladder at X 91 y 232 -> L+R up the X-96 face and onto the y-160 ledge, run right | L+R, 1-f | **legal `[Right, A+Right, A+Right, A+Right, A+Left, Left] x 5`, then Right -> X >= 148 on y <= 160 on 33,375 = TAS +23** (`cyc_r39e.out`, 5,145 legal cases, from TAS 33,290; TAS 33,352). Record: room 39 +21 in total |
| 33,319 / 32,667 | Windmill throws (rooms 39 / 37) | - | we hold J&S: Up+B in the air = a spin (5 ninpo), or drop them; untested on our line |
| 33,736-33,760 | room-40 entry: up the X-160 face with taps every 4 f to y 216, jump off left, a second wall jump at X ~132, over to the y-160 floor | period 4, 1-f | legalized TAS rows fall into the pit (death at 33,765). **Legal: `[Left, A+Left, A, A+Right, Right, Right] x 4`, then A+Left held -> X <= 128 y <= 185 on 33,777 = TAS +15** (TAS 33,762; `cyc_r40e2.out`, 4,081 legal cases from TAS 33,735; hp 14). Not chained to the platform piece (which starts from the TAS state 33,792). A Left-tail grid (`cyc_r40e.out`, 3,675 cases) and an 80-f beam found nothing |
| 33,793-33,860 | jump from (82,160); **U+D+L 22 f = 0.45 px/f leftward while facing LEFT** (idle pad keeps the drift speed set by the 1-f Right at 33,794); land on the y-128 ledge at X 72; A+Right on the ground (no turn) + **L+R 33 f = 1.5 px/f right while facing left** (a right-facing Ryu would cling to the platform's left face) onto the y-96 platform | U+D, L+R | **legal: A x2, `(Left x2, blank x4) x 5` (0.5 px/f average), Right x3 (turn on the ledge), A+Right x2, Right -> on the platform X >= 123 on 33,863 = TAS +2** (`r40g.py`, 1,092 cases; 30+ variants give 33,863; `work/l61p/r40_plat_33863.txt`, rows from TAS 33,793). After it, the TAS rows at lag 1-4 meet the room-40 bird (t11, spawn 33,887) at 33,928 or fall into the pit: needs a short repair beam |
| ~180 rows | 1-f A/B, presses < 5 f apart | press cap | Enforcer (2-f holds) |

**Expected 6-2 on legal pieces (from TAS states): room 36 +0, room 37 ~+60..+80 (pillar top +60, rest unknown), room 38 +16,
room 39 +23 (entry) + rest, room 40 +15 (entry) +2 (platform) + repair -> roughly TAS +110..+150 = record -80..-120.** The record pays +102
in room 37, +28 in room 38, +21 in room 39, +22 in room 40.

### Arrival dependence (`$BF`, `$3E`, cutscene leftovers) - judge on NesHawk only

* **Readers in 6-1 / room 36 (measured):** the throwers (type 2: 6-1 at (427,144) on 31,014; room 36 at (1,214,128) on 31,761
  and (926,160) on 31,953) and their axes (type 18), and **the jetpack ninjas' shuriken (type 21) in room 36** (x moves +-1 px
  with `$BF`; NesHawk `nhdiag.py`). Also two hidden phase bytes: **`$3E` (`status_i`, 6-frame counter of the status-bar
  redraw, frozen in the cutscene)** and Start-time leftovers of the cutscene (`$394`, `$3C4`, `$3C7`, `$621`). Proof: an arrival
  from a 5-4 kill 5 f later fails even with `$BF` poked to 84, and poking only `$3E` back fixes it (NesHawk `nh_arr2.py --groups`).
* **`$BF`-poke scan (Mesen `bf61.py`, all 256 c, from the TAS arrival; the plain legal rows give the same classes):**
  136 good; H61 36 (6-1 thrower axes from 31,059), H36 65 (room-36 thrower axes), J36 19 (a shuriken hit on 32,426, 2 f before the
  32,428 spin). Good c: 1-2, 4, 6-7, 9-14, 17-22, 24-29, 32-36, 38, 40-43, 45-72, 74, 77, 81, 84-85, 88-89, 92, 94, 98, 100, 104, 108,
  118, 130, 133, 137, 139, 143-144, 147-148, 150-158, 162, 165-166, 169, 176-195, 197-198, 201, 203-204, 207-208, 211-212, 230,
  233-234, 237, 240, 243-244, 247-248, 251, 254. Full lists: legal_a56_notes. **This is an upper bound only:**
* **NesHawk, real arrivals = the TAS 5-4 with the Start delayed by k (c = 84 + k), `nh_late.py`, k 0-60: the head start is
  TAS-equivalent only for k 0, 1, 5, 8, 14, 16, 20, 34, 49, 53, 55, 59, 60 (13 of 61; c 84, 85, 89, 92, 98, 100, 104, 118, 133,
  137, 139, 143, 144).** Every NesHawk-good c is Mesen-good, but Mesen-good c 88, 94, 108, 130 fail on NesHawk (Mesen `kscan.py`
  with the same real Start delays agrees with the poke scan, not with NesHawk). Most bad k are H61 (6-1 thrower, ~rows 1,000-1,020);
  others fail early (k 3 / 17 at row 194, k 39 / 40 at row 384, k 28 / 46 at row 553, k 57 at row 757).
* **So the band cannot be precomputed for our chain:** it depends on `$BF`, `$3E` and `$62` (set by our 5-4 kill frame) and on the
  Start delay. **Procedure when 5-4 is locked: save a NesHawk state on the 5-4 kill row K, run
  `venv/Scripts/python work/l61p/nh_late.py 0,1,2,...,40 --state <name> --kill K`** (about 1.5 min per k), take the smallest good k
  (cost k f; k 0 or 1 if lucky). On the TAS kill the gaps between good k are up to 14 f (k 34 -> 49).
* **Free shifts: none** (Transitions).
* **6-1 J&S variant `pre61js_32595.txt`** (B+Left 31,015-16 breaks the J&S lantern X 528, caught 31,020; extra B+Left 31,057-58 = a
  spin at the thrower; the TAS's later 6-1 air B's become spins): Mesen, all 36 H61 c clean to 31,487; **NesHawk k 0-30: 6-1 passes
  for 29 of 31 k (k 3 / 17 still die at row 194), but room 36 is hit at row ~1,924 (TAS-eq 31,986, the dogs t9; np runs out, so
  the room-36 air B's differ).** Needs a room-36 repair before it is usable; it is the way to make 6-1 itself arrival-proof.
* Not tried: an earlier 32,428 spin for J36; spins at the room-36 throwers for H36.

### Ninpo / art / HP (Act VI: 6-1 -> 6-4a)

* Act VI starts with np 0, no art, hp 16. 6-4a needs **J&S + exactly 5** at the 6-3 exit (one spin, the record's kill);
  ninpo and art are cleared after 6-4a. Leftover ninpo at 6-2 -> 6-3 costs nothing (no boss tally); 6-3 burns the excess with
  free air spins.
* **6-1 lanterns** (`python -m ng.solve.items 6-1`; room 35 runs left, so in order of passing):
  * Star X 1,456 y 160 (TAS passes at y 208: untouched; TRAP only with J&S);
  * +5 X 1,216 (TAS 30,558);
  * **+10 X 1,024 y 160: free** - jump 6 f earlier (A+Left 30,684-85 instead of 30,690) + B+Left 30,688-89 -> +10 on 30,693,
    back on the TAS path by 30,733 (`l1024.py`, 88 cases; NesHawk);
  * Windmill X 800 y 128 (TAS passes at y 134 without a slash: never slash there);
  * +5 X 656 y 128 (TAS y 176; ~15 f, untested);
  * **J&S X 528 y 128: free** (B+Left 31,015-16, caught 31,020) - only for the H61 fix above;
  * **+5 X 240 y 96: free** - B+Left 31,203-04 in the air -> +5 on 31,208 (NesHawk: positions = TAS);
  * +10 X 112 y 96 (TAS y 144; ~15 f, untested).
* **Room 36:** +5 X 1,232 y 160 (TAS y 208: a jump + slash like X 1,024, untested); **Windmill X 1,072 y 112 (TRAP; TAS
  passes under at y 189)**; +5 X 1,056 (TAS 31,935); +10 X 800 y 176 (TAS 60 px above; ~15 f); +5 X 544 (TAS 32,285);
  **J&S X 432 y 80 (TAS 32,353: take)**; **Windmill X 256 y 128 (TRAP: the TAS's 32,483 spin breaks it and catches it -
  drop that B; verified, 0 f)**; +5 X 64.
* **Spins in room 36 (needed):** 32,428 (kills the jetpack ninjas) and 32,531 (the TAS's air slash; with J&S it is a spin).
  Without the 32,531 B, or with Down+B there, Ryu is hit and dies at the exit (tested). The 32,537 B then does nothing.
* **Head start exit: room 37 with J&S + 20, hp 15** (TAS: Windmill + 5). 
* **Rooms 37-40** (TAS line; re-check on ours): Star X 176 / Windmill X 432 / FW X 544 (room 37, TRAPS), +10 X 720 (TAS 32,764),
  +5 X 320 (~8 f); room 38 Windmill X 48 never hangs; room 39 +5 X 272, +5 X 320 (cost 1), +10 X 544 (TAS 33,617); room 40
  +5 X 304, health X 384 y 80, +10 X 512 (cost 1), **InvFW X 560 y 160 (TRAP, on the line)**.
* **6-2 exit target: J&S + >= 10** (the record: J&S/10; 6-3 then needs its own spins + exactly 5 at its exit). With 20 at room
  37 and the TAS-line lanterns (+10, +10) there is room for ~6 spins in rooms 37-40 (the TAS used 2 Windmill throws there).
* HP: the TAS takes 16 -> 15 (32,560, room 36; also on our head start), 15 -> 14 (33,699, room 39), 14 -> 12 (34,200, room 40);
  6-3 and 6-4a refill nothing until 6-4a (boss stages refill). 15 at room 37 is plenty.

### Head start (verified)

* **`work/l61p/pre61_32595.txt` = 2,533 stage rows from the 6-1 control row (row 1 = Left on F = TAS 30,063) to TAS 32,595
  (room 37, the row before its first input).** Legalized TAS rows (1-f A/B held 2 f) + the J&S line in room 36 (no 32,483 B)
  + the free lanterns +10 X 1,024 and +5 X 240.
  * 6-2 control on row 1,576 (F + 1,575 = TAS); **room 37 on row 2,511 (F + 2,510 = TAS 32,573)**; hp 15, **np 20, J&S**.
  * Positions = TAS on every frame except the X-1,024 jump (30,685-30,732) and the 1-px stretch 32,507-32,559.
  * **NesHawk = Mesen on all 2,532 frames** (`nhpre61.py` / `mpre61.py`), at c 84 and at the six spot-check c values.
  * `check_inputs.py --period 5 --hold 2 --release 2 --windows 600:109,1800:246`: PASS (alone; re-judge on the chain, the windows
    cross the 5-4 boundary). `legal_ok` with the TAS's previous rows: ok.
  * **Arrival: NOT independent.** TAS-equivalent on NesHawk for 13 of 61 real Start delays from the TAS kill (above); Mesen `$BF`
    pokes: 136/256. Realistic slot leftovers (5-4 kills delayed 2 / 5 / 11 f) alone change nothing (Mesen); `$3E` does. Fully
    random junk in `$400-$4A7` wrecks it (not a realistic arrival). **Check on the real 5-4 state with `nh_late.py` before grafting.**
* Variant `work/l61p/pre61js_32595.txt` (+ 6-1 J&S and spin, fixes the 6-1 thrower): fails in room 36 on NesHawk (above).
* Room-37 pieces (from TAS states, not chained): `r37_top_32763.txt` (166 rows from TAS 32,596, pillar top on 32,763 = +60),
  room 38 cycle (above), room 39 entry cycle, `r40_plat_33863.txt`.

### Next steps for the 6-1 / 6-2 builders (by value)

1. **Arrival first.** When 5-4 is locked, save a NesHawk state on its kill row and run `nh_late.py` (k 0-40) with
   `pre61_32595.txt`; Start on kill + 595 + k for the smallest good k and graft the head start (room 37 at F + 2,510). If no k <= ~15
   is good, the cheaper fix may be the 6-1 J&S variant with a room-36 repair (6-1 then passes for ~29/31 k).
2. Room 37 (record +102): graft `r37_top_32763.txt`, then repair the run to the exit (lag ~58; soldiers at TAS 32,931 / 32,963,
   the y-160 platform and the y-128 ledge; `r4_62_h2`'s hand line is the model). Target room 38 <= TAS +80.
3. Room 38: the 6-f cycle (+16). Room 39: entry cycle (+23), then the run (the TAS's rows; its Windmill throw 33,319 becomes a
   spin or nothing). Room 40: the entry cycle (+15), the platform line (+2), a short repair for the bird at 33,928, the run.
4. Ninpo: arrive in 6-3 with J&S + >= 10; never touch the room-37 Star/Windmill/FW or the room-40 InvFW.
