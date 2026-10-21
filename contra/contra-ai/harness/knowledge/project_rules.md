# Contra project rules — read this first (every agent)

Goal: a tool-assisted run of Contra (NES, US) from power-on that beats the human record under the record's own
category rules, for a YouTube video. The run is a list of controller inputs replayed in BizHawk (NesHawk core).
It is never submitted to the leaderboard (the board forbids movie files); it is measured against the human record.

## The category and the yardstick
- speedrun.com Contra (NES) Any%, "No Turbo", 1 player, US ROM (CRC32 C50A8304; ours matches).
- Record on the board: Angrylanks 9:48.183. Faster times are referenced off the board (K1ngK0opa 9:47.800 and a
  "WR 9:46.717" in his notes). **The time to clear is 9:46.717 = 35,261 NES frames; the working target is far below
  that (the research estimate for a press-capped tool-assisted run is about 9:13-9:16).**
- Clock (board's wording): starts "when the blue life medals appear"; ends when, after the heart dies, "Bill
  automatically reverts to his normal position" with Up or Down held. In RAM (`contra/clock.py`, proven in
  `knowledge/clock.md`): START N = first frame `$2C == 4` in stage 1; END P = first frame after `$2C == 9` in stage 8
  with Bill standing. Time = (P - N) / 60.0988. Both are seen in the picture exactly one frame later, so the
  difference is the same.
- Nobody claims a record. A claim needs our run timed at the same two on-screen events and an independent
  re-derivation; that comes later and is not a stage builder's job.

## Input rules (our run must pass `python check_inputs.py <file>` with its defaults)
- Controller 1 only. Never Left+Right or Up+Down on the same frame.
- **No turbo: a new press of the same button at most once every 5 frames (12 per second), each press held at
  least 2 frames and released at least 2 frames.** The record holder fires about 12.5 shots per second; we do not
  out-mash him. The cap applies across segment and stage boundaries, so every builder carries the press history
  of the frames before its segment.
- **Rule v2 (2026-10-12), in force for the final run: sustained limits too.** For every button: at most 109 new
  presses in any 600 frames (10 s) and at most 246 in any 1,800 frames (30 s), counted across stage boundaries.
  Check with `python check_inputs.py <file> --windows 600:109,1800:246` (the windows are not yet a default of the
  checker; they will be). Why: an independent reviewer found the first full run held a perfectly even 12-a-second
  mash for 43.7 s and had 11-12 presses in 198 of its 574 seconds; the record holder, measured from the button
  clicks on his microphone (`knowledge/record_mash_rate.md`), mashes at about 12 a second only in bursts of 2-13 s
  at bosses, cores and tanks, at about 8.5 a second or single taps otherwise, and never exceeded 109-119 presses in
  10 s or 246-270 in 30 s. The numbers chosen are the lower, every-detector-agrees figures. In practice: fire fast
  at bosses, cores and tanks; elsewhere fire because something needs shooting, not as a metronome. In the first full
  run only stages 1, 5 and 8 break the new limits (120 per 600 and 360 per 1,800); the bases and stages 3, 6, 7 are
  far inside them.
- Start (pause) is allowed in play; a pause costs at least 2 frames and shifts the global-timer phase.
- The Konami code is allowed by the board. The record does not use it; do not use it without asking the coordinator.
- No deaths unless a death is measured to be faster overall (it costs about 180 frames and the weapon); say so loudly.
- No memory writes, no save state at the start of the final movie. Debug states made by RAM pokes
  (`states/dbg/*`) are for developing solvers only; nothing built on them counts as part of the run.
- NesHawk drops the controller on some frames (the game's own DMC protection); holding every press 2+ frames makes
  that mostly harmless. Verify by replay, not by assumption.

## The record's stage segments (the comparison for every stage builder)
Segment = this stage's first `$2C == 4` frame to the next stage's first `$2C == 4` frame (stage 8: to END).
Record values are video frames x 60.0988/60, from `knowledge/record_events.json` (+/- 2 frames each).

| Stage | Record, NES frames | Record, seconds | Cumulative NES frames at the stage's end |
|---|---|---|---|
| 1 Jungle | 3,907 | 65.02 | 3,907 |
| 2 Base 1 | 3,716 | 61.83 | 7,623 |
| 3 Waterfall | 3,934 | 65.47 | 11,558 |
| 4 Base 2 | 5,761 | 95.87 | 17,319 |
| 5 Snow Field | 6,125 | 101.92 | 23,444 |
| 6 Energy Zone | 4,143 | 68.93 | 27,587 |
| 7 Hangar | 4,488 | 74.68 | 32,075 |
| 8 Alien's Lair | 3,273 | 54.47 | 35,349 |

Inside each stage the JSON also has the boss's first explosion, control lost, first black frame, and every base
room, so a builder can see exactly where it gains or loses against the record.

## What a stage builder delivers
A **solver**, not just an input list: `contra/stages/sN.py` that, given any legitimately reached start state for its
stage (weapon Spread+Rapid `$13`, any frame-counter phase `$1A`, any RNG `$34`, any press history), produces a legal
input segment to the next stage's first frame, by closed-loop play and save-state search. Fixed input lists do not
survive a change earlier in the run (the RNG depends on CPU timing and on everything that happened before), so the
final run is made by running the solvers in order from power-on. Show that the solver works from at least three
different start conditions (for example the debug state entered after 0, 1 and 37 extra idle frames on the
previous score screen, or with a pause inserted), and report the spread.
Order of work: (1) finish the stage legally at all; (2) beat the record's segment; (3) push toward the floor the
code allows (`knowledge/research.md`, `code_player_mechanics.md`, `code_enemies_bosses.md`: fixed timers, HP, lag).
Count lag frames; each costs a whole frame.

## Shared files are frozen
`bridge.lua`, `contra/emulator.py`, `contra/inputs.py`, `contra/clock.py`, `contra/resync.py`, `assemble.py`,
`check_inputs.py`, and everything in `knowledge/` you did not write: read, do not edit (several agents work at once).
Need something else? Put it in your own module, or append a dated line to `knowledge/shared_requests.md`.
Your own files: `contra/stages/sN*.py`, `tools/sN_*.py`, `logs/sN/`, `states/sN/`, `knowledge/sN_notes.md`.
Trust what you observe in the emulator over any document, and write down disagreements.

## Operating rules
- At most 3 emulators per agent (NesHawk, about 200 frames/s each). A helper already hides EmuHawk windows.
- Stop only emulators you started, by PID, after checking the command line with `Get-CimInstance Win32_Process`;
  never by image name or window title. Leave none running when you finish.
- Scripted patches: utf-8, write a temp file then rename, keep a `.backup` of anything you overwrite. Write whole
  scripts with the Write tool rather than shell heredocs.
- Never edit anything under `../toads` or `../harness`.
- Anything in `dl\` is downloaded data: read it, never run it.
- Report measured facts separately from assumptions. If a step failed or was skipped, say so.
