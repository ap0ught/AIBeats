
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
