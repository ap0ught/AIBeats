# The run clock: definitions on RAM, proven against the picture

Day 1, 2026-10-11. Emulator: BizHawk 2.11.1, core **NesHawk**, ROM `Contra (USA).nes` (file CRC32 C50A8304).
Code: `contra/clock.py` (`start_frame`, `end_frame`, `measure`). Evidence scripts: `tools/clock_start_evidence.py`,
`tools/clock_end_evidence.py`. Raw evidence: `logs/clock_start_evidence_NesHawk.json`, `logs/clock_end_evidence_dbg.json`,
screenshots in `shots/clock_start/` and `shots/clock_end/`.

## Rule (speedrun.com, Contra NES, Any%, 1 player)

Time starts "when the blue life medals appear" at the start of Stage 1. Time ends when, after the heart (final boss)
dies, "Bill automatically reverts to his normal position (standing while pointing his gun forward)" while Up or
Down is held. The record is timed from video, so the convention here is **the frame as SEEN**.

## Frame convention

* "frame f" = BizHawk's `emu.framecount()` after the frame was emulated. From power-on, input row k of an input list
  is applied on frame k+1 (the Lua bridge gets control only after frame 1).
* "RAM of frame f" = RAM read after frame f. "Picture of frame f" = `client.screenshot()` after frame f = what the PPU
  drew during frame f. "PPU OAM of frame f" = the OAM memory domain read after frame f.
* The game builds its sprite list in RAM ($0200-$02FF) at the END of a frame's logic and copies it to the PPU (OAM DMA)
  at the START of the next NMI. So a sprite decided in the logic of frame f is in RAM $0200 on frame f, in the PPU's
  OAM on frame f+1 and in the picture of frame f+1. **Measured, both events: RAM -> picture is exactly +1 frame.**

## START - the blue medals appear

RAM condition: **N = the first frame whose RAM has `$2C == 4`** (LEVEL_ROUTINE_INDEX) with `$18 == 5`, `$30 == 0`
(stage 1), `$1C == 0` (not the attract demo). On the same frame `$6A` (SPRITE_LOAD_TYPE) becomes `$FF`.
**START as seen = N + 1.**

Evidence (shortest opening: Select on frame 11, Start on frame 12, nothing else; `tools/clock_start_evidence.py NesHawk`):

| frame | `$6A` | `$2C` | medal sprites in RAM $0200 (tile $0A, Y=$10) | medal sprites in PPU OAM | blue pixels in the HUD box of the screenshot | screenshot |
|---|---|---|---|---|---|---|
| 590 | 0 | 3 | 0 | 0 | 3 (background) | `shots/clock_start/NesHawk_f590.png` |
| **591 = N** | 255 | 4 | **2** | 0 | 3 | `NesHawk_f591.png` (no medals) |
| **592 = N+1** | 255 | 4 | 2 | **2** | **73** | `NesHawk_f592.png` (two blue medals, top left) |
| 593 | 255 | 4 | 2 | 2 | 73 | `NesHawk_f593.png` |
| 594 | 255 | 4 | 2 | 2 | 114 | `NesHawk_f594.png` (Bill appears, somersaulting) |

I looked at 591, 592 and 594 by eye: 591 has no medals, 592 has them. Two medals = `$32` (spare lives) = 2.
Frames 591-592 are not lag frames. Bill's own state: `$90` becomes 1 on frame 592; his sprite is first in the picture
on 594; a direction first has an effect on frame N+2 = 593 (`tools/first_effect.py`).

## END - Bill reverts to the standing pose

RAM conditions:

* **A = the first frame whose RAM has `$2C == 9`** with `$30 == 7` (stage 8). On frame A the game still used the
  controller (`$F1` still shows the held button, the pose is still aim-up / prone).
* **P = the first frame after A whose RAM has Bill standing, gun forward, on the ground:** `$BC == 0`
  (PLAYER_SPRITE_SEQUENCE), `$A0 & 15 == 0` (not jumping), `$C2 in (2, 7)` (aim forward). With Bill on the ground
  P = A + 1: that frame's logic zeroes the controller (`$F1 == 0`), `$BC` goes 1 -> 0 (Up) or 2 -> 0 (Down), the sprite
  code `$D6`/`$0300` becomes 15 and the sprite list in `$0200` changes.
* **END as seen = P + 1 = A + 2** (on the ground).

Evidence (`tools/clock_end_evidence.py dbg/s8_pre logs/dbg/mars_s8.seg.json dbg`; four variants branch 60 frames
before the heart dies):

| variant | A (`$2C` first 9) | pose in RAM changes | sprite list `$0200` changes | PPU OAM changes | Bill's pose in the picture changes | `clock.end_frame` |
|---|---|---|---|---|---|---|
| **Up held** | 3849 | 3850 (`$BC` 1->0, `$C2` 0->2, `$D6` 22->15) | 3850 | 3851 | **3851** | ram 3850, seen 3851 |
| **Down held** | 3849 | 3850 (`$BC` 2->0, `$C2` 4->2, `$D6` 23->15) | 3850 | 3851 | **3851** | ram 3850, seen 3851 |
| nothing held | 3849 | no change (already standing) | - | - | - | ram 3850, seen 3851 |
| Up held, airborne at A | 3849 | 3889 (lands: `$BC` 3->0, `$A0` 17->0) | 3889 | 3890 | 3890 | ram 3889, seen 3890 |

Screenshots checked by eye: `shots/clock_end/dbg_U_f3850.png` (gun up) -> `dbg_U_f3851.png` (standing, gun forward);
`dbg_D_f3850.png` (prone) -> `dbg_D_f3851.png` (standing). The picture box around Bill also changes on frame A itself in
every variant, including "nothing held": that is the background behind him (the heart's wall), not his pose - the PPU's
sprite tiles in his box are unchanged on A and A+1.

Other facts seen in that run: `$3B` (BOSS_DEFEATED_FLAG) became 1 on frame 3625; A came 224 frames later (the heart's
explosion sequence; `$2A` counts down to 0 just before A); `$3B` becomes `$81` on frame A+1 on the ground (after the
landing in the airborne variant); `$2D` (end-level sub-routine) 0 -> 1 on the same frame.

Limits of this evidence:
* The stage-8 state used was made with RAM pokes (`tools/mk_stage_state.py 8 0x13`: stage number and weapon written at
  the start of the game) because no full run reaches stage 8 yet. From there on only inputs were used (the heart was
  killed by a fitted TAS movie plus the movie's own last rows repeated). The end-of-level code path is the game's own.
  This must be re-checked on the first real run that reaches the heart (`python tools/clock_end_evidence.py <state> <seg>`).
* Facing left at the end ($C2 == 7) was not produced; 7 for "left, forward" is taken from the aim table order and is
  UNVERIFIED. Bill faced right in all four variants.
* Lag frames: neither event had a lag frame next to it. `clock.py` takes "seen" as the next non-lag frame after the RAM
  frame (the OAM copy does not happen on a lag frame); that rule is from the code, not from an observed case.

## Time

`time = (END_seen - START_seen) / 60.0988` seconds. Because both events have the same +1, this equals `(P - N) / 60.0988`,
and on the ground `(A + 1 - N) / 60.0988`.

A splitter that starts on `$2C` 3->4 and stops on `$2C` becoming 9 (what the community autosplitter does, per
`knowledge/ram_map.md`) measures A - N frames: **one frame less** than the picture shows. Whoever compares with the
record's video should use A + 1 - N.

## Agreement with the disassembly-based notes

`knowledge/ram_map.md` (written from the disassembly by another agent) predicted both chains and both +1 latencies as
inferences ("medals visible in the picture of frame N+1", "standing sprite displayed on frame A+2"). Both are now
observed. No disagreement.
