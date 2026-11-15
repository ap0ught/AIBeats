# An AI vs NES Tetris: 100 lines in 2:14.91, and in 2:16.24 using only tetrises

This folder has two input files for **Tetris (NES, USA)**, category **100 Lines (A-Type)**. Both were built by an AI
(Claude, working in Claude Code) and start at power-on:

| run | time | frames | pieces | line clears |
|---|---|---|---|---|
| **any piece** (`tetris_ai_2m14s_any_piece`) | **2:14.91** | 8,108 | 256 | 38 (5 singles, 10 doubles, 17 triples, 6 tetrises) |
| **tetrises only** (`tetris_ai_2m16s_tetrises_only`) | **2:16.24** | 8,188 | 257 | 25, every one a tetris |
| world record time: Cheez, 7 March 2022, console | 2:43.54 | 9,828 | 243 | about 63 |

The any-piece run is **28.63 s** under the world record time; the tetrises-only run is **27.30 s** under it.

Both runs are timed the way the record is: from the frame the Start press on the level-select screen begins, to the
first frame the LINES counter on screen shows 100. Both start on level 19, as the record does (a level 19 game stays
on level 19 for the whole 100 lines). Frames are NES frames at 60.0988 per second.

These are **tool-assisted runs** played in an emulator (BizHawk 2.11.1, NesHawk core). They are input files, not
leaderboard submissions: the board (speedrun.com/tetrisnes) only takes runs played live, and nobody claims them as
human records. What makes them worth comparing with the record is that the AI held itself to human input rules,
written down as numbers below.

**Deliberately left out:** the game ROM (bring your own), savestates, the disassembly listing the AI made from the
ROM, the record's video and anything taken from it, and video-production files.

## Watch it on your own computer

1. Install [BizHawk 2.11.1](https://tasvideos.org/BizHawk).
2. Use your own dump of *Tetris (USA)* (Nintendo, 1989, NES-EI-USA). You can check it:

   | | SHA-1 |
   |---|---|
   | the game data (PRG + CHR, without the 16-byte header) | `FD9079CB5E8479EB06D93C2AE5175BFCE871746A` |
   | the whole `.nes` file as No-Intro ships it (NES 2.0 header) | `3026D28B63D94C921FE58364F8B0659D10B5A0AC` |

   If your file has another header but the same game data, BizHawk may warn that the hash differs; the game is the
   same and the movie plays the same.
3. **File > Open ROM**, then **File > Movie > Play Movie** and choose `tetris_ai_2m14s_any_piece.bk2` (or
   `tetris_ai_2m16s_tetrises_only.bk2`). Leave the NesHawk settings at their defaults.

The movie is the run: every button on every frame from power-on. There is no savestate and no memory write. The
first 298 frames are the title and menu screens; Start on the level-select screen is pressed on frame 299.

### Check it yourself (Windows, Python 3.9+, no extra packages)

    python verify_bk2.py --bizhawk "C:\path\BizHawk-2.11.1-win-x64" --rom "C:\path\Tetris (USA).nes"
    python verify_bk2.py --run tetrises --bizhawk "C:\path\BizHawk-2.11.1-win-x64" --rom "C:\path\Tetris (USA).nes"

The script starts one EmuHawk with a private copy of your config and plays the movie hands-off through BizHawk's own
movie playback (`verify_movie.lua` makes no joypad calls and writes no memory). It takes under a minute. It then
checks every frame's RAM against the reference, reads the time off the LINES counter in RAM, and prints PASS or FAIL.
Our results are in `verification/bk2_playback_any_piece.json` and `verification/bk2_playback_tetrises_only.json`.

## The files

| file | what |
|---|---|
| `tetris_ai_2m14s_any_piece.bk2` / `.inputs.txt` | run 1: the BizHawk movie and the same inputs as text (a `# frames=` line, then one row per frame, buttons joined by `+`) |
| `tetris_ai_2m16s_tetrises_only.bk2` / `.inputs.txt` | run 2, the same way |
| `make_bk2.py` | writes a movie from a text file and reads it back to confirm the input log equals the list |
| `verify_bk2.py`, `verify_movie.lua` | the hands-off movie check |
| `verification/` | the per-frame RAM reference of each run, our movie-check results, the model-vs-BizHawk comparison |
| `run/` | the input-rule check of each run, the planner's log of each run, and `progress.csv` (every run the project made, with its time) |
| `harness/` | the code that built the runs (see `harness/README_HARNESS.md`) |

**Movie frame offset.** The harness power-cycles the core (frame counter 0) and plays list row k on frame k. In a
movie, input-log line k is also played on frame k, so the movie is the list unchanged, with no lead-in line.

## The rules it kept

The leaderboard's rules for 100 Lines: NTSC game, any starting level, no turbo, no Left+Right or Up+Down, no
savestates, no demo glitch. On top of those, our own human rules (checked by `harness/check_inputs.py`):

- controller 1 only, one unbroken input file from power-on;
- never Left+Right or Up+Down on the same frame;
- **no more than 30 presses a second on any button**: a new press of the same button at most every 2 frames (held at
  least 1 frame, released at least 1 frame). That is the fastest rate we measured in the record holder's own run, in
  short bursts, and it is as fast as the game can read a button at all.

`python harness/check_inputs.py <list> --period 2 --hold 1 --release 1 --windows none` passes for both runs; the full
reports (presses per button, fastest second per button) are in `run/*.check_inputs.txt`.

**The pieces.** NES Tetris picks the next piece from a 16-bit number that changes once every frame, so which pieces
come depends on timing. The AI plans with that: it chooses the frame of the Start press and the moment each piece
lands, and so it chooses its pieces. A person can in principle do the same, and the leaderboard's rules do not forbid
it, but no human can do it frame-perfectly for 256 pieces. This is the main reason a tool-assisted run is so much
faster than a human one.

## How it was checked

1. **The AI's copy of the game is exact.** `harness/tet/nes.py` runs the ROM's own 6502 code in Python with the
   NES's exact timing. Both final runs were replayed in BizHawk from power-on, inputs fed through Lua, and all 2,048
   bytes of RAM were compared with the Python copy after every frame: identical on every frame
   (`verification/model_vs_bizhawk.txt`).
2. **BizHawk's own movie playback** of each `.bk2`, with no input injection: the lag flag and the SHA-256 of all of
   RAM equal that replay on every frame, and the time read from the LINES counter is 8,108 and 8,188 frames
   (`verification/bk2_playback_*.json`).
3. **The input rules**, by a separate checker (`run/*.check_inputs.txt`).

## Can it beat the best TAS?

These runs are tool-assisted too: built frame by frame, by an AI, in an afternoon. There is no published tool-assisted
run of this category to compare with: TASVideos has NES Tetris movies for other goals (a maximum-score movie, a Mode B
movie and a playaround), not for 100 lines. A tool-assisted run with no human limits would be faster than ours,
because ours holds itself to 30 presses a second and to the human rules above; we have not measured by how much.

## How it was built

1. **Watching the record.** The record video was read frame by frame for its timing, its piece count and the record
   holder's tap rate (the 30-per-second limit comes from there). Nothing from the video is in this folder.
2. **Taking the game apart.** The AI disassembled the ROM to learn the piece generator, the drop timing, the line
   clear delay and when the game reads the controller (the listing is not included).
3. **Rebuilding Tetris in Python** (`harness/tet/nes.py`, about 5,000 frames per second), then a faster piece-level
   model (`harness/tet/fast.py`) that is checked against it.
4. **Planning.** A beam search (`harness/work/plan100.py`) keeps a few hundred possible games, tries every legal
   placement of the next piece in each, and keeps the best, for 256 pieces. Its scoring keeps the stack high (a piece
   that falls less lands sooner) and makes small clears expensive (every clear freezes the game for about 19
   frames). The first plan, 2:22.43, already beat the record time; tuning brought it to 2:14.91. The tetrises-only
   run forbids every clear smaller than four rows.

`run/progress.csv` lists every run along the way.

## Credits

- Cheez, for the 2:43.54 world record time to chase.
- BizHawk (TASVideos).
- Tetris (c) 1989 Nintendo; Tetris (c) Elorg. The ROM is not included; use your own.
- Built by Claude (Anthropic), in Claude Code.
