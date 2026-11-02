# Ninja Gaiden (NES) Any% record: frame timing notes

**Run:** TheRetroRunner, 11:32.183 (692.183 s), speedrun.com run `z5pwrgdm` (https://www.speedrun.com/ngnes/runs/z5pwrgdm).
- Platform and region on the board: NES console, not emulated, USA / NTSC.
- Video: Twitch VOD https://www.twitch.tv/videos/1890225973 (the board links it as `twitch.tv/theretrorunner/v/1890225973`), titled "Ninja Gaiden Any% WR in 11:32.183".
- Dates: the VOD was created 2023-08-04 21:18 UTC. The run's date on the board is 2023-08-05, and it was verified 2023-08-05.
- I downloaded the source quality (1080p60, 536 MB) with yt-dlp to `dl/record_video/v1890225973.mp4` and measured it on 2026-10-19.

Machine-readable numbers are in `record_events.json`. The scripts and intermediates are in `work/vid/` and `tools_research/`.

All frame numbers below are **video** frame indices: frame n is shown at video time n/60 s.

## Headline

| | video frame | video time |
|---|---|---|
| START: Ryu first visible in 1-1 | 1707 | 28.450 s |
| END: HUD first shows TIMER-000 after the demon | 43238 | 720.633 s |
| Span | 41531 frames | 692.1833 s |
| Claimed | 41531 frames at 60 fps | 692.183 s |

**The span matches the board time to the frame.** The moderators timed from the first video frame where Ryu is visible to the first video frame showing TIMER-000, counting at 60 fps.

In NES frames (60.0988 fps): 692.1833 x 60.0988 = **41,599 +/- 2**.

## 1. What the video contains

- **Container: constant 60.000 fps.**
  - The packet timestamps step 1530 or 1440 ticks of 1/90000 s (1/60 s rounded to the millisecond).
  - 86,340 frames over 1,439.0 s.
  - A frame-accurate seek (`-ss (n-0.5)/60`) reproduced the sequential decode exactly at frames 3980, 15000, 30001 and 43230 (mean difference 0.00).
- **Content: 30 distinct images a second, each of them one whole NES frame.**
  - There is no interlace comb: adjacent lines align at a horizontal shift of 0.
  - Each image is held for 2 video frames.
  - The NES frame between two images is missing. Between consecutive images, a running scroll moves 3 NES pixels, which is two frames at 1.5 px per frame.
  - So the video can place an event only to the nearest 2 NES frames.
  - The pairing phase drifts: pairs start on odd frames at 3600 and on even frames at 43238.
- **Tolerance:** +/-1 video frame at START and at END. The true NES event can fall on a missing frame, up to 1 NES frame before the first frame that shows it. The two ends have the same bias, so most of it cancels.
- **Layout:**
  - The game sits at about x 600-1800, y 140-1040 of the 1920x1080 frame.
  - Twitch chat lines are drawn over the top of the HUD.
  - LiveSplit is at the upper left (attempt counter 1516/31808, final split "Demon n Done").
  - The webcam shows the runner's face, not his hands.
- **The VOD starts in the middle of the previous attempt** (2-1, LiveSplit at 1:10). That attempt is reset at about 21 s (a blue screen), the TECMO PRESENTS 1989 screen follows at about 22-26 s, and the record attempt begins. The reset is in the video, as the rules require.

## 2. START (rule: "Timing starts when you gain control of Ryu")

- Black 1314-1602, after the TECMO screen. The runner presses Start on the TECMO screen, which goes straight to 1-1.
- The 1-1 picture first appears at 1603 and finishes fading in at about 1699.
- Ryu is absent at 1706 and **first visible at 1707**, at the left edge (pair 1707-1708).
- The HUD timer digits stay blank until **1711**, where they appear already reading 149.
- **RAM equivalent:** see `ram_map.md` and `project_rules.md`. In the published TAS replayed in BizHawk:
  - Frame 174 is the first frame with `$33 == 0x97` (this is the LiveSplit autosplitter's start condition).
  - On that frame `$63` (seconds) drops to 149 and `$62` (sub-timer) begins counting down.
  - Ryu moves on frame 175.
  - TASVideos says Ryu is "typically 2 frames before he appears on screen" playable.
  - So the moderators' START is about RAM frame N+2 to N+3, where N is the first `$33 == 0x97` frame.
  - **This picture-to-RAM offset is not yet measured in our emulator**; the harness should screenshot it.

## 3. END (rule: "Timing ends when the timer reaches 000 after defeating the demon statue")

- 6-5: the demon's ENEMY bar is empty from **42806**, with the HUD timer at 145.
- The timer then tallies into the score at 3 frames per second of timer. In the video the display goes 013, 011, 009 and so on, showing **only odd values, each for 6 video frames**.
  - So the HUD timer digits seem to be redrawn every 6 frames, or the capture's missing frames line up with the even values.
  - In RAM (TAS replay) `$63` drops by 1 every 3 frames, with no skipped values.
  - **The harness should check on screen when TIMER-000 is first drawn, relative to the first frame with `$63 == 0`.**
- TIMER-001 is shown 43232-43237. **TIMER-000 is first shown at 43238.**
- The screen goes black at 43264 and the ending cutscene follows. The run has no deaths: lives P-02 throughout.

## 4. Span against the claim

43238 - 1707 = 41531 frames = 692.18333 s. The claim is 692.183 s, so the difference is 0 frames.

## 5. Stages and bosses

- "Control (est.)" is the frame the HUD timer digits first appear, minus 6. This was calibrated in 1-1, where Ryu is visible at 1707 and the timer appears at 1711, so control is at about 1705. +/-3 frames.
- "Boss bar empty" is the first frame the ENEMY bar shows no pink. In the TAS replay, the matching RAM event is `$66 == 0` (TASVideos uses it as the act split).
- Each bar drains in steps from the hits, so the kill is a few frames before the bar is empty. `$66` is a display counter.
- Cumulative times run from START (1707).

| Stage | Black before | First picture | Timer digits shown | Boss bar empty (cum s) | HUD timer at bar-empty | Weapon / ninpo shortly after the stage starts |
|---|---|---|---|---|---|---|
| 1-1 | 1314-1602 | 1603 | 1711 | | | none / 00 |
| 1-2 Barbarian | 3791-3910 | 3911 | 4017 | 4109 (40.03) | 148 | Windmill / 10 |
| 2-1 | 4649-4746 | 4747 | 4857 | | | none / 00 |
| 2-2 | 7533-7650 | 7651 | 7757 | | | orange icon (Fire Wheel or Jump&Slash) / 15 |
| 2-3 Bomberhead | 10649-10744 | 10745 | 10853 | 10933 (153.77) | 149 | Windmill / 05 |
| 3-1 | 11445-11570 | 11571 | 11685 | | | none / 00 |
| 3-2 | 13087-13168 | 13169 | 13285 | | | orange / 17 |
| 3-3 Basaquer | 15415-15526 | 15527 | 15609 | 15769 (234.37) | 147 | orange (Fire Wheel) / 17, then 01 at the kill |
| 4-1 | 16241-16410 | 16411 | 16519 | | | none / 00 |
| 4-2 | 18543-18630 | 18631 | 18707 | | | Windmill / 00 |
| 4-3 | 20772-20898 | 20899 | 21007 | | | Windmill / 10 |
| 4-4 Kelbeross | 23336-23481 | 23482 | 23560 | 23588 (364.68) | 150 | Windmill / 00 |
| 5-1 | 24072-24227 | 24228 | 24344 | | | none / 00 |
| 5-2 | 26596-26693 | 26694 | 26800 | | | orange / 45 |
| 5-3 | 29056-29169 | 29170 | 29254 | | | Windmill / 55 |
| 5-4 Bloody Malth | 32076-32127 | 32128 | 32234 | 32292 (509.75) | 149 | Windmill / 05 |
| 6-1 | 32804-32931 | 32932 | 33038 | | | none / 00 |
| 6-2 | 34394-34510 | 34511 | 34620 | | | orange / 35 |
| 6-3 | 37538-37657 | 37658 | 37768 | | | Windmill / 10 |
| 6-4a Masked Devil | 40512-40567 | 40568 | 40676 | 40744 (650.62) | 148 | Windmill / 05 |
| 6-4b Jaquio | 41256-41387 | 41388 | 41494 | 41756 (667.48) | 146 | none / 00 |
| 6-5 Demon | 42256-42441 | 42442 | 42490 | 42806 (684.98) | 145 | none / 00 |
| END TIMER-000 | | | | 43238 (692.18) | 000 | |

Notes on the table:
- **CORRECTION 2026-10-24:** the purple swirl is **Jump & Slash**, not the Windmill. The orange diagonal icon is the **Windmill**, and the orange round flame is the Fire Wheel. These were calibrated on NesHawk screenshots (`shots/nb_icon_*.png`). A corrected per-stage art/ninpo table is in `ninpo_budget.md` section 2/6.
- The weapon icons are read from 400 px-wide HUD thumbnails. Purple swirl = Windmill Star; the orange icon is the Art of the Fire Wheel or Jump & Slash, which I could not tell apart at that size. Treat the weapon column as approximate.
- The in-stage rooms (22-frame black transitions) are listed in `record_events.json` (`rooms_in_stage`). There are 26 of them: 2-1b-d, 2-2b-c, 4-1b-c, 4-3b-d, 5-2b-d, 5-3b-g, 6-2b-e and 6-3b-d.
- The runner's comment: "Without the missed manip, maybe a low 31 or high 30." The "manip" is the RTA 5-1 manipulation (see `game_mechanics.md`). He also says he "should have missed the plate kill, missing 2 slashes": the Jaquio plate kill, the fastest human Jaquio strategy.

## 6. Against the published TAS, stage by stage

TAS = TASVideos 4751M, replayed in BizHawk 2.11.1 NesHawk (`work/tasrun/tas4751_ram.csv`).
- TAS stage starts are its first timer-running frame. They equal the "Initial" column of the TAS submission table exactly.
- Record stage starts are the "Control (est.)" frames, converted to NES frames.
- The last row runs to TIMER-000 on both sides.

| Stage | Record cum (s) | TAS cum (s) | Record behind (s) | Record stage (s) | TAS stage (s) | Diff (NES f) |
|---|---|---|---|---|---|---|
| 1-1 | 0.00 | 0.00 | 0.00 | 38.43 | 38.17 | +16 |
| 1-2 | 38.43 | 38.17 | 0.26 | 14.00 | 13.88 | +7 |
| 2-1 | 52.43 | 52.05 | 0.39 | 48.33 | 46.62 | +103 |
| 2-2 | 100.77 | 98.67 | 2.10 | 51.60 | 48.17 | +206 |
| 2-3 | 152.37 | 146.84 | 5.53 | 13.87 | 13.81 | +3 |
| 3-1 | 166.23 | 160.65 | 5.58 | 26.67 | 26.71 | -2 |
| 3-2 | 192.90 | 187.36 | 5.54 | 38.73 | 38.39 | +21 |
| 3-3 | 231.63 | 225.74 | 5.89 | 15.17 | 13.78 | +83 |
| 4-1 | 246.80 | 239.52 | 7.28 | 36.47 | 35.16 | +79 |
| 4-2 | 283.27 | 274.68 | 8.59 | 38.33 | 37.90 | +26 |
| 4-3 | 321.60 | 312.59 | 9.01 | 42.55 | 39.83 | +163 |
| 4-4 | 364.15 | 352.42 | 11.73 | 13.07 | 12.83 | +14 |
| 5-1 | 377.22 | 365.25 | 11.97 | 40.93 | 38.32 | +157 |
| 5-2 | 418.15 | 403.57 | 14.58 | 40.90 | 36.29 | +277 |
| 5-3 | 459.05 | 439.86 | 19.19 | 49.67 | 44.11 | +334 |
| 5-4 | 508.72 | 483.97 | 24.75 | 13.40 | 13.36 | +2 |
| 6-1 | 522.12 | 497.33 | 24.79 | 26.37 | 26.22 | +9 |
| 6-2 | 548.48 | 523.55 | 24.93 | 52.47 | 48.64 | +230 |
| 6-3 | 600.95 | 572.19 | 28.76 | 48.47 | 45.19 | +197 |
| 6-4a | 649.42 | 617.38 | 32.03 | 13.63 | 13.46 | +10 |
| 6-4b | 663.05 | 630.84 | 32.21 | 16.60 | 14.08 | +152 |
| 6-5 to 000 | 679.65 | 644.92 | 34.73 | 12.57 | 9.87 | +162 |
| **Total** | **692.18** | **654.76** | **37.43** | | | **+2,248** |

How to read this:
- Each stage time includes the end-of-stage transition, and for a boss stage also the timer tally, the cutscene skip and the load.
- The record is within a few frames of the TAS on the bosses (1-2, 2-3, 4-4, 5-4, 6-4a) and on 3-1 and 6-1.
- Its losses are in the wall-climbing stages: 2-1, 2-2, 4-3, 5-1, 5-2, 5-3, 6-2 and 6-3 together account for about 1,670 of the 2,248 frames. Those stages are where the TAS uses L+R and U+D+L (banned for us) and frame-perfect damage boosts.
- The other big losses are Jaquio (+152) and the demon (+162).

## 7. Calibration facts for a harness (all from the TAS replay; to be confirmed)

- Room load: from `$6D` changing (the new stage) to the timer starting is exactly 151 frames at every stage start.
- In-stage room transition: 22-23 frames of black. The video shows 22-frame black segments; the TAS table has 22-23 frames between "exit" and "Initial".
- Tally: 3 frames per remaining timer second. In both the record and the TAS, the tally starts while the ENEMY bar is still draining.
- 6-5: kill to TIMER-000 took 432 video frames in the record (timer 144-145 at the kill) and 441 frames in the TAS (timer 147). **A faster demon kill leaves more timer, and each extra timer second costs 3 frames of tally. Net: one second (61 frames) faster at the demon saves about 58 frames.**
