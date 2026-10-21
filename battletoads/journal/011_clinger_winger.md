# 011 — Clinger-Winger (Level 11, level byte 10)

## Done in one evening (2026-09-28/29)

Start: the toad appears at (28, 44) 220 frames after the level loads and walks onto the unicycle (anim 100–103)
at x 164, which waits there until the Buzzball chase starts (~frame 260). The 1P TAS (FCEUX log
`tas/watch_1p_l11.txt`, 6,650 frames) holds **Up+Down while riding horizontally and Left+Right while riding
vertically** — impossible on a real pad, banned for us — so its inputs could not be replayed. The legal
mechanic: the unicycle follows the rail by itself; pressing the direction of the next segment at each corner
keeps top speed (spd 240), otherwise it slows to 128 and the Buzzball (0x7a) catches up (hit = death). The maze
has 75 segments; their directions and corner positions came from the TAS's motion
(`knowledge/l11_segments.json`; vertical position = camera y, the toad's height byte stays 44). A greedy
controller (`l11greedy.py`) chooses, corner by corner, the switch distance D (2–24 px before the corner) that
gets through the next corner fastest alive: **5,143 frames for the whole maze, ~15 frames ahead of the TAS**.
Then follow sections (search "height" = −camera y, `L4S_HCAM`): c2 the last straight into the arena (248 f),
c3 the arrival animation (28 f), and the Buzzball fight (0x7b, hp 207): the beam, ranked by Buzzball damage
(`L4S_RATDEAD` + `L4S_FOEID=0x7b`), lands 16-damage jump kicks — c4 1,000 f (207 → 47), c5 276 f (47 → 0).
The TAS does it faster by ramming it against the wall (−48/−64 per hit): optimization target (~700 f).
`l11.py` then waits for the level change and Starts into The Revolution (level byte 5), placement (136, 30).
**Verified from power-on: 54,702 frames to The Revolution's start (136, 30), RAM sha1 dbcb47d2, 6 lives** (logs/assemble_L11route.txt). Run clock at Level 12's start: 52,628 frames = 14:36.
