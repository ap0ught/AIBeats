# 007 — Karnath's Lair (2026-09-27, afternoon)

Level 4 ends in a Mega Warp: `l4.py` now runs 12,450 frames from the tunnel's end to the first frame of
control in Karnath's Lair (level byte 8), hp 47, 4 lives. Bookmark `L6_start`.

## Room 1, first look

The toad spawns at (120,216), height byte 30, on a floor that runs to x 447. About 100 frames in, a snake's
head (ID 0x4c) slides out of the hole in the left wall at (64, h 80), travels right at 2 px/f, at x≈336 climbs
(h 114 → 194 → 240) and carries on right at h 240; body segments (0x4d) follow 60–80 px behind. The exit hole
(0x4f, HP 15) is at (384, h 176). A press alone is a small hop (+21). The plan is the beam: `reach` 370/+130
from `L6_start` with the level check set to 8; the snake is a moving platform, the exit a hole in the wall.
Route verification from power-on through the warp is running (`assemble_L4route16`).

Route verified from power-on through the Level 4 warp: **27,054 frames, sha1 f403616a**, level byte 8,
4 lives (`logs/assemble_L4route16.txt`). Levels 1, 3 (the full tunnel, to be replaced by the skip later),
and 4 are now a single reproducible input list.

## Room 1 mechanics (afternoon)

- The snake's **body is a static platform** (the toad can stand on it at h 94 = body h + 14) but it does not
  carry the toad; the **head carries** (collision on its top, only at and behind its centre — 4 px ahead and the
  toad slides off the nose).
- A full jump (A held 32) from the floor peaks at +75 (h 105); under the body the jump is capped at h 64
  (head-bonk, anim 45). Jumping at the approaching head when it is 38–52 px away, then holding Left, lands
  the toad on the body (h 94); tracking the head's x (x = head − 2) rides it up the corner at x 336 (the toad
  is pushed up, z 8) and along the top at h 254 to the right wall at (449,254). The head enters the wall at
  (446,240) (object 0x4e appears there) and the body retracts ~30 frames later, dropping the toad to the floor.
- Nothing enters a new room: standing at the wall, Up/Down/B/Right there, falling past the wall hole,
  flying through the marker object 0x4f at (384,176), jumping from the top segment at x 352–416 (the h byte
  wraps past 255 up there — my "peak" logs lied), riding the nose. The marker 0x4f (HP 15) never moves.
- Snake cycle ~600 frames from the left hole (64,80). A **second snake** appears only after the toad has been
  at the top right: it leaves the right wall at floor level (447,48), runs left to x≈294, up to 144, on to
  (208,34)/(112,8) and into a left-wall hole at (64,176) (0x4e there).
- Beam fix: the search skipped A while airborne, so it could never hold a jump beyond 4 frames (+45). Now A
  may continue a hold started on the previous macro (B is still only allowed on the ground). New mode `room`:
  goal = the 0x4f marker gone from the object table. Running it from `L6_ahead` toward the top right.

## Where is the exit? (late afternoon)

Beam `room` mode from the toad-ahead state: unsolved after 400 frames (best h 336 at x 440; the marker
never vanished). Guides say the first section is "jump from snake to snake"; TAS #6758: "At the top of the
first snake, there is a small patch of collision on the center of the snake's head... By jumping onto this
and then jumping to the exit hole"; TAS #3356: "an invisible platform on the snake's nose, that appears
randomly, depending on toads positions, allows to jump into an out hole earlier". So the exit is a hole you
JUMP into from the head — the beam with a teleport goal (the toad's x jumping >100 px in one macro) is
running from the top-right state (toward the left-wall hole) and from the toad-ahead state (toward the top
right). GameFAQs/StrategyWiki/Fandom pages are blocked (403/402) from here.

## The upper half (evening)

Heights wrap: the "second snake at floor level" is really in the **upper half** of the room (its h bytes are
+256): it comes out of the top-right hole (447,304) — the very hole the first snake enters — runs left at
6 px/f along 304, climbs at x 304 to 400, runs left to 208, drops to 240, left to 112, climbs to 432 and enters
the left wall at (~64,432). The room scrolls vertically (camy 513 on the floor, 246 at the top). The beam
found the way to stay up there: keep hopping on the first snake's retracting tail at the wall until the
second snake emerges, then land on its body (`knowledge/l4s_L6_ahead2_best.json`; screenshot
`shots/l6_best_sheet.png`). By hand: from the top-right stand, Left+A held 20 at k 132 puts the toad on the
second head as it emerges (`L6_onhead2`), but the head outruns a walking toad (2.4 vs 6 px/f) and a dash
throws the toad off the head's small patch. Riding its body to the left wall (the head gone) does nothing.
Searching from the on-head state with the teleport goal (toward the left hole) and the marker goal (toward
(384,432) — the marker's h 176 may also be a wrapped 432).

## Still no exit (evening)

Six beam searches (marker-gone and teleport goals; from the toad-ahead, top-right, on-second-snake and
on-second-head states; ranked toward the top right, the top left, the left-wall hole and the marker's
possible raised position) and 240 random 400-frame playouts: no room change ever. Riding the second snake's
head fails on speed: it runs 6 px/f, the toad walks 2.4 and a dash throws it off the head's small patch.
TAS #6807 says: "At the end of this first room, I do a precise jump onto the edge of the blue snake's head,
and then quickly jump from there to the exit hole" — the blue (first) snake, at the end of its path. So the
exit must be right by the top-right wall hole, entered by a jump from the head's edge — yet every jump and
wall-press there did nothing, so something about the timing or the hole's state escapes me. New tool:
the harness can now play a BizHawk movie (`BizHawk(movie=...)` + `step_movie`), and the TAS's .bk2 is in
`tas/`; it desyncs on our 2.11.1 NesHawk in level 1 (the toad stalls at x 335), so BizHawk 2.3.2 — the version
it was made on — is downloading to replay it and watch the real exit with RAM logging.

## The TAS shows the room (evening)

BizHawk 2.3.2 replays the TAS in sync (`toads/tas/watch_log.txt`, `analyze.py`). Unwrapping the height byte
by continuity gives the real geometry: the room is about three screens tall. Snake 1: left hole (64,80) →
right → up at x 336 → right-wall hole (446,240). Snake 2 (from the right-wall hole at (447,304), only after the
toad has been at the top right): left along 304 → up at x 304 to 400 → left to 208 → down to 240 → left to
112 → up to 432 → left-wall hole (64,432). Snake 3 (left-wall hole (64,496), after the toad has stood in the
snake-2 hole at (62,446)): right along 496 → up at 336 → ... → left along 560 → up at 112 → right along 624 →
right-wall hole (446,624). **The exit is a ledge at (366,691) beside the marker 0x4f at (384,688)** (its h byte
176 = 688 mod 256; every "h 176" I chased was this, 512 px too low). The TAS's P1 stood on snake 3's 560-body
at x 179, jumped Right onto snake 3's head passing on the 624-run (landed (220,638)), jumped again at once to
the ledge (366,691), stood there while sparkles (0x30) rose from the marker, and the room changed 128 frames
later. Heads pause at corners and lift a toad standing on them up the vertical legs; a toad walking along the
body catches the head at the next corner. Caveat: the TAS is 2-player and P1 rode P2's head in places.

Working through snake 2 by hand from the beam's column-top state (`L6_seg1_solved`, 124 frames from the nose
landing): trail the head by ~10 px along the 400-run, park at x 220 just right of the x-208 corner while the
head descends and lays the 240-run, then step off and fall straight down (holding Left during the 80-frame
fall drifts the toad 160 px past the run's end).
The drop lands on the 240-run at (126–189,254) after a 65-frame fall (Left held 20 frames drifts it to 126);
standing at 126–128 the toad is NOT lifted when the head climbs the x-112 column — it falls off the run's end
instead — so the standing spot for the lift must be closer to the column (the TAS's P1 was at 128, but it was
a 2-player run). Scanning 108–124.

Snake 2 done by hand: park at x 220, drop when the head passes x 204 (Left for the first 20 frames of the
fall) → (126,254); at x 126 beside the x-112 column a 2-frame Left+A hop at the right moment (k 80 after the
drop) lands on the rising head → lifted to (116,446); walk into the left hole (62,446). The hole's floor (the
retracting snake-2 body) vanishes the moment snake 3's head appears at (64,496); a Right+A jump 96 frames after
entering the hole lands on it at (84,510). Snake 3's true path: right along 496 → DOWN at 336 to 368 → right
to 400 → up to 560 → left along 560 → up at 112 to 624 → right along 624 → right-wall hole (446,624).
Snake 3 by hand: ride its head along 496 tracking its centre (a nose landing falls off), park at x 312 while
the head dives down the x-336 column, walk to the body's end (330) once it has, then Right+A held 20 when the
head climbing the x-400 column reaches h≈470 lands on it and rides to the 560-run (`L6_on560`). Walking left
to x 182 and waiting for the head's return along 624 dropped the toad on the floor — the 560-run retracts
before the head comes back, so the wait spot and the timing need the head's schedule.

## ROOM 1 SOLVED (2026-09-27, ~17:00)

The last piece: the toad on the 560-run drifts left to x 126 (the x-112 column stops it); when snake 3's head
comes back along 624 its centre passes 8 px left of the toad — jump straight up (A 32) as it does (trigger:
head.x − toad.x ≥ −8) and land on it at h 638; track its centre rightward and at x 270 press Right+A 32 → the
toad lands on the exit ledge at (366,691); 128 frames of standing there later the room changes and the toad
appears at (76,62) in room 2, as in the TAS. Bookmark `L6_room2`.

Full room-1 recipe (all snakes 2 px/f, heads pause at corners):
1. Right to x 300; when snake 1's head is 44 px away jump A 32, hold Left → on its body (h 94); track x =
   head − 2 up the x-336 column and along the top to the wall (449,254).
2. 147 frames after the head vanishes into the wall, Left+A 20: lands on snake 2's nose as it leaves the
   top-right hole (447,304). The beam's 124-frame line (`knowledge/l4s_L6_seg1.json`) rides it up the x-304
   column to (292,414).
3. Trail the head by 10 px along the 400-run; park at x 220 when the head reaches 222; when it has laid the
   240-run below (head at h 240, x ≤ 204) step off, Left for 20 frames of the fall → (126,254). 80 frames after
   the drop, Left+A 2 → onto the rising head → (116,446). Walk Left into the hole (62,446).
4. 147 frames after the lift completes, Right+A 20 → onto snake 3's emerging head (84,510). Track its centre
   right to x 308, park at 312 until the head has dived below h 440, walk to 330, and when the head climbing
   the x-400 column reaches h 470 press Right+A 20 → carried to the 560-run.
5. Track the head left along 560 (the run is laid behind it) — the toad ends at (126,574). Jump A 32 when the
   returning head on 624 is 8 px left of the toad; ride it right; Right+A 32 at x 270 → the ledge → stand.

Room 2: the toad drops to the floor at (76,30); the portal 0x22 appears at (432,104) at once with a ~450-frame
lifetime; a snake emerges beside the toad at (112,32) and climbs; the floor right of x≈150 is spikes (walking
right dies at (160,28)). Beam `warp` mode running from `L6_room2`.

## Room 1 scripted (2026-09-27, ~17:30)

`l6.py` reproduces the whole room from `L6_start`: **1,984 frames** to room 2 at (76,62), hp 47, 4 lives
(`logs/pbeam_L6a.json`). Two lessons from making it deterministic: the height unwrapper must see every
frame (a 20-frame button press hid a wrap and every later phase read garbage), and fixed frame offsets must
mirror the probe exactly (160 ride frames with the x-449 fallback, 133 idle, then Left+A 20 — one frame off
and the toad lands airborne beside the nose instead of on it). Power-on verification running
(`assemble_L6route1`); beam `warp` mode running in room 2.

## Room 2 (evening)

Power-on verification through room 1: **29,028 frames, sha1 385b6a60**, level byte 8, 4 lives.

Room 2 geometry: floor at h 30; a spiked floor from x≈150 with a spiked block at x≈288–320 rising to h≈110;
the portal 0x22 sits at (432,104) from the first frames (HP counts 190→0 by f200, the object is gone by
~f450). The snake rises from the floor hole at (112,32) at f70, reaches 336 at f220, runs right to 176, drops
to 176, runs right along 176 and enters the wall at (446,176) at f490 — too late for the portal. The TAS is
2-player: its P1 dash-jumped from the floor straight into the spiked block (dead at (291,94) — "the game
doesn't check if you are alive when you hit the exit") while P2 must have taken the portal. So the 1-player
route has to use the snake: get on it as it rises, ride to the 336-run, drop off its end at x 176 moving right
(clearing the block), land right of it and jump up into the portal — if the floor there is safe, and before
f450. Standing on the hole is not lifted by the emerging head.

**The mechanic I was missing: the toad CLIMBS snake bodies.** The beam's best room-2 line stands at x 103
beside the column rising from the floor hole and holds A (with a direction): the toad goes up at ~2.9 px/f
in a climbing animation (anim 88/89, z 8) and pops out on top of the 336-run. Every "hop onto the head" in
room 1 was the hard way.
The climb needs the alternation: Left+A / Right+A every 4 frames beside the column (x 103–106) climbs to the
336-run's top at (106,350) in ~110 frames (`L6_r2_onrun`); plain A, Left+A or Right+A held all drop off.
Room 2 hazards (debug-poke map on a snapshot, 16-px grid, height byte only): single spike tiles in the air
at (128,238–254), (224,238–254), (320,238–254); a spiked block at (336–352, ≤94); the spiked floor from x≈160.
Dash speed here is only 3 px/f; a floor dash-jump peaks at h 105 and lands in the block. The TAS's P2 route
was "Right+A held 65 frames, then Right for 140": jump, keep holding right, hit the wall and slide down into
the portal at (432,104) — trying it from the 336-run's end.

## ROOM 2 SOLVED — Level 6 warp (2026-09-27, ~18:30)

From the 336-run: trail the head by 24 px until it turns down the x-176 column, walk to x 162, Right+A held
12 frames, then hold Right: the arc peaks at h 421 near x 230, clears the spike tiles, and the toad comes down
the right wall into the portal at (417,94) — routine pointer $E50D, the warp to Level 8. Only that exact
(x 162, 12-frame) combination worked in the first scan; longer holds die on the (336–352) block, other x's on
the tiles. Adding room 2 to `l6.py`, the script's own on-run state landed 1 px off and died, so the jump is
being re-scanned from the script's state.

## LEVEL 6 DONE (2026-09-27, ~18:45)

From the script's own on-run state the winning jump was (x 154, A held 8) — a different knife-edge than the
probe's (162, 12); with it `l6.py` runs 2,390 frames from `L6_start` to the engaged warp at (418,94), hp 47,
4 lives (`logs/pbeam_L6a.json`). Power-on verification running (`assemble_L6route2`). Next: the warp card into
Level 8 (Intruder Excluder), the vertical climb and Robo-Manus.
