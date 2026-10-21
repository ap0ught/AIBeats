# 008 — Intruder Excluder (Level 8)

## Level 6 verified, Level 8 opened (2026-09-27, evening)

The final Level 6 segment (2,660 frames, `l6.py`) replays from power-on: 29,704 frames to the Level 8 spawn,
RAM sha1 359e7790 on both replays, 4 lives, full health. Token mark "L8 start" written.

First look from `L8_start`: the toad spawns at (128, 94) on a pink floor spanning x 56–244; a pink platform
above at h 158 (x ≈ 46–223, open on the right), a cyan floor at h 222 with an orange block sliding along it
(object 0x4a, x 59↔199 at 1 px/frame, period ≈ 280 frames), a flying enemy 0x50 patrolling x 127–192 at h
168–175 that spits two sparks (0x3a, ±4 px/frame at h 180) every ≈130 frames, and the pipe 0x1c on the right
wall at (248, 116). **Heights go UP with h** (h 94 floor, 158 platform, 222 next floor). A jump raises h, not z
(z is just 8 while airborne): hold-32 arc = 57 frames, +76 px; hold-8 = 40 frames, +54 px. Under the h-158
platform the jump is capped at h 128 (the toad is 30 px tall for ceilings). Sparks at h 180 hit a toad whose
h ≥ ~145. Pressing B within ~21 px of the pipe grabs it (state bit 32 set; B then swings it overhead, anim
38/40) — the TAS never takes it, so neither will we unless an enemy forces it.

## What the TAS does here — and what we may copy

Re-ran BizHawk 2.3.2 with the TAS movie and a Level-8 watcher (`tas/watch7.lua`: RAM, objects, both players'
inputs, a screenshot every 20 frames → `tas/watch7_log.txt`, `tas/l8/`; at 800 % speed the whole thing took
under two minutes). Level 8 in the TAS spans f9580–f12236 (2,656 frames). Its opening is **banned for us**:
both players hold Left+Right, which forces the camera to scroll up by itself (camy 4028 → ~2200 at 3 px/frame
while the toads stand still), the mid-level checkpoint (sparkles 0x30) activates when the camera reaches it,
the toads drop off the bottom and respawn at that checkpoint — `knowledge/research.md` already lists
"L8 L+R camera scroll + death respawn" as a TAS-only glitch, and L+R is impossible on a stock controller.
So we climb the whole tower. Legal facts from the TAS's second half (f10284 → f11300, 2,116 px in 1,016 frames):

- Height is world-relative mod 256 (unwrap by continuity as in Level 6); the camera follows the toad
  (camy drops 1 per px climbed: 4028 at the bottom, ~65 at the boss arena → the tower is ≈3,960 px tall).
- Floors sit 64 px apart. The TAS climbs a floor per jump: hold A ~10–13 frames, the apex reaches the next
  floor's edge and **the platform snaps the toad up by as much as 10 px** at the apex (h 116 → 126 in one
  frame, z 8 → 0), then it jumps again the very next frame: ≈17 frames per floor when the geometry allows.
- Orange blocks 0x4a are the moving holes in the floors ("moving holes in platforms with electricity"); the
  TAS goes up through one with |Δx| ≈ 6 from its centre ("through the very edge while the electricity is on").
- Moving platforms 0x36 (elevators, ~4 px/frame, oscillating), electric fields 0x0a sliding along floors
  (hp field 207), fliers 0x50 with sparks 0x3a, other objects 0x51–0x59 (enemies/shots) and 0x7d = Robo-Manus.
- Boss (f11300–f11920, ≈620 frames): "run forward and repeatedly down-smash" from the right side of the arena,
  past where the bullets spawn, then a ram attack knocks him off the stage; level ends 316 frames later.

Plan: beam search (`l4s.py`, new `climb` mode: rank = height, goal = landed ≥ N px higher; reduced action set
via `L4S_ACTS=climb`) in sections of ~600 px from `L8_start`; then script `l8.py` from the section jsons.

## First section climbed (later that evening)

Section 1 (`L8_p1` → `knowledge/l4s_L8_p1.json`): 608 px up in 560 frames, no damage, found by the sharded beam
(`l4sp.py`, 3 emulators, 600 wide, 4-frame macros, rank = height, 139 steps, 18 min). The single-emulator
`l4s.py` on the same section runs ~1.5× slower. That pace is 1.09 px/frame, about half the TAS's 2.08 px/frame
in the upper half of the tower — the contact sheet (`shots/l8view_L8_p1.png`, made by `l8view.py`) shows waits
and one 37-px drop, so either the lower tower's moving holes force waits or the height-only rank prunes the
fast lines. Owner's rule: finish first, optimize later — noted as a fat spot (~1,000 frames over the level).
Two chains run in the background: `l8climb.py p l4sp.py` and `l8climb.py c l4s.py`, 600 px per section.

Sections 2–4 (p chain): 592, 516, 464 frames; after four sections the toad is at H 2590 (2,496 px up) in 2,140
frames, full health. Two lessons: (1) every search root is its bookmark's saved state **plus two idle frames**
(`load` + one step already advances a frame here), so `l8.py` records two idle frames at each section boundary
— with one, section 2 desynced and the toad died; (2) the sharded search hung once in section 5 (two workers
burning CPU for 20 minutes without finishing a step, right after a rebalancing import) — killed and restarted;
`l4sp.py` now prints the rebalancing cost. Width 1,200 vs 600 on section 1 gave the identical 528-frame line, so
the beam is not width-limited; the slow pace is the level's (or the rank's), to revisit in optimization.

## The top of the tower and Robo-Manus (night)

Seven sections, two chains, both reach the arena floor (world H 4126, raw h 30) in 3,104 frames (`L8_c1`..`L8_c7`,
replayed by `l8.py` → bookmark `L8_top`; the p chain lands 2 frames later). The arena: the toad drops in at x 116,
a 160-frame arrival animation (toad anim 50, no control) while Robo-Manus (object 0x7d) descends from (240,192)
to his spot at (232, 30); the camera clamps at camy 12. He stands ~130 frames after landing, then jumps (h up to
126, ~70 frames) and shoots — a spark hit the idle toad at x 128 after ~130 frames (−16 hp), and standing under
him when he comes down is a crush.

**Attacks.** Double-tap Right = run (3 px/frame; a plain hold only walks at 1.5). B while running far from him =
running kick (anim 35, no contact); B while still at full speed next to him = the ram (anim 49, state 128: grabs
and carries him to the right wall — the TAS's finisher). B after the run has ended, standing next to him, gives one
of several attacks and *which one is RNG*: punch (anims 24/28), kick (31/30) — both knock him away to x ≈200,
h ≈90, after which he hops around and the fight turns chaotic — or **the smash (anims 38 → 87, toad state 128 at
contact, +9 frames)**, which leaves him in place. That is what the TAS "manipulated RNG to ensure": 21 smashes
at 2,000 points each and a ram at the end. **The score is the hit counter**: digits at $5F4–$5F9 (158000 on
arrival → 160000 after one smash; the kill adds 10,000). No enemy health bar exists in RAM's HUD.

Even a clean smash launches him (h 43–81) if it lands ~130 frames after he settled — right when his own jump
starts — and he came down on the toad (hp 47 → 0 in 45 frames). The TAS hit him 113 frames after his landing and
he never moved again for 20 hits. Our toad starts 97 px away instead of the TAS's 32, so the first hit is late.
Hand-scripting this is a losing game; the beam now has a `boss` mode: rank = score (more smashes first) then
distance to him, state buckets keyed by score too, goal = 0x7d gone. Two searches launched from `L8_arena`
(= `L8_top` + 160 idle frames), widths 600 and 300.

## Robo-Manus falls (late night)

The score-ranked beam (width 300, 4-frame macros, full action set) killed him in **1,092 frames** from `L8_arena`
(272 steps, 31 minutes): 21 smashes, score 158000 → 210000, an extra life on the way (5 lives now), no damage.
The width-600 twin was slower per step and still running. The level byte leaves 7 some 440 frames after the kill;
Terra Tubes (level byte 11) then takes ~180 frames to load and drops the toad in at (40,112), landing at h 6
(x 44) — an enemy 0x6d at x ≈312 spits a spark (0x3a, 6 px/frame leftwards) that hits an idle toad ~110 frames
after the landing, so the Level 9 script has to move at once. `l8.py` now runs the whole level: 7 climb sections,
160 frames of arrival, the fight, the wait, Start through the card, and stops at the landing (`L9_start`) —
**4,886 frames + the load** from the Level 8 spawn; `logs/pbeam_L8a.json` written, power-on verification
launched (`logs/assemble_L8route.txt`). Fat spots for later: the climb (~1,000 frames over the TAS's pace) and
the fight (~1,092 vs. a plausible ~700 with a stun-locked smash chain).

**Verified from power-on: 34,816 frames to the Terra Tubes landing, RAM sha1 427d0410 on both replays, 5 lives,
full health** (`logs/assemble_L8route.txt`). Level 8 closed; on to Terra Tubes (journal 009).
