# Super Mario Bros. 3, Any% (No Wrong Warp): AI run, 10:39.514

An AI built this run from scratch by search, under human input rules, with the human world record's video as its
route and its bar. It is 61 frames (1.019 s) under the human world record, **10:40.533 by MostDefinitelyAlbert**
(https://www.speedrun.com/smb3/runs/y26rrl9m).

## Files

| file | what |
|---|---|
| `smb3_ai_10m39s.inputs.txt` | the run: one input file from power-on, 38,503 lines (line k = the buttons held on frame k; an empty line = nothing; `#` = comment). The same file as the project's `logs/RUN_v1.inputs.txt` (SHA-1 ee5029e485fce018b69460a7bb8962a8e7330506). |
| `smb3_ai_10m39s.bk2` | the BizHawk 2.11.1 movie of it (NesHawk core): the file line for line plus 120 idle lines so the fade after Bowser's door is in the movie. |
| `make_bk2.py` | writes the movie from the input file (and checks the movie's input log against the file). |
| `verify_bk2.py`, `verify_movie.lua` | plays the movie with BizHawk's own movie player, hands-off, and checks it (see below). |
| `verification/` | the reports: `bk2_playback.json` (the movie check), `verify_RUN_v1.txt` and `verify_RUN_v1_second.txt` (the two full verifications of the input file), `wr_events.md` / `.json` (the record's video, frame by frame, at the same events). |

Not included, on purpose: the ROM, save states, and any third-party disassembly. You need your own
**Super Mario Bros. 3 (USA)** ROM, revision PRG0: whole-file SHA-1 `5F9019040FE23CB412A484E1EF430E59E589F9B4`
(headerless `a611b90b4833b20a364bf06ee3be3b9093ea4df9`).

## The rules it played by

- **Leaderboard:** speedrun.com Any% (No Wrong Warp). Warp whistles allowed, no wrong warps. Time starts on the
  Start press on the title screen and ends on entering the door after Bowser, "exactly 5 frames before the screen
  begins to fade".
- **Human input rules on top:** a new press of the same button at most once every 5 frames, never Left+Right or
  Up+Down together, controller 1 only, one input file from power-on. An input judge (`check_inputs.py --period 5
  --hold 1 --release 1`) passes over all 38,503 lines.
- No TAS inputs are in the run. The best TAS's save states were used only as throw-away practice states while the
  search tools were being built; the run itself was searched on its own chain, level after level.

## Timing

- Start: the second Start press, line 68 (the game needs two: lines 13 and 68). The game's pad byte `$17` shows
  Start on frame 68.
- End: `Level_ExitToMap` (`$14`) becomes non-zero on Bowser's door on frame 38,502. The fade's first darker picture
  is frame 38,507 = end + 5, so this is the leaderboard's "5 frames before the fade".
- 38,502 - 68 = **38,434 frames = 639.514 s = 10:39.514** at the NES's 60.0988 frames a second.
- The record measured the same way from its video (Start press = video frame 19050, end = 5 frames before the
  first darker picture, 57449 - 5): 38,495.7 NES frames; its official 10:40.533 = 38,495.3. **61 to 62 frames
  faster** by every measure (official time -61.3, same events -61.7, picture to picture -61.5; error budget about
  3 frames). The record's events are in `verification/wr_events.md`.

## How it was checked

1. **Input judge:** pass (the whole file).
2. **Two emulators from power-on:** built on Mesen 2; replayed on Mesen and on BizHawk 2.11.1 / NesHawk. The two
   agree on all 197 milestones (level loads, goal cards, doors, pipes, Level_ExitToMap, map turns, black and visible
   pictures), on the same rows. Done twice (`verification/verify_RUN_v1*.txt`).
   NesHawk's power-on comes one frame earlier than Mesen's, so on NesHawk the file is played without its first
   (empty) line; in the movie that line is the first movie frame, which is the same thing.
3. **The video capture** (NesHawk, the file stepped frame by frame through BizHawk's Lua): 38,683 frames (the file
   + 180 idle), no repeated or dropped picture, every one of 38,682 screenshots identical to its dump frame, and its
   RAM milestones identical to the Mesen list.
4. **The movie** (`verify_bk2.py`): BizHawk's own movie player, no input injection, no memory writes, no save
   states. It must load the movie on NesHawk from power-on with the right ROM, and the RAM + lag flag of every frame
   2..38,623 must hash to `0bac2e729dbca3718d221b3711c21622b3e434c6` (the capture's), the Start press must be seen
   on frame 68, `Level_ExitToMap` on 38,502 in Bowser's castle, and frame 38,507 must be darker than 38,506.

       python verify_bk2.py --bizhawk "C:/path/BizHawk-2.11.1-win-x64" --rom "C:/path/Super Mario Bros. 3 (USA).nes"

   Result (2026-11-15, BizHawk 2.11.1, NesHawk): **PASS**. Trace SHA-1 matched, Start press on frame 68, Level_ExitToMap on
   frame 38,502 (World 8 castle), 38,434 frames = 10:39.514, frame 38,507 darker than 38,506. Report: `verification/bk2_playback.json`.

## The best TAS

This is a tool-assisted run too (an AI built it frame by frame with save states), but under human input rules. The
best published TAS of this category is **3922M, 10:24.338 by Lord_Tom, Maru & Tompa** (https://tasvideos.org/3922M,
FCEUX, USA PRG0, timed from power-on to its last input; about 10:23 by the leaderboard's events, an estimate). It is
about 16 seconds faster than this run. The AI first tried to beat that TAS and came within 1/16 of a pixel of the
frame it needed in 8-1; then the goal became the human record.

Super Mario Bros. 3 (c) 1988 Nintendo. BizHawk (TASVideos), Mesen.
