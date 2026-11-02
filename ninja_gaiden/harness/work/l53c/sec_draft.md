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
