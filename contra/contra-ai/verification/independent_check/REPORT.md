# Independent check of chain2/run_chain2.inputs.txt (2026-10-16)

Saved by the coordinating agent from the verifier's final message (the verifier could not write files outside its
tools). Tools and evidence are in this folder (adapted from verify1, read before use; no builder code run; builders'
files opened only after the verifier's numbers existed).

## Verdicts
| # | Item | Verdict |
|---|---|---|
| 1 | Reproduction, ROM, controller 1 only, clean replay path | Confirmed on BizHawk 2.11.1 NesHawk (three processes identical). FAILS on quickerNES (game over in stage 1) |
| 2 | Clock from pictures | Confirmed: START 594, END 34509, 33,915 frames = 564.321 s = 9:24.321 (9:25.250 at 60.000) |
| 3 | Faster than 9:48.183 like for like | Confirmed: 23.862 s (1,434 frames); worst case 22.88 s. vs 9:46.717: 22.40 s, worst case 21.42 s |
| 4 | Rule v2, 1 player, no deaths, no Konami code, eight stages, no glitch seen | Confirmed, with caveats |
| 5 | Same result on a real console | Could not determine (emulator-only) |

No difference of substance from the builders' numbers.

## Key evidence
- Input file SHA-1 f807a473119482b44191885f7a9df59a2280b70e (34,567 rows). ROM whole-file SHA-1 c9ea66bb..., CRC32
  C50A8304; headerless CRC32 F6035030, SHA-1 979494e7869ac7ab4815fdbd1dc99f893f713fbf.
- Two processes: per-frame trace SHA-1 e25d14dbe6be95eefd5203de21bfc388fa18b783 both; RAM SHA-1 at frame 34568
  2242cdd88af3f06e8ed6a43de637fc42cb50d619 both (= builders'); all 35,167 PNGs byte-identical.
- START 594: 0 medal-blue pixels on frames 2..593, 70 on 594. END 34509: prone box 34394..34508, standing from 34509
  (gun forward, facing left); Down alone held 34393..34510. Experiment C (Down held to 34700): stands on 34509 anyway,
  so the stop is the game's automatic revert. Experiment D (Down released at 34480): stands on 34481, i.e. the run
  gains nothing by its choice. Heart flag 34283; `$2C` 8 -> 9 at 34507.
- 142 lag frames inside the span; 58 idle rows after the last input are untimed.
- Rules: PASS. B 1,078 presses, max 12/60, 70/600, 144/1,800; longest unbroken 5-frame run 41 presses (3.4 s); 28 of
  564 seconds at 11-12. Six 5-frame pauses (stage 6: 24223, 24255, 24767; stage 7: 28078, 29808, 29872); `$1A` and
  `$34` keep moving during pauses. Lives 2 -> 8, never fall; no death flag; no Konami code; S at 2021, S+Rapid from
  3460; Barrier in stage 7 and stage 8; eight stages in order; 35 ignored-pad frames; 283 sampled pictures, no glitch
  seen (sample only); Bill undrawn 29 frames (34351-34379) during the heart's explosions.

## Caveats a public claim must carry
1. Tool-assisted, emulator-only (BizHawk 2.11.1 NesHawk), not eligible for speedrun.com: under the board's timing
   rule the emulated time is 23.86 s under the fastest board run (22.88 s worst case).
2. One core only (desyncs on quickerNES); no console, second accurate emulator or .bk2 check yet; 142 lag frames timed.
3. "No turbo" is our numeric rule (one press per 5 frames, 2-frame holds, max 109 per 600 and 246 per 1,800 frames).
4. Six 5-frame pauses shift timing and randomness: allowed by our rules, not humanly reproducible at that precision.
5. Quote both conversions (9:24.321 at 60.0988, 9:25.250 at 60.000) and the headerless CRC/SHA-1.
6. Bill ends facing left; experiment C shows facing does not move the stop frame.
7. The description must answer the TAS question with real Contra TAS numbers.

## Differences from the builders
- Builders report START 593 / END 34508 in RAM and 594 / 34509 seen; same span.
- Lag 159 (BizHawk counter incl. frame 1) vs 158 from frame 2; both 142 in the span.
- Small evidence flaw: `chain2/clock_evidence.json` reports 3 "blue_pixels_in_hud_box" on frames 590-593 (starfield
  pixels in its box); does not move START, but fix or explain before publishing that evidence.
