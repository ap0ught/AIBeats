# Ninja Gaiden (NES, US) RAM map

**UNVERIFIED unless marked [replay].** It is compiled from public sources. [replay] means I saw the value behave as described in the BizHawk 2.11.1 replay of TAS 4751M (`work/tasrun/tas4751_ram.csv`, one row per frame).

Sources:
- **[TV]** TASVideos GameResources/NES/NinjaGaiden RAM table and symbol files: https://tasvideos.org/GameResources/NES/NinjaGaiden (text copy `dl/tas/text/GameResources_NES_NinjaGaiden.txt`)
- **[DIS]** 0xe1f/NinjaGaidenNES, a byte-exact ca65 disassembly, work in progress. Cloned read-only at `dl/NinjaGaidenNES`. Bank 07 (the fixed `$C000` bank: engine, timer, HUD, player control) is fully source. See `docs/game-notes.md` and `docs/progress.md`. The repo carries its own `.agents/` and `AGENTS.md` files; those are instructions for that repo's authors, not for us.
- **[ASL]** BroDMax/NinjaGaiden-NES-autosplitter (`dl/NinjaGaiden-NES-autosplitter/ninja-autosplitter.asl`). The board's own autosplitter (speedrun.com resource `d6x1v`) sits behind a Cloudflare challenge and was not fetched.

The harness agent keeps its own field list in `knowledge/ram.json`, with `ram_notes.md` for the evidence. It has more fields than this file: pad `$2A`, new presses `$29`, pause `$1E`, boss rush `$77`, dead `$8B`, cutscene `$BE`, boss kill `$4B8`, main loop `$C088`. Where the two disagree, its verified notes win.

## The clock (what the board times)

| Address | Meaning | Source |
|---|---|---|
| `$33` | Goes 0x00 to **0x97** on the first frame of control in a stage. The autosplitter starts when `$33` goes 0 to 0x97 and `$4C` goes 0x40 to 0x00 | [ASL] [replay]: frame 174 in 4751M, with `$4C` 64 to 0 on the same frame |
| `$62` | Sub-timer, 60 down to 0. Decrements once per play frame; `$63` decrements when it wraps. **Carries over between stages** (TV) | [TV] [DIS] [replay] |
| `$63` | Level timer in seconds; the HUD "TIMER". 150 at each stage start, boss rooms included. After a boss dies it is tallied into the score at **3 frames per second**. `$FF` = time up | [TV] [DIS] [replay]: 6-5 tally 147 to 0 in 441 frames |
| `$66` | Enemy (boss) HP **display**. Drains toward the real HP (`$0490-$0497`), about one unit per 2 frames. TASVideos splits acts on `$66 == 0` | [TV] [replay] |
| `$6D` | Area/stage index ("area" in DIS): 0=1-1, 1=1-2, 2=2-1, 3=2-2, 4=2-3, 5=3-1, 6=3-2, 7=3-3, 8=4-1, 9=4-2, 10=4-3, 11=4-4, 12=5-1, 13=5-2, 14=5-3, 15=5-4, 16=6-1, 17=6-2, 18=6-3, 19=6-4 (Masked Devil), 20=6-4 (Jaquio), 21=6-5 (Demon) | [replay] |
| `$6E` | Room number, counting up through the game: 0,1,2..5 (2-1a..d), 6..8 (2-2a..c), 9, 10, 11, 12, 13..15 (4-1a..c), 16, 17..20 (4-3a..d), 21, 22, 23..26 (5-2a..d), 27..33 (5-3a..g), 34, 35, 36..40 (6-2a..e), 41..44 (6-3a..d), 45, 46, 47. **The final room is 47 (0x2F)** | [replay] [ASL] |
| `$6F` | Bit 7 = entered by going back to the previous room | [DIS] |
| `$1FD` | Stack-area byte. 0xD5 to 0xD6 at the end of a tally. The autosplitter splits on it when `$63 == 0` | [ASL] [replay]: 0xD5 from 39,084, 0xD6 at 39,528 (3 frames after `$63` hits 0) |
| `$2D` | "Game mode": non-zero at stage transitions (TASVideos stage splits) | [TV] [replay]: 7/2 at stage loads, 79 on the first control frame, 0 in play, 64/192 during tallies |
| `$BF` | Global timer: counts up every frame (0-255) from power-on. DIS calls it `nmi_count`. Drives tosser delays and toss speed (`$BF >> 1`), the final boss's spew timer and the x speed of its spit | [TV] [DIS] |

**Board events in RAM terms (proposed; to confirm on screen):**
- START N = first frame with `$33 == 0x97` (and `$6D == 0`).
- END P = first frame with `$6D == 21`, `$63 == 0`, after `$66` has reached 0 in that room.
- Time = (P - N) / 60.0988.
- The picture lags RAM: Ryu is drawn about 2 frames after control. The HUD's TIMER-000 may be drawn up to a few frames after `$63 == 0`; the record video showed odd timer values only, 6 frames each.
- **The harness must measure both on-screen offsets.** Until then, keep a few frames of margin.

## Player

| Address | Meaning | Source |
|---|---|---|
| `$64` | Ninpo (spiritual strength) | [TV] [DIS] |
| `$65` | Ryu HP (full 16 = `$10`) | [TV] [DIS] [replay] |
| `$76` | Lives (2 at boot, shown as P-02) | [TV] [DIS] [replay] |
| `$80-$83` | Ryu animation | [TV] |
| `$84` | Ryu facing and state. Bit 6 = facing left; bit 2 = airborne | [TV] [DIS] |
| `$85` / `$86` | Ryu x position: fraction / pixel (screen coordinates) | [TV] |
| `$87` / `$89` | Ryu y speed: fraction / pixel (signed). A jump sets `$89 = $FC` (-4). Each airborne frame adds `$37` to the fraction | [TV] [DIS] |
| `$8A` | Ryu y position. `$F8` or more is a pit | [TV] [DIS] |
| `$8C`, `$8E`, `$8F` | Background collision (Ryu) | [TV namelist] |
| `$92` | 0x00 until the first sword use, then 0x10. **The first sword attack after power-on cannot kill.** The first jumping slash after using Spin Slash keeps a larger hitbox (0x20 allows "impossible" kills) | [TV], 3223M notes |
| `$95` | Invulnerability timer, 60 to 0 after taking damage | [TV] |
| `$AC` / `$AD` | Ryu x speed: fraction / pixel | [TV] |
| `$C9` | Sub-weapon: `$00` none, `$80` Art of the Fire Wheel (5 ninpo), `$81` Throwing Star (3), `$82` Windmill Throwing Star (5), `$84` Invincible Fire Wheel, `$85` Jump & Slash (5 per use) | [TV] [DIS] |

## Screen and scroll

| Address | Meaning | Source |
|---|---|---|
| `$3D` | Bit 7: room starts at its right end ("which way is forward") | [TV] [DIS] |
| `$40` | Ground pointer | [DIS] |
| `$4C` | Scroll flags. Bit 6 = a column is waiting to be drawn, and enemies are skipped that frame (the "drawing interrupt": 0xC1/0x80). Bit 7 = last column came from the left. Bit 0 flips each screen | [TV] [DIS] |
| `$4E` / `$4F` | Screen left column / right column (16 px units) | [DIS] |
| `$50` / `$51` / `$52` | Scroll fraction / stage x / stage x high byte | [DIS] |
| `$53` | Number of screens this room scrolls | [DIS] |
| `$56`, `$59` | CHR banks for sprites / background | [DIS] |
| `$5F` | Ground index of the current column (steps 6 bytes per column) | [DIS] |
| `$67-$6C` | Level scrolling | [TV] |
| `$A2` / `$A3` | Screen position: fraction / pixel | [TV] |
| `$0300-$03BF` | Level collision blocks (2 nibbles per byte; see the TASVideos `ViewBG` Lua for tile kinds: walls, corners, floor, ejecting block, ladder, exits 12-15) | [TV] |

## Enemies (8 slots, index 0-7)

| Address | Meaning |
|---|---|
| `$0400-$0407` | Enemy ID (`11` = bird) |
| `$0408-$040F` | Frames until the next action (direction change, throw) |
| `$0410-$0417` | Action |
| `$0438-$043F` | Movement |
| `$0440-$0447` | Facing |
| `$0448-$044F` / `$0450-$0457` | X speed: fraction / pixel |
| `$0458-$045F` / `$0460-$0467` | X position: fraction / pixel. **The fraction is inherited from the previous occupant of the slot** |
| `$0468-$046F` / `$0470-$0477` | Y speed: fraction / pixel |
| `$0478-$047F` / `$0480-$0487` | Y position: fraction / pixel |
| `$0488-$048F` | Background collision |
| `$0490-$0497` | Hit points: non-zero only for bosses and the grey disc tossers. For bosses, `$497` is the boss and `$496` an alternate |
| `$0498-$049F` | State |
| `$04B8-$04BA` | Boss explosion animations |
| `$04BB-$04C0` | Special weapon x (C, B, A) and y (C, B, A) |
| `$04C1-$04C6` | Special weapon speed |
| `$04C7` / `$04C8` | Special weapon time-out fraction / counter (hourglass, invincible fire wheel) |
| `$04D0-$04EF` | Lanterns, birds and power-ups: x fraction, x, y, frames until the power-up vanishes |
| `$73` / `$74` | Busy slots / current slot |
| `$B4` | Spawn count for the room |
| `$B5` | Spawn iterator (advances by about 8 a frame) |
| `$96-$9B` | Pointers: block / y / id spawn tables |
| `$D0` | Bit 7 = hourglass freeze active [DIS] |

## Other

- `$60` / `$61`: score, little-endian. The display shows 4 digits plus a static "00".
- `$0600`: sound number queue [DIS]. `$06xx` is the sound engine.
- `$02xx`: OAM buffer.
- `$05xx`: unused [TV].
- Code addresses (TV namelist, bank 7): `$EB7B`/`$EB81` player control / in air; `$DECF` slash collision; `$DF1F` damage enemy; `$C75D` bird AI; `$E595` spawn check; `$F603` load new block; `$F7E4` reloads the 60-frame divider [DIS]; `pick_area` `$C0E9` is a hidden stage select that nothing calls [DIS]. Useful for debug states only; it is not part of a legal run.

## Useful Lua (TASVideos page, FCEUX syntax)

`NGRAMview` (HUD overlay), `PredictBird` (bird trajectories), `ViewBG` (collision tiles) and `Spawns` (spawn iterator view) are reproduced on the TASVideos page. They port easily to BizHawk (`memory.readbyte` takes the same addresses).
