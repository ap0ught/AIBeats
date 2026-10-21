# Stage 8 (Alien's Lair) - builder's notes

Emulator: BizHawk 2.11.1 / NesHawk. Development state: `states/dbg/s8_pre` (debug: stage and weapon `$13` written
into RAM by `tools/mk_stage_state.py`; first frame L = 591, frame counter 62 at L). Nothing below is part of a run
from power-on. Files: `contra/stages/s8.py` (solver), `contra/stages/s3s8_engine.py` (savestate lookahead engine),
`contra/stages/s3s8_lib.py` (input-rule bookkeeping), `tools/s8_*.py`, `knowledge/s8_map.json` (collision map from a
debug fly-through), `logs/s8_ref_trace.txt` (the fitted TAS segment `logs/dbg/mars_s8.seg.json`, traced row by row).

## 1. Result

Best legal segment: **`logs/s8/best.inputs.txt` / `.seg.json` (= run v5): 3,266 rows, first frame to END = 3,265
frames; the record's stage 8 is 3,273 (8 frames ahead).** Replayed open-loop from the state by the solver's own
check: same END frame, 1 lag frame (row 1816), 13 frames on which the game ignored the pad (harmless: every press
is held 2 frames), no death, weapon out `$13`. `check_inputs.py` at its defaults: PASS. END follows
`contra/clock.py`: A = first frame with `$2C` = 9 (row 3264), P = A + 1 with Bill prone -> standing (Down held).

Timeline in rows from the stage's first frame (row r produces frame L + r), against the record (video frames
after the medals x 1.00165) and the fitted TAS (30 presses per second, not legal for us):

| event | ours (v5) | record | fitted TAS |
|---|---|---|---|
| alien guardian appears | 517 | 521 | 514 |
| guardian HP 0 | 771 (254 after it appeared) | 795 (first explosion) | 721 (207) |
| boss scroll starts (screen 9 offset `$A0`) | 2,829 | not measured | 2,784 |
| heart: boss flag set | 3,039 (210 after the scroll start) | 3,050 (first explosion) | 3,034 (the fit's filler) |
| control lost (A) | 3,264 | | 3,258 |
| END (P) | **3,265** | **3,273** | 3,259 |

Earlier legal runs: v3 = 3,295 (no Barrier, firing through the ending: 17 lag frames in the 60 frames after
the heart's death), kept as `logs/s8/best_legal_v3.*`.

## 2. The stage as measured

* Horizontal, 10 screens; scroll starts when Bill reaches X 128, 1 px per frame at best, a jump costs 1 frame.
  The boss scroll (96 frames) starts at screen 9 offset `$A0` (world position 2,464); after it the level stands
  still at screen 10 offset 0 and Bill is stopped by a wall at X 152.
* Terrain jumps of the fitted TAS (world X = screen*256 + offset + X at the A press): 98, 224, 309, 383, 490
  before the guardian; 799, 1009, 1066, 1138, 1255, 1602, 1678, 1782, 2588 after it. The solver schedules a jump at
  each of these ("hints") and repairs around them by lookahead.
* Alien guardian (type `$10`): created at world position 432 with **HP 103** (Spread held), then a 64-frame forced
  scroll. A solid wall (world X 624-655, top at Y 128) stands in front of it; bullets pass through walls in this
  stage. Its bullet box is X +-28, Y +-18 around (176, 96): from the floor (Y 180) only up-right shots reach it,
  and they arrive fastest from the top of a jump. Measured: a jump with Up+Right held and B at the legal cadence
  takes 25-30 HP per 60-frame jump (0.45-0.5 HP per frame); standing it is under 0.15. The wall opens about
  70 frames after the HP reaches 0 (ours: HP 0 at 771, moving again at about 842).
* Heart (type `$16`): created 48 frames into the boss scroll at X 240, **HP 103**, stops at X 192. Its box is above
  the floor line: it is shot from jumps at the wall (X 152), flat or up-right. Measured: 49 HP in one 60-frame
  jump at point blank (0.8 HP per frame); 25 HP in the 111 frames before Bill gets there.
* After the heart's HP reaches 0: boss flag on the next frame, `$2C` = 9 exactly 224 frames after the flag when no
  frame lags (ours: flag 3,040, A 3,264). The spiders stay alive for about 100 of those frames and kill a prone
  Bill; every bullet fired during the explosions makes lag (17 lag frames in 60 when firing on). The solver
  dodges without firing and goes prone from 110 frames after the flag.

## 3. The ideas that were to be tested

(a) **Barrier.** The capsule pair of screen 0 (M at Y 48, Barrier at Y 192) is created at world position 64. The
    solver shoots the Barrier capsule down-right from the platform at world X about 440 and takes the item in the
    next jump (hill climbing, found within 24 trials, costs no frame: spawn row 517 with it, 518 without). It
    then protects through the pits and mouths up to about row 1,540.
    **Touching the guardian with the Barrier destroys it outright - but the spot cannot be reached.**
    Debug experiment (`tools/s8_barrier_touch.py`, RAM pokes, not part of any run): Bill placed inside the
    guardian's box with the Barrier timer set: its HP went 102 -> 0 and its routine to "destroyed" on that very
    frame; the same without the Barrier: Bill dies. So the kill is real. Geometry: the box (code notes: X
    `$93`-`$CC`, Y `$49`-`$6E` for a jumping Bill; a standing or falling Bill is tested with a taller box) lies
    above the wall, i.e. Bill would have to be on top of the wall (standing Y 116, world X 624-655). A jump from
    the floor in front of it peaks at Y 121 (floor 180, rise 59; a landing 64 px up needs a rise of 67); the
    higher platform (Y 148) ends at world X 527, 97 px away, and a jump from it to that height lasts 48 frames
    at 1 px per frame; the upper platform (Y 100) ends at world X 463. No way up was found. Prize if someone finds
    one: about 250 frames (the 254-frame fight becomes one touch).
(b) **A weaker weapon for less boss HP: not tried in the emulator.** From the measured rates: with Spread the
    guardian takes 254 frames for 103 HP and the heart about 115 frames at the wall. The default gun gives one
    bullet per press, 12 per second = at most 0.2 HP per frame, so 55 HP would take at least 275 frames per boss
    even if every bullet hit - slower on both bosses before counting the rest of the stage without Spread. This
    is arithmetic from measured Spread rates, not a measured default-gun fight.
(c) **Spread after a low-HP spawn: no.** The only S capsule of the stage appears at world position 992, after the
    guardian (432); HP is latched on a boss's first frame (read: 103 on the frame the slot appears). For the heart
    one would have to carry a weaker gun through 1,470 px and the heart screen has no S. Not tried.

## 4. How the solver works, and what is random

* P1/P3 (running): Right held, B at the legal cadence (2 on, 3 off), jumps at the hinted positions. A lookahead
  of 260 frames finds deaths, stalls against a step and weapon pick-ups (the M capsule!); candidates (aim Up /
  Down windows, a jump 1-75 frames earlier, short stops, double jumps) are simulated from a checkpoint and the one
  with the most progress is kept. A coordinate descent then moves each jump by +-3 rows (P1: 519 -> 518).
* P2/P4 (bosses): one jump at a time. From the checkpoint every candidate (wait 0-5 frames, B phase, aim per third
  of the jump: up-right / flat / down) is simulated to its landing; the best damage per row is committed. The
  first segment starts 80 rows before the boss appears and gets credit for bullets still in flight.
* P5: lookahead survival without firing, Down held from flag + 110.
* Random: the wadders' blobs and the spiders depend on `$34`; any change of firing changes them. The repairs are
  recomputed from the state, so nothing is replayed blindly. Lag: 1 frame in the whole stage when the ending
  is not fired through.

## 5. Start conditions

Debug states made by `tools/s3_mkvariants.py 8 1,37` (the opening waits k frames on the title screen), each solved
from scratch by `python -m contra.stages.s8 <state>`:

| state | `$1A` / `$34` at L | first frame to END | guardian appears / HP 0 | boss scroll | heart flag | lag | ignored pad | Barrier | wall time |
|---|---|---|---|---|---|---|---|---|---|
| `dbg/s8_pre` (k = 0) | 62 / 159 | **3,265** | 517 / 771 | 2,829 | 3,039 | 1 | 13 | taken | 34 min (2 emulators) |
| `s8/var1_pre` | 62 / 21 | **3,267** | 517 / 772 | 2,830 | 3,040 | 2 | 21 | taken | 28 min |
| `s8/var37_pre` | 98 / 134 | **3,264** | 517 / 770 | 2,828 | 3,038 | 2 | 13 | taken | 15 min |

Spread 3 frames; all three: no death, weapon `$13`, 0 rule violations, `check_inputs.py` PASS
(`logs/s8/var1.*`, `logs/s8/var37.*`), END replay-checked on a fresh emulator. One run needed the deepest repair
level (443 candidates) at world X 1,645 after the Barrier ran out.

## 6. What failed or was dropped

* A generic hill climb over jump / aim overrides for the bosses stalled at 292 rows for the guardian; the
  jump-by-jump greedy replaced it (254).
* Without hints the lookahead needed double-jump searches (443 candidates each) at the pits near world X 300 and
  1,050; with hints but without the Barrier one run (v4) got stuck at world X 996-1,110.
* The fitted TAS's own inputs are useless under the cap (2,773 one-frame B presses); only its jump positions were
  taken.

## 7. Floors and remaining ideas

* Scrolling: 2,464 px at 1 px per frame + 80 frames to reach the scroll column + one frame per jump (14 here) is
  about 2,560 frames outside the guardian's wall; ours is 2,829 - (842 - 517) = 2,504 + the wall wait.
* Guardian: 103 HP at the measured 0.5 HP per frame = 206 frames + 70 for the wall; ours 254 + 71. The approach
  (bullets fired from the platform jump before it appears) is worth about 20 HP and we get 19. Remaining: about
  20-30 frames with a better first jump at the wall.
* Heart: created at scroll + 48; floor = 48 + 103 = 151 frames after the scroll start if every frame hit; ours
  210, the record about 195 (inferred), the point-blank rate measured 0.8 HP per frame. Remaining: 15-30 frames
  (land at the wall on the frame the scroll ends, flat shots during the scroll from the right height).
* Ending: 225 frames, fixed.

## 8. Second pass (2026-10-12) - what was tried, what it measured, what was kept

All measurements from the same debug start states as section 5. Files added: `contra/stages/s3s8_fight.py` (boss
beam search + pellet prediction + a row-level polish), `tools/s8_pellets.py` (per-frame pellet-fate log of a
finished fight), `tools/s8_beam_dev.py`, `tools/s8_polish_dev.py`, `tools/s8_barrier_search.py`,
`tools/s8_noprogress.py`, `tools/s8_timing.py`; `contra/stages/s8.py.backup_pass1` is the first builder's solver.

### 8.1 Result

| state | first pass | second pass | guardian HP 0 after its spawn | boss scroll | heart HP 0 after the scroll start | lag | solve time |
|---|---|---|---|---|---|---|---|
| `dbg/s8_pre` | 3,265 | **3,242** (`logs/s8/p2_v1.*`) | 232 (was 254) | 2,810 | 206 (was 210) | 4 | 25 min on 2 emulators (17 on 3) |
| `s8/var1_pre` | 3,267 | **3,237** (`logs/s8/p2_var1.*`) | 227 (was 255) | 2,805 | 206 (was 210) | 3 | 25 min on 2 |
| `s8/var37_pre` | 3,264 | **3,248** (`logs/s8/p2_var37.*`) | 230 (was 253) | 2,812 | 209 (was 210) | 4 | 30 min on 2 |

Record 3,273. All three: no death, weapon out `$13`, 0 rule violations, `check_inputs.py` PASS, END with Down held
(A = flag + 224, P = A + 1), and the solver's own open-loop replay on a fresh emulator gives the same END frame.

### 8.2 Why the bosses take 0.5 and 0.85 HP per frame (measured with `tools/s8_pellets.py`)

* One hit per enemy per frame, and a hit pellet's slot stays busy 6 more frames (the slot is free again 7 rows
  after the hit); a miss holds its slot until it leaves the screen (30-45 frames). Spread has 10 slots and a
  press makes only as many pellets as there are free slots (order: centre, +11, -11, +22, -22 degrees). **The
  press cap is not what limits the damage: the slots are.** Rate = 10 / (flight + 7 + the wait for the next
  press), so everything depends on the flight time, i.e. on how far the muzzle is from the boss's bullet box.
* Bullet boxes as hit in the emulator: guardian X 149..204, Y 79..114 (code 8 around (176, 96), +1 from the
  carry); heart X 166..221, Y 85..140 (code 7 around (193, 112)).
* Guardian: Bill cannot get closer than X 119 (the wall: `check_player_solid_bg_collision` tests the column X + 8
  from Y - 11 down 27 px, the wall's top cell starts at Y 128, so the side only lets him pass at Y <= 112 and the
  jump peaks at Y 121). Jumping muzzle (up-right) = (134, Y - 15): 15 px left of the box. Near the top of the jump
  the four flatter pellets arrive after 5-8 frames (the 67-degree one passes above the box unless Bill's Y >= 129);
  in the lowest third of the jump they need 11-20 frames and the two flat ones miss. Measured in the first
  pass's fight: 126 pellets in 254 frames, 108 hits, mean flight 10.1, mean slot life 16.1 -> a slot comes back on
  the 4th press -> 0.5 HP/frame. In a beam fight: 28 hits in the 41 frames around the top of a jump (0.68), 5 in
  the 20 lowest (0.25). The fitted 30-presses-a-
  second TAS needs 207 frames after the spawn for the same reason; ours is now 227-232 at 12 presses a second.
* Heart: at the wall (X 152) the up-right muzzle (167, Y - 15) is INSIDE the box while Bill's Y <= 155 (46 of the
  60 frames of a jump): pellets hit on consecutive frames from the press frame; slot life about 9-12 -> 0.9
  HP/frame at best; measured 0.87 (first pass) and 0.81-0.85 (beam) from the wall to the kill. The loss is before that: the heart exists from scroll + 47 but Bill is held at
  X 128 until the scroll ends (+96) and reaches the wall at +121; until then the muzzle is 69 -> 0 px from the box
  and diagonal pellets close at only 2.5 px/frame. First pass: 26 HP before the wall; beam: 33.
* Pellets absorbed by other enemies (fetuses, spiders) are marked in the log; they are few and were not counted
  exactly.

### 8.3 Kept

* **Boss beam search** (`s3s8_fight.beam_fight`, used by `s8.beam_boss` for both bosses; the old jump-by-jump
  greedy is the fallback, `--nobeam` forces it). 5-row layers; per layer: no press, or a press on any legal row
  with aim up-right or flat; the first jump's row is a choice and a stratum of the beam, later jumps are taken on
  the landing row; ranking = boss HP minus the pellets a straight-line prediction puts into the box (the boss's
  future position is known from the level data, so pellets can be in flight for its first frame). Every child
  is played in the emulator; a wipe-out goes back 5 layers with jumps free. Two beams per boss (jump rows on
  different phases), the earlier kill wins. Guardian: 254 -> 227-232 frames after the spawn (-22..-28); heart:
  210 -> 206-209 after the scroll start (-1..-4). 2 minutes per beam on 3 emulators.
* **Lag repair in the running sections** (`run_phase`, `delag`): a lag frame inside the part about to be committed
  is tried with the presses of the previous 6-60 rows left out; kept when the lag frame goes and nothing dies in
  the horizon. Removed 1 lag frame per run; 3-4 remain (old runs had 1-2; the count depends on the enemies).

### 8.4 Tried, did not pay

* **Barrier touch on the guardian: no legal way (searched, `tools/s8_barrier_search.py`, 159 schedules, no shot
  fired so any HP loss would be a touch):** first jump on every second row of the 150 before and after the spawn,
  later jumps on landing, with / without Right released after the A press (changes `$94` and X), with stops of
  10-40 rows. Guardian HP never changed. Smallest Y at the wall's face 121 (needs <= 112: 9 px short, not 2: the
  "2 px" was for landing on the wall's top, but the side is tested 27 px deep); largest world X reached at
  Y <= 112: 590 (the wall's side is at 616, the guardian's box starts at 643). Nothing on that screen moves Bill
  faster than 1 px/frame or carries him, and the upper platforms end 73 and 137 px before the wall.
* A row-level hill climb on the finished guardian fight (`s3s8_fight.polish_rows`: a press dropped or moved,
  aim flipped, a jump moved): 150 trials, no earlier kill. Not wired in.
* Wider beams: guardian W 8 / 16 / 32 -> kill row 768 (W 8, before stratifying by the first jump) / 747 / 749;
  heart W 16 / 32 -> the same row. The limit is the geometry above, not the search width.
* A ranking that charges for busy slots (`slot_value`) was tried on the stage 3 dragon and made the beam stop
  firing; it is 0 for the stage 8 bosses.

### 8.5 What is left (estimates)

* Running sections: P3 has 11 jumps (all terrain or the heart beam's two before the scroll), 2 ledge landings and
  3 lag frames = 16 rows without progress; the 3 lag frames are the only removable part. P1: 5 jumps, none removable
  by coordinate descent.
* Heart: up to about 10 frames if the 74 frames between its creation and Bill's arrival at the wall were shot
  better (33 HP now, the slot bound is about 40); the beam is stratified by the first jump only.
* Guardian: a few frames; the row-level polish found none.
* Fixed: 70 frames for the wall after the guardian, 224 + 1 after the heart.

### 8.6 The `--prior` path and the files

* `--prior` was exercised for the first time with a non-empty history (`logs/s8/p2/prior_test.inputs.txt`: 12 rows
  ending with Right + Up held and a B press on its first frame): `python -m contra.stages.s8 dbg/s8_pre --quick
  --emus 2 --prior ...` -> 3,238 frames (`logs/s8/p2_prior.*`), the segment's first row holds B for the press's
  second frame, 0 violations counted with the history, and history + segment passes `check_inputs.py`
  (`logs/s8/p2/prior_plus_segment.inputs.txt`). The quick mode (one beam of width 8 per boss) happened to kill the
  guardian 224 rows after its spawn, better than the two width-16 beams of the full runs (227-232): the fight
  moves by about +-5 rows with the press phase it starts on. A third beam per boss (width 8, another jump phase)
  was tried on the dbg state afterwards (`logs/s8/p2_v2.*`, 3,242 again): guardian 764 against 749 from the two
  width-16 beams, and the heart's third beam died out (every lineage dead at the scroll trigger); it was taken out again, so the solver is the one that made the table in 8.1.
* `logs/s8/best.*` is now the second pass's `p2_v1` (3,242); the first pass's best is `logs/s8/best_pass1.*`.
  The `states/s8/best_*` savestates still belong to the first pass's run.
* All three second-pass segments were also replayed open-loop on a fresh emulator with `tools/s8_verify_p2.py`,
  END taken by `contra/clock.py`: 3,242 / 3,237 / 3,248 frames, Down held at control loss, no death.

## 9. Rule v2 (press budget), 2026-10-12 / finished 2026-10-16

Rule v2: at most 109 new presses of a button in any 600 frames and 246 in any 1,800, across stage boundaries
(`knowledge/project_rules.md`). Work started 2026-10-12, stopped by the owner's pause before its report; finished
and validated 2026-10-16. Pre-change modules: `contra/stages/*.py.backup_v2`; `s8.py.backup_v2b` = the rule v2
solver before the 2026-10-16 change of the guardian beam list.

### 9.1 What changed (shared engine with stage 3)

* `s3s8_lib.Pad` is the press budget: it keeps every button's press starts of the last 1,800 rows and refuses a
  press that would break a window (hard); `reserve` holds presses back for a fight ahead (soft). `history_tail()`
  gives a solver the last ~1,800 rows of the real history (cut where nothing is held). `--windows` on both solvers
  (default `600:109,1800:246`; `none` switches it off); `check_rows` counts the windows too.
* `s3s8_engine.gen(fire="demand")`: B only inside `fires` intervals (the running sections fire because the
  lookahead repair asked for a shot, `s8.fire_cands` / `move_cands`; bursts that work are thinned to fewer volleys).
  `fire=True` (the old metronome, `--metronome`) is still there and is throttled by the budget.
* `s3s8_fight.beam_fight`: a child whose press created no pellet (no free bullet slot; same slot trace as the
  no-press child) is dropped; ties are broken by fewer presses; the node carries its press count.
* `s8.py`: demand firing everywhere, `press_report` (presses / pellets / presses that fired nothing per section,
  fullest 60/600/1,800 windows with the history), the report runs the project's `check_inputs.check` on history
  tail + segment. Guardian beams since 2026-10-16: W24 off0, W24 off2, W16 off0, W12 off1 (was W16 off0, W16 off2,
  W8 off0, W12 off1). `s3.py`: `--windows` and the 1,800-row history tail; nothing else.

### 9.2 Results (all: open-loop replay on a fresh emulator with `tools/s8c_verify.py`, END by `contra/clock.py`,
Down held at control loss, 0 deaths, weapon out $13, `check_inputs.py` with the windows PASS on history + segment)

| start | pass 2 (metronome) | rule v2, first beams (10-12) | **rule v2, final (10-16)** | guardian dead | scroll | heart flag | lag | B presses (guardian / heart / stage) | max B in 600 / 1,800 (history counted) |
|---|---|---|---|---|---|---|---|---|---|
| `s8c/c1_s8_pre` + chain1 history (1,862-row tail) | 3,237 (chain1) | 3,245 (`v3_c1`) | **3,229** (`v3_c1_r2`) | 737 | 2,798 | 3,003 | 1 | 43 / 32 / 85 | 45 / 95 |
| `dbg/s8_pre` | 3,242 | 3,244 (`v3_dbg`) | **3,235** (`v3_dbg_r2`) | 739 | 2,799 | 3,008 | 2 | 42 / 31 / 128 | 44 / 86 |
| `s8/var1_pre` | 3,237 | - | **3,235** (`v3_var1`) | 741 | 2,804 | 3,009 | 2 | 40 / 29 / 118 | 42 / 76 |
| `s8/var37_pre` | 3,248 | - | **3,227** (`v3_var37`) | 737 | 2,797 | 3,001 | 1 | 42 / 32 / 167 | 84 / 123 |

Spread 3,227-3,235 (record 3,273). All files `logs/s8/v3_<name>.{inputs.txt,seg.json,report.json,verify_v3.json,
withprior.inputs.txt}`, solver logs `logs/s8/v3/<name>.out`. `v3_c1_r2` on the WHOLE chain1 history
(`v3_c1_r2.fullhistory.inputs.txt`, `tools/s8c_fullcheck.py`): the windows that reach into stage 8 hold at most
45 / 95 B presses; the file as a whole fails only inside the chain1 history's own stages 1 and 5 (being redone).

### 9.3 Where the first rule v2 run lost its 8 frames on c1, and how they came back

* Not the budget: the windows were never close (most 65 / 93 with the history), 0 presses refused by the Pad.
* The guardian fight: kill 751 against 745 in chain1 (6 rows); P3 +1; heart +2. The beam's kill moves by +-10
  rows with its width / phase (from the same fight start: W16 off0 751, off2 759, W8 770, W12 off1 757, W24 off0
  **737**, W24 off2 738, W24 off1 751, W20 753, W32 off0,2 753; `logs/s8/v3/beam_exp_*.out`). Adding the two W24
  beams gives 737-741 on all four starts (220-224 after the spawn, was 227-234). Cost about 2 more minutes per run;
  a whole solve is now 27-34 min on 3 emulators.
* Demand firing in P3 wastes some presses (28-45 "fired nothing" in var1/var37/dbg: shots at targets that a
  volley already covered); harmless under the budget, and c1_r2 needed only 8 presses in P3.

### 9.4 Stage 3 regression (same engine)

`python -m contra.stages.s3 dbg/s3_pre --out s3/v3_dbg` with the rule v2 engine: **3,517** rows to stage 4's first
frame (pass 2: 3,521 on this state; var37 3,494), dragon flag 2,805, 0 deaths, weapon $13, lag 34 (18 before
control is lost), 36 B presses, `check_inputs.py` with the windows PASS, open-loop replay reaches stage 4's first
frame at the same row. Not re-run on the other stage 3 start states.
