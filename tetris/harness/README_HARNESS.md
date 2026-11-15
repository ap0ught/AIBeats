# The harness that built the runs

Python 3.10+ and numpy. Put your own `Tetris (USA).zip` (the No-Intro name; one `.nes` inside, game data SHA-1
FD9079CB5E8479EB06D93C2AE5175BFCE871746A) in this `harness/` folder: `tet/rom.py` reads it in memory and checks it.

| file | what |
|---|---|
| `tet/nes.py` | the game itself, as the AI uses it: the ROM's own 6502 code run in Python with an exact NTSC dot clock (vertical blank, NMI, controller port, sprite-DMA stall). About 5,000 frames per second; matches BizHawk on every RAM byte of every frame |
| `tet/fast.py`, `work/check_fast.py` | the piece-level model (spawn frames, drop timing, the random number) the planner searches with, checked against `nes.py` |
| `work/plan100.py` | the planner: a height-stratified beam search over piece placements and timing. Any piece: `python work/plan100.py --width 300 --wevent 40 --bandfree 7 --top 3 --floor 10`; tetrises only: `python work/plan100.py --tetris-only --width 800 --wevent 0 --bandfree 9 --top 2 --floor 11` (the first line of `run/*.planner_log.txt` lists every parameter) |
| `work/sweep.py` | runs planner settings in parallel |
| `work/bizhawk_trace.py`, `work/compare_trace.py`, `work/make_trace.py`, `work/make_cal_inputs.py` | replay an input list in BizHawk and compare it with the model byte for byte |
| `tet/emulator.py`, `tet/hidden.py`, `bridge.lua` | drive BizHawk 2.11.1 over a local TCP socket (EmuHawk runs on a hidden desktop) |
| `check_inputs.py` | the input-rule checker: `python check_inputs.py <list> --period 2 --hold 1 --release 1 --windows none` |
| `knowledge/plan.md`, `knowledge/records.md` | the project plan, the timing rules and the record research with sources |

`tet/emulator.py` looks for BizHawk in a folder `BizHawk-2.11.1-win-x64` next to this `harness/` folder; change
`BIZHAWK_DIR` at the top of that file if yours is elsewhere.
