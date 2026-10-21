# 009 — Terra Tubes (Level 9)

## Opening the level (2026-09-28, after midnight)

Level 8 is verified from power-on (34,816 frames to the Terra Tubes landing). The toad lands at (44, 6) with
5 lives; an enemy (0x6d) at x ≈300 on the same floor spits sparks (0x3a, 6 px/frame leftwards) that hit a toad
anywhere on that floor within ~90 frames, crouching included — so the first move must leave the floor.
Level byte 11. Jumping is huge here (hold A: h 6 → 105).

What the notes say (`knowledge/research.md` 2.10): four checkpoints = walls broken by Krazy Kogs (gears);
skip a gear and the later ones never spawn; all four must be activated or the end object does not load, and the
camera must pass the top of the final shaft; a "visited areas" indicator at $0585. Swimming: ~3× slower than
land, A on key frames to rise, let go to sink, wall bumps kill speed, punching freezes you. Land speed 192,
jump speed 128. The RTA route (and the TAS) starts with the **start-of-level out-of-bounds: hold A+Left as the
level starts, the top of the left wall has no collision**, dropping past the first hallway and the upward
spinner — allowed under Any% (No Credits Warp), which is our ruleset now (the "skip for us" note dates from the
glitchless days). Still banned for us: Left+Right (the TAS uses it in a few places here) and anything needing
a second player.

The TAS's Terra Tubes (level byte 11, f12256–21378, 9,123 frames, 2 players): start OOB (Left, then Down+Left)
falling ~700 px to H ≈ −550, then right along that depth, a long swim up (Up+A) to H ≈ 40 at x ≈ 700 (gears
0x6b appear), then a maze of swims and walks spanning x 0–1700 and H down to −2100, a deliberate death at
f20906 and a respawn at (1531, −2136) with a broken camera, 270 frames from the end — "checkpoint activation
tricks". Summary in `logs/tas_l9_summary.txt`, screenshots `tas/all/L11_f*.png`, sheets `shots/tas_l9/`.

**The start OOB works from the drop-in frame** (`L9_drop`, the frame the toad appears at (40,112); `l8.py` now
ends its segment there, 5,076 frames): hold Left+A from that frame — the toad jumps at once (h +99), drifts left
over the wall top (x 44 → 22 by frame 45) and sinks into the water beyond it (swimming anims 98/99); holding
Left+A it sank ~1.8 px/frame, then rose again. From the landing frame the same jump goes nowhere (x stays 44).

Two beam-search fixes the tubes forced (`l4s.py`): the state key now includes whether A is still held while
airborne (before, a jump with A held merged with one released at the same spot, so the 24-frame hold needed to
clear the start wall never survived), and the toad's horizontal velocity/direction ($448) and facing ($4A2 bit
6) — the wall pins x at 44 during the first frames, so a Left-jump and a Right-jump looked identical. Water goals
(`reach_w`, `reach_down_w`, `reach_left_w`, `reach_down_left_w`) drop the "on the ground" condition. Unsolved
searches now keep their best-ranked line instead of the highest one. The spike line at H −516 (x 32–55 dies)
is what the TAS sidesteps by drifting to x ≤ 31 — a water pocket — for a dozen frames.

Sections so far (`l9chain.py`, absolute targets converted per section; `l9.py` replays them after the 24-frame
Left+A prefix): S1 184 frames to (32, −507) just above the spike line — idling there drifts the toad into the
water pocket at x 28, safe; S2 152 frames to x 186 inside the flooded tube (H ≈ −650). 366 frames from the
drop-in, on par with the TAS's two toads at that point.

Section 2 redone: the first solution (x ≥ 180, H ≤ −640) dived 70 px under the tube into a flooded chamber with a
downward current that no search could climb out of — the TAS line runs along the upper tube's water line at
H ≈ −650. A new water "band" goal (past x with |H − target| ≤ 12) reproduces it: 152 frames to (184, −646).
Lesson for the tubes: goals must pin the height band, not just a bound. (Also: never put a process-name
pattern in a PowerShell command run from Bash — the query matches and kills its own shell.)

Section 3 with the loose goal (past x 450, anywhere above H −660): 252 frames along the top of the blue tube to
(453, −586), on the ground — the TAS runs the tube's outer surfaces here too, just a ledge lower. 620 frames
from the drop-in at x 453.

Geometry lesson from a reachability map (`l9map.py` over an `explore`-mode trace, TAS trajectory overlaid) and
hand probes: past the tube (x ≈ 440–467) the TAS jumps DOWN-right into a flooded channel (surface ≈ −617 at
x 467 rising to ≈ −560 by x 530) and swims it to x ≈ 600; then the shaft at x 600–660 is a stack of pools —
each climbed with a **water jump** (A while swimming launches the toad ~45 px into the air; Up+A held ~15
frames, then swim again). Our top-route section 3 walked the pipe above that channel to a wall at x 628 with
nothing to climb — archived (`*_s3_top*`). Two more search fixes: A presses are now allowed while swimming
(the "airborne" rule blocked every first A press in water) and a `swim` action set adds Up+A.

## Following the TAS (small hours of 2026-09-28)

Guessing goals through this maze was going nowhere, so the beam got a **`follow` mode**: the TAS's player-1
position per frame (placement-anchored, from the watcher log) is the corridor; each node's progress is the index
of the nearest TAS point within 48 frames ahead of its parent's, rank = −progress + 2 × distance, goal = index
≥ i_to within 24 px. From the section-2 endpoint (TAS index 375) it reached the channel (index 700, (522, −572))
in 208 frames — 117 faster than the TAS's toads. The next follow section (700 → 1130, the pool jumps up the
shaft to the land) was climbing at once. `l9follow.py` chains follow sections at TAS indices 1130, 1500, 1900,
2300, 2700, 3100; `l9.py` replays `L9_s1 L9_s2 L9_s3g L9_s4g L9_f3 …`. Caveat for later: wherever the TAS
needed Left+Right or the second toad, the follow search will stall and that stretch needs its own route.

The channel's end is a pipe whose interior is a 28-px water band (raw h 32–60; the pipe's top plate at raw 70)
under a wall at x 628; you thread it swimming at raw 53–62. Every in-pipe state died because a shooter
(0x6d at x ≈ 388, raw 38) fires a spark along raw 61 every 104 frames at 6 px/frame, passing x 602 exactly
~52 frames after our arrival — the TAS's toads simply arrive at another phase. A beam cannot wait (waiting
states lose rank and are pruned), and the water at the pipe's mouth is only 20 px deep (no bobbing: a bob
lands on the plate). Fix: a scripted 30-frame idle right after section 1, in the water pocket at x 28
(`L9_s1wait`), then section 2 re-searched (`L9_s2b`, 132 frames), then the follow sections (`L9_s3b`, `L9_s4b`).
The follow goal now demands ≤ 16 px and the same medium as the TAS (swimming where it swims) — with 24 px it
accepted the pipe's top plate, a dead end.

Two parallel attempts at the pipe: (a) `L9_s4b` with a **forbidden box** (`L4S_FORBID=545,640,-560,-400`, the
top plate) so the beam has to wait at the mouth and thread the interior between sparks; (b) a second chain
(`l9follow2.py`: `L9_s2wait`, a 36-frame bob in place at the tube's water line where the TAS bobs too, then
`L9_s3c`, `L9_s4c`) to shift the arrival phase by ~36 frames. The spark passes x 585 at absolute frames
639 + 104k after the drop-in.

## Status at 04:00

The pipe under the wall at x 628 is still unsolved. Facts established tonight: the pipe's interior water band is
raw h 32–62 (our toad floats up to 62 inside it); the TAS's toads hover at raw 56–58 there and survive a spark
that runs along raw 61–69 every 104 frames; ours, floating at 62, is hit whenever the spark passes (it did in
every attempt, at absolute frames 639 + 104k). A beam cannot wait at the mouth (the water there is 20 px deep,
a bob lands on the top plate at raw 70), a forbidden box over the plate left the beam waiting at x 543 for
200 steps without a surviving entry, a 36-frame bob-wait upstream broke section 3, and jump-spamming on the
plate is safe but stepping back off it never worked. The TAS's splash at x 640 puts the surface at raw 66.
A lower route exists (fall out of the band at the mouth onto a dry floor at H −746, walk right to water at
x 851) but its reachable region (−650..−820) shows no connection to the shaft so far. Last shot running: a
precise beam (2-frame macros, width 1,500, plate forbidden). If it fails, the level needs a different route
past this point — the human Any% route's own path through here (no second toad) is the thing to research next.

## The pipe, understood (05:00)

The hit at x 597 is a spark from the shooter 0x6d at x ≈ 375–416 (raw 38), spawned at x 399 about 14 frames
after the toad passes x 540 (it also fires every 104 frames while the toad stays in range), flying right at
6 px/frame along raw 61 and overtaking a swimming toad (1.5 px/frame) at x ≈ 597 whatever the absolute time —
every chain got hit 44–49 frames after its section root. Phase shifts upstream cannot help (the pocket wait
is absorbed by section 2's descent; a bob-wait at x 22 shifts the chain but the shooter is triggered by our own
approach). In the TAS the second toad absorbs that spark (their log shows no raw-61 spark left near x 600).
Local dodging is impossible: the spark's hitbox covers a toad at raw 45–70; below raw 32 the toad falls out
of the band; a bob from the mouth water always lands on the top plate (it extends left to x ≤ 516 above the
whole mouth), and a jumping toad on the plate is safe but can never re-enter the water. Remaining options:
take the hit (search with `L4S_HPMIN=23`, running), or find another route past x 628 (the lower dry floor at
H −746 leads to water at x 851 — unexplored beyond).

**Verdict on the pipe (05:40):** two-player only. Everything local was tried — punching the spark, crouching,
extra bobs, sinking under it (it hits even at raw 30), taking the hit (the knockback lands the toad on the
plate, a dead end). But the reachability map of the lower pocket (fall out of the pipe's band at the mouth,
dry floor at H −746, x 580–720) sits directly under the TAS's own later path: at index ~1700 the TAS comes
down to (720, −665) after the cog section and swims right along H −580 to x 1130. If the pocket connects up
those 50 px, we join the TAS route there and skip the shaft, the land and the first cog section outright.
Follow search launched from the pocket (indices 1650 → 1800) plus a 150-step exploration of the pocket.

**Sources (06:15):** TAS #6758 (2P warpless) confirms the two-toad trick: "one toad dies from a laser enemy while
the other continues through out-of-bounds water" — our spark is that laser. TAS #5093 (FODA, 1 player, warpless,
FCEUX 2.2.3) is the single-player reference: "Sonikkustar's found to go below the tubes right to the checkpoint,
then DylaX's trick to pass through the gear checkpoint" — "below the tubes" is our lower pocket. Movie
downloaded to `tas/` (.fm2); exploring onward from the pocket's water at x 851.

## The single-player line through the pipe (07:00)

FODA's 1-player TAS (#5093) plays in sync on FCEUX 2.6.6 (`tas/watch_fceux.lua`, log `tas/watch_1p_log.txt`,
screenshots `tas/1p/`, sheets `shots/tas1p_l9/`). Its Terra Tubes is the same out-of-bounds line and it threads
the pipe without a scratch: when the row-61 spark spawns (toad at x 490) it dives in the channel's deep end to
raw 23–29 at x 505 while the spark passes overhead, rises to the pipe's bottom (raw 34–36 at x 514–546), one
bob at x 549, hovers at raw 57, sinks to raw 38–44 through x 600–621 (under the spark row, above the row-29
sparks), and water-jumps at x 624 into the first pool — all before the next spark, 104 frames later. The
follow mode can now track this log (`L4S_TASLOG=tas/watch_1p_log.txt`); a 2-frame-macro follow search runs
from the channel (`L9_s3cut`, index ~528) to the pool (index 720), and `l9follow.py` continues along the
1P path in 300-index sections after it.

**07:50.** Our own spark schedule at the channel (from `L9_s3cut`, x 472 raw 14): row-29 sparks pass x ~500 at
frames 16, 120, 164; row-61 sparks pass x 597 at frames 83 and 187. A water bob is a slow +30 lift over ~30
frames (vertical state byte $484 now in the beam's key), so a toad cannot hold the 7-px safe band (raw 38–44)
for long; every scripted plan and the follow search from this arrival die. Since the phases depend on when the
shooters were loaded, the other chains' arrivals (f, g, h) are being tried in parallel from their channel cuts.

**08:40.** The screenshots finally explain the geometry: the "band" is the inside of the blue water tube (raw
30–62), the "plate" its top surface (raw 70), the spark flies inside the tube along its ceiling, and the tube is
entered only from the channel low down (raw 25–36 at x 505–515), which is what the 1P TAS does. Our arrivals
sit on the tube's top instead. The channel below is crossed by row-29 sparks every few dozen frames and the
row-61 shooter fires ~7–15 frames after the toad crosses x ≈ 490; every scripted plan from our channel states
dies within 30 frames. Last systematic attempt: explore-mode searches (no progress pressure, tube top
forbidden, 2-frame macros) from both channel cuts with the goal "past the wall (x ≥ 640, above H −565)".
Explore-mode searches from both channel cuts: unsolved (nothing past the wall). Running now: a follow search on
the 1-player path starting back at the tube's water line (`L9_q1`, indices 345 → 720, 2-frame macros), so the
beam picks its own timing into the channel rather than inheriting the 2-player line's dive.

## THROUGH THE PIPE (10:10)

Single player, no damage, scripted from the channel cut (`L9_s3cut`, x 472 raw 14): A on frames 0, 1 and 12
(the lift clears the row-29 spark at frame 17 with 4 px to spare), Right/Left pulses to hold x ≈ 507 where the
toad sinks instead of hovering, and the moment raw h reaches 28 (frame ~66, the periodic row-61 spark passing
overhead — sparks spawn every 104 frames, at 49 + 104n after this root, not on approach) one Right+A: the lift
carries the toad up into the tube's buoyant bottom band at x 511, it rides right, a second bob once past x 546
at raw ≤ 36 (peaks under the ceiling instead of on the top plate), sink to ~51 by x 624, and a 12-frame
Right+A water-jump at x 626 clears the wall: x 641 at raw 68, 167 frames. Facts that made it work: the toad's
hitbox is ~32 px tall (a raw-61 spark hits feet ≥ 29; the raw-29 sparks hit feet ≤ 37), the tube interior is
raw 30–62 with buoyancy only from x ≥ 511, the channel's updraft holds a toad at raw ~55 at x < 490 but lets it
sink at x ≈ 505 (where it also falls out below raw ~27 unless lifted), and a water bob is a +23–30 lift spread
over 30 frames. Section `L9_pipe` (`knowledge/l4s_L9_pipe.json`); the chain is now
`L9_s1 L9_s1wait L9_s2b L9_s3cut L9_pipe`.

## Gear 1 (Krazy Kog) — 11:40

After the pipe the follow chain ran two clean sections (`L9_p2` 260 frames through the pools to the upper land,
then a section down to x 865) and stalled at the wall at x 744, H −138: the gear that should smash it never
moved. In the 1P TAS the gear (0x6b, parked at (736, raw 160) = 90 px above the upper land) starts rolling the
frame it is loaded while the toad is within ~70 px; the TAS toad even waits 60 frames at x 801 for that. Our
toad loaded it from x 848 (too far) and it stays parked forever. The progress byte $585 matches the TAS exactly
(22 → 23 at the upper land), so it is not a checkpoint issue. Fix, scripted section `L9_gear` (89 frames from
the upper-land root): walk right to x 760 and hop (A 8 frames every 40) — the gear starts at frame 89 with the
toad at x 766. The gear then runs its track: down 64, right to x 832, up 64, right to x 1024, down ~300, left
to the wall at x 744. The follow chain restarted behind it (`L9_p3` 1P indices 1085 → 1385, …). Follow-mode fix
too: equal-distance ties now pick the LATEST TAS index, so standing where the TAS stands still counts as
progress (before, a waiting TAS stalled the beam).

Follow chain after the gear: `L9_p3` 244 f (to the wall at 760), `L9_p4` 304 f (gear smashes the wall 128 f after
arrival; down 512 px), `L9_p5` 412 f (TAS: 300) — our gear runs ~70 frames behind the TAS's relative to the
toad (we triggered it later), so the toad waits for it on the H −490 ledge while it rolls on to wall 2 at
x 1116; wait-to-catch-up lines looked like a stall for 50 steps but the beam kept one waiting node alive and
finished. Optimization note: trigger gear 1 earlier (the TAS triggers at 1P index 1083) to get those ~110
frames back.

## Gear 2 / checkpoint 2 (afternoon)

Sections 6–9 ran at or under the TAS's pace (284, 268, 368, 244 frames). Section 10 died: gear 2 runs ~41 frames
behind the TAS's relative to the toad, and every beam node crowded forward to x 1402–1421 (the most TAS-like
spot) where the gear, descending the column at x 1408 to smash the wall at x 1436, crushed them all. Fix, in
three parts: follow search to the waiting floor (`L9_p10a`, 52 f, to (1402, −970)); a scripted section
`L9_p10w` (194 f): hold at x 1388 (the wall's left end), and when the gear on its raw-32 track reaches x 1400,
alternate Down/Right every frame — the crouch-walk the TAS uses — so the toad passes under the descending gear
and under the wall (a crouching toad fits under it) as the gear smashes it; then the follow search again
(`L9_p10b`, 1P indices 3370 → 3685). Knife-edge: trigger x 1398/1402/1404 all get hit, only 1400 works.
`l9follow.py` now supports scripted WAIT rows (idle, optionally holding an x, until an object is gone) and its
row list is explicit (p3…p9, p10a, p10w, p10b, q0…q19).

Evening: sections q0–q6 at the TAS's pace (300, 308, 300, 316, 308, 296, 284), checkpoint 3 passed in q5 and
gear 3 started on approach in phase with the TAS. q7 died the "crowding" way again: gear 3 climbs a column at
x 192 and rolls left along the toad's path; the TAS toad waits 44 frames at x 211 beside the column and
follows behind the gear, while every beam node ran ahead of it. Split into `L9_q7a` (follow to the column, 152
f), a condition wait `L9_q7w` (hold x 211 until the gear rolls left past x 186 on its raw-192 track: 56 f) and
`L9_q7b` (follow behind it, 328 f). The driver now has WAITC rows (hold an x until a RAM condition holds).
General lesson: wherever the TAS waits for a moving hazard, the follow beam needs a scripted wait — a beam that
ranks progress will always crowd forward.

Planned ahead (driver rows): gear 4 — the TAS toad waits 110 frames at x 488 while the gear dips down its column
at x 288 and climbs back (TAS resumes when the gear is at raw 178), then swims left, dives under the gear as it
rolls right along raw 192 (x ≈ 405–418 at 1P index ~7375), and follows it to the wall at x 504 → rows
`L9_q11a` (to x 488), `L9_q11w` (hold 488 until the gear is at x 286–292, raw ≥ 178), `L9_q11b` (7308 → 7585).
The level end: the 1P TAS dies on the last spikes at index 8940 (x 1491, H −1953) and reaches the end trigger
while dying ($585 26 → 27 at index 8949; "the game doesn't check if you're alive when you reach the end");
the level byte changes 340 frames later. `l4s.py` got `L4S_ENDCP` (goal = $585 ≥ n) and `L4S_LIVESOK`
(losing a life doesn't prune), used with `L4S_HPMIN=0` for the last row `L9_end` (8785 → 8949).
- r0: 608 f vs TAS 300 (waited out enemy 0x72's timing at x ~790; picked up a 1-up) — optimization target

## Terra Tubes done (2026-09-28, 16:10)

All sections solved; `l9.py` (default section list = the full chain) runs from `L9_drop` through the end
trigger, waits for the level byte to leave 11 (340 frames after the trigger), Starts through the card and waits
for the Rat Race placement at (88, 158): **10,219 frames**, 5 lives (6 after a 1-up, minus the planned death at
the end), `logs/pbeam_L9a.json`, bookmarks `L10_load`, `L10_start`. Section times (frames): s1 184, s1wait 30,
s2b 132, s3cut 177, pipe 168, p2 260, gear 89, p3 244, p4 304, p5 424, p6 284, p7 268, p8 368, p9 244,
p10a 52 + p10w 194 + p10b 292, q0–q6 300/308/300/316/308/296/284, q7a 152 + q7w 56 + q7b 328, q8 328, q9 272,
q10 284, q11a 4 + q11w 125 + q11b 280, r0 608, r1 472, r2 292, r3 312, end 156. The 1P TAS: 9,289 frames
from placement to the level change; ours ~9,660 for the same span. Fat spots: gear 1 triggered late (~110 f),
r0/r1 waiting on enemy timing (~480 f).
Power-on verification launched (`logs/assemble_L9route.txt`).
**Verified from power-on: 44,999 frames to the Rat Race start, RAM sha1 21133bb7 on both replays, toad at
(88, 158), hp 47, 5 lives** (`logs/assemble_L9route.txt`; route segments L1 L1to3 L3rat1 L3a L3mount L3t L4a
L6a L8a L9a). Run clock (from the Level 1 landing, frame 2074): 42,925 frames = 11:54 at the start of Level 10.
