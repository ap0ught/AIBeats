# Chain B (up16b): the full Level 8 (climb + arrival + fight + A/B page mash) - working notes

Started 2026-10-10 02:17. Owner of this file: chain B. Files: `u16b_*.py`, `logs/fix/u16b_*`, segments `logs/pbeam_B*.json`
and `pbeam_u16b_T8.json`, bookmarks `states/B*_end0`, `u16b_T8_end0`, routes `up16b*`.

## 1. The finding that changes the plan: NOTHING behind Level 8 has to be re-fitted

Measured, not assumed (`u16b_chain.py`, `logs/fix/u16b_chain_T8.txt`):

- Test segment `u16b_T8` = `L8c[0:5]` + up14's own climb + `early_l8arrive_best` + `early_l8fight_e` + 300 empty frames +
  A,B alternating to the Terra Tubes placement (exactly recipe 1 + recipe 3 of `early_savings.md`; 4,469 inputs,
  414 shorter than `L8c`; placement on up14-clock frame 16952; health 47, lives 3, score 143600).
- Behind it the OLD segments `L9heli_c2`, `L9heli_c2L10`, `L9heli_c2L11s`, `L12h`, `L13_L12h_k0` were replayed and their
  RAM compared after every frame with each segment's own reference run (replayed from its own bookmark), stack page
  excluded: **5 frames differ, all within the first 7 frames of Level 9** (the level timer `$0B` reads 0 instead of 1
  while the level is still loading, and scratch byte `$75`); from Level 9's frame 8 to the T. Bird cut **every frame is
  bit-identical**. End state identical.
- Why: the level load zeroes the dice (`$25-$28` read 0,0,0,0 from the frame the old toad is removed until the first
  real frame of the new level) and resets the level timers. What can still differ is the hidden CPU phase in the idle
  loop (`early_savings.md` section 6); behind this Level 8 it came out the same as up14's.
- So the refit chain (rngfit of Levels 9/10/11/12 and a new Queen solve) is NOT needed as long as the new Level 8's
  Terra Tubes entry is "in sync". Check for any new Level 8 with
  `python u16b_entry8.py <segment> L9heli_c2 240 base` (frames 8..240 of Level 9 identical?) and prove it with
  `python u16b_chain.py <segment> L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h <queen>`.
  If a new Level 8 is NOT in sync: `u16b_entry8.py <segment> L9heli_c2 240 scan <out>` tries tail variants (one extra
  Select/Up/Down on a frame after the killing blow, the wait before the mash +-3, the mash starting on B) and writes
  the shortest variant that is.
- Safety route assembled from this: `up16b0` = `L1b L3u L3skipu L4c5 L6c u16b_T8 L9heli_c2 L9heli_c2L10 L9heli_c2L11s
  L12h L13_L12h_k0` (expected T. Bird cut 46005 = 12:10.98). Result: see section 4.

## 2. The climb search

`u16b_climb.py` = `early_l8climb.py` with the queue fixed (see its docstring): order = frames + (4032 - height) / RATE
(a lower node is expanded only when it is that much younger: entries dominated in (height, frame) sink), hard drop
260 px under the front, failed candidates stop early, the standing move kept, the arrival cutscene is part of the
search (cost = the control frame + the run to the boss; a flattened toad is rejected), root = `early_L8_p0`.
`u16b_climb2.py` = the same + a refinement pass: the best kids of every node are polished by trying the neighbouring
moves (wait / run length / A hold one or two frames shorter or longer, dash on/off): the coarse random grid alone
loses a frame or two per floor.

Reference numbers (frames since the placement, up14 frame 12488): up14 stands on the arena floor at 3,135, the
cutscene starts at 3,167/3,168 and control returns at 3,302 (frame 15790). The record's climb is 369 frames shorter
(placement -> boss descent 2,799), i.e. control at about 2,933.

Runs (logs `logs/fix/u16b_climb_<tag>.out`, results `logs/fix/u16b_climb_<tag>.json`, milestones
`logs/fix/u16b_climb_mark<px>_<tag>.json`): see section 3 for the table as it fills in.

## 3. Results (running log)

### The climb
- 02:24-02:42 `u16b_climb.py` (queue fix only) and `u16b_climb2.py` (+ refinement): from the old milestones they
  reproduced the old lines and then stalled at 2,496 px exactly where the old search had (164 expansions without
  progress). Cause found in up14's own inputs: on the flier floors (sparks 22 px above the floor) up14 DUCKS (`Down`,
  animation 75, 76 frames of it between 1,900 and 2,600 px) and the candidate family had no Down at all.
- `u16b_climb3.py` = + ducking (stand ducked, duck during the wait, duck between run and jump; a jump out of a duck
  leaves at sprint speed 192). With it:

| run | root | settings | result (frames since the placement; up14 = 3,302 to control) |
|---|---|---|---|
| s1 | `u16b_climb_mark2300_r2.json` (2,304 px at 1,745) | climb3, 100 tries, seed 31, rate 1.6 | first FINISH after 22 min: control at 2,958 (x 157); best 2,952 (x 149) = **-350** |
| s2 | `early_l8climb_mark1800d_v.json` (1,856 px at 1,432) | climb3, 100 tries, seed 32, rate 1.8 | control at **2,914 (x 183) = -388** (the record's climb: -369) |
| s3 | fresh from the bottom | climb3, 100 tries, seed 33, rate 1.8 | running: +500 px at 394 (-149), +1,100 at 853 (-208) |
| s4 | `early_l8climb_1400b.keep_v.json` | climb3, 110 tries, seed 34, rate 2.0 | stopped at 2,000 px (1,559, same as the others) to free an emulator |

| t1 | `u16b_climb_mark3400_s3.json` (3,456 px at 2,334) | climb3, 140 tries, seed 41, **rate 3.0**, depth 400 | control at **2,749 (x 182) = -553** (184 faster than the record's climb) |
| t2 | `u16b_climb_mark3200_s3.json` | climb3, 120 tries, seed 42, rate 2.4 | stuck at 3,512 px like s3; stopped |
| v1 | `u16b_climb_mark2200_s3.json` (2,208 px at 1,639) | climb3, 140 tries, seed 51, rate 3.0, depth 400 | running |

  s3 (fresh) finished at 2,917: it was 116 frames ahead of s2 at 3,500 px and lost all of it at the next gate (a floor
  hole over the bobbing platform at 3,506 px): rates 1.6-2.4 dive past the earlier pass, rate 3.0 (t1) finds it
  (3,600 px at 2,402 instead of 2,559). Lesson: the gates of this tower (2,400-2,500, 3,200-3,330, 3,500-3,650,
  3,700-3,800 px) are passed on the clock; near them the search has to be close to uniform cost.

  Snapshots used downstream: `u16b_climbC3.json` (s3: 2,917), `u16b_climbC4.json` (t1: 2,749), `logs/fix/u16b_climbC1.json` (s1's first finish, 2,958), `u16b_climbC2.json` (s2, 2,914).
  The camera matters at the top: the cutscene starts when the camera has caught up; a long last jump brings it up
  sooner (s1: cutscene 12 frames after the landing; up14: 32).

### The fight
- On climb C4 (control 2,749): a 648 (kill 15885), b 662 (15899), c 678, d 678, e 682, f 695, g 670, h 652 (15889),
  b3 648 (15885; = b to hit 20, last blow a ground punch). Hits come every 26 frames; the 32-62 frame gaps are his
  jumps. **The boss's death takes 437 frames after a ground punch (b3) and 443 after a jump attack** (up14: 441): a
  fight should be ranked by kill frame + death, not by the kill frame.
- Not every fight can be merged with the old Level 9: both fights with the kill on 15885 (a, b3) reach Terra Tubes only
  with alignments 5/10/20/25/35/40/50 on the right parity (none merges; 1,465 single presses with Select/Up/Down,
  1,765 with A/B/Left/Right, 1,000 pairs, late mash starts: `logs/fix/u16b_sync_B8d*.txt`, `u16b_census_B8d_raw*.txt`);
  h and b merge. So after a fight: `python u16b_auto.py <climb json> <fight tag> <tag>` (build + merge scan, 6 minutes).
- `u16b_fight.py <climb json> <tag> [width] [tries] [seed]` (early_l8fight's candidate(), chain A's extra tier and resume).
- C1a (climb C1, width 10, 100 tries, seed 5): 22 blows in 652 frames from control, kill on up14-clock frame 16098 (up14 16877).

### Level 9 sync: what decides it, and how to get it on purpose
- The dice `$25-$28` are zeroed by the level load. The loop that scrambles them (`$871F`: `JSR $8728 / JSR $8743 / JMP`,
  213 cycles a pass, no data-dependent timing) is entered afresh every frame when the frame's logic ends and is cut by
  the NMI at an instruction boundary. So the only hidden state is the CPU's ALIGNMENT against the frame: a few cycles.
  It can be READ: QuickNES core blob of a savestate, bytes 4-5 = timestamp (1/15 CPU clocks), 8-11 = frame count,
  12-13 = PC, 14-19 = registers (`u16b_phase.py`).
- A variant of the segment that reaches the next level's first frame with the same RAM and the same alignment behaves
  identically for ever; an alignment a cycle or two off either MERGES with the old run within a few frames (the NMI
  catches both at the same instruction boundary) or rolls other dice. Each alignment needs testing once.
- **PARITY RULE (the trap of this job):** odd and even PPU frames differ by a third of a CPU cycle. A new segment that
  shifts the route by an ODD number of frames can never merge for good: `B8a` (4,038 inputs, shift -845, alignment
  timestamp 0) tracked the old Level 9 for all 9,790 frames (16 frames with a stray RAM byte) and then rolled other dice
  6 frames into Rat Race (`logs/fix/u16b_chain_B8a.txt`). With an EVEN shift and a merging alignment everything is
  bit-identical: `u16b_T8` (shift -414, timestamp 15) and `B8b` (shift -846, timestamp 15) both replay the whole old
  chain unchanged (`u16b_chain_T8.txt`, `u16b_chain_B8b.txt`: only frames 1-7 of Level 9 differ).
- Tools: `u16b_sync.py <segment> <next> <T0> <next level byte> <out>` adds one harmless press (Select / Up / Down) on
  every frame of the free tail (rolling base, about 5 minutes for a Level 8 tail), reads the alignment at the frame the
  toad is set down, tests each alignment once (frames 8..240 identical AND the alignment and frame parity equal to the
  reference's 240 frames in), prints the table and writes the shortest merged variant. `u16b_pick.py` writes a chosen
  one. `u16b_bound.py` does the same for an A / B page mash at a boundary (env `U16B_BM` = entry bookmark of the new
  lineage, `U16B_PRE` / `U16B_PREBTNS` = presses before the mash). `u16b_chain.py` is the proof.
- Level 8 -> 9, measured: reference alignment at the Terra Tubes entry PC `$84B1` timestamp 60. Merging: 60 and 15;
  tracking but not merged: 0 with an odd shift; diverging: 5, 10, 20, 25, 30, 35, 40, 45, 55. The page after Level 8
  sets the toad down 43 to 47 frames after the level byte leaves 7 (dice, steered by the same presses).
- Boundary segments made with `u16b_bound.py` (A,B page mash, kept only when the next segment MERGES, even shift):
  **B4** = `L4c5` with the warp page mashed A,B + Select on index 4931: 5,154 inputs (-2), no Start left in it;
  **B9** = `L9heli_c2` with the page mashed A,B + Select on index 9398 (a live frame near the end): 9,788 (-2);
  **B6** = `L6c` with its 8 Start presses on the warp page replaced by A on the same frames (same length; the A,B mash
  at -2 never merges with Level 8: 917 variants). With B4, B6, B8, B9 the whole chain replays unchanged
  (`logs/fix/u16b_chain_B4_B6_B9.txt`) and the route has no Start after the title screen.
  Rat Race -> Clinger-Winger (946 variants) and Clinger-Winger -> Revolution (868): no merging variant found.
- Terra Tubes -> Rat Race, reference lineage, first scan: the A,B mash gives 9,788 (-2) but always alignment `$84F7`/15 against the
  reference `$84F3`/0, 5 identical frames; no press in the last 200 frames (the toad is dead) or in the mash changes
  it (`logs/fix/u16b_bound_B9.txt`). Not usable as it stands.

## 4. Routes

- **up16b2 (the route of this chain; 2026-10-10 05:57):** `python assemble.py up16b2 L1b L3u L3skipu B4 B6 B8_h B9
  L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0 > logs/fix/u16b_assemble_up16b2.txt`
  -> `up16b2: 45425 frames ... replay MATCH sha1 10722e85`,
  `up16b2: RUN TIME 12:01.33 = 43351 frames (landing 2074 -> cut to Professor T. Bird 45425); queen_speech_cut 45006
  (reference only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 for a landing at 2074 -> UNDER the
  record by 27.92s`.
  Segments: `B4` (L4c5, warp page mashed A,B: 5,154, -2), `B6` (L6c, Start -> A on the warp page: 2,595), `B8_h` =
  `L8c[0:5]` + climb `u16b_climbC4.json` (s3 fresh from the bottom to 3,456 px + t1: 2,749 inputs to control, -553
  against up14; cutscene at +2,613, the record's about +2,799) + fight `u16b_fight_C4h.json` (652 frames, kill on
  up14-clock frame 15889) + 300 empty frames + A,B mash, Select on segment index 3415 for the alignment: 3,893 inputs
  (L8c 4,883: -990), `B9` (L9heli_c2, page mashed A,B + Select on 9398: 9,788, -2); the rest are the old segments,
  untouched. Proof that everything behind Level 8 is bit-identical to the old chain: `logs/fix/u16b_chain_B8_h.txt`
  (only the first 6-10 frames after three level loads differ in the timer byte). Banned-press scan
  (`logs/fix/u16b_scan_up16b2.txt`): 0 Left+Right, 0 Up+Down, Start only on the 4 title frames, Select on 133 frames.
  Climb proof: `logs/fix/u16b_verify_climb.txt` (health 47 throughout, lives 2, 0 banned presses, toad at x 216 when the
  cutscene starts, not flattened, x 182 at control).

- **up16b** (the first full route of this chain; 2026-10-10 04:19): `python assemble.py up16b L1b L3u L3skipu L4c5 L6c
  B8 L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0 > logs/fix/u16b_assemble.txt`
  -> `up16b: 45573 frames ... replay MATCH sha1 10722e85`,
  `up16b: RUN TIME 12:03.79 = 43499 frames (landing 2074 -> cut to Professor T. Bird 45573); queen_speech_cut 45154
  (reference only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 for a landing at 2074 -> UNDER the
  record by 25.46s`. `B8` = `pbeam_B8b.json` = `L8c[0:5]` + climb `u16b_climbC2.json` (run s2: 2,914 inputs to control,
  -388 against up14; arena floor at +2,761, cutscene at +2,777, the record's about +2,799) + fight `u16b_fight_C2c.json`
  (630 frames from control, kill on up14-clock frame 16032) + 300 empty frames + A,B mash, Select on segment index 3559
  (tail frame 9) for the alignment: 4,037 inputs (L8c 4,883: -846). The old segments behind it are untouched and replay
  bit-identically (`logs/fix/u16b_chain_B8b.txt`). Banned-press scan (`logs/fix/u16b_scan_up16b.txt`): 0 Left+Right,
  0 Up+Down, Start on the same 22 frames as up14 (title 1171-1174; warp pages inside L4c5 and L6c 9681-9742 and
  12281-12342), none in B8. Climb proof: `logs/fix/u16b_verify_climb.txt`.

- **up16b0** (safety route: recipe 1 + 3 only, up14's own climb): `assemble.py up16b0 L1b L3u L3skipu L4c5 L6c u16b_T8
  L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0` -> 46,005 frames, replay MATCH sha1 10722e85,
  `RUN TIME 12:10.98 = 43931 frames (landing 2074 -> cut to Professor T. Bird 46005) ... UNDER the record by 18.27s`
  (`logs/fix/u16b_assemble_up16b0.txt`). Banned-press scan of `logs/up16b0.inputs.txt`: 0 Left+Right, 0 Up+Down;
  Start on 22 frames, the same 22 as in up14 and up15h (4 at the title, 18 in the warp pages of L4c5 and L6c;
  none in anything built here).


## 5. What is left in Level 8 (not done; for the next batch)

Sub-12:00 needs the T. Bird cut on 45,345 or earlier: 80 frames from up16b2.
- **Fight, about 20-30 frames:** the fights on climb C4 came out 648-695 (best mergeable 652); on climb C2 three seeds
  gave 630 / 632 / 638. More seeds on C4 (20 minutes each, `u16b_fight.py`), ranked by kill + death (a ground punch as
  the last blow: death 437 instead of 443), each followed by `u16b_auto.py` (one fight in three or four cannot be merged).
- **Climb gates:** the time goes at 2,400-2,500 px (about 170 frames for 100 px), 3,200-3,330 (150) and 3,700-3,800
  (70). They are passed on the clock; t1 caught the pass before the one s2/s3 took at 3,500-3,650 by searching at rate
  3.0. The same has not been tried from before 2,400 with enough lead (v1 from 2,208 at rate 3.0 was 15 frames slower
  than s3 at 2,800 and was stopped). A fresh run at rate 3.0 from the bottom is hours of machine time.
- **Page mashes with a merge:** Rat Race -> Clinger-Winger and Clinger-Winger -> Revolution (2 frames each): no merging
  variant among 946 / 868 single presses (`logs/fix/u16b_bound_B10.txt`, `_B11.txt`); pairs not tried. Karnath -> Level 8
  at -2: none among 917.
- The Level 8 -> 9 page: the toad is set down 43-47 frames after the level byte leaves 7; B8_h has 44 with a merging
  alignment (3,893); 43 was seen 7 times in 1,465 variants, never with a merging alignment.
- Not understood: why some fights only reach non-merging alignments (the timestamp's value modulo 15, a third of a CPU
  cycle, differs from the reference's for every variant on the right frame parity). The tools find out in 6 minutes.

## 6. Files

Scripts: `u16b_climb.py`, `u16b_climb2.py`, `u16b_climb3.py` (use climb3; `u16b_mk_climb2.py` / `u16b_mk_climb3.py` generated
them), `u16b_fight.py`, `u16b_build.py`, `u16b_auto.py`, `u16b_sync.py`, `u16b_pick.py`, `u16b_bound.py`, `u16b_chain.py`,
`u16b_phase.py`, `u16b_phase2.py`, `u16b_census.py`, `u16b_entry.py` / `u16b_entry8.py` (first, blind versions of the scan),
`u16b_tailprobe.py`, `u16b_verify_climb.py`, `u16b_scan_inputs.py`, `u16b_lib.py`, `u16b_ps.py` / `u16b_kill.py` (stop one
of my own jobs by PID), `u16b_bench.py`, `u16b_mkb6x.py`.
Segments: `pbeam_B4`, `B6`, `B8` (= `B8b`, up16b), `B8_h` (up16b2), `B9`; raw / test ones `B8a*`, `B8b_raw`, `B8c1`, `B8d_raw`,
`B8e*`, `B8_b3_raw`, `B8_h_raw`, `u16b_T8`, `u16b_B6x`, `u16b_B6s`. Bookmarks `<segment>_end0`. Outputs `logs/fix/u16b_*`.
