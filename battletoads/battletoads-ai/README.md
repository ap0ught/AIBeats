# An AI vs Battletoads (NES): the harness, the journal, and the 11:54 run

> **Correction (October 2026).** The video and the first version of this repository said the AI's run was **12:23.39**
> and beat the record. That was wrong. The clock had been stopped at the cut to the Dark Queen's speech; the category's
> rule ends the run one cut later, at Professor T. Bird's dialogue. Timed correctly, that published run is **12:31.75**,
> which is 2.5 seconds *slower* than jay_cee's 12:29.25. A viewer, @retrothundr, caught it.
>
> The AI went back to work. The run in this repository now is **11:54.02**, timed by the rule, checked against the
> record holder's own video, and re-verified by a separate checker that had to assume the builders were wrong. The
> full story is in [`run/CORRECTION.md`](run/CORRECTION.md); the published run is kept, with its true time, in
> `run/published_run/`.

This is everything behind the video. It has the tools the AI (Claude, working in Claude Code) wrote for itself, the
journal it kept while working, every search and probe script it ran, and the input file of the final run: **11:54.02**
on the speedrun clock, in Battletoads (NES), Any% (No Credits Warp). The human world record at the time was 12:29.25
by jay_cee.

**Deliberately left out:**
- The game ROM. Bring your own.
- Emulator save states and the multi-gigabyte captures.
- The TASVideos movies and other people's documentation that the AI read (linked below).

Nothing here plays without your own copy of the cartridge.

## Watch your own computer play the run (two minutes)

1. Install [BizHawk 2.11.1](https://tasvideos.org/BizHawk). Keep the default NES core, **QuickNes**.
2. Load your own dump of *Battletoads (USA)*. BizHawk should identify it as SHA-1 `5C3A497A82BE60704DEDF45248B6AD9B32C855AB`.
3. Go to **File → Movie → Play Movie** and choose `run/battletoads_ai_11m54s.bk2`.

The movie is the run: every button on every frame from power-on. Other files in `run/`:

| file | what |
|---|---|
| `battletoads_ai_11m54s.bk2` | the run for BizHawk's default core (QuickNes): 11:54.02 |
| `battletoads_ai_11m54s_NesHawk.bk2` | the same route ported to BizHawk's accuracy core (NesHawk): 11:54.16. The game's random numbers follow CPU timing, so each core needs its own input file; an input file is proof only on the core it was made for |
| `inputs.txt`, `inputs_NesHawk.txt` | the same inputs as plain text, one line per frame |
| `why.txt` | the notes the AI attached to each part. These are the WHAT/WHY lines shown beside the run |
| `token_log.jsonl` | what it cost, mark by mark |
| `VERIFICATION.txt` | the numbers: which frames start and stop the clock, the hashes, how to check them yourself |
| `CORRECTION.md` | what was wrong the first time, how it was found, and what changed |
| `verification/` | the independent checker's report and its pictures of the two ending cuts |
| `published_run/` | the run shown in the video (12:23.39 on the wrong clock, 12:31.75 on the right one), kept for the record |

You can check a movie yourself with `verify_movie.lua`; the instructions are inside it.

## How the run is timed

The category's rule: time starts when you gain control of the toad in Level 1 and ends when the game cuts to Professor
T. Bird's final dialogue.

- Start: the frame the toad lands in Level 1, frame 2,074 of the input file.
- End: the *second* time the level byte goes 13 → 254, frame 44,986. The *first* such change (frame 44,566) is only the
  cut to the Dark Queen's speech; the game goes back to the tower after it. Stopping there was the original mistake.
- 44,986 − 2,074 = 42,912 frames at 60.0988 frames per second = 714.02 s = **11:54.02**.
- The record's 12:29.25 was re-read on jay_cee's own video, frame by frame: it runs between the same two events.
  Reading the start a few frames differently changes either time by at most 0.07 s.

## Run the harness yourself

```
pip install -r requirements.txt
python smoke_test.py          # launches BizHawk with the bridge and reads a frame
```

The harness expects `BizHawk-2.11.1-win-x64/` and `Battletoads/Battletoads (USA).nes` next to this folder (see
`toads/emulator.py`).

The route was built level by level:
1. Searches (`toads/beam.py`, `toads/pbeam.py`, `fightbeam.py`, `l4s.py`, `l13solve2.py`, …) write segment files.
2. `assemble.py` stitches the segments together from power-on and replays them twice, which is how every route was verified.
   It reports the run time from the landing to the T. Bird cut, and refuses to report one for a route that stops early.

The `l*.py`, `*_pipeline.py`, `probe`-style and `tas*` scripts are the history: every experiment, in the order it
happened. The scripts of the recovery are the ones named `end_*`, `l13z_*`, `l12h_*`, `early_*`, `l9heli_*`, `u16*`,
`u17*`, `tw1_*` and `core_check_toads.py`; their findings are written up in `knowledge/*.md`.

## What is where

| path | what |
|---|---|
| `bridge.lua` | the script inside the emulator: hold buttons, read RAM, save and load states, over a socket |
| `toads/emulator.py` | the Python side of that socket, plus input logging, screenshots and replay |
| `toads/beam.py`, `toads/pbeam.py` | the beam searches over input sequences |
| `toads/ramscan.py`, `toads/dis6502.py` | finding things in memory, and a 6502 disassembler for reading the game's code |
| `assemble.py` | the final route from segments, verified by replaying from power-on twice |
| `rngfit.py`, `retjoin.py`, `oldwalk2.py`, `splice.py` | re-fitting later levels when the random numbers change |
| `end_tail.py`, `end_model.py` | the ending after the Queen's last hit: what decides its length, and the shortest legal one |
| `core_check_toads.py` | porting a route to the NesHawk core |
| `make_bk2.py`, `verify_movie.lua`, `verify_bk2.py` | the BizHawk movie and its hands-off check |
| `journal/` | the AI's journal, written as it went |
| `knowledge/` | what it found: search results, fight solutions, level notes (JSON), and the recovery's write-ups (Markdown) |
| `video_tools/` | everything that made the videos: the montage, grids, memory explainers, the tower map, the chiptune, the cut, and the run-with-panel renderer (`run_capture.py`, `run_text.py`, `run1080b.py`) |

## The rules it ran under

- **Category:** speedrun.com Battletoads (NES), Any% (No Credits Warp).
- **Allowed:** the hidden warps and the board's level-end tricks (the Turbo Tunnel bike skip, the death at the end of Terra Tubes).
- **Banned:** the credits warp, pressing Left+Right or Up+Down at the same time, and turbo. The released input files
  have no auto-fire: the between-level pages are passed with single presses.
- **The game itself:** unmodified, controller 1 only, no memory writes in a run.

Save states and search were used to build the run, and it presses buttons with single-frame precision throughout
(including the Select button, which re-rolls the game's random numbers). That makes it a tool-assisted run (TAS), not
a human run. It does not go on the human leaderboard, and no person could perform it.

## Thank you

- jay_cee, for the record to chase.
- @retrothundr, for catching the timing error.
- jc583, for the Speed Demos Archive notes.
- The TASVideos authors (https://tasvideos.org/66G): feos, Alyosha & Samsara; Lobsterzelda; MESHUGGAH & Koh1fds; Phil & Genisto.
- feos's disassembly and Lua tools.
- The DataCrystal RAM map.
- The BizHawk team.

Battletoads © 1991 Rare / Tradewest.
