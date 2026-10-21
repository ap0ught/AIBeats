# Reference run - what exists, what does not, and exactly what was changed (day 1, 2026-10-11)

**Bottom line: no published TAS syncs on this ROM/emulator, and there is no reference run through the whole game yet.**
What exists: a verified run from power-on through all of stage 1 to the first frame of stage 2, and fitted TAS stages
5 and 8 that start from debug stage states. The bases (stages 2 and 4) are the blocker. Nothing below is a claim
against the record.

Emulator: BizHawk 2.11.1 / NesHawk. ROM: `Contra (USA).nes`, CRC32 C50A8304.

## 1. The movies (downloaded to `dl/tas/`, parsed as data with `python -I tools/tas_convert.py`)

| tasvideos | authors | ROM | emulator | frames | converted to |
|---|---|---|---|---|---|
| 4623M (current "1 player") | Mars608 & aiqiyou | **Contra (Japan)** | FCEUX 2.2.2 (.fm2) | 31,745 | `logs/tas_4623M_raw.inputs.txt` |
| 4504M (previous) | alex_ik | **Contra (Japan)** | FCEUX 2.3.0 (.fm2) | 31,771 | `logs/tas_4504M_raw.inputs.txt` |
| 114M (last US-ROM "1 player", 2004) | Genisto | Contra (U) | Famtasia 5.1 (.fmv) | 34,447 | `logs/tas_114M_raw.inputs.txt` |

The task said "the current and previous 1-player publications of the US ROM"; the current and previous 1-player
publications are both on the **Japanese** ROM (every NES Contra publication since 2007 is). 114M is the newest US-ROM one,
so I fetched it too (same site, same approval). All three use controller 1 only and contain no reset.

Their inputs (measured with `check_inputs.py` / `tas_convert.py`; all three FAIL our input rules, as expected):

| movie | B presses | of which 1 frame long | fastest second | closest two B presses | Left+Right frames | Up+Down frames | Start presses |
|---|---|---|---|---|---|---|---|
| 4623M | 2,773 | 2,773 | 28 | 2 frames (30 per second) | 2 (24215, 24219) | 10 | 25 (of which 4 in-level pauses, Start twice 2 frames apart: 22476, 22507 in stage 6; 25965, 27564 in stage 7) |
| 4504M | 2,856 | 2,856 | 27 | 2 frames | 5 | 0 | 23 |
| 114M | 2,905 | 2,826 | 30 | 2 frames | 10 | 0 | 1 |

Our cap (default: one press per 4 frames = 15 per second, hold >= 2, release >= 2) is half their B rate, and every
one of their presses is too short.

## 2. Why none of them simply replays

1. **Luck.** `$34` is advanced by the CPU's idle loop, so it depends on exact CPU timing: it is different on every
   emulator (NesHawk vs quickerNES differ from frame 12) and on the other ROM. Running soldiers, turret fire etc. differ.
2. **Lost presses.** NesHawk emulates the console's DMC/controller conflict; the game then ignores the pad for a frame.
   FCEUX/Famtasia movies fire with one-frame B presses; a few per stage vanish (3 during the stage-8 first boss).
3. **Different ROM.** The Japanese ROM has map screens instead of score screens (so the frame counter is at a
   different value in every stage: anything keyed to it - "frame rules", flame jets - is out of phase), and its
   bases behave differently: its movies kill the first base core with shots that, on the US ROM, arrive about
   16 frames before the core can be hit (US: hittable 258 frames after the room loads - measured).
4. **Bosses come up short.** With the movie's shots alone the US bosses survive (stage 1 wall, stage 8 first boss:
   9 HP left of 102; the heart too).
5. **Famtasia (114M).** With the opening shifted by one frame (NesHawk needs Select on 11, Start on 12; the movie has
   10/11) it runs stage 1 without dying up to the boss wall but arrives with the wrong weapon (`$10`, Rapid only) and
   cannot kill the boss (32 -> 23 HP). Offsets -3..+7 tried on quickerNES, 0..+3 on NesHawk: all others die
   earlier or fall into the attract demo.

Plain offset searches: 4504M and 4623M at 19 alignments each for stage 1 (none survives; best 1,917 / 2,095 frames).

## 3. The fitting method (`contra/resync.py`, `tools/repair.py`, `tools/build_ref.py`)

Per stage, from a savestate one frame before the stage's first playable frame L:

* **Alignment m** = the movie frame applied on L. Stage 1: the movie's one-frame Right press at its frame 451 must be on
  L+2, the first frame a direction has an effect during the drop-in (measured) -> m = 449. Stage 5 and 8 (Right simply
  held): scan; the movie's last Start press + 49 worked (15048, 28798).
* **Lost-press compensation**: a button sent but missing from `$F1` after the frame is pressed again on the next frame.
* **Repair loop**: play until death / fence stun / 1,800 frames without progress / the movie running out; then try
  small edits before the failure and keep the one that gets furthest:
  `B+` one extra B frame (re-rolls the luck for free), `P k` a pause of k frames (re-rolls luck, shifts the frame
  counter), `loop`/`cyc` repeat the movie's own last 48-96 rows (more boss damage; `cyc` tries every resume point
  within 12 frames of the boss's HP reaching 0), `loopwait` keep shooting until a base fence is down, `dup`/`del`/`A+`.
* When the stage ends, the rows really sent are replayed open-loop from the stage state as a check.

Every kept edit is in the stage's `seg.json` ("edits", in order; row numbers count from L, after earlier edits).

## 4. What was fitted

### Stage 1 - from power-on, verified (`logs/ref_stage1.inputs.txt`, 4,620 rows)

`python assemble.py ref_stage1 logs/open_nh.inputs.txt logs/ref/s1.seg.json blank:242 blank:60`
-> two power-on replays MATCH (RAM SHA-1 b6b87cc680a0..., trace SHA-1 41dd121319a5...).

* Opening: nothing but Select on frame 11 and Start on frame 12 (the earliest frames the title accepts them on NesHawk).
* Movie 4623M from its frame 449, edits: `B+` at row 1382, `P 4` at row 3090, `loop 96 x 2` at row 3226 (192 extra
  frames of the movie's own boss pattern), 37 rows changed by lost-press compensation.
* Frames (emulator frame numbers): stage 1 first frame **591** (medals seen on **592** = clock START), boss defeated 3836,
  control lost 3999, level byte changes 4319, stage 2 first frame **4562**.
  **Stage 1 = 3,971 frames, 17 lag frames** (1 in the level - the frame the boss is destroyed - and 16 while stage 2
  loads). Weapon at the end `$13` (Spread + Rapid), lives 3, no death. 7 play frames on which the game ignored the pad.
* This is NOT the TAS's stage 1: an earlier fit with other edits (`logs/ref_mars/s1.seg.json`, 4 x `B+`) reached the
  level change 56 frames sooner (4263), and the movie on its own ROM takes at most 3,636 frames from its frame 449 to
  its next map screen. The reference is an upper bound only loosely; the boss fight is where the frames go.
* Bookmarks: `states/ref_s1.State` (frame 591), `states/ref_s1_boss.State` (3836), `states/ref_s2.State` (4562);
  `states/ref/s1_f590.State` and `states/ref/s2_pre.State` are one frame before each stage's first frame.

### Stages 5 and 8 - from DEBUG stage states (stage and weapon written into RAM; `tools/mk_stage_state.py`)

Per-stage facts about the fitted movie, not parts of a run (the frame counter and luck a real run brings into the
stage are different). Weapon assumed `$13`, 2 spare lives. `logs/dbg/stage_report.json`, `logs/dbg/mars_s<k>.seg.json`.

| stage | state (L) | m | edits | boss defeated | control lost (A) | level byte change | next stage's first frame | lag (level + load) | notes |
|---|---|---|---|---|---|---|---|---|---|
| 5 | `dbg/s5_pre` (591) | 15048 | `P 5`@1609, `P 6`@3066, `B+`@3423, `P 7`@4185 | L+5438 | L+5488 | L+5771 | **L+6027** | 0 + 13 | no death; 6 ignored-pad frames |
| 8 | `dbg/s8_pre` (591) | 28798 | `cyc 15`@702 (first boss), `P 6`@1937, `B+`@2547, `cyc 66`@2969 (the movie ends with the heart alive), then Up held | L+3034 | L+3258 | L+3580 | - | 2 + - | **END: RAM frame L+3259, seen L+3260**; 12 ignored-pad frames |

For scale only: the movie's own stage 5 is 5,806 frames from stage start to stage start on the Japanese ROM.

### Not fitted

* **Stage 2 (base 1).** Rooms 1-3 were passed with waits of 3, 17 and 144 frames; room 4 kills Bill while he waits for
  the fence (in the movie's game the room is already cleared and its bullets are gone). Wrong tool for the job: the
  bases need their own driver (stand under the core's X, fire when it is hittable, Up on the frame after `$37` reads
  `$80`, and again on the frame after each of the 4 walk-in steps) rather than a Japanese movie. Facts for that driver
  are in `ram_notes.md` (items 3, 4) and `code_enemies_bosses.md`. **No base-room savestates exist.**
* **Stage 4 (base 2)**: not attempted (same problem).
* **Stage 6**: from a debug state the movie dies at flame jets at the same emulator frames whatever the alignment; a
  frame-counter phase scan (pauses of 2-64 frames, `tools/phase_scan.py`) gets at most to screen 5. Not fitted.
* **Stage 3** (from a debug state, m = 7327): stuck at screen 5.2 of the climb after 10 repair rounds (6 minutes) -
  Bill falls off the bottom of the screen whatever is tried. Likely cause (not proven): the movie's jumps rely on the
  Y sub-pixel accumulator `$94`, which is never cleared and so is not what the movie had when it got there. Stopped.
* **Stage 7**: only the alignment scan was run (16 alignments, m = 24630..24645): every one dies at the same emulator
  frame (1034, screen 1.104) - a hazard keyed to absolute time, i.e. the frame-counter phase again. No fit attempted.
* Debug stage-start states exist for every stage: `states/dbg/s2_pre` ... `s8_pre` (first playable frame = 578, 573,
  578, 591, 591, 591, 591 for stages 2-8; weapon `$13`). They are for studying a stage, never for a run.

## 5. The time under the leaderboard rule

**There is none**: no run reaches the END event from power-on. What is measured:

* START (real run): RAM frame 591, seen frame 592.
* Stage 1 (real run): 3,971 frames = 66.07 s at 60.0988.
* Stage 5 (debug state): 6,027 frames = 100.28 s. Stage 8 to the END event (debug state): 3,259 frames = 54.23 s.
* The movie itself: 31,745 frames power-on to last input on the Japanese ROM; its timing rule (power-on to last input)
  and its ROM are both different from the leaderboard's, so that number must not be compared with 9:48.183.

## 6. What I would do next

1. A base-room driver (above), then stage 2 and stage 4 from real states; save `ref_s2_room<r>` states as it goes.
2. Chain the outdoor stages from real states with `tools/build_ref.py` (the frame counter each stage starts with then
   is the real one; stage 6 and 7 will still need the phase/pause search).
3. Or drop the TAS as a source of inputs and keep it as a source of routes and per-stage targets: under a 15-per-second
   press cap a TAS's inputs are not usable anyway.
