# Ninja Gaiden (NES, US) - RAM map as verified in the harness (BizHawk 2.11.1, NesHawk)

The field list the bridge reports is `knowledge/ram.json`. This file is the evidence. "Code" = read in the ROM with
`tools/dis6502.py` (and the public disassembly `dl/NinjaGaidenNES`, read only). "Test" = an experiment in the
emulator (`tools/ram_verify.py` -> `knowledge/ram_verify.json`, screenshots `shots/verify/`), "Trace" = seen in the
per-frame trace of the TAS 4751M replay (`logs/tas4751.trace.csv` / `logs/tas4751.events.json`).

## Frame numbering (the Contra lesson, measured here)

* A fresh EmuHawk launch connects to the bridge at **framecount 1** (frame 1 already emulated with no input):
  input row k is applied on frame **k+1**.
* After `BizHawk.reset()` (bridge `reset` = `client.reboot_core`) the framecount is **0**: row k is frame **k**,
  exactly the .bk2 numbering. `tools/launch_vs_reset.py logs/tas4751.inputs.txt 5000`: launch playing rows[1:]
  and reset playing rows end on the same framecount with the same RAM SHA-1 and an identical per-frame trace
  (4,999 frames compared, 0 differ), so the two ways are the same power-on (row 1 must be empty for the launch way).
* `reset()` drops every Lua memory callback (measured: an exec tick counts 0 after a raw `reset`).
  `BizHawk.reset()` re-registers the ticks; anything else registered with `watch` must be set again after a reset.
* Opposing directions: the base config's `OpposingDirPolicy` is 0 ("Priority"): BizHawk silently drops one of
  Up+Down / Left+Right sent through `joypad.set` (measured: Up+Down+Left reached the game as Up+Left = $0A). Movies
  bypass that, which is why the TAS desynced at frame 806 in the first replay. Every harness instance now uses
  policy 2 ("Allow"): the console gets exactly the row (tested: U+D -> $2A = $0C, L+R -> $03, U+D+L -> $0E).
  Legal-run rules are enforced by `check_inputs.py`.

## Controller, frame and lag

| Address | Meaning | Proof |
|---|---|---|
| `$28` | raw read (the routine `$E819` shifts 8 bits of `$4016` into it); after the NMI it equals `$2A` | Code `$E819`, `$F9CC` |
| `$2A` | **held buttons** after this frame's read (A=$80 B=$40 Select=$20 Start=$10 Up=$08 Down=$04 Left=$02 Right=$01, the harness's mask layout) | Code `$F9CC-$F9E7`; Test `pad_held_$2A_new_$29` |
| `$29` | **new presses** this frame (`$28 & ~old $2A`) | same |
| `$21` | the first of the two reads | Code |
| `$EA` | cinematic engine's own "previous buttons" (cutscene Start edge = `$28 & ~$EA`, bank 4 `$83A9`) | Code |

* The controller is read **in the NMI, every frame the NMI runs** (`$F9CC`): twice; if the two reads differ
  (NesHawk emulates the DMC/controller conflict) the game keeps the previous frame's buttons. A press that starts on
  such a frame arrives one frame late. `run_comp()` / bridge `stepc` re-presses it (pad byte `$2A`, from ram.json).
* **No input latency**: a button on row k is in `$2A` after frame k and acts that frame (Right on frame 2247 ->
  x 32.0 -> 33.128 after 2247; Test).
* BizHawk lag frames (no `$4016` read) happen only while the NMI is off (power-on, scene loads): 9 in the first
  174 frames of the TAS replay. They are reported as `lagged` / `lag`.
* **Game lag** is different: the main loop (`$C085`: wait for the NMI flag `$1F` at `$F104`, then sprite 0 at
  `$F5A2`) runs once per frame when it keeps up. The tick `gm` counts executions of `$C088` (the instruction after
  the NMI wait) per frame: `gm == 0` on a play frame = the game logic did not run that frame. Because `$29` is
  rebuilt by every NMI, **a press whose first frame falls on a game-lag frame is lost** (the next NMI sees it
  already held). Hold presses 2+ frames (the human cap does) or check `gm`.
* Pause: Start in play toggles `$1E` bit 7 (`$C091`); while paused the main loop skips the game (timer frozen; Test).

## Mode (where the CPU is) - `ng/mode.py`

There is no single "game mode" byte. The harness counts executions of fixed code addresses per frame (bridge `tick`;
a bank-switched address only counts while its 4 ROM bytes are mapped, so the NMI's sound bank cannot fake it):
`gm` play loop `$C088`, `dw` death wait `$E40E` (190 frames), `bk` boss-kill tally `$D5C0`, `se` stage-end wait
`$D621`, `nx` next-stage load `$E8A8`, `cs` cinematic script loop `$80EC` (bank 4), `csskip` script end `$813E`
(bank 4; Start or natural end), and the power-on flow `title` `$80B0` (title script $0D starts), `act1` `$80BA`
(ACT I card $0C starts), `csdone` `$80BD` (game starts). `$2D` is TASVideos' "game mode" but it is the NMI's saved
A register (Code `$F91A`); it only looks like a mode.

## Player, stage, HUD

| Address | Meaning | Proof |
|---|---|---|
| `$86` / `$85` | Ryu x (screen pixels) / sub-pixel | Test: walking adds exactly 384/256 px a frame; OAM sprites at x-12..x+3 |
| `$AD` / `$AC` | Ryu x speed px / sub (1.128 = 1.5 px walking) | Test |
| `$8A` | Ryu y (208 on the 1-1 floor; >= $F8 = pit) | Test jump: 208 -> 160 -> 208 |
| `$89` / `$87` | y speed px (signed, $FC = -4 at a jump) / fraction (+$37 per airborne frame) | Test |
| `$84` | flags: bit 2 airborne, bit 6 facing left | Test (bit 2 set on the jump frames) |
| `$80` | animation (0 stand, 1 walk, 3 sword 16 frames, 5 jump) | Test |
| `$8B` | bit 7 = dead (poking $80 runs the death routine `$E3C9`) | Code `$E3BA`; Test |
| `$95` | post-hit invincibility timer | public map |
| `$65` | Ryu HP (16 full) | Trace / Test (falls when hit) |
| `$64` | ninpo | Trace |
| `$C9` | sub-weapon ($80 fire wheel, $81 star, $82 windmill, $84 invincible fire wheel, $85 jump&slash) | Trace |
| `$76` | lives (2 at boot, HUD P-02) | Code `$E53A`; Test (death -> 1) |
| `$63` | timer seconds (150 at a stage start, `$FF` = time up -> death) | Test, Code `$F7E4` |
| `$62` | sub-timer 60..0; `$F7E4` decrements it **only on play frames with no background column waiting** (`$4C` bit 6 clear: the main loop skips `$F7E4`, the enemies and the spawn checks on those frames) - so a timer second is 61 such frames, 62-63 real frames while scrolling | Code `$C0C1`; Test |
| `$66` | boss HP **display** (drains to the real HP `$0497`) | Trace |
| `$6D` | stage (area) 0..21 = 1-1,1-2,2-1,2-2,2-3,3-1,3-2,3-3,4-1..4-4,5-1..5-4,6-1,6-2,6-3,6-4a,6-4b,6-5 | HUD screenshot of every value (`shots/lvl_hud.png`, `ng/stages.py`) |
| `$6E` | room (0..47); first room of each stage = bank 0 `$AF2C` table | Code; Trace |
| `$51` / `$52` / `$50` | stage x scroll px / screen / fraction | Test: scroll grows while x stays 128 |
| `$4C` | scroll flags (bit 6 = a column waits to be drawn) | Code |
| `$33` | $97 from the first control frame of a stage (sprite-pointer byte; the autosplitter's start) | Trace / clock |
| `$BE` | bit 7 = stage over: run the area's cutscene (`$E347`) | Code |
| `$04B8` | boss kill indicator (bits 6-7 -> tally loop `$D5BD`) | Code |
| `$1FD` | stack byte: $D5 -> $D6 at the end of the final tally (autosplitter end) | Trace |

## RNG

* `$BF` (`nmi_count`) is incremented at the end of **every NMI** (`$FA1B`) and is the game's only "random" source
  (the disassembly's every read of it: enemy throw delays/speeds, the demon's spit). It does not depend on input at
  all; it depends only on how many NMIs have run since power-on (the reset routine clears RAM, so it starts at 0).
  The NMI runs on every frame except while the game has NMIs switched off (scene loads), so input changes `$BF`
  only by changing how long the game spends in loads, pauses etc. Test: +1 per frame in play.
* Enemy-slot leftovers (x fraction inherited from the slot's previous occupant) are the other "luck" (TASVideos).

## Enemy slots (8)

`$0400+i` id, `$0410+i` action, `$0460+i` / `$0458+i` x / fraction, `$0480+i` / `$0478+i` y / fraction,
`$0490+i` HP (bosses: slot 7, `$0497`), `$0498+i` state; `$73` busy-slot bits. Test on the 2-3 boss state.

## Test results (`python tools/ram_verify.py`, 2026-10-19; `knowledge/ram_verify.json`)

All 11 PASS: `$2A`/`$29` (Right held: pad 1,1,1, new 1,0,0); x `$86.$85` +384/256 px every walking frame, speed
`$AD.$AC` = 1.128; OAM sprites at x-13..x+3 of `$86`; jump `$89` = $FC, y 208 -> 160 -> 208, `$84` bit 2 while
airborne; scroll 0 -> 106 while x stays 128; timer: 63 frames between `$63` ticks while scrolling = exactly 61
play frames with `$4C` bit 6 clear; `$BF` +1 every play frame; pause `$1E` = $80, timer frozen, Start again
resumes; poked death: 190 death-wait frames, lives 2 -> 1; boss 2-3 (TAS state): Ryu HP `$65` 15 -> 14 when hit,
slots: ids `$0400` [0,0,0,3,3,3,42,24], boss slot 7 HP `$0497` 16 = `$66` display 16, x/y in `$0460`/`$0480`
match the OAM sprite clusters.

HUD cross-check (`shots/verify/hud_sheet.png`, TAS states `room03_2-1` / `room05_2-1` + 30 frames): RAM timer 135 /
ninpo 20 / `$C9` $82 / lives 2 <-> HUD "TIMER-135", "-20", Windmill Star icon, "P-02"; RAM 122 / 10 / $85 <-> HUD
"TIMER-122", "-10", Jump & Slash icon. Score: `$61:$60` = HUD digits / 100 (HUD shows 4 digits + "00").
Sub-weapon changes in the TAS replay: $85 at 1,223 (1-1), cleared to 0 at every boss kill ($D610), $82/$85 in Act II,
$81 -> $80 (Fire Wheel) in 3-1, ... (`logs/tas4751.trace.csv`).

## The TAS 4751M replay through the bridge (`logs/tas4751.events.json`)

Stage loads / control frames (control = load + 151 everywhere): 1-1 -/174, 1-2 2316/2468, 2-1 3150/3302,
2-2 5952/6104, 2-3 8847/8999, 3-1 9677/9829, 3-2 11282/11434, 3-3 13589/13741, 4-1 14417/14569, 4-2 16530/16682,
4-3 18808/18960, 4-4 21202/21354, 5-1 21973/22125, 5-2 24276/24428, 5-3 26457/26609, 5-4 29108/29260,
6-1 29911/30063, 6-2 31487/31639, 6-3 34410/34562, 6-4a 37126/37278, 6-4b 37935/38087, 6-5 38781/38933.
These match the research replay (bk2 movie playback) frame for frame. No deaths. No game lag. 33 BizHawk lag
frames. 59 play frames on which the game kept the previous buttons (DMC conflict; e.g. 203, 497, 516).
Stage exit 127 frames, room change 23 frames, boss tally + exit 129 frames.
