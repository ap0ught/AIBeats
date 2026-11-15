# NES Tetris: plan

Project: an AI plays the original Tetris on the NES and beats a human world record, for the series
"AI learns video games, then beats the world record". Started 2026-11-13. Folder `<project>\`.

## 1. The record to beat (owner's choice, 2026-11-13)

**100 Lines, A-Type** on speedrun.com/tetrisnes ("Clear 100 lines as fast as possible, starting at any level").

| | |
|---|---|
| Record | **2:43** on the board; the runner's own retime in the video title is **2:43.54** |
| Holder | Cheez (the player who invented rolling) |
| Date | 2022-03-07, verified 2022-03-09; unbeaten since (2nd: EricICX 2:49, 3rd: Gwafey 2:55 in 2024) |
| Platform | NES console, level 19 start |
| Video | https://www.youtube.com/watch?v=T2uQ6I-eM6I (854x480, 30 fps) |
| Timing | "begins at level select, and ends when the score value displays greater than or equal to 100 lines" |
| Banned | PAL, turbo, Left+Right or Up+Down, save states, the demo glitch |
| Board size | 239 runs; 17 new runs in 2025 and 17 so far in 2026 |

Target in frames: 163.54 s x 60.0988 frames/s = **9,828 NES frames** from the Start press on the level-select
screen to the first frame the LINES counter shows 100 or more. Our run counts the same way, in the emulator.
A start level of 19 never changes level within 100 lines (the first level-up from a 19 start is at 140 lines);
start levels 9 to 15 also stay constant (first level-up at 100).

The owner first looked at B-Type Height 0-5 (5:42, Gwafey, 2025-01-08) and dropped it for being a small category
(20 runs, none in 2026). It, 300K Points (1:35) and 100 Lines Level 0 Start (3:42) can reuse everything built
here if a follow-up is wanted. The endurance records (score 40.26M, crash, rebirth) are a poor fit: hours long,
set on a modified ROM since 2024, unbounded for a bot, and they need 20-30 presses per second throughout.
Full table with dates and sources: `records.md`.

## 2. The ROM

`Tetris (USA).zip` (the owner's file, 24,312 bytes) holds `Tetris (USA).nes`, 49,168 bytes: 16-byte NES 2.0 header,
32 KB PRG, 16 KB CHR, mapper 1. PRG+CHR sha1 `FD9079CB5E8479EB06D93C2AE5175BFCE871746A`, crc32 `1394F57E`:
BizHawk's own cartridge database (`gamedb/NesCarts.xml`) lists exactly this as "Tetris", Nintendo, NES-EI-USA,
1989-11, NES-NTSC, board NES-SEROM, dump ok. So it is Nintendo's licensed NTSC release, the version the category
requires. The zip is read in place (BizHawk loads it directly, Python reads it in memory); nothing is extracted.

## 3. What the record run does (measured from the video, 2026-11-13)

Method: every video frame was drawn to a canvas in the built-in browser and the 10x20 field read at the cell
centres (5,263 frames at 30 fps; nothing was downloaded). Two NES frames per video frame.

- 243 pieces and about 63 line-clear events to reach 102 lines. Mostly singles to triples, few tetrises.
- Level 19 throughout (a piece falls one row every 2 frames).
- The stack is not built from the floor: a narrow pillar holds a floating working area, so pieces fall less far.
  Highest filled row just before each spawn: mostly rows 4 to 8 counted from the top (mode 6).
- Time from one spawn to the next: 28 to 36 frames without a line clear, 48 to 56 with one.
- Taps: 415 sideways shifts. 123 pairs of same-direction shifts are one video frame apart (2 NES frames, the
  game's ceiling of 30 presses per second), 77 are two apart, 21 are three apart. Bursts at the ceiling: 48
  doubles, 30 triples, 5 quadruples.
- The B-Type record (Gwafey, 60 fps video, 559 shifts) shows the same: 142 same-direction pairs exactly
  2 frames apart, 72 at 4 frames, 22 at 6 (DAS), bursts of up to 4 taps at 30 per second.

Where a planner can gain on it (estimates, to be replaced by planned numbers):

- Line clears. Each clear event costs 17 to 20 frames whatever the number of lines. 63 events is about 1,250
  frames; 25 tetrises would be about 480. The 300K record holder writes that this run lost "approx 7 seconds"
  to long-bar luck. The piece sequence is not luck for a planner: it is fixed by the frame each piece spawns on.
- Fall distance. Every row higher saves about 1.5 frames per piece (2 less falling, 0.5 more entry delay).
- The wait before pressing Start on the level-select screen is not timed and decides the first pieces.

Rough size of the prize: 250 pieces at 29 to 32 frames plus 25 clears is 7,750 to 8,500 frames, about 2:09 to
2:21, against 2:43.54. This is arithmetic, not a result.

## 4. Input rules (owner's decision, 2026-11-13)

Series rules that carry over unchanged: controller 1 only, no Left+Right, no Up+Down, no turbo, one unbroken input
file from power-on, no save states in the final run, no one else's movie.

**Press rate: 30 presses per second per button** = the record holder's own measured peak. A new press of a button
at most every 2 frames, held at least 1 frame, at least 1 frame released before the next press. This is also the
game's ceiling: it only sees a press after a released frame.

Checker: `python check_inputs.py LOG --period 2 --hold 1 --release 1 --windows none`.

The owner was offered three options: 12 per second (the TMNT rule, recommended for series consistency, estimated
5 to 12 seconds slower), 30 per second, or 15. He chose 30. The planner still takes the period as a parameter.

What the rate buys on level 19 (one row of fall every 2 frames): a shift every 2 frames means a piece can move one
column per row it falls, so a column d steps from the spawn column is reachable from d rows down. At 12 per second
it would have been one column per 2.5 rows.

## 5. How the run gets made

1. **ROM-level model** (`tet/nes.py`): the game's own 6502 code, translated block by block to Python, with the
   vertical-blank/NMI clock, the controller port and the sprite-DMA stall modelled on the real dot clock.
   About 5,000 frames per second in one process (BizHawk under load: about 250). Status in section 7.
2. **Piece-level model** (`tet/fast.py`): placement and timing rules written out by hand for the planner (level
   19 only), checked against the ROM-level model piece by piece (`work/check_fast.py`). Planner: `work/plan100.py`.
3. **Planner**: search over start frame, placements and timing; pieces come from the game's own generator, so the
   plan includes which frame each piece spawns on.
4. **Verification**: the input file is replayed in BizHawk from power-on and compared with the model, then
   checked by `check_inputs.py` under the agreed limits. Timing is read from the LINES counter on screen.

## 6. Machine sharing (until the owner says TMNT is finished)

At most 2 BizHawk emulators from this project at a time and about 4 CPU workers. Emulators are only needed for
verification; planning runs in the model. Never kill EmuHawk by name; only our own child processes are stopped.
Nothing under `TMNT\` is modified. `tet/emulator.py` refuses to launch when memory is short (on 2026-11-13 the
commit limit was 97% used while TMNT ran 11 emulators and the owner was in a game).

## 7. Status (2026-11-13)

- ROM identified (section 2).
- Record chosen by the owner: 100 Lines.
- ROM-level model matches BizHawk on all 2,048 RAM bytes of every frame of two traces from power-on, 11,495 frames
  (`logs/cal1`, `logs/cal2`: menus, A-Type level 0, B-Type level 19 height 5, pause, top-out, restart).
  Not covered yet: line clears, level-ups, the 100-line finish. Next check.
- Two things were set from the BizHawk traces: its power-on RAM (00 00 00 00 FF FF FF FF repeating) and that the
  first frame starts without the vertical-blank flag.
- Input limit decided by the owner: 30 presses per second (section 4).
- Line clears now covered: `logs/fastchk` (6,480 frames, a game with completed rows) is identical to BizHawk too.
- Piece-level model `tet/fast.py` agrees with the ROM-level model on 1,721 pieces and 303 cleared lines in 30
  random games (`python work/check_fast.py 30 300 7`): spawn frame, field, pieces, random number, line count.
- **First verified run under the record: 8,560 frames = 142.43 s** (record 9,828 frames = 163.54 s), 259 pieces.
  `logs/plan_w400.inputs.txt`, 8,871 frames from power-on; Start is held from frame 299 and the LINES counter
  shows 100 on frame 8,859. Replayed in BizHawk from power-on: every RAM byte of every frame equals the model.
  `check_inputs.py --period 2 --hold 1 --release 1 --windows none`: PASS (389 Left, 266 Right, 141 A, 23 B, 130 Down).
  Made by `python -m work.plan100 --width 400` in 150 s on one core.
- 2026-11-13 later: **134.91 s** (`logs/s2_5`, 8,108 frames, 38 clear events) and a **tetris-only run, 136.97 s**
  (`logs/t1_2`, 8,232 frames, exactly 25 tetrises, the owner asked for it). Both identical to BizHawk from power-on
  and passing the input check. Planner options: `--wevent` (ranking cost of small clears), `--tetris-only`,
  `--floor/--top/--bandfree`; `work/sweep.py` runs several settings on 4 workers. Every run goes in `logs/progress.csv`.
  Finding: pieces already lock on rows 3-6; the time was in 61 small clears (about 19 frames each).
- **Final runs (owner accepted them on 2026-11-13): any piece `logs/s2_5` 134.91 s; tetris-only `logs/t2_1`**
  **136.24 s (8,188 frames, 25 tetrises).** Both go in the video, any piece first. Speed work is closed.
- Slack left on the table, for the record: the first piece is dropped straight and the wait before Start is fixed (0); the
  platform is held at row 9 or lower (`MIN_FLOOR`), the arithmetic in section 3 says about 2:05 to 2:10 is there;
  the search is a width-400 beam with a hand-set estimate.

## 8. Files

- `knowledge/records.md`: all records researched, with sources.
- `tet/rom.py`, `tet/dis6502.py`, `work/disasm/tetris.asm.txt`: ROM access and our own disassembly.
- `tet/nes.py`: ROM-level model. `work/compare_trace.py NAME`: model against a BizHawk trace.
- `tet/emulator.py`, `bridge.lua`, `tet/hidden.py`, `tet/inputs.py`, `check_inputs.py`: copied from TMNT and adapted.
- `work/make_cal_inputs.py`, `work/bizhawk_trace.py`: calibration traces.
