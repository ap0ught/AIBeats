# Contra (NES, US) - enemies, bosses, stage logic, randomness (from the disassembly)

Source: `dl\nes-contra-us\src\*.asm` (read only). Every claim: label + `file:line`.
Hex is written `$xx`; decimal follows in brackets where useful. "inference" = deduced, not read literally.
CURRENT_LEVEL is 0-7 (stage N = CURRENT_LEVEL N-1). A run from power-on has GAME_COMPLETION_COUNT = 0.
Status: complete pass over bank0 (enemy code), bank2 (level data, soldier generation) and the enemy engine in bank7.
Frame counts labelled "derived" come from stepping the routines by hand - verify them in the emulator (section I).

## A. Generic enemy system

### A1. Per-frame order (level_routine_04, bank7.asm:3184)
1. `check_for_pause` - if PAUSE_STATE != 0 the routine exits: NO game logic runs (bank7.asm:3185-3187).
2. If BOSS_DEFEATED_FLAG != 0 -> switch to level_routine_08 (end-of-level sequence) (bank7.asm:3188-3189).
3. `set_frame_scroll_draw_player_bullets` (player logic, input, player bullets) (bank7.asm:3196).
4. `run_level_enemy_logic` (bank7.asm:3205): handle_scroll -> `exe_all_enemy_routine` -> `load_screen_enemy_data`
   -> `exe_soldier_generation` -> palettes -> alternate tile loading.

So enemy routines see the player position/bullets already updated this frame, and a screen-table enemy created
this frame first runs NEXT frame.

### A2. exe_all_enemy_routine (bank7.asm:7345)
Slots are processed from $0f (15) DOWN to 0. For each slot with ENEMY_ROUTINE != 0:
1. run the enemy's current routine (`exe_enemy_routine`, bank7.asm:7390). ENEMY_ROUTINE is 1-based (routine_00 = 1).
2. if ENEMY_SPRITES != 0 and ENEMY_STATE_WIDTH bit0 = 0 -> `check_players_collision` (bank7.asm:7371).
   (Indoor levels: only when ENEMY_Y_POS >= $9c, bank7.asm:7363-7365.)
3. if ENEMY_STATE_WIDTH bit7 = 0 -> `bullet_enemy_collision_test` (bank7.asm:7376). Note this is skipped when
   ENEMY_SPRITES = 0 (bank7.asm:7358-7359) - an enemy with sprite code 0 cannot be hit at all.

ENEMY_STATE_WIDTH bits (bank7.asm:8401-8438, 7074, 7575, 7650): bit7 = bullets pass through (no bullet test);
bit0 = no player collision; bit2 = play hit sound; bit1 = play explosion sound; bit3 = explosion type;
bits4-5 = collision box selector; bit6 = player can land on it.

### A3. Bullet -> enemy damage (THE damage rule)
`bullet_enemy_collision_test` bank7.asm:6954, `bullet_collision_logic` bank7.asm:7053.
* Loops player bullet slots $0f..0; the FIRST bullet inside the enemy box is processed and the routine RETURNS
  (bank7.asm:7032-7036). => **at most ONE bullet damages a given enemy per frame**, whatever the weapon.
* Damage is always exactly 1: `sbc #$00` with carry clear (bank7.asm:7061). There is NO per-weapon damage value.
  PLAYER_WEAPON_STRENGTH never enters the damage path; it only scales some enemy HP at spawn, the soldier
  generation timer, soldier bullet counts and the wall-cannon close time (see C).
* ENEMY_HP = 0 -> ignored (already dying). ENEMY_HP >= $f0 -> no damage (bank7.asm:7057-7060) but the bullet is
  still consumed (`set_bullet_routine_to_2`, bank7.asm:7033). $f0 = "no hit", $f1 = "hittable, no damage"; the only
  functional difference is `destroy_all_enemies` skips exactly $f0 (bank7.asm:8169-8170).
* HP reaches 0 -> `add_enemy_score_set_enemy_routine` (bank7.asm:7998): adds score, then sets ENEMY_ROUTINE to the
  enemy's "destroyed" routine index from `enemy_destroyed_routine_ptr_tbl` (bank7.asm:8078-8146) unless the enemy
  is already at a later routine. The destroyed routine runs on the NEXT frame.
* A bullet must be in PLAYER_BULLET_ROUTINE = 1 to hit (bank7.asm:6967-6969). Horizontal distance
  |enemy X - bullet X| must be < $80 (bank7.asm:7002-7011).
* Indoor rooms (LEVEL_LOCATION_TYPE bit0 = 1): if ENEMY_STATE_WIDTH bit5 = 0 the bullet only counts when
  PLAYER_BULLET_TIMER < 2 (bank7.asm:6979-6982), i.e. when the shot has finished travelling "into" the screen;
  if bit5 = 1 (rollers) only bullets with PLAYER_BULLET_SLOT bit7 set count (bank7.asm:6973-6977).
  (Bullet travel timing itself belongs to the player-code agent.)
* Laser (PLAYER_BULLET_SLOT = 5): on a hit, the routine destroys the FIRST still-flying segment of that player's
  laser (slots 0.. or $0a..), not necessarily the segment that hit (bank7.asm:7014-7033). So one laser shot can
  deliver several 1-damage hits on consecutive frames (one per remaining segment still overlapping).
* Barrier (INVINCIBILITY_TIMER != 0): touching an enemy with 0 < HP < $f0 sets its HP to 0 and runs the
  destroyed routine (bank7.asm:6869-6878) - this INSTANTLY KILLS ANY enemy with a real HP value, including bosses
  whose ENEMY_HP holds real HP and that have player collision enabled (inference from the code path; verify per boss).
* Falcon / boss kill: `destroy_all_enemies` (bank7.asm:8150) puts every enemy that has a sprite, is not type 2/3
  (pill box, capsule) and has HP != $f0 into its destroyed routine and sets ENEMY_ATTRIBUTES bit7.

Destroyed-routine flow for ordinary enemies (bank7.asm:7574-7719): `enemy_routine_init_explosion` (1 frame, sets
state bits $81 = no collision of any kind, sound_19 if state bit1) -> `enemy_routine_explosion` (1 + 10 x N frames;
N = 3 sprites if state bit3 = 0, 4 if bit3 = 1) -> `enemy_routine_remove_enemy` (slot freed). So a killed enemy keeps
its slot for 33 (N = 3) or 43 (N = 4) frames after the kill frame (derived).

### A4. Enemy slots, spawning from the screen tables (load_screen_enemy_data, bank2.asm:1517)
* 16 slots ($0f..0). `find_next_enemy_slot` (bank7.asm:9101) takes the HIGHEST free slot. Random soldiers may only
  use slots 6..0 (`find_next_enemy_slot_6_to_0`, bank7.asm:9094).
* Outdoor levels (bank2.asm:1538-1612): one table entry (plus its repeats) is processed per frame. Entry
  `XX TT YY`: created when `LEVEL_SCREEN_SCROLL_OFFSET >= (XX & $fe)` while LEVEL_SCREEN_NUMBER = table index.
  - Horizontal: ENEMY_Y = YY & $f0, ENEMY_X = $f0 - (offset - (XX&$fe)) (bank2.asm:1597-1604). So it appears at
    screen X = $f0 (240); its world X = screen*256 + (XX&$fe) + 240. Attributes = YY & $0f (bank2.asm:1585-1587).
  - Vertical (stage 3): ENEMY_X = YY & $f0, ENEMY_Y = overshoot (normally 0 = top of screen)
    (bank2.asm:1590-1594). XX is the vertical scroll offset within the screen at which it appears.
  - Entries are ordered by XX and read sequentially via ENEMY_SCREEN_READ_OFFSET; an entry is never re-read.
  - No free slot: if XX bit0 = 0 the enemy is silently DROPPED (bank2.asm:1575-1577); if XX bit0 = 1 it steals the
    slot of an enemy bullet (`find_bullet_slot`, bank7.asm:9114) or, if there is no bullet, slot 0 (bank7.asm:9123).
    All bosses/mandatory targets have odd XX.
* Indoor levels (bank2.asm:1620-1684): on room entry (ENEMY_SCREEN_READ_OFFSET = 0) ALL enemies are removed
  (`remove_all_enemies`), INDOOR_ENEMY_ATTACK_COUNT, WALL_PLATING_DESTROYED_COUNT, INDOOR_RED_SOLDIER_CREATED,
  GRENADE_LAUNCHER_FLAG are cleared, byte 0 of the room table -> WALL_CORE_REMAINING, then every listed enemy is
  created at once into slots $0f downward. Position byte `YX`: Y = Y*16 (+8 if type byte bit7),
  X = X*16 (+8 if type byte bit6) (bank2.asm:1659-1677; the code adds 7 + carry = 8).
* Despawn: most enemies call `add_scroll_to_enemy_pos` / `update_enemy_pos` and are removed when X < 8
  (horizontal) or Y >= $e8 (232) (vertical, and falling off the bottom) (bank7.asm:7771-7802, 7861-7883).

### A5. ENEMY_ATTACK_FLAG (bank7.asm:3925, 4064-4079)
Cleared every frame, then set to 1 only if some player has NEW_LIFE_INVINCIBILITY_TIMER = 0 AND PLAYER_STATE = 1
(normal). While it is 0: no random soldiers (bank2.asm:1963), no enemy bullets
(`create_enemy_bullet_if_attack_enabled`, bank7.asm:9913-9919), wall cannons do not open (bank7.asm:9373), and
several bosses hold their timers (noted per boss below). At the start of every stage (player dropping in +
new-life invincibility) nothing attacks.

### A6. Boss-defeated chain (common to all stages)
* `level_boss_defeated` (bank7.asm:8384): play sound A, DELAY_TIME_LOW_BYTE = $ff, BOSS_DEFEATED_FLAG = 1. Nothing else.
* `boss_defeated_routine` (bank7.asm:7566) = init_APU_channels + `level_boss_defeated`(sound_57) +
  `destroy_all_enemies` + falls into `enemy_routine_init_explosion`. Used by stage 1 door, stage 2 eye, stage 3
  mouth, stage 4 gemini (2nd helmet) and stage 7 door. The stage 5, 6 and 8 bosses call `level_boss_defeated`
  themselves (see each stage).
* The boss's "destroyed" routine runs the frame AFTER the killing bullet registered, so BOSS_DEFEATED_FLAG becomes 1
  on (hit frame + 1) (+ more if the boss has an intermediate routine - noted per boss).
* Next frame level_routine_04 sees the flag and switches to level_routine_08 (bank7.asm:3188, 3366); on that one
  switch frame no player or enemy logic runs at all (`bne set_to_level_routine_08` returns). level_routine_08
  keeps running player + enemy logic every frame. While DELAY_TIME_LOW_BYTE = $ff it only waits (bank7.asm:3374-3377:
  `iny / beq exit`). The $ff is a "boss still exploding" sentinel.
* Each boss's LAST explosion routine calls `set_delay_remove_enemy` (bank7.asm:8393) with a per-boss value D
  (DELAY low = D, high = 0). level_routine_08 then decrements once per frame and continues ~D+1 frames later
  (requires at least one player in PLAYER_STATE 1) -> sound_46 and the end-of-level sequence.
  => kill-to-level-end time is FIXED per boss (explosion animation + D); the only variable part is nametable draws
  being refused when CPU_GRAPHICS_BUFFER is full (see A7). Per-boss D is listed in each stage section and in C2.

### A7. Background-drawn enemies and CPU_GRAPHICS_BUFFER
Enemies drawn as background tiles (pill boxes, turrets, cores, platings, bosses) call `draw_enemy_supertile_a`
(bank7.asm:8615) / `update_enemy_nametable_tiles` (bank7.asm:8703). These FAIL (carry set) when
GRAPHICS_BUFFER_OFFSET >= $40 (super-tile, bank7.asm:1353-1355) or >= $50 (tiles, bank7.asm:1650-1652); the enemy then
retries next frame (ENEMY_ANIMATION_DELAY forced to 1, bank7.asm:8600-8606). State changes that are coupled to the draw
(pill box becoming hittable, plating HP set, core opening, "destroyed" tile + counter increments) slip by one frame
per failed draw. Slots are processed high->low, so the higher slot wins the buffer.

## B. Stage by stage

### B1. Stage 1 Jungle (CURRENT_LEVEL 0) - level_1_enemy_screen_xx, bank2.asm:2275-2342
World X of an entry = screen*256 + XX + 240 (it is created at screen X $f0 when scroll offset reaches XX).

| scr | XX | Y | enemy | attr | note |
|---|---|---|---|---|---|
| 0 | $10,$40,$80 | $60 | soldier x3 | 0 | run left, no shooting |
| 0 | $50 | $c0 | sniper | 0 | |
| 0 | $60 | $a0 | **pill box M** | 1 | bank2.asm:2279 |
| 0 | $f0 | $40 | **flying capsule R** | 0 | bank2.asm:2281 |
| 1 | $90 | $c0 | sniper | 0 | |
| 2 | $20 | $80 | exploding bridge 1 | | |
| 3 | $40 | $80 | exploding bridge 2 | | |
| 4 | $00 | $a0 | rotating gun | 0 | HP 8 |
| 4 | $10,$50 | $60 | sniper x2 | 0,1 | |
| 4 | $60 | $40 | **flying capsule S** | 3 | bank2.asm:2300 |
| 5 | $20 | $40 | sniper | 1 | |
| 5 | $40 | $a0 | **pill box F** | 2 | bank2.asm:2305 |
| 5 | $80 | $80 | rotating gun | 0 | |
| 6 | $40 | $80 | rotating gun | 0 | |
| 7 | $20,$a0 | $a0,$40 | red turret x2 | 0,1 | HP 8 |
| 8 | $00 | $c0 | **pill box S** | 3 | bank2.asm:2319 |
| 8 | $50 | $80 | sniper | 0 | |
| 9 | $10 | $40 / $b0 | **flying capsule R** and **flying capsule L** | 0 / 4 | one entry with repeat, bank2.asm:2324 |
| 9 | $e0 | $80 | red turret | 1 | |
| $0a | $c0 | $c0 | rotating gun | 0 | |
| $0b | $40 | $c0 | rotating gun | 3 | 3 bullets per attack |
| $0b | $a8 | $80 | bomb turret (jungle bg) | 1 | HP $10 (16), optional |
| $0b | $b1 | $b0 | **plated door = boss target** | 0 | HP $20 (32) |
| $0b | $b4 | $50 | boss-screen sniper | 2 | HP 1, optional |
| $0b | $c0 | $80 | bomb turret (wall bg) | 0 | HP $10 (16), optional |

Boss arrival: LEVEL_STOP_SCROLL = $0b (bank2.asm:1401). When the player forces scroll on screen $0b with
LEVEL_SCREEN_SCROLL_OFFSET >= $a0, `set_boss_auto_scroll` (bank7.asm:6552) sets AUTO_SCROLL_TIMER_00 = $60 (96):
96 frames of forced 1 px/frame scroll (bank7.asm:5606-5615); the player is no longer scroll-locked at X=$80 and may
walk right during it (set_frame_scroll_if_appropriate exits, bank7.asm:5164-5168).
Boss-screen entries are created DURING the auto-scroll as offsets $a8, $b0 ($b1&$fe), $b4, $c0 are reached, i.e.
about 8, 16, 20 and 32 frames after the auto-scroll starts (one entry per frame).

Plated door (type $11, `boss_wall_plated_door_routine_ptr_tbl` bank0.asm:2183; props `$0c,$82,$20` bank7.asm:9269):
* ENEMY_HP = $20 (32) from creation, state bit7 = 0 => **vulnerable the moment it exists**, ~16 frames into the
  auto-scroll, while it is still at screen X $f0 and sliding left to its final X $a0, Y $b0. No open/close cycle, no
  dependence on the bomb turrets. Only the door must die.
* Kill chain: hit frame H (HP -> 0, routine := 3) -> H+1 `boss_defeated_routine` (BOSS_DEFEATED_FLAG = 1, all other
  enemies destroyed) -> 41-frame explosion -> clear sprite -> routine_05 -> routine_06 draws 8 tunnel tiles 8 frames
  apart (bank0.asm:2206-2239) -> `set_delay_remove_enemy($30)` (bank0.asm:2238). Derived total: end-of-level tune at
  about H+163.
Bomb turrets (type $10, bank0.asm:2082): HP $10; first shot after $20 frames, then $28 between shots; bomb X speed
index = RANDOM_NUM & 3 (bank0.asm:2121-2124). Their cannonballs (bullet type 1) ignore ENEMY_ATTACK_FLAG
(bank7.asm:9914-9917).

Exploding bridges (type $12, bank0.asm:2264): each bridge = 4 super-tiles (32 px each). Trigger: closest player
|X - bridge X| < $18 (bank0.asm:2274-2276). Then per section: tile + bg collision removed, 3 clouds 4 frames apart,
a 31-frame explosion, then the enemy moves +$20 px to the next section (bank0.asm:2288-2399). Section k loses its
collision at about 5 + 46k frames after the trigger (derived). The first section goes 5 frames after the trigger,
i.e. while the player is still ~7 px short of it: walking falls in the water; the remaining three sections collapse
slower (32 px per ~46 f) than the player runs (32 px per 32 f). Speed relevance = whether water or a jump is faster
(player-movement agent).

Pill box sensor (type $02, bank0.asm:503-657): created with HP $f0 (closed, absorbs bullets). Timeline from creation
(derived): 49 frames -> fully open, HP := 1 (bank0.asm:569); stays hittable 80 frames; closed 80 frames; repeats
(delays $20 initial, $08 per animation step, $40 hold: bank0.asm:521, 541, 558, 585). Deactivates for good when it
scrolls to X < $18 (bank0.asm:535-538). The HP change is coupled to a super-tile draw (A7). When shot it turns into
the weapon item in the same slot (bank0.asm:642-654).
Flying capsule (type $03, bank0.asm:674): HP 1, starts at X = $10 (left edge), Y = table Y + $20, moves right
1.5 px/frame with a sine in Y; always hittable. Weapon item (type $00): pops up (Y vel -3, X vel +0.5), gravity
+$10/256 per frame, lands on ground; picked up by touch (bank7.asm:6884).
Weapon attribute decode (bank7.asm:6895-6945): 0 = R, 1 = M, 2 = F, 3 = S, 4 = L, 5 = B (INVINCIBILITY_TIMER = $80,
$90 in stage 7; decremented every 8th frame, bank7.asm:6913-6920, 4083-4088), 6/7 = falcon.

### B2. Indoor base rooms (stages 2 and 4) - common rules
Room data: level_2_enemy_screen_xx bank2.asm:2366-2413, level_4_enemy_screen_xx bank2.asm:2535-2609.
Byte 0 = WALL_CORE_REMAINING. Enemies are all created on the frame the room becomes current (A4).

**Core (type $14, `wall_core_routine_ptr_tbl` bank0.asm:3128)**. Attribute: bit3 = big, bit2 = plated,
bits0-1 = opening delay index into `core_opening_delay` = $20,$80,$b0,$f0 (bank0.asm:3176); plated cores always use $20.
While closed the core has state bit7 set (props `$9f` bank7.asm:9279) = bullets fly through it, no damage possible.
HP (`wall_core_hp_tbl` bank0.asm:3184): normal 8; big $10 (16); plated 5 + 5 + 5 then 8 = 23 hits
(bank0.asm:3288-3316: each time HP hits 0 the plating tile steps down and HP is reloaded 5, 5, then 8).
Opening timeline, T = frames since the room was loaded (derived from bank0.asm:3141-3253; +1 per failed draw):

| core kind | attr | hittable from T = | HP |
|---|---|---|---|
| normal, delay idx 3 | $03 | $f0 + 18 = **258** | 8 |
| normal, delay idx 1 | $01 | $80 + 18 = **146** | 8 |
| big, delay idx 3 | $0b | $f0 + 2 = **242** (no opening animation, bank0.asm:3236-3238) | 16 |
| plated | $04 | $20 + 1 = **33** | 23 |

Once open a core never closes. It only shoots after INDOOR_ENEMY_ATTACK_COUNT >= 7 (bank0.asm:3264-3266).
There is NO room timer other than these opening delays.

Room clear chain (hit frame H = last core HP -> 0; derived from bank0.asm:3288-3417):
H+1 destroyed tile drawn -> 32 frames explosion -> `wall_core_routine_07`: WALL_CORE_REMAINING--; when 0:
`destroy_all_enemies`, then 4 back-wall super-tiles (first after 4 frames, then 1 per frame) -> $10 frames ->
**INDOOR_SCREEN_CLEARED = 1 at about H+57** (bank0.asm:3413-3414). Next frame `animate_indoor_fence` removes the
fence and sets INDOOR_SCREEN_CLEARED = $80 (bank7.asm:2931-2934).

Electric fence: pressing Up alone on the ground while INDOOR_SCREEN_CLEARED = 0 sets ELECTROCUTED_TIMER = $30 (48
frames of stun; bank7.asm:4590-4600). The stun is cancelled the moment the room becomes cleared (bank7.asm:4805-4812).
The fence cannot be passed early: the advance only starts when INDOOR_SCREEN_CLEARED != 0 (bank7.asm:4595-4596) and
the background transition only runs when it is $80 (bank7.asm:5776-5777).

Advance to the next room (bank7.asm:4602-4629, 5775-5881): hold Up (alone, on the ground, not jumping). Up sets
INDOOR_SCROLL = 1 and INDOOR_PLAYER_ADV_FLAG. Each of 4 sub-steps: LEVEL_TRANSITION_TIMER = $20, one tile column
written per frame for 32 frames, then 1 frame swap (INDOOR_SCROLL = 2, LEVEL_SCREEN_SCROLL_OFFSET++), then the player
routine ends the walk-in animation and Up must be seen again to start the next sub-step. Derived cost: 4 x 34 = about
135 frames from first Up to the 4th swap; input cannot shorten it, releasing Up lengthens it. On the 4th swap:
LEVEL_SCREEN_NUMBER++, ENEMY_SCREEN_READ_OFFSET = 0, INDOOR_SCREEN_CLEARED = 0, the player is forced to jump
(INDOOR_PLAYER_JUMP_FLAG, bank7.asm:5855-5861, 4457-4463) and the new room's enemies load the same frame.
When the new screen number equals LEVEL_STOP_SCROLL the room is the boss room (LEVEL_LOCATION_TYPE = $80,
bank7.asm:5862-5866).
Earliest Up that works is the frame INDOOR_SCREEN_CLEARED becomes non-zero, so be on the ground holding only Up then.

Per-room budget (derived): core-open wait T + hits + ~57 (clear) + ~2 + ~135 (transition).

Other room enemies (all optional):
* Wall turret (type $13, bank0.asm:3036): HP 4; opens after `wall_turret_initial_delay_tbl[attr]` = $50,$80,$b0,$f0
  (all placed turrets use attr 0 = $50) + 3 draws 8 frames apart; hittable only when open; first shot $80 later, then
  every $50.
* Indoor soldier generator (type $19, bank0.asm:2406): timer decremented only on ODD FRAME_COUNTER frames and frozen
  while a grenade launcher is alive (bank0.asm:2422-2428). First enemy 2 x $40 = 128 frames after room load, then
  2 x (delay byte) frames between entries of lvl_x_enemy_gen_screen_xx (bank0.asm:2546-2663). The generator removes
  itself after 7 passes (INDOOR_ENEMY_ATTACK_COUNT = 7, bank0.asm:2462-2467). It is NOT a hittable enemy (HP $f1).
* Red jumping soldier = the only weapon source in the bases (bank0.asm:3546-3559, 3648-3663): a jumping-soldier entry
  with attr bit1 set becomes red only if INDOOR_ENEMY_ATTACK_COUNT >= 1 (i.e. from the entry that ends the first pass
  onward) and no red one was made in this room yet. Weapon = attr bits 2-4. It only drops the item if killed with
  $64 <= X < $9c.
* Rollers (type $11, HP 5), roller generator (type $1a, first roller after 2 x $60 frames, odd frames only,
  bank0.asm:3908-3920), grenades, grenade launcher (type $17), group of four (type $18): HP 1 each.

Earliest red-soldier spawn per room, T after room load (derived from the generator tables; +-2 frames):

| stage / room (screen) | weapon | earliest T | table line |
|---|---|---|---|
| 2 / room 1 (scr 0) | R | ~354 | bank0.asm:2547 |
| 2 / room 2 (scr 1) | M | ~736 | bank0.asm:2553 |
| 2 / room 3 (scr 2) | none | - | bank0.asm:2562 |
| 2 / room 4 (scr 3) | M | >= ~578 | bank0.asm:2567 |
| 2 / room 5 (scr 4) | F | ~736 | bank0.asm:2580 |
| 4 / room 1 (scr 0) | none | - | bank0.asm:2596 |
| 4 / room 2 (scr 1) | F | ~896 | bank0.asm:2606 |
| 4 / room 3 (scr 2) | L | ~1150 | bank0.asm:2619 |
| 4 / room 4 (scr 3) | B | ~896 | bank0.asm:2625 |
| 4 / room 5 (scr 4) | R | ~416 | bank0.asm:2635 |
| 4 / room 6 (scr 5) | S | ~832 | bank0.asm:2640 |
| 4 / room 7 (scr 6) | F | ~704 | bank0.asm:2650 |
| 4 / room 8 (scr 7) | M (attr $47; the source comment says R, the bits say M) | ~864 | bank0.asm:2659 |

A fast clear kills the core at T ~ 260-270, so every base weapon costs at least ~90 frames of waiting (stage 2
room 1 R) and usually 400+; they are effectively not on the speed route.

### B3. Stage 2 Base 1 (CURRENT_LEVEL 1) - rooms
Position decode: Y = hi nibble*16 (+8 if type bit7), X = lo nibble*16 (+8 if type bit6).

| room (scr) | cores needed | contents (type, X, Y, attr) |
|---|---|---|
| 1 (0) | 1 | soldier gen; core $03 at X$88 Y$68 (opens T=258, HP 8) |
| 2 (1) | 1 | soldier gen; core $03 at X$68 Y$68 (258, HP 8); wall turret X$98 Y$68 |
| 3 (2) | 1 | soldier gen; core $03 at X$80 Y$70 (258, HP 8); wall turrets X$68 Y$68 and X$98 Y$68 |
| 4 (3) | 1 | soldier gen; roller gen; wall turret X$80 Y$58; core $03 at X$88 Y$68 (258, HP 8) |
| 5 (4) | 1 | soldier gen; BIG core $0b at X$88 Y$68 (242, HP 16); wall turrets X$68 Y$68, X$98 Y$68, X$80 Y$50 |
| boss (5) | (1) | boss eye X$80 Y$40; wall cannons X$50 Y$60 and X$b0 Y$60; platings X$80 Y$60 (attr 1), X$50 Y$90, X$80 Y$90, X$b0 Y$90 |

(bank2.asm:2366-2413.) LEVEL_STOP_SCROLL = 5 (bank2.asm:1417).

Stage 2 boss (boss screen, LEVEL_LOCATION_TYPE = $80 so bullets use the outdoor collision rule):
* Wall plating x4 (type $0a, bank7.asm:9478-9524): closed (HP $f0, absorbs bullets) for $80 frames, then two draws
  4 frames apart; **HP = $0a (10) from T = 133** after the boss room loads (derived; bank7.asm:9489-9508). Never
  closes. Destroyed routine draws the wreck tile then WALL_PLATING_DESTROYED_COUNT++ (bank7.asm:9517-9521; the count
  only increments when the draw succeeds).
* Wall cannon x2 (type $08, bank7.asm:9346-9472): optional. Real HP 8 kept in ENEMY_VAR_1; hittable only while open
  ($40 frames); stays shut $50 at first, then $c0 between openings if PLAYER_WEAPON_STRENGTH < 2, $60 if >= 2
  (bank7.asm:9456-9461). Does not open while ENEMY_ATTACK_FLAG = 0.
* Boss eye (type $10, bank0.asm:2666-2799): waits until WALL_PLATING_DESTROYED_COUNT >= 4, then $40 (64) more frames
  (bank0.asm:2689-2694), then becomes hittable (`enable_enemy_collision`) with real HP $10 (16) in ENEMY_VAR_1
  (bank0.asm:2699-2701). ENEMY_HP is kept at 1; each hit runs boss_eye_routine_03 next frame (VAR_1--, HP back to 1)
  and the bullet test still runs that same frame, so **1 hit per frame is possible** (inference from A2 order).
  It moves horizontally at 1.25 px/frame between X $50 and $b0 at Y $40 (bank0.asm:2695-2698, 2736-2748); it does not
  move on frames spent in routine_03. No open/close cycle. Fire-ring delay by weapon strength: $70,$50,$40,$28
  (bank0.asm:2764).
* Kill chain: 16th hit at H -> H+1 routine_03 (VAR_1 = 0, advance) -> H+2 `boss_defeated_routine`
  (BOSS_DEFEATED_FLAG = 1) -> explosion -> `boss_eye_routine_06`: `set_delay_remove_enemy($60)` (bank0.asm:2796-2799).
* Minimum work: 4 x 10 + 16 = **56 hits**, plus fixed waits 133 (platings) and 64 (eye).

### B4. Stage 4 Base 2 (CURRENT_LEVEL 3) - rooms

| room (scr) | cores needed | contents |
|---|---|---|
| 1 (0) | 1 | soldier gen; PLATED core $04 at X$88 Y$68 (hittable T=33, 23 hits); wall turrets X$68 Y$68, X$98 Y$68 |
| 2 (1) | 4 | soldier gen; cores at Y$70: X$68 ($03, T=258), X$78 ($01, T=146), X$88 ($01, T=146), X$98 ($03, T=258); 8 HP each |
| 3 (2) | 2 | soldier gen; PLATED cores $04 at X$78 Y$68 and X$88 Y$68 (T=33, 23 hits each); wall turret X$80 Y$58 |
| 4 (3) | 2 | soldier gen; wall turret X$80 Y$60; cores $03 at X$78 Y$70 and X$88 Y$70 (T=258, 8 HP) |
| 5 (4) | 2 | soldier gen; cores $03 at X$68 Y$68 and X$98 Y$68 (T=258, 8 HP); wall turret X$80 Y$68 |
| 6 (5) | 1 | roller gen; soldier gen; core $03 at X$88 Y$68 (T=258, 8 HP) |
| 7 (6) | 1 | soldier gen; core $03 at X$80 Y$58 (T=258, 8 HP); wall turret X$80 Y$68 |
| 8 (7) | 1 | soldier gen; BIG core $0b at X$88 Y$68 (T=242, 16 HP); wall turrets X$80 Y$50, X$68 Y$68, X$98 Y$68 |
| boss (8) | 2 (gemini) | red/blue soldier gen; gemini helmets X$68 Y$30 and X$98 Y$30; wall cannon X$80 Y$50; platings X$50 Y$80, X$80 Y$80 (attr 1), X$b0 Y$80 |

(bank2.asm:2535-2609.) LEVEL_STOP_SCROLL = 8 (bank2.asm:1449). Several cores can be damaged on the same frame (one
bullet each).

Stage 4 boss:
* 3 wall platings, same rules as stage 2: HP 10 each from T = 133.
* Red/blue soldier generator (type $20, bank0.asm:6082): first group 2 x $80 frames after load, even frames only;
  removed as soon as the 3 platings are gone (bank0.asm:6091-6095).
* Gemini helmets (type $1c x2, `boss_gemini_routine_ptr_tbl` bank0.asm:5442): each has real HP $0a (10) in
  ENEMY_VAR_4 (bank0.asm:5453). They wait for WALL_PLATING_DESTROYED_COUNT >= 3 then $40 (64) frames
  (bank0.asm:5476-5481), then bullets collide.
  Cycle (bank0.asm:5554-5601): merged and hittable while ENEMY_ANIMATION_DELAY counts down - first window $20
  (31 hittable frames), later windows $30 (47 frames); then `disable_enemy_collision`, each helmet splits into two
  flickering phantoms (drawn at X0+off on even FRAME_COUNTER, X0-off on odd, bank0.asm:5605-5617) moving out to
  off = $30 at 0.5 px/frame (96 f), hold $20 (32 f), back in (~98 f), merged again. Period ~274 frames with 47 hittable.
  Hit handling: a hit sends the helmet to boss_gemini_routine_03 next frame (VAR_4--, ENEMY_HP back to 1,
  bank0.asm:5635-5663); the bullet test still runs that frame, so 1 hit per frame per helmet is possible, and while it
  is hit every frame routine_02 never runs: **the helmet neither moves nor closes** (inference from A2 order).
  Bug #3 (docs/Bugs.md:69-152) in practical terms: routine_03 decrements ENEMY_ANIMATION_DELAY without ever calling
  `disable_enemy_collision` (bank0.asm:5636-5638). If routine_03 is the one that takes the timer from 1 to 0 (a hit
  registered on the frame the timer was 2 at frame start, or any unbroken run of hit-frames that walks it down to 0),
  routine_02 then sees 0 and skips the disable (bank0.asm:5561): the helmet stays hittable while split and moving,
  until the far-apart hold ($20) expires (same trick works there). Gain: instead of waiting ~227 frames for the next
  merge, damage continues at the phantoms' per-frame position.
  With 10 HP per helmet the real optimum is simpler: land 10 hits on consecutive frames on each helmet inside the
  first 31-frame window (both helmets can be hit on the same frame) -> both dead ~10 frames after the first hit.
* Kill chain: helmet's 10th hit at H -> H+1 routine_03 (advance) -> H+2 `boss_gemini_routine_04`:
  WALL_CORE_REMAINING--; the second one calls `boss_defeated_routine` (BOSS_DEFEATED_FLAG = 1) -> explosion ->
  `boss_gemini_routine_06`: `set_delay_remove_enemy($60)` (bank0.asm:5669-5687).
* Gemini bubble attack delay = table[((RANDOM_NUM + FRAME_COUNTER) >> 1) & 3] ($8a,$a9,$63,$d7) - 8 x weapon
  strength, and this WRITES RANDOM_NUM (reseed, bank0.asm:5536-5550).
* Minimum work: 3 x 10 + 2 x 10 = **50 hits**, fixed waits 133 and 64.

### B5. Stage 3 Waterfall (CURRENT_LEVEL 2, vertical) - level_3_enemy_screen_xx, bank2.asm:2439-2508
Vertical entry `XX TT YA`: created at the TOP of the screen (Y = 0) when the vertical scroll offset within screen
`scr` reaches XX; X = Y-nibble*16; attr = low nibble (A4).

| scr | XX | X | enemy | attr / note |
|---|---|---|---|---|
| 0 | $08 | $20 | soldier | 1 |
| 0 | $22,$62,$82,$a2,$e2 | $30,$d0,$b0,$50,$90 | rock cave (boulder generator) | |
| 0 | $40 | $90 | **pill box F** | 2, bank2.asm:2442 |
| 0 | $48 / $68 | $20 / $30,$90 | soldiers | |
| 0 | $c0 | $90 | **pill box L** | 4, bank2.asm:2449 |
| 1 | $38 | $e0 | sniper | |
| 1 | $60 | $a0 | scuba diver | |
| 2 | $40 / $e0 | $f0 / $10 | rotating gun | HP 8 |
| 2 | $73 | $50, $b0 | moving flame x2 | attr 3 (right), 2 (left) |
| 2 | $80 | $e0 | sniper | |
| 2 | $d0 | $30 and $a0 | **flying capsule B** (X$30) and **flying capsule R** (X$a0) | 5 / 0, bank2.asm:2462 |
| 3 | $11 / $81 | $50 / $70 | floating rock platform | attr 0 / 1 |
| 3 | $20 | $20 | sniper | |
| 3 | $c0 | $10 | rotating gun | |
| 3 | $d0 | $50 | scuba diver | |
| 4 | $38,$88,$a8,$d8 | $70,$a0,$40,$80+$e0 | soldiers | |
| 4 | $50 | $e0 | scuba diver | |
| 4 | $60 | $b0 | **pill box S** | 3, bank2.asm:2477 |
| 4 | $a0 / $e0 | $f0 / $10 | rotating gun | |
| 5 | $20 | $10 | **pill box M** | 1, bank2.asm:2486 |
| 5 | $30 | $e0 | red turret | |
| 5 | $38 | $60 | soldier | |
| 5 | $40 | $30 | rotating gun | |
| 5 | $79 | $80 | floating rock platform | attr 1 |
| 6 | $28,$40,$58,$e8 | $c0,$10,$90,$60 | soldiers | |
| 6 | $78 | $20 | sniper | |
| 7 | $08 | $e0 | soldier | |
| 7 | $a8 | $50 (attr 1) and $b0 (attr 0) | dragon arm shoulder orbs | |
| 7 | $c1 | $80 | **dragon mouth = boss target** | |

Vertical flying capsule (bank0.asm:696-701, 717): starts at the BOTTOM (Y = $e0), X = table X + $20, rises 1.5 px/frame.

Hazards (bank0.asm:4280-4497):
* Floating rock platform (type $10): landable (state $c0), invulnerable. attr 0: X velocity -0.5 px/f between X $50
  and $b0; attr 1: +0.75 px/f between $70 and $c0 (tables bank0.asm:4304-4317); reverses at the bounds. A player on
  it gets the platform's per-frame movement as PLAYER_FAST_X_VEL_BOOST (bank7.asm:6804-6818).
* Moving flame (type $11): invulnerable, bullets pass through; +-0.5 px/f between X $48 and $b8. Not timer based.
* Rock cave (type $12): first boulder 8 frames after activation, then one every $e0 (224) frames
  (bank0.asm:4379-4391). Boulder (type $13): HP 5; wobbles $40 frames (not hittable, bit7), then falls and bounces
  (-1.25 px/f bounce, gravity $10/256).
* Scuba diver (type $0c, bank7.asm:9607): hittable only for $30 frames at a time while up; hidden $c0 frames.

Boss arrival: LEVEL_STOP_SCROLL = 7 (bank2.asm:1433). `set_vertical_level_frame_scroll` (bank7.asm:5236-5245): when the
player is above Y $50 and rising on screen 7 with scroll offset >= $c0, AUTO_SCROLL_TIMER_00 = $40 (64 frames at
1 px/f, bank7.asm:6577-6584, 5691-5700). The dragon entry ($c1) is created on that same offset.

Dragon mouth (Gromaides, type $14, `boss_mouth_routine_ptr_tbl` bank0.asm:4500):
* Real HP $20 (32) kept in ENEMY_VAR_1 while closed (bank0.asm:4513-4514).
* Closed = state bit7 set (bullets fly through) and ENEMY_HP = $f1: **cannot be damaged while closed**
  (props bank7.asm:9304; bank0.asm:4632-4636).
* First opening (derived, bank0.asm:4512-4557): routine_01 waits for BOSS_AUTO_SCROLL_COMPLETE and
  BG_PALETTE_ADJ_TIMER = 0, then counts $ff (255) frames; routine_02's first `dec` wraps 0 -> $ff, another 256 frames;
  then 2 draws 6 frames apart. **Hittable about 517 frames after the auto-scroll (and palette fade) finish.**
  Nothing the player does shortens this.
* Open window: ENEMY_ANIMATION_DELAY = $70 -> **112 frames** hittable; 3 fireballs 6 frames after opening.
* Close/re-open: 3 closing draws (18 f) + wait D + 2 opening draws (12 f), D = `boss_mouth_anim_delay_tbl`
  [arms destroyed] = $c0 / $70 / $20 for 0 / 1 / 2 arms (bank0.asm:4660-4679). So with both arms gone the closed gap
  is ~62 frames; with both alive ~222.
* Kill chain: H -> H+1 `boss_defeated_routine` (flag = 1) -> 41-frame explosion -> clear sprite ->
  `boss_mouth_routine_08` 14 tile draws on consecutive frames -> `set_delay_remove_enemy($60)` (bank0.asm:4697-4699).
  Derived: level end about H+156.
* Minimum: 32 hits inside one 112-frame window (1 hit/frame cap) - arms are then irrelevant.

Dragon arms (type $15, bank0.asm:4739-5440): each shoulder spawns 4 more orbs (1 per frame) once the auto-scroll is
complete; only the outermost red "hand" is hittable: HP $10 (16) (bank0.asm:4800-4805); other orbs have bit7 set.
Before extending, the hand waits $20 counts decremented on odd FRAME_COUNTER frames (64 f), then each orb slides out
for 16 frames (hand first) (bank0.asm:4857-4911). Killing a hand removes the whole arm
(`dragon_arm_orb_routine_04`, bank0.asm:5422-5440) and increments BOSS_SCREEN_ENEMIES_DESTROYED.
Arm attack pattern delay uses (RANDOM_NUM + FRAME_COUNTER) & 3 (bank0.asm:5077-5081).

**Freeze to AVOID (docs/Bugs.md:154-225; code bank0.asm:4893-4904):** when an arm finishes extending, the orb next to
the shoulder walks the linked list and blindly `inc`s every orb's ENEMY_ROUTINE. If the hand's HP reached 0 on the
frame just before (its routine was already set to the "destroyed" routine but had not run yet), it is pushed past
`dragon_arm_orb_routine_04`, the arm never self-destructs, the hand's slot is later reused by a fireball and
`@enemy_orb_loop`/the position loop never terminates = hard freeze. Rule for the bot: **never land the 16th hit on a
red hand on the frame immediately before that arm completes its extension** (about 4 + 64 + 64 frames after the
auto-scroll completes; watch the shoulder orb's ENEMY_ROUTINE change from 3 to 4 and keep the kill at least 2 frames
away from it). Killing a hand earlier during extension or any time after is safe.

### B6. Stage 5 Snow Field (CURRENT_LEVEL 4) - level_5_enemy_screen_xx, bank2.asm:2636-2751

| scr | XX | Y | enemy | attr / note |
|---|---|---|---|---|
| 0 | $20,$50,$d8 | $60 | ice grenade generator | |
| 0 | $60 | $80 | turret man (Basquez) | HP 10 |
| 1 | $00 | $80 | turret man | |
| 1 | $08 | $60 | ice grenade generator | |
| 1 | $80 | $a0 | **pill box M** | 1, bank2.asm:2646 |
| 2 | $60 / $c0 | $80 / $b0 | turret man x2 | |
| 3 | $20 | $50 | turret man | |
| 3 | $60 | $30 | **flying capsule R** | 0, bank2.asm:2656 |
| 3 | $d8,$f0 | $40 | ice grenade generator x2 | |
| 4 | $80,$c0 | $50 | ice grenade generator x2 | |
| 4 | $d0 | $80 | turret man | |
| 5 | $60 | $80 | **pill box F** | 2, bank2.asm:2668 |
| 6 | $40 | $30 / $70 / $b0 | **flying capsules R / FALCON / S** | 0 / 6 / 3, bank2.asm:2672 |
| 6 | $40 | $d0 | scuba diver | |
| 7 | $10 | $d0 | scuba diver | |
| 7 | $a0 | $80 | sniper | |
| 8 | $00,$40,$80,$c0 | $b0 | ice pipe joints (decor sprites) | |
| 9 | $01 | - | **TANK 1** (attr 2) | bank2.asm:2690 |
| $0a-$0c | | | pipe joints; turret man at scr $0b XX$a8 | |
| $0d | $01 | - | **TANK 2** (attr 3) | bank2.asm:2710 |
| $0e | $d0 | $a0 | turret man | |
| $0f | $60,$a0,$e8 | $50 | ice grenade generator x3 | |
| $10 | $60 | $a0 | **pill box L** | 4, bank2.asm:2727 |
| $11 | $00,$60,$c0 | $80 | ice grenade generator x3 | |
| $11 | $b0 | $80 | turret man | |
| $12 | | | pipe joints | |
| $14 | $01 | - | **boss UFO (Guldaf)** | bank2.asm:2748 |

Ice grenade generator (type $10, bank0.asm:6174): invisible, invulnerable; once its X < $c8 it throws a grenade every
$80 (128) frames (first one 1 frame after activation). Grenade: Y vel -2, X vel +0.5, gravity $0a/256; explodes on
ground. Pure own timers. Turret man (type $0e, bank7.asm:9527): HP 10; first shot after attr*16+1 frames, then every
attr*16+$30; bullet flies left 2.5 px/f.

Tanks (Dogra, type $12, `tank_routine_ptr_tbl` bank0.asm:6257):
* The tank is background tiles; it "drives in" because TANK_AUTO_SCROLL = FRAME_COUNTER & 1 forces 1 px of scroll on
  odd frames (0.5 px/f) on top of any player scroll (bank0.asm:6292-6294; bank7.asm:5617-5621).
* It starts at virtual X $130 and must reach X < $a0 (bank0.asm:6267-6270, 6298-6300): 145 px. Its X drops by
  FRAME_SCROLL + TANK_AUTO_SCROLL each frame (bank0.asm:6369-6377), so **a player who keeps scrolling right brings
  it in at 1.5 px/f (~97 frames) instead of 0.5 px/f (~290 frames)**.
* While driving in ENEMY_HP = $f0: it absorbs bullets and takes NO damage (props `$85,$79,$f0` bank7.asm:9310;
  collisions are switched on when it enters the screen, bank0.asm:6379-6387). **It cannot be killed before it stops.**
* On stopping (`tank_stop` bank0.asm:6348): TANK_AUTO_SCROLL = 0, **ENEMY_HP = $47 (71)** - not weapon scaled.
  It then stays stopped for 2 x timer frames (timer decremented on even FRAME_COUNTER frames): tank 1 timer $00 =
  256 counts = 512 frames; tank 2 $f8 = 496 frames (bank0.asm:6394-6405), firing 3-bullet bursts (first aim after
  8 frames, $30 after each aim, $20 between bullets, bullet speed code = attr 2 / 3). After that it drives on
  (auto-scroll resumes) and still has its HP.
* Touching it is lethal (player box X-44..X+44 for a standing player, `collision_box_codes_03` entry 9,
  bank7.asm:7318), so the player cannot stand at the scroll point X $80 once tank X <= about $ac.
* Destroyed (`tank_routine_04/05` bank0.asm:6554-6617): collisions off; TANK_AUTO_SCROLL keeps running
  (FRAME_COUNTER & 1) until the wreck has scrolled off the left edge (X wrapped and < $d0), then auto-scroll,
  PAUSE_PALETTE_CYCLE and TANK_ICE_JOINT_SCROLL_FLAG are cleared (bank0.asm:6531-6542). So after the kill the level
  keeps giving a free +0.5 px/f of scroll for ~208 px of travel.
* Hits: 71 each (>= 71 frames each at the 1-hit-per-frame cap). Mandatory in practice: a live tank is a lethal wall.

Boss UFO (Guldaf, type $14, `boss_ufo_routine_ptr_tbl` bank0.asm:6653):
* LEVEL_STOP_SCROLL = $13 (bank2.asm:1465): auto-scroll (96 f) starts at screen $13 offset $a0; the UFO entry is on
  screen $14 offset 0, so it is created when the auto-scroll ends.
* ENEMY_HP = $20 (32) from the property table (bank7.asm:9312); never parked. Vulnerability = state bits only.
* Cycle from the frame routine_01 runs (t0, ~2 frames after creation) (derived, bank0.asm:6679-6929):
  X = `boss_ufo_x_pos_tbl`[RANDOM_NUM & 3] = $40,$60,$80,$80; Y steps $30 -> $50 -> $70 -> $30...;
  4 frames drawing; $60 (96) frames; **collision on at about t0+100**; bays open; 255 frames of attacks (a bomb or a
  mini-UFO every 16 frames); bays close; **collision off at about t0+403**; $20 frames; invisible; 4 frames;
  $60 frames; new t0. => hittable ~303 frames, then ~232 frames not.
* Kill chain (bank0.asm:6935-7033): H+1 routine_09 (other enemies destroyed), 5 explosions 9 frames apart after a
  16-frame wait, 3 door explosions, then `level_boss_defeated` (**BOSS_DEFEATED_FLAG only at about H+95**) and
  immediately `set_delay_remove_enemy($30)`. Derived: level end about H+145. (Accumulator is $ff at that call =
  the DMC glitch sound, docs/Bugs.md:36-67; harmless.)
* Minimum: 32 hits, first possible ~102 frames after the auto-scroll ends.

### B7. Stage 6 Energy Zone (CURRENT_LEVEL 5) - level_6_enemy_screen_xx, bank2.asm:2768-2840
Fire beams use the full low nibble as attribute: bits0-1 = length index (`fire_beam_length_tbl` 5,9,13,15 segments of
8 px, bank0.asm:7242), bits2-3 = delay index P (`fire_beam_anim_delay_tbl` $00,$20,$40,$60, bank0.asm:7200).
The source comments next to the data show only 3 attribute bits and are wrong for these; decoded values below.

| scr | XX | Y | enemy | len segs | P | note |
|---|---|---|---|---|---|---|
| 0 | $40,$60 | $80,$60 | soldiers | | | |
| 0 | $c0 | $a0 | **pill box M** | | | bank2.asm:2771 |
| 0 | $e0 | $60 | sniper | | | |
| 1 | $80,$e0,$f0 | $60,$60,$c0 | turret man x3 | | | HP 10 |
| 2 | $a0 | $c0 / $90 | turret man / sniper | | | |
| 3 | $40 | $a0 | **pill box L** | | | attr $c, bank2.asm:2787 |
| 3 | $48 | $20 | DOWN beam | 13 | $20 | |
| 3 | $c8 | $20 | DOWN beam | 9 | $20 | |
| 3 | $e0,$f0 | $90,$c0 | turret man x2 | | | |
| 4 | $28 | $20 | DOWN beam | 15 | $20 | |
| 4 | $b8 | $50 | LEFT beam | 5 | $40 | |
| 4 | $b8 | $80 | LEFT beam | 5 | $20 | |
| 4 | $b8 | $b0 | LEFT beam | 13 | $00 | |
| 5 | $58 | $60 | LEFT beam | 5 | $60 | |
| 5 | $58 | $90 | LEFT beam | 9 | $40 | |
| 5 | $a8 | $20 | DOWN beam | 13 | $20 | |
| 5 | $a0 | $a0 | **pill box B (barrier)** | | | attr $d, bank2.asm:2803 |
| 5 | $c8 | $30 | sniper | | | |
| 5 | $f8 | $c0 | LEFT beam | 13 | $00 | |
| 6 | $58 | $30 | LEFT beam | 9 | $40 | |
| 6 | $58 | $60 | LEFT beam | 5 | $20 | |
| 6 | $a8 | $60 | RIGHT beam | 13 | $60 | |
| 7 | $40 | $60 | turret man | | | |
| 7 | $48 | $90 | RIGHT beam | 9 | $40 | |
| 7 | $68 | $20 | DOWN beam | 9 | $20 | |
| 7 | $a8 | $c0 | RIGHT beam | 5 | $00 | |
| 7 | $e8 | $20 | DOWN beam | 15 | $20 | |
| 8 | $60 | $90,$c0 | turret man x2 | | | |
| 8 | $68 | $60 and $c0 | RIGHT beam x2 | 13 | $40 | |
| 8 | $e8 | $60 | RIGHT beam | 5 | $20 | |
| 8 | $f0 | $90 | turret man | | | |
| 9 | $68 | $20 | DOWN beam | 15 | $00 | |
| $0b | $b1 | $a0 | **giant boss soldier (Gordea)** | | | |

(All beams get +8 added to Y at init, bank0.asm:7186-7187.)

Fire beam timing (bank0.asm:7168-7451) - this is the pause question:
* Burst shape, all three kinds: one 8-px segment per 2 frames while growing (draw, then 1 frame delay), hold $10
  (16) frames at full length, shrink one segment per 2 frames, then off. Lethal only between ignition and full
  retraction (collision enabled bank0.asm:7221, disabled 7279); hitbox follows the current length. Beams are
  invulnerable (HP $f0) and never ignite once their X < $30. Each segment draw can be refused when the graphics
  buffer is full (bank0.asm:7429-7430) which stretches the burst.
* **DOWN beam (type $10): own timer + player proximity, NOT FRAME_COUNTER.** After creation it waits P frames, then
  ignites the first frame the closest player is within $20 (32) px in X (bank0.asm:7204-7212). After a burst it waits
  P frames again and needs proximity again.
* **LEFT beam (type $11): pure FRAME_COUNTER.** Ignites whenever (FRAME_COUNTER & $7f) == P while idle
  (bank0.asm:7294-7301). Period 128 frames, phase fixed to the global frame counter. Because FRAME_COUNTER keeps
  counting during pause while enemy logic is frozen (A1), **pausing shifts every left beam's phase relative to the
  player's progress by exactly the number of paused frames** - that is the TAS pause.
* **RIGHT beam (type $12): own timer + RANDOM_NUM.** First ignition P frames after creation (P = 0 means 256); after
  each burst the next delay is RANDOM_NUM & $3f (0 = 256) (bank0.asm:7344-7352, 7276-7278). Pausing changes
  RANDOM_NUM too (idle-loop mixing), so right beams can also be re-rolled by a pause, but not steered directly.

Giant boss soldier (Gordea, type $13, `boss_giant_soldier_routine_ptr_tbl` bank0.asm:7485):
* Created on screen $0b at offset $b0, i.e. 16 frames into the 96-frame boss auto-scroll (trigger offset $a0).
* **ENEMY_HP = $40 + 8 x PLAYER_WEAPON_STRENGTH, sampled once on its first frame** (bank0.asm:7507-7512):
  default 64, F 72, M 80, L 80, S 88.
* Props `$04,$9d,...` (bank7.asm:9322): bullets and player collide from creation - **vulnerable immediately, even
  while it scrolls in** from X $f0 to X $a0 (Y $9b). No invulnerable phases.
* Behaviour: waits $31 frames, then loops (bank0.asm:7536-7613): move = ENEMY_VAR_1 & 3 where ENEMY_VAR_1 was
  RANDOM_NUM at the end of the previous move: 0 = jump (Y vel -6.5, gravity $38/256; X vel from
  (RANDOM_NUM + FRAME_COUNTER) & 3 -> +0.5, 0, 0, -0.5), 1 = throw a disc after $20 frames (max 3 in a row; needs
  ENEMY_ATTACK_FLAG), 2/3 = walk at 1.09 px/f left or right (RANDOM_NUM & 1) until X < $20 or >= $c0.
  Touching him kills. Discs (type $14) cannot be shot (bit7).
* Kill chain: H+1 `boss_giant_soldier_routine_06` calls `level_boss_defeated` (flag = 1), 4 explosions, then the exit
  door opens in 10 steps of 10 frames, `set_delay_remove_enemy($01)` (bank0.asm:7790-7936). Derived: level end ~H+110.

### B8. Stage 7 Hangar (CURRENT_LEVEL 6) - level_7_enemy_screen_xx, bank2.asm:2872-2981
Claw attribute (low nibble): bits0-1 = length code (`claw_length_tbl` 4,3,8,3 segments of 8 px; code 3 = "seeking"),
bits2-3 = trigger index T (`claw_frame_trigger_tbl` $00,$20,$40,$60) (bank0.asm:8045-8067, 8113).

| scr | XX | Y | enemy | decoded |
|---|---|---|---|---|
| 0 | $47 / $67 / $87 | $a0 | claws | 3 segs, T $00 / $20 / $40 |
| 0 | $97 / $a7 / $b7 / $c7 | $40 | claws (top) | 4 segs, T $00 / $20 / $40 / $60 |
| 0 | $a7 / $c7 | $a0 | claws | 3 segs, T $60 / $00 |
| 1 | $00 | $a0 | **flying capsule F** | attr 2, bank2.asm:2885 |
| 1 | $80 | - | stationary mining cart | |
| 1 | $97 / $a7 | $40 | claws | 8 segs, T $00 / $20 |
| 1 | $f7 | $a0 | claw | 4 segs, T $60 |
| 2 | $07 | $a0 | claw | 4 segs, T $40 |
| 2 | $18 | $60 | turret man | |
| 2 | $64 / $84 | $b0 | rising spiked wall | trigger $30 px, step $0c / $08 |
| 2 | $90 | $b0 | **flying capsule R** | attr 0, bank2.asm:2897 |
| 3 | $04,$44,$84 | $90 | TALL spiked wall x3 (attr 2 = full height) | HP 16 each |
| 4 | $04 / $84 | $70 | rising spiked wall | trigger $30, step $04 / $02 |
| 4 | $07,$87 | $a0 | claws | 3 segs, T $60 |
| 4 | $27 / $47 / $67 | $40 | claws | 4 segs, T $40 / $20 / $00 |
| 4 | $27 / $47 / $67 | $a0 | claws | 3 segs, T $40 / $20 / $00 |
| 4 | $70 | $40 | mining cart generator | |
| 4 | $a0 | - | stationary mining cart | |
| 5 | $20 | $60 | **pill box B (barrier)** | attr 5, bank2.asm:2919 |
| 5 | $c7 / $e7 | $40 | claws | 8 segs, T $40 / $00 |
| 6 | $30 | - | stationary mining cart | |
| 7 | $10 | $40 | mining cart generator | |
| 7 | $f0 | $60 | sniper | |
| 8 | $00 | $30 | **flying capsule M** | attr 1, bank2.asm:2934 |
| 8 | $58 | - | stationary mining cart | |
| 8 | $80 | $c0 | **flying capsule S** | attr 3, bank2.asm:2936 |
| 8 | $84,$c4 | $70 | spiked wall (attr 0 = upper half) | HP 16 |
| 8 | $87,$a7 | $a0 | SEEKING claws | re-arm $40 |
| 8 | $c7,$e7 | $a0 | SEEKING claws | re-arm $20 |
| 9 | $04 | $70 | spiked wall (attr 0) | HP 16 |
| 9 | $07 | $a0 | SEEKING claw | re-arm $00 |
| 9 | $a4 / $c4 / $e4 | $90 | rising spiked walls | trigger $30 / $50 / $70 px, start delay 0 / $0f / $1e, step $02 |
| $0a | $d7 / $e7 / $f7 | $80 | claws | 8 segs, T $20 / $60 / $20 |
| $0b | $07 / $17 / $27 | $80 | claws | 8 segs, T $60 / $20 / $60 |
| $0b | $44 | $d0 | rising spiked wall | trigger $40, step $02 |
| $0b,$0c | $f0 / $20,$a8,$fe | | turret men | HP 10 |
| $0d | $69 / $a9 | $d0 | mortar launchers (attr 1 / 0) | HP 8, optional |
| $0d | $d9 | $80 | **armored door = boss target** | HP $20 (32) |
| $0d | $e1 | $a0 | boss soldier generator | not hittable |

Claws (type $10, bank0.asm:8038-8186): invulnerable, bullets pass through, lethal to touch at the moving tip.
* **Normal claws descend when (FRAME_COUNTER & $7f) == T** (bank0.asm:8075-8078) and X >= $2c: 128-frame period
  locked to the global frame counter (pause shifts it, same as the stage 6 left beams). One segment per 3 frames
  down, 8 frames at the bottom, one per 3 frames up; idle for the rest of the 128 frames. Each step is a tile draw
  (retry when the graphics buffer is full).
* Seeking claws (length code 3): after a re-arm delay (initial $20; then the value in the table) they drop when the
  closest player is within $10 px in X **and FRAME_COUNTER < $c0** (bank0.asm:8095-8103). They never fire while
  FRAME_COUNTER is $c0-$ff (64 of every 256 frames).

Spiked walls:
* Rising spiked wall (type $11, bank0.asm:8226-8341): HP $10 (16). Dormant (bullets pass) until the closest player is
  within the trigger distance; then hittable at once, waits the start delay and rises in 7 draws with the step delay
  between them (so 7 x (step+1) frames). Its lethal box (about X +-14 px) exists from the trigger and grows upward
  with each draw (`rising_spiked_wall_data_tbl` bank0.asm:8333-8340); the tiles become SOLID from the 4th draw
  (bank0.asm:8309-8314). Destroying it (16 hits) removes it in 3 frames and clears the solid tiles
  (bank0.asm:8343-8393).
* Tall / fixed spiked wall (type $12, bank0.asm:8410-8433): HP $10 (16), hittable from creation, lethal. attr 2 =
  floor-to-ceiling wall (screen 3: three in a row = 48 mandatory hits), attr 0 = wall on the upper half only.

Mining carts (bank0.asm:8436-8568):
* Stationary cart (type $15): HP 3, can be stood on (state $6e). When a player lands on it it starts rolling RIGHT at
  0.75 px/f (X velocity fract $c0, bank0.asm:8556-8557) and reverses on walls. A rider receives the cart's movement
  as PLAYER_FAST_X_VEL_BOOST = 0 or 1 px each frame, average 0.75 (bank7.asm:6804-6818): **riding and walking right
  gives ~1.75 px/f and FRAME_SCROLL becomes 2 on the boosted frames** (docs/Bugs.md:227-257). Touching a cart from
  the side kills (bank7.asm:6721-6738).
* Cart generator (type $13): spawns a moving cart (type $14, HP 3) at X $f8 moving LEFT at 0.5 px/f that explodes on
  hitting background; a new one $80 frames after the previous one is gone.

Stage 7 boss (LEVEL_STOP_SCROLL = $0d, bank2.asm:1497; auto-scroll trigger at offset $a0):
* Armored door (type $16, `boss_door_routine_ptr_tbl` bank0.asm:8579): props `$0c,$93,$20` -> **HP 32, hittable from
  the frame it is created** (offset $d8 = 56 frames into the auto-scroll, at screen X $f0 sliding to $c8, Y $80).
  Only the door must die. When its HP < 5 it also stops the soldier waves (bank0.asm:8597-8601).
* Mortar launchers (type $17): HP 8, open only after the auto-scroll completes; optional.
* Soldier generator (type $18, bank0.asm:8785-8930): first wave $a0 frames in; wave size table[RANDOM_NUM & 3] =
  3,4,2,4; side follows the player (from the left if player X >= $a0), random after 20 waves or once a launcher is
  dead; door re-open delay table[(RANDOM_NUM >> 3) & 3] = $f0,$80,$a0,$c0. Stops after 30 waves or both launchers dead.
* Kill chain: H+1 `boss_door_routine_02` (tile draw, retried if buffer full) -> `boss_defeated_routine` (flag = 1) ->
  41-frame explosion -> 2 tile draws -> `set_delay_remove_enemy($80)` (bank0.asm:8650-8651). Derived: ~H+176.

### B9. Stage 8 Alien's Lair (CURRENT_LEVEL 7) - level_8_enemy_screen_xx, bank2.asm:3000-3069

| scr | XX | Y | enemy | note |
|---|---|---|---|---|
| 0 | $40 | $30 / $c0 | **flying capsules M / B (barrier)** | attr 1 / 5, bank2.asm:3001 |
| 0 | $f0 | $a0 | alien fetus (bundle) | HP 2 |
| 1 | $60,$a0,$a8 | $50,$60,$60 | alien fetus x3 | |
| 1 | $b0 | $60 | **alien guardian (mid-boss)** | |
| 2 | $be,$de | $40 | alien mouth (wadder) x2 | |
| 3 | $1e,$3e,$de,$fe | $60 | wadder x4 | |
| 3 | $e0 | $c0 | **flying capsule S** | attr 3, bank2.asm:3021 |
| 4 | $de,$fe | $e0 | wadder x2 | |
| 5 | $1e / $de,$fe | $e0 / $80 | wadder x3 | |
| 6 | $7e,$9e / $fe | $e0 / $80 | wadder x3 | |
| 7 | $1e / $be,$de | $80 / $e0 | wadder x3 | |
| 8 | $3e,$5e | $60 | wadder x2 | |
| 8 | $a0,$c0,$f0 | $c0 | alien spider (bugger) x3 | |
| 9 | $30,$b8 / $70 | $c0 / $20 | bugger x3 | |
| 9 | $3e | $e0 | wadder | |
| 9 | $c0,$e0 / $c2,$e2 | $40 / $c0 | spider spawn (eggron) x4: 2 ceiling, 2 floor | optional |
| 9 | $d1 | $70 | **heart (Gomeramos King) = final target** | |

Alien guardian (type $10, `alien_guardian_routine_ptr_tbl` bank0.asm:8969):
* Created on screen 1 at offset $b0; its first routine sets **AUTO_SCROLL_TIMER_01 = $40** (64 frames of forced
  scroll, bank0.asm:9009-9010) which carries it from X $f0 to X $b0 (Y $60).
* **ENEMY_HP = min($a0, $37 + 16 x PLAYER_WEAPON_STRENGTH + 16 x GAME_COMPLETION_COUNT), sampled once on its first
  frame** (`set_guardian_and_heart_enemy_hp` bank0.asm:9017-9034): default 55, F 71, M 87, L 87, S 103.
* Props `$04,$78,...` (bank7.asm:9337): bullets and players collide from creation. **The mouth animation is
  cosmetic - there is no closed/invulnerable state** (routine_01/02 never touch ENEMY_HP or the collision bits,
  bank0.asm:9037-9221). Bullet box (code 8, `collision_box_codes_04` bank7.asm:7336): X-28..X+28, Y-18..Y+18 around
  the enemy position.
* Mouth toggles every $20 frames; every 3rd opening it spits 2 fetuses (3 if weapon strength = 3)
  (bank0.asm:9198-9221); needs ENEMY_ATTACK_FLAG.
* Death (not a level boss, no flag): H+1 routine_03, 12 x 5 frames of explosions, then about 9 frames of tile
  draws; the WALL in front of it and its bg collision are removed in routines 09/0a (bank0.asm:9345-9400).
  Derived: the way forward opens about H+70 (more if draws are refused).
* Barrier note (inference from bank7.asm:6869-6878): it has player collision and a real HP value, so a player with
  INVINCIBILITY_TIMER != 0 who overlaps its player box (X-29..X+29, Y-30..Y+29) would zero its HP instantly. The B
  capsule of screen 0 is 1024 frames long. Whether the box can be reached over the wall is level geometry - untested.

Fetus / bundle (type $11): HP 2 + completion count (bank0.asm:9466-9469). Wadder / alien mouth (type $12): HP =
weapon strength + 4 (4/5/6/6/7) (bank0.asm:9635-9642); first blob $0a frames after creation, then every
$c0 + (RANDOM_NUM & $1f) frames; stops when X < $20. White blob (type $13): HP 1. Bugger / spider (type $14): HP =
weapon strength + 2 (2/3/4/4/5) (bank0.asm:10019-10024), runs left at 2.5 px/f, jump decided by
((RANDOM_NUM >> 1) + FRAME_COUNTER) & 2. All optional.

Final boss (LEVEL_STOP_SCROLL = 9, bank2.asm:1513; auto-scroll 96 f from screen 9 offset $a0):
* Heart (type $16, `boss_heart_routine_ptr_tbl` bank0.asm:10330): created at offset $d0 (48 frames into the
  auto-scroll) at X $f0, ends at X $c0, Y $70. **HP by the same formula as the guardian, sampled on its first frame:
  55 / 71 / 87 / 87 / 103.** Props `$04,$a7,...` (bank7.asm:9343): **always vulnerable from creation**, no cycle; the
  beat only speeds up as HP drops (delay = HP/2, bank0.asm:10356-10364).
* Spider spawns / eggrons (type $15): HP = $18 + 2 x weapon strength (24/26/28/28/30) (bank0.asm:10212-10220). They
  first open after $a0 + ((RANDOM_NUM + FRAME_COUNTER) & $3f) frames and then emit spiders. **They do NOT have to be
  destroyed** - only the heart's death calls `level_boss_defeated`.
* Kill chain (bank0.asm:10482-10486, 9425-9434, 10401-10444): H+1 `boss_heart_routine_03`: init_APU_channels,
  sound_57, **BOSS_DEFEATED_FLAG = 1**, first explosion -> 12 x 5 frames of explosions -> 2 frames drawing the dead
  heart -> `alien_guardian_routine_0b` puts every remaining fetus/mouth/blob/spider/spawn into its death routine and
  calls `set_delay_remove_enemy($a0)` (160 frames). Derived: level_routine_08 proceeds about H+226. What the player
  sees: boss music cut, explosions spreading from the heart for ~1 s, heart tiles replaced by the wreck, all other
  aliens popping, a ~2.7 s pause, then the end-of-level tune and the level-end sequence (covered elsewhere).

## C. HP summary and hits needed

### C1. The rule
Every player bullet does exactly 1 damage and an enemy can take at most 1 hit per frame (A3). So
**hits needed = HP, and the minimum kill time in frames = HP**, for every weapon. Weapons differ only in how many
bullets they can keep arriving on consecutive frames (player-code agent) and in how they inflate some HP values.

### C2. Bosses and mandatory targets

| stage | target | HP default | F (str 1) | M (2) | L (2) | S (3) | where set | vulnerable | D after kill |
|---|---|---|---|---|---|---|---|---|---|
| 1 | plated door | 32 | 32 | 32 | 32 | 32 | bank7.asm:9269 | from creation (16 f into auto-scroll) | $30 |
| 2 | 4 wall platings | 10 each | = | = | = | = | bank7.asm:9507 | T >= 133 after room load | - |
| 2 | boss eye | 16 | = | = | = | = | bank0.asm:2699 | 64 f after 4th plating gone | $60 |
| 3 | dragon mouth | 32 | = | = | = | = | bank0.asm:4513 | ~517 f after scroll end, then 112 f windows | $60 |
| 3 | (dragon hands, optional) | 16 each | = | = | = | = | bank0.asm:4802 | once arms exist | - |
| 4 | 3 wall platings | 10 each | = | = | = | = | bank7.asm:9507 | T >= 133 | - |
| 4 | 2 gemini helmets | 10 each | = | = | = | = | bank0.asm:5453 | 64 f after 3rd plating, 31 f window | $60 |
| 5 | tank x2 | 71 each | = | = | = | = | bank0.asm:6356 | only once stopped | - |
| 5 | UFO | 32 | = | = | = | = | bank7.asm:9312 | ~102 f after scroll end, ~303 f windows | $30 |
| 6 | giant soldier | **64** | **72** | **80** | **80** | **88** | bank0.asm:7507 | from creation | $01 |
| 7 | spiked walls (each) | 16 | = | = | = | = | bank7.asm:9327 | see B8 | - |
| 7 | armored door | 32 | = | = | = | = | bank7.asm:9332 | from creation (56 f into auto-scroll) | $80 |
| 8 | alien guardian | **55** | **71** | **87** | **87** | **103** | bank0.asm:9017 | from creation | (wall opens ~70 f) |
| 8 | heart | **55** | **71** | **87** | **87** | **103** | bank0.asm:9017 | from creation (48 f into auto-scroll) | $a0 |

Base cores: 8 (normal), 16 (big), 23 (plated) - B2. Weapon strength is the MAX over both players' weapons
(bank7.asm:4096-4105) and is recomputed every frame; scaled HP is latched on the enemy's first frame.
Stage totals of unavoidable hits (boss room only): S1 32; S2 56; S3 32; S4 50; S5 32 (+142 for the tanks);
S6 64-88; S7 32 (+ walls); S8 55-103 + 55-103.

### C2b. Barrier (B) touch-kill candidates (inference from bank7.asm:6858-6878 - UNTESTED, cheap to test)
With INVINCIBILITY_TIMER != 0, overlapping an enemy's player-collision box sets ENEMY_HP to 0 if 0 < HP < $f0 and
the enemy has state bit0 clear. That is a one-touch kill for: stage 1 door, stage 5 stopped tank and open UFO,
stage 6 giant soldier, stage 7 armored door, stage 8 guardian and heart, and the dragon hands. It is only 1 damage
for the stage 2 eye (ENEMY_HP is a dummy 1) and impossible for cores, wall platings, wall cannons, the gemini
helmets and the dragon mouth (state bit0 set = no player collision; props bank7.asm:9258-9304).
B sources on the route: stage 3 capsule (scr 2), stage 6 pill box (scr 5), stage 7 pill box (scr 5, $90 = ~1152 f),
stage 8 capsule (scr 0), base rooms too late. Timer: $80 x 8 = ~1024 frames.
* Stage 8 guardian: B is released ~370 px of scroll before the guardian appears, so time is ample; the open
  question is geometry - the guardian's player box for a jumping player is X $93..$cc, Y $49..$6e (enemy at X $b0,
  Y $60; `collision_box_codes_01` entry 8, bank7.asm:7279) and a solid wall stands in front of it from about X $72
  to $b1, Y >= $70 (bank0.asm:9274-9276).
* Stage 6 boss: pill box at world X ~1680, boss fight at ~3100-3230: ~1450 px at 1 px/f > 1024 f - looks too far.
* Stage 7 door: pill box at world X ~1550, door at ~3780: too far even with cart boosts.

### C3. Every other place weapon strength / completion count changes things
| what | effect | where |
|---|---|---|
| soldier generation timer | - 5 per strength point, - $28 per completion (max 3) | bank2.asm:1736-1770 |
| soldier burst size | strength bit1 (M, L, S) -> 2-bullet bursts more likely | bank0.asm:1488-1503 |
| rotating gun | faster rotation / shorter pause with strength (tables) | bank0.asm:819-821, 894-896 |
| red turret first shot | $28 frames, $08 after one completion | bank0.asm:1020-1024 |
| wall cannon closed time | $c0 (strength 0-1) or $60 (2-3) | bank7.asm:9456-9461 |
| stage 2 eye fire ring delay | $70,$50,$40,$28 | bank0.asm:2755-2765 |
| gemini bubble delay | table - 8 x strength | bank0.asm:5536-5550 |
| giant soldier HP | $40 + 8 x strength | bank0.asm:7507-7512 |
| guardian fetuses per volley | 3 instead of 2 when strength = 3 | bank0.asm:9207-9209 |
| fetus HP | 2 + completion | bank0.asm:9466-9469 |
| wadder HP | strength + 4 + 2 x completion | bank0.asm:9635-9642 |
| bugger HP | strength + 2 + completion | bank0.asm:10019-10024 |
| eggron HP | $18 + 2 x strength + 2 x completion | bank0.asm:10212-10220 |
| eggron spider interval | $0a - (weapon code) + 0..3 steps of $14 frames | bank0.asm:10266-10281 |
| guardian / heart HP | $37 + 16 x strength + 16 x completion, cap $a0 | bank0.asm:9017-9034 |

### C4. Enemy property table (enemy_prop_ptr_tbl, bank7.asm:9229-9343)
Columns: state byte (bit7 = bullets pass, bit0 = no player collision), score/collision byte (hi nibble = score
code: 1=100, 2=300, 3=500, 4=1000, 5=2000, 6=3000, 7=5000, 8=10000, 9=15000, $a=500000; lo nibble = collision box),
initial ENEMY_HP ($f0/$f1 = undamageable). "enabled later" = the routine clears bit7 itself.

| type | name | state | sc/col | HP | notes |
|---|---|---|---|---|---|
| 00 | weapon item | $82 | $22 | 1 | bullets pass; picked up by touch |
| 01 | enemy bullet | $80 | $00 | 1 | cannot be shot |
| 02 | pill box sensor | $0f | $32 | $f0 | HP 1 only while open (B1) |
| 03 | flying capsule | $0b | $32 | 1 | |
| 04 | rotating gun | $8f | $22 | 8 | enabled when it opens (X <= $f0 + 8 f) |
| 05 | soldier | $83 | $10 | 1 | enabled after its start delay ($01/$10/$20/$30 by attr bits4-5) |
| 06 | sniper | $83 | $30 | 1 | |
| 07 | red turret | $8f | $30 | 8 | enabled when fully risen |
| 08 | wall cannon | $0f | $52 | $f1 | real HP 8, only while open |
| 0a | wall plating | $0f | $42 | $f0 | HP 10 after opening |
| 0b | mortar shot | $8a | $05 | 1 | cannot be shot |
| 0c | scuba diver | $83 | $42 | 1 | only while surfaced |
| 0e | turret man | $0e | $33 | 10 | |
| 0f | turret man bullet | $80 | $01 | 1 | cannot be shot |
| L1 10 | bomb turret | $0f | $42 | 16 | |
| L1 11 | plated door | $0c | $82 | 32 | boss |
| L1 12 | exploding bridge | $89 | $00 | 1 | not hittable |
| L2/4 10 | boss eye | $8d | $02 | 1 | real HP 16 in VAR_1 |
| L2/4 11 | roller | $2f | $22 | 5 | |
| L2/4 12 | grenade | $81 | $03 | 1 | not hittable |
| L2/4 13 | wall turret | $9f | $35 | 4 | when open |
| L2/4 14 | core | $9f | $05 | 1 | HP set by routine: 8 / 16 / 5+5+5+8 |
| L2/4 15,16,18 | indoor / jumping / group soldier | $13 | $16 | 1 | |
| L2/4 17 | grenade launcher | $13 | $36 | 1 | |
| L2/4 19,1a,20 | generators | $89/$81 | $00 | $f1 | not hittable |
| L2/4 1b | eye fire ring | $8f | $13 | 2 | hittable once Y >= $48 |
| L2/4 1c | gemini helmet | $8f | $02 | 1 | real HP 10 in VAR_4 |
| L2/4 1d | spinning bubbles | $0a | $15 | 1 | |
| L2/4 1e,1f | blue / red soldier | $03 | $30 | 1 | |
| L3 10 | floating rock | $c0 | $04 | $f0 | platform |
| L3 11 | moving flame | $80 | $02 | $f0 | |
| L3 12 | rock cave | $81 | $00 | $f0 | |
| L3 13 | falling rock | $8f | $31 | 5 | enabled when it starts falling |
| L3 14 | dragon mouth | $8d | $83 | $f1 | real HP 32, only while open; no player collision |
| L3 15 | dragon arm orb | $0e | $52 | $f1 | hand: HP 16, state $0c |
| L5 10 | ice grenade generator | $81 | $00 | $f0 | |
| L5 11 | ice grenade | $81 | $02 | $f1 | |
| L5 12 | tank | $85 | $79 | $f0 | HP 71 once stopped |
| L5 13 | pipe joint | $81 | $00 | $f0 | |
| L5 14 | boss UFO | $8d | $93 | 32 | bit7/bit0 toggled by the cycle |
| L5 15 | mini UFO | $02 | $20 | 1 | |
| L5 16 | drop bomb | $0a | $12 | 1 | |
| L6 10-12 | fire beams | $81 | $0f | $f0 | |
| L6 13 | giant soldier | $04 | $9d | 1 | HP set by routine: 64-88 |
| L6 14 | spiked disc | $80 | $05 | 1 | cannot be shot |
| L7 10 | claw | $80 | $0a | $f0 | |
| L7 11 | rising spiked wall | $8d | $0f | 16 | enabled on trigger |
| L7 12 | spiked wall | $0c | $0f | 16 | |
| L7 13 | cart generator | $81 | $00 | $f0 | |
| L7 14,15 | mining carts | $6e | $0c | 3 | landable |
| L7 16 | armored door | $0c | $93 | 32 | boss |
| L7 17 | mortar launcher | $8f | $72 | 8 | when open |
| L7 18 | soldier generator | $89 | $00 | 1 | not hittable |
| L8 10 | alien guardian | $04 | $78 | 1 | HP set by routine: 55-103 |
| L8 11 | fetus | $06 | $22 | 1 | HP 2 |
| L8 12 | wadder | $06 | $42 | 1 | HP 4-7 |
| L8 13 | white blob | $02 | $22 | 1 | |
| L8 14 | bugger | $06 | $33 | 1 | HP 2-5 |
| L8 15 | eggron | $06 | $62 | $10 | HP 24-30 |
| L8 16 | heart | $04 | $a7 | 1 | HP set by routine: 55-103; 500,000 points |

## D. Every weapon pickup in the game
Decode: attr & 7 -> 0 R, 1 M, 2 F, 3 S, 4 L, 5 B, 6 falcon (bank7.asm:6895-6921).
Pill box: sits at world X = scr*256 + XX + 240, at table Y; hittable 49 f after it scrolls in, 80 on / 80 off (B1).
Flying capsule (horizontal stages): created when the scroll reaches scr*256 + XX; it enters at the LEFT edge
(screen X $10) at Y = table Y + $20 and flies right at 1.5 px/f in world terms (so +0.5 px/f relative to a
scrolling screen) with a vertical sine (bank0.asm:680-734). HP 1.
Dropped item: Y vel -3.0, X vel +0.5 px/f (vertical stage: +0.25, or -0.25 when X >= $80), gravity +$10/256 per
frame, bounces off the screen edges ($18 / $e8), lands on the first floor below (bank0.asm:166-258).

| stage | scr | XX | Y (or X for stage 3) | carrier | weapon | line |
|---|---|---|---|---|---|---|
| 1 | 0 | $60 | $a0 | pill box | **M** | bank2.asm:2279 |
| 1 | 0 | $f0 | $40 | capsule | **R** | bank2.asm:2281 |
| 1 | 4 | $60 | $40 | capsule | **S** | bank2.asm:2300 |
| 1 | 5 | $40 | $a0 | pill box | **F** | bank2.asm:2305 |
| 1 | 8 | $00 | $c0 | pill box | **S** | bank2.asm:2319 |
| 1 | 9 | $10 | $40 | capsule | **R** | bank2.asm:2324 |
| 1 | 9 | $10 | $b0 | capsule | **L** | bank2.asm:2324 |
| 2 | rooms 1,2,4,5 | - | - | red jumping soldier | R, M, M, F (late, see B2) | bank0.asm:2547-2580 |
| 3 | 0 | $40 | X $90 | pill box | **F** | bank2.asm:2442 |
| 3 | 0 | $c0 | X $90 | pill box | **L** | bank2.asm:2449 |
| 3 | 2 | $d0 | X $30 (+$20) | capsule | **B** | bank2.asm:2462 |
| 3 | 2 | $d0 | X $a0 (+$20) | capsule | **R** | bank2.asm:2462 |
| 3 | 4 | $60 | X $b0 | pill box | **S** | bank2.asm:2477 |
| 3 | 5 | $20 | X $10 | pill box | **M** | bank2.asm:2486 |
| 4 | rooms 2-8 | - | - | red jumping soldier | F, L, B, R, S, F, M (late, see B2) | bank0.asm:2606-2659 |
| 5 | 1 | $80 | $a0 | pill box | **M** | bank2.asm:2646 |
| 5 | 3 | $60 | $30 | capsule | **R** | bank2.asm:2656 |
| 5 | 5 | $60 | $80 | pill box | **F** | bank2.asm:2668 |
| 5 | 6 | $40 | $30 | capsule | **R** | bank2.asm:2672 |
| 5 | 6 | $40 | $70 | capsule | **Falcon** | bank2.asm:2672 |
| 5 | 6 | $40 | $b0 | capsule | **S** | bank2.asm:2672 |
| 5 | $10 | $60 | $a0 | pill box | **L** | bank2.asm:2727 |
| 6 | 0 | $c0 | $a0 | pill box | **M** | bank2.asm:2771 |
| 6 | 3 | $40 | $a0 | pill box | **L** | bank2.asm:2787 |
| 6 | 5 | $a0 | $a0 | pill box | **B** | bank2.asm:2803 |
| 7 | 1 | $00 | $a0 | capsule | **F** | bank2.asm:2885 |
| 7 | 2 | $90 | $b0 | capsule | **R** | bank2.asm:2897 |
| 7 | 5 | $20 | $60 | pill box | **B** | bank2.asm:2919 |
| 7 | 8 | $00 | $30 | capsule | **M** | bank2.asm:2934 |
| 7 | 8 | $80 | $c0 | capsule | **S** | bank2.asm:2936 |
| 8 | 0 | $40 | $30 | capsule | **M** | bank2.asm:3001 |
| 8 | 0 | $40 | $c0 | capsule | **B** | bank2.asm:3001 |
| 8 | 3 | $e0 | $c0 | capsule | **S** | bank2.asm:3021 |

Pickup rules (bank7.asm:6884-6945): R sets the rapid flag (bit4) on the current weapon; taking a DIFFERENT letter
weapon clears the rapid flag, taking the SAME letter keeps it. B = INVINCIBILITY_TIMER $80 ($90 in stage 7),
decremented when FRAME_COUNTER & 7 = 0 (about 1024 / 1152 frames). Falcon = `destroy_all_enemies` + 32-frame flash.
Route consequence of C2: holding S when the stage 6 boss, the stage 8 guardian and the heart are created costs
+24, +48 and +48 hits versus the default gun (+16/+32/+32 for M or L, +8/+16/+16 for F).

## E. Randomness

### E1. RANDOM_NUM ($34)
* Updated ONLY in the idle loop: `forever_loop` does `RANDOM_NUM += FRAME_COUNTER` (adc, carry carried over) over
  and over until the next NMI (bank7.asm:284-288). Its value at the start of a frame therefore depends on how many
  loop iterations fit after the previous frame's logic, i.e. on CPU load, and on FRAME_COUNTER.
* Cleared (with FRAME_COUNTER) only when a demo level starts (bank7.asm:1123-1125).
* Written by game code in one place: the gemini attack roll stores RANDOM_NUM + FRAME_COUNTER back (bank0.asm:5541-5543).
* Deterministic under emulation for identical input; any change that alters CPU time in a frame (one more bullet, an
  enemy more or less, a pause) changes it from then on.

| use | decision | where |
|---|---|---|
| soldier generation | which player's Y to search from: (FRAME_COUNTER + RANDOM_NUM) & 1 | bank2.asm:1805-1808 |
| soldier generation | spawn side: `gen_soldier_initial_x_pos`[(FRAME_COUNTER + RANDOM_NUM) & $0f] (8 right $fa, 8 left $0a) | bank2.asm:1887-1891 |
| soldier generation | while scrolling: RANDOM_NUM & 3 = 0 -> a group of 3 soldiers instead of 1 | bank2.asm:2036-2040 |
| soldier generation | ledge behaviour bit: (RANDOM_NUM + FRAME_COUNTER) & 2 | bank2.asm:2060-2065 |
| soldier | jump strength: RANDOM_NUM & 3 | bank0.asm:1420-1426 |
| soldier | bullets per burst: table[(RANDOM_NUM & 3) + strength bit] | bank0.asm:1488-1498 |
| stage 1 bomb turret | bomb speed 1,3,5,7 by RANDOM_NUM & 3 | bank0.asm:2121-2124 |
| stage 3 dragon arm | pattern delay $40,$60,$30,$70 by (RANDOM_NUM + FRAME_COUNTER) & 3 | bank0.asm:5077-5081 |
| stage 4 gemini | bubble delay + reseed | bank0.asm:5541-5550 |
| stage 5 UFO | X position $40,$60,$80,$80 by RANDOM_NUM & 3 at each (re)appearance | bank0.asm:6680-6684 |
| stage 6 right beam | re-ignite delay RANDOM_NUM & $3f | bank0.asm:7349-7351 |
| stage 6 boss | first move (RANDOM_NUM latched at creation), every next move, jump X velocity, walk direction | bank0.asm:7513, 7550-7558, 7588-7595, 7606-7611 |
| stage 7 boss soldiers | wave size, side, door delay | bank0.asm:8840-8843, 8879-8881, 8913-8919 |
| stage 8 fetus | re-aim timer, speed | bank0.asm:9476-9484, 9491-9494 |
| stage 8 wadder | blob interval $c0 + (RANDOM_NUM & $1f) | bank0.asm:9666-9669 |
| stage 8 white blob | activation delay $50 + (RANDOM_NUM & $1f); freeze 2 or $22 frames | bank0.asm:9709-9712, 9804-9808 |
| stage 8 bugger | will-jump flag | bank0.asm:10011-10015 |
| stage 8 eggron | first-open delay, spider interval jitter | bank0.asm:10221-10225, 10275-10279 |
| 2-player only | target player picks | bank0.asm:7620, 9718, 10004 |

### E2. Decisions keyed on FRAME_COUNTER ($1a)
FRAME_COUNTER is incremented once per executed game frame in `exe_game_routine` (bank7.asm:690), including paused
frames, so everything below can be phase-shifted against game progress by pausing.

| what | rule | where |
|---|---|---|
| **stage 6 LEFT fire beams** | ignite when (FC & $7f) = $00/$20/$40/$60 | bank0.asm:7297-7301 |
| **stage 7 claws** | descend when (FC & $7f) = $00/$20/$40/$60; seeking claws disabled while FC >= $c0 | bank0.asm:8075-8078, 8098-8100 |
| stage 5 tank | TANK_AUTO_SCROLL = FC & 1 (scroll on odd frames); stop timer counts on even frames | bank0.asm:6292-6294, 6401-6405, 6520-6522, 6566-6568 |
| soldier generation | timer -2 per frame, but only -1 on odd frames while scrolling | bank2.asm:1782-1800 |
| soldier generation | Y search mode: FC & 3 = 0 top-down, 1 bottom-up, 2/3 from the player's Y upward | bank2.asm:1821-1827 |
| soldier generation | screen flag $80: spawn only if FC is even; flag $40: only if FC & 3 = 0 | bank2.asm:2005-2019 |
| soldier generation | shooter/non-shooter variant: attr table column FC & 3 | bank2.asm:2053-2059 |
| soldier (running right, while scrolling) | start delay counts only on odd frames | bank0.asm:1282-1290 |
| base soldier generator / roller generator | timers count on odd frames | bank0.asm:2422-2424, 3919-3921 |
| stage 4 red/blue generator | timer counts on even frames | bank0.asm:6098-6100 |
| stage 4 gemini phantoms | drawn/hittable at X0 + off on even frames, X0 - off on odd | bank0.asm:5605-5617 |
| stage 4 bubbles | speed/spin class = FC & 3 at creation | bank0.asm:5703-5706 |
| stage 3 dragon arm | pre-extension delay counts on odd frames | bank0.asm:4861-4864 |
| stage 3 boulder | wobble +-1 px every 4th frame by FC bit 2 | bank0.asm:4410-4423 |
| barrier | INVINCIBILITY_TIMER-- when FC & 7 = 0 | bank7.asm:4083-4088 |
| electric fence / palette cycle / sprites | cosmetic (FC & 3, FC & 7) | bank7.asm:2939-2944, 3604-3607 |

## F. Random soldier generation (exe_soldier_generation, bank2.asm:1697)
* Runs every frame after the enemy routines. SCREEN_GEN_SOLDIERS is zeroed whenever LEVEL_SCREEN_NUMBER changes
  (bank2.asm:1698-1703). There is NO cap on the count; reaching $1e (30) only unlocks left-side spawns in stage 1 and
  disables the edge check (bank2.asm:1897-1902, 2022-2029).
* State 0 (1 frame): timer = `level_soldier_generation_timer`[level] = $90, 0, $d8, 0, $d0, $c8, $c0, 0
  (bank2.asm:1779) minus $28 x completions (max 3) minus 5 x weapon strength. 0 = no generation at all (stages 2, 4, 8).
* State 1: timer -= 2 per frame (-1 on odd frames while FRAME_SCROLL != 0). Default gun, completion 0: an attempt
  every ~73 frames standing still / ~97 frames while scrolling in stage 1; stage 3 109/145; stage 5 105/140;
  stage 6 101/134; stage 7 97/129. With S subtract ~8-10 frames. On expiry the timer is reloaded and a spawn point is
  searched at the chosen screen edge every 16 px of Y for a floor tile (bank2.asm:1803-1938). Stage 1 with
  completion 0 always uses the RIGHT edge (X $fc) until 30 soldiers were generated on that screen.
* State 2 (next frame, bank2.asm:1948-2081) - the spawn is CANCELLED if any of:
  - Y < $40 (except stage 3) or Y >= $e0;
  - **ENEMY_ATTACK_FLAG = 0** (player dropping in, dead, or new-life invincible);
  - stage 5 screens >= $11: spawn point on the left half;
  - solid tile at / next to the spawn point;
  - **no free slot among slots 0-6**;
  - **LEVEL_SCREEN_NUMBER = 0** (first screen never spawns);
  - screen entry in `soldier_level_attributes_xx` is $ff;
  - entry bit7 set and FRAME_COUNTER odd; entry bit6 set and FRAME_COUNTER & 3 != 0;
  - (completion 0 and < 30 generated) **a player within $40 px of that edge: X < $40 for a left spawn, X >= $c0 for
    a right spawn** (`player_edge_check` bank2.asm:2144-2187).
  Otherwise one soldier (type 5) is created, or - when scrolling and RANDOM_NUM & 3 = 0 (not stage 3) - three at once
  (`create_default_soldiers`, not counted in SCREEN_GEN_SOLDIERS).
* Per-screen table (index = screen - 1), value = attr group | $80 (50 %) | $40 (25 %), $ff = none
  (bank2.asm:2212-2230; groups in `gen_soldier_initial_attr_tbl` bank2.asm:2236-2243: 0 never shoots, 1-3 = 1-3 of 4
  shoot, 4 always shoots, 5/6 include the $08 variant):
  - stage 1: scr 1-7 $80, scr 8-9 $40, scr 10 $80, scr 11-12 $ff.
  - stage 3: scr 1-3 $00, scr 4 $01, scr 5 $00, scr 6 $ff, scr 7 $01, scr 8-9 $ff.
  - stage 5: scr 1-8 = 01,02,03,04,03,03,03,02; scr 9 $ff; scr 10-12 = 04,02,03; scr 13 $ff; scr 14-17 = 02,03,04,02;
    scr 18-20 $ff.
  - stage 6: scr 1-3 = 00,05,02; scr 4-5 $ff; scr 6 $80; scr 7-8 = 05,03; scr 9 $82; scr 10-12 $ff.
  - stage 7: scr 1-9 = $80,05,06,$80,$80,05,07,$80,$80; scr 10 = 04; scr 11 $ff; scr 12-13 = 04; scr 14-15 $ff.
* How a runner suppresses spawns: (1) all of slots 0-6 occupied blocks a spawn, but that is not practical to
  arrange; (2) arrange FRAME_COUNTER parity
  on $80/$40 screens so state 2 lands on a blocked frame (the expiry frame is deterministic from scroll history, a
  1-frame pause flips the parity); (3) stand within $40 px of the spawn edge when not scroll-locked (boss rooms);
  (4) nothing spawns on screen 0, on $ff screens (all boss screens), or while ENEMY_ATTACK_FLAG = 0; (5) a weaker
  weapon lengthens the timer by 5 per strength point. Killed soldiers also cost: each explosion keeps its slot ~33 f.

## G. Level headers and boss arrival
Header bytes: bank2.asm:1389-1515 (docs/Level Headers.md). Screens = entries in the enemy screen pointer table.

| stage | type | screens (table entries) | LEVEL_STOP_SCROLL | LEVEL_ALT_GRAPHICS_POS | solid-bg check byte | header |
|---|---|---|---|---|---|---|
| 1 | outdoor horizontal | 13 ($00-$0c) | $0b | $0b | $00 | bank2.asm:1390 |
| 2 | indoor | 6 (5 rooms + boss) | $05 | $04 | $00 | bank2.asm:1406 |
| 3 | outdoor vertical | 10 | $07 | $07 | $00 | bank2.asm:1422 |
| 4 | indoor | 9 (8 rooms + boss) | $08 | $07 | $00 | bank2.asm:1438 |
| 5 | outdoor horizontal | 22 ($00-$15) | $13 | $13 | $01 (items collide with solids) | bank2.asm:1454 |
| 6 | outdoor horizontal | 13 | $0b | $0b | $81 (bullets stop on solid bg) | bank2.asm:1470 |
| 7 | outdoor horizontal | 15 | $0d | $0d | $81 | bank2.asm:1486 |
| 8 | outdoor horizontal | 11 | $09 | $09 | $00 | bank2.asm:1502 |

Boss auto-scroll (`set_boss_auto_scroll` bank7.asm:6552-6584): fires from the player-scroll code when
LEVEL_SCREEN_NUMBER = LEVEL_STOP_SCROLL and LEVEL_SCREEN_SCROLL_OFFSET >= $a0 (horizontal) / $c0 (vertical);
AUTO_SCROLL_TIMER_00 = $60 / $40 frames at 1 px/f; LEVEL_STOP_SCROLL := $ff; BOSS_AUTO_SCROLL_COMPLETE++ at the end
(bank7.asm:5606-5610). Total scroll needed to trigger: stage 1 2976 px, stage 5 5024, stage 6 2976, stage 7 3488,
stage 8 2464 (= STOP*256 + 160).
What a fast player can influence:
* Nothing shortens the 96 / 64 frame auto-scroll or the indoor transitions.
* Bosses that are hittable DURING the auto-scroll (so be in position and firing as they slide in): stage 1 door
  (from +16 f), stage 6 boss (+16 f), stage 7 door (+56 f), stage 8 heart (+48 f); stage 8 guardian from its creation.
* Bosses on a timer that starts when the scroll completes: stage 3 mouth (~517 f), stage 5 UFO (~102 f), stage 7
  mortar launchers. Room/boss-room timers that start on room load: cores (B2), platings (133 f).
* Timers gated by progress: stage 2 eye and stage 4 gemini start their 64-frame delay only when the last plating's
  wreck tile has been drawn - kill the platings as early as possible, all on nearly the same frame.
* Stage 5 tanks approach 3x faster while the player scrolls (B6).
* HP latched from weapon strength at creation: stage 6 boss, stage 8 guardian and heart (C2).

## H. Lag-relevant observations
* Per active enemy per frame: its routine + (if bit0 clear) a 2-player collision test + (if bit7 clear) a loop over
  all 16 player bullet slots (bank7.asm:6962-6996). Enemies that are "bullets pass through" skip the 16-slot loop.
* Explosions are full enemies: `create_two_explosion_89` / `create_enemy_for_explosion` allocate a slot as a fake
  pill box running two explosion cycles (~66+ frames) (bank7.asm:8322-8376); boss deaths spawn up to 14 of them.
* `find_next_enemy_slot` failing is silent: enemy bullets are not fired (bank7.asm:9939-9940), generated enemies and
  even-XX screen enemies are dropped (A4).
* Soldier generation's search frame can call `get_bg_collision` up to ~15 times (bank2.asm:1831-1882) - a CPU spike
  every ~73-145 frames on generation screens, which also perturbs RANDOM_NUM.
* Dragon boss: 10 arm orbs + mouth; each shoulder recomputes every orb position every frame
  (`dragon_arm_orb_set_positions`, bank0.asm:4971-4972) - the heaviest enemy code in the game.
* Background-tile enemies queue writes in CPU_GRAPHICS_BUFFER; when GRAPHICS_BUFFER_OFFSET >= $40 / $50 the write is
  refused and retried (A7). Heavy tile users: stage 5 tank (a wheel super-tile EVERY frame while moving,
  bank0.asm:6312-6343, plus scrolling columns), UFO thrusters, stage 6 beams (a tile group every 2 frames per active
  beam), stage 7 claws (every 3 frames each) and rising walls, stage 8 guardian mouth (3 super-tiles per toggle).
* Indoor rooms redraw 4 fence tiles ($40 bytes) every 4th frame until the room is cleared (bank7.asm:2936-2944).
* Player bullets are drawn on alternating frames (8 per frame, bank7.asm:3888-3905) - sprite flicker, not lag.

## I. Open points / things to verify in the emulator
All frame counts marked "derived" were obtained by stepping the routines by hand; verify with RAM watches
(per-slot arrays, index = slot 0-15, from ram.asm:1026-1078: ENEMY_SPRITES $030a, ENEMY_Y_POS $0324, ENEMY_X_POS
$033e, ENEMY_ROUTINE $04b8, ENEMY_TYPE $0528, ENEMY_ANIMATION_DELAY $0538, ENEMY_VAR_A $0548, ENEMY_ATTACK_DELAY
$0558, ENEMY_FRAME $0568, ENEMY_HP $0578, ENEMY_SCORE_COLLISION $0588, ENEMY_STATE_WIDTH $0598, ENEMY_ATTRIBUTES
$05a8, ENEMY_VAR_1..4 $05b8/$05c8/$05d8/$05e8; zero page: INDOOR_SCREEN_CLEARED $37, BOSS_DEFEATED_FLAG $3b,
LEVEL_SCREEN_NUMBER $64, LEVEL_SCREEN_SCROLL_OFFSET $65, TANK_AUTO_SCROLL $77, SOLDIER_GENERATION_ROUTINE $79,
SOLDIER_GENERATION_TIMER $7a, BOSS_AUTO_SCROLL_COMPLETE $84, BOSS_SCREEN_ENEMIES_DESTROYED $85, WALL_CORE_REMAINING
$86, WALL_PLATING_DESTROYED_COUNT $87, INDOOR_ENEMY_ATTACK_COUNT $88, ENEMY_ATTACK_FLAG $8e). In particular: the 517-frame dragon wait, core opening T values, the
~135-frame room transition, kill-to-level-end totals, and the barrier-touch kill on the stage 8 guardian.
