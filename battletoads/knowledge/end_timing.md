# The end of the run: where the clock stops, what the ending costs, and how short it can be

Track END, 2026-10-09. Everything below was measured on the verified route `up14`, on 17 stored Dark Queen fights
replayed from their bookmarks, on debug-poked snapshots (probes only, never in a run), in the ROM's own code, and on
the record's video. Scripts: `end_*.py`; raw output: `logs/fix/`.

## 1. The mistake and the correct clock

| | frame | run time (landing = 2074) |
|---|---|---|
| landing in Level 1 (clock start, `$3B5` 5 -> 4) | 2,074 | 0 |
| 20th hit on the Queen | 46,032 | 12:11.43 |
| **last (21st) hit**: object 0x7e -> 0x46 | 46,085 | 12:12.31 |
| FIRST level byte 13 -> 254: cut to the **Dark Queen's speech** (what up14 was timed to) | 46,751 | 12:23.39 |
| back on the tower (A pressed on this frame) | 46,762 | |
| SECOND level byte 13 -> 254: cut to **Professor T. Bird** = end of the run | **47,253** | **12:31.75** |

- up14's real time is **12:31.75** = 45,179 frames, 2.50 s slower than the record (12:29.25 = 45,029 frames =
  T. Bird cut on frame 47,103 for a landing on 2074; to beat it the cut must be on **47,102 or earlier**, 47,100 to be
  safe against a one-frame reading difference, see section 5).
- On both cut frames the picture is the status bar on black; the next frame is fully black; the T. Bird picture appears
  10 frames after the cut (`end_black.py`). The record's video shows the same three steps.
- **Fixed in code:** `render_overlay.run_splits` (finish = second 13 -> 254; the first is kept as
  `run_splits.queen_speech_cut`, also `run_ends()`), `assemble.py` (prints `RUN TIME` from landing to the T. Bird cut,
  `queen_speech_cut` for reference, and `NOT FINISHED` when the inputs stop before the T. Bird cut). Backups:
  `render_overlay.backup_end.py`, `assemble.backup_end.py`.
- A route's last segment must now run to the T. Bird cut: `end_tail.py` builds it.

## 2. What the game does after the last hit (ROM bank 0, `$EB49-$EC0B` dead boss, `$D352-$D50B` Queen)

Queen = object slot 3 (`s`), tables are 15 bytes apart: id `$3C1+s`, height `$439+s`/`$42A+s`, whirl timer `$4ED+s`,
angle `$556+s`, angle step `$4DE+s`, phase `$5A1+s`, counter `$583+s` (= `$586`, the hit counter of the fight), mode
`$592+s`. Ending flag `$F4`.

| piece | frames | what decides it |
|---|---|---|
| flight | 154 - 180 | 9 frozen frames, then the dead Queen (0x46) is thrown up at 7 px/frame from the height she was hit at, falls to the floor (h 44), bounces once (camera shakes every 4th frame) and drops off the bottom. **154 if she is hit at h 44-51, +1 per 7 px above: 160 at h 87, 166 at h 130 (up14), 169 at h 153.** Table: `logs/fix/end_flight.json`. |
| countdown | 207 | `$583+s` set to 207 when she re-enters as 0x7e at x 128, height -15 (-13 after a floor kill); her first rise frame is 208 frames after the respawn |
| rise 1 | 171 or 172 | 1 px/frame while `$5A1+s` < 86, which counts odd-timer frames only: 171 if (`$0B` at the hit + flight) is even |
| stand | 122 | `$5A1+s` 86 -> 208; then `$F4` = 1 and **cut 1** (Queen's speech, level byte 254) |
| speech | 9 - 13 | frames until the speech screen first polls the pad: dice. A NEW press (`$2B|$2C` != 0: A, B, Select; Start also but it pauses the game afterwards) on that frame returns to the tower on that same frame. One frame is enough. A button held since before is not new: holding A never skips. |
| reload | 14 or 15 | frames until Level 13's timer runs again (dice / CPU time). 9 + 14 = 23 is the least seen, (9,15) and (10,14) are common |
| tower | 340 | 48 frames (`$5A1+s` 208 -> 256), second rise 172 frames (height 156 -> 328), stand 120 (the 121st stand frame is the first tick of the final wait); the rescued pair drops in meanwhile |
| **final wait** | **1 - 256** | **the game counts the Queen's whirl timer `$4ED+s` down to zero, then cuts to T. Bird (cut 2)** |

`frames(last hit -> T. Bird cut) = flight + 207 + rise1 + 122 + speech + reload + 340 + final wait`
up14: 166 + 207 + 171 + 122 + 11 + 14 + 340 + 137 = **1,168**.

### The final wait is the lottery ("the faster ending")
The whirl timer is the byte her whirlwind attack uses in the fight. It is frozen from the last hit to the first rise,
then ticks once per rise frame (343/344 rise frames in all). When it reaches zero it is reloaded:
- **height 0..127** (rise frames 15..142): random, `(rng$26 & 63) + 32 (+1)`, step `(rng$25 & 7) - 3 or 4`;
- **otherwise**: `|0xC0 - angle| / 2` with step +-2; her angle then sits on 0xC0, so the reload after that is **0, and a
  zero is not reloaded: the byte wraps to 255 and runs 256 frames.**

Let K = the rise frame on which that zero is loaded (the timer "parks"). Then `final wait = K + 84 - rise1` and

**`frames(last hit -> T. Bird cut) = flight + speech + reload + K + 753`** (= flight + K + 776 with 9 + 14)

K cannot be earlier than the first rise frame at height >= 128: **K >= 143** (141 after a floor kill). up14: K = 224.
- Fastest possible ending: 154 + 9 + 14 + 141 + 753 = **1,071 frames** (floor-level last hit, timer parked at once).
- With up14's last hit (Queen at h 130): 166 + 9 + 14 + 143 + 753 = **1,085**.
- Slowest: about 1,300 (hit high, final wait 256), +27 more if the toad stands in her way.
- Seen in the 17 stored fights, unsteered: 1,091 (L13w) to 1,244 (L13n). The record's run: about 1,172.

What the timer at the last hit (`a`) means, for angle 128 / step -2 (best case with the dice steered; `end_x4.py`):
`a` 1..78 -> final wait 56 (the floor) · 79..111 -> 56..64 · 112..142 -> 57..89 · 143 -> 102, 150 -> 116, 160 -> 136,
171..224 -> 137, 230 -> 148, 255 -> 198, 0 -> 200 (from 143 up there are no dice: the wait is decided at the last hit).
In the fight the timer only ticks while she whirls (up14: 3 while she hops, 43 when a whirl starts 17 frames before
the last hit, 27 at the hit).

### The dice can be steered - legally
`$25-$28` are scrambled in the idle loop, so any input earlier in the ending changes every later roll. The toad stays
controllable through the whole ending; Select does nothing else, Up/Down do nothing visible. One press on one frame
is a re-roll (`end_x2.py`: 30 Select frames gave timers 34..93, steps -3..4).

### The toad can ruin it
If the toad stands within about 25 px of x 128 when she rises (rise frames ~38-45, her height 23-25), her whirlwind
hits it three times: 27 frozen frames and a dead toad (L13d, L13n, L13w6, L13x1, L13y1: toad at x 112-150; safe at
x <= 96 and >= 170). `end_tail.py` walks it away during the flight if it is at x 96-160.

## 3. Tools

- **`end_model.py`** - the model. `predict(ram)` = the PREDICTOR: RAM of the frame the Queen's id turns 0x46 ->
  `best` (frames to the T. Bird cut with the best legal ending), `floor`, `flight`, `n1`, `a`, `theta`, `d`,
  `steerable`; with `natural=True` also the unsteered range. `simulate()` runs the timer; `FLIGHT` is the table.
  Checked: 11/11 stored endings without a toad collision and 28/28 poked last-hit states reproduce to the frame
  (`end_check.py`, `end_x4.py`, `logs/fix/end_x4.tsv`).
  **T. Bird cut frame = last-hit frame + predict(ram)["best"].** For a fight search: minimise that, not the hit frame.
  Against up14's last hit a floor-level one is worth 14 frames (flight 154 instead of 166, and the timer can park 2
  frames sooner); a timer of 143 or more at the hit costs 46 to 144 frames against one below 112.
- **`end_tail.py <L13 segment> <out> [--steer seconds] [--route R --state S --frame N]`** - finds the last hit, appends
  the tail and writes `logs/pbeam_<out>.json` (fight to the last hit + tail to the T. Bird cut + 30 idle frames, with
  an `end` block). Plain: nothing, one A on the first frame the speech takes it, nothing. `--steer`: single-frame
  Select/Up/Down presses searched so the timer parks at K = 143 and the speech/reload take 9 + 14; needs under 2
  minutes. Class `Ending` for use on a live emulator. Always a fresh `<out>`; verify with `assemble.py`.
- Probes: `end_var.py` (17 fights), `end_flight.py` (height -> flight), `end_skip.py` / `end_x3.py` (speech),
  `end_x2.py` (dice vs inputs), `end_x4.py` (predictor vs game), `end_black.py`, `end_cap.py`, `end_an.py`, `end_ev.py`.

## 4. Results

| route / fight | last hit | Queen's speech cut | T. Bird cut | tail | time |
|---|---|---|---|---|---|
| up14 as published (plain tail) | 46,085 | 46,751 | 47,253 | 1,168 | 12:31.75 |
| **up14e** = up14 + steered ending (`L13y0E2`), **verified from power-on**: 47,200 frames, replay MATCH sha1 a1b291b6, 0 banned presses | 46,085 | 46,751 | **47,170** | **1,085** | **12:30.36** |
| floor-kill demonstration: old fight `L13w` + steered ending (`L13wE`, from its bookmark, not a route) | - | - | - | **1,071** | - |
| toad-in-the-way demonstration: old fight `L13d` (plain ending 1,173: the rising Queen kills the toad) + walk away + steered ending (`L13dE`) | - | - | - | 1,080 | - |
| the record (video) | 45,930 equiv. | 46,582 equiv. | 47,101 equiv. | ~1,172 | 12:29.25 |

up14e's ending inputs (route frames): Down 46,468 · Up 46,511 · Up 46,525 (timer rolls 83 then 33 and parks on rise
frame 143) · Down 46,744 (speech polls on its 9th frame, reload 14) · A 46,760 · nothing. Final wait 56 instead of 137.

Segments: `pbeam_L13y0P` = up14's fight + the plain tail (T. Bird cut 47,253, one A on frame 46,762); `pbeam_L13y0E2` = the
steered one used in up14e (`pbeam_L13y0E` is a first attempt, 1 frame slower); capture `video/up14e.mkv`, trace
`logs/up14e.trace.txt`; `logs/fix/assemble_up14e.txt`, `logs/fix/end_tail_*.txt`.

**Frames saved by the best ending against up14's 1,168-frame tail: 83 with up14's own last hit (verified), 97 with a
floor-level last hit (the bound; demonstrated on L13w).** The route still needs the T. Bird cut 68 frames earlier than
up14e's 47,170 to beat the record (47,102), 130 for a one-second margin (47,040): 14 of those are in the flight (kill
her on the floor), the rest must come from before the last hit.

## 5. The record's own ending (jay_cee, youtube A7czTlY7OI0, 60.00 fps; `knowledge/wr_final.json`)

| event | video frame | video s | run s (landing clock) | our-frame equivalent |
|---|---|---|---|---|
| landing in Level 1 (scroll stops) | 1,249 | 20.817 | 0 | 2,074 |
| Level 12's first black frame | 43,639 | 727.317 | 706.50 | 44,534 |
| final blow (10 identical pictures 45,032-45,041) | 45,032.5 | 750.54 | 729.72 = 12:09.7 | 45,930 |
| cut to the Queen's speech | 45,684 | 761.400 | 740.58 = 12:20.6 | 46,582 |
| back on the tower (from the fade steps) | 45,694 | 761.57 | 740.75 | 46,592 |
| **cut to Professor T. Bird** | **46,202** | **770.033** | **749.22** | **47,101** |

- **749.25 s IS the T. Bird cut.** 749.250 x 60 = 44,955 video frames exactly; our event definitions give 44,953
  (the board's retime is one frame wider at each end). The Queen's-speech cut is 8.6 s earlier.
- His tail, final blow -> T. Bird cut: 1,169.5 video frames = **1,171 NES frames (+-1.5)** - 3 frames LONGER than
  up14's. He kills her on the floor (first camera shake 100 frames after the blow = flight 154, 12 less than ours),
  leaves the speech after about 10 frames, and then waits about 155 frames on the timer (ours 137). There is no trick
  in his ending; he was 155 frames ahead at the final blow (12:09.7 against our 12:12.3) and 152 at the cut.
- Level 13 for him, first black to final blow: 1,396 frames; up14: 1,028 (level byte 13 to last hit). We arrive about
  523 frames behind and win about 368 in the fight.
- Journal 014's "run time = video time - 20.69 s" is 0.12 s off: the landing is at 20.817 s (video frame 1,249; the
  horizon scrolls 2 px/frame, then 1 px/frame for 46 frames, and stops on the landing frame - identical in our
  capture). `knowledge/wr_splits.json` therefore reads its level ends about 7 frames late (not its total).

## 6. Limits of what was done

- "Delay the last hit by k frames" was not done by re-timing the blow (that needs a fight search); instead the last-hit
  frame's own variables (timer, angle, step, height) were overwritten on a snapshot and the game's ending compared
  with the model, on top of the 17 real fights.
- The record's frames are read off a 60.00 fps video: each event +-1 frame, his tail +-1.5.
- The steered ending depends on the dice like every re-rolled level of the route: it is verified on BizHawk 2.11.1's
  default NES core (QuickNes), twice from power-on, and has to be re-steered (2 minutes, `end_tail.py --steer`) whenever
  anything before the last hit changes.
- Lower floors not found: the speech + reload never came out under 9 + 14 frames in about 130 tries; the final wait
  cannot go under 54-56 because the timer can only park at height >= 128; no input shortens the flight, the countdown,
  the rises or the stands.
