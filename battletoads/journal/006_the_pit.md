# 006 — The pit after checkpoint 5 (2026-09-27, afternoon)

Route verified from power-on through checkpoint 5: **21,791 frames, sha1 12faf8e4** (`logs/assemble_L4route9.txt`),
4 lives, timer 112. The rat-1 retry with the fixed dedup (`logs/l4s_rat3.txt`) still failed (190 steps, best x 210):
the generic beam does not kill rat 1 clean. Parked again; `l3.py` stays.

## Checkpoint 6 is not where the ball is

After barrier 5 the ledge descends left to the corner (32,47) and a new ice ball (0x38, HP 143) starts down the
same zigzag 30 frames behind the toad. Idling from the corner: the toad slides down-right to (109,221), back
down-left to (48,127), and the ball catches it there at f121. The shaft is four legs with the height byte wrapping:
corner (32,47) → (109,221≡−35) → (48,127≡−129) → floor at (101,94≡−162), a flat that runs right to x 192 and
ends in a spike pit.

Intercept (measured last night): walk Right to the bowl of leg 2 (x 115, h 227), wait, punch when the ball is
≤34 px away → it stops at (110,235) bouncing in place. **The stop lasts only ~40 frames on a slope** (the ball
rolls again at f40). Lift window: B works from f20 (the toad hops for frames 3–18 and must be on the ground) to
f38. Carrying: anims 11/13 then 16–18, the ball rides 34 above the toad; Left 120 f carries it down to (32,143),
Right slides it down leg 4 onto the floor.

Where's the barrier? Not on this floor. The floor ends at x 192 in a spike pit crossed by two floating platforms
(0x3e): platform 1 (h 104) shuttles 205↔360 at 1 px/f, platform 2 (h 136) shuttles 398↔548; they meet in the
middle (gap 38 px) and part again at 2 px/f. Hanging over the pit are two orange spikes (ID 0x43, HP 31) at
(288,144) and (512,176). The first scrapes a standing rider off platform 1 (the toad stops at x 280 while the
platform goes on, falls into the spikes); **crouching (Down) passes under it**. Punches and a thrown ice ball do
not damage them (HP stays 31) — they are hazards, not barriers. The pit's spike bed is higher on the right half
(deaths at h 93 left of x 380, h 125 right of it), so platform 2 sits barely above the spikes.

So the ball is useless here: throw it Right from x≈152 (after settling on the ice, or the throw-hop slides the
toad off the edge at 192 — that killed one regeneration) and it flies off the floor's end into the pit. Then the
toad waits at x 174–178 for platform 1 to come back left past 215 and hops on (Right+A 6, Right 4; a longer
run-up slides straight across it into the spikes). Riding: idle 66, Down 40 for the spike.

Platform 2: hand-timed jumps from the meeting point all died (the platforms part at 2 px/f while the toad is in
the air, and it lands at h 125 on the raised spikes). The beam (`l4s.py L4_cp6_p1_past 410 30 200 reach`,
SAFE 30) found a 64-frame two-hop line in 3 seconds — but its endpoint slid off platform 2's right side 22 frames
later: **the platform tops are icy too**, and SAFE 30 was too short to notice. A 2-frame Left brake holds it.
The second spike (512,176) then kills a standing rider at x≈505, and crouching at the platform's edge (offset
−22 from its x) drops the toad off it. Right of the spike is an ice ledge at the platform's right end (screenshot
`shots/l4_cp6_sheet5.png`). Re-searching from the regenerated `L4_cp6_p1_past` straight to that ledge
(gx 560, dh 30, SAFE 60) so the beam handles the brake, the crouch and the step-off together.

`l4.py` now runs to the platform-1 ride past the first spike: 8,094 frames, hp 15, 4 lives (bookmarks
`L4_cp6_stop`, `L4_cp6_free`, `L4_cp6_onp1`, `L4_cp6_p1_past`).

## Across the pit (later that afternoon)

The re-search with SAFE 60 found a 180-frame line to platform 2's right end (x 560) in 28 s — but it ends
mid-punch (Left+B was just the surviving child): **inputs are ignored for 19 frames after a punch** (anim 25/29),
which is why every jump I tried from that endpoint "did nothing". After the 19 frames, Right+A held 14 with
Right lands on top of the ice pillar (610,190) standing at the ledge's left end (held 6: on the ledge at (607,158)
against the pillar, blocked). The ledge (h 158) runs between two pillars (x≈610 and ≈740) and a rolling spiky
ball (0x40, HP 255, unkillable) spawns at 720 the moment the toad lands and patrols 633↔734 at 2 px/f,
period ~100 f; one touch = death at hp 15. The pillar top is icy: an idle toad slides off it into the ball. A
hand-timed hop over the pillar died on the ball's return; searching it (`l4s.py L4_cp6_pillar 780 -40`, SAFE 60).

`l4.py` now reproduces everything to the pillar top: **8,327 frames**, hp 15, 4 lives (`L4_cp6_onp2` at
(560,141), `L4_cp6_pillar` at (610,190)). Route re-verification from power-on running (`assemble_L4route10`).

## The switchback (evening)

Past the spiky ball the upper ledge simply ends at the level's right wall (x clamps at 799, camera 574): the
beam's "best unsolved" line (324 frames of hopping around the ball, `knowledge/l4s_L4_cp6_pillar.json`) leaves
the toad airborne at (769,236) off the second pillar, and from there it falls ~130 px onto a **lower ledge at
h 62** with its own pillar (x≈650) and a faster spiky ball (spd 192, 3 px/f) that rolls in from the left.
First leftward search (`reach_left`, height unconstrained) "solved" by flying back onto the upper ledge at
(580,158) — added mode `reach_down_left` (x ≤ gx, dh ≤ gdh) and it found the real run in 66 s: 208 frames
to (620,62) past the ball and the pillar. Off that ledge's left end the toad drops again, 96 px, onto **ledge 3
at h 222**, landing against a rock wall at x 576; a third spiky ball spawns at 720 and rolls left at 2 px/f
(kills an idle toad at f101). Three stacked ledges, alternating directions, each with a ball: a switchback
down the right side of the level. Searching ledge 3 rightward (`reach_down`, gx 740, dh ≤ −60).

`l4.py`: **8,863 frames** to `L4_cp6_lower` (620,62), hp 15, 4 lives; power-on verification running
(`assemble_L4route11`). Searches so far today all solve in 1–2 minutes now that the dedup keeps the
better-ranked child; the goal definition is the whole game.

## The bottom bowl

Off ledge 3's right-end pillar the toad slides down the level's right wall onto an icy slope (799,143) that
runs left into a bowl: floor 94 (x 733–691) → bottom at h 30 (x 558–590) → up to a short floor 94 (x 453–408)
with an ice pillar at x≈436 (top 126) and, left of the pillar, **checkpoint 6 itself: a pink snowball stack
(0x3c) at (392,118) with 255 HP** — eight times the earlier stacks. The pocket between stack and pillar
(x 408–436) is a safe spot: the spiky ball that follows the toad down the slope patrols the bowl 444↔796
(spd 80, ~600 f per lap) and turns at the pillar. An ice ball (0x38, HP 143) spawns at (480,79) the moment
the toad lands and oscillates 455↔770 in the bowl. Neither ball ever touches the stack on its own; punches
don't dent it. Walking Right off the pillar top slides the toad straight down into the bowl (icy) — two hand
scripts died that way. Running the beam in `wallhit` mode (now "any damage vs the root HP") from the pillar
top, and testing by hand whether a thrown ice ball clears the pillar and what one hit takes off 255.

Route verified from power-on through the lower ledge: **23,457 frames, sha1 1d8d4daa**, 4 lives.

## Checkpoint 6 falls (evening)

The stack takes **16 per ice-ball hit** (255 → 239 on the first), and one throw is enough: from the floor
right of the pillar the ball is carried at h 128, above the pillar top (126), so a Left throw sails over the
pillar into the pocket, where it **bounces between pillar and stack** and grinds the 255 down in ~190 frames.
Recipe (measured, `cp6_bowl()` in `l4.py`): walk Left to the pillar's right face (x 436–440), hop straight up
(A 16) when the spiky ball arrives → its top (436,126), safe; wait there until the ice ball comes back left
(x ≤ 540, heading left) while the spiky ball is far right (> 640); Right 4 drops the toad off the pillar's
right side to (439,94) (longer holds slide it down the slope); punch when the ball is ≤ 24 px (it stops at
~461 — with 34 px it stops on the slope at 465 and the chase slides the toad away); lift with Right taps
(1 on, 1 off); the lift animation takes ~30 frames before a throw registers (the ball rides up to h+35 first);
walk Left to x ≤ 441, Left+B. The throw-hop drops the toad back on the pillar top, out of the spiky ball's lap.
The toad cannot jump while carrying (A is ignored). Stack gone → 5000 points, a 0x41 husk; the pocket opens
onto the floor beyond: a second pillar at x≈330 with another spiky ball patrolling 184↔316 and a slope down at
the far left. Searching that (`reach_down_left` 190, from `L4_cp6_open`).

Route verified from power-on through the slide into the bowl: **23,590 frames, sha1 14de4426**. The
`wallhit` beam from the pillar top never caught the ball (its rank had nothing to say about the ball).

## Checkpoint 6 reproduced in the script

Two more surprises on the way to a deterministic recipe: (1) a punch at ≤20 px doesn't just stop the ice
ball, it **pulls it in and lifts it** (anim 13/11 → 17 over ~20 frames) — my "lift" B press after the punch
was actually a throw, sending the ball the wrong way; (2) throws go toward the toad's facing, and a toad
pinned against the pillar can't turn by walking, so after the carry settles it needs 4 Left frames (it slides
to 437) before Left+B. With that, `l4.py` breaks the stack at f10442 and the beam's line past pillar 2 replays
to (189,94) at **f10628** — segment 10,628 frames, hp 15, 4 lives, bookmark `L4_cp6_left2`.

The floor ends at a third pillar (x≈170); left of it a wall of urchins fills the bottom of the screen, with an
open passage above it (h > 150) where two slow yellow sparks (0xa, HP 207) drift about. The beam's endpoint
at pillar 3 is a trap (the spiky ball arrives 98 frames later) — SAFE 60 is not a guarantee. Searching the
climb over the urchins (`reach_left` 100, dh ≥ +40) from the script's own bookmark.

## Over the urchins (late evening)

Route verified from power-on through checkpoint 6: **25,222 frames, sha1 e8d523e1**, 4 lives.

Pillar 3 is the end of the bowl floor; from its top a Left+A held exactly 14 frames clears the urchin column
(at x 97 the toad is at h 100, the urchins' top) — 8 or 20 frames land in it — and the toad drops down the
far-left shaft onto a long down-right slope at (47,0). A snowman (ID 0x75, HP 47) sits above the landing
and throws a snowball (0x3d) every ~90 frames; they roll down the slope and kill an idle or a running toad
within 90 frames. Hugging the left wall at (32,15) is safe indefinitely. The beam (`reach_x` 320, SAFE 60)
is running down the slope; the pillar hop and the 14-frame jump are scripted in `l4.py`.

## Down the slope (night)

Snowball timing measured from the wall: one drops from (48,111) every 84 frames, falls ~36 frames, then rolls
down the slope at ~3 px/f and vanishes at the slope's end (x≈192, a spike pit). The beam (`reach_x` 320,
SAFE 60) found a 140-frame descent in 94 s — run, pause 4 frames, run, hop the slope's end onto a small ice
ledge (x 230–350, h 126) over spikes. A big snowman (0x33, HP 31, top hat) stands on it at 328 throwing
snowballs (0x3a) to the left; the toad slides right past it to the ledge's end at 350 and is safe there. An
icicle (0x39) hangs at (428,228) over the next ledge to the right. Punching the snowman when overlapping took
15 off it once (HP 16); every later punch missed as the toad slid away. Beam across the ledges running
(`reach` 520, from `L4_cp7_slope`).

`l4.py`: **10,873 frames** to `L4_cp7_slope` (320,126), hp 15, 4 lives; the pillar hop, the 14-frame jump
and the slope line all reproduce. Power-on verification running (`assemble_L4route14`).

## Checkpoint 7 (night)

Across the small ledges (beam, 288 f, via a shuttling platform 0x3e at h 106 under a hanging spike) to a
ledge at h 126 (x 600–657) whose right end is **checkpoint 7: a short snowball stack (0x3c at 672,150) with
79 HP**. Something off-screen to the right (an ID 0x35, HP 15, glimpsed once at (768,96)) fires fast
snowballs (0x3a) leftward at h 130/149 every ~41 frames; **each one passes through the stack for 8 damage
and flies on to hit the toad (8 damage)**. Crouching doesn't duck the h-130 ones. So the checkpoint breaks
itself in ~10 shots if the toad survives ten snowballs — the beam is on it (`wall` mode, rank pinned to
x 640). The ledge is icy and short: two settle scripts slid off its left end into the spikes.

`l4.py`: **11,163 frames** to `L4_cp7_plats` (610,126); route verified from power-on through the ledges.

## A false alarm, and the warp

The stack falls to a hand policy: walk to x 655, **crouch** (the h-149 snowballs from the unkillable snowman at
x 440 pass over a crouching toad), and **hop 2 frames** when one of the big snowman's h-130 snowballs is
36–48 px away (those hit a crouching toad). 79 → 0 in 630 frames, hp 15 kept.

Then an hour lost to a phantom: the script's regeneration died at the stack and its bookmarks looked "hundreds
of frames late" — I even wrote `rebuild_bm.py` to rebuild bookmarks from the recorded inputs and tested the
emulator's save (it is immediate; a load applies on the next step, so `load` + 1 idle step = the saved frame
exactly). The real cause: a second, redundant slope search had finished later and overwritten
`knowledge/l4s_L4_cp7_shaft.json` with a 384-frame line ending somewhere else, so the ledge line was replayed
from the wrong state. Lesson: never run two searches that write the same file name; check the log's own
frame numbers before blaming the emulator.

Past the broken stack the ledge slopes down-right onto **the falling platform (ID 0x35, HP 15) at (768,96)**:
riding it down, the **warp portal (0x22) appeared at (776,152)** when the platform reached h≈47, with a
lifetime counter in its HP byte (62 → 10 in ~50 frames) — this is the Level 4 → 6 warp. The toad slid off the
platform's right end into the wall and died; jumping on the platform from the start didn't raise it in 28
jumps. Next: ride down, wait for the portal, then jump repeatedly to bring the platform back up to it.

## LEVEL 4 DONE — the Mega Warp (2026-09-27, ~14:30)

With the slope line restored, `l4.py` breaks checkpoint 7 at **f11816** (hops 2, hp 15, 4 lives). From the
script's true state the falling platform (0x35) sinks under the toad from h 96 through the wrap; the portal
(0x22) appears at (776,152) with a countdown in its HP byte (0 after ~50 frames, but it stays); jumping on the
platform (A 10, re-centering between jumps) lifts it back up, and on the 7th jump the toad touched the portal:
**routine pointer $E50D at k 225 — warp engaged**. 156 frames later the level byte flips (254/255 during the
"MEGA WARP — ADVANCE 2 LEVELS" card) and Start-mashing lands the toad at (120,30) in **Karnath's Lair**
(internal level byte 8), hp 47, 4 lives. Screenshot `shots/l4_warp_sheet.png`. Policy `warp_platform()` in
`l4.py`; regenerating the whole Level 4 segment through the warp now.
