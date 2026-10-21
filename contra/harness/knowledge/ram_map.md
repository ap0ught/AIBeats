# Contra (NES, US) — RAM map for the harness

Source of every address and label: the annotated disassembly `vermiceli/nes-contra-us` v1.4, file `src/ram.asm`
(local read-only clone: `dl\nes-contra-us`). Line numbers are for that clone (cloned 2026-10-11, `--depth 1`).
Label names below are the disassembly's own. "P1 / P2" means the address is a 2-byte array, P1 first.
Cross-checks: DataCrystal's RAM map (datacrystal.tcrf.net/wiki/Contra_(NES)/RAM_map) agrees on $18, $1A, $25, $30, $32, $38, $40, $41, $90, $AA, $F1, $FC/$FD, $200, $600, $700;
the community LiveSplit autosplitter (github.com/cactuar1989/nes_autosplitters, `Contra/contra.asl`) uses $1C, $2C and $30 exactly as described in section 2.

All claims in this file are **read in the code** unless marked *(inference)*.

---

## 1. Frame structure, lag, RNG (read this first)

- The whole game runs inside the NMI handler `nmi_start` (`src/bank7.asm:294`). Between NMIs the CPU spins in `forever_loop` (`bank7.asm:284`).
- **Lag frame**: `NMI_CHECK` ($1B) is set to 1 at `bank7.asm:324` and cleared at `bank7.asm:338`. If an NMI arrives while it is still non-zero
  (`bank7.asm:302-303`), the handler jumps to `handle_sounds_set_ppu_scroll_rti` (`bank7.asm:355`): it only runs the sound engine and re-writes the scroll,
  then returns into the interrupted frame. On such a frame there is **no OAM DMA, no controller read, no game logic, and `FRAME_COUNTER` does not advance**.
  A lag frame therefore costs exactly one real frame and shifts the "global timer" phase by one relative to real time.
  BizHawk's lag flag (no controller poll that frame) should coincide with this *(inference — verify)*. `$1B` bit 7 is set while inside `play_sound` (`bank7.asm:513-525`).
- **`FRAME_COUNTER` ($1A)**: incremented once per non-lag frame at the top of `exe_game_routine` (`bank7.asm:690`), in every game mode, **including while paused**
  (pause only makes `level_routine_04` return early, `bank7.asm:3185-3187`). It is never reset during a real game: the only write is in `set_next_demo_level`
  (`bank7.asm:1124`, attract-mode demo). RAM is zeroed at reset (`bank7.asm:242-249`), so its value at any moment = (non-lag frames since power-on/reset) mod 256,
  unless the attract demo was allowed to start. This is the speedrunners' "global timer".
- **`RANDOM_NUM` ($34)**: the only RNG byte. `forever_loop` does `lda FRAME_COUNTER / adc RANDOM_NUM / sta RANDOM_NUM / jmp` continuously until the next NMI
  (`bank7.asm:284-288`; the carry is not cleared, so it feeds back). Its value when a frame's logic runs depends on how many loop iterations fit in the previous
  frame's idle time, i.e. on the exact CPU-cycle cost of the previous frame's logic. It is deterministic in an emulator but changes with anything that changes
  cycle counts (number of sprites/enemies/bullets, button presses that create bullets, pause). Reset to 0 only in the demo (`bank7.asm:1125`); one enemy routine
  rewrites it (`bank0.asm:5543`, see `code_enemies_bosses.md`).
- **Pause**: `check_for_pause` (`bank7.asm:3425`). A new Start press (`CONTROLLER_STATE_DIFF & $10`) sets `PAUSE_STATE` ($25)=1 and the level routine returns
  without running game logic that frame. Un-pausing needs another *new* Start press (so at least one frame with Start released in between); on the un-pause frame
  logic runs normally. Minimum cost of a pause = 2 frames of game logic lost (press, release) while `FRAME_COUNTER` advances 2 *(inference from the code path; matches
  TAS notes "one less pause usage saved 2 frames")*. Pause is ignored while `PPU_READY` ($20) != 0 or in demo mode.
- Controller: `load_controller_state` (`bank7.asm:961`) reads both pads twice (DPCM-safe) and, in 1-player mode, **ORs pad 2 into pad 1** (`bank7.asm:980-987`).
  `CONTROLLER_STATE` ($F1) = held buttons; `CONTROLLER_STATE_DIFF` ($F5) = buttons newly pressed this frame (not held last frame).
  Bit layout: 7=A, 6=B, 5=Select, 4=Start, 3=Up, 2=Down, 1=Left, 0=Right.

---

## 2. State machine and the two clock events

### 2.1 Game routine — `GAME_ROUTINE_INDEX` ($18) (`game_routine_pointer_table`, `bank7.asm:705`)

| $18 | Routine | Meaning |
|---|---|---|
| 0 | `game_routine_00` | one-shot init of the title scroll |
| 1 | `game_routine_01` | title logo scrolling in / player-select menu; Konami code is checked here (`konami_input_check`, `bank7.asm:930`) |
| 2 | `game_routine_02` | attract-mode demo (resets `FRAME_COUNTER` and `RANDOM_NUM` when a demo level starts) |
| 3 | `game_routine_03` | Start was pressed: "1 PLAYER" flashes until `INTRO_THEME_DELAY` ($28) and `DELAY_TIME_LOW_BYTE` ($2A) both reach 0 |
| 4 | `game_routine_04` | one frame: clear $28-$EF and $300-$6FF, set lives |
| 5 | `game_routine_05` | in a level: dispatch on `LEVEL_ROUTINE_INDEX` ($2C) |
| 6 | `game_routine_06` | ending (after the heart): dispatch on `GAME_END_ROUTINE_INDEX` ($19) |

`$19` is shared: `GAME_ROUTINE_INIT_FLAG` during routines 2/3, `GAME_END_ROUTINE_INDEX` during routine 6.

Title timing facts: pressing Start/Select while the logo is still scrolling jumps straight to the menu and starts the intro jingle, setting `INTRO_THEME_DELAY`=$A4
(`bank7.asm:1091-1106`); that timer is decremented only on even `FRAME_COUNTER` values (`bank7.asm:1110-1117`), i.e. 328 frames. A second (new) Start press selects
the game (`bank7.asm:1064`). `game_routine_03` then needs `$28`==0 and `$2A`==0 (it sets `$2A`=$40 on entry). So the earliest stage-1 load is ~328 frames after the
first Start press no matter how fast the second press is, as long as the second press comes at least $40+1 frames before the jingle timer ends.
[stated: TASVideos forum, Invariel 2016: "Start or Select on frame 11 and Start again on frame 16" skips the scroll.]
The Konami code (`konami_code_lookup_table`, `bank7.asm:954`: U U D D L R L R B A) must be entered during `game_routine_01` (while the logo scrolls — pressing Start early ends the scroll,
and `konami_input_check` keeps being called after the scroll completes, see `bank7.asm:750-751`); `KONAMI_CODE_STATUS` ($24)=1 when accepted; `KONAMI_CODE_NUM_CORRECT` ($3F) counts progress ($FF = failed).

### 2.2 Level routine — `LEVEL_ROUTINE_INDEX` ($2C) (`level_routine_ptr_tbl`, `bank7.asm:3040`)

| $2C | Routine | What happens | Leaves when |
|---|---|---|---|
| 0 | `level_routine_00` (3055) | zero nametables, load the level header into $40-$5F, `BOSS_DEFEATED_FLAG`=0 | 1 frame (plus lag) |
| 1 | `level_routine_01` (3110) | draws "STAGE n / name / REST nn"; sets `$2A`=$C0 | 1 frame |
| 2 | `level_routine_02` (3133) | score/stage screen, counts `$2A` down from $C0 (192 frames), then loads level graphics, palettes, starts the stage music, sets `VERTICAL_SCROLL` | timer 0 |
| 3 | `level_routine_03` (3175) | draws the first screen one tile column (row on the waterfall) per frame, counting `LEVEL_TRANSITION_TIMER` ($61) down: $30 (48) frames outdoor horizontal, $20 (32) indoor, 30 rows vertical (`init_lvl_nametable_animation`, 5525) | when it finishes: `SPRITE_LOAD_TYPE` ($6A)=$FF and $2C=4 **on the same frame** (3178-3180) |
| 4 | `level_routine_04` (3184) | normal play: pause check, player, bullets, scroll, enemies, soldier generation | `BOSS_DEFEATED_FLAG` ($3B) != 0 → 8; both players game over → $0A |
| 5 | `level_routine_05` (3248) | level finished or game over: clears $40-$EF and $300-$6FF but keeps `P1_CURRENT_WEAPON`; `CURRENT_LEVEL`++; if it reaches 8 → `GAME_ROUTINE_INDEX` 6, `CURRENT_LEVEL`=9, `GAME_COMPLETION_COUNT`++ | 1 frame |
| 6 | `level_routine_06` (3319) | game-over CONTINUE/END screen | Start |
| 7 | `level_routine_07` (3359) | game over, no continues | Start |
| 8 | `level_routine_08` (3366) | boss destroyed: **player still has full control**, enemies still run. Waits while `$2A`==$FF, otherwise counts `$2A` down; when 0 and `PLAYER_STATE`==1, plays sound $46 and $2C=9 | see below |
| 9 | `level_routine_09` (3407) | end-of-level sequence: **inputs are zeroed every frame** (`run_end_level_sequence_routine`, `bank3.asm:1228-1233`), scripted walk/jump | `end_level_sequence_02` → $2C=5 |
| $0A | `level_routine_0a` (3417) | game-over delay (`GAME_OVER_DELAY_TIMER` $29 from $60) | → 5 |

`END_LEVEL_ROUTINE_INDEX` ($2D) = sub-state inside routine 9 (0 wait for landing, 1 scripted exit, 2 final delay), `bank3.asm:1239-1547`.
`BOSS_DEFEATED_FLAG` ($3B): 0 normal; 1 boss destroyed (`level_boss_defeated`, `bank7.asm:8384`, which also sets `$2A`=$FF); $81 during the scripted exit (`bank3.asm:1269`); 2 at the end (`bank3.asm:1538`).
End-of-level scripted exits (for planning where to stand when control is lost), `bank3.asm:1332-1534`:
stage 1 walk right, jump at X>=$90; stages 2/4 P1 walks **left** to the elevator at X=$0C; stage 3 walk to X within 8 px of $80 then jump; stages 5/6/7 walk right off the screen
(player hidden at X>=$F8); stage 8: no walking. After the exit: `LEVEL_END_SQ_1_TIMER` ($0191, $F0, decremented on odd `FRAME_COUNTER` only → a hard cap of 480 frames) then
`level_end_level_delay_timer_tbl` (`bank3.asm:1322`): $A0 (160) frames for every stage except the waterfall ($E0 = 224).
The exit ends as soon as the player's `LEVEL_END_LVL_ROUTINE_STATE` ($0192) returns to 0, i.e. as soon as he is hidden/off-screen — so **standing next to the exit when control is lost saves real time on stages 1-7**.

### 2.3 CLOCK START — "the blue life medals appear" (Stage 1)

Chain, read in the code:
1. `level_routine_03` finishes drawing the first screen: `lda #$ff / sta SPRITE_LOAD_TYPE` and `inc LEVEL_ROUTINE_INDEX` (`bank7.asm:3178-3180`).
2. Later in the **same** NMI, `draw_sprites` (`bank1.asm:3998`) sees `SPRITE_LOAD_TYPE` != 0 and calls `draw_hud_sprites` (`bank1.asm:4218`), which writes one sprite per spare life
   (max 4; `P1_NUM_LIVES` $32 = 2 at a normal start → two medals; tile $0A, Y=$10, X=$10,$1C,$28,$34, attribute 0 = blue palette for P1) into `OAMDMA_CPU_BUFFER` ($0200-$02FF).
3. The **next** NMI copies $0200-$02FF to the PPU (`bank7.asm:308-309`), so the medals are in the picture drawn after that NMI.

RAM condition: **let N = the first frame at whose end `$2C == 4` (with `$30 == 0`, `$1C == 0`, `$18 == 5`). Equivalently the first frame with `$6A == $FF`.**
The medals are first visible in the picture of frame N+1 *(inference: one frame of OAM latency; the harness should confirm once by looking for tile $0A at Y=$10 in PPU OAM / a screenshot)*.
The autosplitter used by the community starts on exactly this transition (`$2C` 3→4 with `$1C`==0).
Note: Bill himself is not yet on screen; `player_state_routine_00` runs on the first `level_routine_04` frame and drops him in from Y=$20, X=$30 (`bank7.asm:4152-4228`).

### 2.4 CLOCK END — "Bill reverts to the standing pose and control is removed" (Stage 8)

Chain, read in the code:
1. Heart's HP reaches 0 → its destroyed routine eventually calls `level_boss_defeated` (`bank7.asm:8384`): `BOSS_DEFEATED_FLAG`=1, `DELAY_TIME_LOW_BYTE` ($2A)=$FF (exact heart chain and frame counts: see `code_enemies_bosses.md`).
2. Next frame `level_routine_04` sees `$3B` != 0 and only sets `$2C`=8 (`bank7.asm:3188-3189, 3238-3245`) — no game logic runs on that single frame.
3. `level_routine_08` runs normal logic each frame (player fully controllable). While `$2A` == $FF it just waits (`bank7.asm:3374-3377`); an enemy routine (the boss's explosion sequence) later stores a
   finite delay into `$2A` (`set_delay_remove_enemy`, `bank7.asm:8393`); then `$2A` counts down 1/frame; at 0, if `PLAYER_STATE` ($90) == 1, sound $46 plays and `$2C` becomes 9 (`bank7.asm:3381-3401`).
   If the player is dead/respawning (`$90` != 1) at that moment the transition waits — a death here delays the end of the run.
4. From the next frame on `level_routine_09` calls `run_end_level_sequence_routine` **before** the player routine and zeroes `CONTROLLER_STATE`/`_DIFF` for both pads (`bank3.asm:1228-1233`).
   With no input a grounded Bill shows `PLAYER_SPRITE_SEQUENCE` ($BC) = 0 (standing). If Up or Down was held he visibly snaps from aim-up/prone to standing — this is the board's stop frame.
   If he is airborne when `$2C` becomes 9 he keeps the jump curl until he lands (`end_level_sequence_00` waits for `PLAYER_JUMP_STATUS` == 0, `bank3.asm:1245-1265`), so be **on the ground, holding Up or Down** when it happens.

RAM condition: **let A = the first frame at whose end `$2C == 9` with `$30 == 7`.** On frame A the player was still controlled; frame A+1 is the first frame whose logic ignores input
and writes the standing sprite to the OAM buffer; that picture is displayed on frame A+2 *(inference: same one-frame OAM latency as the medals)*.
So the on-screen interval between "medals appear" and "Bill stands" is **A − N + 1 frames** *(inference; the harness/timing agents should confirm the ±1 against the record video's convention)*.
The autosplitter splits on exactly `$2C` becoming 9. Seconds = frames / 60.0988.

---

## 3. Global / level variables

| Addr | Label | Meaning |
|---|---|---|
| $18 | GAME_ROUTINE_INDEX | see 2.1 |
| $19 | GAME_END_ROUTINE_INDEX / GAME_ROUTINE_INIT_FLAG | see 2.1 |
| $1A | FRAME_COUNTER | global timer, +1 per non-lag frame, runs while paused |
| $1B | NMI_CHECK | 1 while a frame's logic is running; non-zero at NMI entry = lag frame; bit 7 = inside play_sound |
| $1C | DEMO_MODE | 0 real game, 1 attract demo |
| $1D | PLAYER_MODE_1D | 1 = 1 player, 7 = 2 players |
| $20 | PPU_READY | counts 5→0 after `configure_PPU`; screen is blanked and pause is ignored while non-zero |
| $22 | PLAYER_MODE | 0 = 1 player, 1 = 2 players |
| $24 | KONAMI_CODE_STATUS | 1 = 30-lives code accepted |
| $25 | PAUSE_STATE | 1 = paused |
| $28 | INTRO_THEME_DELAY | title jingle timer ($A4, −1 every other frame) |
| $29 | GAME_OVER_DELAY_TIMER | $60 → 0 |
| $2A/$2B | DELAY_TIME_LOW_BYTE / HIGH_BYTE | general delay: score screen ($C0), boss-defeated delay ($FF = "wait") |
| $2C | LEVEL_ROUTINE_INDEX | see 2.2 — **both clock events are transitions of this byte** |
| $2D | END_LEVEL_ROUTINE_INDEX | sub-state of routine 9 |
| $2F | PLAYER_WEAPON_STRENGTH | recomputed every frame from the weapon: default 0, F 1, M 2, L 2, S 3 (`weapon_strength`, `bank7.asm:4111`). Used by enemies for HP/aggression scaling (not bullet damage — see `code_player_mechanics.md`) |
| $30 | CURRENT_LEVEL | 0-7 = stages 1-8; 9 = ending |
| $31 | GAME_COMPLETION_COUNT | loops completed (0 in a run) |
| $32/$33 | P1_NUM_LIVES / P2 | spare lives (2 at start, 29 with the code); 0 = last life |
| $34 | RANDOM_NUM | RNG byte, see section 1 |
| $35 | OAMDMA_CPU_BUFFER_OFFSET | rotating OAM write offset (+$4C per frame) — sprite flicker order |
| $37 | INDOOR_SCREEN_CLEARED | base rooms: 0 not cleared, 1 cleared (cores gone), $80 cleared and fence removed |
| $38/$39 | P1_GAME_OVER_STATUS / P2 | 1 = game over (P2 is 1 in a 1-player game) |
| $3A | NUM_CONTINUES | |
| $3B | BOSS_DEFEATED_FLAG | see 2.2 |
| $3C-$3E | EXTRA_LIFE_SCORE_LOW/HIGH | next extra-life score |
| $40 | LEVEL_LOCATION_TYPE | 0 outdoor, 1 indoor (base), $80 base boss screen / advancing between rooms |
| $41 | LEVEL_SCROLLING_TYPE | 0 horizontal (and bases), 1 vertical (waterfall) |
| $48 | LEVEL_ALT_GRAPHICS_POS | screen number where boss graphics load ($FF after loading) |
| $49-$4B | COLLISION_CODE_x_TILE_INDEX | tile-index thresholds for floor / empty / water collision |
| $58 | LEVEL_STOP_SCROLL | screen number where scrolling stops ($FF once boss auto-scroll starts) |
| $59 | LEVEL_SOLID_BG_COLLISION_CHECK | bullets collide with solid background when negative (stages 6, 7) |
| $61 | LEVEL_TRANSITION_TIMER | stage-start draw timer; base-room advance animation timer |
| $64 | LEVEL_SCREEN_NUMBER | **current screen / base-room index** (0-based) |
| $65 | LEVEL_SCREEN_SCROLL_OFFSET | pixels scrolled within the screen (0-255 horizontal; 0-239 vertical); bases: 0-3 during the advance animation |
| $68 | FRAME_SCROLL | pixels the screen scrolls this frame (0/1 horizontal; up to 4 vertical; 2 when riding a cart) |
| $6A | SPRITE_LOAD_TYPE | 0 = no HUD, $FF = draw life medals — **clock-start flag** |
| $71 | ALT_GRAPHIC_DATA_LOADING_FLAG | 1/2 while boss graphics are being loaded (a source of lag) |
| $73 | INDOOR_SCROLL | base-room transition: 0 none, 1 advancing, 2 done |
| $74 | BG_PALETTE_ADJ_TIMER | fade timer (dragon, UFO, base transitions) |
| $75/$76 | AUTO_SCROLL_TIMER_00 / _01 | boss-reveal auto-scroll timers (1 px/frame while non-zero) |
| $77 | TANK_AUTO_SCROLL | extra scroll per frame while a snow-field tank drives in |
| $79-$7C | SOLDIER_GENERATION_ROUTINE / _TIMER / _X_POS / _Y_POS | random running-soldier spawner (timer −2/frame, −1 while scrolling) |
| $7D | FALCON_FLASH_TIMER | screen flash for the falcon item |
| $82 | ENEMY_SCREEN_READ_OFFSET | read offset into the current screen's enemy list |
| $84 | BOSS_AUTO_SCROLL_COMPLETE | set when the boss-reveal scroll ends |
| $85 | BOSS_SCREEN_ENEMIES_DESTROYED | stage 3: dragon arms destroyed; stage 7: mortar launchers destroyed |
| $86 | WALL_CORE_REMAINING | base rooms: targets left before the fence drops; stage 4 boss: helmets left |
| $87 | WALL_PLATING_DESTROYED_COUNT | base boss screens: platings destroyed |
| $88 | INDOOR_ENEMY_ATTACK_COUNT | base rooms: passes of the scripted enemy list (stops at 7) |
| $89 | INDOOR_RED_SOLDIER_CREATED | base rooms: the one red (item) soldier has been spawned |
| $8A | GRENADE_LAUNCHER_FLAG | base rooms: a grenade launcher is active |
| $8E | ENEMY_ATTACK_FLAG | 1 = enemies may fire and random soldiers may spawn. Cleared every frame and set only when the player is in state 1 with `NEW_LIFE_INVINCIBILITY_TIMER`==0 (`bank7.asm:3925, 4068-4079`) → **nothing shoots and nothing spawns during the first $80 frames of a life** |
| $FC | VERTICAL_SCROLL | PPU scroll Y (waterfall: decrements as the screen climbs) |
| $FD | HORIZONTAL_SCROLL | PPU scroll X |
| $0190 | LEVEL_END_DELAY_TIMER | end-of-level delays |
| $0191 | LEVEL_END_SQ_1_TIMER | cap on the scripted exit |
| $0192/$0193 | LEVEL_END_LVL_ROUTINE_STATE | per-player exit script state |
| $0195 | SOLDIER_GEN_SCREEN | screen the soldier spawner is counting for |
| $0196 | SCREEN_GEN_SOLDIERS | random soldiers generated on this screen |
| $07E2/$07E3 | PLAYER_1_SCORE_LOW/HIGH | score ÷ 100, 16-bit |

World position of the screen on horizontal stages = `$64` × 256 + `$65` (pixels). On the waterfall = `$64` × 240 + `$65` (pixels climbed).
Bill's world X = that + `SPRITE_X_POS` ($0334) *(inference — everything in this engine is stored in screen coordinates, per the code and Blomquist's articles)*.

---

## 4. Player (index 0 = P1, 1 = P2)

| Addr (P1) | Label | Meaning |
|---|---|---|
| $90 | PLAYER_STATE | 0 dropping in (one frame init), 1 normal, 2 dead (death animation), 3 can't move (elevator) |
| $0334 | SPRITE_X_POS | Bill's screen X (integer pixels; there is no X sub-pixel for the player — see `code_player_mechanics.md`) |
| $031A | SPRITE_Y_POS | Bill's screen Y |
| $0300 | CPU_SPRITE_BUFFER / PLAYER_SPRITES | sprite code currently drawn for P1 (bytes 2-9 = eight player-bullet sprites) |
| $034E | SPRITE_ATTR | P1 sprite attributes (bit 3 = +1 Y recoil, 6/7 flips) |
| $94 | PLAYER_JUMP_COEFFICIENT | **Y sub-pixel accumulator; not cleared between jumps** — the waterfall "ledge skip" value (also used for the base-room walk-in animation) |
| $98 | PLAYER_X_VELOCITY | 0, 1 or $FF |
| $C4 / $C6 | PLAYER_Y_FRACT_VELOCITY / PLAYER_Y_FAST_VELOCITY | Y velocity 8.8 (negative = up). Death pop: $FD80 (`bank7.asm:4257-4260`) |
| $A0 | PLAYER_JUMP_STATUS | low nibble 1 = jumping; bit 7 = jumping left |
| $A4 | EDGE_FALL_CODE | non-zero = falling (bit 7 dropping through a platform, bit 6 walked off left, bit 5 walked off right) |
| $B8 | PLAYER_FALL_X_FREEZE | Y threshold (ledge Y + $14) below which X control returns after a drop |
| $A2 | PLAYER_FRAME_SCROLL | scroll requested by this player this frame |
| $B2 | PLAYER_WATER_STATE | bit 2 in/leaving water, bit 3/7 walking out, bit 4 entry finished |
| $CC | PLAYER_WATER_TIMER | water enter/exit animation timer |
| $B6 | PLAYER_ON_ENEMY | standing on a cart / floating rock |
| $D4 | PLAYER_FAST_X_VEL_BOOST | extra X speed from a moving cart/rock |
| $BC | PLAYER_SPRITE_SEQUENCE | pose: outdoor 0 standing, 1 aiming up, 2 prone, 3 running or jump curl, 4 dead; indoor 0 facing wall, 1 electrocuted, 2 crouch, 3 strafing, 5 walking into the screen, 6 dead |
| $A6 | PLAYER_ANIMATION_FRAME_INDEX | animation frame within the pose |
| $9E | PLAYER_ANIM_FRAME_TIMER | run animation timer; in state 2 the death countdown ($40 after landing) |
| $D2 | PLAYER_SPECIAL_SPRITE_TIMER | death / jump-curl animation counter |
| $D6 / $D8 | PLAYER_SPRITE_CODE / PLAYER_SPRITE_FLIP | final sprite code and flip bits |
| $C2 / $C0 | PLAYER_AIM_DIR / PLAYER_AIM_PREV_FRAME | aim direction 0-$0A (0 up facing right, 1 up-right, 2 right, 3 down-right, 4 prone right, 5 prone left, ... clockwise) |
| $AA | P1_CURRENT_WEAPON | low nibble: 0 default, 1 M, 2 F, 3 S, 4 L; **bit 4 = Rapid**. ($AB = P2). Preserved across stage transitions (`bank7.asm:3252-3264`) |
| $AC | PLAYER_M_WEAPON_FIRE_TIME | machine-gun auto-fire state (high nibble bullets in burst, low nibble frame counter) |
| $CE | PLAYER_RECOIL_TIMER | frames of recoil left |
| $AE | NEW_LIFE_INVINCIBILITY_TIMER | $80 at stage start and after each respawn, −1/frame |
| $B0 | INVINCIBILITY_TIMER | Barrier: $80 ($90 on stage 7), −1 every 8th `FRAME_COUNTER` (≈1024 / 1152 frames) |
| $B4 | PLAYER_DEATH_FLAG | bit 0 dead, bit 1 was facing left |
| $BA | PLAYER_HIDDEN | non-zero = not drawn (off-screen / exited) |
| $C8 | ELECTROCUTED_TIMER | base fence stun timer |
| $CA | INDOOR_PLAYER_JUMP_FLAG | forces the hop when a new base room appears |
| $D0 | INDOOR_PLAYER_ADV_FLAG | walking "into" the screen between base rooms |
| $A8 / $BE | PLAYER_INDOOR_ANIM_Y / _X | start position of the base-room walk-in |
| $92, $96, $9A, $9C | INDOOR_TRANSITION_* | base-room walk-in velocities/accumulators |
| $DA | PLAYER_BG_FLAG_EDGE_DETECT | bit 7 draw behind background, bit 0 walk off ledges without falling (set during scripted exits) |
| $DF | PLAYER_GAME_OVER_BIT_FIELD | 0 = only P1 playing |
| $F1 / $F5 / $F9 | CONTROLLER_STATE / _DIFF / CTRL_KNOWN_GOOD | held / newly pressed / last good read (P1; +1 for P2) |

Kill line: Bill dies if `SPRITE_Y_POS` >= $E8 while visible (`bank7.asm:4238-4240`).
Spawn positions: stage type 0 (stages 1, 5-8) X=$30 Y=$20 falling; bases X=$70 Y=$60; waterfall X=$30 Y=$50 (`bank7.asm:4147-4228`); if nothing is below, the game scans X=$10,$20,… for a floor.

---

## 5. Player bullets — 16 slots, index 0-15 (`ram.asm:1384-1517`)

| Addr | Label | Meaning |
|---|---|---|
| $0388+i | PLAYER_BULLET_SLOT | 0 = free; else weapon type + 1 (1 default, 2 M, 3 F, 4 S, 5 L); can be negative |
| $03C8+i / $03B8+i | PLAYER_BULLET_X_POS / _Y_POS | screen position |
| $0408+i / $03E8+i | PLAYER_BULLET_X_VEL_FAST / _FRACT | X velocity 8.8 |
| $03F8+i / $03D8+i | PLAYER_BULLET_Y_VEL_FAST / _FRACT | Y velocity 8.8 |
| $03A8+i / $0398+i | PLAYER_BULLET_X_VEL_ACCUM / _Y_VEL_ACCUM | sub-pixel accumulators |
| $0418+i | PLAYER_BULLET_TIMER | F swirl / indoor S size / L spacing; on base stages the "depth" timer |
| $0428+i | PLAYER_BULLET_AIM_DIR | direction 0-9 |
| $0438+i | PLAYER_BULLET_ROUTINE | bullet routine index |
| $0448+i | PLAYER_BULLET_OWNER | 0 = P1, 1 = P2 |
| $0458+i | PLAYER_BULLET_F_RAPID / _S_INDOOR_ADJ | |
| $0468+i | PLAYER_BULLET_DIST / _S_ADJ_ACCUM | distance travelled (outdoor S scale) |
| $0478+i, $0488+i, $0498+i, $04A8+i | F/S helper arrays; $04A8 = PLAYER_BULLET_S_BULLET_NUM (index within a spray) | |
| $0368+i / $0378+i | PLAYER_BULLET_SPRITE_CODE / _ATTR | |

Only 8 of the 16 are drawn each frame: even slots on even `FRAME_COUNTER`, odd slots on odd (`bank7.asm:3890-3917`) — bullets flicker at 30 Hz by design, so a screenshot shows at most half of them.
Slot allocation, per-weapon limits and the fire rules are in `code_player_mechanics.md`.

---

## 6. Enemies — 16 slots, index 0-15 (`ram.asm:1519-1640`)

| Addr | Label | Meaning |
|---|---|---|
| $04B8+i | ENEMY_ROUTINE | routine index + 1 (0 = empty slot) |
| $0528+i | ENEMY_TYPE | enemy type id (table in `code_enemies_bosses.md` / `docs/Enemy Glossary.md`) |
| $0578+i | ENEMY_HP | **hit points (bosses too)** |
| $033E+i / $0324+i | ENEMY_X_POS / ENEMY_Y_POS | screen position |
| $030A+i | ENEMY_SPRITES | sprite code (0 = invisible / background-tile enemy) |
| $0358+i | ENEMY_SPRITE_ATTR | |
| $0508+i / $0518+i | ENEMY_X_VELOCITY_FAST / _FRACT | |
| $04E8+i / $04F8+i | ENEMY_Y_VELOCITY_FAST / _FRACT | |
| $04D8+i / $04C8+i | ENEMY_X_VEL_ACCUM / _Y_VEL_ACCUM | sub-pixel accumulators |
| $0538+i | ENEMY_ANIMATION_DELAY | general timer (e.g. stage-4 boss vulnerability timer) |
| $0548+i | ENEMY_VAR_A | hit sound / misc |
| $0558+i | ENEMY_ATTACK_DELAY / ENEMY_VAR_B | attack delay; item arc |
| $0568+i | ENEMY_FRAME | animation frame |
| $0588+i | ENEMY_SCORE_COLLISION | SSSS CCCC: score code, collision-box code |
| $0598+i | ENEMY_STATE_WIDTH | bit 7 = bullets pass through (invulnerable), bit 0 = no player collision, bit 6 = player can stand on it |
| $05A8+i | ENEMY_ATTRIBUTES | type-specific (e.g. which weapon an item gives; fire-beam/claw phase) |
| $05B8+i … $05E8+i | ENEMY_VAR_1 … ENEMY_VAR_4 | type-specific (dragon arm links in VAR_3/VAR_4; stage-4 helmets' HP in VAR_4) |

`ENEMY_CURRENT_SLOT` ($83) = slot being processed. An enemy is vulnerable only while bit 7 of `ENEMY_STATE_WIDTH` is clear — the harness can read "is the core open / is the mouth open" straight from this bit.

---

## 7. Sound

| Addr | Label | Meaning |
|---|---|---|
| $0106+s | SOUND_CODE | sound code playing in slot s (0-5) |
| $0122 | INIT_SOUND_CODE | last sound code requested |
| $012F | PAUSE_STATE_01 | pause flag for the sound engine |

Useful sound codes as event markers: $52 player death (`bank7.asm:4247`), $54 pause jingle (`bank7.asm:3437`), $46 stage-clear fanfare — played on the exact frame `$2C` goes 8→9 (`bank7.asm:3399-3401`),
$26 title jingle, level music codes in `level_vert_scroll_and_song` (`bank7.asm:3164`).

---

## 8. Suggested harness watch list (minimum)

`$18 $19 $1A $1B $1C $20 $25 $2A $2C $2D $2F $30 $32 $34 $37 $3B $40 $58 $61 $64 $65 $68 $6A $75 $76 $77 $7A $84 $85 $86 $8E $90 $94 $98 $A0 $A4 $AA $AC $AE $B0 $BC $C2 $C4 $C6 $F1 $F5 $FC $FD`,
`$031A $0334`, bullets `$0388-$0397 $03B8-$03D7`, enemies `$04B8-$04C7 $0528-$0537 $0578-$0587 $0598-$05A7 $033E-$034D $0324-$0333`.
Per-frame lag = (`$1A` did not change) or the emulator's lag flag.
