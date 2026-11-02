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
