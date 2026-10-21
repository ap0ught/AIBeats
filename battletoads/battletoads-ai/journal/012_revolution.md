# 012 — The Revolution (Level 12, level byte 5)

## Opening (2026-09-29, ~01:10)

Verified start: 54,702 frames from power-on, the toad placed at (136, 30) 219 frames after the level loads,
6 lives, run clock 14:36. An enemy hits an idle toad ~110 frames after placement. The 1P TAS (FCEUX log
`tas/watch_1p_l12.txt`, summary `logs/tas1p_l12_summary.txt`): 7,519 frames, climbing the rotating tower to
H ≈ 5,500; x wraps around the tower at 512. It holds Left+Right on 298 frames (sprite-plane shifting — banned
for us), so some stretches may need our own line. Research notes (2.13): springs rotate at a fixed rate
(128 frames per circle); the green disappearing platforms run on the global timer $000B (256-frame loop);
dash-springs and the mid-air direction switch are legal; the L+R early end-object spawn at the top is not.
Plan: follow sections of 300 TAS frames (`l12follow.py`, `L4S_XWRAP=512` wrap-aware distance), `l12.py` replays.

## The TAS replays exactly (2026-09-29)

The first follow search died at the first spring (springs fire on their own clock). Then a better idea: FODA's
inputs replay frame-exactly in BizHawk with a 1-frame shift (our step s applies TAS input s+1, compared with log
row s+1). That holds for 861 frames, right up to the first Left+Right. `L12_r1` is that replay, 857 frames
(steps 0..856, every input legal), ending with the toad just landed off a spring at x 298. Steps 800–858 are
the spring launch and landing: no input does anything there.

## Cluster 1: the TAS's instant sprint, done legally

At step 861 the TAS presses Left+Right+A: an instant 3 px/frame running jump left, onto a platform at x 187.
Calibration of the legal sprint (speed $565):
- plain hold: accelerates slowly to 128 (2 px/f); a jump from it falls short.
- double tap (tap, 1 idle frame, hold) in the direction the toad FACES: 192 at once (3 px/f).
- the toad lands off the spring facing right. Pressing Left turns it, and a double tap only counts once the turn
  (anim 1 for ~6 frames) is over. Turning in the air or during the landing does nothing (inputs are locked).
- fastest legal line: Left, 5 idle, Left, idle, Left+A held 21 frames → lands on the x-187 platform at step 903,
  6 frames behind the TAS. That is section `L12_r2` (45 frames, scripted in `l12chain.py`).
Landing resets the sprint, so every later jump needs its own double tap. The follow search has composite
actions for that (RunL, RunLA = tap, idle, hold). From here `l12chain.py` runs 300-index follow sections.

## Follow sections (l12chain.py)

`L12_f0` (TAS 899→1214): solved, 456 frames for 315 TAS frames, 141 frames behind. Where they go (replayed
side by side with the TAS): 1–2 frames per jump where the TAS sprints and the beam walks (6 → 35 behind by TAS
frame 1054), then two stalls on the sinking platforms (object 0x36, which sink while stood on and rise again).
The TAS jumps off them as they rise and gains about 136 px in one jump. The beam, which doesn't see the
platform's phase, loses ~65 frames at x 383 and ~35 at x 447.
Tried: a "TAS replay" action in l4s.py (`L4S_TASIN`, `L4S_SYNCTOL`): a node within a few pixels of a TAS
frame may replay the TAS's next legal inputs. It kept sync only briefly after the 6-frame offset and didn't
beat plain follow, so it stays off. Width 200 moves about as far per step as 400 at ~60 % of the cost, so later
sections use 250 (`L12_WIDTH`).
The TAS's later Left+Right spots at 1672 and 2534 are the same instant-sprint jump off a spring landing
(the same ~6-frame turn cost for us). 2287 and 2764 are short, and 2889 is Up+Down while standing and waiting.

## The Hornheads lock the camera (2026-09-29 morning)

`L12_f1` stalled at x 385 three times. First cause: the beam merged sprinting and walking states (fixed:
`L4S_SPDKEY=1` puts sprint speed in the state key; releasing the direction in mid-air drops 192 → 128 for good).
Second cause, the real one: at TAS frame 1403 the TAS snaps onto a ring ledge at x 385 and sprint-jumps ~160 px
to x 35. Our replay of its exact inputs matched it pixel for pixel up to 1402, then flew through the ledge.
Side-by-side, the TAS's camera starts scrolling up at 1398 and ours never moves. The only difference was the
Hornhead (object 0x5c) that our line had dodged. **While a Hornhead lives, the camera does not scroll, and the ledge
above isn't there.** The TAS kills every Hornhead (0x5c) and every 0x62 walker it meets (16 hp per hit, a
running kick = anim 31 kills in one hit), so the chain now has a kill section at each of those spots.
Kill sections: `L4S_RATDEAD` + `L4S_FOEID` + `L4S_FOEW=20` (a hit must outrank path progress), `L4S_FOEDX=1` (pull
toward the live foe), progress capped at the section's end, goal = a seen foe dead and none alive (`foeseen`).
`L12_f1k` killed the first one in 244 frames. From the platform, no beam found the launch, but redoing the TAS's
approach exactly works: walk left 68 frames to the floor, double-tap right, run 5 frames, then the TAS's own inputs
1344..1459 land on the far platform at (35, 165) exactly like the TAS (`L12_f1s`, 192 frames, scripted).
`L12_g1459k` killed the next Hornhead in 292 frames.
`L12_g1640` (TAS 1640→1829): the follow beam stalled at the second sinking-platform launch (x 304 again, pj 1739).
`resync.py` (short legal prefix: position, turn, double tap, jump; then an exact frame match with the TAS and
its own inputs) found 207 frames: a 90-frame approach, then TAS inputs 1713..1829, landing exactly on the TAS
at (50, 150). The chain now runs this re-sync automatically when a plain follow section fails.

## The big walker (TAS 2860–3160)

Kill sections worked for the Hornheads at 1920 (0x62, 188 f), 2120 (216 f, after two fixes: past the section's end
the off-path penalty is dropped so the toad can go back to the foe; with no foe on screen yet, climbing is
rewarded, since the camera spawns it) and 2390 (124 f). Follow sections in between: 1829→1920 in 44 f, 2000→2120
in 128, 2230→2390 in 200, 2500→2800 in 380, 2800→3080 in 92.
At TAS 2860–3160 the TAS fights a 0x62 walker with 111 hp (seven hits) from the bouncing platform at x 487. It
waits at x 400 until the RNG lets it walk over, and our inputs move the RNG (Select, Down, A and Up all change it).
Idle, it comes at frame 324; Down held, at 70. The kill beam wandered to it, got one hit and stalled at 95.
Fix: random samples of Select/Down/A/Up for 40 frames find triggers near frame 50–75. After a trigger, the TAS's
own fight inputs (aligned to when its walker left x 400) land five hits with the toad unhurt (`L12_g3080a`,
330 f scripted). A kill section fenced to the platform side (`L4S_FORBID=0,465,...`) finishes it (`L12_g3080b`, 208 f).

## Circling platforms (TAS 3160–3565)

Two new kinds of platform. A 0x34 platform circles the tower at 2 px/frame (TAS 3298–3340): the TAS catches it
from a fixed base; 4-frame steps kept missing it by a few frames, and 2-frame steps (`L12_g3290`, macro 2) caught it.
Then a sinking platform (0x36 at x 480) that needs the bounce launch: the beam's own landing on it, plus a
re-sync from there (a double tap left, then TAS 3398..3442), gave 160 frames. That became an automatic fallback in
the chain (`beam_resync`: from each of the failed beam's last landings, re-sync with the TAS).
At TAS 3504 a sinking platform that also circles: the TAS rides it, bounces, and launches to a platform at x 224.
Beam (4-, 2- and 1-frame steps) and re-sync from our landing all topped out at height 3305 vs the TAS's 3364. Our
landing matched the TAS's toad exactly but the platform sat 4 px off. Waiting doesn't help: the platform spawns when
the camera reaches it, so its phase depends on the climb, not the clock. Fix: `resync.py` got an object check
(the 0x36 objects must be where the TAS had them at the match frame). With it: a 57-frame approach, then TAS
3487..3565, landing on the TAS's platform (`L12_g3442`, 136 frames). The chain's fallback now retries with this check.
Then the platform chain at TAS 3564–3856 (fixed bounce platform at x 224 ↔ circling platform, three times). The
re-sync ended 1 px off (x 212 vs 213) and that pixel walked the toad off the next bouncing platform. Fixes:
re-sync now requires an exact match (tol 0). Sections spliced in by re-sync skip the 2 idle frames at the section
boundary (`knowledge/l12_noidle.json`, honoured by `l12.py`): they would break a bounce, and load-and-continue
equals a continuous replay (checked on RAM). After a match the TAS's own inputs keep running while the toad
stays within 3 px (sub-pixel drift), ending on the last exactly-matching landing. Result: `L12_g3442` = 52-frame
approach + TAS 3461..3856, 448 frames for 414 TAS frames, through every platform of the chain (exact landings
at 3608, 3703, 3752, 3792, 3856). The chain skips planned rows that a spliced section already covered.
Level 12 so far: 5,011 frames to TAS 3856, about 1,150 frames behind the TAS.

## The pole and the Swellcheeks (TAS 4610–5199)

Follow sections 3856→4060 (372 f), 4060→4360 (112 f), 4360→4500 (260 f), kill 4500 (160 f). Then a hard stretch.
The TAS rides a circling platform (0x36 at h 55), bounce-launches onto a pole (0x5f at x 480, h 152), hangs there
~260 frames, drops back onto the platform, bounces again and launches onto an upper circling platform (0x34 at
h 136) at 5199. What each part is:
- The pole is shelter: a Swellcheeks face (0x60) rises and blows wind (0x61 particles); an unsheltered toad is
  blown off. The face spawns relative to the toad's arrival, so its timing doesn't match the TAS's for us.
- The dead Hornhead's body (hp 0, still flying) keeps the camera locked until it leaves the screen (~80 frames).
- The face keeps the camera locked too: the upper platform only appears after the face has gone. That's why every
  "skip the pole" launch topped out with the camera at 1512 and nothing to land on.
- Single bounce (A held from standing on the circling platform): +99 px. Boarding: wait, jump, drift left.
- The search never boarded the platform on its own (it jumped from the floor below). A direct search boards it
  and grabs the x-480 pole (`L12_polehang`); from there a follow search runs to the TAS's 5199 landing.
Also: attacks are now only tried when an enemy is within 120 px (`ATKNEAR`, default in Level 12 follow searches).
Solved: hanging idle on the pole, the face rises (frames 19–115 after the grab), blows (115–435), and leaves at
~468; then the camera unlocks (1512 → 1488) and the upper circling platform (0x34, h 136) comes around under the
pole. Down lets go of the pole. Earliest drop onto it: hang 604 frames, Down, land 18 frames later at
(480, h 141) = the TAS's 5199 landing height. `L12_g4610` = board + bounce + grab (138 f) + hang/drop (622 f) =
760 frames for TAS 4610→5199 (589): ~170 frames lost to the face's later timing. Chain continues from 5199.

## The sinking circling platform at TAS 5420 (the sub-pixel lesson)

The toad's $457 is its x sub-pixel. It only changes on the TAS's Left+Right frames; legal play keeps it at 0, while
the TAS's was 168 for most of the level. So TAS positions can only be matched to about a pixel, which explains
the recurring 1-px drift. At 5420 the TAS lands on a circling 0x36 platform that sinks and launches it; ours never
sank. RAM dumps (FCEUX, per frame) showed the platform's attribute $50B+slot turning 128 at the landing. The TAS
toad reaches the platform from below and snaps up onto it at its jump's apex, with speed. The TAS's approach is
a standing double-tap sprint jump from x 498 (Right, -, Right+A). Recipe: walk left 219 frames, settle, tap
Right (rest at x 498 facing right), wait 141 frames until the platform is where the TAS had it at 5399, then
play the TAS's inputs. They stay in sync through the arming, sink, bounces and launch, but 1 px short at the
snap onto the fixed platform (x 240) at 5536, and the toad falls to its death. One changed input (Left at 5477
instead of the TAS's) recovers the pixel; sync then holds to 5610 (the 0x62 fight). `L12_g5350` = 617 frames,
ending at TAS 5575. Snapshot pokes of $457 and of the camera changed nothing (experiments only).
Emulator note: EmuHawk crashes after long msave-heavy scripts; restart it per outer iteration.

## Faces two and three (TAS 5575–6936)

Kill of the 0x62 walker at 5575 (192 f). Then the same pole/face puzzle twice more, solved by hand with small
tools (`polegrab.py`: board a circling platform, bounce, steer until a pole grab; `platjump.py`: board, ride,
bounce-launch into a target box):
- Face 2: board the circling h-192 platform, bounce onto the pole at x 96 (187 f). Hanging: wind from 93 to
  ~414 frames after the grab, face gone at ~473, then the camera unlocks and a higher circling platform (h 249)
  appears. Drop (Down) straight onto it at 605 frames (the TAS's 6319 landing height, H 4832), skipping the
  TAS's detour via the lower platform. `L12_g5730` = 814 frames.
- Face 3: from the h-249 platform, bounce-launch onto the small sinking platform at x 64 (342 f; it rides a
  whole lap first). The face rises; the toad must step right onto the platform at once (standing, it slides off
  the edge and falls) and jump into the wind, which carries it ~230 px to the pole at x 288 (114 f). Face gone
  339 frames after the grab; drop at 374 onto the h-249 platform (x 290, like the TAS); launch back to x 64
  (143 f); hold A through the sink and launch left to the ledge at H 4992 (40 f). `L12_g6330` = 1,049 frames,
  ending at TAS 6936.
Each face costs us several hundred frames against the TAS, which dropped from its poles mid-wind (our faces run
on a later schedule relative to the toad).

## The top (TAS 7242 → end) — LEVEL 12 DONE

The TAS scrolls the camera with Left+Right at 7262–7459 to spawn the end event (0x7F) early; we climb instead.
Legal ending found: the TAS's bounce off the x-464 sinking platform (its Left+Right+A replaced by A) lands on a
ring ledge at H 5664 (48 f). Small static platforms go up from there: 0x34 at x 240, 0x34 at x 160, and at the
very top the spring 0x35 at x 240, with the green cloud (0x5d) beside it. `hopchain.py` found the hops (165 + 40 f).
From the x-160 platform, a right sprint jump (-, Right, -, Right+A ×16, Right ×18) lands on the spring; holding A
bounces the toad onto the top ledge, the camera scrolls to the top, and 0x7F appears 62 frames later; the level
switches to 13 another 130 frames later. `L12_gtop` = 484 frames. Earlier climb searches all "died out" because the
toad falls off these small platforms (landing momentum) and anything below the screen dies.
`python l12.py $(cat knowledge/l12_sections.txt)` = 10,499 frames from `L12_start` to Armageddon (`L13_load`).
**Verified from power-on: 65,201 frames, sha1 768f0388, 6 lives, run clock 17:30 at Level 13's start.**
(The emulator connect timeout is now 240 s: with other heavy jobs on the machine EmuHawk took 79 s to boot.)
