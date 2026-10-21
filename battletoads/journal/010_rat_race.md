# 010 — Rat Race (Level 10, level byte 9)

## Opening (2026-09-28, 16:20)

Verified start: frame 44,999 from power-on, the toad placed at (88, 158) with control at once, 5 lives, run
clock 11:54. Two fliers (0x50) patrol above and sparks (0x3a) cross; Right runs (x +59 in 40 frames), A jumps
(h 158 → 228). The level (research.md 2.11): race the rat Giblet down three times to reach a bomb before it
does, then General Slaughter. Our rules (Any% No Credits Warp) allow the **rat boot**: "the rat must be hard
hit after the bomb is exploded, and then finished off with a Boot attack. The rat has infinite HP... seems to
have a 'boss' flag"; RTA: "If you can manage to free-fall throughout the race as much as possible without
touching the platforms, the rat will usually land in a consistent location on the screen at a consistent
time"; object 0x46 = the rat / level end; $00F3 = rat slot. The 1P TAS #5093 (warpless) plays the full level
(logged in `tas/watch_1p_log2.txt`, level byte 9 = FCEUX frames 60961–62885, 1,924 frames).

The 1P TAS's Rat Race (logged in FCEUX: `tas/watch_1p_l10.txt`, screenshots `tas/1p_l10/`, summary
`logs/tas1p_l10_summary.txt`): 1,898 frames from placement to the level change. It zig-zags down the platforms
(each ~64 px, run to the edge, drop, turn) to H −640, then free-falls a long shaft at 4 px/frame to H −2946 with
the rat (0x46, hp 255) alongside, lands at H −3200, kicks the bomb (0x5a, hp 1) at index ~1300 (anims 31/30),
walks right and back, hard-hits the rat at index ~1540 (anim 35, rat hp 255 → 239) and boots it at ~1580
(anim 31 → rat hp 0) — the rat boot; the level ends ~300 frames later. Only one race instead of three.
Plan: follow sections on this path (`l10follow.py`, `L4S_PLACE=88,158`, `L4S_TASLOG=tas/watch_1p_l10.txt`)
and a last section with goal "rat hp 0" (`L4S_RATDEAD`); `l10.py` replays them, waits for the level to end and
Starts into Clinger-Winger (level byte 10).

## The rat boot, found (2026-09-28 evening)

Sections: f1–f4 follow the 1P TAS path (336, 324, 312, 296 frames — the descent and the free fall). f5 is
scripted (160 f): step right off the ledge edge at x 223, land on the H −3008 ledge, walk left off it, steer to
x ≈ 100 during the fall and press **Left+B in the air** a few px above the floor — the flying kick breaks the bomb
(0x5a) at x 80. The search could not find it: it forbade attacks while airborne (fixed: `L4S_AIRB`) and gets no
reward for the kick. f6 is scripted too (277 f), the rat boot: the rat is still falling past us (collision
compares heights mod 256, so its falling sprite passes the toad's height every ~36 frames) in a column at
x 146. From the right side, facing left like the TAS: park at x 196, double-tap Left to run, Left+B at frame
176 (the running kick, anim 35) hits the falling rat → hp 239 + state 64 (the "hard hit"). It bounces in place;
back off to x 160, and 44 frames after the hit double-tap Left again and Left+B → the running kick (anim 31)
lands as the rat comes down → hp 0 = the boot; the level ends ~300 frames later. Things that did NOT work:
standing B next to the rat (punch 25/27 or uppercut 33/32, −0/−8), kicks from the left side, Select presses to
steer RNG, 16-damage attrition (after the first hit the floor opens ~30 frames later and the next race
starts). `l10.py` = 2,076 frames to the Clinger-Winger load, then 220 to the placement at (28, 44).
**Verified from power-on: 47,296 frames to the Clinger-Winger start (toad at (28, 44)), RAM sha1 694c4a13 on both
replays, 5 lives** (`logs/assemble_L10route.txt`; segments … L9a L10a). Run clock at the start of Level 11:
45,222 frames = 12:32 (the record is 12:29 for the whole game).
