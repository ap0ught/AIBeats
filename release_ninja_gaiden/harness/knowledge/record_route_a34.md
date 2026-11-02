# The record's route through Acts 3-4 (TheRetroRunner 11:32.183), extracted from his video

Agent a34, round 2 (2026-10-19). Method reused from the other agents (`record_route_a56.md`, `record_route_a12.md`),
not re-invented:

* Frames: `states/tmp/a34r2_vid/extract.sh` cuts every video frame of each stage from
  `dl/record_video/v1890225973.mp4` (game area 1200x900 at (600,140) -> 256x240, `flags=area`) to
  `states/tmp/a34r2_vid/s31 s32 s33 s41 s42 s43 s44` (file name = video frame index).
* Trace: `work/a34r2/rtrace.py` = `work/a12r2/rtrace.py` (= a56's `record_trace.py` with the HUD mask at y 60) on
  those folders -> `work/a34r2/rec/r31, r32, r41, r42, r43.json` (room index from black screens, cumulative background
  scroll since the room start, Ryu's screen position = densest Ryu-blue cluster).
  **Caveat:** in 4-1c (sky) and parts of 4-2 the lavender sky / night background matches the Ryu-blue colour test,
  so `sx/sy` are garbage there; the scroll column is still exact. I used the scroll (not Ryu's position) for timing.
* `work/a34r2/lag.py <rec json> <TAS control> <TAS end> [step]`: for each record image, the TAS time (frames after
  control) at which the TAS's scroll since the same room's start (room change + 23) first reaches the record's scroll
  -> "lag" = record t - TAS t. Valid for rooms that scroll rightwards only (3-1, 3-2, 4-1a/c, 4-2, 4-3b).
* Contact sheets / zoomed crops for the places that matter: `work/a34r2/sheet.py`, `work/a34r2/crop.py`
  -> `work/a34r2/rec/*.png`.
* Times: t = NES frames after the stage's control frame (video frame - control video frame) x 60.0988/60; control
  video frames = "timer digits first shown - 6" (record_events.json, +-3 f): 3-1 11679, 3-2 13279, 3-3 15603,
  4-1 16513, 4-2 18701, 4-3 21001, 4-4 23554.

## Room entries (t after control; record = first picture after the 22-frame black, TAS = room change + 23)

| stage | TAS rooms (first picture t) | record rooms (first picture t) | record - TAS |
|---|---|---|---|
| 4-1 | a 0, b 1463, c 1561 | a 0, b 1474, c 1603 | b +11, c +42; stage end +79 |
| 4-3 | a 0, b 139, c 774, d 1560 | a 0, b 160, c 856, d 1687 | b +21, c +82, d +127; stage end +163 |

## Per stage

### 3-1 (record 26.67 s = TAS -2)
Scroll lag table not usable from the control frame (stage 3-1's room byte is stale on the TAS control frame); the
record is level with the TAS throughout (stage total -2 f). Our round-1 file is TAS +5.

### 3-2 (record 38.73 s = TAS +21)
Scroll lag (record - TAS): +2 to scroll 499, +4 to 739, **+21..+25 from scroll ~800 (TAS t ~600-620; the record
loses ~17 f there)**, then at the pillar (scroll 1700-1765, TAS t 1204-1265, the TAS's L+R section 12646-12718)
the record goes from +25 to +38 and then **+18**: the record crosses the pillar section ~7 f faster than the TAS, and
stays +18..+23 to the end. Our round-1 goal beam lost +10 at the pillar instead (TAS-guided), i.e. ~17 f worse than
the record's line there.

### 3-3 Basaquer (record 15.17 s = TAS +83)
Contact sheets `work/a34r2/rec/s33.png`, ENEMY bar crops `hud33.png`. The record throws Fire Wheels from the
left/centre while the boss is in the air and sitting LEFT (bar 16 -> 13 by video 15660, -> 10 by 15672, -> 8 by
15708, -> 5 by 15732 while the boss jumps right), then when the boss sits RIGHT (video 15738-15774 = TAS-frame
~13876-13912) Ryu walks to him and jump-slashes: bar 3 -> 2 -> 0, empty at video 15769 (TAS-frame ~13907).

### 4-1 (record 36.47 s = TAS +79)
* 4-1a: lag +2..+9 to scroll 1459, +11..+12 after the 15700 block (TAS chimney climb).
* 4-1b (shaft): record +11 at entry, +42 at the 4-1c entry.
* **4-1c** (TAS: in-wall L+R/U+D wobble 16132-16199, then a damage boost onto the wall top at 16199-16220):
  crops `work/a34r2/rec/c41climb.png` (video 18125-18213). The record enters at the bottom left of the tall wall,
  **climbs its left face with single-wall jumps at a period of ~8 frames (~1.5 px/f)**, jumps off onto the branch
  stub that sticks out of the wall's left face (y 128 in RAM), a bird dives at him on the branch, he jumps from the
  branch, takes the bird hit high up (damage boost; he flies off the top of the screen) and lands on the wall top at
  video ~18225 (TAS-frame ~16284; the TAS is there at 16220). Then he runs along the top of the screen at TAS pace:
  scroll lag constant +83 from scroll 72 to the end of the room.

### 4-2 (record 38.33 s = TAS +26)
Scroll lag +6..+8 to scroll 1000, +10..+15 to scroll 2800 (constant +14 through the TAS's U+D+Right section at
TAS 18160-18232, i.e. the record loses nothing there: he slashes the birds/ninja in the air, video 20203-20225),
then the end walk.

### 4-2 detail at the round-1 stall (crops `work/a34r2/rec/c42.png`, video 20262-20334)
From the end of the upper brick platform (TAS ~18270) the record jumps up onto the brown "branch" ledges at the top
of the screen (video 20268-20307 he runs along them at the top edge), then drops at 20310 slashing the bird and
lands on the lower floor at 20322 (TAS-frame ~18300 + 14). The TAS instead walks down with U+D+Right.

### 4-3 (record 42.55 s = TAS +163)
* 4-3a (crops `s43ab2.png`): runs left from the right side, climbs the LEFT face of the central brown pillar
  (single-wall climb, like the TAS's x=104), exits at the top (room change ~t 139; TAS 116).
* 4-3b: appears at the bottom of the narrow gap between the left wall and the brown box (RAM x 91, y 232 - the
  same entry as the TAS), wall-jumps between the box's left face and the left wall (chimney) up onto the box top
  (video 21198, ~t 197), then goes right. Scroll lag +38 -> +79 at scroll 195-238 (TAS t 315-371; ~36 f lost),
  then constant +77..+79 to the room's end.
* 4-3c (crops `c43c.png`, video 21855-21975): enters at the bottom by the tall pillar's left face, climbs the gap
  between the small box and the pillar onto the box (21883-21899), jumps up and right onto the top of the tall
  pillar (21927-21939, ~TAS-frame 19899; the TAS is at the same point at 19824 with L+R, record +75).
* 4-3c/4-3d: +82 at c's entry, +127 at d's entry, +163 at the end (rooms scroll leftwards, lag table not computed).

### 4-4 Kelbeross (record 13.07 s = TAS +14)
Not re-extracted (our round-1 file is TAS +0 = record -14).

## What a legal run can take from this (found in round 2)
* **Single-wall climbing is legal and fast**: `Left+A, Left+A, Right x6` (wall on Ryu's right; mirrored for a wall
  on his left), 8-frame cycle, 1.54 px/f measured at the 4-1c wall and 1.45 px/f in the 4-3b gap
  (`work/a34r2/climbsweep.py`, all 310 legal 5-8 frame cycles). This is the record's own rhythm. Round 1's "only
  alternating patterns climb" was wrong (it tested the wrong spots / patterns). Beam macros `C8`, `C8m`.
* Mechanics (ROM, bank 7 $EB7B-$EC5A, $E677, $EFF1): on a wall the jump-off needs pad == A+away EXACTLY ($81/$82);
  it flips the facing, sets vy -2 and run speed; the wall can be re-grabbed only after no wall tile is touched for
  one frame (`touching` bit 7); in the air the opposite direction only drifts at 0.5 px/f (facing never turns in the
  air); wall contact is not tested above y 72.

## Round-2 use of the extraction (what it changed)
* 4-1c: the record's single-wall climb + branch + jump onto the wall top, done with legal C8 cycles and an A* over
  stable states (`ng/stages/a34r2_astar.py`): our 4-1 = TAS +72 = **record -7** (`logs/a34/4-1_r2c`).
* 4-2: the record passes the round-1 stall at TAS pace (+14) on the brown top ledges; our A* passes it at ~+11..+17
  but loses ~25 f at the exit wall (the TAS uses a damage boost there): 4-2 = TAS +53 = record +27 (`4-2_r2d`).
* 4-3b: the record's chimney onto the box (the gap left of the box is a chimney with a ledge at y 208); our A*
  matched it within ~8 f; room c's start (record climbs the gap between the small box and the tall pillar) cost
  our A* ~40 f more than the record; the pillar/stepped-block section at TAS 20030-20130 was not solved in time.
* 3-3: the record's ENEMY-bar drops while Basaquer crosses are Fire Wheel hits (ninpo 12 -> 07 at video ~15708);
  sword hits on the flying boss were not reproduced (0 in all sweeps): the sword reaches him only at take-off.
