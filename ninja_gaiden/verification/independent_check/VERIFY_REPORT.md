# Independent verification: Ninja Gaiden (NES) Any% vs TheRetroRunner 11:32.183

Verifier: a separate agent, 2026-10-28. All code is in `work/verify/`. It imports nothing from `ng/`, `tools/`,
`assemble.py`, `check_inputs.py` or `yt/`. It has its own Lua replay, its own RAM/picture event detection, its own
input-rule counter and its own frame extraction from the record video. The record video was used for timing only.
No frame of it was copied anywhere near `yt/`.

## PROBLEMS FOUND (read first)

**No blocking problem.** The rule, the record's timing, our START/END events and the input rules all check out on
the locked part, rows 1-35,799. The final time does not exist yet. These are the small issues, in order of importance:

1. **Wording risk, not timing.** `yt/DESCRIPTION_DRAFT.md` line 26 says "An AI beat the Ninja Gaiden (NES) world
   record". The run is an emulator input file, and the board bans movie files, so it can never sit on the board.
   The defensible claim is "faster than the human world record under the board's own rules, timed by the same
   on-screen events". Our time is NES frames / 60.0988. The record is the moderators' real-time video timing.
2. **Stale header in the locked file.** `logs/l62_LOCKED_v2_to63_poweron.inputs.txt` says `# frames=35799` but holds
   **35,798** rows. Row 35,799 (Right, the 6-3 control row) is only in `logs/l62_v2.inputs.txt`. Readers that skip
   `#` lines are unaffected. Do not trust the header count.
3. **Two numbering conventions for "control", one frame apart from 5-3 on.** `LOCKED_CHAIN.md` says 5-3 control
   27,360 and 6-2 control 32,632; the assemble report and the yt capture say 27,361 and 32,633. The loads agree
   everywhere. This is split bookkeeping only. It cannot change the final START->END time.
4. **The project's per-stage "vs record" numbers are approximate.** They compare our RAM control frame with the
   record's "control est" (timer digits - 6 video frames). Timed instead by the same on-screen event on both sides
   (the HUD TIMER digits first drawn in each stage), each stage moves by up to +/-5 f, because the HUD redraws its
   digits on a 6-frame cycle. Cumulative at 6-3: **-489.4 f (verifier) vs -491.4 f (project)**. There is no sign
   error and no drift.
5. **The yt capture's SHA check said "MISMATCH" for `l61lock`.** The cause is a definition mismatch, not a desync.
   The expected SHA came from `logs/l62_r40f.report.json` (34,924 rows), but the capture checked RAM at row
   32,631. For the final render, pass `--expect-sha` a report of the SAME file and row count. Otherwise the check
   means nothing.

## 1. The rules and the record

* **Board rule, verbatim** (`dl/api/v2game.json`, `knowledge/rules_verbatim.md`): "Timing starts when you gain
  control of Ryu." / "Timing ends when the timer reaches 000 after defeating the demon statue." The timing method
  is `realtime` only, with milliseconds shown. Any% (`ndx8vvkq`) has no extra rules. Banned: Left+Right and turbo;
  the linked NES doc also bans Up+Down, savestates, RAM watch and movie files.
* **The record:** `dl/api/run.json` gives `z5pwrgdm`, TheRetroRunner, `realtime_t` 692.183, NES console (not
  emulated), verified 2023-08-05. `lb.json` puts it at #1, ahead of 693.933.
* **How it was timed (re-derived):** I took the timestamps from the video's own packets (`pkt.csv`, 90 kHz
  timebase) and labelled each decoded frame by its own pts (ffmpeg showinfo, `-copyts`, `-fps_mode passthrough`).
  * Ryu is first visible at video frame **1707** (frame 1706 has no Ryu; contact sheet `vid/sheet_start.png`).
  * TIMER-000 is first shown at **43238** (TIMER-001 is shown 43232-43237; sheet `vid/sheet_end.png`).
  * pts(43238) - pts(1707) = **692.183 s exactly**. The moderators timed from first-visible Ryu to first-shown
    TIMER-000. LiveSplit reads 11:32.36 on that frame, so the board time is a retime, not the runner's timer.
* **Video format:** the container is CFR 60.000 fps (pts steps of 16/17 ms; |pts - n/60| <= 1 ms). The content is
  30 distinct images per second, each one NES frame, 2 NES frames apart (the scroll moves exactly 3 px per image
  when running at 1.5 px/f).
* **Is the video clock real time? Yes, within about 16 ppm.**
  * About every 20.5 s the capture drops one whole image. The scroll then jumps 6 px (4 NES frames) in one
    image step. I saw this at video frames 3343, 11935, 19279 and 20527.
  * The period is 1,227 +/- 2 video frames (12.99, 14.00 and 7.00 periods apart). That is the 0.0988 Hz surplus of
    a 60.098 Hz console sampled on a 60.000 Hz clock: 2 NES frames per 20.46 s, so the console ran at 60.0978 Hz
    in video time.
  * An NES-locked capture would never drop. So the record took 692.183 s of real time, which is
    **41,599.4 +/- 2 NES frames**.
* **Record error bars, +/-2 NES frames (+/-0.033 s):**
  * each end can fall on the missing NES frame between two images (0..-1 f per end);
  * pts rounding is <= 1 ms;
  * the 16 ppm clock ratio is worth about 0.7 f over the run.
  * The official number itself is fixed at 692.183.
* **Our START/END detection matches the rule.** The project and I use the same events on our side:
  * START seen = first picture with Ryu (row 175; RAM control `$33=$97` is row 174).
  * END seen = first picture showing TIMER-000.
  * time = (END seen - START seen) / 60.0988.
* **Leaderboard convention:** real time in seconds with ms. Our side converts NES frames with 60.0988 fps, the NTSC
  NES rate: 21.477272 MHz / 4 / 89,341.5 dots per frame. The yt pipeline renders at 150247/2500 = 60.0988 fps, so
  a frame-stepping viewer of our video gets the same seconds.
* **Record line:** 175 + 41,599.4 means **END seen <= 41,774** gives <= 692.177 s, which beats the record.
  41,775 gives 692.194 s, which loses. This confirms the project's "END seen <= 41,774".

### Stage transitions in the record, re-measured

For each stage I found the first video frame where the HUD TIMER digits are drawn. All **22 of 22** agree exactly
with `knowledge/record_events.json` (`record_stage_events.json`). I checked 8 by eye in
`vid/sheet_stage_digits.png`: 2-1, 3-3, 4-3, 5-3, 6-2, 6-3, 6-4b and 6-5. The playfield "first picture" is a fade-in,
so its frame depends on the threshold (2-10 frames off in 7 stages). I do not use it.

Calibration: the 1-1 digits appear **4 frames after Ryu** in both runs (record 1707 -> 1711; ours 175 -> 179). There
is no constant picture offset between the two.

## 2. Our run, independently (locked part)

Replay: `vreplay.py` + `vreplay.lua`.
* It does a fresh power-on launch of BizHawk 2.11.1 NesHawk with a private config: rewind off, NES core =
  NesHawk, OpposingDirPolicy 2. Opposing directions do not appear in a legal file, and the rule counter checks for
  them.
* The core was confirmed by its memory domains; the ROM sha1 is CA513F84...
* Row 1 is the launch frame, so play starts with row 2. Row k = emulator framecount k, which is the .bk2 numbering
  the project uses.
* Per frame it logs RAM, the PPU-bus timer digits and the palette/OAM, plus screenshots around the events.

**`logs/l62_v2.inputs.txt` (35,799 rows = the locked rows 1-35,798 + the 6-3 control row), result
`run/lock63/final_check.txt`:**
* Input rules (my own counter `vrules.py`): **PASS**.
  * 0 L+R, 0 U+D, no press closer than 5 f, every hold and release >= 2.
  * Worst windows: Up 87/600 f, 171/1,800 f; A 78/600 f, 125/1,800 f (caps 109 and 246).
  * The same verdict as `check_inputs.py`.
* RAM sha1 after row 35,799: **6ada68899a66**, identical to the project's two replays.
* All 18 stage loads and all 41 room changes are identical to `logs/l62_v2.report.json` and the yt capture.
* 0 deaths. 26 BizHawk lag frames, all at loads.
* START: RAM 174, **Ryu first in the picture 175** (screenshots `run/test400_start_sheet.png`). 1-1 digits are in
  the picture and in the nametable on the same row, 179.

Same-event comparison with the record (event = TIMER digits first drawn; NES frames after Ryu first visible; the
record's video frames x 60.0988/60):

| stage | ours cum | record cum | cum diff | stage split diff | project's split |
|---|---|---|---|---|---|
| 1-1 | 4 | 4.0 | 0.0 | -11.8 | -9.8 |
| 1-2 | 2302 | 2313.8 | -11.8 | -7.4 | -7.4 |
| 2-1 | 3136 | 3155.2 | -19.2 | -84.8 | -82.8 |
| 2-2 | 5956 | 6060.0 | -104.0 | -59.1 | -64.1 |
| 2-3 | 8998 | 9161.1 | -163.1 | -12.4 | -7.3 |
| 3-1 | 9819 | 9994.4 | -175.4 | +1.4 | -0.7 |
| 3-2 | 11423 | 11597.1 | -174.1 | +8.2 | +7.2 |
| 3-3 | 13759 | 13924.9 | -165.9 | +5.5 | +6.5 |
| 4-1 | 14676 | 14836.4 | -160.4 | -41.6 | -41.6 |
| 4-2 | 16826 | 17028.0 | -202.0 | -5.8 | -4.8 |
| 4-3 | 19124 | 19331.8 | -207.8 | +6.8 | +3.8 |
| 4-4 | 21688 | 21889.0 | -201.0 | -18.3 | -13.3 |
| 5-1 | 22455 | 22674.3 | -219.3 | -86.0 | -91.0 |
| 5-2 | 24829 | 25134.3 | -305.3 | -96.0 | -96.0 |
| 5-3 | 27191 | 27592.4 | -401.4 | -93.9 | -93.0 |
| 5-4 | 30082 | 30577.3 | -495.3 | -0.3 | -0.3 |
| 6-1 | 30887 | 31382.6 | -495.6 | -10.6 | -9.6 |
| 6-2 | 32461 | 32967.2 | -506.2 | +16.8 | +13.8 |
| **6-3** | **35631** | **36120.4** | **-489.4** | (open) | cum -491.4 |

**At 6-3 we are 489.4 +/- 2 NES frames (8.14 s) ahead of the record by the same on-screen event.** The project
says 491.4. The 2 f difference is the HUD redraw phase; the cumulative numbers agree.

### END detection tested on a finished run (TAS 4751M)

`run/tas4751/final_check.txt` replays the published TAS from power-on.
* My picture detector finds TIMER-001 on rows 39,524-39,529 and **TIMER-000 first on 39,530**; the nametable shows
  the same row (`run/tas4751/end_sheet.png`).
* RAM `$63`=0 is on row 39,525. START 175.
* That gives 39,355 frames = **10:54.838**, identical to the project's `tas4751_full.report.json`.
* By the same-event table, the TAS is -2,244.4 f vs the record (record_notes, by RAM: +2,248).
* (The TAS of course FAILS the input rules: 1,221 L+R rows and 3,430 U+D rows. That proves the counter catches
  them.)

## 3. Final check: run this when the final file exists (under an hour, normally ~10 min)

    cd "G:\AI World Record\Ninja Gaiden"
    python assemble.py <final> <final inputs> --serial          # the project's own report (optional, for the cross-check)
    python work/verify/final_check.py logs/<final>.inputs.txt --report logs/<final>.report.json --name final

* It waits for >= 2.5 GB free RAM, runs one NesHawk (~6 min for 42,000 frames) and analyses the run.
* It prints:
  * the input rules PASS/FAIL, with the per-button maxima;
  * deaths;
  * START (RAM / picture) and END (RAM / nametable / picture);
  * **our time**, the **margin vs 11:32.183** in seconds and NES frames with +/-2 f error bars, and a verdict
    (BEATS / TIES / SLOWER);
  * the stage-by-stage same-event table down to END;
  * the differences from the project's report (stage loads, START/END seen, RAM sha1 when the row counts match);
  * a PROBLEMS line.
* Output: `work/verify/run/final/final_check.txt`, `.json`, `start_sheet.png`, `end_sheet.png`. **Open both sheets
  and look**: Ryu absent then present at START, TIMER-001 then TIMER-000 at END.
* `--reuse` re-analyses without replaying. `--tail N` sets the idle frames after the last row (default 1500; the
  demon kill to TIMER-000 is ~450).
* Accept the claim only if all of these hold:
  * the rules PASS;
  * PROBLEMS is "none";
  * the verdict is BEATS;
  * END seen <= 41,774;
  * the two sheets look right;
  * the project's END seen equals ours.

## Files

* `vid.py`: pts-labelled frame extraction.
* `vstages.py`: the record's per-stage digit events, written to `record_stage_events.json`.
* `vdrift.py` / `vcadence.py`: the scroll and cadence analysis of the record video.
* `vrules.py`: the input rules.
* `vreplay.py` + `vreplay.lua`: the replay.
* `vanalyze.py`: the events and the clock.
* `final_check.py`: the driver.
* `run/<name>/`: replay outputs.
* `vid/`: crops of the record used for timing (timing only; never for the video).
