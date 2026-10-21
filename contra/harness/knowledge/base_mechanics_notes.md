# Base rooms (stages 2 and 4): what the emulator showed (2026-10-11, NesHawk)

Shared by `s2_notes.md` and `s4_notes.md`. Everything here was watched in BizHawk/NesHawk through the tools in
`tools/s2_snip/` and is what `contra/stages/base_plan.py` (the room model) and `base_room.py` (the driver) rely on.
"T" = frames since the room's enemies appeared (T = 0 is the frame `$64` changes; for the first room of a stage it is
the stage's first frame + 1). Lag frames do not count in T (no game logic runs on them).

## Confirmed from the code notes
* Core opens (state `$9F` -> `$1F`) on T = 258 (normal), 146 (inner cores of Base 2 room 2), 242 (big core),
  33 (plated). A bullet arriving on that very frame hits.
* With Rapid a bullet can hit a wall target only on its arrival frame = press frame + 20.
* One Spread press = at most 1 damage on one wall target; two targets in reach of different pellets each take one.
* Walk-in: next room appears 195 frames after the last core's HP reaches 0 (cores-left counter 0 at +34,
  `$37` = 1 at +59, `$80` at +60, four steps of 34 frames).
* Plated core: HP 5, 5, 5 then 8 (23 hits). The reload takes one frame and a hit on the reload frame still counts.
  The plating's bullet box is the wide one (collision code 2, 22 px); the bare core's is 12 px (code 5).

## Things the code notes did not say, or had wrong
1. **Core X.** Cores sit at X = 128 where the notes say `$88` (136), 104 for `$68`, 152 for `$98`: the room tables'
   X nibble * 16 + 8 is the right edge, the enemy's X is 8 less. Positions are read from RAM, never from the table.
2. **Slot timing.** A pellet that hits frees its slot for a new press 27 frames after its own press, a pellet that
   misses after 28. All pellets of one press therefore come back together - except the one that hit, one frame
   early. A press on exactly that frame fires a single pellet. This one-frame difference is the only way to split
   the two 5-pellet groups into the small groups a 5-frame "hose" needs (10 slots, 28-frame flight: six groups).
   Soldiers at the back wall and open wall turrets are hit the same way as cores and split groups too.
   Measured consequence (model, confirmed in the emulator): an 8-HP core dies at T = 317 with no earlier hit on
   anything, 305 with one, 300 with two, 295 with three, 293 (the floor: 258 + 7 x 5) with four.
3. **Partial sprays.** A press creates min(5, free slots) pellets, always in the order centre, +4, -5, +9, -10 px
   (landing offsets at the wall). A single is always the centre pellet.
4. **Where pellets land.** Standing, facing right: centre pellet at floor(0.375 * X + 81); facing left or
   crouching: 2 less; airborne: 1 less. Arrival Y: 104 standing, 116 crouching, min(player Y, 152) - 40 airborne.
   So a core at Y 104 (box 99..110) needs standing shots, a core at Y 112 (Base 1 room 3, Base 2 rooms 2 and 4)
   needs **crouch** shots, and the core at Y 88 (Base 2 room 7) needs shots fired at jump height 123..134.
   A standing shot cannot hit a Y-112 core and a crouch shot cannot hit a Y-104 core.
5. **Bullet boxes** (from `collision_box_codes_04`, checked by the hits the driver gets): core / turret 12 x 12
   (X -5..+6, Y -5..+6 around the enemy), soldier X -5..+6, Y -12..+9, plating 22 x 22.
6. **Enemy slot order matters.** Enemies are processed from slot 15 down and each takes the highest-numbered
   pellet in its box; a soldier in front of a core (higher slot) eats the pellet first. New soldiers take the highest
   free slot, so their slot depends on what was killed before.
7. **The 50-frame hop.** After every walk-in Bill is forced to hop for 50 frames (T = 0..50); standing shots are
   possible from T = 51 (first arrival T = 71). Shots during the hop are airborne shots; they can hit the wide
   plating box, which is how the plated rooms get hits before T = 71.
8. **Fence trick.** Touching the fence early (Up held from before the clear) starts the walk on the same frame as
   pressing Up on the frame after `$37` first reads 1: both reach the next room 195 frames after the last hit.
   Pressing Up only after `$37` reads `$80` is one frame slower. The trick gains nothing for a frame-exact player
   and exposes Bill (standing, stunned) to bullets; the driver presses Up on the frame after `$37` = 1.
9. **Lag.** Base 1 room 4 (rollers + group of four soldiers + bullets) has lag frames (8 in the first legal run);
   the driver treats a lag frame as "the frame did not happen" and repeats its input.
10. **Grenade launcher soldier (type `$17`)** walks to a spot that depends on where Bill stands (it stood on top of
    a core in Base 2 room 2 and ate the pellets). Its recorded path is not trusted; when the emulator shows it
    somewhere else the driver adds it to the model there and re-plans.
11. **Group-of-four soldiers (type `$18`)** are all created on one frame at X 88 and walk out one every 6 frames.
12. **Dropped presses.** On some frames the game does not see a new press (DMC conflict); the driver notices that no
    bullet appeared, forbids that frame and re-plans.
13. **Stage-start drop.** At a stage's first room Bill lands at T = 32 at X 112; one frame of Right during the drop
    makes him drift (X 144 on landing). The driver does not steer during drops and hops.

# Second pass (2026-10-12): the two boss screens

Everything in this section is implemented in `contra/stages/base_bsim.py` (an offline model of a base boss screen,
one `step()` per game frame) and was checked frame by frame against RAM captures of real fights with
`python tools/s4_simcheck.py <stage> <capture>`: player, all ten bullet slots, platings, wall cannons, the Eye and
its rings, the two helmets. Result: 594 of 594 frames of the first builder's stage 4 fight and 366 of 366 frames of
his stage 2 fight reproduce exactly (the only differing frame is the one on which the boss-defeated routine removes
everything), and so do the fights of this pass. `tools/s4_hzcheck.py` checks the frame on which a cannon bullet
kills Bill (3 captured deaths: same frame in the model).

## Frame order and the shot (boss screens use the outdoor bullet code)
* Per frame: aim from THIS frame's d-pad -> fire (new B press) -> bullets move -> Bill moves -> enemy slots 15..0,
  each: its routine, then at most ONE bullet is consumed (bullet slots searched 9 down to 0).
* A shot leaves from Bill's position BEFORE this frame's move. Muzzle (dx, dy): standing up (-1, -24), up-right
  (+15, -16), up-left (-15, -16), right/left (+-16, -6); jumping up (0, -16), diagonals (+-15, -15), right/left
  (+-16, 0). On the frame A is pressed the standing muzzle is still used. No d-pad = straight up (on these screens).
* One press = min(5, free slots) pellets into the LOWEST free slots, in the order centre, +1, -1, +2, -2 steps of
  11.25 degrees. Speed 3.48 px/frame (table `s_bullet_*_vel_rapid_fire_tbl`). A new pellet sits at the muzzle on its
  first frame and can already hit there.
* The sub-pixel accumulators of a bullet slot ($0398/$03A8 + slot) are NOT cleared when a bullet is created: a
  pellet's path depends by up to a pixel on what flew in that slot before. The model keeps them.
* A pellet that hits keeps its slot for 6 more frames (free for a press 7 frames after the hit); one that misses
  keeps it until X < 5, X >= 251, Y < 5 or Y >= 232.
* Every boss part (plating, cannon, Eye, helmet) has the 22 x 22 bullet box: bullet X in [x-10, x+11], Y in
  [y-10, y+11]. The Eye's ring: 34 x 34.
* A shut plating (HP $F0), a shut cannon (HP $F1) and the wreck of either on the frame after its last hit all
  CONSUME bullets (no damage). The cannon in stage 4 sits at (128, 80), straight above the middle plating and
  between the helmets: it eats every pellet that goes up the middle.

## Bill on the boss screen
* Jump: A press frame = no move; then vy = -4.0625 px/frame, +0.1367 per frame; peak 59 px (y 142) on air frame 29;
  he lands on the first frame with vy >= 0 and y > 200 (air frame 59), y snaps to 201. X = 1 px/frame, also on the
  landing frame; in the air the last direction persists (he cannot stop, only reverse). X range 31..224.
* The forced hop at the room load can be steered like any jump (the first builder waited for the landing).
* The game does not read the pad on some frames (NesHawk's DMC conflict: it re-uses the previous frame's
  buttons). WHICH frames depends on the inputs (probed with Select toggled every frame: the first one came 148
  rows into the room with no shooting, 153 rows with a plan's shooting). A changed button on such a frame arrives
  a frame late: that happened 1-4 times per fight of about 340 rows.

## Timers ("boss row" = rows counted from the row on which the boss room appears, that row being 1; the room load
## costs 8 lag rows, so game time T = boss row - 9)
* Platings: HP 10 from boss row 142 (T = 133). Only two background tiles can be drawn per frame, so with three or
  four platings the last ones open a frame later: stage 4 slots 11, 10 (left, middle) on row 142, slot 9 (right) on
  143; stage 2 slots 13, 11 (upper middle, left) on 142, slots 10, 9 (lower middle, right) on 143.
* The wreck is drawn (and the destroyed count goes up) on the frame after the last hit; the final part (Eye /
  helmets) counts 64 frames from there: it can be hit from (last plating hit) + 65.
* Wall cannon: opens (HP 8) on boss row 102 for 64 frames, fires three bullets on row 106, shuts on row 166, opens
  again on row 292 (fires 296), and so on every 190 frames. Its bullets have fixed velocities: (-0.9375, +1.613),
  (0, +1.859), (+0.9375, +1.613) px/frame from (x-8 / x / x+8, y+8). They kill Bill when the bullet is at
  dx in [-6, 7] and dy in [-16, 18] of him standing, dy in [-2, 11] jumping (bullet minus Bill; collision code 5).
  A destroyed cannon never fires again.
* Exit: from the frame the boss-defeated flag is set the stage ends a fixed time later (stage 4: 804 frames, stage
  2: 784-786) as long as Bill stands at x <= about 170 when the end sequence starts 139 frames after the flag (he
  walks to x 31 with Left held, then the game walks him to the lift at x 12). There is nothing to gain there:
  the first builder's "exit loses 20 frames in stage 4" is the stage itself (it is 804 with Bill waiting at the
  left edge 29 frames early).

# Third pass (2026-10-12): the rooms again, and two things about the Eye

Measured in NesHawk with the snippets `tools/s4t_snip/a1.py` .. `a6.py`, `lag1.py` (run through
`tools/s2_daemon.py`); implemented in `contra/stages/base_plan3.py` (planner) and `base_room3.py` (driver).
"Row T" = the input row that produces the state at room frame T.

## Bill's x is free from the frame the previous room's last press is made (the first driver never used it)
* **Entry x = exit x.** Bill enters a room with the x he had when he pressed Up at the fence (182 -> 179/180,
  122 -> 122, 107 -> 107, 208 -> 205: a few pixels of perspective at the far right only). The room is cleared 58-59
  frames after the last hit and the last bullets fly 20 frames, so he has about 76 frames to walk anywhere within
  66 px before the walk-in, for nothing.
* **The 50-frame hop (and the stage-start drop) is steered** by a 2-frame tap of Left/Right from row 2 on: he
  drifts 1 px per frame until he lands (a tap of the other direction reverses, nothing stops him), X range 48..208.
* **He walks while B is pressed and held** (x changes on every frame of a walk whatever B does). A press on row T
  is fired from the x he has BEFORE that row's move, with the facing the row's d-pad gives him (a Left press turns
  him on its first frame). Landing x of the centre pellet: standing or walking `(3x + 648) // 8`, 2 less facing
  left or crouching (as before); in the air `(3x + 640) // 8` whatever the facing.
* **The hop's height:** y is 168 on the ground, 126 at the top (T = 26); an airborne shot arrives at
  `min(y, 152) - 40`, so the 22-px plating box (Y 104) is reached from rows 13-16 and from row 38 on, not from
  rows 17-37; the stage-start drop reaches it from row 25 (y 137; Bill is still too high before).
* **He can fire during the walk-in** between two rooms (rows after Up at the fence): the pellets fly, free their
  slots 22 frames after the press (not 27/28) and those still in the air when the next room appears go on flying in
  it (fired at T = -7: arrival T = 14). Nothing can be hit there, so a split hose can be KEPT through the walk-in
  (one press every 5 frames, 87 presses to carry it to the next core's T = 238) but nothing can be split. Not used:
  rule v2 allows 109 presses in 600 frames and such a carry is 12 a second for 430 frames on top of two hoses.

## What the slots allow (exact search of the abstract model, `tools/s4t_hose.py`)
* One target that every press hits, all ten slots free at the first press: the 23rd hit lands 134 frames after the
  first one (22 x 5 = 110 would be the press cap alone); the 8th after 59, the 16th after 99. Counting argument:
  the first two presses take all ten slots (5 + 5), nothing is free for 27 frames, and the next 27 frames can only
  hold four presses (1, 4, 1, 4), so the 7th press cannot come before frame 54: 24 frames lost, then one hit per 5
  frames. **Stage 4 room 1's floor is therefore T = 25 + 20 + 134 = 179 (what we have), not 143.**
* Two plated cores side by side (stage 4 room 3): one press hits both with 2 pellets while at least one still has
  its plating (22-px box), with 3 pellets (centre, +4, -5) when both are bare. Ten pellets per 27 frames bound the
  plating part to 10 hits per 27 frames; the planner's best is last hit T = 206 (beam 12,000 and 50,000 give the same).
* Two cores 48 px apart (stage 4 rooms 2 and 5): the centre pellet reaches a core from 32 px of floor, the +9 / -10
  pellets of a 4- / 5-pellet press from 26 px further out, so the walk between "last press on one" and "first press
  on the other" can be as short as 46 px (152 -> 106) at the price of two big sprays, or 73 px with small ones.

## Lost controller reads in the rooms
* About 1 row in 60-100 is not read ($F1 keeps the previous row's buttons). Which rows depends on everything played
  before (it is deterministic: the same rows before T lose row T again), so a different plan moves them.
* A lost B press fires one frame late (B is held two frames); in a hose that usually merges two bullet groups.
  The driver sees it on the frame ($F1 against the row sent) and plans only the rest of the room again, keeping the
  rows up to 24 frames before the loss; a lost read that changes nothing (same Left/Right, no new press) is ignored.

## Lag (stage 2 room 4)
* Lag rows come when all 16 enemy slots are in use (six rollers, the group of four soldiers, bullets: T = 192..265)
  and nine or ten of our pellets are in the air, mostly on press frames. Two plans with the same last hit (T = 293)
  had 4 and 12 lag rows; the planners do not model it. `s2.solve` plays the first driver's plan too for a room
  with 3 or more lag frames and keeps the shorter room.

## The Eye
* It moves 1.25 px per frame on every frame it was not hit the frame before and Bill moves 1 px per frame: a line
  that stops hitting it for 20-30 frames has to wait for it to come back from the wall. The generic planner's
  ranking now has a term for Bill's distance from the Eye (`base_bfight.make_planner`, `far`).
* Slots can be prepared during the 64-frame wait: sprays fired then fly through the shut Eye and free their slots
  pellet by pellet 22-57 frames later depending on aim and x (`tools/s2t_eye1.py exits`; e.g. ground x 128 straight
  up: 50, 51, 51, 54, 33 frames). With two such sprays and the jump started 40 frames before the opening, the first
  jump makes 9 hits in the 20 frames after the opening (second pass: 6) - and then the Eye runs away (see
  `s2_notes.md`, third pass, for why this is only an extra candidate).
