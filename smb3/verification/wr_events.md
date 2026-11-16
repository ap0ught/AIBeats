# WR 10:40.533 (MostDefinitelyAlbert): video frame of every milestone, in NES frames since the Start press

Source: `research/wr_splits.md` (frame-accurate picture boundaries of `dl/wr/wr_5ZzdW6FA8cA.mp4`, 59.94006 fps), checked again on the frame
sheets `dl/wr/frames/00_start_press_title_freeze_f19048-19059.png`, `00_title_cleared_map_fadein_f19100-19119.png`,
`99_end_door_entry_fade_f57424-57453.png`. Regenerate: `python -I work/wr_events_build.py > work/wr_events_table.txt; python -I work/wr_events_md.py`.
The table 'ours vs WR at every milestone' is printed by `python -I work/verify_run.py logs/<run>.inputs.txt` (it reads `work/wr_events.json`).

## Conversion

NES frames = video frames x 60.0988 / 59.94006 (1 video frame = 1.00265 NES frames). The capture is not locked to the emulator, so every
picture event is good to +/- 1 video frame.

## The two timing events

* **Start press = video frame 19050 (+/- 1).** It cannot be seen directly, so it is derived from the two pictures that follow it, with
  the delay measured in the emulator (`work/w7_start_delay.py`, NesHawk, Start pressed on 8 different frames: the title is cleared
  (blank cream picture) exactly 55 frames and the World 1 map is first visible exactly 67 frames after the Start press, every time).
  WR video: first full cream frame 19105 (19104 is a torn frame), map first visible 19117 ->
  19105 - 55 x 0.99735 = 19050.1 and 19117 - 67 x 0.99735 = 19050.2. `research/wr_splits.md` read 19052 +/- 2 off the frozen title
  sprites and LiveSplit's zero at 19051.5 +/- 1; the official time puts it at 19050.4. All agree within their error; 19050 is used here.
* **End = video frame 57444** = first darker picture of the fade after Mario enters the door behind Bowser (57449; 57448 is
  still at full brightness, checked on the sheet) minus 5, as the speedrun.com rule says. The runner's LiveSplit stops on 57449 at 10:40.60.
* **Total: 38394 video frames = 38495.7 NES frames = 640.540 s.** Official 10:40.533 = 38495.3 NES frames
  (38393.6 video frames). Difference +0.4 NES frames: it adds up. (The '38,494.6' in the brief does not come out of
  either product: 640.533 x 60.0988 = 38,495.3; the 0.7 does not matter.) With the older Start estimate 19052 the video gives 38,493.7.
* **Picture-to-picture check that needs no Start press:** World 1 map first visible (19117) -> first darker picture after the door
  (57449) = 38332 video frames = 38433.5 NES frames (+/- 1.4). In our run both pictures are read from NesHawk screenshots.

## The same events in our run (how `work/verify_run.py` finds them)

* Start press = the last new Start press in the first 400 rows of the file (row 68 in the rebuild files).
* MAP1 = first picture with more than 2 colours after the blank cream picture (NesHawk screenshot of every frame after the Start press).
* BLACK = first picture of a run of >= 3 all-black pictures; VISIBLE = first picture after it. One black stretch per transition;
  the WR table has one boundary per transition (its VISIBLE for map -> level, its BLACK for everything else), so they pair in order.
* End: row E on which `Level_ExitToMap` ($0014) becomes non-zero. The first darker picture is row E + 5 both ways it was measured
  (palette buffer $07C1-$07E0 changes on row E + 4 and is shown one row later; mean brightness of the NesHawk screenshot drops on row E + 5;
  4 of 4 level exits in the test file, and E + 5 in Bowser's room on Mesen in round 2). So the rule's end ('5 frames before the fade') is row E itself.
  The tool prints the fade row it SAW, it does not assume + 5.
* Time of our run = (E - Start row) / 60.0988 s. The record is beaten when E - Start row < 38,495 with a margin larger than the
  +/- 2 frames of the video reading (see the unsafe list in hr/NOTES_w8.md, Round 7).

## Table (NES frames since the Start press)

| # | boundary | kind | video frame | NES frames since Start |
|---|---|---|---|---|
| 1 | start of: W1 map: START tile -> enter 1-1 | MAP1 | 19117 | 67.2 |
| 2 | start of: 1-1 | VISIBLE | 19409 | 360.0 |
| 3 | start of: W1 map: 1-1 -> 1-2 | BLACK | 20720 | 1674.4 |
| 4 | start of: 1-2 | VISIBLE | 20930 | 1885.0 |
| 5 | start of: W1 map: 1-2 -> 1-3 | BLACK | 22171 | 3129.3 |
| 6 | start of: 1-3 (ends by running off behind the scenery) | VISIBLE | 22359 | 3317.8 |
| 7 | start of: 1-3 Toad House (whistle 1) | BLACK | 23472 | 4433.7 |
| 8 | start of: W1 map: Toad House -> 1-Fortress | BLACK | 24077 | 5040.3 |
| 9 | start of: 1-Fortress main room | VISIBLE | 24355 | 5319.0 |
| 10 | start of: 1-Fortress whistle room (whistle 2) | BLACK | 25079 | 6045.0 |
| 11 | start of: W1 map: whistle 1 used (after 1-F) | BLACK | 25431 | 6397.9 |
| 12 | start of: Warp Zone, 1st arrival: whistle 2 used | BLACK | 25750 | 6717.7 |
| 13 | start of: Warp Zone, 2nd arrival: into the World 8 pipe | BLACK | 26097 | 7065.7 |
| 14 | start of: W8 map 1: start -> enter 8-Tank | BLACK | 26316 | 7285.2 |
| 15 | start of: 8-Tank autoscroller | VISIBLE | 26614 | 7584.0 |
| 16 | start of: 8-Tank boss room (Boomerang Bro) | BLACK | 32509 | 13494.6 |
| 17 | start of: W8 map 1: 8-Tank -> enter 8-Navy | BLACK | 33102 | 14089.2 |
| 18 | start of: 8-Navy autoscroller | VISIBLE | 33292 | 14279.7 |
| 19 | start of: 8-Navy boss room (Boom Boom) | BLACK | 37809 | 18808.7 |
| 20 | start of: W8 map 1: 8-Navy -> pipe | BLACK | 38407 | 19408.3 |
| 21 | start of: W8 pipe connector 1 | VISIBLE | 38649 | 19650.9 |
| 22 | start of: W8 map 2: 3 hand tiles (no grab) -> enter 8-Airship | BLACK | 38845 | 19847.4 |
| 23 | start of: 8-Airship autoscroller | VISIBLE | 39066 | 20069.0 |
| 24 | start of: 8-Airship boss room (Boom Boom) | BLACK | 42019 | 23029.8 |
| 25 | start of: W8 map 2: Airship -> pipe | BLACK | 42620 | 23632.4 |
| 26 | start of: W8 pipe connector 2 | VISIBLE | 42845 | 23858.0 |
| 27 | start of: W8 map 3 (dark): -> enter 8-1 | BLACK | 43041 | 24054.5 |
| 28 | start of: 8-1 | VISIBLE | 43211 | 24225.0 |
| 29 | start of: W8 map 3: 8-1 -> 8-2 | BLACK | 44630 | 25647.7 |
| 30 | start of: 8-2 | VISIBLE | 44832 | 25850.3 |
| 31 | start of: W8 map 3: 8-2 -> 8-Fortress | BLACK | 46330 | 27352.2 |
| 32 | start of: 8-Fortress room 1 | VISIBLE | 46550 | 27572.8 |
| 33 | start of: 8-Fortress room 2 | BLACK | 46993 | 28017.0 |
| 34 | start of: 8-Fortress room 3 | BLACK | 47364 | 28389.0 |
| 35 | start of: 8-Fortress room 4 | BLACK | 47731 | 28757.0 |
| 36 | start of: 8-Fortress Boom Boom room | BLACK | 48018 | 29044.7 |
| 37 | start of: W8 map 3: 8-F -> pipe | BLACK | 48871 | 29900.0 |
| 38 | start of: W8 pipe connector 3 | VISIBLE | 49146 | 30175.7 |
| 39 | start of: W8 map 4: -> enter 8-Tank2 (Super Tank) | BLACK | 49342 | 30372.2 |
| 40 | start of: 8-Tank2 autoscroller | VISIBLE | 49489 | 30519.6 |
| 41 | start of: 8-Tank2 boss room (Boom Boom) | BLACK | 53435 | 34476.1 |
| 42 | start of: W8 map 4: Tank2 -> enter Bowser's Castle | BLACK | 54033 | 35075.6 |
| 43 | start of: Bowser's Castle room 1 | VISIBLE | 54361 | 35404.5 |
| 44 | start of: Bowser's Castle room 2 | BLACK | 54690 | 35734.4 |
| 45 | start of: Bowser's room -> end of run | BLACK | 55770 | 36817.2 |
| end | door entry after Bowser (first darker frame 57449 - 5) | END | 57444 | 38495.7 |
