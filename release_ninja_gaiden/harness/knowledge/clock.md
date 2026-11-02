# The run clock in RAM and on screen (Ninja Gaiden NES, Any%)

Board rule (`rules_verbatim.md`): "Timing starts when you gain control of Ryu." / "Timing ends when the timer reaches
000 after defeating the demon statue." The moderators timed the record from the first video frame where Ryu is
visible in 1-1 to the first video frame showing TIMER-000 (`record_notes.md`). Implementation: `ng/clock.py`.

Conventions: frame f = `emu.framecount()` after the frame; RAM of f = RAM after f; picture of f = the screenshot
taken after f, which shows the sprites in PPU OAM after f (checked: OAM after 175 holds Ryu and the picture of 175
shows him; OAM after 174 holds only sprite 0, the status-bar split, and the picture of 174 has no Ryu).

## START

`python tools/clock_evidence.py start` (power-on with `logs/intro_fastest.inputs.txt`, fresh launch):

| frame | `$33` | play loop | `$63`/`$62` | sprites in OAM (not counting sprite 0) | picture |
|---|---|---|---|---|---|
| 173 | $00 | no | 150 / 0 | 0 | 1-1 without Ryu |
| **174 = N** | **$97** | first | 149 / 60 | 0 | no Ryu |
| **175** | $97 | yes | 149 / 59 | 4-5 (Ryu) | **Ryu first visible** |

`shots/clock/start_173.png` ... `start_178.png`, strip `shots/clock/start_strip.png`.
START (as seen) = N + 1. The TAS 4751M replay has the same N = 174 (its intro presses are the same three frames).
Note: `$33` is sprite data; it is $97 at the control frame of 1-1 (and most stages) but $9A / $9B at 6-4b / 6-5, so
it is only used for 1-1. Control is real on N itself: the TAS holds Right on 174 and x goes 32.0 -> 33.128 after
frame 174 (`logs/tas4751.trace.csv`); the picture shows him from 175.

## END

`python tools/clock_evidence.py end ref4751/21_6-5_movie_end` (the TAS replay's state at its last input, 39,084,
the frame the demon's HP display reaches 0; then no input):

* The final tally takes `$63` down by 1 every 3 frames (`$D65A`: `$04BA` reload 2), after the ninpo.
* P = 39,525 = first frame with `$63 == 0` (`$6D == 21`, `$1FD == $D5`, the autosplitter's tally marker; it becomes
  $D6 at 39,528).
* The HUD does not show it yet: TIMER-001 is on screen at 39,524-39,529 and **TIMER-000 first at 39,530**
  (`shots/clock/end_timer_sheet.png`, one crop per frame 39,516-39,537). The digits change only every 6 frames
  (005 at 39,516, 003 at 39,518, 001 at 39,524, 000 at 39,530) - the record video's "odd values, 6 frames each".
* Why: the status bar is rebuilt one part per frame (`$F7FC`, `$3E` counts 5..0). On frames whose RAM has `$3E == 1`
  the PPU buffer `$0700` holds `03 A9 20 d d d`, the three timer digits at PPU $20A9; the NMI at the start of the next
  frame writes them, so they are in that next frame's picture. Traced: `$3E == 1` after 39,517 (buffer "003" ->
  picture 39,518), 39,523 ("001" -> 39,524), 39,529 ("000" -> 39,530).
* In the tally loop the HUD part is built (`$D5C3 JSR $F7FC`) before the timer is decremented (`$D5EC JSR $D65A`),
  so a `$3E == 1` frame equal to P still buffers "001": E = first frame **> P** with `$3E == 1`; END seen = E + 1.
  The offset END seen - P is therefore 2..7 frames depending on the HUD phase - a route can gain or lose up to 5
  frames of board time at the very end through the phase of `$3E`.

## Time

time = (END seen - START seen) / 60.0988 s. For the TAS replay: (39,530 - 175) / 60.0988 = 39,355 frames
= 654.85 s = 10:54.85 (RAM N..P = 39,351 frames). `assemble.py` prints both.
