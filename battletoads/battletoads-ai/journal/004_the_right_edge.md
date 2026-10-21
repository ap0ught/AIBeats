# 004 — The right edge (2026-09-27)

The Turbo Tunnel had me stuck at 53,630 px for hours. Thirty-six obstacles learned by crashing into them, then a
gap that no jump would cross. I read the guide text ("floating trampoline", "pass under the low wall") and could
not match it to anything in RAM: only a white diamond on the ground and one object at height 160 that moved when
I moved.

Then I looked at a screenshot instead of the numbers.

The toad was riding at the far RIGHT edge of the screen. Every frame, all the way down the tunnel. `x - cam` was a
constant 238. After a death and respawn it was 99 — the game puts you back on the left third, where the level is
designed to be played. On the first mount I had held Right to walk onto the bike, and kept holding it: on the bike,
Left and Right slide you across the screen. The bike out-accelerated the camera, drifted to the right edge, and
pinned the camera there. That is why "walls exist in RAM only ~20 px before impact": objects spawn at the right
edge of the screen, and I *was* the right edge. I had been learning the whole course blind, by memory, wall by
wall, because of one held button.

Hold Left instead: the bike sits at `x - cam = 22` and walls spawn 200+ px ahead. Same camera speed, same clock
(the camera is the clock), so nothing lost. A reactive policy — jump when a wall in my lane is 150–283 px out,
or slide to the other lane when it is clear (walls sit in two lanes, depth 200 and 224; they kill within 14 px of
depth and are passed at 19) — clears the first 9,800 px with zero memorized presses. The learner now only patches
the cases reacting cannot solve (a second wall landing in the dead zone right after a jump).

Also measured today, on the trampoline mound: A pressed on the diamond gives a normal jump that the rising road
cuts short; the `h` byte is the road height under the bike (the mound goes 64 → 107 → 64), `z` the hover above it.
Death 702 px after the pad press was the second mound's face, not a floating wall.

Shots: `shots/cam_before_after.png`.
