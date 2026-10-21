# What was wrong the first time, and what changed

## The mistake

The video "AI vs Battletoads" and the first version of this repository said the AI's run took **12:23.39** and beat
jay_cee's world record of 12:29.25. It did not.

The category's rule (speedrun.com, Battletoads NES, Any% No Credits Warp): time starts when you gain control of the toad
in Level 1 and ends **when the game cuts to Professor T. Bird's final dialogue**.

After the Dark Queen's last hit the game cuts twice:

1. to the Dark Queen's speech. The game then goes back to the tower for about eight more seconds;
2. to Professor T. Bird.

In the game's memory both cuts look the same (the level byte goes from 13 to 254), and the AI's clock stopped at the
first one. On the right clock the published run is **12:31.75**: 2.50 seconds slower than the record.

A viewer, @retrothundr, pointed this out under the video: the record holder lands the final blow about two seconds
before the AI did, so the AI could not be ahead at the end. He was right.

There had been a warning sign. In the comparison with the record, the AI's last level measured about eight seconds
*faster* than the record's. That was taken as good news. It was the bug.

## What was done about it

The end of the run was first pinned down on both sides: in the game's own code and memory, and on jay_cee's video, read
frame by frame. His 12:29.25 runs from the Level 1 landing to the cut to Professor T. Bird. Then the AI went looking for
the time it was missing, and kept going.

| what changed | saved | notes |
|---|---|---|
| Level 8, the climb | 9.2 s | searched again by landings instead of by frames; the old search had no way to duck under the sparks |
| Level 8, Robo-Manus | 7.6 s | only the jump-smash keeps him in place; which attack B gives is a dice roll that a Select press re-rolls |
| Level 12, the tower, second half | 7.8 s | the reference run's line with legal sprints (tap, release, hold) instead of Left+Right |
| Level 12, the tower, first half | 4.2 s | exactly one 256-frame cycle of the level's clock: the ledges after the first wind face are solid only part of each cycle |
| Level 9, the last shaft | 3.3 s | sprint under the propeller bugs instead of being carried down at one pixel a frame |
| Level 13, the Queen and the ending | 2.9 s | an all-smash juggle, and an ending whose last wait is steered with Select |
| Level 6, Karnath's Lair | 2.2 s | the record holder's own jump in the warp room, held up the snake at run speed |
| the pages between levels | 0.4 s | single presses on the first frame each page accepts |

Two of these (the shaft in Level 9 and the tower in Level 12) were pointed out by the channel's owner, watching the
published run back.

Published run, timed correctly: 12:31.75. This run: **11:54.02** (BizHawk's default core) / **11:54.16** (its accuracy
core). The record: 12:29.25.

## How it is checked now

- Every route is assembled from power-on and replayed twice; the memory at the end must be identical.
- The run time is counted from the landing to the *second* cut. A route whose inputs stop earlier gets no time.
- Before any number was repeated in public, a separate checker, told to assume the builders were wrong, replayed the
  input file with its own code, scanned every frame for banned presses, looked at pictures of both cuts (the Dark
  Queen's speech at the first, Professor T. Bird at the second), compared the levels visited with the record's video,
  and re-read the record's own video for the two clock events. Its report is in `verification/`.
- The route was then rebuilt on BizHawk's accuracy core (NesHawk) and played back there as a plain movie, hands-off.
- The released input files have no auto-fire. The 30-presses-a-second mashing on the between-level pages in the
  published run was cosmetic; removing it leaves every frame of the run identical.

## What it still is

A tool-assisted run under the human category's rules. It was built with save states and search, and it presses buttons
with single-frame precision. It is not a leaderboard run and no person could perform it.
