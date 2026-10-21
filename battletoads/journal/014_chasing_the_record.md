# 014 — Chasing the record: where the 5½ minutes go (2026-09-30)

The owner watched the 18:04 WIP and asked me to compare against the world record and fix wherever we lose real time.

## The comparison
jay_cee's 12:29.250 (youtube A7czTlY7OI0): no splits on speedrun.com, so I read the video in the browser pane —
drew frames into a canvas (the YouTube player's MSE blob is same-origin, pixels readable), found the black transition
blips, and converted video time to run time (run = video − 20.69 s, constant). Our video measured the same way
(ffmpeg signalstats on the game area). Per level, seconds, ours vs WR:
L1 4.8/4.3 · **L3 203.6/43** · **L4 202.5/85.4** · L6 44.3/32.1 · L8 84.5/88.0 · L9 170.0/161.9 · L10 38.2/35.8 ·
L11 123.3/113.6 · **L12 179.1/143.3** · L13 33.9/41.8. The differences add to the full 334.8 s.

## Turbo Tunnel skip — DONE (−128.6 s)
TAS #5093's RAM (FCEUX dump every frame, `tas/ram_skip_1p.txt`) and the object loader disassembly (bank 3 $D2C0;
`tools/dis6502.py`) explain it: entries are 11 bytes [id, trigger hi, trigger lo, ?, x lo, x hi, y, ?, h, ?, flags];
id $FF = jump, $FE = end; an entry fires when camera X ≥ trigger. The respawn loads $B7/$B8 from $E5/$E6, the saved
checkpoint pointer — which is $0000 until the first checkpoint. So: mount the bike, tap Left+Up / nothing (the bike
rolls BACK to x≈1618 in the upper lane), Left+Down into the gap between the lanes before the checkpoint saves → die →
respawn with the list pointer at $000B (the global timer is the "id"). When $0B hits $FF the entry is a jump into
page 3 ($037F); the reader then walks the object tables 11 bytes per frame; at $0403 (slot 6's x) it reads $7F with
a passing trigger → the level-end object; the level ends 128 frames later. The TAS's Up+Down at the end is cosmetic.
Our state after `L3_bikes_seen` matches the TAS's closely: its approach inputs with a 9-frame run-in reproduce the
corruption, and its post-respawn inputs shifted by 1 frame spawn $7F at the same 288 frames. `l3skip.py` →
`logs/pbeam_L3skip.json` (598 frames vs 8,326 for the ride), bookmark `L3skip_end`. Costs a life (lives 2 at L4).

## Level intros — ~20 s of free time
Levels 3, 4, 9, 10, 11 and 12 each sat 229 frames between the level byte changing and the toad appearing; the TAS
takes 24 (a button press on the intro page skips it). Mashing B from `L3skip_end` places the L4 toad 232 frames
sooner, and the old L4 inputs replay identically afterwards.

## RNG carries over — later levels need re-fitting
Full-run check with the skip (`skiprun`): L4 and L6 sync, L8 desyncs (first object difference at L8 input 1,385, toad
at 3,316; died → game over). Diff at the L8 entry: RNG $25–$28, lives, score. The RNG step (bank 0 $8743 etc.) is
A=$25^$28+$27→$26; ROL $27 − $28→$27; ^$26→$25 — and $28 is INCremented inside the idle busy-wait (bank 3 $8578), so
it depends on each frame's CPU load: inputs change it, and it can't be steered to an old value. Consequence: optimise
in order (L3 → L4 → …) and re-fit the downstream levels once, on the new RNG.

## Level 4 on the TAS's line (2026-09-30, evening)
TAS #5093's Level 4 inputs replay frame-exactly from our placement (`L4_skip_placed`, intro mashed) until its first
Left+Right at its frame 1,461 - the walk-plane trick that stops the ice block for the pickup. A legal pickup: Right
x20, idle x26, B (`knowledge/l4_pick53.json`, 53 frames vs the TAS's 60). From there the follow search
(`L4S_FOLLOW=1512,1830`, goal `$585 >= 4`) carried the block down the shaft and broke barrier 4 in 432 frames;
`reach 633 -21` crossed the spike pit onto the ledge (100 frames). **Checkpoint 4 at 1,994 frames from the tunnel
end vs 6,190 on the old route (-70 s).** `l4chain.py` rebuilds it; bookmarks `L4n_cp4`, `L4n_ledge5`.
Checkpoint 5 stalled: the TAS kills the x-244 snowman with an airborne kick (B at frame 1,493, anim 35, lands the
hit at (272,160)); 1,500 random legal jump/kick variants and dense scans of standing punches from our line never
register a hit on it (the old route killed the same snowman with a standing Left+B at (263,158), anim 69 -> 25,
after a run-jump-brake). Diffs in its slot tables vs the TAS: $4FC/$50B (its throw timer phase) - we arrive while
it is mid-throw. Parked; the splice instead: `l4tail.py` runs the OLD policy's closed-loop code from the ledge on
the new state (raw old inputs die after 196 frames - different x). Old cp4->warp = 6,259 frames vs TAS 2,279 to
cp7: the big remaining Level 4 loss is cp5->cp6 (old 3,286 frames vs TAS 718).

## Level 3 gauntlet
Intro mash saves 214 frames (`pbeam_L13fast`: placement at 203 instead of 417; the old rat/pit inputs then
replay exactly to the bikes, `L3_bikes_fast`, and the tunnel skip still works from it, 0x7F one frame earlier).
TAS #5093's gauntlet inputs replay from the fast placement until its Left+Right+A running jump at 13,920
(x 678). Our old route reaches x 678 at 900 frames vs the TAS's 765, then loses ~1,000 more frames to its
"stop, wait beside the rat, headbutt twice" recipe vs the TAS's one-hit-and-run (2,400 vs 932 to x 900). The
re-sync search can't rejoin the TAS (the banned jump gives it a speed we can't reproduce in place); the follow
search stalls at the x-900 rat. Parked at -2 s; the old gauntlet stays for now.

## RNG
Confirmed empirically: $25-$28 change every frame AND with the buttons held (Select, B, A, Right each give a
different sequence from the same state), so any frame-count change upstream re-rolls every later level. Re-fit
tooling: `selfpath.py` writes our old segment's trajectory in the follow-log format (tas/self_L8a.txt etc.) so
`l4s.py follow` can chase our own old line on the new RNG.

## Level 3 gauntlet, continued (2026-10-01, ~03:00)
The pit at x ~1230 is not the problem: our toad hit "a wall" at x 1263 in every jump because the CAMERA was not
scrolling - the rat that spawns at x 1128 (behind the toad once it reaches 1229) is alive on screen, and the 3D
levels only scroll right with no live enemy on screen (research.md). The TAS turns around at 1227, kills that
rat (150 frames), then dash-jumps the pit. Dash-jump recipe confirmed: tap Right, 1 frame gap, Right+A held - the
toad is at speed 192 from the first frame (a plain Right+A ramps to a 128 cap; jumping out of a running sprint
also drops to 128). Sections so far: `l3_rat827.json` (324 f), `l3_f2a.json` (268 f, to x 1167); next the
rat-1128 kill from `L3n_pit2`, then the jump (`knowledge/l3_f2b.json` when found), rat at 1432, the bikes.
Level 4: `L4n_cp5` = 2,884 f from the tunnel end (old 7,241). cp5->cp6 cannot follow the TAS (its descent uses the
banned walk-plane shift to fall through the h-94 floor); the old logic (`l4tail2.py`, exec of l4.run's source from
"desc =") carries to "on platform 1" (483 f after cp5) and then its open-loop platform-2 hop misses - being
re-searched (`l4s.py n2_L4_cp6_p1_past 410 30 400 reach`). The 255-HP cp6 stack is the real cost (old route
grinds it 16 hp per ice-ball bounce, ~1,300 f); the TAS breaks it with a carried-block throw (frames 18330-18426).

## Status 2026-10-01 ~00:10
Level 3 gauntlet DONE on the TAS's line: `l3chain.py` = 2,847 f from `L1route_end` to the bikes (old 3,894):
r1 324 f, f2a 268, r2 388 (rat 1128 - the first kill ended in an uncontrollable rebound slide into the pit at
~1,108; `L4S_GOALSTILL` = goal must be standing still), f2b 114 (dash-jump), r3 655, f4 120 (x 1678, sprinting).
The tunnel skip must be re-timed from this arrival: depth 218 + 12-frame run-in + the TAS roll-back taps corrupt
the pointer for dive frames nleft 32-42, but the TAS's post-respawn inputs no longer spawn 0x7F (the walk through
the object tables starts at $03xx with xx = $0C when $0B wraps, so it depends on the global timers at the respawn,
and the 0x7F it reads is a death particle's x). Running an ENDOBJ=7F beam search from each respawn state
(`l3skipn2.py`). Level 4 chain: cp5 2,884 f; after cp5 the legal line is the old one re-fitted piece by piece:
corner/ball 405, platform hops 426 (closed-loop, `l4_p2hop.json`), pillar top 236, past the spiky ball (old
section replays), lower ledge 52, ledge 3 100, bowl top 100, down to the ice ball 56, pickup 8; searching the
throw that makes the ball ricochet between pillar and stack (TAS: 255 hp in 135 f).

## Level 4 DONE on the new route (2026-10-01 ~01:40)
`l4chain.py` = **7,045 frames from the tunnel end to Karnath's Lair (old 12,450, -90 s)**. After cp6 the old
route's geometry gave the search goals: the stack dies from the pillar top (stand x 430, face RIGHT, B - the ball
ricochets in the 44-px gap, 255 hp in 180 f, found by brute force after the beam could not see 150 frames ahead),
then reach_left onto the left ledge over the spiky V-dip (cp 6 ticks there), the shaft to (46,1), the slope to
(322,126), the ledges to 611, and the OLD closed-loop `l4.cp7_stack` + `warp_platform` run unchanged from there
(barrier 7 at +664, warp at +1,029, Karnath's Lair at +1,299). Lesson of the night: the beam search is great at
one geometric goal at a time (50-250 frames); chain it with the old closed-loop policies for the long waits.
Verification `newrun1` (L1 L13fast L3skip L4n + old L6a..L13a) running to find where the RNG change breaks the
later levels.

## The 2-frame lesson (2026-10-01 ~02:30)
`newrun1`/`newrun2` (power-on verifications with the new Level 4) died 2,273 frames into Level 4. Not RNG: the
chain's root bookmark `L3skip_end` matched the replay at the segment boundary in every byte except $25-$28 (and
the chain reproduced on the replay-exact state too) - the difference was that the intro mash placed the toad
2 frames sooner on the replay state, so the recorded input list ran 2 frames early against the game. Rule: build a
segment's input list from a state reached by INPUT REPLAY from power-on (`L3skip_end_r`, saved by replaying
logs/newrun2.inputs.txt to the boundary), never from a savestate taken inside a tool run. `l4chain.py` takes
`L4CHAIN_ROOT`/`L4CHAIN_PREFIX`; pbeam_L4n is now 7,043 f from `L3skip_end_r`.

## PAUSED 2026-10-01 ~04:30 (owner's call)
State: `newrun3` verified from power-on to the Level 8 entry (frame 16,500 vs 26,975 in the WIP) = L1 L1to3
L3rat1 L3a L3skip L4n, sha1 840eeeb6 for the whole list (later levels die on the new RNG). Level 8 re-fit: climb
section r1 solved (536 f, `knowledge/l4s_L8_r1.json`, `states/L8_r1_solved.State`); section r2 died when one of
the three l4sp.py emulator workers crashed (EOFError), so the chain stopped.
RESUME: `L4S_HPMIN=15 L4S_WORKERS=3 python l8climb.py r l4sp.py 2 7 600` (it copies L8_r1_solved -> L8_r2 and
goes on), then `python l8refit.py` (saves L8r_arena), `L4S_LVL=7 python l4s.py L8r_arena 0 0 300 boss`,
`python l8refit.py` again (writes logs/pbeam_L8n.json), then verify `assemble.py ... L4n L8n` and build the
Level 9 root (replay-exact) for `l9follow.py` (its old json sections are archived in knowledge/old_route/).
Parked: the new Level 3 gauntlet (`pbeam_L3n`, -14 s) until its tunnel skip is re-timed; Level 12 and 13 re-fits
will need the RNG-sensitive parts (faces, the queen) re-searched.

## 2026-10-01 afternoon: watching the record frame by frame (again)
Resumed. Video panel rebuilt meanwhile (see below). Then upstream first, because any change upstream re-rolls the
RNG for every level after it.

**The spike pit damage boost (Level 4, after checkpoint 5).** The record's runner lies at the floor's edge, then
stands IN the spikes and falls through them. It is not the "hold Down" spike rule (crouch-sliding into the
urchins at x 192 kills, Down held or not): the toad is lying because the shaft's ice ball knocked it down, and
the knockdown's invulnerability (about 160 frames from the hit) lets it walk into the spikes and fall through.
Recipe (scan over where to stand): tap-walk to x 187-188, the ball hits at frame 54-55 after `L4r_edge`, hold
Right; the toad gets up at ~+130, steps off at 192, falls through and comes out on ledge 3 at (576,222) with
hp 31 - 231 frames after the edge (`knowledge/l4_boost.json`, bookmark `L4r_l3b`). Standing at 182-185 dies
(invulnerability runs out 47-58 px down); 189+ walks into the spikes before the ball arrives. This replaces the
ball dodge, both floating platforms, the pillar top, the upper and lower ledges: checkpoint 5 -> ledge 3 in ~385
frames instead of 1,629.
Other findings on the way: a hanging spike at x 512 scrapes a standing rider off platform 2 (that was the
"wall" every dash-jump died on); the column left of the ledges is solid spikes (no straight drop from platform
2); the first room of Level 6 is where we lose ~4 s to the record, the warp room ~3 s (the runner gets on the
snake's head early; a toad on the floor is NOT lifted by the head, and my scripted head-mount never landed).
**Level 3 skip from the new gauntlet**: arriving in exactly the old position/speed/timers is not enough - the
skip also needs five of the toad's sub-pixel/velocity bytes ($448 $457 $466 $4C0 $4CF) equal to the old run's
(debug pokes on a snapshot, leave-one-out). The earlier ENDOBJ beam died at 56 frames only because the garbage
walk zeroes the toad's hp; rerunning it with HPMIN=0/LIVESOK.
**Video**: `render_overlay.py` now draws a run timer (starts at the landing), the record's time, the split
delta after each level, a WR-vs-AI race bar by level, and "THIS PART COST n TOKENS TO WORK OUT: <why>" from
`knowledge/token_reasons.json`; `video_text2.py` builds events/captions/tokens for any route from its trace.

## 2026-10-02 — Level 4: the spike-pit damage boost works; the object loader decoded; the lift

**The boost (record's run 95.3–99.3).** At the pit's edge after checkpoint 5 (bookmark `L4r_edge`) the shaft's ice
ball (0x38, 4 px/frame along the floor, a new one every 192 frames) knocks the toad down at x 190 (frame ~55); it
gets up at ~190 and for ~30 frames is invulnerable: walking off the edge it sinks THROUGH the spike tiles. 95 px
down the height's high byte changes ($1900 → $18ff, the next "screen") and the toad is pushed sideways 64 px per
frame; what happens then depends on the camera x at that moment (the game reads collision from video memory —
dozens of `LDA $2007` in bank 3 — and AxROM has a single 256-px nametable, so off-screen x aliases):
- camera ≤ ~62 at the push to 320 (slow walk-in, e.g. hold Left during the fall): the toad is put at **x 128** and
  falls on to the LEFT ledge of the pillar chamber (h $185e, x 128–159), camera following. `l4fall.py`.
- camera 64–76: it hangs at 320 for a few frames, then 384/448, off screen → the camera stops following → death.
- camera ≥ 77 (a dash into the pit): 320 → 384 → 448 → 512 → 576, lands on ledge 3 off camera (useless).
- the record's toad falls straight at x ≈ 281–300 with NO push and lands on the short ledge left of pillar B
  (x ≈ 310). Not reproduced: `l4dash*.py`/`l4air.py`/`l4eject.py` scans (dash, dash+brake, dash-jump, facing, hit
  while moving) never avoid the push. It would save ~1.5 s over the left-ledge landing; parked.

**Chamber map** (h low bytes; high byte $18): spikes x<128 · left ledge 128–200 (h 94) with pillar A (163–180,
top 126) · V-dip (259, h 62) · short ledge · pillar B (~330, top 126) · [barrier 0x3c spawns at 392] · pillar C
(422–436, top 126) · slope down to the bowl (577, h 30) · right side up to a floor at h 94 (x 686+).

**Object loader** (bank 3 $D2C0, list at $F440… for Level 4, 11-byte entries [id, trig hi, trig lo, x hi, x lo,
?, y, h hi, h lo, ?, flags]). In Levels 4 and 11 the low 2 bits of the trigger pick the test: 0 = camera x ≥,
1 = camera x ≤, 2 = camera y ≥, 3 = camera y ≤; one entry per frame; id $44 = a no-op marker. After the boost the
pointer is still at $F46C waiting for camera x ≥ 200/256/460/464 (the upper platforms' triggers), so NOTHING
later spawns — no checkpoint-6 barrier and ball, no platform/barrier/lift/warp below. Checkpoints are the barrier
objects themselves (walking past a broken one flushes the objects and reloads the pointer), so the list must be
walked: from the landing run RIGHT over pillars A/B/C and through the bowl until camera x ≥ 464 (toad x ≈ 670);
then barrier (392), ice ball (480 → rolls into the bowl) and the spiky ball (799) appear within 8 frames.
`L4S_GOALPTR=f4da` (new l4s goal: loader pointer) found it: 240 frames from the mid-fall state (`L4r_fall`).
That is what the record does too (its 99.3–103.0).

**New line after checkpoint 5** (frames): edge 152 · knock-down + fall to the mid-fall root 222 · right to the
loader trigger 242 (`l4_fall_right.json`, bookmark `L4r_adv`) · back to the rolling ball, punch-lift 92
(`l4ball.py lift`, `L4r_carry`) · carry to pillar C's top 118 (l4s `L4S_ACTS=climb`, `L4r_top`) · Right×5, B and
wait 184 (`l4ball.py throw`, `L4r_bardead`) · then left to the shaft. Old line cp5 → barrier dead: 2,442 frames;
new: ~1,010.

**The lift at the end** (0x35, x 768): the warp (0x22 at 776,$1798) spawns when camera y ≥ 2090, i.e. the toad
must ride ~110 px down; the lift then rises only 1 px/frame. There is a foothold at the ledge's lower lip
(753,$175e); the warp engages standing at (779,$1789). New l4s mode `l4warp` (two-phase rank: lift low, then the
warp) from `L4o_cp7`: 240 frames vs 344 for the old closed loop (−104). The record does lift → lip → warp in
~160; ours bounces on the lift three times first. Camera y band: follows a falling toad 23 px late, a rising one
59 px late.

### Later on 2026-10-02 — Level 3 rebuilt the TAS's way, skip re-aligned, new Level 4 verified

**Rats: flying attack + boot.** TAS #5093 kills each rat ~95 frames after it drops in: jump at it with B in the air
(−16 and a stun), land, dash + B = the boot (24-frame wind-up, kills whatever the health). Our searched fights
needed 324/388/655 frames. Its blind inputs only break at its two Left+Right frames (an instant dash out of the
boot's recovery); legal: wait ≥11 frames, tap, gap, direction+A. `l3fight.py` builds the foot section in stages
(scan a few parameters per stage on savestates; the toad's depth must be within ~4 px of the rat's lane):
**1,796 frames from the Level 1 portal to the bikes (was 2,847; 3,900 before that)** → `logs/pbeam_L3t.json`.

**Skip re-aligned.** The mechanism, traced pointer by pointer (table in this session's log): respawn → timers
reset → 255 frames later the loader jumps to $037F and walks RAM; the bike must crash on that exact frame so its
three debris objects take slots 3–5, the garbage object 0x12 then sits in slot 6 and dies with x low = $7F.
`l3skipn3.py` keeps the old post-respawn inputs and scans the dive (`nleft`) and a 0–15 frame shift:
`logs/pbeam_L3skipt.json`, 615 frames. (A false positive on the way: "level byte changed" was a game over.)

**Verified from power-on** (`assemble.py up2 L1 L3t L3skipt L4n2 L6a`, sha1 f15354b6): Level 8 at frame **12,884**
(newrun3: 16,500; the first full run: 26,975). Run clock at the level ends, ours / record: L3 **45.1** / 47.3 ·
L4 134.9 / 132.7 · L6 179.1 / 164.8. Replay-exact roots: `L3skipt_end_r` (= `logs/up1.inputs.txt`).
New Level 4 = `l4chain2.py` → `logs/pbeam_L4n2.json`, 5,509 frames (was 7,043); it replayed unchanged on the new
RNG. Level 6 is now the biggest upstream loss (43.5 s vs 32.1 s).

### 2026-10-02 evening — Level 1 rebuilt, upstream frozen as `up4`, downstream re-fit begins

- **Level 1** (`l1b.py`, staged scan): the old line headbutted the first pig leftwards, slid to x 31, whiffed a
  punch at the second and walked the last stretch (300 frames from the landing). New: 239 (record ~210).
- **Level 3** rebuilt from the new Level 1 end (`L3F_ROOT=L1b_end_r L3F_TAG=u python l3fight.py`), and
  `l3end.py` now picks the arrival at the bikes and the skip TOGETHER: not every arrival lets the skip fire, and
  the skip's length varies 596–649 with it. Bikes at 1,824 + skip 596.
- **Level 4**: barrier 7 with a running start (`l4cp7b.py`: dash off behind the last snowball, −25 frames at the
  barrier but only −8 at the warp: the lift is the bottleneck), `l4chain2.py` → `pbeam_L4n3.json` 5,499 frames.
- **Level 6**: room 2's faster line spliced in (`l6f.py` → `pbeam_L6b.json`, −36). Mashing Left+A/Right+A every
  frame climbs a snake at 2.85 px/frame (the 4-frame rhythm: 2.5) and reaches the head's top by frame ~150 like
  the record's run, but no way to stand on the rising head or to get a real jump off it was found (three scans,
  a breadth-first search). The record jumps from there and lands on the portal's ledge ~110 frames sooner.
- **Verified from power-on:** `assemble.py up4 L1b L3u L3skipu L4n3 L6b`, sha1 d172c096, **Level 8 at frame
  12,785** (run clock 178.2 s; the record is at ~173). Level ends on the clock: L3 44.2 s, L4 133.9 s, L6 177.5 s.
- **What depends on the random numbers** (`rngtest.py`: poke $25–$28 on the old bookmarks, replay the old
  segments): Level 8's climb NOT (the old seven sections replay exactly; only Robo-Manus), Level 9 from frame
  ~3,660 (the 0x6e swimmers), Level 10 not at all, Level 11 only the Buzzball (from ~6,280), Level 12 from frame
  2,448, Level 13 everything. So the re-fit is: boss searches + Level 9's second half + most of Level 12.
  `l8f.py` = old climb + new boss search (`L8f_arena`).
- WR split corrections for the race bar: Level 4 ends (warp black) at 127.6, Level 6 at 168.8 — the stored
  132.7 / 164.8 were the wrong blips; all ten need re-measuring the same way before the final render.

### 2026-10-02 night — re-fitting the later levels with SELECT (`rngfit.py`)

The plan had been ~20 hours of re-searching (boss fights, Terra Tubes' second half, most of The Revolution) every
time something upstream changes. Not needed:

- The random number generator is not a per-frame step: the main thread sits in `JSR $8728 / JSR $8743 / JMP $871F`
  (bank 0), scrambling $25–$28 with the toad's x, sub-pixel, object depths and the frame timer for as long as the
  CPU is idle. So the dice depend on how much CPU time each frame's game logic took.
- **Select does nothing in play, but its frame costs different CPU time → every later random decision changes.**
- `rngfit.py <old segment> <new entry> <out>`: replay the old inputs from the new entry and compare the toad's
  track (plus chosen enemies: the boss ids) with the old run's own track. Where they part: (1) if they meet again
  by themselves it was harmless; (2) in a segment's last 300 frames only the end state matters (idle/cut to the
  old last frame); (3) otherwise go back ≤180 frames and add Select on one frame (then two, then random
  patterns) until the old track holds 12 more frames. One random decision at a time.
- Lessons while building it: savestates made while testing a rejected variant must be thrown away (one accepted
  "fix" did not hold on a clean replay); a 240-frame acceptance window needs several lucky rolls at once and never
  passes; the boss must be in the key (its landing spot is rolled long before the toad's track shows it); lives
  must not be (1-ups come from the score).
- Result on route `up4` (`bash fitchain.sh L8_entry_up4 g`): **Level 8 (Robo-Manus: 20 re-rolls), Level 9 (2),
  Level 10 (0), Level 11 (3) in about five minutes**; Level 12 in progress. Old climb/tube/maze inputs are kept
  verbatim; only Select presses are added.
- Consequence: upstream polish no longer costs a re-search of everything after it.

### 2026-10-02 (later) — watching the record side by side: the briefing pages

The Revolution's re-fit first stuck at a pole drop: after a fight that went differently the toad grabbed the pole
at the same spot but a circling platform (which spawns with the camera) sat 1–2 frames off. `rngfit.py` got a
second repair, tried after the single-Select re-rolls: **make the old run's last wait up to 130 frames longer or
shorter** (idle frames inserted before / dropped ahead of the next press). It also resumes (`RNGFIT_SEL=`).

While it ran I read the record's video frame by frame in the browser (a canvas reads the video's pixels; a
contact-sheet overlay shows 28 moments per screenshot):

- **All ten of the record's level-end times re-measured** to 1/30 s as the first black frame after each level
  (`knowledge/wr_splits.json`): 3.53, 47.18, 127.61, 168.81, 251.74, 413.79, 449.94, 563.11, 706.63, 749.25.
  On a warp our screen goes black ~170 frames BEFORE the level byte changes (`blackcal.py`), so our Level 4 and 6
  deficits had been overstated by ~3 s: route up4 is 3.07 s AHEAD after Level 3, 3.4 s behind after Level 4,
  5.9 s behind after Level 6.
- **The briefing pages.** In the record the screen is black for about a second between levels. Ours showed the blue
  "LEVEL 12 - THE REVOLUTION" page for four seconds: the old segment scripts pressed Start every 20 frames until
  the level byte changed and then simply waited ~220 frames for the toad to appear. A fresh A press every other
  frame from ~60 frames before the byte change (`mashtest.py`) places the toad **232 frames sooner at each of
  Levels 9, 10, 11 and 12** (≈15.5 s), and 66 + 68 frames at Levels 6 and 8 (which were already mashing Start).
  `rngfit.py` now does this itself as step 4 (tries A / A+Start patterns from 120/60/30/0 frames before the last
  level change and keeps the earliest arrival), so every re-fit segment ends with it.
- **The Buzzball.** Our damage-ranked beam needed ~985 frames for 13 kicks because the ball got out of the corner.
  The TAS (tas/watch_1p_l11.txt 68569–69133) needs 564: jump left, kick on the way back, then [direction, B]
  every 45 frames at x≈1744 with the ball pinned at the right wall. The record does the same at ~47 frames a
  kick. `l11fight.py`: the TAS's opening (shifted 2 frames) + a small beam over (lead-in press, wait) per hit;
  first six hits come every ~40 frames.
- **The Revolution, scene by scene** (ours vs the record, seconds since the toad appears): first Hornhead
  22.5–28.5 vs 21.8–24.8; the pyramid's red walker 45.7–53.2 vs 39–42; big green walker 61.4–70.4 vs 51.8–60;
  wind face 1 84.6–91 vs 74.3–81.8; face 2 101–111 vs 91.5–98.3; then a Hornhead and a 7-second stand on a
  platform (our "walk left, wait for the TAS's platform phase" hack) – face 3 131–142 vs 113.3–118.5; a 6-second
  platform lap; face 4 149.8–157 vs 122.3–128.3; end flash 172.2 vs 140.3. So: ~10 s lost in fights before the
  first face, ~8 s around face 2, ~9 s at face 3 and its lap, ~3 s at the top.
- Side effect to remember: shifting a level's entry by N frames can cost a few frames of waiting further on
  (Karnath's Lair needed +38, Intruder Excluder +35: things there run on the global frame counter).

### 2026-10-02 (afternoon) — what a level load resets, and what it does not

- First version of the page-skip ended each segment on the first frame the toad's position matched the old run's
  last frame. Then Karnath's Lair needed "+38 frames of waiting" and Intruder Excluder stuck at frame 1,817.
  Cause: with the page skipped, that position is already set at level timer 1; the old run's last frame is the same
  picture at timer 34. **38 idle frames after the new entry the whole RAM equals the old entry – 0 differing
  bytes, random numbers included** (measured with the slow mash). So `rngfit.py` now idles on until the level
  timers ($0B/$0C) equal the old run's, and the next segment's old inputs start in phase. Real gain per page:
  ~26–30 frames at Levels 6/8, ~195 at Levels 9–12.
- A level load zeroes the random numbers ($25–$28 = 0 at timer 1). But with the FAST mash the entry is not
  bit-identical (37 bytes: the dice, $75, a buffer at $740): the sound engine is at a different point of its jingle,
  its CPU time differs, and the idle loop rolls the dice differently. Only the old slow rhythm (a press every 20
  frames) reproduces the old entry exactly. So the boss fights still need their Select re-rolls after a fast skip,
  but the deterministic parts replay as they are.
- The toad can be moved ~9 frames after the level is set up (timer 5); our old segments start at timer 34. That
  is ~29 idle frames at every level start (7 levels ≈ 3.4 s) for a later polish: it needs each level's opening to
  be re-timed against whatever runs on the level timer.
- `rngfit.py` "harmless" test tightened: two tracks only count as met again if every object on the list is where
  it was (a circling platform two pixels off killed the fit 600 frames later). If no re-roll restores that, it
  goes on with the toad's track alone and says so.
- `fightbeam.py <segment> <a> <b0-b1> <ids>`: generic fight redo (hit-by-hit beam, each blow must end on the
  ground, then a breadth-first walk back to any old-run state in a window). First test, Level 12's third Hornhead:
  kill in ~150 frames instead of 242.

### 2026-10-02 — PAUSED (owner needs the machine). Where to resume

Everything was stopped mid-search; nothing below is verified from power-on yet. Last verified route is still `up4`.

State of the pieces:
- Upstream with page skips: `pbeam_L4nm.json` (5,435 f, bookmark L3skipu_end_r) and `pbeam_L6m.json` (2,594 f incl.
  its 38-frame entry wait, bookmark L4nm_end0) are done; bookmark `L6m_end0` (slack 38) is Level 8's entry.
- Chain to rerun (it was inside Level 8's boss re-rolls): `python fitchain.py L6m_end0 38 m L8a L9a L10a`.
  Known from the interrupted runs: Level 8 needs the full 38-frame wait, Level 9 fits with 2 re-rolls, Rat Race
  needs NO entry wait (starts 218 frames sooner). Then Level 11 (use `L11b` once the fight is done), 12, 13.
- `rngfit.py` fixes made today, all untested on a full chain: lag frames now get the old raw input unless only
  the old run dropped the frame (the previous rule broke Level 8 at frame 1,817); a segment ends where the toad is
  set down (`_end0`, slack recorded); `--scan` picks the smallest entry wait that holds as far; `parts` reference.
- Buzzball: `python l11fight.py` (resumes from `knowledge/l11fight_ck.json` if present; delete it to start over).
  Hits 1-7 come every ~40 frames, then the toad has crept to x 1770 and nothing lands; the last change ranks
  states by frame + 3 per pixel right of x 1748 (the TAS holds 1744). Unfinished.
- Level 12 fights: `fightbeam.py L12a <a> <b0-b1> <ids> <name>` -> `knowledge/fight_<name>.json`. Specs:
  H3 1364 1686-1692 5c | H4 1865 2115-2158 5c | W5 2269 2553-2566 62 | H6 2737 2920-2934 5c | H7 3058 3248-3265 5c |
  W8 3706 4267-4288 62 | H9 5739 5953-6025 5c | H10 6736 7017-7110 5c | W11 7591 7837-7872 62.
  The tool now has the boot (dash, then direction+B: the TAS kills a once-hit Hornhead with it); only an older
  H3 result exists (254 frames for the old 328, three 16-point kicks). Then
  `python virtual.py L12a L12v knowledge/fight_*.json` and fit `L12v` in the chain instead of `L12a`.
- Still open in Level 12 after the fights: the 7-second stand on the platform before face 3 (old frames
  7100-7382), face 3's lap, the top. Level 9: the duck corridor (old frames 8430-8850) is hopped at 1.2 px/frame
  where the record runs it (~3 s).

### 2026-10-02 (resumed) — the chain with page skips

- `fitchain.py L6m_end0 38 m L8a L9a L10a`, then `L11a`: Level 8 4,880 frames (5,076 + 38 entry wait before; the
  briefing page at its end is gone), Level 9 9,988 (10,219; 3 re-rolls), Rat Race 2,062 (2,297; it needs NO
  entry wait at all, the entry scan found k=0), Level 11 7,173 (7,406; 4 re-rolls, entry wait 0). Old Levels 4 and 6:
  5,435 and 2,594. Not yet assembled/verified.
- Level 12 fights with `fightbeam.py`: modest. H3 283 for the old 327 (an earlier run had 254: beam width and the
  'first six leads' cut-off matter), H7 210 for 191 (no gain, do not use), W5 failed because the walker only
  spawns when the old inputs climb (fixed: the tool now plays the old inputs until the enemy is there).
- The Buzzball search reaches 12 of 13 hits in ~700 frames (old ~985) and then stalls with the toad crept to the
  wall; rerunning with 12/16/20-frame retreats and a 10-frame penalty per pixel right of x 1748.

### 2026-10-03 — the new route to Level 12, verified

- `assemble.py up5p L1b L3u L3skipu L4nm L6m L8m L9m L10m L11n`: **36,570 frames to The Revolution's placement,
  replay MATCH sha1 9da6befc** (up4 + the old late levels would have been ~37,850; newrun3 was 54,702). Run clock at
  Level 12's start 9:34.0; the record is there at ~9:24.
- Level 11 (`L11b`, fit as `L11n` 6,879 frames): the Buzzball kicked 12 times in the corner at ~40-frame spacing
  (`l11fight.py`, beam over lead-in/wait per hit), then the old damage-ranked beam for the 13th (`l4s.py` from
  the hp-15 state: 80 frames); dead at 6,417 instead of 6,710; with the page skip the segment is 527 frames shorter.
- Level 12 re-fit behind it: 10,508 frames (10 re-rolls). The queen (Level 13) never re-fits by re-rolls (every
  move is random): `l13solve.py` re-runs the original three `l4s.py ctr` sections on the new entry (~1.5 h).
- Dead ends today: `fightbeam.py` fights (Level 12's Hornheads) gain little or lose (the exact rejoin eats it and
  the dead body holds the camera: rejoin now also demands the same camera and no body); `shortcut.py` found
  35 + 67 frames in Level 4 but the pieces do not stitch (the toad's full state column must match, and with that
  nothing shorter exists); nothing in Terra Tubes' duck corridor (all lines die ~90 frames in) or Level 12's
  platform wait, lap and top (phase-bound).

### 2026-10-03 — **route up5: 12:58.87 from power-on** (48,882 frames, replay MATCH sha1 bfb65ff9)

`assemble.py up5 L1b L3u L3skipu L4nm L6m L8m L9m L10m L11n L12n L13n`. Level ends vs the record (first-black
terms, ours/record, level difference): L1 3.78/3.53 (+0.25), L3 44.28/47.18 (−3.15), L4 131.08/127.61 (+6.38),
L6 174.25/168.81 (+1.96), L8 258.27/251.74 (+1.10), L9 424.43/413.79 (+4.11), L10 458.78/449.94 (−1.81),
L11 573.24/563.11 (+1.29), L12 748.52/706.63 (+31.76), L13 778.87/749.25 (−12.27: the queen in 1,110 frames).
Total +29.62 s. Everything but The Revolution is within 6 s of the record; The Revolution is the record.
Video: `video_text2.py up5` (page-skip and Buzzball story added), `render_overlay.py up5` (warp levels' ends
moved 170 frames earlier to match the record's black-frame convention).

### 2026-10-03 — **route up6: 12:53.79** (48,578 frames, replay MATCH sha1 f56d516a)

The Revolution's 7-second stand before the sinking-platform launch: the old line walked LEFT around the tower
(219 frames) to the TAS's spot at x 498 and then waited for the platform's phase (141). Walking RIGHT takes 69
frames and the same phase comes one lap (256 frames) earlier; the old launch inputs then replay within a pixel
(`rngfit.py` got `RNGFIT_XTOL=1` for that sub-pixel flicker; the walker fight after it re-rolled as usual).
`L12w` 10,254 frames; the queen re-solved behind it (`L13w`, dead at 1,102). 304 frames saved.
Face 4 without the lap: a jump straight off the circling platform's first pass reaches the small sinking
platform in 73 frames (old 343) and the ledge above it before the wind starts - but the wind on that ledge kills
within ~2 s whatever the input, and no jump from the early landing has found the pole (the old one rides the
wind up to it). Still open; worth ~250 frames.

### 2026-10-03 — the fights by the TAS's own inputs (in progress)

Idea: our route is in exact sync with the 1-player TAS at several landings (old frame 1801 ≡ TAS row 1483 etc.).
Replace old[1802:2302] (499 frames) with the TAS's inputs 1460..1826 (367), referenced against the FCEUX log
(`tasvirtual.py`, `rngfit.py` parts with "tasrow"), and let Select re-rolls make the Hornhead do what it did for
the TAS. Found: our toad follows the TAS pixel for pixel through the jump; the Hornhead spawns 2 frames earlier
(our camera leads by 3) but WAKES one frame later, so the TAS's frame-exact kick misses. With 3 (or 7) idle frames
put in first the kick lands (63→47 at the TAS's frame) but the boot does not, and the shifted bounce-platform ride no
longer matches the log (tolerances `RNGFIT_XTOL` tried up to 12 inside TAS stretches). Now trying `resync.py`
(the chain's exact re-sync, which also searches time offsets) with jcheck after the kill.
Potential across the nine fights: ~960 frames (16 s) - the single biggest item left.

### 2026-10-03 — where it stands (end of this stretch)

**Verified: route `up6`, 12:53.79** (video `video/up6_overlay.mp4`, narration `video/up6.srt` / `up6_script.md`).
Record 12:29.25: 24.5 s left, ~27 s of it in The Revolution (fights ~15 s, face 4's lap ~4 s, the top ~3 s), the
rest spread over Level 4 (+6.4), Terra Tubes (+4.1), Karnath's Lair (+2.0), Level 8 (+1.1), Clinger-Winger (+1.3);
we are ahead on Levels 3, 10 and 13.
Tried and parked today, with the reason: fights by exact rejoin (the dead body holds the camera; the rejoin
state never matches), fights by the TAS's inputs (the Hornhead wakes a frame off our timeline; shifting breaks the
bounce-platform sync), face 4 without the lap (no pole grab found from the early landing), Level 4 shortcuts (joins
on ice keep a sliding sub-pixel; the snowball schedule), Terra Tubes' duck corridor (every line dies ~90 frames in),
Level 1 (nothing shorter), Level 12's top and lap (phase-bound).
Next time, the most promising single thing: `resync.py`/`rngfit.py` with the TAS fight inputs once the Hornhead's
wake-up phase is understood (what sets it: camera, a global timer, or the toad's position).

### 2026-10-03 (continued) — the TAS fights, nearly

- The Hornhead's wake-up is not random and not the frame counter: it fires on a 4-frame grid (poking the camera
  so it spawns 1-3 frames later still wakes it on the same frame). Ours is one grid step off the TAS's, so the
  TAS's frame-exact sliding kick misses.
- One idle frame inserted mid-jump (TAS row 1520, before the spawn) puts our toad a frame later on that grid: the
  TAS's whole fight then reproduces (63 -> 47 -> 0, toad unhurt). `resync.py` from the post-kill state found a
  92-frame prefix + TAS 1713..1829 back onto the TAS's exact landing (50,150). Piece: 400 frames for the old 503.
- But the remainder cannot rejoin the old route there: the next walker (fight 5) is already spawned at a different
  age; the TAS-walk must continue through fight 5. `tasrun.py` (resync stretch by stretch, idle-grid fix when a
  stretch holds a TAS hit) got 1829 -> 1920 and then no resync to the next landing: the sub-pixel (TAS 168, ours
  always 0 - checked over the whole level) makes short hops land a frame off, and the walker fight blocks the
  position check. `tasfight.py` (our own hit-beam on the TAS path) kills in 320 frames with four 16-point blows:
  our dash+B is a running kick (anim 35), never the boot (anim 31) - the boot needs the stunned enemy on the ground
  next to the toad, which only the TAS's exact slide produces.
- Level 4: piece 1's end state is doomed (every line from it dies within 46 frames: an object the old route had
  is missing), piece 2 is only valid after the OLD 4235 state. Terra Tubes' corridor: drifting mines (0x72) at
  head height and ducks; even keeping crouching states the beam never passes old frame ~8700.
- Buzzball on a strict 45-frame rhythm: stalls at hit 3 (the dash-kick to the right is the TAS's second blow).
Where this leaves the fights: the method works when (a) our toad enters the fight on an exact TAS sync, (b) one
idle frame is placed to match the wake grid, and (c) the piece is continued along the TAS through the next fight
until an exact landing exists where our old route also is. (c) is the open problem.

## 2026-10-03 (evening): Level 12 by the record's own inputs, fights 6 and 7

What stopped the walk at TAS 2128 was not the fight but a spawn: **Hornhead 6 appears when the vertical camera
(`$89/$8A`) reaches 4096**, and in our fight-5 piece the camera was 13 px short of that, so the enemy never
came. The camera lagged because the record bounce-launches off the springy platform at 1990 (sits on it through
a deep sink, 204 instead of 219, and is thrown to the floor above at 2002) while our piece hopped off it with a
normal jump and walked the floor. Skipping the fight is not an option either: **a live Hornhead locks the
vertical scroll**, so the next platform (`0x35` at (416,242)) never spawns and the toad falls back.

Fixes, in order:
- `l12f5tail.py`: after the walker dies (piece index 369 = TAS 1984) wait 21, hold A 20, then the record's floor
  inputs 2003..2128 -> lands at (194,30) at TAS-time 2151 (23 frames late) with the camera at 4096. The Hornhead
  then falls straight like the record's (in some launch variants it spawned with an upward arc instead - the
  spawn-to-landing timing decides, not the dice). The record's fight inputs 2129..2244 with one standing frame
  fewer kill it at index 90 (`F6_kill`), 25 frames before the record's own kill.
- **Dash jump rule** (measured): double-tap sprint (speed 192 = 3 px/frame) survives into a jump only if the
  direction is released for one frame right before direction+A, and only within ~12 frames of the tap; a plain
  direction+A out of the sprint drops to walking speed 128. The resync prefix generator now has this variant.
- `l12h6c.py`: from the kill, land, step back, tap, release, Right+A -> exact TAS 2284 landing on the sinking
  platform (99-frame variant kept as `H6_j2284b`).
- The record's Left+Right stand on that platform (2287..2298) = 9 idle frames + Right+A x3, which reproduces its
  spring launch to the (431,246) ledge pixel for pixel (`H6_j2346b`).
- Hornhead 7 then spawns 3 frames later than the record's (our camera ramps one frame later and one step slower
  after the spring jump - not the frame parity, not `$0B`; left unexplained) and the record's kick misses, so
  `l12f7.py` fights it with a kill beam and resyncs onto the record's 2557 platform landing (replacing its 2534
  Left+Right+A dash jump by the legal tap-release-jump).

### Big walker (TAS 2867..3172) and the stretch to 3295
- Two more timer facts: the **green platform** at (384,152) (`0x34`) is solid only in a ~120-frame window of
  the 256-frame `$0B` cycle (we arrive 88 frames later in the cycle than the record and had to wait 42 frames
  before the jump at 2771); the **bouncing platform** at (480,28) is also on that timer (our toad's bounce was
  one frame off the record's until the whole approach was moved by 3 frames).
- The walker spawns when the camera reaches 3408; our camera rests at 3419 after the fall (its ramp lags the
  record's), so we hop once on landing (A x12) to pull it the last 11 px - the walker then spawns 42 frames
  later than the record's. We re-land at exactly x 480 when it is 33 frames old (`BW_pre2`), i.e. the TAS's 2900.
- Its departure from (400,62) is a dice roll made BEFORE it leaves: `rngfit` (reference = the TAS log rows,
  `parts: [{bookmark..}, {tasrow..}]` so its re-roll window reaches back over the hop) found Down on the frame
  before the spawn. With the three-frame shift the record's fight inputs then land six of its seven blows plainly
  (the fourth misses by the walker's 4-px lead); `l12bwfin.py` adds one jump-kick (71 frames) and the record's
  spring launch 3180..3217 reproduces after a 17-frame wait (the platform's period is 39) when spliced at the
  exact mid-air match INCLUDING the record's release frame (its 3215 'A' is the second tap of a dash jump).
- Chain so far (`logs/pbeam_L12x_part.json` + `L12bw4` + `l12_bwkill` + `l12_bwl`): TAS 3295 at our frame
  ~3920, every bookmark reproduced byte for byte from `L12_start`.
- 3172 -> 3330: the launch (wait 15, Right released on two mid-air frames so the record's double tap forms, see
  `l12_bwl.json`) reproduces 3217/3237/3295 exactly; the green platform at (188,144) then needs a 13-frame wait
  at 3295 (`l12_gp1.json`, lands at x 199 instead of the record's 175); resync to 3391 in progress. Chain to
  that landing: 3,962 frames, verified byte for byte from `L12_start`.
- The (188,144) "green" platform is in fact a MOVING one (2 px/frame left); ours spawns ~17 frames later than
  the record's, which is what the 13-frame wait was for. `resync.run(GP_P1, 3346, 3390, 3391, "L", objcheck=None)`
  found the record's leftward dash jump off it (prefix 34 + TAS 3347..3391) and stayed in sync to its 3439 landing
  (385,62) = the old route's landing at old frame 4560. `l12compose.py none 3439 4560` -> `logs/pbeam_L12y.json`:
  4,089 new frames + the old remainder = 9,783 frames (L12w: 10,254; -471 before the fit). `rngfit L12y L11n_end0
  L12z` running (join: camera equal, `$0B` 141 vs the old route's 87, so expect wait repairs downstream).
- Join at 3439 failed (the old route's bounce sequence on the (224,61) platform is phase-bound and our `$0B`
  is 54 off). Instead the record's inputs are replayed plainly from 3439: they hold to 3513; a **20-frame
  standing wait on the static green platform at 3492** (plus Right, idle, idle, Right at 3513 for a 2-px drift)
  phases the bouncing platform, after which 3563/3608/3658/3703/3752/3792/3856 all land pixel-exact
  (`l12_gq1/gq2/gq3.json`). 3856 (96,62) = old L12w frame 5011 with identical speed/facing/anim -> join there.
  New part: 4,586 frames to TAS 3856; the faces/lap/top stay the old route's. Fitting as `L12z`.

### Where the Level 12 rebuild stands (2026-10-04, 08:30)
Verified and reproducible from `L12_start`: 4,529 frames to the record's 3856 landing (= old L12w frame 5011, same
position, speed, facing, camera): `logs/pbeam_L12x_part.json` + `L12bw4` + `l12_bwkill` + `l12_bwl` + `l12_gp1` +
`l12_gp2` + `l12_gq1/2/3` (`l12compose.py none 3856 5011 ...` -> `logs/pbeam_L12y.json`). That is 482 frames
(8.0 s) faster than the old route to the same spot, and `rngfit` carries it onto `L11n_end0` through all the
fights (five dice re-rolls) and the faces section (leniently).
NOT solved: the old route's tail from there. Every join tried (old 4560, 5011, 5388, 5503/5526/5542) breaks within
~500 frames on hidden state the old route carries and we do not: (a) the face spawned 3 frames earlier relative
to our arrival (its first bubble at join+92 vs +95; the horizontally cycling `0x37` platforms are 24 px = 3 frames
off for the same reason) - a wait makes it worse, arriving earlier is impossible with the record's flight; (b) a
sprint flag the old route (and the record) keep through the flagpole hang: after the drop a single Left starts
a 192 sprint for them and a walk for us, so every later landing is 2 frames/6 px off; no tap, release or
facing change found that recreates it; (c) sub-pixel height at ledge snaps (5558: (268,49) vs (268,53)).
Tools added today for this: `rngfit` parts may carry `pre` (standing idle frames, reference = the bookmark state)
and `inputs` (their own reference inputs); the key sorts tracked objects by (id,x,h); new repair steps
`shift()` over any 2+ idle stretch and `tweak()` (one-frame button replacement in our run only); `tailfix.py`
(standalone landing-by-landing tweak loop). None of them bridge (a)-(c).
Options: rebuild the tail (faces -> lap -> top, ~5,200 old frames) on the new timeline with the lap/pole/top
searches (`l12pole.py`, `l12lap*.py`, `platjump.py`, `l13solve.py`), or shave 3 frames between the face spawn
(record 3825) and the 3856 landing (nothing found), or shorten part 1 by 43 frames so `$0B` matches the old
route's (would also fix the `$0B`-bound platforms but not the face/sprint state).

### Tail rebuild on the new timeline (2026-10-04 afternoon)
Owner: "do both, don't stop to ask". Path chosen: follow the record from our 3856 landing with our own pieces
where its hidden state differs. Pieces so far (all from `GQ_j3856`): `l12_pole.json` (the record's pole hang,
drop delayed 12 frames so the wind has stopped: 373 f), `l12_u1.json` (l4s follow section TAS 4217->4360, 108 f,
+ the record's inputs to 4391), `l12_col.json` (the four-ledge column: the ledges are green platforms that are
solid only in a `$0B` window - a 66-frame standing wait at 4391 then a legal double-tap dash jump; lands all
of 4406/4424/4442/4460/4468/4500, 5 px left of the record), `l12_f8_kill0.json` (Hornhead 8 by our kill beam,
146 f). Next: step onto the sinking circling platform from the h-60 ledge as the record does at 4734 (it rides it
sinking to (502,30), jumps at 4752, lands 5087 after the lap), then its banned runs at 5145-5154, 5721,
5764-5776, 6199-6246 and the end 7262+. Tools: `l12fight.py` (fight + resync, generalised), `l12chain3.py`
(l4s follow chain on the new timeline; section 1 worked, section 2 did not because of the green-platform window),
`rejoin.py` (beam onto the old route's states; joins are easy to find but the old route's hidden state makes
them worthless).

### 2026-10-04 evening: the tail joined at the second flagpole
After the h-30 column and Hornhead 8 (`l12_col.json`, `l12_f8_kill0.json`): board the sinking circling platform
from the floor with a vertical hop timed so it is at (486,55) when we land at x 477 (`l12_lap.json`'s prefix),
ride and jump as the record does, hang on the (480,152) pole; the record's drop at 5043 kills us (the pole
vanishes in the wind), and the record's next platform (5199) spawns on a camera line our camera never reaches,
so instead we do what the OLD route does from this very pole: hang until the moving platform `0x34` is at x 16,
Down x3, land on it at (480,141) exactly like old frame 6691, then the old inputs with one idle frame before its
6705 jump (our landing-animation counter is one frame behind) - `l12_poledrop.json`, bookmark `PJ_6705`.
Whole chain `L12_start` -> old 6705 in 6,142 frames (the old route: 6,705): `logs/pbeam_L12y4.json` = that + the
old route from `L12w_at6705`; fitting as `L12z`.

## 2026-10-04 afternoon: Level 4, checkpoint 5 the TAS's way (while the Level 12 tail fight runs)

Measured the record's Level 4 in the browser pane (contact sheets of the YouTube video, 0.25-2 s steps): the whole
Level 4 deficit (~6.4 s) sits at checkpoint 5. The record reaches the switchback's end, drops at the right wall,
runs straight left along the floor to the x-244 snowman, kicks it, throws from its pile and leaves: ~6 s. Ours took
13: it picked the far-right pile's snowball, threw it at the right snowman, walked left at 2 px/frame (the sprint
was lost at the landing from the last jump: one released frame = brake), threw every 45 frames and walked up the pile's
slope at half speed afterwards.
The fix is the 1-player TAS's own inputs (tas/ram_l4_1p.txt 17222-17700): our sprint over the switchback already matches
it pixel for pixel; it keeps Right held through the landing, kicks (Right+B) ON the landing frame (a flying kick that
keeps the momentum - one frame later it is a standing kick that stops the toad, which is why the first replay died
at x 674), drops at the wall, dash-jumps left and kicks the snowman from the air. We run 1 px behind, so `l4c5tas.py`
repeats the current input until our toad has landed whenever the TAS just landed (`C5_LANDSYNC=1`): with that the
TAS's inputs hold from our frame 6816 to its 17700 (snowman dead at 17505). Its four pile throws are 30 frames apart
and two of them missed for us (the 1-frame lag), so the piece is cut at the pile arrival (frame 351 of the piece) and
the throws scanned there: B, idle 32, B, ... - barrier dead 153 frames later. **Checkpoint 5 piece: 504 frames from
up6 frame 6800 (old 700): -196 frames.** Bookmarks `L4c5_6800`, `L4c5_pile0`, `L4c5_bardead0`; pieces
`knowledge/l4c5_pile.json`, `l4c5_throws0.json`. Next: `l4s.py L4c5_bardead0 178 -341 400 reach_down_left` (the zigzag
down to the pit's edge), then a wait scan before the old boost inputs (`l4c5chain.py`, the ice ball's phase), and the
chain re-fit downstream.

### Later on 2026-10-04: Level 4 built (−281 frames), Level 12 tail joined to the level end

**Level 4** `l4c5chain.py` → `logs/pbeam_L4c5.json`, 5,156 frames (L4nm 5,435; −279 net), bookmark `L4c5_end0` (the toad
set down in Karnath's Lair, slack 38 as before). Chain: L4nm up to frame 6800 (index 2067), the cp5 piece (504), 2 idle +
`l4s_L4c5_bardead0.json` (the zigzag down to the pit floor, 148; l4s roots sit 2 idle frames after their bookmark), then
the boost redone: the ice ball sweeps the whole pit floor every 192 frames and cannot be waited out at the floor (the toad
stands on its path), so take the hit on the slide instead: idle w, Right x4, slide (on the ice a 4-frame run slides ~100
px), hit at x 185, lie 118 frames, Right into the spikes, Left 27 frames during the fall; the old inputs are rejoined at
the fall piece's mid-fall frame (128,243,$18) and run open-loop to the warp (a 2-frame drift at the warp text page: the
toad was set down 2 frames after the old inputs' end - the bookmark was moved there).
**Level 12** `l12compose3.py` → `pbeam_L12t.json`: the chain to the pole (6,142) + old 6705-6773 + our fight 9 (223) +
walk (164) + old-route walk to the top Hornhead (`ow_o2.json`[:459]) + our kill (`fight_h10_used.json`, 223, joins old
7597) + `ow_o3.json` (850, to old 8429) + `l12_pole2_w-2.json` (dropping 2 of the old's idle frames at 8429: the
jump off the circling platform 2 frames earlier lands 1 px deeper on the spring platform and its launch flies to the last
pole; +24 hanging frames to the bookmark) + `ow_o5b.json` (the hang shortened: `oldwalk.py` may now DROP all of the old
route's leading idle frames - the pole drop came 256 frames sooner) + old[10208:]. First composition (with the long hang)
verified from `L12_start`: 10,185 frames (old 10,254; only −69: the tail's platform waits ate the 563 saved at the pole:
176 at old 7200, 34 at 7318, 230 at the pole drop, 88 in the 7100 walk). With the deep-wait walker: the 7100 walk is 379
frames instead of 650 (`ow_o2b.json`, −271) and the hang 1,355 instead of 1,611 (`ow_o5b.json`). The o2b line needs the
top fight redone from its own spawn state (`OW_o2b_spawn`, `fightbeam ... h11` running), then o3/pole/o5 again.
Downstream: `fitchain.py L4c5_end0 38 c L6m L8m L9m L10m L11n` running (→ L6c … L11c), then L12t onto L11c_end0, the queen.

### 2026-10-04, evening: the state of play
- **Downstream re-fit done**: `fitchain.py L4c5_end0 38 c L6m L8m L9m L10m L11n` → L6c 2,595 (0 re-rolls), L8c 4,883 (19),
  L9c, L10c 2,063 (0), L11c 6,880 (6). `rngfit.py L12t L11c_end0 L12c` → 9,946 frames (6 re-rolls). `l13solve.py L12c_end0 0 L13c`
  running (the queen, ~1.5 h). Then `assemble.py up8 L1b L3u L3skipu L4c5 L6c L8c L9c L10c L11c L12c L13c`.
- Also fitted as a fallback: `pbeam_L12z.json` (L12t onto the old upstream L11n_end0, 9,928 f); its queen solve was stopped.
- **Level 12 tail, shorter-walk line (L12u)**: fight h11 from `OW_o2b_spawn` = 223 f (same as h10); `ow_o3b.json` 1,171 f to old 8750
  (passes the circling platform with wait −2 at 8429); the spring launch to the last pole needs its own scan
  (`l12tail2b.py`: OW_o3b_8429 + wait scan → `PL3_hang`, then `oldwalk ... o5c`); `l12compose4.py` → `pbeam_L12u.json`.
  Expected ≈ 9,650 frames (−600 vs L12w). Then rngfit onto L11c_end0 → L12d, queen again → up9.
- **Terra Tubes' corridor by the TAS's inputs** (`l9tas.py`, `l9fix.py`, `l9align.py`): our toad follows the 1-player TAS
  (rows 59565+) to within 1 px, but the drifting mine at (705,220) homes on the toad (speed byte 32→160 within ~8 px) and clips
  us at TAS 59673 where the TAS passes 1 px to the left. The 1-px lead comes from the x sub-pixel ($448) at the sync (drift
  starts at 59575, air control in the first jump); no sync frame / one-frame tweak keeps the exact track >9 frames; entry
  waits (0..258) do not change the mine's phase (it spawns on the corridor entry, camera 444, and drifts left 0.5 px/f).
  Next idea: find the TAS's sub-pixel by poking $448 on a snapshot (allowed: debug on snapshots), then search our approach for
  a state with that sub-pixel. Potential ≈ 145 frames (TAS 315 vs our 460).
- **L12u verified from L12_start: 9,413 frames (L12w 10,254, −841 = 14 s).** The two big finds in the tail: at the circling platform
  (old 8429) the old route idled 204 frames before its jump; dropping 174 of them (`l12tail2b.py`, wait −174) still lands on the spring
  platform in the phase that launches to the last pole (hang at old 8824); and at the hang itself 88 of the old's idle frames go too
  (`ow_o5c.json`, 1,295 f vs the old 1,384 from the hang). Composition: `l12compose4.py`. Now fitting onto L11c_end0 (`L12d`).
- Terra Tubes' corridor, continued: neither sub-pixel byte ($448, $457 poked on a snapshot) makes the TAS track exact, so the mine
  is passed by search instead: `l4s.py L9T_pre 770 0 400 reach_x` (L4S_LVL=11, MACRO 2) from our state at TAS 59650 = 82 frames
  to (770,198) past the homing mine; a fresh TAS sync at 59734 then dies on the next mine (59793), so the rest of the corridor
  (770 → 1120) is being searched the same way (`L9T_770`). Pieces so far: `knowledge/l9_pre.json` (85 TAS frames from L9m 8403),
  `l4s_L9T_pre.json` (2 idle + 82). After the exit: `oldwalk2.py L9m L8m_end0 0 <bm> <j> <jstop> <out>` rejoins the old L9m route.
- Corridor by search, result: `l4s.py L9T_770 1120 0 400 reach_x` took 298 frames for the remaining 370 px (hops between the mines,
  ~1.2 px/frame - the same pace as our old line), so the new line is 85 + 84 + 298 = 467 frames vs the old 460 for the corridor:
  no gain from the beam. The TAS's 315 is a matter of mine phases that only an exact track reproduces. `l9rejoin.py` measures the
  whole thing back onto the old L9m route anyway (the first part, to x 770, is 118 frames faster than the old).

### 2026-10-04 18:25 — **route up9: 12:37.73** (47,613 frames, replay MATCH sha1 ca809083)
`assemble.py up9 L1b L3u L3skipu L4c5 L6c L8c L9c L10c L11c L12d L13d` — 965 frames (16.1 s) better than up6 (12:53.79). Level 4's
TAS-input checkpoint 5 (−279) and the Level 12 tail (−841 at the segment; the fits downstream cost ~155 in entry waits and
lag shifts). The queen (`L13d`): 740 + 420 + 48 frames, level byte leaves 13 at input 1,903. Remaining gap to the record: 8.5 s.
Video: `video/up9_overlay.mp4` (render running), captions updated for the new Level 4 / Level 12 lines.
Next (for up10, one queen solve for the batch): Level 12's 7100 walk overshoot (−88) and the first pole's 110-frame delay;
Level 4's lift (the record does lift → lip → warp in ~160, ours 240); Karnath's room 2 (−110, five scans failed); Terra Tubes'
corridor (−145, parked).
- Night: the queen fight behind L12d is 149 frames longer than the old one (random); a second solve with 1 idle frame first
  (`L13e`) is running. Fight 9's return lands 230 px from the 7100 standing spot (walk 164 vs the old 76): `fightbeam.py L12w
  6773 7024-7100` from `PJ_6773` (out f9b) and the tail chain again behind it (`l12tail3.py` → `l12compose5.py` → L12v).
  The first pole's 211 idle frames (`l12_pole.json`: the face's cycle) would need the whole middle re-solved - parked.
- f9b: the kill (223-227 f) ends at x ~292-305 every time and the return BFS (depth 120) never reaches the old 7024-7100 walk states
  (231 px away through the wrap) - dropped; L12u's fight 9 + walk stays. Queen variants `L13e` (1 idle) and `L13f` (2 idle) running
  against L13d's 1,903 frames; the shorter one goes into up10 (same chain otherwise).
- First pole: scanning the drop frame (idle k then Down+Left over the 211 hanging frames, `GQ_j3856` + the piece's first 137 inputs)
  only k=210 survives - the wait IS the face's blow cycle; no earlier window. Parked for good unless the approach phase changes.
- Queen variants: `L13e` (1 idle) f1 768 then f2 died out at once; `L13f` (2 idle) f1 736 but f2 past step 170 (> L13d's 420-frame
  f2) - neither beats L13d's 1,903. up10 not assembled. The route stands at **up9 = 12:37.73**.

## 2026-10-05 — after up9
- Terra Tubes: with the sprint macros (`L4S_ACTS=rev`) the corridor beam is no faster (x 770 at step 40, like the walking beam):
  the mines force the hops whatever the speed. Level 9 + Level 10 together are only +2.4 s against the record (the TT/Rat Race
  boundary shifts the split), i.e. the corridor IS the Terra Tubes deficit. Parked.
- The queen: variants `L13g` (3 idle) and `L13h` (4 idle) running; the fight behind L12d (1,208 frames of fighting) is ~110 frames
  slower than the old L13w fight - the cheapest 2 s left if the dice allow.
- Owner's finds in the up9 replay: (1) Terra Tubes frame 25279: our toad is carried down by a hovering bug (0x74, hp 15; anim 36/37)
  at 1 px/frame for 330 px - the record falls (TAS 59336-59438, ~100 frames). The bug homes on the toad; the TAS's inputs from
  (813,102) get caught whatever the wait (`l9heli*.py`); `l9bug.py` searches a descent that never enters the carried state.
  Potential ~280 frames. (2) The Revolution's double spring bounces: `up9` has multi-bounce stretches at L12+1250 (2), +1639 (2),
  +2300 (3, 97 f), +3509..+3790 (7: a Hornhead fought from the spring, 280 f for 7 kicks where the TAS needs 2 blows), +5253 (3,
  124 f), +6249 (2), +6869 (2). All in part 1 (before old 6705): changing any of them means the tail chain, the fit and the queen again.
- TT descent: `l9bug.py` (beam that prunes the carried state) reaches the floor (915,38) in 120 frames and `l9bug2.py` walks it to
  (792,38) in 130 more - 250 vs the old 424 to that floor. But the old route cannot be rejoined there: it runs through at speed 96 with
  the mines elsewhere (we are ~170 frames earlier, the floor's mine train sits at 796-833 for us), the speed-matched join fails and a
  further search to the old's standing state at (635,38) dies out. Pieces: `knowledge/l9_bug.json`, `l9_bug2.json`, bookmarks
  `L9B_down`, `L9B_left`. Next idea: search from L9B_down with the goal 'the corridor entry state (584,70)' directly, or a wait at
  the landing until the mines are where the old route had them.
- Buzzball `l11fight3.py` on L11c: 12 hits in 527 frames (up9: 697) but no 13th from any beam state; `l4s ... rat` with
  L4S_HPMIN=15 from the 12-hit state (`L11d_12b`) running.
- TT descent, end of this stretch: `l9bug4.py` ends running left at (774,38) speed 88 (148 f); but the old route cannot be rejoined
  at 8279 (its jump to the 8300 landing misses from 11 px behind) and a beam from there to the corridor entry (584,70) dies at x 743:
  the floor's mine train blocks the crossing at our (earlier) time. The ~280-frame descent gain needs the whole floor crossing
  re-solved in one search with waits allowed (a beam that keeps idle states by frame count). Parked with pieces saved.
- Queen `L13g`: 764 + 440 - worse than L13d. No up10 from the dice.
- Buzzball, end of this stretch: the lead-in/wait beam (`l11fight3.py`) pins the ball for 8-9 kicks then it drifts off the wall
  (12 hits in 527 frames, no 13th from any state; `l4s ... rat` with damage allowed from the 12-hit state finds grazes (hp 11-13),
  no kill in 160 steps); the strict-pin variant has no pinned states after the opening; XKEEP 1740 loses the ball at hit 6.
  The TAS's rhythm is the only known 564-frame line and its inputs miss from press 2 on our state. up9's 914-frame fight stays.
- The queen vs the TAS: the 1-player TAS's Armageddon log (`tas/watch_1p_l13.txt`, 77093-78033) is 940 frames to its last input,
  with Select presses between blows (`p1=riBse`, `ABse`); ours kills at L13 frame 1,375 (the three `ctr` sections: 740 + 420 + 48,
  the 5-hit middle section is the slow one). ~430 frames (7 s) of potential. New `L4S_ACTS=queen` (the rev set + Select
  variants) so the beam can re-roll her moves; `l13solve.py L12d_end0 0 L13q` running with it.
- Buzzball: `l4s rat` found the 13th hit only 772 frames later (took damage) - useless; the XKEEP-1740 beam loses the ball at hit 6.
- **Rat Race by the TAS's own inputs** (`l10tas.py`): the 1-player TAS's Level 10 has no banned presses and replays frame for frame
  from our placement (sync held to its last input, +1,897); with L10c's page-skip tail → `pbeam_L10t.json` 1,945 inputs
  (L10c 2,063; −118), end state identical. `fitchain.py L10t_end0 0 r L11c L12d` → L11r, L12r; then the queen on L12r_end0 → up10.
- Mishap: a scripted caption edit crashed on `write()` (cp1252 encoding) and truncated `video_text2.py` to 0 bytes. Rebuilt it from
  `logs/up9.events.txt` / `up9.captions.txt` (the lost version's outputs, frames made level-relative) on top of a 2026-10-02 copy
  recovered from the conversation transcript; `python video_text2.py up9` reproduces the up9 outputs exactly. Backup kept as
  `video_text2.backup.py`. (Replaying old edit commands from the transcript spawned 260 stray processes - killed.)
- `l9cross.py` (time-aware beam from the bug-free landing to the corridor entry) died out at x ~746: the mine train blocks even
  with waiting. Rerun with damage allowed (HPMIN=31: one or two mine hits, the knock-back costs frames but may pass).
- Crossing with damage allowed (HPMIN=31): died out at x ~740 too. The Terra Tubes descent gain is unreachable at our arrival time;
  parked for good (the whole floor would need a different timing, e.g. arriving later on purpose).
- Level 4 lift on the new chain (`l4s L4c5_cp7 770 -125 400 l4warp`): 244 frames, the old piece 240 - the beam has no better line
  than the three bounces; the record's lift→lip→warp stays unreproduced. Parked.
- 15:03 a Wi-Fi adapter reset dropped every emulator bridge; all searches died. `l13solve` resumed L13r at section 2:
  **L13r = 2,038 inputs** (764 + 548 + 68; L13d 1,903) - the dice behind L12r are worse, so up10 (L10t −118, L13r +135) would be
  slower than up9. Waiting on L13rq (the Select set) and the wider Select-set search of section 2 from L13r's section-1 end
  (`L13x_f2`); if that beats 548, `l13solve ... L13y` composes L13r-f1 + x-f2 + a fresh f3.
- **The Select set works on the queen:** `l4s.py L13x_f2 0 0 600 ctr` with `L4S_ACTS=queen` (Select presses re-roll her moves) solved
  section 2 in 388 frames (L13r's own 548, L13d's 420). `l13solve ... L13y` composed L13r-f1 (764) + 388 + 68 → **L13y 1,892 inputs**
  (L13d 1,903). Assembling up10 = up9 with L10t (TAS Rat Race, −118) + L11r/L12r (re-fits) + L13y.

### 2026-10-05 16:35 — **route up10: 12:35.67** (47,489 frames, replay MATCH sha1 0889aa51)
`assemble.py up10 L1b L3u L3skipu L4c5 L6c L8c L9c L10t L11r L12r L13y` — 124 frames better than up9: Rat Race by the TAS's own
inputs (−118) and the queen's middle section with Select re-rolls (L13y 1,892). Gap to the record: 6.4 s. Video rendering.
- Buzzball with Select lead-ins (`L11_SELECT=1`): the ball leaves the wall at hit 7 like every other variant - the escape is physics,
  not dice. Parked. Queen solves running: `L13rq` (Select, width 400; section 1 past step 270, slow) and `L13w6` (Select, width 600);
  `up11_pipeline.py` assembles up11 if either beats L13y's 1,892.
- `L13rq` (Select set at width 400) solved section 1 in 1,420 frames: the 19-action set dilutes a 400-wide beam. Killed. Running:
  `L13w6` (Select, 600), `L13w8_f1` (Select, 800), `L13v_f1` (default set, 800) - the plan is the best section 1 + Select section 2.
- `L13w6` (Select set, width 600): section 1 744, **section 2 268** (L13y's 388, L13d's 420) - the Select re-rolls plus the wide beam
  are the right tool for the queen. Section 3 running; `up11_pipeline.py` assembles up11 behind it (expected ≈ −130 frames vs up10).
- **L13w6 = 1,830 inputs** (744 + 268 + 120; L13y 1,892, L13d 1,903). Assembling up11 with it (expected ≈ 47,427 frames, 12:34.6).

### 2026-10-05 19:48 — **route up11: 12:34.64** (47,427 frames, replay MATCH sha1 96217b30)
`assemble.py up11 L1b L3u L3skipu L4c5 L6c L8c L9c L10t L11r L12r L13w6` — 62 frames better than up10, 186 better than up9.
Gap to the record 5.4 s. The queen's kill is at input 1,138 of the segment; the TAS's last input is at 940 → ~200 frames still
there (section 1: 744 for 15 hits; section 3: 120 for the last blow). Searching section 3 again with the Select set from the
L13w6 section-3 root, and sections 1 at width 800 (`L13w8_f1` Select, `L13v_f1` default) are still running.
- `L13v_f1` (default set, width 800): 736 frames (w6's 744). Its section 2 with the Select set at 600 is being searched (`L13v_f2`);
  `l13solve ... L13v` will compose it if section 2 beats 268 + 8.
- Section 3 with the Select set (`L13f3s_f3`): 120 again - the last blow's timing is fixed by her pattern there.
- Video `video/up11_overlay.mp4` sent. Running: `L13w8_f1` (Select, 800), `L13v_f2` (Select 600 behind the 736-frame section 1),
  `L13w6b_f1` (Select 600, one idle frame first = other dice).
- Queen section-1 samples: `L13w8_f1` 744 (= w6), `L13v_f1` 736 (default set) but its Select section 2 passed 268 frames unsolved
  (killed). Running `L13w6b/c/d_f1` (Select 600 after 1/2/3 idle frames): any that beats 744 gets a Select section 2 + section 3.
- `L13w6b_f1` (Select 600, 1 idle frame first): **728** (w6 744). `l13solve L12r_end0 1 L13w6b` composes it with a Select section 2
  and 3; `up12_pipeline.py` assembles up12 if the segment beats 1,830.
- Queen samples: `w6c` 752, `w6d` 764; `w6b` (728) got a Select section 2 that passed 320 frames unsolved (w6's was 268) - killed:
  the 268 was lucky dice behind THAT opening. Running `L13w10_f1` (Select, width 1000, 1 idle), `L13m2_f1` (macro 2), `L13w6e_f1`.
  The queen seems near this method's floor (~1,830); the TAS kills ~200 frames sooner.
- Hornhead blows (`U_j4500`, fight 8's start): every kick does 16 - dash (speed 192) or walk, B held 1..32 frames, before or after a
  first hit. There is no 31-damage boot; a 47-hp Hornhead is three 16s and the fights' length is the wait for its return between
  kicks (f8 146: hits at 32/76/146; f9 223). The "TAS two-blow kill" note in the summary was wrong. Fights 8/9 parked.
- Queen opening samples so far: w6 744, w6b 728, w6c 752, w6d 764, w6e 740, w8 744, v 736 (default set). Running w10 (1000 wide), w6f/g/h (5/6/7 idle).
- `L13w6f_f1` (5 idle): **724** - best opening. `l13solve L12r_end0 5 L13w6f` composes it (Select section 2 must be <= 288 to beat L13w6's 1,830); `up12_pipeline_f.py` assembles up12 if so.
- Section-2 lotteries (Select 600, capped at 75 steps = 300 frames) behind the 728 (w10) and 740 (w6e) openings; the w6f one passed 320 and was killed.
- Lottery hit: section 2 behind the w6e opening (740) = 268. `l13solve L12r_end0 4 L13w6e` composes (f3 search); up12 if < 1,830 (needs f3 <= 116).
- w8's section-2 lottery: 272 (no gain); w10's: unsolved within the cap. w6e composition = same input count as w6 (its 4 idle frames eat the 4-frame shorter opening). Capped width-800 section-2 tries behind the 724 (w6f) and 728 (w6b) openings launched.
- Queen lottery, the catch: the section-1 solves behind k idle frames all end at the SAME input index (746 for k = 0/4/8: w6 744,
  w6e 740, w6i 736) - her counter reaches 180 at a fixed moment of her pattern, the idle frames only shorten the searched part; and
  their section-2 lotteries then give the same 268 (same state). Only a genuinely earlier opening (w6f 724 at k=5 → index 731,
  w6b/w10 728 at k=1 → 731) can gain, and those openings' section 2 lotteries have all passed the cap so far (600/800; 400 running).
  The queen stays at L13w6 = 1,830; ~15 frames at stake here, not worth more machine time after the running tries.
- Queen lottery closed: w6j 900; the capped section-2 tries behind the 724/728 openings (widths 400/500/600/800) all unsolved. The
  queen stays at L13w6 = 1,830 (route up11 = 12:34.64). Next targets, in order: Karnath's room 2 (1.8 s; the record mounts the
  snake's head early - look for a head pause near the floor), Terra Tubes' descent + floor crossing (2.4 s; needs a different
  arrival time), Level 12's walk after fight 9 (−60) and the fights' waits, Level 4's lift (lip route), the Buzzball (TAS rhythm).
- **Karnath's room 2, the head's pause:** from `L6r_room2` the snake head (0x4c) appears at frame 7 at (112,32) and does not move
  until frame 71 (65 frames) - at floor height, 36 px right of the toad (76,30) - then rises 2 px/frame, runs right at h 80, up again,
  right at h 176 to x 440. All five earlier scans tried to catch the RISING head; nobody tried standing on it during the pause.
- Room 2 mount tests: standing on the head's column (x 105-116, exact placement by releasing Right at 88-92) before the rise: not
  lifted (the head passes through a standing toad); a hop as it rises: the toad is pushed to x 134 (the head is solid sideways);
  jumps during the floor pause (frames 44-68, A held 1-10): never land on top (its top is at floor level). The record's mount must
  happen on the h-80 run or the x-176 rise; a ledge the toad can stand on where the head rises would be needed (room 1's lift at
  x 112 works that way). Parked.
- Fight 9 again with a deeper return (FB_RETDEPTH=230, window 7024-7100, out f9c): the earlier try died at depth 120 ~231 px short.
- f9c: the kill (223) again ends at x ~292-305 and the return BFS finds no way to the old 7024-7100 states even at depth 230 (first candidate; the others pending). The walk after fight 9 stays.
- TT crossing with an explicit wait at the landing (WAIT0 = 60/120/180, damage allowed, width 400): does the mine train let a later arrival through?
- Turbo Tunnel's gauntlet by the TAS's inputs (`l3tas.py`): the 1-player TAS's gauntlet has two Left+Right frames (13920, 14352), each
  an INSTANT sprint (speed 0 → 192 in one frame) into a jump; stripped, our toad jumps at speed 16 and the line drifts there. No legal
  5-frame replacement reproduces a sprinting jump by 13926 (a legal double tap builds speed over ~8 frames). Like for like the TAS
  gauntlet is only ~75 frames shorter than L3u (1,484 vs 1,559 from the same sync state), and a new gauntlet line would force the
  bike skip's sub-pixel-exact re-solve plus a whole-chain re-fit. Parked.
- Ours vs TAS (frames of play, up11): L10 equal; L11 +208 (Buzzball); L9 +653 (descent, corridor); L13 ~+200 (queen); L4 ~+150
  (the TAS's cp5→cp6 is banned); L3 ~+75; L12 not comparable (the TAS's Left+Right everywhere).
- **Terra Tubes descent + crossing solved**: `l9cross.py` with WAIT0=60 (mine train moves on), damage allowed, ranking by x only:
  212 frames from the bug-free landing to the corridor entry (586,70). From L9c index 7852: 120 (descent) + 60 + 212 = 392 frames
  vs the old 550 → **−158**. Pieces `knowledge/l9_bug.json` + `l9_cross_60.json`; bookmark `L9X_corr60`. Rejoining the old route
  at index 8402 with `oldwalk2 ... o9c`.
- Corridor beam from the matched entry stuck at x ~915 (a mine); second beam with WAIT0=120 (exit2). Queen: w10b opening 724 at k=5 (index 731); its capped section-2 lottery launched.
- TT corridor from the matched entry: the TAS's inputs die at its homing mine (x 622-747, TAS 59632-59707) for every wait 0..700 (the
  same 1-px sub-pixel problem as before); the old route's hop line misses its first landing (8462) by >8 px from an entry that matches
  in x/h/speed - so the x sub-pixel ($448) decides the hop. Next: the crossing's goal gets the old's $448 as well.
- First corridor hop repaired by a height-dominant beam (MODE=down): 64 frames from L9X_corrb to (600,198) ~ the old's 8462 landing (601,198, spd 96; ours 76). `oldwalk2 ... L9X_corrhop1 8462 ... o9e` running.
- Corridor chain ( from L9X_corrhop1 8462): walks 113/45/0/49 + repairs 114/32/118 = 471 frames for the old's 8462-8831 (369): the repairs cost ~100 more than the old's hops (our mine phases), so the descent's 158 is down to a +56 net so far; repair to the (1076,38) ledge failed in 80 steps - rerun with 220 steps / width 600 (rep3b).
- Corridor chain (l9chain.py from L9X_corrhop1 at 8462): walks 113/45/0/49 + repairs 114/32/118 = 471 frames for the old's 8462-8831
  (369): the repairs cost ~100 more than the old's hops (our mine phases), so the descent's 158 is a +56 net so far. The repair to the
  (1076,38) ledge failed in 80 steps; rerun with 220 steps and width 600 (rep3b). Pieces so far: knowledge/l9chain_pieces_part1.json.
- Corridor chain, end: the climb to the (1076,38) ledge needed 404 frames (the old's 8831→8857 is 26) - net −322: the descent line is
  a LOSS at our mine phases. Parked for good; pieces kept (knowledge/l9chain_pieces_part1.json, l9_cross_0rep3b.json).
- Next two searches: the queen as ONE section to 240 (no 180 split) with the Select set, width 600 (`L13one`); the Buzzball by the
  same damage beam (l4s 'rat' mode, Select set, width 600) from the ball's appearance on L11c (`L11buzz`).
- Buzzball by the Select-capable damage beam (l4s rat, width 600): after 120 frames the best state is still undamaged (min hp 191-203 only in side states) - the 'rat' ranking does not keep the hits; killed. The one-section queen search (L13one, Select 600, goal 240) runs on, ~13 min per 10 steps.
- 19:12 owner needed the RAM: all emulators stopped. The two one-section queen searches (`L13one` Select set at step 100 ≈ 400 frames
  of her 20 hits, `L13one2` default set at step 60) were killed; l4s has no resume, so they restart from scratch when the machine is free:
  `L4S_ACTS=queen L4S_CTR=586 L4S_CTRGOAL=240 L4S_LVL=13 L4S_FOEID=0x7e L4S_AIRB=1 L4S_STEPS=600 L4S_SAFE=20 python -u l4s.py L13one_f1 0 0 600 ctr`.
  Route stands at up11 = 12:34.64.

## 2026-10-06 (evening) — The Revolution against the record, frame by frame

The record's video, read by pixel OCR of his score HUD (1280x720 player: digits at x 487+24.5k, y 124..150; template
match at full res, 0.5-s steps) plus contact sheets of both runs, aligned on the four wind faces (RAM: face object
0x60 spawns when the camera reaches y 2048 / 1512 / 1112 / 1056 - CAMERA-triggered, then enters ~100 f, blows
~320 f (bubbles 0x61), leaves). Ours vs his, absolute run seconds: level entry 567.7 vs 564.1 (-3.6); F1 blow
644.7 vs ~640 (-4.5); F2 blow 661.4 vs ~658 (-3.5); F3 blow 689.0 vs ~679 (-10); F4 blow 702.1 vs ~688.5 (-13.5);
end flash 722.4 vs 704.5 (-17.4). So the fights before F1 are only ~1 s behind now; the loss is F2->F3 (6.6 s),
F3->F4 (3.6 s) and the top (2.5 s).

Where it goes (L12r segment frames, logs/L12p.ram = every frame's RAM from l12probe.py):
- after F2's blow ends (5944) we hang 170 more frames (drop 6113); after F3's (7599) 197 more (drop 7796); 30 idle
  on the circling platform at 7878; 124 idle at the top (8984). oldwalk2 drop scans (f2drop, f3drop): no earlier
  drop reaches the old landings - the circling platforms (0x36, x = 2*$0B + 58 mod 512, PERIOD 256 frames) and the
  lift/bounce apparatus (0x34 same speed) are frame-counter bound. He simply arrives at better phases.
- THE QUANTUM: a phase-locked wait W only shrinks when the time gained since the previous phase lock reaches 256-W,
  and then it gives a whole lap (256 f) at once. F3's wait 197 needs >= 59 f gained between F2's drop and F3; the
  bounce launch at 6769 (previous opportunity 6513) needs the wide-platform Hornhead dead by ~6340 instead of 6423
  (spawn 6184; he kills it in ~90 f from the first hit by KNOCKING IT OFF THE PLATFORM EDGE - +750 then +5000, the
  Hornhead flies off the left edge at 667.0 in his video); the green walker (6804-6983, ours 5 kicks 179 f, his 96 f)
  then feeds F3's quantum. Two laps = 512 f = 8.5 s -> 12:26.
- Running: fightbeam.py on the wide Hornhead (6184, out wide), the pre-F2 Hornhead (5218, pre2), the walker (6804).
- **THE BIG BOOT IS REAL** (bootprobe.py, snapshot 6240 = 13 f after hit 1 on the wide Hornhead, hp 47): idle 12-16,
  walk toward it 34 frames (shorter walks give the 16-damage kick), direction+B one frame -> hp 47 -> 0 in one blow
  (the toad's anim 31 wind-up ~23 f, then anim 30 lunge). The TAS does exactly this at its frames 74880-74939 (walk
  'le' 34 f, 'leB'); our 2026-10-04 test ("every kick does 16") never walked long enough before the press - the walk
  has to turn into a run. `l12boot.py 6240 12 34 12 w12`: hp 0 at 6311, the body gone at 6337, landed 6352 at
  (219, h 4574) - 124 frames before the old kill's 6461/6437. Bookmarks BOOT_w12 / BOOT_w12L.
- Next: l4s.py from BOOT_w12L (reach_band, gdh +192 = the walker's platform h 4766) to find the lift + bounce launch
  one lap (256 f) earlier than the old 6769; then splice.py (rngfit re-fits the walker fight and the rest).
- **The lap is ours** (`l12chase3.py`): after the big-boot kill (landed 6352 at x 219) walk RIGHT into the oncoming
  circling platform (Right 72 f, Right+A 13 f -> on it at 6451 at x 360, the platform at 372 = the old route's 6720
  pump spot), hold A at once (d 2-4: the platform sinks 30 px and springs), keep Left+A through the rise, land on the
  static platform (H 4727), hop up: the walker's platform at **6526 vs old 6786 (260 f earlier)** - more than the
  211 the 45-frame lock at 7026 needs, so the whole lap (256 f = 4.26 s) carries to the level's end.
  Mechanics learned: walking with the tower's rotation is 3 px/f (spd 192), against it 2 px/f (128); a jump reaches
  +58 px only with A held ~13 f; the big boot needs the toad already moving at 192 when B is pressed.
- Next: retjoin.py CHASE_best -> old 6786..6830, piece = boot + chase + join, splice.py L12r -> L12q, re-solve the queen behind it.
- Karnath's Lair vs the record (contact sheets, 2-s steps): we are ~1.2 s AHEAD through the four rooms and the
  OUT door; the 2 s go in the warp room after it. Probes (climbprobe*.py from L4c5_end0 + L6c inputs 2127..): the
  tube is climbed by alternating Left+A/Right+A; period 4 (ours) tops out in 83 f, period 1/3 in 73 f but the toad
  then dies at the top, period 2 lands later; the far-ledge landing is ~244 f after the climb start whatever the
  rhythm - the launch is tube-timed. Where his 2 s come from is still unclear (needs 0.1-s frames). Parked for now.
- Warp room (after Karnath), more probes: the room's frame counter resets at the entry (L6c index 2022; the tube
  0x4c spawns at +6), so its schedule is entry-relative. The tube is shimmied at ~2.5-2.9 px/f (tubeclimb.py beam:
  top in 74 f vs our 83; no jump-climb exists); every earlier top got the toad killed by the flying stars in the
  fling (hp 0 at x ~257-290). The record's toad tops out ~0.3 s after grabbing and is flung ~0.9 s later, landing
  ~2 s before ours - mechanism still unknown (maybe the fling fires when the toad reaches the top while the tube's
  second rise is on, and the star schedule happens to be clear for him). Parked; ~120 frames at stake.
- L12q: fightbeam `wq` (FB_START=JOIN_chase) killed the walker in 229 f and rejoined old 6994; the full piece
  (a 6184, b 6994, 598 inputs, saves 212 + the lap) is splicing (`l12q_splice.py` -> rngfit of the remainder).
- Splice lesson: rngfit's key is (x, h, $41B, z, hp, level) and a join that matches x/h but not the camera ($41B is
  the screen y) or the sub-pixel ($448) loses the track within frames (the walk diverged 3-4 px). `retjoin.py` now
  takes RJ_SUB=1 (sub-pixel in the key): from the walker fight's end it joined old 7003 in 7 frames and the next
  120 old inputs replay identically (only the walk-anim byte is off by one). Piece `knowledge/piece_L12q2.json`
  (a 6184, b 7003, 605 inputs, saves 214 + the lap) splicing as L12q2.
- Splice L12q2 stuck at old 7080 (the jump onto circling platform #2): with the lap gained the platform's phase no
  longer matches - these platforms are CAMERA-SPAWNED and circle from their spawn, so after a changed camera
  timeline every later platform has its own new phase (the 2*$0B+58 fit earlier was that one platform's luck).
  So the remainder needs per-landing re-sync: `oldwalk2.py L12r L12p_f7000 7000 WQSUB_join 7003 9280 q2walk`.
- Fixed the jump onto platform #2 by timing it to the platform itself (x 334 when the toad stands at x 186): from
  the sub-pixel join (old 7003) walk Right 12-15, brake Left 3-8, idle to 30-34 frames, then the old inputs from
  7071 - lands on the platform (x 223 like the old) and grabs F3's pole at old-index 7185-7189 (`Q2_jump`,
  `knowledge/q2_jump.json`). The rest of the level from there: `oldwalk2.py ... Q2_jump 7071 9280 q2walk2`
  (per-landing wait scans handle the re-phased platforms below F3's pole, at 7878 and the top).

### 2026-10-07 (small hours) — **L12q3: The Revolution 249 frames shorter (9,171 vs 9,420)**
`l12q3_compose.py`: old[:6184] + piece_L12q2 (big boot 6311, oncoming-platform launch one lap early, walker fight
wq, sub-pixel join at old 7003) + q2_jump (walk 12, brake 3, idle 19, old jump 7071) + OW_q2walk2 (old 7071..9247
re-walked: every landing with wait 0, one with -2) + old[9247:]. Replays from L11r_end0 to the same end state as
L12r (level 13, toad 0,0, lives 4). Bookmark L12q3_end0. The queen re-solve `l13solve.py L12q3_end0 0 L13q3`
(width 600) and `assemble.py up12pre ... L12q3` (power-on check without the queen) are running.
Expected: up11 12:34.64 - 4.14 s = ~12:30.5 if the queen comes out at ~1,830 again; the record is 12:29.25.
- **Terra Tubes vs the record** (sheets): even from the start to ~392.7 s (the pink cylinders before the duck
  corridor). He swims the duck corridor and the final blue chamber in ~14 s (394.5 -> the last spikes at 408.5, where
  he ALSO dies: "5000" pops, the screen holds 5.5 s, black at 414.0); we take ~21 s to the same spikes (hit at
  413.98, black 419.83). So ~5.5 s sit in the duck corridor + final chamber approach, not in the death.
  `up12pre` (L12q3 without the queen): 45,348 frames to Armageddon's door, replay MATCH sha1 d341245c (up11: 45,617).
- Terra Tubes, the record's route past the ducks (0.25-s frames 392-398): he swims along the water at the bottom-left
  of the cylinder area, climbs the pink staircase (394-395), drops into the blue on the right and swims down into the
  star corridor (396.5) - ~4 s. We drop to the cylinder floor (h 6086) and hop right past the ducks for 7.5 s. The
  TAS does his route too (watch_all_log 19500-20300, with a 75-frame stand and the bug-carried descent). Beam
  `l4s.py L9_duck_8300 1120 -20 600 reach_w` (swim set) from our x 749 on the pipe tops, goal x >= 1120 near h 6162.
- Queen: the single-section Select search (`L13one_f1`, width 600, 2.8 h) reached 20 hits in 1,000 frames - the same
  as L13w6's 1,016; the ending after the 20th hit is a fixed 814. The queen is at this method's floor; dropped.
- Terra Tubes: the one-stage swim beam hugged the wall at x 915 (the way on is up the water column and over the
  steps first). Two stages now: `l4s.py L9_duck_8300 820 60 600 reach_w` (the steps' top, h >= 6242) then down to
  the star corridor (x >= 1120, h ~6162).
- Terra Tubes, the way down into the star corridor: from the steps' top (832, 6250; the TAS stands at 834) every
  jump lands on a floor at 6182 that ends in a wall at x 915 (jumps reach 915 at ~6200 and stop; A held 22+ gets hurt
  at the apex ~6272). The TAS gets below that floor at x 899-904 with a Left+Right press (banned). How the record
  gets down the right side is still unknown; an exploration beam (`l4s.py L9_duck_s1L ... explore`, trace
  logs/l9_explore.txt) is mapping what is reachable without it.
- **Terra Tubes, found it.** Our heights (L9c 7360-8300): we stand at (489, 6310), swim up the water column to the
  staircase top (809, 6502) at 7840 - the TAS's "x 834 h 102" is that spot (hh 25) - and then the BUG carries us
  (anim 36/37) 320 frames down the x-938 column to the floor at 6182, below the star corridor, which we re-enter
  200 px further on through the duck corridor and the water at (1123, 6162 -> 6362). The record and the TAS swim
  down that column only to ~6380 and go straight right into the star corridor (x 954+, H 6350-6440); the TAS
  needs ~300 frames from the staircase to x 967 vs our ~1,040 to x 1146. Beam `l4s.py L9_at7800 960 -88 600
  reach_band_w` (the corridor door). Then the corridor's mines (time-based) need a re-solve to the old route.
- Queen behind L12q3: section 1 solved in 784 frames (sections 2-3 running); `up12_pipeline_q3.py` is armed.
- Terra Tubes, the geometry around the staircase top (809, 6502) = L9c 7840/7852: two hovering bugs 0x74 (hp 15,
  unhittable by punches or jump-kicks) at (824/840, ~6530); walking right under them at x ~818 gets the toad
  grabbed (anim 36/37, 1 px/f) and carried down the x-915 column to the floor at 6182 - that is our old route.
  The TAS (and the record) instead land on a ledge at H 6406 (x 884-904), get into the water just below it
  (6366-6394) and swim right/down the x-938 column into the star corridor (which lies at ~6000-6170, BELOW our
  floor at 6182; our old route reaches it from the duck corridor through the water at (1123, 6162)). The TAS
  drops through the ledge with a Left+Right press. x 915 is not a wall but the screen's right edge: the camera x
  sits at 772 and the toad is clamped at camx+143 while in the air; the TAS's camera scrolls on once it swims.
  We CAN land on the ledge (jump from the top, steer Left, hold Right: lands at (884-892, 6406) after ~113 f)
  but the chasing bug grabs us at x 896 right after. Open: get into the water under the ledge before the bug
  (beam `l9water.py`: goal = swimming at x >= 860, H <= 6420, carried states pruned).
- Queen behind L12q3: **L13q3 = 1,861 frames** (f1 784, f2 384 -> 20 hits at 1,172, finish; L13w6 was 1,830).
  `up12_pipeline_q3.py` assembles up12 = L1b..L11r L12q3 L13q3 (expected 47,209 frames = 12:31.1) and renders.
  Queen openings with 1 and 4 idle frames (L13q3b/c) running for a shorter one.
- Terra Tubes: `l9water.py` (swim under the ledge, carried states pruned) died out - the bug catches every line.
  Parked with the geometry notes above; the prize there is ~5-10 s and it is the clearest path to the record.

### 2026-10-07 — **route up12: 12:31.08 from power-on** (47,209 frames, replay MATCH sha1 c198a38c)
`assemble.py up12 L1b L3u L3skipu L4c5 L6c L8c L9c L10t L11r L12q3 L13q3`. up11 was 12:34.64: -3.56 s, all of it
The Revolution (the big boot + the lap: -249 frames in L12; the re-solved queen +31). Record 12:29.25: +1.83 s.
Video: `video_text2.py up12` (new L12 captions: THE BIG BOOT, THE LAP, shifted faces/top) + `render_overlay.py up12`.
Next: the queen openings L13q3b/c (running); Terra Tubes' staircase-ledge-water route (~5-10 s, see above); the
warp room after Karnath (~2 s); then the record.
- Armed: `up12_pipeline_q3b.py` / `up12_pipeline_q3c.py` assemble + render up12b/up12c automatically if the queen
  openings L13q3b (1 idle) / L13q3c (4 idle) come out shorter than 1,861. `l9water2.py` (width 1000) still looking
  for the water under the ledge in Terra Tubes.

### 2026-10-07 (day) — the tower's waits, explained by the TAS log
User's question: we lose ~9 s on the tower, "he had to wait too". Answer: the waits are where we arrive at the wrong
moment; the TAS (and the record) arrive so that the next platform is right there.
- **Face 2** (TAS 74091-74822, ours L12r 5218-6171): our frame 5218 == TAS 74091 (spring 0x36 x 34, Hornhead 384/95,
  camy 1616). The TAS kills the pre-face-2 Hornhead with a walk-away + turn (Right+B) big boot (kill 80 f after hit 1, ours 120),
  lands on the circling SPRING (0x36, H 4407), PUMPS it (A held; its Left+Right just keeps the toad still) and the
  launch lifts the camera to 1512 in mid-air -> face 2 spawns 108 frames earlier than ours. Re-pumps to the pole.
  At the end of the wind it drops early (64 f before the wind ends, legal), catches the spring, pumps, and the lift
  (0x34 H 4488, spawned at fixed x ~232 when the camera passes ~1496 - i.e. when the toad rises) appears under it.
- Ours now (`l12f2full.py` kill by TAS inputs, pump with Right held, wait 20 -> pole x 480 at 5454, face 5444; the old
  lift ride copied 84 frames earlier): wide platform at 6087 vs 6171 with the EXACT old state (x 458, cam 1450),
  piece `knowledge/piece_L12f2b.json`. Then the old inputs replay 1:1 through the Hornhead and the lap; the walker's
  dice differ -> rngfit splice from before the walker (`piece_L12f2_6480/6420.json`, RNGFIT_LOOSEALL=1 XTOL=2).
  The x-32 pole (wait 16) reaches the wide platform at 6054 (-117) but lands elsewhere (camera 17 px off) - not used yet.
- **The top** (L12q3 8735): the 124 idle frames are a ride on the slow moving platform 0x5d (1.16 px/f) to x 313.
  Walking Left 72 frames on it instead: the old jump inputs from 8859 replay and the level ends at 9118 vs 9170 (-52).
- **Face 3**: the lower spring (0x36 H 4800) passes under our pole at 7450 (L12q3); dropping at 7412-7424 lands on it.
  The TAS launches from it and its camera reaches 1055 (face-4 spawn) at once; ours only reaches 1086 - open.
- Lift/springs are spawned by the camera at fixed x; the camera locks while a face is out. Never use
  `taskkill /FI "WINDOWTITLE eq none"` (did it again today; killed two searches).
- **Top patch verified on L12q3**: `l12toppatch.py L12q3 L12q4` -> L12q4 = 9,118 frames (-53), level 13 reached,
  toad unhurt. Queen re-solve `l13solve.py L12q4_end0 0 L13q4` running (guaranteed gain route: up13a = ... L12q4 L13q4).
- Walker on the spring (face-3 setup): `fightbeam.py` got FB_SPRING=1 (return goal = standing on the lower spring
  0x36 H 4800); fake segment logs/pbeam_F2W.json = face-2 prefix + q3 tail; run `fightbeam.py F2W 6456 6650-6720 62 wspring`.
- After face 4 the TAS rides the upper spring idle 32 f and pumps (110 f to the 4942 ledge vs our 143); replaying its
  inputs from our landing drops the toad off the spring (our landing offset differs); a scan found nothing. Parked (~33 f).
- Second pump for the wait-8 face-2 variant (face 5433): apex only 4458 (A after landing) / 4385 (A through landing). Parked.
- **L12f = 9,033 frames (L12q3 9,171, -138)**: face-2 piece (f2w_pre) + walker re-fought (`fightbeam.py L12q3 6540
  6772-6860 62 w2q` with FB_START=F2W_pre: 242 f) + exact sub-pixel join (`retjoin` RJ_SUB -> old 6789) + q3 tail;
  after face 4 `oldwalk2` re-sync (all waits 0-2) to the top platform, then walk Left 72 (level end 9033).
  Walker splices by rngfit failed: the walker spawns elsewhere for us (dice can't fix). Queen `L13f` solving;
  `up13_pipeline.py` assembles up13 = ... L12f L13f, renders. Expected 12:31.08 - 2.30 s = ~12:28.8 if the queen is ~1861.
- Face 3 via the TAS's walker-on-the-spring: the TAS's walker inputs do not reproduce (walker moves by RNG); our kill
  is 232 f vs TAS ~163, landing on the spring at 6919 (a lap late). Needs Select-steered walker dice - next.

### 2026-10-07 — **route up13: 12:28.60 from power-on — under the record (12:29.25) by 0.65 s**
`assemble.py up13 L1b L3u L3skipu L4c5 L6c L8c L9c L10t L11r L12f L13x1` = 47,064 frames, replay MATCH sha1 fdadd8f2,
0 banned presses. L12f = face 2 the TAS's way + re-fought walker + the top walked (-138 f); queen L13x1 1,854 (was 1,861).
Found while checking: every route since up11 had ONE Up+Down frame (L3skipu input 594, a level-transition frame);
replacing it with nothing gives the identical final RAM (sha1 fdadd8f2), so it is removed (backup pbeam_L3skipu.backup.json).
Queen pitfall: l13solve caches sections by name - a reused name (L13f) replayed 4-day-old sections and the toad died.
Next: faces 3/4 (prototype on L12f: face 4 at -77 f so far; the TAS's camera snap would give ~-175).
- **L12g = 8,880 frames (L12f 9,033, -153)**: `l12g.py` staged scan on L12f - ride the lower spring 118 f (face 3
  spawns at 6954 with the spring at x 412), TAS pump + Right+A to the x-32 pole (6971); drop 7358 onto the lower spring,
  pump 18, Left+A to the upper spring (7479); pump to the x-352 pole, face 4 at 7545 (L12f 7633). Then drop 7939 onto the
  upper spring, Right 32 + Right+A 72 -> the 4941 ledge at 8085 (L12f 8239); `oldwalk2` re-sync to the top, all waits 0.
  Queens L13y0/L13y1 solving; `up14_pipeline.py` validates and assembles up14 (expected ~12:26.1).
- 2026-10-07 evening: owner's call - "beat is beat". Final route **up13 = 12:28.60** (record 12:29.25). Work stopped.
  Parked, not verified: L12g (faces 3/4, -153 f, logs/pbeam_L12g.json, bookmark L12g_end0); queens L13y0/L13y1 had
  section 1 cached (724/740) when stopped. Resume with `l13solve.py L12g_end0 0 L13y0` + `up14_pipeline.py` if ever wanted.
- 2026-10-07 evening (later): owner changed their mind - finish up14 for a bigger margin. Queens L13y0/L13y1 resumed.

### 2026-10-07 — **route up14: 12:23.39 from power-on — 5.9 s under the record (12:29.25)**
`assemble.py up14 L1b L3u L3skipu L4c5 L6c L8c L9c L10t L11r L12g L13y0` = 46,751 frames, replay MATCH sha1 e2a1d2dc,
0 banned presses. L12g (faces 2, 3, 4 the TAS's/record's way + the top walked) 8,880 f; queen L13y0 1,694 f (lucky dice).
