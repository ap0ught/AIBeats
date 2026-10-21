# The helicopter shaft in Terra Tubes (Level 9): 198 frames, proved from power-on

Track HELI, 2026-10-09/10. Lead from the project owner: "the helicopter part around 6:27 looks like it could cost time".
Everything below was measured on the verified route `up14` (`logs/cap14.ram`, `cap14_f<k>` bookmarks), on snapshots
(debug pokes in probes only, never in a run), on the 1-player TAS's RAM dump and on the record's video.
Scripts: `l9heli_fix_*.py`; raw output: `logs/fix/heli_*`; bookmarks `L9heli_*`.

## 0. Result

- The lead was right. up14 lets a propeller bug carry the toad down the last shaft of Terra Tubes at **one pixel per
  frame for 314 frames**. The record does not ride it: it dash-jumps under both bugs and falls.
- **New Level 9 line `logs/pbeam_L9heli_c2.json`: 9,790 inputs instead of 9,987 = 197 frames saved**, 0 banned presses,
  the same health track as up14 (nothing lost before the planned death on the last spikes), no new Select presses. With the re-fitted Levels 10 and 11 behind it the whole run is
  **198 frames shorter than up14, and Levels 12, 13 and the ending replay unchanged, bit for bit.**
- Replayed from power-on (one pass each, `l9heli_fix_verify.py`, same stepping as `assemble.py`):

| route | inputs | Queen's speech cut | cut to T. Bird | run time |
|---|---|---|---|---|
| up14, plain ending | 46,751 | 46,751 | 47,253 | 12:31.75 |
| up14e (END track's steered ending) | 47,200 | 46,751 | 47,170 | 12:30.36 |
| **new chain + plain ending** (one A press) | 46,553 | 46,553 | **47,055** | **12:28.45** |
| **new chain + `L13y0E2` unchanged** | 47,002 | 46,553 | **46,972** | **12:27.07** |
| the record (needs the cut on 47,102 or earlier) | | | 47,103 equiv. | 12:29.25 |

  RAM SHA-1 after the last input: `e2a1d2dc` (plain) and `a1b291b6` (steered) - the same values up14 and up14e end on,
  so the end state is identical to the old runs', only 198 frames sooner.
- Not done by me: `assemble.py` (it writes route files and a video I do not own). Command for the official double
  replay: `python assemble.py <new name> L1b L3u L3skipu L4c5 L6c L8c L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12g L13y0E2`
  (expected: 47,002 frames, T. Bird cut 46,972). The complete input list I replayed is
  `logs/fix/heli_route_c2E.inputs.txt` (plain-ending version: `heli_route_c2.inputs.txt`).

## 1. Where the section is and what up14 does there

Level 9 = segment `L9c`, route frame = L9c index + 17,366. Run-timer 6:27 = route frame 25,332 = L9c index 7,966:
the toad is hanging under a propeller bug, sinking.

| L9c index | route frame | frames | what happens (x, height H = `$439` + 256 x `$42A`, speed `$565`) |
|---|---|---|---|
| 7,816 - 7,835 | 25,182 - 25,201 | 20 | lands on the lower ledge (x 756, H 6534), dashes right (speed 192), jumps up |
| 7,837 - 7,855 | 25,203 - 25,221 | 19 | on the upper ledge (H 6502) shuffling at x 810-813, speed 24-60: lining up for the bug |
| 7,856 - 7,857 | 25,222 - 25,223 | 2 | dash-jump right (speed 192) into the first bug |
| **7,858 - 8,171** | **25,224 - 25,537** | **314** | **carried** (animation 36/37): H 6513 -> 6208, exactly 1 px per frame; x steered 821 -> 899 -> 864 at speeds 0-100 around the stars and spikes; nothing the toad does makes it faster |
| 8,172 - 8,197 | 25,538 - 25,563 | 26 | the bug lets go at the water (H 6207); the toad floats down to the pool floor (H 6182, x 828) |
| 8,198 - 8,255 | 25,564 - 25,621 | 58 | a hop on the spot (x 826 -> 816): the floor mine passes underneath |
| 8,256 - 8,279 | 25,622 - 25,645 | 24 | runs left on the floor to x 785 (speed 66 -> 96, the cap in this water) |
| 8,280 - 8,402 | 25,646 - 25,768 | 123 | the jump out of the pool at x 785, dash, two long water hops, corridor ledge at 8,402 |

From leaving the ledge (7,856) to standing on the pool floor (8,198): **342 frames** for 320 pixels of height.
There is no waiting on gears or enemies in it - the ride itself is the cost.

## 2. The references

**The record (jay_cee, youtube A7czTlY7OI0; run time = video time - 20.69 s; read from frame sheets, +-3 frames).**
It dash-jumps from the same ledge straight under the two bugs, is never grabbed, and free-falls the shaft: ledge at
run time 383.6 s, pool floor at 385.4 s = about 108 frames (ours 342). Its floor crossing (about 204 frames from the
floor landing to the corridor ledge) and its corridor (19.7 s to the spikes) are the same as up14's. Terra Tubes by
the first-black rule (`blackcal.py`, `logs/fix/early_black_up14.json`): record 251.74 -> 413.79 s = **162.05 s**;
up14 route frames 17,317 -> 27,284 = 9,967 frames = **165.84 s, +3.79 s (228 frames)**. The descent alone is about
235-250 frames slower than the record's; in the rest of the level up14 is slightly ahead. So the whole Level 9 deficit
was this shaft. New line: 9,770 frames = **162.57 s, +0.52 s**.

**The 1-player TAS** (`tas/watch_1p_log*.txt`, RAM dump `logs/fix/heli_tas1p_ram.txt` from `l9heli_fix_dump.lua`).
Its checkpoint 26 -> 27 stretch takes 1,448 frames against our 1,936, but not by anything we may copy: it walks on
depth `$41B` = 202 (ours 216), a walk plane it reaches with Left+Right presses (banned). On that plane neither the
bugs nor the floor mine touch it. **The 2-player TAS** drops through a water column at x 938; the legal camera stops
at 772, which keeps the toad at x <= 915 - that shortcut needs the Left+Right camera glitch too. Neither is usable.

## 3. What the game does here (found on snapshots)

- **Propeller bugs**: object 0x74, slots 4 and 6, at x 824 and 840, height 128-135 on page 25 (H 6528-6535). They
  are carriers by design: the toad is grabbed when it is within about 5-10 px in x and 16-36 px below one. Carried,
  it sinks exactly 1 px per frame and can be steered; no button lets go (B is a hanging kick); it is released only
  at the pool surface. They cannot be killed (243 attack variants tried).
- **The tunnel under them** has a ceiling at height 134 for x 819-847: no jumping over. A dash-jump at speed 192 with
  the feet at heights 118-134 crosses both grab boxes too fast to be taken.
- **The shaft**: star x 862-892 from H 6438 up, hazard x 868-893 at H 6302, spikes x 898-922 at H 6408-6420, a
  ledge x 886-904 at H 6406, the right wall's hazard at x 915. The free fall is 4 px per frame.
- **The pool**: the water surface (H 6206) resets the fall (22 floating frames to the floor, H 6182). On the floor
  the walk cap is 96 (+2 per frame), no sprint; jumps float 33-62 frames. A floor mine (0x72, slot 5) spawns with the
  camera and drifts at the toad at 0.5 px per frame; it has to be hopped. This is why both the record and we stand
  around on the floor.
- **Why a splice is hard**: the old inputs after the pool only work from the old state exactly - x and sub-pixel,
  speed, and the vertical sub-pixel `$466` (constant on this floor, changed by a table value per hop, -79 per frame
  on dry ground). Tolerance at the join: `$466` within -3..+2 of the old value. Join target T' = the old state at
  L9c index 8,279 (x 785.160, speed 96, Left held), one frame before the old jump out of the pool.
- **The bug that is no longer ridden stays in slot 4.** The two corridor mines therefore spawn in slots 7 and 9
  instead of 4 and 8, their lunge scripts run a frame or two off, and the old inputs are hit at old index 8,574 and
  8,761. (Probe: freeing slot 4 by a debug poke makes the rest of Level 9 replay with zero differences - the join
  itself is exact.) Repairs are needed at both mines.
- **Frame-counter phase**: acceleration on dry ground and the mine scripts depend on the frame counter modulo 4.
  With G = frames gained at T', s = frames lost at mine 1, w = extra wait at mine 2: the stand before mine 2 only
  reproduces if G - s = 1 (mod 4), the rest of the level if G - s - w = 0 (mod 4), and `$466` after the wait only if
  -79 w = about 0 (mod 256), i.e. **w = 13** (-3). So w is forced, and s must be G - 13 (mod 4).
- **Lag**: with one more object alive the game drops 3 frames in the corridor (old index 8,478 twice, 8,791); the old
  input is held through them.

## 4. The new line

Inputs: `logs/pbeam_L9heli_c2.json` (bookmark `L8c_end0`, 9,790 inputs; identical to `L9c` up to index 7,818 and
from old index 8,786 on). Built by `l9heli_fix_full.py c2 logs/fix/heli_rand_s160.json 1 logs/fix/heli_edits_c2_2.json - 0`.

| new index | route frame | frames | what happens |
|---|---|---|---|
| 7,819 - 7,835 | 25,185 - 25,201 | 17 | as before: dash along the lower ledge, jump to the upper ledge (x 806, H 6502) |
| 7,836 - 7,849 | 25,202 - 25,215 | 14 | **dash-jump Right+A x9, Right x5** at speed 192: x 809 -> 848 with the feet at H 6508-6534, under both bugs, not grabbed |
| 7,850 - 7,930 | 25,216 - 25,296 | 81 | **free fall**, steered left of the star (x 859-864), right past the spikes (to x 898), back left: H 6525 -> 6210 |
| 7,931 - 7,952 | 25,297 - 25,318 | 22 | the water surface; floats to the floor |
| 7,953 - 7,993 | 25,319 - 25,359 | 41 | on the pool floor (x 836 -> 817): lets the floor mine come |
| 7,994 - 8,046 | 25,360 - 25,412 | 53 | one hop under the shaft (Right+A x2) over the mine; it also sets `$466` to 119 (old 118) |
| 8,047 - 8,069 | 25,413 - 25,435 | 23 | runs left to x 785.160, speed 96 = **T', 210 frames early** (old index 8,279) |
| 8,070 on | | | the old inputs 8,280... (toad's track identical to up14's) |

Ledge to pool floor: 118 frames (up14 342, the record about 108).

After T':
- **Mine 1** (old inputs 8,520-8,581, 62 frames) replaced by 59: `Left x2, nothing x4, Left+A x22, Right+A x2,
  Right x20, Left, Right, nothing, Right x6` - the old hop's height track with other steering, back on the old
  take-off state exactly (`l9heli_fix_mine.py`, `logs/fix/heli_mine_c2.json`). **+3 -> 213.**
- **Mine 2**: 13 more idle frames in the stand at x 880 before the dash-jump (old index 8,746). **-13 -> 200.**
- 3 lag frames. **-3 -> 197.** The tank at the end needs no re-roll; the death on the last spikes and the level
  change come at the same old indices. Level byte leaves 11 on route frame 27,108 (up14: 27,305).

Proof: (1) built on `cap14_f25000` with the old inputs replayed and compared byte for byte up to the branch; (2) at
T' the toad equals the old run's; (3) to the level end the toad's x, health and level byte equal the old run's at
the same old index (height differs by 1 px in places, harmless); (4) the Level 10 entry RAM equals the old run's in
all 2,048 bytes; (5) the power-on replays in section 0.

Other joins found (all verified 150 frames past T'; `logs/fix/heli_rand_*.json`): 220, 217, 212, 211, 210, 207...
frames early. The 220 and 217 ones need other mine-1 repairs because of the phase rule (found: +11 and +4 frames) and
come to at most 196 and 200 before their lag frames (the 217 one drops at least 7) - no better than this one.

## 5. Downstream cost: measured, and it is zero behind Level 11

Any change re-rolls the dice of the later levels (journal 014). Measured for this line:

| level | tool | result |
|---|---|---|
| 10 Rat Race | `rngfit.py L10t L9heli_c2_end0 L9heli_c2L10` | 1,944 frames (1,945), 0 re-rolls. The entry RAM is identical, the dice part company 14 frames later, but the Rat Race track does not depend on them |
| 11 Clinger-Winger | `rngfit.py L11r L9heli_c2L10_end0 L9heli_c2L11` | 6,879 frames (same), 3 Select re-rolls, all in the Buzzball fight |
| 12 The Revolution | - | plain re-fit: 7 re-rolls and **+17 frames** (lag). Avoided: see below |
| 13 the Queen, ending | - | unchanged |

**The trick that makes Levels 12-13 free** (`l9heli_fix_entry2.py`): after a re-fit the next level's entry RAM equals
the old run's, but its dice still drift when the CPU time left in the first frames differs. One extra Select on a
quiet frame of Level 11's tail changes that. As fitted, the dice parted 2 frames into Level 12. Scanning one Select on
every frame 6,420-6,872 of the new Level 11: 26 frames (all between 6,428 and 6,553, after the Buzzball is dead) give a
Level 12 whose first 120 frames are bit-identical to up14's (whole RAM, stack excluded). Used:
**Select on frame 6,428 -> `logs/pbeam_L9heli_c2L11s.json`**. Behind it `L12g`, `L13y0` and the steered ending
`L13y0E2` replay unchanged, proved by the end-state SHA-1s in section 0.

So: **nothing has to be re-solved - not the tower, not the Queen, not the ending.** Work the other tracks do on
Levels 12/13 and the ending from the old states (`L11r_end0`, `L12g_end0`, up14's frames) stays valid behind this
chain as it is. What does have to be redone if someone changes Levels 1-8: the usual chain (`rngfit` of this Level 9,
Level 10, Level 11, then the entry scan again) - minutes, not hours; this Level 9 has the same six Select presses as
`L9c` and no new dice-dependent spots (the tank passed without a re-roll).

A first, slower chain is kept as a fallback (mine 1 repaired with +17 instead of -3): `pbeam_L9heli_s160_1` (9,810),
`L9heli_L10`, `L9heli_L11`, `L9heli_L12`, `L9heli_L13` = 177 frames, also verified from power-on (T. Bird cut 47,076
plain, 46,994 with `L13y0E2`; `logs/fix/heli_verify_s160_1*.txt`).

## 6. What may still be there (estimates, not proved)

- **Pool floor, up to about 35 frames.** We now need 239 frames from the floor landing to the corridor ledge; the
  record and up14 need about 204. The hop over the floor mine is forced, the stall before it (34 frames) and the
  sub-pixel line-up are what could shrink. 6,000-trial random searches topped out at 220 frames early at T' (this
  line: 210), and the phase rule then decides which of those can be used.
- **Corridor mine 2, 13 frames**, and 3 lag frames: forced as long as the rest of the level is the old inputs. Getting
  them back means re-searching the corridor to the level end (1,200 frames) - a day's work for at most 16 frames.
- Remaining Level 9 deficit to the record by the first-black rule: 0.52 s (31 frames).
- Honest total: **0-15 frames with more of the same searching, perhaps 30-45 with a fresh search of pool floor and
  corridor.** Nothing here is needed to be under the record.

## 7. Files

- Segments: `logs/pbeam_L9heli_c2.json` (Level 9), `logs/pbeam_L9heli_c2L10.json`, `logs/pbeam_L9heli_c2L11s.json`
  (`L9heli_c2L11` = the same without the entry Select). Fallback chain: `pbeam_L9heli_s160_1`, `L9heli_L10..L13`;
  first complete line: `pbeam_L9heli_t1` (155). `pbeam_L9heli_c2L12/L13` are the plain re-fits (not needed).
- Bookmarks: `L9heli_c2_end0` (Level 10 entry), `L9heli_c2L10_end0`, `L9heli_c2L11_end0`; `L9heli_R_*` (states at T'),
  `L9heli_7800/7819` and others from the searches.
- Proof logs: `logs/fix/heli_verify_c2.txt`, `heli_verify_c2E.txt`, `heli_full_c2.txt`, `heli_rngfit_c2.txt`,
  `heli_entry2_c2L11.txt`, `heli_wscan_c2.txt`, `heli_mine_c2.txt`, `heli_table_c2.txt`; route inputs
  `logs/fix/heli_route_c2.inputs.txt`, `heli_route_c2E.inputs.txt`.
- Tools (all `l9heli_fix_*.py`): `lib` (helpers), `beamAB`/`beam2` (tunnel pass and fall), `stA4`/`hop1`/`rand3` (join
  search: fall variant -> hop -> T'), `mine` (corridor hop repair; env `SHOFF`, `SMOD`), `wscan`/`m2scan` (wait at
  mine 2), `reroll` (Select re-rolls for the tank), `full` (builds and checks a Level 9 line, writes the segment),
  `endbm` (entry bookmark), `entry`/`entry2` (level-entry dice scan), `verify` (power-on replay with ending),
  `chain2`/`diag`/`table` (reports), `p*`/`t*`/`w*` (probes).
