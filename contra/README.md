# An AI vs Contra (NES): a 9:24.321 run under the human "No Turbo" rules

**The video:** [An AI Beat Contra's World Record by 24 Seconds](https://www.youtube.com/watch?v=OaePvbX8jqw)

This folder has an input file for Contra (NES, USA), Any%, 1 player. It was built by an AI (Claude, working in Claude
Code). It starts at power-on and plays all eight stages. On the speedrun.com clock it takes
**9:24.321 (33,915 NES frames)**. The human record in the same category, Angrylanks' **9:48.183**, is 23.86 s slower.

It is a **tool-assisted run (TAS)**. It was built with save states and search, and it plays in an emulator (BizHawk
2.11.1, NesHawk core). It does not go on the human leaderboard, and nobody claims it as a human record. What makes it
worth comparing to the human record is that the AI played by the human category's rules, written down as numbers
below, and not by TAS rules.

**Deliberately left out:** the game ROM (bring your own), emulator save states, per-frame captures and videos, the
downloaded TAS movies, and the third-party disassembly the AI read (credited below).

## Watch it on your own computer

1. Install [BizHawk 2.11.1](https://tasvideos.org/BizHawk).
2. Use your own dump of *Contra (USA)*. You can check it against these hashes:

   | | CRC32 | SHA-1 |
   |---|---|---|
   | whole `.nes` file (with its 16-byte iNES header) | `C50A8304` | `C9EA66BB7CB30AD5343F1721B1D4D3219859319B` |
   | headerless (the game data, what No-Intro lists) | `F6035030` | `979494E7869AC7AB4815FDBD1DC99F893F713FBF` |

   BizHawk records the whole-file SHA-1 in the movie header. If your file has a different iNES header but the same
   headerless hash, BizHawk warns that the hash differs, but the game is the same.
3. **File > Open ROM**, then **File > Movie > Play Movie** and choose `contra_ai_9m24s.bk2`. The movie names the
   NesHawk core, so BizHawk switches to it by itself. Leave the NesHawk settings at their defaults.

The movie is the run: every button on every frame from power-on. There is no save state and no memory write.

### Check it yourself (Windows, Python 3.9+, `pip install pillow`)

    python verify_bk2.py --bizhawk "C:\path\BizHawk-2.11.1-win-x64" --rom "C:\path\Contra (USA).nes"

The script starts one EmuHawk with a private copy of your config. It plays the movie hands-off through BizHawk's own
movie playback with `verify_movie.lua`, which makes no joypad calls. This takes about 3 minutes. Then it checks
everything listed under "How it was checked" below and prints PASS or FAIL. Our result is in
`verification/bk2_playback.json`.

## The files

| file | what |
|---|---|
| `contra_ai_9m24s.bk2` | the BizHawk movie (NesHawk, power-on, 34,568 frames) |
| `contra_ai_9m24s.inputs.txt` | the same inputs as text: 34,567 rows, one per frame, buttons joined by `+` (SHA-1 `f807a473119482b44191885f7a9df59a2280b70e`) |
| `make_bk2.py` | writes the movie from the text file and reads it back to confirm the input log equals the list |
| `verify_bk2.py`, `verify_movie.lua` | the hands-off movie check |
| `verification/` | our movie-playback result, the reference pictures, the corrected clock evidence, the independent checker's report and tools |
| `run/` | the run's own proof: two-replay report, per-stage table, input-rule check, clock evidence and pictures, chain notes |
| `harness/` | the code that built the run (see "How it was built") |

**Movie frame offset.** BizHawk emulates frame 1 before a Lua script gets control. So in the harness, list row `i`
(0-based) is played on frame `i + 2`. In a movie, input-log line `k` is played on frame `k + 1`. The movie is
therefore one empty frame followed by the list, unchanged. BizHawk's own movie writer, re-saving the loaded movie,
produced the identical input log.

## The rules it kept (checked by `harness/check_inputs.py`)

- Controller 1 only. Never Left+Right or Up+Down on the same frame.
- **No turbo.** A new press of the same button at most once every 5 frames (12 a second). Every press is held at least
  2 frames and released at least 2 frames.
- **Sustained limits.** At most **109 new presses in any 600 frames (10 s)** and **246 in any 1,800 frames (30 s)**
  for every button, counted across stage boundaries. These numbers come from the record holder's own mashing,
  measured from the button clicks on his microphone (`harness/knowledge/record_mash_rate.md`). He mashes at about 12
  a second only in bursts at bosses, cores and tanks.
- Power-on start. No save state at the start, no memory writes, no Konami code, one player, no deaths.

The run's numbers: B pressed 1,078 times. The most B presses in any 60 / 600 / 1,800 frames are 12 / 70 / 144. The
longest unbroken run of presses 5 frames apart is 41 presses (3.4 s). Lives go 2 -> 8 and never fall. Spread is
picked up at frame 2,021 and Rapid from 3,460. Start is pressed 13 times: once on the title screen and 12 times for six
5-frame pauses (stage 6 at frames 24,223, 24,255 and 24,767; stage 7 at 28,078, 29,808 and 29,872). The stage 6 and 7
solvers chose these pauses to shift the game's timing. Our rules allow them, but no human could reproduce them at that
precision.

## The clock

speedrun.com, Contra (NES), Any% (category timing rules, verbatim):

> Timer starts when the blue life medals appear
> - Timer ends when you lose control after killing the final boss (heart)
> - Tip: Hold 'UP' or 'DOWN' after killing the heart. When Bill automatically reverts to his normal position (standing while pointing his gun forward), that is the frame to stop the timer

Frames are BizHawk's frame counter. A picture of frame f is what the console drew during frame f.

| event | in RAM | on screen |
|---|---|---|
| START: the medals are written to the sprite list (`$2C` becomes 4 in stage 1) | 593 | **594** (0 medal-coloured pixels on 590-593, 70 on 594) |
| control lost after the heart (`$2C` becomes 9 in stage 8), Down held | 34,507 | |
| END: Bill stands, gun forward | 34,508 | **34,509** (34,508 prone, 34,509 standing) |

**34,509 - 594 = 33,915 frames.** At the NES's 60.0988 frames a second that is **564.321 s = 9:24.321**. At a flat
60.000 it would be 9:25.250. The 142 lag frames inside that span are timed, as they are for a human. The rows after
END are an untimed tail. Bill ends facing left. The independent check held Down past the end and found that he stands
on 34,509 anyway, so the stop frame is the game's automatic revert, not a choice the run made.

## Stage by stage, against the record

Segment = a stage's first medal frame to the next stage's (stage 8: to END). The record's segments were measured
from Angrylanks' video (video frames x 60.0988/60, +/- 2 frames each).

| stage | ours (frames) | record | ours - record | ahead at the stage's end | lag frames | B presses |
|---|---|---|---|---|---|---|
| 1 Jungle | 3,905 | 3,907 | -2 | +2 | 16 | 97 |
| 2 Base 1 | 3,600 | 3,716 | -116 | +118 | 25 | 160 |
| 3 Waterfall | 3,516 | 3,934 | -418 | +537 | 36 | 32 |
| 4 Base 2 | 5,155 | 5,761 | -606 | +1,143 | 22 | 277 |
| 5 Snow Field | 6,040 | 6,125 | -85 | +1,228 | 13 | 158 |
| 6 Energy Zone | 4,059 | 4,143 | -84 | +1,312 | 13 | 115 |
| 7 Hangar | 4,413 | 4,488 | -75 | +1,387 | 17 | 157 |
| 8 Alien's Lair | 3,227 | 3,273 | -46 | +1,434 | 0 | 82 |
| **total** | **33,915 = 9:24.321** | 35,349 = 9:48.2 | **-1,434 = -23.86 s** | | 142 | 1,078 |

The record's stage segments add up to 35,349 frames, which agrees with its 9:48.183. In the worst case of the
+/- 2 frame measurement, the margin is 22.88 s. Against the faster unofficial 9:46.717 mentioned in the record
holder's notes, the margin is 22.40 s.

## How it was checked

1. **Two power-on replays** by the builders' `assemble.py` on two fresh NesHawk instances. Both gave RAM SHA-1
   `2242cdd88af3f06e8ed6a43de637fc42cb50d619` after frame 34,568 (the frame of the last row), with identical
   per-frame traces.
2. **An independent checker.** It had its own replay code, no access to the builders' harness, and opened the
   builders' files only after it had its own numbers. Its report is `verification/independent_check/REPORT.md`.
   - Three NesHawk processes were identical: the per-frame trace, RAM SHA-1 `2242cdd8...` at 34,568, and all 35,167
     pictures.
   - The clock, read from pictures, matched: START 594, END 34,509, 33,915 frames.
   - The input rules passed. It found no deaths, no Konami code, eight stages in order, and no glitch in 283 sampled
     pictures.
   - It ran two experiments on the ending. Holding Down longer still gives 34,509. Releasing Down at 34,480 makes
     Bill stand on 34,481, so the run gains nothing from its choice at the end.
3. **BizHawk's own movie playback of `contra_ai_9m24s.bk2`** (`verify_bk2.py`, result in
   `verification/bk2_playback.json`), with no input injection.
   - BizHawk loaded the movie in PLAY mode on NesHawk, from power-on, with the ROM hash in the header.
   - The RAM after frame 34,568 has SHA-1 `2242cdd88af3f06e8ed6a43de637fc42cb50d619`.
   - The per-frame RAM and lag flag of frames 2 to 34,568 has SHA-1 `9573e94d483c393b76f758818fe1bb9f242d1a61`. That
     is the same digest the independent checker's two Lua-fed replays give, so the movie reproduces every frame.
   - Medals are written in RAM on 593, control is lost on 34,507, and Bill stands on 34,508.
   - The pictures of frames 590-594, 34,508 and 34,509 are pixel-identical to the reference pictures in
     `verification/pictures/`. Frame 34,508 shows Bill prone and 34,509 standing (see
     `verification/end_f34508_f34509_side_by_side.png`).
4. **Clock evidence, corrected.** The builders' `run/clock_evidence.json` counted 3 "blue" pixels in the medal box on
   frames 590-593, before any medal is drawn. They were light-blue starfield pixels (100,176,254). The independent
   check flagged this. `verification/clock_evidence_corrected.json` (made by `verification/fix_clock_evidence.py`)
   counts only the medal ribbon's colour (66,64,254) and gets 0 on 590-593 and 70 on 594. START and END do not
   change. The original file is kept unchanged.

### What this claim must carry (caveats)

1. **Tool-assisted and emulator-only.** It ran on BizHawk 2.11.1 NesHawk and is not eligible for speedrun.com. The
   23.86 s margin (22.88 s worst case) is emulated time, compared with the fastest run on the board under the board's
   timing rule.
2. **One core only.** The same inputs desync on BizHawk's other NES core (quickerNES), with a game over in stage 1,
   because the game's random numbers follow exact CPU timing. It has not been played on a console or on a second
   accurate emulator.
3. **"No Turbo" is our numeric rule** (above). The board's rule is about controllers, not numbers.
4. The six 5-frame pauses are within our rules but are not humanly reproducible at that precision.
5. Bill ends facing left. Facing does not move the stop frame.

## Can it beat the best TAS? No.

This run is itself a TAS, so the fair question is whether it beats the best TAS. It does not. The fastest published
1-player Contra TAS is **8:48.213** by **Mars608 & aiqiyou** ([tasvideos.org/4623M](https://tasvideos.org/4623M),
FCEUX). It uses the **Japanese** ROM, whose stage transitions are about 25 s shorter in total because there is no
score screen. Compared on gameplay alone, from each stage's first medal frame to its boss event, the TAS is **about
13.6 s (820 frames) faster than our best stage results** (`harness/knowledge/tas_compare.md`). Most of that gap is
fire rate. The TAS presses B up to 30 times a second in the bases and boss fights, while our rules allow at most 12 a
second and 109 per 10 s. Our run is compared with the human record because the AI played by the human category's
rules.

Some route knowledge did come from that TAS. The world positions of the terrain jumps in stages 1, 5 and 8 were read
from its route, and the solvers use them as hints. Every input in this run was produced by the AI's own solvers. No
TAS input data is included here.

## How it was built

`harness/` is the snapshot of the code that made this run (`harness/SNAPSHOT.md` lists every file's SHA-1). It holds:

- `bridge.lua` and `contra/emulator.py`: drive EmuHawk over a socket.
- `contra/stages/s1.py` ... `s8.py` and their helpers: one **solver** per stage. Each plays its stage closed-loop with
  save-state search from whatever state the previous stage left.
- `chain.py`, `run_s67.py` and `finish.py`: run the solvers in order from power-on and verify every prefix by replay.
- `assemble.py`: the two-replay proof. `check_inputs.py`: the rules. `clock_shots.py`: the clock pictures.
- `tools/`: every probe and experiment script, in the order they happened.
- `knowledge/`: what the AI found and wrote down: RAM map, clock proof, per-stage notes, mechanics read from the
  disassembly, the record's measured events and mash rate, and the TAS comparison.

Three chains were run with different title-screen waits. Chain C (wait 3) was the fastest. See `run/chain2_README.md`
and `run/FIXES.md`.

To run it, put `BizHawk-2.11.1-win-x64/` next to `harness/` (in this folder) and your ROM as
`harness/Contra (USA).nes`, then:

    cd harness
    python assemble.py run_chain2 ../contra_ai_9m24s.inputs.txt
    python check_inputs.py ../contra_ai_9m24s.inputs.txt

The snapshot's `contra/emulator.py` here finds BizHawk next to the harness folder. The copy that made the run used the
same code with an absolute path to BizHawk. The solvers search with real emulator timing, so re-running a chain is not
guaranteed to give the same rows. Every result is checked by the same replays.

## Thank you

- Angrylanks, for the record to chase, and the other Contra runners whose tutorials, wiki and notes the AI read.
- Mars608 & aiqiyou, and the other TASVideos Contra authors, for the TAS to measure against.
- vermiceli, for the annotated Contra disassembly (github.com/vermiceli/nes-contra-us).
- The BizHawk team.

Contra © 1988 Konami.
