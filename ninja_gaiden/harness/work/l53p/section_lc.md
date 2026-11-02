## Next: 5-3 plan (prep agent l53p, 2026-10-27)

5-3 = rooms 27 (runs LEFT), 28 (right), 29 (left), 30 (right), 31 (left), 32 (right), 33 (short run right into 5-4).
**Headline: 5-3 is three copies of one leftward room end and three copies of one rightward room start. The TAS's banned
inputs are almost all in those six places, plus one pit crossing in room 27. The leftward exits have a tested legal way
(+46 f per exit). The room-27 pit is the one open problem: the TAS's way across is provably not legal, and no legal way
has been found yet. The record crosses it, so one exists.**
Tools and data are in `work/l53p/`:
* `dumps.py` -> `tas53_ram.bin` (NesHawk TAS RAM 26,610-29,409); `lib0.py` (`TM(f)`, `XY`; falls back to the 5-1 and 5-2 dumps);
* `lib.py` (Mesen helpers, `core_at(f)`); `mkst.py` -> Mesen TAS states `states/mesen/l53p_tas<f>.mst` (65 frames
  26,607-29,099, 0 RAM diffs vs NesHawk);
* `ev.py` -> `tas53_ev.txt` (rooms, hp, ninpo, spawns); `rle.py` -> `tas53_rows_rle.txt`; `brk.py` (rule breaks as spans);
  `spins.py` (spins and kills); `slots.py`;
* `roommap.py` / `roommap0.py` (room collision maps, with / without the TAS path);
* `tf.py` (follow legal TAS rows); `b53.py` (beam); `diag.py` (one row spec, printed trace);
* `bf53.py` (thrower `$BF` scan); `spintest.py`;
* `axe31.py` / `axe31bf.py` / `axe31b.py` (room-31 axe-boost tests); `bird29.py` (written, not run);
* `pitgrid.py` (room-27 ladder test); `pre53.py` / `nhpre53.py` (head start, Mesen arrival test + NesHawk).

Frames are power-on rows on the TAS axis. **TAS 5-3 control row = 26,608** (Left; = 5-2 trigger 26,329 + 279).
**`$BF` at our 5-3 control row F = (F - 23) mod 256** (TAS: 217).

### Splits

Room change = the first frame with the new `$6E`. Record = the first picture after the 22-f black, minus 22 (`record_events.json`).
The record's control estimates are +-3 f at each end.

| room | TAS frames (room change -> room change) | record | record loses | TAS t at room end (from control) |
|---|---|---|---|---|
| 27 (left) | 405 (26,608 -> 27,013) | 514.8 | **+110** | 405 |
| 28 (right) | 472 (-> 27,485) | 512.9 | +41 | 877 |
| 29 (left) | 436 (-> 27,921) | 504.8 | **+69** | 1,313 |
| 30 (right) | 473 (-> 28,394) | 504.8 | +32 | 1,786 |
| 31 (left) | 235 (-> 28,629) | 304.5 | **+70** | 2,021 |
| 32 (right) | 215 (-> 28,844) | 234.4 | +19 | 2,236 |
| 33 + transition | 415 (-> 5-4 control 29,259) | 408.7 | -6 (timing noise; it is a plain run) | 2,651 |
| **5-3** | **2,651** | **2,985** | **+334** | |

* **Record pace: 5-4 control <= F + 2,985**, i.e. 5-3 trigger <= F + 2,826. The 5-3 -> 5-4 transition: trigger = `$5C` 2 -> 4
  when Ryu reaches X 380 in room 33 (TAS 29,100); hp refill to 16 on trigger + 7; room 34 load trigger + 8;
  **5-4 control = trigger + 159** (TAS 29,259).
* **Where the TAS gains (and the record loses):**
  * the three **leftward room exits** (rooms 27, 29 and 31 share one geometry: the wall X 96-127 with the exit tile
    'M' at X 96-111 y 64-79 on top);
  * the three **rightward room entries** (rooms 28, 30 and 32: the same entry shaft and ladder);
  * the **room-27 pit** (X 480-552). Per room, the record's losses are 110 / 69 / 70 in the leftward rooms and 41 / 32 / 19
    in the rightward rooms.

### TAS rule breaks in 5-3 (`brk.py`), split into legal and banned parts

The key code is in bank07:
* `touch_walls` $E677 returns at once when Ryu's y < 72, so no wall check, floor check or exit check runs above y 72.
* The exit check needs a touch point in an exit tile:
  * (X + 5, y - 5) or (X - 9, y - 5);
  * y >= 72.
* In the air, holding the direction he does NOT face gives 0.5 px/f (`drift_speed`).
* U+D+L (and L+R) choose `ctrl_idle`: no turn and no speed change, but `move_ryu` still steps Ryu at 1.5 px/f.
  So the TAS **moves against its facing at full speed**.
* A wall jump-off needs the pad to be exactly A+away ($81 / $82). It flips his facing away from the wall.

| TAS rows | what | banned part | legal version / verdict |
|---|---|---|---|
| 26,608-26,704 | run left, jump | 1-f A | **legal TAS rows = TAS positions exactly** (head start below) |
| 26,704-26,752 | **room-27 pit** (X 496-527 between the '1' pillar X 528-543 and the '21' block X 480-511, both without floor tops): wall jump-offs every 24 f off the pillar tops with **U+D+L for 47 f** (moves left 1.5 px/f while facing right) | U+D | **The TAS's way is not legal (shown from the code and by search).** A jump-off from a wall on his left must be A+Right, so he faces right. Moving left is then 0.5 px/f, about 10 px per bounce. The 16-px gap X 512-527 has no wall to bounce on, so drift falls into the pit. Two beams (`b_pit27.out`, `b_pit27b.out`, width 150) stall at the X-543 pillar. **Not solved:** a ladder climb of the X-672 column onto the y-112 platform (X 448-639) was tried. `pitgrid.py` ran 576 walk/jump/climb variants and beam `plat27` ran 120 f; neither ever rose above y 160. The record's trace is on that platform at y ~115 from ~t 141, and the record is only ~+17 here, so a legal way up exists. **First job for the 5-3 builders.** |
| 26,855 | spin (kills 3 t0) | - | needed (`spintest.py`: without it, or with a Down+B slash, hp 3 -> 2) |
| 26,937-26,966 | climb the '84' pillar's right face (X 200), U+D+L over its top (y 123-128) | U+D, 1-f | not needed on the legal exit (below) |
| 26,995-27,012 | **leftward exit**: A+Right jump-off from the X-128 wall at y 83, then **U+D+L 12 f above y 72** over the wall top into 'M' | U+D | **No legal version from the right side (proof from the code).** To reach the exit he must cross from X >= 137 to X <= 120 above y 72 (the '8' cap at X 112-127 y 64-79 and the '1' below block Left at every y 72-192). The tools: a normal jump from the nearest floor (the y-128 pillar top) peaks at y 80; a wall jump-off (vy -2, ~14 px) faces away, so Left is 0.5 px/f for about 12 f above y 72 (6 px). A hit while clinging is cancelled into a new cling the next frame (`axe31bf.py`: axes hit him on the face for many `$BF`; no exit). Hits in the air during the jump from the pillar top gave no exit either (`axe31b.py`, 992 BF x wait cases). **Legal exit = under the wall and up the ladder face from the left**: walk left along the floor under the wall (y 192 is open), climb the '9' ladder (X 96) with `[A+Left x2, Right x6]` cycles; the exit fires at y <= 84. **Beam `b_ex27b` (from TAS 26,900, X 254 y 208): room 28 on 27,059 = TAS +46, hp 3, np unchanged (0 spins).** Rows: `work/l53p/b_ex27b_h3n35i133.txt` |
| 27,037-27,063 (r28), 27,945-..., 28,653-... | entry ladder: taps (1-f A+L / A+R, 2 px/f) | 1-f | the 5-2 legal 5-f cycle (`cyc.py`, room-24 exit = TAS +6) or the `[A+Left x2, Right x6]` cycle; untested here |
| 27,065-27,097, 27,973-28,005, 28,681-28,713 | **rightward entry**: jump from the '84' top (y 192) with **L+R 33 f** = move right 1.5 px/f while still facing LEFT (he walked left onto the ledge; an A+Right press on the ground jumps without turning) | L+R | **legal: turn on the ground first** (Right >= 2 f, then A+Right): the same arc 1-3 f later. Untested; expect +2..+5 per room |
| 27,484, 28,393 | 1-f L+R on the exit ladder (X 667) the frame before the room change | L+R, 1-f | exit-ladder taps as above; +0..+3 |
| 27,838-27,848 (r29) | climb the col-14 wall's left face with A+Left taps + L+R | L+R, 1-f | `[A+Left x2, Right x6]` cycle; a few f |
| 28,568-28,582 (r31) | U+D+L over the '84' pillar top after the axe-boost hit at 28,564 | U+D | not needed on the legal (floor + ladder) exit |
| 28,617-28,628 (r31), 27,909-27,920 (r29) | leftward exits (same as room 27) | U+D | same verdict, same legal fix: **room 29 (beam `b_ex29` from TAS 27,800): room 30 on 27,975 = TAS +54**, hp 3, 2 spins (TAS 1); **room 31 (beam `b_ex31` from TAS 28,540): room 32 on 28,692 = TAS +63**, hp 3 (the TAS takes a hit here), 3 spins (TAS 0; the beam burns ninpo freely, so fewer should do). Rows `b_ex29_h3n10i133.txt`, `b_ex31_h3n0i133.txt` |
| ~150 rows | 1-f A/B, presses < 5 f apart | press cap | Enforcer (2-f holds) |
| - | U+D in the boss tally | - | not in 5-3 |

### Ninpo, spins, J&S (sets the 5-2 exit)

* 5-3 lanterns (ROM, 60 ninpo in total):
  * room 27: **FW X 192 y 112 (TRAP)**, +5 X 240 y 160, +10 X 320 y 80, +5 X 400 y 160;
  * room 28: +5 X 288 y 96 (TAS), +10 X 496 y 144 (TAS);
  * room 29: **InvFW X 144 y 80 (TRAP; on the TAS jump to the wall)**, +10 X 272 y 80, **Star X 496 y 160 (TRAP)**;
  * room 30: +5 X 336 y 112 (TAS), **Windmill X 464 y 96 (TRAP)**, **Star X 624 y 128 (TRAP)**;
  * room 31: +5 X 64 y 144, **FW X 240 y 80 (TRAP)**;
  * room 32: **FW X 256 y 160 (TRAP)**, **Windmill X 368 y 160 (TRAP)**, +5 X 416 y 112 (past the exit, unreachable).
* **TAS: 11 spins** (26,855 / 27,199 / 27,241 / 27,327 / 27,620 / 27,712 / 27,803 / 28,145 / 28,209 / 28,508 / 28,782). It
  picks up **+20** (27,202 / 27,340 / 28,150), so J&S/40 -> J&S/5.
  Three spins also break the lanterns (27,199, 27,327, 28,145). Every spin kills 1-4 enemies.
* `spintest.py` replaced each spin, on the TAS line, by nothing or by a plain Down+B slash. **Every one of the 11 costs a
  hit (hp -1/-2) or a death** (27,803, 28,508, 28,782 die). The test at 28,145 is inconclusive.
  So on a TAS-shaped line all 11 are needed. The legal exits change three places:
  * beam `ex27b` used 0 spins from X 254 to the exit;
  * `ex29` used 2 and `ex31` used 3, where the TAS used 1 and 0 (the beams spend freely).
  So **expect 10-12 spins**.
* Formula: **5-3 entry ninpo = 5 + 5 x spins - pickups**. With the TAS's pickups (+20) and 11 spins that is 40.
* Each extra lantern taken in 5-3 lowers the entry by its value:
  * +5 X 400 y 160 and +5 X 240 y 160 (room 27) hang 48 px over the floor the line runs on: a jump + slash costs ~0-6 f each;
  * +5 X 64 y 144 (room 31) is next to the legal ladder climb (untested).
* Each spin avoided lowers it by 5.
* **5-2 exit target: J&S + 40** (= 11 spins - 20 pickups + 5). 35 is enough if both room-27 +5s are taken; 45 gives one spare spin. Up to ~55 does no harm (burn the spare spins in the air). The best 5-1 candidate exits with 35, and the TAS's 5-2 is net 0, so **5-2 must gain +5 net**: the +10 X 352 (room 23), the +5 X 96 (room 25), or one 5-2 spin fewer.
* **Entering with too much is nearly free**: an extra air spin (any B in the air without Down) costs 0 f and burns 5. But it
  breaks lanterns in passing, so burn it away from the trap lanterns above.
* **Entering with too little** costs hits: on this line every spin's job is a kill that would otherwise cost hp. Each 5 short
  is one spin lost, i.e. roughly one hit.

### Arrival dependence (`$BF`)

* bank07 readers of `nmi_count` in level stages: only the **thrower (type 2)**. Its timer is `$BF >> 1`, re-read at every
  throw cycle. Its **axe (type 18)** takes x speed `$BF & 1` + `$BF`/256 and y frac `$BF`.
* Room 27 has no thrower. **The head start is arrival-independent** (below), except a possible slot-junk effect (see Head start).
* 5-3 throwers (TAS rows, `bf53.py`, all 256 values from a TAS state shortly before the spawn).
  Spawn `$BF` = (x + k) mod 256, where **x = (F + L) mod 256**:
  * F = our 5-3 control row;
  * L = our lag vs the TAS at that spawn;
  * the TAS has x = 240.

| thrower | TAS spawn (frame, pos, `$BF`) | k | TAS-equivalent spawn `$BF` | good x = (F + L) mod 256 | bad |
|---|---|---|---|---|---|
| room 28 #1 | 27,113, (258,144), 210 | 226 | 125-255 (131 of 256) | **155-255, 0-29** | x 30-154: an early axe hits (hp -1/-2, 11 values die) |
| room 28 #2 | 27,391, (674,176), 232 | 248 | 115-255 and most odd/even pairs below (189 of 256) | **123-255, 0-7** (+ scattered) | most x 8-122: an axe hits during the exit climb (hp -1) |
| room 31 | 28,491, (189,128) on the pillar top, 52 | 68 | 130-255 and 2, 14-15, 17, 42, 44, 47-48, 51-52, 55, 62-71 | 62-187 (+ a few) | the rest: the TAS's own axe boost (28,564) does not come. Our legal exit (floor + ladder) does not use it; re-scan with legal rows (`bf53.py F0 F1 FS --rows`) |

* The room-28 throwers are the real constraint. The two bands overlap at **x = (F + L28) mod 256 in 155-255 or 0-7**,
  ~109 of 256 values. Both spawn by scroll, so **a k-frame wait at the room-28 entry** (Ryu in the entry shaft, nothing
  spawned yet) shifts x by k at a cost of k f. That is cheaper than shifting the 5-2 exit.
* **No free frames at 5-2 -> 5-3** (5-2 prep: Left on any row from trigger + 1 to trigger + 279 gives the same control
  row; Start does nothing). The timer `$62` has no effect on the arrival. Any shift of F is a 1:1 cost.
* So **the 5-2 builders need not aim the exit for 5-3**. Fix the room-28 phase with a short wait at the room-28 entry
  once our L28 is known.

### Head start (verified)

* **`work/l53p/pre53_26704.txt` = 97 stage rows from the 5-3 control row (row 1 = Left on F).** It is the legalized TAS
  rows (1-f A held 2 f) and ends at **X 545 y 161 on F + 96** (TAS 26,704, the pillar cling before the pit), hp/np unchanged.
* = TAS positions on every frame, on Mesen (`tf.py`) and on NesHawk (`nhpre53.py`: ref4751/14_5-3_control + rows,
  0 differences in 95 frames).
* **Arrival test** (`pre53.py`, Mesen, TAS state 26,607 with pokes):
  * `$BF` 0-222, invincibility `$95` 0/33/60, hp 3-16 and ninpo 35-55: **identical positions** in all clean trials.
  * With random junk in the enemy slots `$400-$4A7`, 2 of 5 junk trials differ at 26,651, where the first t0 spawns. A junk
    field is inherited by the spawned enemy.
  * On the real chain the slots hold whatever 5-2's room 26 left. **Check the head start on the real 5-2 exit state
    (NesHawk) before trusting it.**
* Not built on our 5-1 + 5-2 states: 5-2 has only its room-23 prefix so far, so there is no real 5-3 arrival state yet.
  The rows assume Ryu at the room-27 start (x 176 y 208, fixed by the load) with J&S.
* Legality: `legal_ok` with the TAS's previous 150 rows (legalized) as history. Re-judge with our real 5-2 rows.
* Next piece (not chained): **`b_ex27b_h3n35i133.txt`** = 159 rows from TAS 26,901 (X 254 y 208): the legal room-27 exit,
  room 28 on 27,059 (TAS +46). It needs the pit solved in between.

### Expected 5-3

* Leftward exits, measured from TAS states: +46 / +54 / +63, i.e. **~+163**.
* Rightward entries and ladders: ~+5..+10 each, **~+15..+30**.
* Room-27 pit: unknown; the record pays ~+17 there.

**Total ~ TAS +200..+260 = record -75..-135** (record = TAS +334), if the pit costs about what the record pays. The pit is
the risk: until it is solved there is no legal 5-3.

### Next steps for the 5-3 builders (by value)

1. **Room-27 pit (open)**: find how to get onto the y-112 platform (X 448-639) or across the pit legally. Options:
   * a beam that allows damage boosts from the hovering t0 enemies (X 500-540, y 104-112, 26,650-26,780);
   * the X-672 column (its '9' face) climbed with a better contact X (our tests never grabbed it).
2. Leftward exits 29 / 31: graft `b_ex29` / `b_ex31` (+54 / +63 from TAS states) on the real line; cut their spins to what the enemies need.
3. Rightward entries: turn-then-jump instead of L+R; ladder climbs with the 5-2 cycle patterns.
4. Take the room-27 +5 X 400 / +5 X 240 by jump-slashes if each costs < ~6 f (each lowers the 5-2 exit target by 5).
5. Re-run `bf53.py` with our rows for the room-28 throwers; pick a room-28 entry wait to land x in 155-255 / 0-7.

