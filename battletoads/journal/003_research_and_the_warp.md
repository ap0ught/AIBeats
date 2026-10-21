# 003 — Research day, and the Level 1 warp (2026-09-26)

The blind rule is gone. A research pass (speedrun.com API, TASVideos submissions, feos's disassembly labels and
Lua tools) is in `knowledge/research.md`. What changed for the player:

## The map we were missing
feos's object table: 15 slots from $3C1, 35 attributes at stride $0F. Slot 0 is the toad. The columns that
matter: ID $3C1, X $3EE/$3FD (hi/lo), depth $41B, height $439, floor $475, state $4B1, **HP $51A**, X speed
$565, Anim_2 $583. Camera $87/$88. Level $10. Level-clear jingle $33 = 0x81. Timing start (autosplitter):
level 1 and $3B5 goes 5→4, "the toad hits the ground".

Checked against our own dumps: pigs (ID 0x20) have 15 HP and lose 2 per punch; the Walker (ID 0x12) has 31;
the toad has 47. Every "enemy health" byte I found blind was a timer. The one I never looked at was 32 bytes
past the last one I tried.

## The Level 1 warp, in memory
- It is an object like any other: ID 0x22 with Anim_2 = 0x55, in slot 3, world x 304, depth 72, height 208
  (the ledge). Its **HP counts down one per frame from 190 and it despawns at 0**, about 466 frames after
  control. That is the deadline, and the reason the guides say "jump up there quickly".
- The screen will not scroll until both pigs are dead. The record does both with running headbutts and is in
  the portal in about 3.5 s (210 frames). Our first pass punched: 2 HP a hit, 8 hits per pig, far too slow.
- First search wrote the portal into "enemies alive" (it has an ID and an HP) and a level-start object
  (ID 6, HP 47) too, so it fought phantoms and stood at the screen edge with one pig still alive behind it.

## Search changes
- Score = camera + x + enemy HP removed + kills − enemies alive + health − lives lost − distance to the
  portal while it exists (as if far away once it is gone) + 100,000 for a level change.
- Macros now include the TAS movement tech: tap-release-tap dash (192 speed), dash jump (A on the second
  tap), and ram (dash then B, the headbutt).
- 8-frame steps, beam 8 wide, 3 random playouts of 96 frames per move.

## Rules note
Everything in the any% record except the credits warp is legal on the board. We stay stricter: designed warps
yes; the bike-glitch level skip, the Rat Race boot, and the Terra Tubes out-of-bounds no (memory corruption,
boss-flag exploit, OOB). That costs the record route about 2 minutes on the bikes and most of Rat Race, so our
target is really "fastest clean run", with 12:29 as the yardstick.

## Measured today, the hard way (Level 1)
- **A headbutt only works from a dead stop.** Tap-release-tap-hold-B from standing kills a pig in one hit (15→0,
  hit at speed ~184). The same inputs while still moving give 4 damage. After a headbutt the toad slides ~35
  frames in that direction and nothing cancels it (holding the other way, the reverse charge, Up): it must run out.
- The toad is airborne for the first ~157 frames after control (the sky drop): no ground attacks until then. The
  run animation itself hops ($475 goes 15–30 between ground frames), and B in the air is a weak jump kick.
- The pigs stand still until ~frame 220 then walk toward the toad at ~0.4 px/frame. The screen scrolls only once
  both are dead, at ~1.5 px/frame, and only when the toad is on the right half.
- The portal (ID 0x22, Anim_2 0x55) sits at world x 304, "Y" 72, "Z" 208. Its HP counts 184→0 over the first
  210 frames; a second counter ($4FC, 239→0) then runs to its despawn at frame ~467 after control. The rock beside
  it clamps the toad's depth to ≥104 (x 270–310) and ≥89 (x 316+), on the ground and in the air alike, and no
  jump lands on it. Reaching x 304 on the ground with the portal alive does not warp. The record's toad warps
  while airborne there, about 3.5 s after landing; the exact contact rule is still open.
- Hand-scripting the fight cost ~90 minutes for nothing durable. The search now has the recipe as a macro.

## The answer (evening)
- **Jump height depends on how long A is held.** Two frames: 40 px. Eight: 53. Sixteen: 65. Twenty: 70. Thirty: 75.
  Every jump in every search and every hand test today pressed A for two frames. Measured only after reading the
  game's own code for the portal made the geometry impossible with a 41-px jump.
- The portal's touch test, from the ROM ($EEDE): on even global-timer frames, |x diff| ≤ 16, |height diff| ≤ 16,
  |depth diff| ≤ 8 against the portal at (304, depth 72, height 208). Then the warp routine engages (routine
  pointer $23/$24 = $E50D) and the level byte changes only after a wait on the global timer, up to 250 frames
  later. Every earlier detector watched the level byte inside a 60-frame window and could never see a warp.
- The rock beside the portal is a raised floor at height 208 (64 px). A toad placed on it stands there and
  warps in 8 frames. Below 208 the rock's depth clamp applies even in mid-air, which is why no 41-px jump ever
  got near. The way up is a jump with A held ~20 frames, launched from the left where depth 72-80 is standable.
- Pigs are invulnerable until they start walking (~frame 220 after control). A headbutt kills a walking pig from
  28-53 px on the same depth line, from any speed; "needs a standstill" was wrong (distance was the confound).
- Debug poke added to the bridge for these experiments only; runs remain inputs from power-on.

## Level 1 done, verified
Route: power-on → Right held → Start at 1,170 → A held → land (frame 2,074) → left pig headbutt → right pig
headbutt → sprint → A-held jump onto the rock → portal. Two replays match (sha1 93fed2d8). Timed span 2,074→2,373:
299 frames, 4.97 s. The record does this in about 3.5 s. Transition to Level 3 with Start mashed: 199 frames;
left alone it is 860 (Start held is 673: it needs presses).

## Level 3, first rat (night)
- Rats (ID 0x47) have 31 HP. A headbutt does 16 and knocks one down for 93 frames (state 64); nothing lands
  while it is down, and a punch just as it stands does 8 and is a smash that kills it 22 frames later. The
  beam's first pass punched a downed rat to 1 HP (an odd carried state) and watched it stand up with 7.
- The screen does not scroll until the first rat is dead, so Level 3's opening is: headbutt, wait beside it,
  punch on the get-up. New "finish" macro does exactly that; second search running.
- Transition Level 1 → 3 with Start mashed: 191 frames to the level, control 245 frames later (drop-in).

## Rat gauntlet done, onto the bike (2026-09-27, small hours)
- Scripted policy: headbutt / wait / headbutt for rats (a standing rat is the target, a downed one is kept at
  24-40 px); punch the drifting Green Vaders (ID 0x15) when close; seven pits learned by dying, keyed on the last
  frame on the floor (the fall itself lasts 140 frames, which fooled the first version).
- Jumps: a dash-jump from a STANDSTILL carries 89 px; a jump out of a full run only 29 (the run's speed is
  dropped in the air). So each pit is: coast to a stop, tap-release-tap-A held 30. Slow but safe.
- The bikes (ID 0x18) stand at x 1727/1743; walking onto one starts the Turbo Tunnel. Bike speed $D5 ramps 0→8
  over 235 frames; walls are ID 0x23, spawn ~250 px ahead; a crash respawns the toad at the rat section start.
- Route verified from power-on through the rats and onto the bike: sha1 7aaf3522, 6304 frames (Level 1 4.99 s;
  the rat section ~55 s against the record's ~15 s: the fights and the stop-before-each-pit are the cost).

## Turbo Tunnel, first hours
- The bike drives itself at $D5 = 8 (8 px/frame). A jump (any A press) lasts ~55 frames = ~440 px and peaks at
  z 47; hold length does not matter on the bike. A wall (ID 0x23) is cleared when A is pressed with the wall
  155-283 px ahead (measured on wall 1), but the wall object only exists in RAM ~20 px before impact. So the
  tunnel cannot be played by reaction; it is a memorized list of press positions, learned by crashing: a crash at
  x means a wall at x+19, press 220 px before it. Ramps (ID 0x25) throw the bike high (h 155) and long; walls
  right after a ramp landing need the ramp jump itself retimed. 22 walls learned in ~500 rounds so far.
- A crash respawns at the rat section start, so every crash costs a full re-ride: the learn loop runs from the
  bike bookmark, ~6 s per round.
- The course's world x is 16-bit and wraps at 65,536 part-way down (the bike is past 106,000 px by then). Two
  hours of the learner were spent "regressing" from crashes that were actually further than any before, and
  a hand-placed press pair at 43,850/44,300 was tested sixteen ways against a crash 60,000 px later. Unwrapped now.
- Tunnel, morning: crashes are now read at the frame the toad's HP hits 0 (the lives byte drops only after the
  respawn at the last checkpoint, which is what "x 41136" was). Gap deaths key their press on where the road
  ends, not where the fall ends. Past 50,000 px a third obstacle kind appears: ID 0x2B things that bounce across
  the lanes; the learner now tries holding Up or Down for a stretch once jump timings are exhausted.
