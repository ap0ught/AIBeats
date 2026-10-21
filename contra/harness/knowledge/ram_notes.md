# RAM notes - what was actually watched in the emulator (day 1, 2026-10-11)

Machine: BizHawk 2.11.1, core NesHawk unless said otherwise, `Contra (USA).nes` (file CRC32 C50A8304, board UxROM).
Addresses and one-line results: `ram.json`. The disassembly-based map by the other agent is `ram_map.md`; this file only
says what I observed and where the two differ. Method: `tools/ram_capture.py` keeps all 2 KB of RAM plus the PPU's OAM
for every frame of a run from power-on (`logs/ref_stage1.ram.npy`, 4,620 frames: title, stage 1, the start of stage 2),
`tools/ram_verify.py` asks the questions (`logs/ref_stage1.ramverify.json`); base rooms and bosses were watched with
`tools/base_probe.py`, `tools/watch.py`, `tools/hp_trace.py`; stage 8 with `tools/clock_end_evidence.py`.

## Verified (observed, with the numbers)

| What | Address | Observation |
|---|---|---|
| Game mode | `$18` | 0 -> 1 on frame 10, -> 3 on frame 12 (Start), -> 4 on 339, -> 5 on 340 (opening: Select on 11, Start on 12). 2 = attract demo when nothing is pressed. 6 after the heart |
| Level routine | `$2C` | 1@341, 2@342 (score screen, 201 frames incl. 8 lag), 3@543 (48 frames), **4@591** (play), 8@3837, 9@3999, 5@4318, next stage: 0@4324 ... 4@4562 |
| Stage number | `$30` | 0 -> 1 on frame 4319; 7 -> 9 after the heart |
| Screen / base room | `$64`, `$65` | stage 1: screens 0-12, `$65` = pixel offset, wraps exactly when `$64` increments, equals `$FD`. Base: `$64` = room, `$65` counts the 4 walk-in steps |
| Frame counter | `$1A` | +1 on all 4,587 non-lag frames, +0 on all 33 lag frames. Runs during pause |
| RNG | `$34` | changes on 4,567 of 4,620 frames; all 256 values occur. Core-dependent (below) |
| Lag | bridge `lagged` | = frames on which `$1A` does not advance. Lag frames in the reference: 2,3,5-10 (power-on), 536-543 and 4521-4530 (stage graphics load), 3832 (boss destroyed), 4320-4326 (level change). None during normal play in stage 1 |
| Controller as the game sees it | `$F1` (new presses `$F5`) | bits A80 B40 Sel20 St10 U08 D04 L02 R01. Equal to what was sent on 3,294 of 3,301 play frames |
| Player state | `$90` | 0 -> 1 on L+1; 2 while dying |
| Player X, Y | `$0334`, `$031A` | screen coordinates. X +1 per frame up to 128, then the screen scrolls 1 px/frame instead. The PPU draws him there one frame later |
| Pose | `$BC` | 0 standing, 1 gun up (Up), 2 prone (Down), 3 running/jump curl |
| Aim | `$C2` | Up 0, Up+Right 1, forward 2, Down+Right 3, prone 4 (facing right) |
| Sprite code | `$D6` (= `$0300`) | 15 standing, 22 gun up, 23 prone, 8/9 jump curl |
| Jump status | `$A0` | low nibble 1 from the frame after a new A press until landing |
| Weapon | `$AA` | `$01` M, `$02` F, `$03` S, bit 4 Rapid. A new letter clears Rapid. Kept into the next stage |
| Lives | `$32` | spare lives; 2 at the start, +1 when the score passed 20,000 (frame 3835: boss bonus), game over after a death at 0 |
| New-life invincibility | `$AE` | 127 on L+1, 0 on L+128 |
| Death flag | `$B4` bit 0 | set on the frame of the hit |
| Boss defeated | `$3B` | 1 the frame after the boss's HP is 0 (3836), `$81` after control is lost (4019), 2 for the last delay (4159), 0 on the next load |
| Delay | `$2A` | `$FF` while the boss explodes, then counts to 0; `$2C` becomes 9 on the next frame |
| HUD flag | `$6A` | `$FF` from the frame `$2C` becomes 4 = clock START in RAM |
| Player bullets | `$0388+i` | non-zero = live. S = 5 slots per press, at most 10 live (slots 0-9); 26 of 110 presses in stage 1 produced nothing (no free slot) |
| Enemy slots | `$04B8+i` routine, `$0528+i` type, `$0578+i` HP, `$033E+i` X, `$0324+i` Y, `$0598+i` state | 16 slots. Enemy bullets are type `$01`. HP falls by 1 per hit. State bit 7 set = cannot be hit |
| Boss HP | `$0578 +` slot | stage-1 wall core (type `$11`) 32; stage-8 first boss (type `$10`) 102 with S; base core (type `$14`) 8; base turret (type `$13`) 4 |
| Base room cleared | `$37` | 1 about 57 frames after the core's last hit, `$80` the frame after |
| Base cores left | `$86` | 1 -> 0 about 33 frames after the last hit |
| Fence stun | `$C8` | 48 when Up is read with `$37` == 0 |
| Walk to the next room | `$D0`, `$73` | 4 steps x 34 frames; needs Up read on the frame AFTER `$37` reads `$80`, and again on the frame after each step ends |

## Things the disassembly notes did not say, or that differ

1. **The game ignores the controller on some frames on NesHawk.** The game reads the pad twice per frame and, if the
   two reads differ, reuses the previous frame's buttons (its protection against the DMC/controller-read conflict of
   the real console). NesHawk emulates that conflict; quickerNES does not. Measured: 7 of 3,301 play frames in the
   stage-1 reference, 4 of 720 frames around the stage-8 first boss (3 of them one-frame B presses that were simply
   lost). A one-frame press that falls on such a frame does not exist for the game; a held button is seen one frame
   late. `assemble.py` reports the count ("frames on which the game ignored the controller"); the bridge command
   `stepc` / `BizHawk.run_comp()` re-presses a lost button on the next frame. `ram_map.md` describes the double read
   but not that it fires in practice.
2. **NesHawk and quickerNES are not interchangeable for this game.** With identical inputs (NesHawk boots one frame
   later, so its list is shifted by one): `$34` differs from the 12th frame on; frame counter, level routine, screen
   and scroll stayed identical for 4,200 frames; the controller byte first differed at frame 3076 (item 1); the player
   died at the stage-1 boss at different times. Lag frames were the same. A run built on one core will not replay on
   the other wherever luck or a lost press matters. (`tools/core_cmp.py`.)
3. **Base cores open 16 frames later than the `$F0` delay suggests - and later than a Japanese-ROM TAS expects.**
   `ram_map.md`/`code_enemies_bosses.md` give "hittable from T = 258" for a normal core; observed: state `$9F` -> `$1F`
   on the 258th frame after the room loads - agreed. The published Japanese-ROM movies shoot as if the core could be
   hit about 16 frames earlier (their room-1 bursts land from T about 243 and they walk on 57 frames after the 8th
   hit). On the US ROM those first three shots pass through the closed core. This is why those movies cannot be
   replayed through the bases here (see `reference_run.md`). Not checked against the Japanese ROM itself (we do not have it).
4. **Up at a base fence must be read on the frame after `$37` reads `$80`.** Read one frame earlier (flag = 1) the
   walk still starts, but its first step takes 33 frames instead of 32 and an Up pressed exactly 34 frames later is
   ignored. `code_enemies_bosses.md` says "Earliest Up that works is the frame INDOOR_SCREEN_CLEARED becomes non-zero";
   that Up works but costs a frame.
5. **`$1B` at the end of a frame** is 1 after 31 of the 33 lag frames, 0 otherwise - a usable lag flag from RAM alone,
   but the frame-counter test is exact.
6. **Power-on RAM** reads `$FF` on frame 1 on NesHawk (the game clears it by frame 3).
7. **Stage-start drop.** In every stage tried (1, 2, 8) Bill drops in and a direction first has an effect on frame
   L+2 (L = first frame with `$2C` == 4); one frame of Right during the fall makes him drift right for the whole fall
   (stage 1: lands at X 80 instead of 48). `tools/first_effect.py`.
8. **Pause** freezes logic for exactly the frames between the two Start presses (the frame of the first press
   included, the frame of the second not); afterwards only `$1A`, `$34`, the palette cycle `$72`, the sprite-list
   rotation `$35` and the soldier timer `$7A` differ from the unpaused game. So a pause re-rolls the luck and shifts
   everything keyed to the frame counter, and costs its own length.

## Not verified

* `$B0` (Barrier timer) counting, `$C2` values facing left, weapon values 4 (L), 2-player addresses, the Konami code
  (`$24`) - none were exercised.
* Stages 3-7 boss HP and room/boss addresses of base 2: not watched yet.
* The pit kill line (Y >= `$E8`) was only seen as "died around Y 232".
