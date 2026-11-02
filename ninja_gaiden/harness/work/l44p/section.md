## Next: 4-4 plan (prep agent l44p, 2026-10-26)

Kelbeross (two dogs) with J&S + exactly 5 ninpo: **ONE spin, kill on stage row 24 (control + 23) = TAS = the floor;
4-4 = 772 rows (control row -> 5-1 control row), record -14.3; the fight does not depend on the arrival; only `$62` at
the 4-3 trigger (the timer tick) can cost 1-3 f.** Tools/states `work/l44p/`: `lib.py`, `mkst.py` (Mesen TAS states
`states/mesen/l44p_tas21352.mst` = pre-control, `l44p_tas21353.mst`; 0 RAM diffs vs the NesHawk dump), `tr.py` (trace),
`grid.py` (kill grid), `bfscan.py` (`$BF` / `$62` / hp pokes), `run.py`, `nh44.py` (NesHawk from `ref4751/10_4-3_control`
+ TAS rows to 21,352, pokes, Start / Right tests), **`graft.py` (graft onto a 4-3 candidate)**, templates `k44_*.txt`.
Frames = power-on rows (NesHawk frame k after row k); 4-4 stage row 1 = the control row.

### Splits

| | control row | kill (boss HP `$66` 0) | earliest Start | 5-1 load (`$6D` 12) | 5-1 control (first row Right moves Ryu, = first `$62` change) | 4-4 |
|---|---|---|---|---|---|---|
| TAS | 21,353 | 21,376 (row 24), timer 149 | 21,971 (21,970 is just as good) | 21,973 | 22,125 | **772** |
| record | | | | | | 785.3 (video, timer-start convention; TAS = 771 in it) = **TAS +14.3** |
| `logs/a34/4-4_p2` (round 1, from the TAS state) | | 21,376 | | 21,973 | 22,125 | 772 = TAS (old "-14 vs record") |
| ours: `work/l44p/k44_d0.txt` | C | C + 23 | C + 617 | C + 620 | **C + 772** | **772 = record -14.3** |

* Record pace: **5-1 control <= 4-4 control + 786**. Old `logs/a34/4-4_p1` (json "load 21,896") is junk: judge FAIL and
  its rows do not even kill on Mesen.
* The old note "4-4: do nothing after the kill" is right in effect: after the kill only the Start row matters (the tally
  and the cutscene ignore everything else; the TAS's post-kill L+R / U+D dance changes nothing).

### The fight (Mesen, NesHawk-confirmed)

* Two dogs (type 27), slot 7 at x 62 y 160 (on its pedestal), slot 6 at x 176 y 160; they appear on row 2 and **do not
  move before row 24**. Boss HP `$66` = 16, shared. Ryu x 32 y 208 at control (fixed by the stage load).
* J&S spin (`spin_hit`): -(XR+8) < ex - rx < XR+12 and ry - ey <= 24 -> Ryu's feet must be at y <= 184, i.e. 7 rows
  after the jump press (y 208, 204, ..., 185, 182). The spin then hits **1 HP per frame** -> kill = first hit + 15 =
  **jump row + 22**. Only dog 7 is in reach (dog 6 is 114 px away), so 1 HP/frame is the maximum.
* **A on the control row does NOT jump** (Mesen and NesHawk: A+Left / A on row 1 -> no jump, and holding it on row 2
  gives no jump either; it needs a fresh press on row >= 2). So the earliest jump is row 2 and **the kill floor is row
  24 (control + 23)**. Grid (`grid.py`, 1,152 legal candidates: control-row input x jump row 1-4 x A hold 2/6 x air
  direction x B row x B direction, Enforcer-legalized): best kill row 24 (56 candidates), none earlier. B on any row 3-8
  gives row 24; the B direction does not matter.
* Rows (`k44_d0.txt`): `Left` (control row), `A+Left`, `A+Left`, `-`, `B+Right`, `B+Right`, blank ..., `Start` x2 on
  rows 618-619, blank to row 772. Legal (= `4-4_p2`'s pattern, which passed the judge). Ryu ends standing in the spin
  at y 160; no hit is taken (works with hp 1).
* Ninpo: **+10 = same kill, +15 f at the tally** (a 2nd B during the spin spends nothing: np 10 -> 5 stays; the extra 5
  can only be burned in 4-3). **+0 = sword only: best found kill 21,464 = control + 111 = +88 f** (`ng.solve.boss` with
  `$64` poked 0, NesHawk, 0.4 h, width 4: `states/tmp/a56r2_tk_4-4_np0.inputs.txt`; not a proven floor). So a missing 5
  costs ~88 f, an extra 5 costs 15 f.

### Arrival dependence (Mesen `bfscan.py`, NesHawk spot checks)

* **`$BF`: none.** p2-pattern rows with `$BF` poked to every value 0-255 at the pre-control row: all 256 give kill row
  24, timer 149, load row 621, 5-1 control row 773. NesHawk with `$BF` 130 / 7 / 250 / 66: same rows.
* **HP: none** (hp 1 / 2 / 5 / 16 identical). Ryu's x/facing at control are fixed by the stage load (l43p: Left held
  before the control row changes nothing). Ninpo: see above. Score: irrelevant.
* `$BF` at the 5-1 control row = (`$BF` on the 4-4 pre-control row + 3 + extra rows) mod 256 (two frames of the
  transition do not count). `$62` through the act-end transition = (v - 24 - d) mod 61 (frozen one row after the kill, d = jump delay; TAS 59), and 5-1 counts down from it.

### Timer tick: what 4-3's exit frame should catch

* v = **`$62` on the 4-4 control row = its value on the 4-3 trigger frame** (`$62` stops on the frame before the trigger
  and is frozen through the 279-row transition; TAS: 22). In 4-4 it decrements from row 2; the timer ticks (`$63` 150 ->
  149) on row v + 2. The tally reads the timer **one row after the kill** (the row after the kill still ticks), so the
  kill on row 24 collects the tick when **v <= 23**.
* Measured (Mesen run_batch = NesHawk; `graft.py --test`, NesHawk `nh44.py`): 4-4 rows (5-1 control row - 1)

| v | best rows | 4-4 | template |
|---|---|---|---|
| 0-23 | jump row 2 (kill row 24, timer 149) | **772** | `k44_d0.txt` |
| 24 | jump 1 row later (blank on row 2; kill row 25 on the tick) | 773 | `k44_d1.txt` |
| 25 | jump 2 rows later (kill row 26) | 774 | `k44_d2.txt` |
| 26-60 | jump row 2, timer 150 | 775 | `k44_t150.txt` |

* **For 4-3: compare exits by trigger + min(3, max(0, v - 23)).** Each frame 4-3 saves raises v by 1, so a gain that
  pushes v from <= 23 into 24..26 is worth nothing (and 1-2 f slower exits that bring v from 24-26 down to 23 are free).
  On k932b: v = (`$62` at the trigger), read it with Mesen (`$62` = 0x62) on the trigger frame.

### Transitions

* **4-3 -> 4-4:** control = trigger + 279 (NesHawk, l43p); Start does nothing; nothing moves Ryu before the control row;
  the 4-3 file ends at the trigger, rows trigger+1 .. trigger+278 blank, 4-4 row 1 = Left on trigger + 279.
* **4-4 -> 5-1 (act-end cutscene):** earliest Start = **kill + 147 + 3 x timer** (= kill + 594 with timer 149; a press
  one row later gives the same load; one row earlier is ignored, and a Start held across that row blocks the next
  frame's press: it must be a fresh press). Load = kill + 150 + 3 x timer (NesHawk). 5-1 control = kill + 302 + 3 x timer (kill +
  749), measured on NesHawk with kills on rows 24-27 (no phase dependence). **Mesen's `step()` accepts the Start 1 row
  earlier and loads 2 rows earlier than NesHawk; Mesen `run_batch` matches NesHawk: use run_batch or NesHawk here.**
* **5-1 control row:** first row on which Right moves Ryu (x 64 -> 65) = first `$62` change; **Right held from 22,100
  (or any earlier row) moves him on the same row: no free frames.** The 4-4 stage file ends one row before it; 5-1's
  row 1 = Right.

### Graft onto a 4-3 candidate (ready)

`python work/l44p/graft.py <4-3 power-on rows> <Mesen state on its path> <state frame> <tag>`: plays to the trigger,
keeps the rows to the trigger, blanks to trigger + 278, reads v, picks the template, checks kill / 5-1 control with
run_batch, writes `logs/l44p_<tag>.inputs.txt` (4-4 stage rows) + `logs/l44p_<tag>_poweron.inputs.txt`, runs the judge.
Tested on the TAS path (trigger 21,074 -> control 21,353, v 22, kill row 24, 5-1 control 22,125). Then confirm on NesHawk
(`python -m ng.solve.verify chain ...`). No 4-3 candidate reached the trigger yet (2026-10-26 04:20), so nothing grafted.

