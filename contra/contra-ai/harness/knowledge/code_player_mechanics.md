# Contra (NES, US) — player mechanics and weapons, from the disassembly

Source: `dl\nes-contra-us\src` (read only, nothing built or run).
Citations are `label` + `file:line`. `b7` = `bank7.asm`, `b6` = `bank6.asm`, `b2` = `bank2.asm`, `b0` = `bank0.asm`, `b3` = `bank3.asm`.
"computed" = I calculated it offline from the constants in the code (small Python model of the routine, not the game).
"inference" = reasoned from the code, not literally stated in it. Everything else was read directly.
Scope: P1, 1-player. All positions are screen pixels; `SPRITE_X_POS/SPRITE_Y_POS` is the player's centre point.

## 0. Frame order (needed to read everything below)

`level_routine_04` b7:3184 -> `check_game_over_run_enemy_logic` b7:3195, each non-paused frame:

| # | Step | Where |
|---|------|-------|
| 1 | Player state routine: aim -> ledge check -> **fire check (bullet created)** -> X/Y movement, scroll request (`FRAME_SCROLL`) | `player_state_routine_01_logic` b7:4269 |
| 2 | Invincibility timers, recoil timer, clear cart boost, weapon strength | `handle_invincibility_and_weapon_strength` b7:4066 |
| 3 | **Player bullet routines** (move bullets, despawn) | `run_player_bullet_routines` b6:1251 via b7:3886 |
| 4 | Scroll applied to the background | `handle_scroll` b7:5588 |
| 5 | **Enemy routines; per enemy: player-vs-enemy collision, then bullet-vs-enemy collision** | `exe_all_enemy_routine` b7:7345 (calls at b7:7371, b7:7376) |

Consequences: a bullet created in step 1 is advanced to "live" in step 3 of the same frame and can hit in step 5 of the same frame (at its spawn point). A cart/rock boost found in step 5 is applied in step 1 of the next frame. The player is killed in step 5.

Input: `CONTROLLER_STATE_DIFF = (new XOR last) AND new` = newly pressed buttons only (`set_player_input` b7:995). In 1-player mode pad 1 and pad 2 are OR-ed before that (b7:980-987), so pad 2 cannot be used to fake a faster press rate.

## 1. Horizontal movement

| Fact | Value | Where |
|------|-------|-------|
| X velocity | integer only: `$01` (+1), `$ff` (-1) or 0 px/frame. Recomputed from the d-pad every frame. No acceleration, no sub-pixel X outdoors | `handle_player_state_calc_x_vel` b7:4359, `set_player_positive_x_velocity` b7:4643 |
| Ground / air / water / indoor / waterfall speed | all 1 px/frame | same routine for all |
| Fractional X | only `INDOOR_TRANSITION_X_FRACT_VEL/ACCUM`, used solely for the scripted walk between indoor rooms | b7:4429-4435, `set_player_advancing_vel` b7:4882 |
| Right beats left | Right is tested first; L+R = right | `handle_d_pad` b7:4560 |
| Firing does not slow you | `PLAYER_RECOIL_TIMER` (set to `$0f` per shot, b6:625) is only decremented (b7:4091) and read for sprites (b2:832, b2:909). It never touches velocity | |
| `PLAYER_FALL_X_FREEZE` ($b8) | not a timer: it is a Y value = start Y + `$14` (20). While falling off a ledge or dropping through, the d-pad is ignored until Y >= that value | `set_edge_fall_code` b7:4516, `set_x_velocity_for_edge_fall_code` b7:4681 |

What blocks X (`calc_player_x_vel` b7:4373):

| Blocker | Rule | Where |
|---------|------|-------|
| Solid background | tests the point 8 px ahead (`+$08` / `-$08`), from head (Y-11; prone: Y) down to the feet; only code `$80` (solid) blocks, also a floor cell with a solid cell directly under it | b7:4387, b7:4418, `check_player_solid_bg_collision` b7:5390, `floor_get_next_row_bg_collision` b7:6347 |
| Right screen edge | no move if X >= edge. Outdoor `$e6` (230), indoor boss screen `$e0` (224), indoor room `$d0` (208) | `level_right_edge_x_pos_tbl` b7:4444 |
| Left screen edge | no move if X < edge. Outdoor `$1a` (26), indoor boss `$20` (32), indoor room `$30` (48). So min X is edge-1 | `level_left_edge_x_pos_tbl` b7:4451 |
| Boss-screen cap | after the boss reveal scroll (`BOSS_AUTO_SCROLL_COMPLETE`=1), no move right if X >= per-level cap: L1 `$90`, L2-L4 `$ff`, L5 `$a0`, L6 `$d0`, L7 `$b0`, L8 `$b0` (L1 is blocked earlier by the solid door at about `$88`) | `@lvl_boss_max_x_scroll_tbl` b7:4413 |
| Water, Down held | in water, any Down (D, D+L, D+R) = no X movement | `set_player_x_vel_to_a` b7:4651 |
| Water entry | 16 frames with no X movement (computed from `PLAYER_WATER_TIMER`=`$10`, state bit 7 makes `calc_player_x_vel` exit) | b2:1107-1111, b7:4378 |
| Water exit | 13 frames with no X movement (`PLAYER_WATER_TIMER`=`$0c`) (computed) | b2:1202-1206, `player_walk_out_of_water` b2:1229 |
| Jump start | the frame A is pressed has X velocity 0 (see section 3) | b7:4494 |
| Drop-through start | 17 frames with no X movement (see section 3) | |
| Electrocution (indoor) | Up alone before the room is cleared: `ELECTROCUTED_TIMER`=`$30` (48 frames), no move, no fire | `d_pad_up_pressed` b7:4590 |

Cart / floating rock boost: while standing on a landable enemy (mine carts types `$14/$15`, floating rock `$10`), `PLAYER_FAST_X_VEL_BOOST` = that enemy's whole-pixel X movement this frame, added to the d-pad velocity next frame (`@land_on_enemy` b7:6804-6818, `calc_player_x_vel` b7:4376). The sum is what scrolls the screen, so right + cart = 1 + cart speed px/frame (the code comment at b7:4022 says `FRAME_SCROLL` becomes 2 on a moving cart). The boost is lost while ascending in a jump (`@check_player_jumping` b7:6741 skips the landing test while Y velocity < 1).

## 2. Scrolling

Horizontal levels (`set_frame_scroll_if_appropriate` b7:5164):

| Fact | Value | Where |
|------|-------|-------|
| Scroll condition | player state = 1 (normal), outdoor, no auto-scroll timer running, `LEVEL_STOP_SCROLL` not negative, moving right (positive X velocity), X >= `$80` (128) (1-player threshold) | b7:5165-5180, `horizontal_scroll_point_tbl` b7:5228 |
| Amount | `FRAME_SCROLL` = the player's X velocity (1, or 1 + cart boost). The player's own X velocity is then zeroed, so X stays at `$80` | b7:5202-5209 |
| Can the player outrun the scroll? | No. While scrolling is allowed the player never gets past X=`$80`; only when scrolling is blocked (boss screen, auto-scroll) does X move right | same |
| Scrolls while jumping? | Yes, same code path, same 1 px/frame | `handle_jump` -> `calc_player_x_vel` b7:4373 |
| Never scrolls left | the left branch never calls the scroll routine | `@player_negative_x_vel` b7:4417 |
| No scroll while dead / respawning | state must be 1 | b7:5169 |
| `LEVEL_STOP_SCROLL` | level header: screen number where scrolling ends. When `LEVEL_SCREEN_NUMBER` equals it and the in-screen offset >= `$a0` (160) [vertical: `$c0`], and the player is requesting scroll, it sets `AUTO_SCROLL_TIMER_00` = `$60` (96) [vertical: `$40` (64)] and `LEVEL_STOP_SCROLL`=`$ff` | `set_boss_auto_scroll` b7:6552, tables b7:6577-6584 |
| Boss reveal auto-scroll | 1 px/frame for exactly 96 frames (64 on the waterfall), cannot be sped up. Each frame the player is pushed 1 px left (waterfall: 1 px down), so holding right keeps screen X constant | b7:3879-3883, `handle_scroll` b7:5606-5615, `auto_scroll_player` b7:4278 |
| Other auto-scroll | `AUTO_SCROLL_TIMER_01` set at b0:9010 (level 8), `TANK_AUTO_SCROLL` added at b7:5620 (level 5 tanks) — enemy agent's area | |

**Max forward progress on a horizontal level is 1 px/frame** (2+ on a moving cart). It is less only when: the A-press frame of a jump (0 px), water entry (16 f) / exit (13 f) / Down held in water, Down+A drop (17 f), a solid wall 8 px ahead, electrocution, death, and X < `$80` (walking to the scroll point moves the player, not the level — same world speed, so no loss).

Waterfall, vertical (`set_vertical_level_frame_scroll` b7:5237, called from `handle_jump` b7:4751):

| Fact | Value |
|------|-------|
| Condition | player Y < `$50` (80) and Y velocity negative (rising in a jump). Falling or Y >= `$50` = no scroll |
| Amount | the whole-pixel rise of that frame becomes `FRAME_SCROLL` instead of moving the player (Y stays put). Rise per frame is 4,4,4,... down to 0 as the jump decays: at most 4 px/frame (computed: first jump frame velocity is `$fc13` = -3.93) |
| Per jump | a jump started above Y=`$50` scrolls 58 or 59 px over 29 frames (computed) |
| Loop | `handle_vertical_scroll` b7:5691 applies `FRAME_SCROLL` 1 px at a time, any amount |
| Kill line | Y >= `$e8` (232) while not hidden = death, all outdoor levels (b7:4238) |

## 3. Jump physics

Y position is 16-bit: `SPRITE_Y_POS` : `PLAYER_JUMP_COEFFICIENT` ($94). Velocity is 16-bit signed: `PLAYER_Y_FAST_VELOCITY` : `PLAYER_Y_FRACT_VELOCITY`. Each air frame: velocity += `$0023`, then position += velocity (`apply_gravity` b7:5139, `player_jumping_set_y_pos` b7:5114).

| Fact | Value | Where |
|------|-------|-------|
| Jump trigger | new A press (`CONTROLLER_STATE_DIFF` bit 7), on the ground, not in water. Holding A does not re-jump | b7:4486-4494 |
| Initial velocity, outdoor and indoor boss screen | `$fbf0` = -4.0625 px/frame (the comment "-5.94" is wrong) | `set_jump_status_and_y_velocity` b7:4533-4551 |
| Initial velocity, indoor room | `$fc90` = -3.4375 px/frame | b7:4550 |
| Gravity | `$23`/256 = 0.1367 px/frame^2, every air frame, no terminal velocity | `apply_gravity` b7:5139 |
| Variable height? | No. A is not read in the air; releasing A changes nothing | `handle_jump` b7:4708 |
| A-press frame | sets velocity only: no Y move **and X velocity is 0 that frame** (the routine returns before the d-pad is read). Every jump costs 1 px / 1 frame of forward progress | b7:4488-4494, b7:4533 |
| Flat-ground jump, outdoor | A on frame 0; airborne frames 1-58; lands on frame 59 (always, any sub-pixel); next A possible on frame 60. Peak 59 px if coefficient < `$57` at take-off, else 58 px. Rising for 29 frames (computed) | |
| Indoor room jump | lands on frame 48 or 49, peak 41-42 px (computed). Indoor boss screen: frame 60, peak 58-59 | |
| Air control | full: each air frame L/R sets the direction bits of `PLAYER_JUMP_STATUS` (`$20` right, `$40` left) and X = +-1 immediately. With no L/R held the last direction **persists** (you cannot stop in the air, only reverse). A fresh jump has no direction until L/R is seen | `@set_jump_status_from_input` b7:4759-4782 |
| Ceiling | rising: point (X, Y-10) solid -> velocity set to 0 | `@check_collision_above` b7:4733 |
| Landing test (outdoor) | only when falling. Fast velocity 0: no test. Fast 1-3: test only if `(Y + VERTICAL_SCROLL) & $0f < 8`. Fast >= 4: always. Test = collision code at (X, Y+16) non-zero (floor, water or solid) | b7:4709-4731, `get_player_bg_collision_code` b7:5077 |
| Landing snap | Y = `(Y & $f0) + 4` (with vertical scroll folded in). Standing Y is always 16k+4; collision cells are 16x16 px | `set_player_landing_y_offset` b7:4956 |
| Land early | yes: you land as soon as Y is within 4 px above standing height (then snap down), so a flat jump ends 4 px "early". Rising passes through floors from below (one-way platforms) | computed from the two rows above |
| Highest step | 48 px (3 cells). 64 px is out of reach (peak 58-59). Landing frames (computed): +16 px: frame 54; +32: 48-49; +48: 40. Lower platforms: -16: 63; -32: 66; -48: 69; -64: 72; -96: 77-78 | |
| Landing frame | X still moves on the landing frame | b7:4730 |
| Walk off a ledge | automatic when the cell under the centre point is empty (`check_player_ledge` b7:5038). `EDGE_FALL_CODE` = `$21` (facing right) / `$41` (left), fall starts at velocity 0. X keeps moving 1 px/frame in the facing direction, d-pad ignored until 20 px have fallen, then free. No forward loss | `walk_off_ledge` b7:4509 |
| Ledge fall landing | once Y >= start+20, lands on any non-empty cell at (X, Y+16) (no half-cell rule). Landing frame (computed): 16 px lower: 18; 32: 21; 48: 26; 64: 30-31; 96: 37-38 | b7:4681-4688 |
| Drop through (Down+A) | d-pad must be Down without L/R (`& $07 == $04`). Allowed only if some non-empty, non-solid-topped cell exists below (on the waterfall always allowed until the boss scroll starts — can be fatal). `EDGE_FALL_CODE`=`$81`: no X movement on the press frame nor until 20 px have fallen = 17 frames without forward progress (computed) | b7:4491-4501, `can_player_drop_down` b7:5276 |
| In water | A is ignored (no jump) | b7:4486 |

### `PLAYER_JUMP_COEFFICIENT` ($94) — the sub-pixel trick

- It is simply the Y sub-pixel (low byte of the 16-bit Y). It is zeroed only at spawn (`init_player_attributes` b7:5349). Landing snaps the pixel but leaves the sub-pixel, so it carries from jump to jump.
- Effect on a normal jump: peak is 59 px if the value is < `$57` at take-off, otherwise 58 px; arrival frame on some platforms shifts by 1 (e.g. +32 px platform: frame 48 vs 49) (computed).
- How it changes: every air frame adds the velocity's low byte. One flat-ground jump adds `$4d` (mod 256): 00 -> 4d -> 9a -> e7 -> 34 -> 81 -> ce -> 1b ... (computed). Jumps that land at another height, ledge falls, the respawn drop and the indoor room walk (`indoor_transition_set_pos` b7:4818 reuses it) add other amounts. It does not change while standing.
- Waterfall bug (comment at b7:4400): while the screen is scrolling up (Y < `$50`, rising) **and the player has positive X velocity (moving right)**, `set_frame_scroll_if_appropriate` runs twice per frame — once from `handle_jump` b7:4751 and again from `calc_player_x_vel` b7:4405. The sub-pixel add is done twice; only the second carry counts for that frame's scroll. Moving left, not moving, or being stopped by the right edge / a wall = normal single add.
- Size of the effect (computed, full 29-frame rise above Y=`$50`): never moving right = 58-59 px. Right held the whole rise = 54 to 62 px depending on the starting coefficient (best `$00` = 62, worst `$7c` = 54). Choosing right vs not-right per frame so that carries are dodged = 65 px for every starting value. This is the "platform skip": up to +6 px per jump, or reaching a platform a normal jump misses.
- To control it in a harness: read `$94` before each jump, model the adds exactly as above (single add = left/neutral, double add = moving right while scrolling), search the per-frame L/R pattern.

## 4. Hitbox

The player is a single point (X, Y). Each enemy carries a box chosen by its collision code (low nibble of `ENEMY_SCORE_COLLISION`) **and by the player's pose**; hit when `0 <= Y - top < height` and `0 <= X - left < width` (`check_players_collision` b7:6695-6790, `set_enemy_collision_box` b7:7101). Tables: `collision_box_codes_00..03` b7:7251-7323 (bytes: dy, dx, height, width, relative to the enemy).

Pose selection (b7:6752-6770): in water -> table 0; jumping (`PLAYER_JUMP_STATUS` != 0) -> table 1; `PLAYER_SPRITE_CODE` = `$17` (prone, outdoor only) -> table 2; else table 3 (standing, also ledge-falling, also every indoor pose).

Equivalent danger zone around the player for an enemy bullet (collision code 1; regular bullets use code 1, cannonballs 5, dragon fireball 2 — `bullet_collision_code_tbl` b0:387). "dx/dy" = enemy position minus player position:

| Pose | dy range | dx range | Size (w x h) |
|------|----------|----------|--------------|
| Standing / walking | -14 .. +16 | -4 .. +5 | 10 x 31 |
| Jumping (curled) | -1 .. +10 | -5 .. +6 | 12 x 12 |
| Prone | +10 .. +13 | -11 .. +12 | 24 x 4 |
| In water | -17 .. +2 | -12 .. +7 | 20 x 20 |

So yes: the curled jump box is far shorter than standing (12 vs 31 px), and prone is only 4 px tall at foot level (wider, 24 px).

| Special case | Rule | Where |
|--------------|------|-------|
| Water + Down held | all collision skipped: enemies, bullets **and weapon items**. No time limit. But no X movement and no firing (aims 3-6 are blocked in water) | b7:6756-6758, b6:294-300 |
| Indoor room + crouch (Down, no L/R) | enemy bullets (type 1) cannot hit. Other enemies still use the standing box | b7:6709-6715 |
| Rising in a jump vs landable enemies | no test while Y velocity < 1 | b7:6741-6747 |
| Player state not 1 (dropping in, dead) | no collision at all | b7:6703-6705 |
| Enemy collision flag | enemies with `ENEMY_STATE_WIDTH` bit 0 set never touch the player; indoor enemies with Y < `$9c` never do | b7:7360-7371 |

## 5. Death and respawn

| Fact | Value | Where |
|------|-------|-------|
| What kills | touching an enemy / enemy bullet box (no invincibility), or Y >= `$e8` while not hidden | b7:6862, b7:4238 |
| `kill_player` | state -> 2, Y velocity `$fd80` (-2.5), weapon still held for now | b7:4246 |
| Death phase 1 | flies back 1 px/frame (outdoor) under gravity until falling at >= 2 px/frame onto a non-empty, non-water cell (or off the bottom). Flat ground: 35 frames; pit from Y=`$e8`: 45 frames (computed) | `player_state_routine_02` b7:4298 |
| Death phase 2 | lies still for `$40` (64) frames | b7:4338 |
| Then | `init_player_dec_num_lives`: all player vars and **`P1_CURRENT_WEAPON` = 0** (weapon and Rapid both lost), lives - 1, state 0 | b7:5150, `init_player_and_weapon` b7:5338 |
| Respawn frame | 1 frame in state 0: position set, `NEW_LIFE_INVINCIBILITY_TIMER` = `$80` (128), then state 1 falling with full control | `player_state_routine_00` b7:4152 |
| Respawn position | L1, L5-L8: X=`$30` (48), Y=`$20` (32). L3 waterfall: X=`$30`, Y=`$50` (80). L2/L4 rooms and indoor boss screens: X=`$70` (112), Y=`$60` (96) | `level_spawn_position_index` b7:4147, tables b7:4221-4228 |
| X fallback | outdoor only: if nothing to land on under the spawn column, tries X=`$10`,`$20`,...,`$d0` and takes the first column with any non-empty cell below; else `$30` | b7:4166-4188 |
| Death warp forward? | Horizontally no (you die at about X=`$80`, respawn at `$30`), unless the left columns have no floor. Vertically on the waterfall yes: you respawn at Y=`$50`, the scroll line, wherever you died — but it costs about 100 frames | inference from the two rows above |
| Level start | same routine: drop from the same spawn point with the same 128-frame invincibility. Weapon is kept between levels (only `init_player_attributes` runs) | b7:4153 (inference for "between levels") |
| Drop time from spawn | Y=`$20` to standing Y `$a4`: lands on frame 44; `$84`: 38; `$64`: 32; `$c4`: 49 (computed). X control and scrolling work during the drop | |
| New-life invincibility | 128 frames. Enemies and bullets pass through you; **it does not hurt them**. While it runs `ENEMY_ATTACK_FLAG` = 0: enemies do not fire and soldier generation is off | b7:6858, b7:4068-4079 |
| World during the death animation | enemies, bosses, bullets and auto-scroll keep running; only player-driven scroll stops; `ENEMY_ATTACK_FLAG` = 0 (state != 1) so enemies hold fire. Your bullets already in flight keep flying and hitting | b7:3205-3212, b7:4075 |
| Weapon strength side effect | see section 7: after a death the strength code is 0, so strength-scaled bosses spawned afterwards have fewer HP | |

Frame cost of one death (computed): killed on frame K -> control back on frame K+101 (35 + 64 + 1 + 1), on flat ground. On a scrolling section you are then 80 px left of the scroll point, so about **180 frames (3.0 s) lost**, plus the weapon. In a pit: about 190.

## 6. Firing

`check_player_fire` b6:290. No firing when hidden or electrocuted; in water no firing with aim 3-6 (any Down).

| Weapon (`P1_CURRENT_WEAPON` low bits) | Trigger | P1 slots | Per press | Where |
|------|---------|----------|-----------|-------|
| 0 Default | new B press | 0-3 (max 4 alive) | 1 bullet | b6:318-320, `create_bullet_max_04` b6:598 |
| 1 M | **B held** | 0-5 (max 6) | 1 bullet when its counter allows | b6:313-316, `gen_m_bullet_if_delay_met` b6:439 |
| 2 F | new B press | 0-3 (max 4) | 1 fireball | `fire_weapon_routine_f` b6:478 |
| 3 S | new B press | 0-9 (max 10) | up to 5; **partial sprays are created** when fewer than 5 slots are free (order: centre, +1, -1, +2, -2 steps of 11.25 degrees) | `fire_weapon_routine_s` b6:495 |
| 4 L | B held, or new press | 0-3 (one laser = 4 segments) | 4 segments | `fire_weapon_routine_l` b6:533 |

There are 16 bullet slots; P2 would use 10-13 / 10-15 / 6-15. P1 can never use more than the ranges above (b6:604-620). No cooldown timer exists for Default, F, S: the only limits are "new press" and free slots.

Rapid (bit 4, `$10`) does **not** change fire rate or slot counts. It only raises bullet speed (and halves indoor flight time).

### Bullet speed and life

| Weapon | Speed px/frame | With Rapid | Where |
|--------|----------------|-----------|-------|
| Default, M | 3.0 (diagonal 2.12 + 2.12) | 4.0 (2.83) | `bullet_velocity_normal` b6:897, `bullet_velocity_rapid` b6:922 |
| L | 4.0 always (Rapid flag forced on) | 4.0 | b6:534-535, `bullet_velocity_ptr_tbl` b6:879 |
| F | centre moves 1.5 (1.06 diag), bullet circles it, radius 15 px, period 16 frames | 2.0 (1.41) | `bullet_velocity_f` b6:970, `bullet_velocity_f_rapid` b6:946, swirl tables b6:1562-1567 |
| S | 2.99 (`$02fd`), 32-direction table | 3.48 (`$037c`) | b6:1153-1249 |

| Life rule (outdoor and indoor boss screen) | Where |
|------|-------|
| Creation frame: bullet sits at the muzzle (no move), is already hittable (L: only after its segment delay) | `inc_player_bullet_routine` b6:1445, sprite-code test b7:6965 |
| Despawn at once when X < 5, X >= `$fb` (251), Y < 5 or Y >= `$e8` (232) | `destroy_bullet_if_off_screen` b6:1711 |
| Solid background kills bullets only where the level header says so: L6 and L7 (`$81`); not L1-L5, L8 | `check_bullet_solid_bg_collision` b6:1697, headers b2:1402-1514 |
| While the screen scrolls horizontally each bullet loses 1 px/frame of screen X (so 3 becomes 2 net) | `add_scroll_to_bullet_pos` b6:1605 |
| **After a hit (or wall) the slot stays busy 6 more frames** (ring sprite): free for a new shot 7 frames after the hit frame | `set_bullet_routine_to_2` b7:7042, `player_bullet_collision_routine` b6:1747 |

Flight time to the right edge from the scroll point (computed, muzzle at X=`$90`, 107 px): Default 36 frames standing still, 54 while scrolling; with Rapid 27 / 36. That is how long a missed shot blocks its slot.

### M auto-fire (`PLAYER_M_WEAPON_FIRE_TIME`)

Low nibble = frames since the last bullet, high nibble = bullets in the current hold. Held: +1 per frame, bullet when low nibble reaches 8; after 6 bullets in one hold the 7th needs 15 frames. Released: high nibble cleared, low nibble still counts up (capped at 7). If all 6 slots are full it retries every frame. (b6:322-332, b6:439-475)

| Input pattern | Bullet frames | Rate (computed) |
|---------------|---------------|------|
| Hold B | 0, 8, 16, 24, 32, 40, **55**, 63, ... (7 bullets per 63 frames) | 6.7 /s |
| Hold, release 1 frame at least once per 6 bullets | every 8 frames | **7.5 /s (the cap)** |
| Tap every other frame (30 Hz) | every 8 frames | 7.5 /s — tapping faster gives nothing |
| 3 on / 3 off (10 Hz) | 0, 8, 18, 26, ... | 6.7 /s |

### L

A new B press recreates all 4 segments in slots 0-3, **deleting the old laser** even mid-flight. With B merely held, a new laser fires only when all 4 slots are empty. Segments leave the muzzle 1, 4, 7 and 10 frames after firing (`laser_bullet_delay_tbl` b6:593; indoor rooms 1, 3, 5, 7), 12 px apart, each worth 1 hit. On a hit the front-most live segment is removed, the rest carry on (b7:7014-7033). The laser does not pierce: 4 segments = at most 4 hits in total.

### Indoor rooms (levels 2 and 4, not their boss screens)

| Fact | Value | Where |
|------|-------|-------|
| Direction | aim is ignored; every bullet travels "into" the screen: up 1.0 px/frame, Rapid 2.0; X drifts toward X=`$80` at distance/64 px/frame (Rapid /32) | `set_indoor_bullet_vel` b6:984 |
| Lifetime | `PLAYER_BULLET_TIMER` = `$2a` (42 frames), Rapid `$15` (21). L: always 21 frames at 2 px/frame after its delay | `set_indoor_bullet_delay` b6:658, b6:1437-1443 |
| When it can hit a far (back wall) enemy | **only on the single frame when the timer is 1**: 41 frames after firing (Rapid: 20). Earlier it passes through | `@bullet_delay` b7:6979-6982 |
| Near enemies (`ENEMY_STATE_WIDTH` bit 5 set) | can be hit only by bullets fired while crouching (slot bit 7), at any time in flight | b7:6973-6977, b6:818-822 |
| Slot busy | 48 frames per bullet (hit) / 49 (miss); Rapid 27 / 28. Room cleared: all bullets vanish at once | b6:1748-1749, computed |
| S spread at the wall | pellets end at 0, +-5, +-10 px from the centre line (both with and without Rapid) | `s_bullet_pos_mod_tbl` b6:1861, computed |
| **S trap** | the 5 pellets of one press all reach timer 1 on the same frame, and only one bullet per enemy per frame can score (section 7): **one S press = 1 damage on a single wall target** | inference from b7:6964-7036 |

Sustained damage on one wall target in an indoor room (computed, slots are the limit, press rate hardly matters):

| Weapon | No Rapid | With Rapid |
|--------|----------|-----------|
| Default (4 slots / 48 f) | 5.0 /s | 8.9 /s |
| M (auto every 8 f, 6 slots) | 7.5 /s | 7.5 /s |
| S (2 presses / 48 f, 1 hit each) | 2.5 /s | 4.4 /s |
| L, B held (4 hits / 33 f) | 7.3 /s | same |
| L, re-press every 27 f | 8.9 /s | same |

### Shots per second on one target, outdoor (computed)

Rule used: one hit per enemy per frame (section 7); slot free 7 frames after its hit. "Point blank" = the muzzle point is inside the enemy's bullet box, so the hit lands on the firing frame. S figures assume a box deep enough that all 5 pellets are still inside when their turn comes (5 consecutive frames, about 13 px of travel); on a shallow target the late pellets fly on and hold their slots until off-screen.

| Press rate | Default / F | S | L | M |
|-----------|-------------|---|---|---|
| 30 /s (every 2nd frame) | 30 | 60 (the per-enemy cap) | 30 | 7.5 |
| 15 /s (every 4 f) | 15 | 60 | 30 (2 segments per press) | 7.5 |
| 12 /s (every 5 f) | 12 | 56 | 24 | 7.5 |
| 10 /s (every 6 f) | 10 | 50 | 20 (a press every 7 f gives 25.7) | 7.5 |
| B held | 0 | 0 | 15 | 6.7 |

Point blank, Default never runs out of slots (slot limit is 4 per 7 frames = 34 /s). At range the slots bind — hits per second with a flight time of T frames:

| Flight time T | Default 30 Hz | Default 10 Hz | S 30 Hz | S 10 Hz |
|------|------|------|------|------|
| 5 f (15 px) | 20.0 | 10.0 | 46.9 | 36.4 |
| 10 f (30 px) | 13.2 | 9.9 | 33.0 | 29.8 |
| 20 f (60 px) | 8.4 | 7.8 | 21.0 | 19.8 |
| 30 f (90 px) | 6.0 | 5.6 | 15.0 | 14.0 |

General formula: Default/F sustained rate = min(press rate, 4 / (T + 7)) per frame. A 10 /s presser loses nothing against 30 /s once the target is more than about 17 frames of flight away (51 px, 68 with Rapid). L at range: 4 hits per laser, next laser when held = T + 16 frames later.

## 7. Damage

| Fact | Value | Where |
|------|-------|-------|
| Damage per hit | **always 1 HP**, every weapon, every enemy (`sbc #$00` with carry clear) | `bullet_collision_logic` b7:7053-7066 |
| Not hittable | HP 0, or HP `$f0`-`$ff` | b7:7057-7060 |
| **One hit per enemy per frame** | the bullet loop (slot 15 down to 0) returns after the first bullet that connects | `bullet_enemy_collision_test` b7:6954-7036 |
| Invulnerability frames after a hit | none in this code | |
| Which bullets count | sprite code non-zero and bullet routine = 1 (live). Enemy needs `ENEMY_STATE_WIDTH` bit 7 clear | b7:6965-6969, b7:7374 |
| Bullet box | bullet is a point; tested against `collision_box_codes_04` b7:7327 for the enemy's collision code. Carry is left clear before both subtractions, so the box is effectively shifted +1 px in X and Y (inference) | b7:6984-6992 |
| Several enemies | each enemy runs its own test, so one frame can damage several enemies, one bullet each | |
| S at point blank | all 5 pellets spawn on the same point; they score on 5 consecutive frames if they stay inside the box | inference |
| F | no piercing, removed on hit like any bullet | b7:7014-7033 |
| L | 4 separate 1-HP segments, see section 6 | |

`PLAYER_WEAPON_STRENGTH` ($2f) is **not damage**. It is a difficulty code recomputed every frame from the current weapon: Default 0, M 2, F 1, S 3, L 2 (`weapon_strength` b7:4111, `set_player_weapon_strength` b7:4096). Enemies read it when they spawn or pick delays:

| Use | Formula | Where |
|-----|---------|-------|
| L6 giant soldier HP | `$40` + 8 x strength (64 / 72 / 80 / 88) | b0:7507 |
| L8 alien guardian and heart HP | `$37` + 16 x strength (+16 x completions), cap `$a0` (55 / 71 / 87 / 103) | `set_guardian_and_heart_enemy_hp` b0:9017 |
| L8 alien mouth HP | strength + 4 | b0:9635 |
| L8 spider HP | strength + 2; spider spawn HP `$18` + 2 x strength | b0:10020, b0:10212 |
| Timing only | rotating gun delays b0:819/894, boss eye delay b0:2755, Gemini b0:5536, wall cannon delay b7:9457, soldier generation b2:1752, soldier bullets b0:1489 | |

Exploit: HP is fixed when the enemy is created. Holding Default (or having just died) at the moment a strength-scaled boss spawns gives it the lowest HP; e.g. the L8 heart has 55 HP with Default and 103 with S. Whether a faster weapon repays the extra HP is a route decision (details belong to the enemy agent).

## 8. Weapon items

Pickup = player point inside the item's box (collision code 2), state 1, not ducked in water; +1,000 points (`pick_up_weapon_item` b7:6884). Item code = `ENEMY_ATTRIBUTES & 7`, passed straight from the pill box / flying capsule / red soldier that dropped it (b0:647-654).

| Code | Item | Effect | Where |
|------|------|--------|-------|
| 0 | R | `P1_CURRENT_WEAPON` \|= `$10`, weapon letter unchanged | `@set_rapid_flag` b7:6924 |
| 1 / 2 / 3 / 4 | M / F / S / L | sets the letter. **Rapid is kept only if it is the same letter you already hold; a different letter clears Rapid** | `@compare_and_set_weapon` b7:6933-6945 |
| 5 | B | `INVINCIBILITY_TIMER` = `$80` (level 7: `$90`), minus 1 on frames where `FRAME_COUNTER & 7 == 0` -> 1017-1024 frames, about 17 s (level 7: 1145-1152, about 19 s) | `@set_invincibility_timer` b7:6912, `decrement_invincibility_effect` b7:4082 |
| 6 | Falcon | `destroy_all_enemies` + 32-frame palette flash (no pause) | b7:6901-6903 |

- Order matters: take the letter first, then R. Rapid and the letter are both lost on death, kept across levels.
- B barrier: you are immune to the collision path, **and any enemy you touch with 1 <= HP < `$f0` is destroyed outright** (HP set to 0, normal destroy routine and score), whatever its HP (`@invincible_collision` b7:6869). That includes boss parts whose player-collision box you can reach. Pits still kill. During the first 128 frames after a spawn the new-life timer is checked first, so touching does nothing then (b7:6858).
- Falcon (`destroy_all_enemies` b7:8150): every enemy slot with an active routine **and a non-zero sprite**, except pill box sensors (type 2) and flying capsules (type 3) and HP exactly `$f0`, is sent to its destroyed routine. Background-tile bosses (no sprite) are untouched; sprite-based enemies on screen die regardless of HP (which bosses qualify: enemy agent).

Item flight, outdoor (`weapon_item_routine_00/01` b0:144-258, `weapon_item_init_vel_tbl` b0:195):

| Fact | Value |
|------|-------|
| Launch | from the destroyed box / capsule position: Y velocity -3.0, X velocity +0.5 px/frame (waterfall: +0.25 if X < `$80`, else -0.75) |
| Gravity | `$10`/256 = 0.0625 px/frame^2 |
| Arc (computed) | apex 72 px up after 48 frames; back at launch height after 96 frames, 48 px to the right in world terms (it also moves left with the scroll) |
| Height at frame t | 3t - 0.03125 t^2 px above launch |
| Landing | only while falling and below Y=`$20`: lands on any non-empty cell (floor, water surface, solid) 8 px under it and rests at cell top + 10, i.e. 6 px below the player's standing Y on the same floor |
| Bounce | reverses X at X >= `$e8`, X < `$18`, or a solid wall 10 px ahead (walls only on L5-L7) |
| Removed | X < 8 (scrolled off) or Y >= `$e8` |
| Bullets | pass through it (`ENEMY_STATE_WIDTH` = `$80`) |
| Indoor room | arcs to the floor and rests at Y=`$a4`; removed when the next room transition starts | 

Pickup reach (item position minus player position, computed from code 2 boxes): standing dx -10..+11, dy -20..+22; jumping dx -10..+11, dy -2..+15; prone dx -18..+19, dy +5..+20. A jump can therefore grab an item 43-60 px above standing height; a resting item is taken by simply running through it.

## 9. Aim and muzzle positions

`set_player_aim_for_input` b7:4982, `d_pad_player_aim_tbl` b7:5029. Aim codes: 0 up (facing right), 1 up-right, 2 right, 3 down-right, 4 prone right, 5 prone left, 6 down-left, 7 left, 8 up-left, 9 up (facing left).

| D-pad | Outdoor and indoor rooms, facing right | facing left | Indoor boss screen |
|-------|------|------|------|
| none | 2 | 7 | 0 (up) |
| R | 2 | 2 | 2 |
| L | 7 | 7 | 7 |
| U | 0 | 9 | 0 |
| U+R / U+L | 1 / 8 | 1 / 8 | 1 / 8 |
| D | 4 (prone) | 5 (prone) | 0 on the ground (no crouch); `$0a` = up while jumping |
| D+R / D+L | 3 / 6 | 3 / 6 | 2 / 7 on the ground; 3 / 6 while jumping |
| U+D | 7 | 7 | 7 |

- Jumping uses the same table; Down alone in the air (aim 4/5) is turned into **straight down** (velocity index `$0b`) (b6:357-367). So in the air all 8 directions are available; on the ground 7 (no straight down; Down = prone, a low horizontal shot).
- Diagonals need L or R held, which also moves the player (ground and air). Up, and prone, are the only stationary non-horizontal aims.
- Falling off a ledge is not "jumping": Down gives a prone-height horizontal shot, not a downward one.
- Indoor rooms: aim does not steer bullets (section 6); only crouch matters.

Muzzle offset from the player point (US build; `bullet_initial_pos_00/01` b6:714-754, indoor boss `_02/_03` b6:759-786):

| Aim | On ground (dx, dy) | Jumping (dx, dy) |
|-----|--------------------|------------------|
| 0 up | +5, -27 | 0, -16 |
| 1 up-right | +13, -16 | +15, -15 |
| 2 right | +16, -5 | +16, 0 |
| 3 down-right | +13, +6 | +15, +15 |
| 4 prone right | +16, +9 | (down) 0, +16 |
| 5 prone left | -16, +9 | (down) 0, +16 |
| 6 down-left | -13, +6 | -15, +15 |
| 7 left | -16, -5 | -16, 0 |
| 8 up-left | -13, -16 | -15, -15 |
| 9 up (left) | -5, -27 | 0, -16 |

Indoor room muzzle (`set_indoor_bullet_pos_and_slot` b6:788): standing (+1 or -1, -24); crouching (-1, -12) and the bullet is flagged as a crouch shot; jumping (0, 0) with Y capped at `$98`. Indoor boss screen, ground: up (-1, -24), up-right (+15, -16), right (+16, -6), left (-16, -6), up-left (-15, -16).

F fireball: the circle centre starts 16 px beyond the muzzle along the aim (`f_bullet_initialization_tbl` b6:1064); on the firing frame the bullet itself is at the muzzle.

## 10. Things that look exploitable

| # | Fact | Where |
|---|------|-------|
| 1 | Every jump costs exactly 1 frame of forward motion (A-press frame). Never jump unless needed; walking off a ledge is free, Down+A costs 17 frames | section 3 |
| 2 | One hit per enemy per frame: point-blank S can reach 60 HP/s; indoors one S press is worth 1 HP on a wall target | sections 6-7 |
| 3 | Slot stays busy 6 frames after a hit, and until off-screen after a miss: missed shots are what throttle fire, not press speed | section 6 |
| 4 | L: a new press deletes the laser in flight. At point blank press every 4 frames (2 hits each); at range hold B | section 6 |
| 5 | M: release B for one frame at least every 6 bullets to skip the 15-frame gap (7.5 /s instead of 6.7 /s). M is the weakest gun at point blank | section 6 |
| 6 | Indoor rooms: hits land exactly 41 frames after firing (20 with Rapid). Rapid nearly doubles Default's room DPS; fire the last shots of a room early, they cannot be sped up | section 6 |
| 7 | Boss HP scales with the weapon held at spawn (section 7). Death resets it to the minimum | b0:7507, b0:9017 |
| 8 | B barrier destroys anything it touches below `$f0` HP; Falcon destroys every sprite enemy | section 8 |
| 9 | First 128 frames of every level and life: enemies cannot fire, soldiers are not generated, and you walk through enemies | b7:4068-4079 |
| 10 | Waterfall: moving right while the screen scrolls double-adds the Y sub-pixel: up to 65 px of scroll per jump instead of 58-59 | section 3 |
| 11 | Water + Down = total invulnerability (but frozen and unable to shoot). Indoor crouch = immune to bullets | section 4 |
| 12 | Prone box is 4 px tall; curled-jump box 12 px, low half of the body. Rising through a landable enemy's box is not tested | section 4 |
| 13 | Landing and ledge detection use only the centre point: you can stand or land with one pixel of floor under the centre; you land 4 px early | section 3 |
| 14 | Jumping above the top of the screen sets `PLAYER_HIDDEN` (high byte of Y): no firing, the Y >= `$e8` death test is skipped, but enemy collision is not skipped | b7:5130-5132, b6:291, b7:4236 |
| 15 | Indoor room advance: Up alone, on the ground, after the room is cleared; Up alone before that = 48-frame electrocution. Up+L/R just walks | `d_pad_up_pressed` b7:4590 |
| 16 | Boss reveal scroll is a fixed 96 frames (64 on the waterfall) and starts only while the player is actively scrolling at offset >= `$a0` of the stop screen — keep holding right through it | section 2 |
| 17 | Pause: the whole level routine is skipped while paused, so no timer in this file advances (B barrier, invincibility, bullets) | `level_routine_04` b7:3185-3187 |
| 18 | No position wrap at screen edges: X is clamped to `$19`..`$e6` outdoors | section 1 |

## Open points (not verified here)

- Exact cart and rock speeds, which enemies carry which item code, which bosses are sprite-based: enemy agent.
- The +1 px shift of the bullet box (section 7) and the pickup ranges (section 8) are derived from carry-flag reasoning and table arithmetic; worth one emulator check each.
- All "computed" frame counts assume no lag frames and `VERTICAL_SCROLL` = 0 for landing rows.
