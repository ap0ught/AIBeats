# An AI vs Ninja Gaiden (NES): an 11:25.704 run under the human rules

This folder has an input file for Ninja Gaiden (NES, USA), Any%. It was built by an AI (Claude, working in Claude
Code). It starts at power-on and plays all six acts, 22 stages. Timed the way the speedrun.com board times runs, it
takes **11:25.704 (41,210 NES frames)**. The human record in the same category, TheRetroRunner's **11:32.183**, is
6.479 s (389 frames) slower.

It is a **tool-assisted run (TAS)**. It was built with save states and search, and it plays in an emulator (BizHawk
2.11.1, NesHawk core). It is an emulator input file, not a leaderboard submission: the board takes only runs played
live, and nobody claims this as a human record. What makes it worth comparing to the human record is that the AI
played by the human category's input rules, written down as numbers below, and not by TAS rules.

**Deliberately left out:** the game ROM (bring your own), emulator save states, per-frame captures and videos, the
record's video and crops of it, the downloaded TAS movies, third-party scripts and ROM hacks the AI read, and the
input lists of candidate runs that were not used (see "What was left out").

## Watch it on your own computer

1. Install [BizHawk 2.11.1](https://tasvideos.org/BizHawk).
2. Use your own dump of *Ninja Gaiden (USA)*. You can check it against these hashes:

   | | CRC32 | SHA-1 |
   |---|---|---|
   | whole `.nes` file (with its 16-byte iNES header) | `11F953F6` | `CA513F841D75EFEB33BB8099FB02BEEB39F6BB9C` |
   | headerless (the game data, what No-Intro lists) | `7C4A72D8` | `15F245161179AB1959B7DC20E82ADD024D23AA3D` |

   BizHawk records the whole-file SHA-1 in the movie header. If your file has a different iNES header but the same
   headerless hash, BizHawk warns that the hash differs, but the game is the same.
3. **File > Open ROM**, then **File > Movie > Play Movie** and choose `ninja_gaiden_ai_11m25s.bk2`. The movie names
   the NesHawk core, so BizHawk switches to it by itself. Leave the NesHawk settings at their defaults.

The movie is the run: every button on every frame from power-on. There is no save state and no memory write.

### Check it yourself (Windows, Python 3.9+, `pip install pillow`)

    python verify_bk2.py --bizhawk "C:\path\BizHawk-2.11.1-win-x64" --rom "C:\path\Ninja Gaiden (USA).nes"

The script starts one EmuHawk with a private copy of your config. It plays the movie hands-off through BizHawk's own
movie playback with `verify_movie.lua`, which makes no joypad calls. This takes about 4-5 minutes. Then it checks
everything listed under "How it was checked" below and prints PASS or FAIL. Our result is in
`verification/bk2_playback.json`.

## The files

| file | what |
|---|---|
| `ninja_gaiden_ai_11m25s.bk2` | the BizHawk movie (NesHawk, power-on, 41,390 frames) |
| `ninja_gaiden_ai_11m25s.inputs.txt` | the same inputs as text: a `# frames=41390` line, then 41,390 rows, one per frame, buttons joined by `+` (SHA-1 `cf703880841028f3c77383dcb3345db7cec23884`) |
| `make_bk2.py` | writes the movie from the text file and reads it back to confirm the input log equals the list |
| `verify_bk2.py`, `verify_movie.lua` | the hands-off movie check |
| `verification/` | our movie-playback result, the reference pictures, and the independent checker's report, tools and output |
| `run/` | the run's own proof: two-replay report, per-stage table, input-rule check, clock evidence and pictures |
| `harness/` | the code that built the run (see "How it was built") |

**Movie frame offset.** BizHawk emulates frame 1 before a Lua script gets control. In this project's input lists,
row k (1-based, not counting the `#` line) is the input of frame k, so row 1 is never played by the harness and is
empty. In a movie, input-log line k is also played on frame k. So the movie is the list unchanged, with no lead-in
line. (The Contra release needed one empty lead-in line because its lists started at frame 2.) BizHawk's own movie
writer, re-saving the loaded movie, produced the identical input log.

## The rules it kept (checked by `harness/check_inputs.py`)

- Controller 1 only. **Never Left+Right and never Up+Down on the same frame.** The board bans Left+Right; the NES
  rules it links ban Up+Down.
- **No turbo.** A new press of the same button at most once every 5 frames (12 a second). Every press is held at
  least 2 frames and released at least 2 frames.
- **Sustained limits.** At most **109 new presses in any 600 frames (10 s)** and **246 in any 1,800 frames (30 s)**
  for every button. The record's video has no handcam and no usable controller sound, so there is no Ninja Gaiden
  measurement (`harness/knowledge/record_mash_rate.md`). These numbers were taken from the Contra record holder's
  measured mashing.
- Down+B counts as two buttons, each against its own limit.
- Power-on start. No save state at the start, no memory writes, no deaths.

The run's numbers (`run/check_inputs.txt`):

| button | presses | most in 600 frames (cap 109) | most in 1,800 frames (cap 246) |
|---|---|---|---|
| Up | 595 | 87 | 171 |
| Down | 85 | 52 | 68 |
| Left | 353 | 39 | 54 |
| Right | 392 | 38 | 51 |
| Start | 13 | 3 | 3 |
| B | 408 | 52 | 69 |
| A | 828 | 78 | 125 |

0 Left+Right frames, 0 Up+Down frames, no press closer than 5 frames to the previous one, every hold and release at
least 2 frames. Select is never pressed. Start is pressed 3 times in the title and intro and 10 times to skip
cutscenes, as the record and the TAS do; there are no pauses. Lives never fall.

## The clock

speedrun.com, Ninja Gaiden (NES), Any% (board rule, verbatim):

> Timing starts when you gain control of Ryu.
> Timing ends when the timer reaches 000 after defeating the demon statue.

The moderators timed the record from the first video frame where Ryu is visible to the first video frame showing
TIMER-000. This run is timed at the same two on-screen events. Frames are BizHawk's frame counter. A picture of frame
f is what the console drew during frame f.

| event | in RAM | on screen |
|---|---|---|
| START: control of Ryu gained (`$33` becomes `$97` in 1-1) | 174 | **175** (174 has no Ryu, 175 shows him) |
| 6-5 tally: timer `$63` reaches 0 | 41,382 | |
| the nametable holds TIMER 000 | 41,385 | |
| END: TIMER-000 first shown | | **41,385** (41,384 still shows 001) |

**41,385 - 175 = 41,210 frames.** At the NES's 60.0988 frames a second that is **685.704 s = 11:25.704**. The 24 lag
frames inside that span (all at stage loads and cutscene skips) are timed, as they are for a human. The rows after END are an untimed tail.

The HUD redraws its timer digits on a 6-frame cycle, so TIMER-000 appears 2 to 7 frames after `$63` reaches 0,
depending on the phase. This is the same for the record (`harness/knowledge/clock.md`).

**The record's time, re-derived.** The independent checker read the timestamps from the record video's own packets.
Ryu is first visible at video frame 1,707 and TIMER-000 is first shown at 43,238; the two are exactly 692.183 s
apart, which is the board's time. The video's clock is real time to about 16 ppm (the capture drops one picture
about every 20.5 s, as a 60.0988 Hz console on a 60.000 Hz capture must). So the record took **41,599.4 +/- 2 NES
frames**. Any END seen at or before 41,774 beats it; ours is 41,385.

## Stage by stage, against the record

Segment = from the first frame showing one stage's HUD TIMER digits to the next stage's (1-1 starts at Ryu first
visible; 6-5 ends at TIMER-000). The record's segments were measured from TheRetroRunner's video by the independent
checker (video frames x 60.0988/60, +/- 2 frames each). Because of the 6-frame HUD redraw cycle, a single stage can
move by up to +/- 5 frames; the running total does not drift. Source: `run/table.md`.

| stage | ours (frames) | record | ours - record | ahead at the stage's end |
|---|---|---|---|---|
| 1-1 | 2,302 | 2,313.8 | -11.8 | +11.8 |
| 1-2 Barbarian | 834 | 841.4 | -7.4 | +19.2 |
| 2-1 | 2,820 | 2,904.8 | -84.8 | +104.0 |
| 2-2 | 3,042 | 3,101.1 | -59.1 | +163.1 |
| 2-3 Bomberhead | 821 | 833.4 | -12.4 | +175.4 |
| 3-1 | 1,604 | 1,602.6 | +1.4 | +174.1 |
| 3-2 | 2,336 | 2,327.8 | +8.2 | +165.9 |
| 3-3 Basaquer | 917 | 911.5 | +5.5 | +160.4 |
| 4-1 | 2,150 | 2,191.6 | -41.6 | +202.0 |
| 4-2 | 2,298 | 2,303.8 | -5.8 | +207.8 |
| 4-3 | 2,564 | 2,557.2 | +6.8 | +201.0 |
| 4-4 Kelbeross | 767 | 785.3 | -18.3 | +219.3 |
| 5-1 | 2,374 | 2,460.0 | -86.0 | +305.3 |
| 5-2 | 2,362 | 2,458.0 | -96.0 | +401.4 |
| 5-3 | 2,891 | 2,984.9 | -93.9 | +495.3 |
| 5-4 Bloody Malth | 805 | 805.3 | -0.3 | +495.6 |
| 6-1 | 1,574 | 1,584.6 | -10.6 | +506.2 |
| 6-2 | 3,170 | 3,153.2 | +16.8 | +489.4 |
| 6-3 | 3,003 | 2,912.8 | +90.2 | +399.2 |
| 6-4a Masked Devil | 821 | 819.3 | +1.7 | +397.5 |
| 6-4b Jaquio | 1,011 | 997.6 | +13.4 | +384.2 |
| 6-5 Demon | 744 | 749.2 | -5.2 | +389.4 |
| **total** | **41,210 = 11:25.704** | 41,599.4 = 11:32.183 | **-389.4 = -6.479 s** | |

Most of the time was won in 2-1, 2-2, 4-1 and Act 5. The record is faster in 6-2, 6-3 and 6-4b. 6-3 is the biggest
loss (1.5 s). In the worst case of the +/- 2 frame measurement the margin is 6.446 s.

The project's own ledger (`harness/knowledge/LOCKED_CHAIN.md`, "Locked stages") times each stage from RAM control
frame to control frame. Its per-stage numbers differ from the table above by up to 5 frames and end at the same
-389.4.

## How it was checked

1. **Two power-on replays** by the builders' `assemble.py --serial` on two fresh NesHawk instances. Both gave RAM
   SHA-1 `d5d58c8792b76f44d9e6892ce940ab367a19b3dd` after frame 41,390 (the last row) and identical per-frame traces
   (`run/NG_FINAL_v2.report.json`, `run/coord_NG_FINAL_v2.verify.txt`). 0 deaths, 0 game-lag frames, 22 stages in
   order.
2. **An independent checker.** A separate agent with its own replay code, its own event detection, its own input-rule
   counter and its own frame extraction from the record video. It imports nothing from the builders' harness. Its
   report is `verification/independent_check/VERIFY_REPORT.md`, and its check of the final file is
   `verification/independent_check/final/final_check.txt`.
   - Input rules: PASS, with the same per-button maxima as above.
   - RAM SHA-1 at the last row: the same `d5d58c8792b7...` as the builders' replays. Stage loads and room changes:
     identical to the builders' report.
   - The clock, read from pictures: START 175 (Ryu absent on 174, present on 175), END 41,385 (TIMER-001 on 41,384,
     TIMER-000 on 41,385), 41,210 frames, 11:25.704. The contact sheets are `final/start_sheet.png` and
     `final/end_sheet.png`.
   - It re-timed the record from its video (above) and re-measured all 22 stage events in it; all 22 matched the
     project's measurements.
   - It tested its END detector on the published TAS 4751M replayed from power-on: TIMER-000 first on frame 39,530,
     START 175, 39,355 frames = 10:54.838, the same as the project's number. The same counter flags that TAS's
     1,221 Left+Right and 3,430 Up+Down frames.
   - Verdict: BEATS the record by 6.479 s (389.4 frames, +/- 2 frames on the record's side). PROBLEMS: none.
3. **BizHawk's own movie playback of `ninja_gaiden_ai_11m25s.bk2`** (`verify_bk2.py`, result in
   `verification/bk2_playback.json`), with no input injection.
   - BizHawk loaded the movie in PLAY mode on NesHawk, from power-on, with the ROM hash in the header. It played to
     frame 41,390 and finished.
   - The RAM after frame 41,390 has SHA-1 `d5d58c8792b76f44d9e6892ce940ab367a19b3dd`, the same as all three Lua-fed
     replays above.
   - For every frame 2 to 41,390, the lag flag, the 20 RAM bytes the independent checker logged and the three HUD
     timer tiles are identical to the checker's log (SHA-1 `3d6654fd0fa9e790bff3a9b18131d272914825bd` both ways;
     the log is `verification/independent_check/final/frames.csv`). So the movie reproduces every frame.
   - The per-frame lag flag and full RAM of frames 2 to 41,390 have SHA-1
     `0d5f77e24252417616d5bbf794b188802bc542d1` (for anyone re-running the check).
   - Control in RAM on 174, `$63` = 0 on 41,382, TIMER 000 in the nametable on 41,385. No life lost.
   - The pictures of frames 174, 175, 41,384 and 41,385 are pixel-identical to the independent checker's pictures in
     `verification/pictures/`. Ryu appears on 175; the timer reads 000 on 41,385 and not on 41,384.
   - BizHawk's movie writer, re-saving the loaded movie, wrote the identical input log.

### What this claim must carry (caveats)

1. **Tool-assisted and emulator-only.** It ran on BizHawk 2.11.1 NesHawk and is not eligible for speedrun.com. The
   6.479 s margin is emulated time (NES frames / 60.0988), compared with the record's real-time video timing under
   the board's rule.
2. **One core only.** It was played and checked on NesHawk only. It has not been played on a console. (NesHawk
   reproduces the console's DPCM controller-read conflict; two places in 5-3 needed repairs for it.)
3. **"No turbo" is our numeric rule** (above). The board bans turbo but gives no number.
4. The route came from the published TAS (below). Search and save states give frame-perfect play that no human could
   repeat; the rules limit what buttons can do, not how precisely they are timed.

## Can it beat the best TAS? No.

No, and it isn't trying to. The best Ninja Gaiden TAS is **10:50.33** by **eien86 & Scumtron**
([tasvideos.org/4751M](https://tasvideos.org/4751M)). Timed the leaderboard's way (Ryu visible to TIMER-000, the same
events as above) it is **10:54.838**, 30.9 seconds faster than this run. It gets there with inputs humans aren't
allowed: **Left+Right on 1,221 frames, Up+Down on 3,430 frames**, and up to 30 presses a second (it slash-cancels with
Down+B every 2 frames, and most of its Up+Down comes from an Up+Down+Left wall trick). This run plays by human rules,
so the human record is the one it races.

This run was built from that TAS's route. The AI started from the TAS's path through every stage. Where the TAS's
own button presses were already legal, or could be made legal by `harness/ng/legal.py` (removing Left+Right and
Up+Down, and spreading presses out to the press-rate limits), the solvers reused them; everywhere else, and wherever
the game's enemy timing drifted from the TAS's, the AI's own searches found new inputs. Every row of the final file
passes the rules above. No TAS movie file is included here.

## How it was built

`harness/` is a copy of the code and notes that made this run (`harness/SNAPSHOT.md` lists every file's SHA-1). It
holds:

- `bridge.lua` and `ng/emulator.py`: drive EmuHawk over a socket. `ng/fastcore.py` + `ng/fastcore.lua`: a faster
  search loop inside EmuHawk.
- `ng/legal.py`: the legalizer (turns a list into one that passes the rules, or reports why it can't).
- `ng/solve/`: the search tools (beam, A*, boss fights, hitbox model, lantern and ninpo planner, comparisons with the
  record).
- `ng/stages/` and `work/<round>/`: the scripts of every stage round. The run was built **one stage at a time from
  power-on, in order**. Two agents worked each stage with different approaches; the better result that met the
  record's split (or the best that could be found) was locked and never changed again, because any frame change
  shifts the game's global timer `$BF` and every later enemy. `work/l11r` ... `work/l65` are the locked-chain
  rounds; `a12*`, `a34*`, `a56*`, `tk`, `c5`, `r*`, `w21` are earlier act-level solvers and experiments.
- `assemble.py`: the two-replay proof. `check_inputs.py`: the rules. `tools/`: probes, clock evidence, RAM checks.
- `knowledge/`: what the AI found and wrote down: the locked-chain ledger (`LOCKED_CHAIN.md`), RAM map, clock proof,
  game mechanics, ninpo budget, the record's route and events per act, the legal versions of the TAS's tricks, and
  the TAS notes.

To replay it, put `BizHawk-2.11.1-win-x64/` next to `harness/` (in this folder) and your ROM as
`harness/Ninja Gaiden (USA).nes`, then (Python 3.9+, `pip install -r requirements.txt`):

    cd harness
    python assemble.py final ../ninja_gaiden_ai_11m25s.inputs.txt --serial
    python check_inputs.py ../ninja_gaiden_ai_11m25s.inputs.txt --period 5 --hold 2 --release 2 --windows 600:109,1800:246

The stage scripts search with real emulator timing and read save states and candidate lists that are not included,
so re-running a round is not guaranteed to give the same rows. Every result was checked by the same replays.

## What was left out

- The ROM, and a modified ROM and third-party hitbox-viewer Lua scripts the AI read (their logic is ported in
  `harness/ng/solve/hitbox.py`).
- The downloaded TAS movies, the record's video, and the checker's crops of it (`vid/`). The checker's numeric
  measurements of the video are in `verification/independent_check/vid_measurements/`.
- Emulator save states, per-frame captures, screenshots other than the clock pictures, the input lists of candidate
  runs, the Python virtual environment and caches, and `.backup` copies of edited files.
- The video-production code.

## Thank you

- TheRetroRunner, for the 11:32.183 world record to chase
  ([speedrun.com/ngnes/runs/z5pwrgdm](https://www.speedrun.com/ngnes/runs/z5pwrgdm)), and everyone who has pushed the
  Ninja Gaiden leaderboard down over the years.
- eien86 & Scumtron, for the TAS whose route this run was built from, and the other TASVideos Ninja Gaiden authors.
- 0xe1f, for the Ninja Gaiden disassembly (github.com/0xe1f/NinjaGaidenNES); BroDMax, for the autosplitter whose
  start and end conditions the clock follows (github.com/BroDMax/NinjaGaiden-NES-autosplitter); the authors of the
  community hitbox-viewer scripts and maps on the board's resources page.
- The BizHawk team.

Ninja Gaiden © 1988 Tecmo.
