
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
