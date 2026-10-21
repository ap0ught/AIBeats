# Track TOWER1: the first 5,000 frames of the tower (Level 12, The Revolution)

Started 2026-10-10. Written as the work goes. All commands from `../toads`, `TOADS_CORE` unset.
Frame index `k` = inputs since bookmark `A11r_end0` (the A12r / A12x index). TAS row `r` = frame of the 1-player TAS
relative to its placement in Level 12 (`logs/fix/tas_l12.ram` row r + 33, events in `logs/fix/tas_l12_events.txt`).
Owned files: `tw1_*.py`, `tw1_bridge.lua`, `tw1_hook_fceux.lua`, `logs/fix/tw1_*`, `logs/pbeam_T12*.json`, bookmarks
`states/tw1_*`, `states/T12*`. Nothing here writes memory in a run (pokes only in `tw1_*` probes on snapshots).

## 1. The green ledges after wind face 1: the claim checked (it is a frame counter, but the numbers were wrong)

The six green ledges (object 0x34) between the H-3902 floor and the H-4382 ring are SOLID ON A WINDOW OF THE LEVEL'S
FRAME COUNTER `$0B`, period 256. Each ledge: appears (8 frames), is shown 118 frames, blinks 37 frames, is gone 93.
Measured by standing next to them for 560 frames (`tw1_ledge2.py`, sprite byte `$3D0+slot`: 101 shown, 0 hidden, 102
appearing; `logs/fix/tw1_ledge2.json`) and by landing tests (`tw1_ledge1.py`):

| ledge (x, H) | solid for `$0B` in |
|---|---|
| L1 (304, 3968) | 153 .. 52 (through 255/0) |
| L2 (304, 4024) | 21 .. 176 |
| (H 4094: a fixed ledge, always there) | |
| L3 (256, 4144) | 153 .. 52 |
| L4 (256, 4208) | 161 .. 60 |
| L5 (256, 4272) | 169 .. 68 |
| L6 (256, 4336) | 105 .. 4 |

The ledge objects themselves are spawned by the CAMERA (L3 when the camera reaches 1928 etc.), only their in/out phase
is the counter. Nothing else there is counter-bound: the circling spring 0x36 at H 4407 in front of face 2 is spawned
by the camera at x ~6 (in the TAS it is at x 8 with `$0B` = 18, in our run at x 6 with `$0B` = 230; the old note
"x = 2*$0B + 58" was a coincidence of one run).

Hop times (TAS rhythm): floor -> L1 21-22 frames, L1 -> L2 15, L2 -> 4094 16, 4094 -> L3 15 (instant sprint Left),
L3 -> L4 18, L4 -> L5 18, L5 -> L6 18, L6 -> ring 8. So with `a` = `$0B` when L1 is landed on and `b` when L3 is:
- lower half passable for L2 landing c in [21,67] (L1 landed at c-15 or earlier, it stays until 52) or c in [168,176];
- upper half passable for b in [153, 206] (L6 must still be there at b+54 <= 260); ring landing at b+62.

A12r lands on the H-3902 floor at `$0B` = 14 (k 4986), L1 at 35, L2 at 55, stands on 4094 from 71 and waits 66
frames for L3 (landing 157, 4 frames later than possible), ring at 219 (k 5191).
With G = frames gained before that floor (i.e. before wind face 1: the face cycle is fixed, spawn + 479 = floor):

| G (frames gained before face 1) | what happens | net gain at the H-4382 ring |
|---|---|---|
| 0 .. 130 | same cycle, longer wait at 4094 | 0 (4 if the L3 landing is tightened) |
| **131 .. 238** | L1/L2 at 154/169 of the previous cycle, no wait at 4094 (the TAS's own line) | **213** (207 at G = 131) |
| **239 .. 386** | previous cycle, the line we have now | **256-260** |
| 387 .. 494 | two cycles back, TAS line | 469 |
| 495 .. 642 | two cycles back, our line | 512-516 |
| 643 .. | three cycles back | 725 |

So the threshold is 131 (not 189) for 213 frames, 239 for 256. The 1-player TAS waits 24 frames on the floor for the
same reason (it arrives at `$0B` 108, L1 is out until 153).

## 2. Mechanics found on the way (all measured, frame numbers are TAS rows unless marked k)

- **Static springs of the staircase** (0x36 at (112,816), (48,880), (496,944), (432,1008), (368,1072), (432,1136),
  (496,1200)): landing on one starts a fixed 22-frame sink-and-throw; the TAS lands on the right edge (x = spring+15),
  walks to the left edge during the sink (Left on alternate frames), holds A from the bottom and Left+A on the launch
  frame (instant sprint), flies 11 frames to the next one: 34 frames a spring. A fresh A at landing only sinks it deeper
  (-30) and throws no earlier; apex +87, not enough to skip a spring. A12r needed 40-80 frames a spring.
- **The TAS's inputs between its Left+Right frames ARE legal and replay** from a state of ours that matches its row
  within a pixel: `tw1_follow.py` (section 3). Banned TAS frames before face 1: 857 (L+R+A dash), 1667 (same), 2282-2293
  (L+R standing), 2529 (dash), 2759-2764, 2884/2886 (Up+Down). None from 2887 to 4622.
- **Legal replacement for the L+R dash jump out of a boot's recovery** (toad faces the wrong way): nothing beats
  "wait, tap the direction, one frame nothing, direction+A" with the tap 5 (first time) to 7 frames after the toad is
  free again: airborne at sprint speed 25 frames after the landing at row 838 (TAS 19) and 27 after the one at 1648
  (TAS 19). Breadth-first search over 6 buttons x 16 frames, `tw1_bfs.py`; so each such dash costs 6-8 frames.
- **Hits are only tested on every other tick of `$0B`** (`tw1` probe with a debug poke on a snapshot: the same kick at
  the same positions connects with `$0B` one less or one more, and passes through otherwise). To copy a TAS hit our
  `$0B` must have the TAS's parity: an odd number of frames lost before a fight has to be made even.
- **The TAS's camera leads ours for good.** Camera code (bank 2 `$F697-$F7F0`, found with a write hook in FCEUX,
  `tw1_hook_fceux.lua`): it scrolls up by 1/2/3/4 px a frame when the toad's SCREEN height `$493` (minus ~6) is under
  0x70/0x50/0x40/0x20, nothing else. The TAS's Left+Right frames move the toad's depth byte `$41B` (216 -> 215 at row
  857 -> 214 at 1667 ...), which puts it higher on the screen, so its camera starts earlier: ours sits 1 px behind
  from row 1040 on and every camera-spawned enemy comes in 1 frame later for us (Hornheads at rows 1511, 2097).
  This cannot be copied legally; fights after a late spawn need their own timing.
- **Enemy AI is clocked by `$0B` modulo 8.** A Hornhead that walks in (the one at camera 3911) polls "turn toward the
  toad" only on one residue of the frame counter: with our `$0B` minus the reference run's ≡ 0 (mod 8) the old inputs
  replay with ONE Select; with ≡ 4 no Select pattern in 870 tries reproduces even its first step (debug-poke probe on
  a snapshot: differences of 8, 16, 32, 64 give the old track, 4 / 12 / 100 do not). So when old (A12r) or TAS inputs
  are replayed behind a change, the number of frames gained before each fight must be a multiple of 8 relative to
  that reference (pad with idle frames where the toad stands); parity (hits every other tick) is the weak form of it.
- **Sub-pixels decide hits.** The toad's height sub-pixel `$466` differs after a different landing; a jump kick that
  connected by 1 px in the old run (cam-4096 Hornhead, second kick, old row 2561) then misses its frame and lands 2
  frames later with the toad 5 px further on. An exact x also matters: 2 px too far right and the first kick misses.
- **Joining the old run again** needs: same x, height, speed, facing, camera (the camera stops where the toad's
  screen height reaches 0x76, so it is history-dependent: stand 9 frames after the walker before the old jump),
  `$0B` ≡ old (mod 8). Tools: `tw1_join.py`, `tw1_xfix.py` (1-2 input replacements), `tw1_rejoin_g.py` (air
  steering), then `tw1_dice.py` (Select re-rolls against the old run's per-frame track, 1 px toad tolerance).

## 3. Tools (all `tw1_*.py`, nothing else edited)

| tool | use |
|---|---|
| `tw1_lib.py` | helpers; pieces are `logs/fix/tw1_<name>.json` = {base bookmark, base_k, inputs since it, rn} |
| `tw1_probe.py A12r a` | per-frame RAM of A12r -> `logs/fix/tw1_a.ram`, bookmarks `tw1_a_f<k>` every 250 |
| `tw1_follow.py <start> <r0> <r1> <out>` | follow the TAS (default) or the old run (`TW1_REF=old`) frame by frame with repairs (replace / insert / skip an input, Select re-rolls, waits); `TW1_EDITS`, `TW1_TRACE`, `TW1_XT/HT/ET`, `TW1_SPAWN_LAG` |
| `tw1_bfs.py`, `tw1_dash2.py` | fastest legal dash jump out of a recovery (replacement for the TAS's Left+Right dash) |
| `tw1_append.py`, `tw1_seq.py` | append explicit / old / TAS inputs to a piece open-loop and list the events |
| `tw1_var.py` | old inputs with replacements: events against the old run's |
| `tw1_join.py`, `tw1_xfix.py`, `tw1_rejoin_g.py` | put the toad back on the old run's exact state |
| `tw1_dice.py <piece> <tail W> <old row> <out>` | Select re-rolls so the old inputs replay to that row (like rngfit, tolerances explicit, presses allowed on the prefix's last W frames) |
| `tw1_ledge1.py`, `tw1_ledge2.py` | the green ledges' timing (section 1) |
| `tw1_exit.py` | from face 1's pole straight onto ledge L1 (one jump out of the sprint): L1 at k 4985 against 5007 |
| `tw1_bridge.lua`, `tw1_hook_fceux.lua` | probe only: write hook (works in FCEUX, not in QuickNES) that found the camera code |

## 4. What the frame counter `$0B` does to a re-used input list (the reason "gain N frames and replay the rest" fails)

Measured with debug pokes on snapshots (`$0B` and its mirror `$CD` moved, everything else left) and with real runs:

| what | depends on | evidence |
|---|---|---|
| hit tests (toad's blow against an enemy) | `$0B` mod 2 | kick at the cam-4713 Hornhead connects with `$0B` -1 or +1, not with the value itself |
| a walking Hornhead's "turn to the toad" | `$0B` mod 8 | cam-3911 Hornhead: old track with a difference of 8/16/32/64, not with 4/12/100 |
| the big walker's change of flight mode (state 1 -> 2) | `$0B` mod 16 | old row 3507 (`$0B` = 81); with a difference of 104 it comes 8 frames later |
| the big walker's START after its rise | dice, per frame | random row 3458..3500+, the old run has the first possible frame (about 1 try in 80) |
| the toad's height sub-pixel `$466` | counts -79 a frame while it stands or walks, set at each landing | a jump started 8 frames "later in the cycle" rises 1 px differently and lands a frame off on a spring |
| the green ledges, some other 0x34 ledges | `$0B` mod 256 | section 1 |
| the toad's x sub-pixel `$448` | history (every frame at a fractional speed) | 0.7 px more on the face-2 pole = the spring's edge missed by 1 px at old row 5872 |

Consequence: the old inputs (A12r) only replay behind a change when the change leaves `$0B` exactly as it was
(a gain of a multiple of 256 TICKS - hit freezes do not tick) AND the toad is put back on the old run's x, x sub-pixel,
height sub-pixel, speed, facing and camera at the join. Then only the dice differ and Select re-rolls do the rest
(`tw1_dice2.py`: 1 Select for the cam-3911 Hornhead, 1 for the big walker's start, as in the A12r refit).
Behind any other gain every fight and every edge-of-platform landing has to be found again.

## 5. Route A (BANKED in up17t): one cycle of the frame counter, the rest of the level in the old phase

Result: `python assemble.py up17t L1b L3u L3skipu L4c5 L6c A8r2 A9r A10r A11r T12x L13_L12h_k0`
-> `up17t: RUN TIME 12:05.59 = 43607 frames (landing 2074 -> cut to Professor T. Bird 45681)`, replay MATCH sha1
10722e85 (two replays from power-on), UNDER the record by 23.66 s. up16ar2 was cut 45936: 255 frames (4.24 s) faster.
Tower segment `T12x` = 8,154 inputs against A12x's 8,409. Log `logs/fix/tw1_assemble.txt`, scan of the input file
`logs/fix/tw1_scan_up17t.txt` (0 Left+Right, 0 Up+Down, 0 Start in the tower, controller 2 never driven).

The build (pieces `logs/fix/tw1_<name>.json`, base bookmark `tw1_a_f750`, k = inputs since `A11r_end0`):

| piece | what | ends at |
|---|---|---|
| `st2` | A12r[750:868], then the TAS's staircase and cam-4713 Hornhead (rows 858..1659; 2 inputs replaced, 2 idle frames inserted for the legal versions of its banned frames) | k 1673 |
| `e2k` | `st2` cut at k 1538; cam-4458 Hornhead with a GROUND kick first (750 points, not the TAS's 1000-point flying kick) and the big boot (5000): free at k 1690, x 139, score 254050 | k 1690 |
| `e2d` | legal dash to the spring (12 idle, Right, -, -, Right x9, -, Right+A): airborne at k 1716 = TAS row 1667 | k 1716 |
| `e3n` | TAS-follow to row 2002 (walker dead; Selects on TAS rows 1854, 1892): x 114, H 1822 | k 2051 |
| `n1` | 13 idle frames (camera) + A12r[2408:2640]: the cam-4096 Hornhead dies on old row 2619, toad lands at x 291 | k 2296 = old row 2640, 344 ahead |
| `n2` | `tw1_joinA4.py n1 n2`: 88 frames given back on the H-1822 ledge (two hops of 8 and 10 frames with air drift for the height sub-pixel, then the old run's own run-up) so that after old input 2679 the toad has the old x, x sub-pixel, height sub-pixel, speed, facing and `$0B` | k 2424 = old row 2680, exactly 256 ahead |
| `n3` | `TW1_DRAND=1500 TW1_DEND=1 python tw1_dice2.py n2 30 8407 n3`: the old inputs 2680..8407 with 3 Selects (on old rows 2815, 3455, 3619: cam-3911 Hornhead, big walker's start, its flight) and one lag frame more | level 13 at k 8153, lives 4, score 284550 |

`logs/pbeam_T12a.json` = A12r[:750] + the chain (8,153 inputs). `python u16a_syncnext.py T12a L13_L12h_k0 T12x 300 400 16`
adds one Select on index 7951 -> `logs/pbeam_T12x.json` (8,154 inputs), entry RAM differs from the old entry only in
`$0C`, and `L13_L12h_k0` replays unchanged (2,029 frames, 0 RAM differences from frame 16, level byte 13 -> 254 on the
old frames). Three of 300 single-Select variants sync (7951, 7927, 7926).

Two things that cost a rebuild, so nobody repeats them:
- SCORE. The Queen segment only syncs when the score digits equal the old run's (syncnext compares all RAM). A hit
  is worth 1000 as a flying kick (anim 35), 750 as a ground or jump kick (38/39), 5000 as the big boot (30), 2000 as
  a ram (49). The first full build ended on 284800 instead of 284550 because one Hornhead's first hit was the TAS's
  flying kick; the fix was a ground kick there (`tw1_e2b.py`).
- X SUB-PIXEL. An approximate rejoin (right pixel, wrong `$448`) replays 3,200 frames and then misses a spring's edge
  by 1 px at old row 5872. The rejoin has to be exact in `$448` and `$466`, not only in x and H.

## 6. What was found, what was banked, what blocks the rest

Frames found legally before the green ledges (against A12r, measured):

| where | frames | status |
|---|---|---|
| static-spring staircase + cam-4713 Hornhead (TAS line, legal repairs) | 333 | in up17t |
| cam-4458 Hornhead + dash to the spring + walker (TAS line; the legal dash costs 6-8) | about +50: 383 ahead when the walker is dead (TAS row 2002 at k 2024, old row 2408) | first chain only (score 250 too high) |
| the same with the ground kick the score needs | about +24: 357 ahead (TAS row 2002 at k 2051) | in up17t |
| after the cam-4096 Hornhead (shorter post-kill path) | +35 (G = 410 shown) | probe only |
| face-1 pole straight onto ledge L1 (`tw1_exit.py`) | +22 (L1 at k 4985 against 5007) | probe only |

Banked: 256 ticks of `$0B` (344 frames in hand at old row 2640, 88 of them stood off again). The surplus cannot be
kept, because behind a gain that is not a multiple of 256 ticks none of the old inputs replay (section 4).

Tiers (G = frames ahead of A12r at the face-1 pole, tail rebuilt at the new phase): 0..130 -> 0, 131..238 -> 213,
239..386 -> 256-260, 387..494 -> 469, 495..642 -> 512-516, 643+ -> 725. With the old tail replayed unchanged
(exact phase) only 256 (surplus 244..290 at the join) and 512 (surplus >= 500 at the L2 landing) exist.

NOT done, and why:
- 469 (213 more): needs G >= 387 at the pole AND every fight and edge landing from old row 2680 to the level's end
  found again at a phase 213 off (hit parity, Hornhead mod 8, big walker mod 16 + a 1-in-80 start roll, sub-pixels,
  the blinking ledges themselves). G = 410 was reached in a probe before the cam-3911 Hornhead; the tail behind it
  was not rebuilt (the dice search could not hold the old track there: that is how the mod-8 / mod-16 clocks were found).
- 512 exact: needs 500 at the L2 landing; the known items add up to about 344 + 35 + 22 = 401, the missing 100 would
  have to come from the big walker (TAS about +74), the cam-3911 Hornhead (+30) and the climb (+12), all fought at
  non-old phases first. Not attempted.
- The TAS's own line cannot be copied past row 2282: its Left+Right frames shift the toad's depth `$41B`
  (216 -> 199), its camera leads ours and its enemies spawn a frame earlier than any legal input gives.

Left on disk besides the route: helper segments `logs/pbeam_T12o2089.json`, `logs/pbeam_T12fA_partial.json`, bookmarks
`states/T12fA_stuck`, `states/tw1_*`, intermediate pieces and logs under `logs/fix/tw1_*`. Debug pokes were used only
in throwaway probes on snapshots (sections 1 and 4), never in a piece.
