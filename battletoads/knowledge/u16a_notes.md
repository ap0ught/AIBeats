# Chain A (route up16a): Robo-Manus the fast way, old chain kept behind it

Started 2026-10-10 02:15 (local). Written as the work goes; chain B repeats from here.
Owner of: `u16a_*.py`, `logs/fix/u16a_*`, segments `logs/pbeam_A*.json`, bookmarks `states/A*.State`, routes `up16a*`.
Nothing here writes memory. All commands are run from `../toads`, `TOADS_CORE` unset.

## 0. Status (updated last: 04:46)

> **FOR CHAIN B (and anyone building a new Level 8):** put the new Level 8's end in the phase of **`A9r`** (reference
> entry = bookmark `A8r_end0`), not of the old `L9heli_c2`, and assemble **`... <your Level 8> A9r A10r A11r A12r
> A13r_k0p16`** (since 04:22; `A12r`, NOT `A12x`: the polished Queen `A13r_k0p16` starts from `A12r_end0`). Behind
> Level 8 that is 29,033 inputs: 9 fewer than `A9r A10r A11r A12x L13_L12h_k0` (29,042, `up16ar2`) and 20 fewer than
> the old `L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0` (29,053). Verified from power-on in `up16ar3`.
> Your own tool takes it as it is: `python u16b_entry8.py <segment> A9r 240 scan <out>`; ours:
> `U16A_NEXT=A9r python u16a_sync8.py <out> <fight json>` (the fight json = inputs from control to the kill, Level 8 =
> `L8c[0:3113]` + arrival + fight; for another climb copy the tool and change `pre`). With fight t2 28 of 310 tails
> were in that phase, the first one tried was exact (0 differing frames in the whole of `A9r`).

- **BEST: `up16ar3` VERIFIED** (assemble.py, two power-on replays, 04:19-04:22; the refit worker):
  `python assemble.py up16ar3 L1b L3u L3skipu L4c5 L6c A8r2 A9r A10r A11r A12r A13r_k0p16`
  -> `up16ar3: RUN TIME 12:09.68 = 43853 frames (landing 2074 -> cut to Professor T. Bird 45927)`, replay MATCH sha1
  `91a0c7b3` (another end state than `9a02f991`: another Queen fight), UNDER the record by 19.57 s. Log
  `logs/fix/u16a_assemble_up16ar3.txt` (copy `..._45927.txt`), inputs `logs/up16ar3.inputs.txt` (copy
  `logs/fix/u16a_up16ar3_45927.inputs.txt`). Scan (`logs/fix/u16a_scan_up16ar3.txt`): Left+Right 0, Up+Down 0, unknown
  buttons 0, Start 22 (title 4, `L4c5` 10, `L6c` 8; 0 from Level 8 on), Select 197 (A8r2 31, A9r 8, A11r 20, A12r 57,
  Queen 81); the file equals intro + the segments.
  = `up16ar2` with the tail `A12r` (8,408) + `A13r_k0p16` (2,021) for `A12x` (8,409) + `L13_L12h_k0` (2,029): **-9**.
  `A13r_k0p16` = the fresh Queen behind `A12r_end0` (`A13r_k0`, 2,037) polished from its hit 16 (section 3.4).
- Before it: **`up16ar2` VERIFIED** (assemble.py, two power-on replays, 03:23-03:27):
  `python assemble.py up16ar2 L1b L3u L3skipu L4c5 L6c A8r2 A9r A10r A11r A12x L13_L12h_k0`
  -> `up16ar2: RUN TIME 12:09.83 = 43862 frames (landing 2074 -> cut to Professor T. Bird 45936)`, replay MATCH sha1
  `9a02f991`, UNDER the record by 19.42 s. Log `logs/fix/u16a_assemble_up16ar2.txt` (copy `..._45936.txt`), inputs
  `logs/up16ar2.inputs.txt` (copy `logs/fix/u16a_up16ar2_45936.inputs.txt`). Scan: Left+Right 0, Up+Down 0, unknown
  buttons 0, Start 22 (title 4, `L4c5` 10, `L6c` 8: the unchanged upstream segments; 0 from Level 8 on), Select 140.
  = the refit lineage (`up16ar`, section 3.4) with a better Level 8: `A8r2` = 4,411 inputs (fight `u16a_l8fight_t2`,
  618 frames; tail found by `U16A_NEXT=A9r python u16a_sync8.py A8r2 logs/fix/u16a_l8fight_t2.json`, EXACT phase:
  `A9r` replays behind it without one differing frame).
- `up16ar` (45942, 12:09.93) and `up16a` (45954, 12:10.13) are the two earlier verified routes, see below.

- Second: **`up16ar` = RUN TIME 12:09.93, T. Bird cut 45,942** (03:06, refit lineage `A8r A9r A10r A11r A12x` + the
  old Queen `L13_L12h_k0`; replay MATCH sha1 `9a02f991`; sections 3.3-3.4; recipe for chain B = section 4).
  `up16a` below is the in-sync line, 12 frames slower, verified first.
- **`up16a` VERIFIED** (assemble.py, two power-on replays, 02:48-02:53):
  `python assemble.py up16a L1b L3u L3skipu L4c5 L6c A8s145 L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0`
  -> `up16a: RUN TIME 12:10.13 = 43880 frames (landing 2074 -> cut to Professor T. Bird 45954)`, replay MATCH sha1
  `9a02f991`, UNDER the record by 19.12 s. Log `logs/fix/u16a_assemble.txt` (copy `u16a_assemble_up16a_45954.txt`),
  inputs `logs/up16a.inputs.txt` (copy `logs/fix/u16a_up16a_45954.inputs.txt`).
  (At assemble time the Level 8 segment file was called `pbeam_A8.json`; the same bytes are now `pbeam_A8s145.json`,
  see "two workers" below. `logs/up16a.inputs.txt` equals intro + those segments, checked.)
- Level 8 in it: `A8s145` = 4,418 inputs (L8c 4,883: **-465**): fight `u16a_l8fight_s14` (624 frames from control to the
  kill; EARLY's was 674), page skipped with B,A alternating from 145 frames after the kill.
- NO refit and NO new Queen were needed: see section 3 (chain B's finding, confirmed here with another fight).
- Banned-press scan of `logs/up16a.inputs.txt`: Left+Right 0, Up+Down 0, nothing on controller 2, 122 frames with
  Select. Start: the 4 title frames (1171-1174) and 18 presses on the two warp cards inside the UNCHANGED upstream
  segments `L4c5` (route frames 9681-9742) and `L6c` (12281-12342), exactly as in up14 / up15h; none in Level 8 or later.

### Who does what (written 03:10 by the in-sync worker; the refit worker: please leave these to me)
- DONE 03:27: fight `t2` (618) -> `A8r2` (4,411, exact phase of `A9r`) -> **`up16ar2` verified, 45936**; and `A8s2`
  (4,410, in phase with the old `L9heli_c2`; built and checked through Level 9 only, NOT assembled: the old-chain
  lineage is 10 frames longer behind it, expected cut 45946).
- DONE 04:13, no gain: two more Queens from `L12h_end0`, 3 and 4 idle frames first, width 800
  (`python l13solve2.py L12h_end0 3 A13k3 800`, `... 4 A13k4 800`, 55 minutes each next to 8 other emulators):
  `A13k3` = 2,039 with exactly `L13_L12h_k1`'s hits, `A13k4` = 2,029 with exactly `L13_L12h_k0`'s hits and inputs. The
  idle count only matters by its parity (2-frame decisions; the toad is not placed before frame 11), so idle 0/2/4 and
  1/3 are the same two searches. The kill lands on input 948 or 952 whatever the lead in mid-fight was (k3/k4 were 22
  to 28 frames ahead of k0 at hits 9 to 13 and lost all of it by the 20th hit). **2,029 is this solver's floor behind
  `L12h_end0`**; another idle count is not worth an hour. (The refit worker's `A13r_k0` behind `A12r_end0`: 2,037.)
- DONE 04:15, no gain: the 44-frame page behind fight t2 in the phase of `A9r` (`A8r3`): 310 tails + 2,650 tails with
  one extra Select/Up/Down in the boss's death: 346 in phase, all 4,411 or 4,412 inputs; the 4,410 ones never are.
- DONE 03:45, no gain: the 47-frame page after Level 9 (`python u16a_syncnext.py A9r A10r A9p 500`): a Select on any of
  the last 375 frames of `A9r` changes neither the page nor the phase (all 375 variants identical to `A9r`); stopped.
- Not touched by me: `A8r A9r A10r A11r A12r A12x A13r*`, `u16a_syncnext.py`, `u16a_scan.py`, `up16ar`.
- `pbeam_A8.json` = `pbeam_A8s145.json` = the Level 8 of the verified `up16a` (4,418 inputs). Leave it.

### Two workers in this namespace (read this before touching A8, A9, ...)
Between 02:40 and 02:43 a second chain-A worker (same tools, same file prefix) started the ORIGINAL plan next to this
one: `u16a_mkentry.py A8_end0 ...` (power-on bookmark of the 4,417-input Level 8 that was `pbeam_A8.json` at 02:40),
then `u16a_chain.py A8_end0 "" 9 12` = `u16a_rngfit.py` for Levels 9-12 -> `A9`, `A10`, `A11`, `A12`
(`logs/fix/u16a_chain.txt`, `u16a_fit_A*.txt`), and a fight search `u16a_l8fight_s23`. So:
- `pbeam_A8.json` (4,417 inputs, fight s14, A,B from +100; NOT phase-matched) + `A8_end0` + `A9` `A10` `A11` `A12`
  = the refit chain. It needs its own Queen behind `A12_end0`. Do not mix it with the old segments.
- `pbeam_A8s145.json` (4,418) + the OLD segments = the verified `up16a`.
- `u16a_chain.py` is the refit driver (rewritten at 02:55 with the same command line after it was overwritten by
  mistake); the per-frame comparison tool is `u16a_chk.py`.

## 1. Tools made for this chain

| file | what it does |
|---|---|
| `u16a_lib.py` | helpers: `seg()`, `route_inputs()` (assemble.py's intro + segments), `banned()`, `write_seg()` (temp file + rename, keeps `.backup`), `toad()`, `diff()` |
| `u16a_l8fight.py` | copy of `early_l8fight.py`; writes `logs/fix/u16a_<out>.json` / `_partial.json`; fallback tiers when a beam collapses; optional args 6 and 7 = an earlier fight json + number of its hits to keep (resume) |
| **`u16a_sync8.py <out> <fight json> [NA=240]`** | THE BUILD TOOL: Level 8 = `L8c[0:3113]` + arrival + fight + tail, tail variants scanned until the old `L9heli_c2` replays with identical RAM behind it (section 3). Env `U16A_VARIANT=start,first[,k,button]` builds one given tail, `U16A_STEP` grid step, `U16A_STAGE2=0` skips the extra-press stage |
| `u16a_chk.py <first seg> <old seg>...` | replays the old segments behind a new first segment and compares RAM and the toad per frame with each segment's own reference run; prints health / lives / score at every level end against the old chain's |
| `u16a_build8.py <out> <fight json>` | first version of the builder (earliest placement, no phase check): what the refit chain's `A8` was made with |
| `u16a_mkentry.py <bookmark> <segments...> [--cmp bm]` | power-on replay of intro + segments (same stepping as `assemble.replay`), saves the replay-exact bookmark and compares it with a tool-made one (only needed for a refit) |
| `u16a_mkrngfit.py` -> `u16a_rngfit.py` | chain A's copy of `rngfit.py` (section 4): A,B page mash + page dice, HEAD fix, lives/score check |
| `u16a_chain.py <entry> <tag> <first> <last>` | refit driver: `u16a_rngfit.py` for Levels 9..12 with explicit names and the right `RNGFIT_IDS` |
| `u16a_hid.py`, `u16a_p1.py`, `u16a_p2.py`, `u16a_p3.py` | probes (level-entry timers, which bytes differ behind a tail, core-state blocks) |

## 2. Step 1: Level 8 segment A8

Facts measured while building (all from bookmark `L6c_end0`, the entry `L8c` itself starts from):

- `L8c` replayed: kill (score +10,000) at input 4394, level byte leaves 7 at 4835, the toad is placed in Terra Tubes on
  input 4883 = the last one (detector of `early_l8verify.py`: level 11, then hp 0 and x 0, then hp > 0 and x > 0).
  End state: toad (40,112), hp 47, lives 3, score 143600, timers `$0B/$0C` = 1/0.
- New line with `logs/fix/early_l8arrive_best.json` (193 inputs) + `logs/fix/early_l8fight_e.json` (674 inputs):
  control at input 3306 (x 183), kill at input 3980 (414 sooner), level byte leaves 7 at 4423 (443 after the kill; L8c 441).
- The page after Level 8: with A,B on alternate frames the placement comes 44 to 47 frames after the level byte
  leaves 7, and WHICH of those is dice: it changes with anything pressed during the 443-frame death wait (the toad
  hops or punches; nothing else happens). First scan (mash start +0..+454, A or B first): placements 4467 x3,
  4468 x1, 4469 x112, 4470.
- NOT a trap, but looks like one: behind an A,B mash the level timer `$0B` reads 0 on the black frames and on the
  placement frame; behind L8c's A mash it reads 1. It does not matter to the game: the placement frame is followed by
  two more black-timer frames, and on the third frame the level starts its clock (`$0B` := 0, dice seeded with the same
  value `848999c7` in both runs). So the placement frame IS the equivalent of L8c's last frame and the segment is cut
  there (`u16a_p1.py` prints both side by side). It does matter to `rngfit.py`, see section 3.
- Fights (`u16a_l8fight.py <width> <tries> <out> <seed> logs/fix/early_l8arrive_best.json [<fight json> <hits kept>]`,
  about 12 minutes each with four emulators busy, NOT 40):

| run | width, tries, seed | result (frames from control to the kill) |
|---|---|---|
| `early_l8fight_e` (EARLY track) | 10, 100, 5 | 674 |
| `u16a_l8fight_s11` | 12, 100, 11 | died at hit 13 (+362): the strict tier left ONE child and it was a dead end |
| `u16a_l8fight_s12` | 10, 120, 12 | (see log below) |
| `u16a_l8fight_s13` | 14, 90, 13 | died at hit 20 (+594), same beam collapse |
| `u16a_l8fight_s14` | 12, 100, 14, resumed from s11's hit 12 with the fix below | 624 (blows at 26 52 80 124 150 176 202 230 256 282 308 334 364 404 430 456 486 512 544 570 598 624) |
| `u16a_l8fight_t2` | 16, 120, 32, resumed from s14's hit 12, tool with the way back out of dead ends | **618** (s14's blows to 456, then 482 510 542 568 600 618: the last blow is a running attack out of a hop, 18 frames after the 21st) |
| `u16a_l8fight_t1`, `t3` | 14/110/31 fresh; 16/120/33 from s13's hit 7 | level with s14 at blow 14 to 16 (+404, +458); stopped by hand at 03:16 |

  Fix for the collapse (in `u16a_l8fight.py`): the longer horizons (84 strict, 240 loose) are now also tried when the
  50-frame tier leaves fewer than half a beam of children, not only when it leaves none.
  Where the time goes: 26 frames a blow is the floor; each of his take-offs (about every 165 frames) costs 14 to 18.
  s13's opening (28, 60, 92, 118, 144, 170, 196) is 6 frames ahead of the others at blow 7: it pays 6+6 early and
  nothing at the first take-off.

- More fights from s13's blow 7 (`s21`, `s22`, `s23`: widths 14/12/16) were level with s14 at blow 15 (+430) and two of
  them collapsed again around a take-off; stopped at 02:51 because the Level 9 refit had started (rule: swap a fight in
  only before the refit starts). **Fight used: `logs/fix/u16a_l8fight_s14.json`, 624 frames (TAS 599, EARLY's 674).**
- `python u16a_build8.py A8 logs/fix/u16a_l8fight_s14.json` -> **4,417 inputs (L8c 4,883: -466)**: kill at input 3930,
  level byte leaves 7 at 4373, placement 4417 with the mash from +100 after the kill, A first (44 frames of page; the
  scan saw 4417 x4, 4418 x7, 4419 x3 ...). End = L8c's end in every RAM byte but `$0B`. 0 Left+Right, 0 Up+Down, 0 Start,
  26 frames with Select.
- Replay-exact entry: `python u16a_mkentry.py A8_end0 L1b L3u L3skipu L4c5 L6c A8 --cmp A8_end0b` -> power-on replay of
  16,900 inputs, landing 2074, RAM sha1 `1d5b8a09`, **0 bytes differ** from the bookmark the build tool saved
  (`A8_end0b`). So a tool-made end bookmark is replay-exact here; the power-on one is used anyway.

**NAMES (02:50): another process began writing `pbeam_A8.json` / `u16a_chain.py` / `u16a_sync8.py` (a second line of work:
a Level 8 tail "in sync" with the old Level 9, see section 5). To keep the two apart, THE REFIT LINEAGE IS `A8r A9r A10r
A11r A12r` + queen `A13r*`, route `up16ar`; bookmarks `A8r_end0` ... (copies of the files first written as A8..A12).
`pbeam_A8r.json` = the 4,417-input Level 8 above; `pbeam_A8.json` now holds the 4,418-input in-sync variant.**

## 3. Step 2: the refit (Levels 9, 10, 11, 12 behind the new Level 8)

### 3.1 What `rngfit.py` could not do as it is, and the copy that can

`python u16a_mkrngfit.py` writes `u16a_rngfit.py` = `rngfit.py` + four changes (it asserts every anchor, so it can be
re-run when `rngfit.py` changes). Same command line and environment as `rngfit.py`.

1. **HEAD (the one that matters).** Behind an A,B mash the entry frame's `$0B` is 0, behind the old A mash 1. `rngfit.py`
   decides "did the game logic run this frame" from `$0B` changing. On the level's first real frame the old run goes
   1 -> 0 (a tick), the new one 0 -> 0 (no tick), so the tool thinks we dropped a frame, repeats that input, and every
   later frame is one late: STUCK at frame 2 with nothing a re-roll can fix. The copy gives the old inputs verbatim up
   to and including the old run's first timer change (3 frames in Levels 9, 10, 11; 4 in Level 12), checks that the
   key is the old one there, and starts tracking from that frame. Automatic; `RNGFIT_HEAD=n` forces it.
2. The page mash at the end also tries `A,B` and `B,A` on alternate frames (recipe 3); `rngfit.py` only knows one
   button every other frame.
3. Page dice: one Select on each of the 80 frames before the mash (`RNGFIT_PAGESEL=0` turns it off,
   `RNGFIT_PAGESEL_N`), kept only when the toad is set down sooner. Lives and score at the end must equal the old run's.
4. The end check no longer needs the old run's timer values on the entry frame (they are 0 instead of 1 behind an
   A,B mash and the old code then reports a bogus `slack 60`); `RNGFIT_SLACKMAX` (4) bounds that search.

Do NOT use `fitchain.py` for these names (it derives level and output name from the segment name). The four fits, in
order, one emulator, each from the previous one's `_end0` bookmark:

```
python u16a_rngfit.py L9heli_c2      A8_end0   A9                       # no RNGFIT_IDS
python u16a_rngfit.py L9heli_c2L10   A9_end0   A10                      # no RNGFIT_IDS
RNGFIT_IDS=7b    python u16a_rngfit.py L9heli_c2L11s  A10_end0  A11     # the Buzzball
RNGFIT_IDS=5c,62 python u16a_rngfit.py L12h           A11_end0  A12     # Hornheads, walkers
```

### 3.2 Results (frames; "old" = the segment being re-fitted)

| level | old segment | old | new | gain | re-rolls (old frame: Select on frame, tries) | time |
|---|---|---|---|---|---|---|
| 9 Terra Tubes | `L9heli_c2` | 9,790 | **9,787** | -3 (page) | 2: 3711 (Select 3671, 40 tries), 3753 (Select 3721, 32 tries); the same two spots the old chain re-rolled (3719, 3759) | 176 s |
| 10 Rat Race | `L9heli_c2L10` | 1,944 | **1,941** | -3 (page) | 0 | 108 s |
| 11 Clinger-Winger | `L9heli_c2L11s` | 6,879 | **6,876** | -3 (page) | 3, all in the Buzzball fight: 5991 (Select 5990, 1 try), 6124 (6116, 8), 6318 (6315, 3) | 157 s |
| 12 The Revolution | `L12h` | 8,411 | **8,408** | -3 (three fewer lag frames: 99 lag shifts, the dice decide which frames drop) | 6: 2235 (Select 2198+2165, 437 tries: the only pair), 2332 (2295, 37), 2826 (2823, 3), 3458 (3416, 42), 3542 (3541, 1), 6444 (6443, 1) | 337 s |
| **sum 9-12** | | 27,024 | **27,012** | **-12** | 11 re-rolls | 13 minutes on one emulator, machine loaded |

Every end state equals the old run's in all RAM bytes outside the stack and `$0B/$0C` (health, lives, score included:
47/3/168600, 47/3/179600, 47/4/233800, Level 12: lives 4, score 284550, timers 58/29 as before). Nothing stuck; no
`RNGFIT_W` / `RNGFIT_RANDOM` / entry wait was needed. Driver: `python u16a_chain.py A8_end0 "" 9 12` (summary in
`logs/fix/u16a_chain.txt`, per level `logs/fix/u16a_fit_A<n>.txt`). The files were first written as `A9 A10 A11 A12` and
copied to `A9r A10r A11r A12r` (bookmarks `A<n>r_end0`); **refit lineage = `A8r A9r A10r A11r A12r` = 31,429 inputs**
(in-sync Level 8 + old chain: 31,442), Level 13 entered after route frame 43,912.
A dry run of the same chain behind the first Level 8 (fight e, 4,467 inputs: `A9t`, `A10t`) gave 9,788 with ONE re-roll
(4625) and 1,942: the re-roll spots move with the dice, the cost (seconds) does not.

### 3.3 Step 3 without a Queen solve: put the END of the re-fitted Level 12 back in the old phase (`u16a_syncnext.py`)

The same phase idea as section 5, used at the other end of the chain. Behind `A12r` the Queen's dice differ from the old
run's (frames 16..400 of the old Queen: 5 of 385 identical). ONE Select on a quiet frame of Level 12's tail moves the
hidden phase; the tool tries each of the last S frames and keeps the variants behind which the OLD next segment has
identical RAM, then proves the best one over the whole next segment.

```
python u16a_syncnext.py <segment> <next OLD segment> <out> [S=300] [NA=400] [F0=16] [buttons=Select]
    env U16A_PRESS=<frame>,<button>   build exactly this variant;  U16A_S0=<n>  skip the last n frames (already scanned)
python u16a_syncnext.py A12r L13_L12h_k0 A12x 300 400 16          # 2.5 minutes
```
- Result: **Select on input index 8245 (163 before the end, inside the 194-frame hold of A on the last spring)** ->
  `pbeam_A12x.json`, 8,409 inputs (+1: the level byte changes one frame later), bookmark `A12x_end0`, entry RAM
  identical to `L12h_end0` in every byte. Behind it `L13_L12h_k0` is bit-identical through its first cut (the whole
  fight, the kill, the rise, the Queen's speech cut at 1610); 396 frames after input 1634 differ somewhere in RAM and
  the cut to T. Bird still falls on its last input (2029). The in-sync line shows exactly the same 396 frames
  (section 5), so that is the Queen segment's own behaviour behind any upstream, not this variant's.
- Only 1 of 300 frames works here (Level 11's tail gave the helicopter track 26 of 453). If none had: scan further
  back (`U16A_S0=300 ... 700`), other buttons (`Up,Down`), or solve a Queen (step 3 of the plan, below).
- Tool check on another boundary: `python u16a_syncnext.py A10r L9heli_c2L11s A10x 200 400 16` -> Select on index 1915
  gives `A10x`, 1,940 inputs (one SHORTER), and the whole old Level 11 (6,879 frames) replays with zero differing
  frames. So every boundary can be handled either way: re-fit the next level (minutes) or re-phase the end of this one.

### 3.4 Step 4 for the refit lineage: `up16ar` VERIFIED, 12 frames under `up16a`; then `up16ar3` with its own Queen, 45,927

```
python assemble.py up16ar L1b L3u L3skipu L4c5 L6c A8r A9r A10r A11r A12x L13_L12h_k0 > logs/fix/u16a_assemble_up16ar.txt
python u16a_scan.py up16ar L1b L3u L3skipu L4c5 L6c A8r A9r A10r A11r A12x L13_L12h_k0 > logs/fix/u16a_scan_up16ar.txt
```
- `up16ar: 45942 frames, timing starts at 2074, ... replay MATCH sha1 9a02f991`
- **`up16ar: RUN TIME 12:09.93 = 43868 frames (landing 2074 -> cut to Professor T. Bird 45942); queen_speech_cut 45523
  (reference only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 for a landing at 2074 -> UNDER the
  record by 19.32s`** (03:06; copies `logs/fix/u16a_assemble_up16ar_45942.txt`, `logs/fix/u16a_up16ar_45942.inputs.txt`).
  The end RAM sha1 is the same as `up16a`'s: the same final state, 12 frames sooner.
- Scan: Left+Right 0, Up+Down 0, unknown buttons 0, 135 frames with Select (A8r 26, A9r 8, A11r 20, A12x 58, Queen 23).
  Start 22 = the 4 title frames (1171-1174) + 10 in `L4c5` (9681-9742) + 8 in `L6c` (12281-12342), all on the title
  and the two warp cards of the unchanged upstream segments; 0 from Level 8 on. The file equals intro + the segments.
- Frame budget against up15h (T. Bird cut 46,972): Level 8 -466; pages after Levels 9, 10, 11 -9; Level 12 `L12h`
  for `L12g` -469, and -3 lag frames; +1 for the re-phased Level 12 end; Queen `L13_L12h_k0` (cut on its input 2,029)
  for `L13y0E2` (cut on its input 2,113) -84. Sum **-1,030**: 46,972 -> 45,942.
- Pages (level byte leaves the level -> toad set down, from `logs/up16ar.trace.txt`): 8->9 44 frames, 9->10 47,
  10->11 43, 11->12 44. They are not comparable with each other (each level loads its own data); each is the
  shortest of the variants tried at that boundary (300 tails after Level 8: 44 to 47; 24 mash variants + up to 160
  Select frames after Levels 9, 10, 11: best 47 / 43 / 44, the old one-button mash gave 49 / 46 / 47). Nothing
  shorter was seen anywhere, so no frames are known to be left in the pages.
- Step 3 of the plan as written (a fresh Queen behind the refit lineage), done for comparison:
  `python l13solve2.py A12r_end0 0 A13r_k0 800` -> `pbeam_A13r_k0.json`, **2,037 inputs to the T. Bird cut** (kill at
  953, hits 53 108 140 200 241 285 331 381 429 471 521 557 609 647 691 737 783 833 885 923; 57 minutes on a loaded
  machine, log `logs/l13solve2_A13r_k0.txt`). VALID but 7 frames slower than the old Queen behind the re-phased Level
  12 (2,029 + 1), so NOT used as it is.
- **The polish of that Queen IS the best tail (04:18): `A13r_k0p16` = 2,021 inputs to the T. Bird cut.**
  `L13_PREFIX=A13r_k0:16 python l13solve2.py A12r_end0 0 A13r_k0p16 800` (14 minutes on a loaded machine; log
  `logs/l13solve2_A13r_k0p16.txt`): `A13r_k0`'s first 739 inputs kept (through its hit 16), the rest searched again.
  Hits 17-20 at 785 829 881 921 (were 783 833 885 923), **kill at 941 (was 953)**: the 12 frames are in the last blow
  (20 frames after hit 20 instead of 30), 2 in hits 18-20; the ending is 1,080 frames (was 1,083; rise from +367, the
  Queen's speech cut at +660, last scene 411). Replay from `A12r_end0`: 20 counted hits, toad hp min 47, VALID.
  `A12r` + `A13r_k0p16` = 10,429 inputs against `A12x` + `L13_L12h_k0` = 10,438.
- **`up16ar3` VERIFIED with it (04:22): `up16ar3: 45927 frames, timing starts at 2074, ... replay MATCH sha1 91a0c7b3`,
  `RUN TIME 12:09.68 = 43853 frames (landing 2074 -> cut to Professor T. Bird 45927); queen_speech_cut 45507 (reference
  only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 for a landing at 2074 -> UNDER the record by
  19.57s`** (`python assemble.py up16ar3 L1b L3u L3skipu L4c5 L6c A8r2 A9r A10r A11r A12r A13r_k0p16 >
  logs/fix/u16a_assemble_up16ar3.txt`; scan `logs/fix/u16a_scan_up16ar3.txt`: Left+Right 0, Up+Down 0, unknown 0,
  Start 22 all upstream of Level 8, Select 197; the file equals intro + the segments).
  Frame budget against up15h (46,972): the `up16ar` budget above (-1,030) with Level 8 `A8r2` for `A8r` -6, and the
  tail -9 (no re-phase of Level 12: -1; Queen 2,021 for 2,029: -8). Sum **-1,045**: 46,972 -> 45,927.
- Lesson for chain B, corrected: the re-phase (3 minutes) gets a verified route at once and keeps every Queen solved
  behind `L12h_end0` usable; a fresh solve ALONE was worse (2,037), but **fresh solve + polish from hit 16** (57 + 14
  minutes) beat the old Queen by 8. A polish is cheap: run one behind every Queen you keep.
- More polishes, 04:21-04:45, four emulators side by side, NO gain (all VALID segments, none used; `A13r_k0p16` stays):

  | segment | command (`... python l13solve2.py <entry> 0 <out> 800`) | kept | kill | ending | T. Bird cut |
  |---|---|---|---|---|---|
  | `A13r_k0p16` (**used**) | `L13_PREFIX=A13r_k0:16`, `A12r_end0` | 739 | 941 | 1,080 | **2,021** |
  | `A13r_k0p14` | `L13_PREFIX=A13r_k0:14`, `A12r_end0` | 649 | 943 | 1,080 | 2,023 |
  | `A13r_k0p12` | `L13_PREFIX=A13r_k0:12`, `A12r_end0` | 559 | 951 | 1,081 | 2,032 (24 minutes) |
  | `A13r_k0p16p18` | `L13_PREFIX=A13r_k0p16:18`, `A12r_end0` | 831 | 953 | 1,080 | 2,033 |
  | `A13h_k0p16` | `L13_PREFIX=L13_L12h_k0:16`, `L12h_end0` | 738 | 943 | 1,086 | 2,029 (= `L13_L12h_k0`'s length, no gain) |

  What they show: (1) a polish from an EARLIER hit is not better (more frames to search, same beam: p12 lost 11 frames
  to p16), and a polish of the polish from a LATER hit is worse too (p16p18: the kill fell back to 953); hit 16 of a
  21-hit fight is the one that paid, hit 14 came within 2. (2) Kill frames seen in eight solves: 941 943 943 948 951
  952 953 953; endings (cut minus kill) 1,080 to 1,087 (the floor by `l13z_tail.py`'s own table is about 1,073: body 154 + 207 + 171 +
  122 + load 9 + scene 410). So `A13r_k0p16` has the earliest kill AND the shortest ending seen; another ticket has
  perhaps a one-in-ten chance of 2 frames. (3) Behind `L12h_end0` the polish moved the kill 5 frames forward (943) and
  the ending took them back (rise +370, last scene 413): 2,029 again, so the re-phased line `A12x` + old Queen stays at
  10,438 inputs and the refit line `A12r` + `A13r_k0p16` at 10,429 is the best tail.

- Third replay of `up16ar3` by other code (`python u16a_verify.py up16ar3`, 04:42; reads `logs/up16ar3.inputs.txt`, steps
  it from power-on, own detectors): landing 2074, Queen's speech cut 45507, **T. Bird cut 45927 = the last input**,
  43,853 frames = 12:09.68, RAM sha1 `91a0c7b3`; lives / health / score when each level ends: 3/47/143600 (Level 8),
  3/47/168600 (9), 3/47/179600 (10), 4/47/233800 (11), 4/-/284550 (12), 5/47/334550 (end) - the old chain's values.
  `logs/fix/u16a_verify_up16ar3.txt`.
- Polishes started behind it by the in-sync worker, none better: `A13r_k0p14` 2,023, `A13r_k0p16p18` 2,033, `A13r_k0p12`
  (kill candidate at input 951 when last looked: about 2,031). `A13r_k0p16` (2,021) stands.

## 4. The refit recipe from start to finish (for chain B; 21 minutes on one emulator, proved by `up16ar`)

`<B8>` = the new Level 8 segment: bookmark `L6c_end0`, last input = the frame the toad is set down in Terra Tubes.
Re-fit the REFIT lineage's segments (`A9r A10r A11r A12r`: they already carry the A,B pages and are 12 frames shorter
than `L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h`); the old ones work the same way.

```
python u16a_mkentry.py <B8>_end0 L1b L3u L3skipu L4c5 L6c <B8>                   # replay-exact entry, 1.5 min
python u16a_rngfit.py A9r   <B8>_end0   <B9>                                     # 3 min   (2 re-rolls last time)
python u16a_rngfit.py A10r  <B9>_end0   <B10>                                    # 2 min   (0)
RNGFIT_IDS=7b    python u16a_rngfit.py A11r  <B10>_end0  <B11>                   # 3 min   (3, the Buzzball)
RNGFIT_IDS=5c,62 python u16a_rngfit.py A12r  <B11>_end0  <B12>                   # 6 min   (6, Hornheads and walkers)
python u16a_syncnext.py <B12> A13r_k0p16 <B12x> 300 400 16                       # 3 min: the best Queen (2,021) behind it
python assemble.py <route> L1b L3u L3skipu L4c5 L6c <B8> <B9> <B10> <B11> <B12x> A13r_k0p16 > logs/fix/<...>.txt   # 5 min
python u16a_scan.py <route> L1b L3u L3skipu L4c5 L6c <B8> <B9> <B10> <B11> <B12x> A13r_k0p16
```
(since 04:22 the best Queen is `A13r_k0p16`, 2,021 inputs, made from `A12r_end0`: a re-fitted Level 12 is re-phased against
IT; `L13_L12h_k0`, 2,029, made from `L12h_end0`, works the same way and is what `up16ar` used.)

Rules of thumb, all met on the way here:
- Use `u16a_rngfit.py`, not `rngfit.py` (HEAD, section 3.1), and not `fitchain.py` (names).
- A fit that prints `STUCK`: first look at the frame. Stuck at frame 2 or 3 = the entry timer problem (HEAD), not dice.
  Stuck inside a fight: `RNGFIT_W=360` (re-roll window, default 180), `RNGFIT_RANDOM=12000` (random Select patterns,
  default 4000), then `RNGFIT_ENTRYWAIT=1..3`. None was needed in eight fits (two chains). The dearest re-roll was
  Level 12 frame 2235: no single Select in the 180 frames before it works, the 437th candidate (a pair) does.
- Every fit must end with `RAM bytes that differ (stack and $0B/$0C aside): 0` and equal hp / lives / score. Level 9
  ends with the planned death (`deaths 1` in the reference line); the tool compares the death count per frame.
- The fits change segment lengths only through the page (A,B: -2 to -3 each) and lag (Level 12: -3 here; it can be
  plus). Plan with +-5 frames per batch.
- No Queen solve is needed when `u16a_syncnext.py` finds its frame. If it does not: `U16A_S0=300 ... 700` (further
  back), buttons `Up,Down`, a second Queen segment as the target, and only then
  `python l13solve2.py <B12>_end0 0 <fresh name> 800` (40 minutes) + `L13_PREFIX=<that>:16` polish.
  (Since 04:22 the target to re-phase to is `A13r_k0p16` behind `A12r_end0`, 8 frames better than `L13_L12h_k0`:
  `python u16a_syncnext.py <B12> A13r_k0p16 <B12x> 300 400 16`; a re-fit `<B12>` of `A12r` that already ends in
  `A12r_end0`'s phase needs nothing.)
- Faster still when it applies (section 5): build the Level 8 tail in phase with `A9r` (`U16A_NEXT=A9r python
  u16a_sync8.py ...`); then **`A9r A10r A11r A12r A13r_k0p16`** (best, `up16ar3`) or `A9r A10r A11r A12x L13_L12h_k0`
  (9 longer, `up16ar2`) replay behind it as they are and only assemble is left.
  Check with `python u16a_chk.py <B8> A9r A10r A11r A12r A13r_k0p16`.

## 5. The in-sync line: no refit, no new Queen (how `up16a` was built)

Chain B's finding (`knowledge/u16b_notes.md`): the level load zeroes the dice and the level timers; the only thing a
rebuilt Level 8 can leave different is the hidden CPU phase in the idle loop. If that comes out as before, the OLD
`L9heli_c2`, `L9heli_c2L10`, `L9heli_c2L11s`, `L12h` and the Queen `L13_L12h_k0` replay unchanged behind it.
Confirmed here with another fight, and measured what moves the phase:

- **Presses on the page do not move it.** Fight s14, 114 tails that only differ in when and with which button the
  A,B mash starts inside the last 70 frames before the level byte changes: all out of phase in the same way
  (first RAM difference on Level 9's frame 8; the dice `$25-$28` and scratch `$75`, `u16a_p2.py`).
- **Presses during the boss's death do** (443 frames between the last blow and the level byte leaving 7; the toad
  hops or punches, which costs other CPU time). Mash start on a 6-frame grid over that wait x who presses first:
  **5 of 172 tails in phase** (start +145 B, +133 A, +109 B, +49 A, +31 B), all 4,418 inputs long. The shortest tails
  seen (4,417, a 44-frame page) were not among them: the in-sync Level 8 costs ONE frame against the unsynced one.
- "In phase" by the quick test (Level 9 frames 8..240, or 8..600, RAM identical) can still be only NEAR the old phase.
  Behind `A8s145` (`u16a_chk.py`, every frame of every segment against the segment's own reference run):

| old segment behind `A8s145` | frames with any RAM difference | frames where the toad differs | end (health, lives, score) |
|---|---|---|---|
| `L9heli_c2` (9,790) | 15 (5 in the first 7 frames as in chain B's run, 10 stray ones later) | 0 | 47, 3, 168600 = old |
| `L9heli_c2L10` (1,944) | 1,913 (the dice run differently from frame 6: Rat Race does not use them) | 1 (frame 1905: the level byte changes one frame apart) | 47, 3, 179600 = old; end RAM identical |
| `L9heli_c2L11s` (6,879) | **0** | 0 | 47, 4, 233800 = old |
| `L12h` (8,411) | **0** | 0 | lives 4, 284550 = old |
| `L13_L12h_k0` (2,029) | 396, all after input 1634 (behind the Queen's speech) | 0 | 47, 5, 334550 = old; cuts at 1610 and 2029 = old |

  So Levels 11 and 12 and the whole Queen fight are bit-identical, and the route ends on the predicted frame. Chain
  B's `u16b_T8` (fight e) is in the exact phase (no stray frame anywhere). A near-phase tail is fine when it passes
  `u16a_chk.py` and `assemble.py`; `u16a_sync8.py` now replays the whole next segment behind its candidates and
  prefers a tail with no stray frame (it prints `EXACT phase` or `near phase`).
- The core's savestate cannot serve as a shortcut for "same phase": 24 bytes of it differ even between chain B's
  exact-phase run and the old run at the same Level 9 frame (frame counters, sound state; `u16a_p3.py`).

Recipe for any new Level 8 that ends with the same fight interface (bookmark `L6c_end0`, `L8c[0:3113]`, an arrival, a
fight json):
```
python u16a_sync8.py <A8 name> <fight json> 240          # scan, picks the shortest tail in phase, writes the segment
python u16a_chk.py <A8 name> L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0     # every level end = the old chain's?
python assemble.py <route> L1b L3u L3skipu L4c5 L6c <A8 name> L9heli_c2 L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0
```
`U16A_NEXT=A9r python u16a_sync8.py ...` puts a new Level 8 in phase with the refit lineage's Level 9 instead
(reference = `A9r` behind `A8r_end0`), so that `A9r A10r A11r A12x` replay behind it.
Times: the scan about 5 minutes (one emulator), the check 5, assemble 5.

### 5.1 Later findings (03:10-04:15)

- The "13 stray frames" are not a sign of a poor tail: every in-phase tail of two different fights (s14: 4 tails,
  t2: 8 tails) shows exactly 13 frames after the 7th with a RAM difference in the whole of the old `L9heli_c2`, the toad
  never differs and the end RAM is identical. Against `A9r` (a reference that itself starts behind an A,B mash) the
  same kind of tail shows 0. Either reference works; `u16a_chk.py` + `assemble.py` decide.
- Which page length comes with the wanted phase depends on the fight: s14 -> old phase only with a 45-frame page
  (4,418), `A9r`'s phase with 44 (that is `A8r`, 4,417); t2 -> old phase with 44 (`A8s2`, 4,410), `A9r`'s phase only
  with 45 or 46 (`A8r2`, 4,411).
- Fight tool: `u16a_l8fight.py` keeps the last three generations; when no candidate of a generation lands a blow (every
  node doomed: he lands on the toad) it goes back two blows and doubles the beam for four blows. Searches converge on
  618 to 624 frames (TAS 599); the first twelve blows are at the 26-frame floor except the first take-off (+20).
- `u16a_sync8.py` crashed at its very end when stage 2 had run (sorting results with and without an extra press);
  fixed 04:18 (`RK` sort key). Its stage 2 costs 40 minutes and found nothing shorter in two tries: use
  `U16A_STAGE2=0`.

## 6. Files of the in-sync worker

- Segments: `pbeam_A8.json` = `pbeam_A8s145.json` (4,418; Level 8 of `up16a`), `pbeam_A8s14x.json` (4,418, another tail),
  `pbeam_A8s2.json` (4,410, fight t2, old phase; not assembled), **`pbeam_A8r2.json` (4,411, fight t2, phase of `A9r`;
  Level 8 of `up16ar2`)**, `pbeam_A13k3.json` (2,039), `pbeam_A13k4.json` (2,029 = k0), `pbeam_A9t.json`,
  `pbeam_A10t.json` (dry run of the refit behind the first Level 8, not part of any route).
- Fights: `logs/fix/u16a_l8fight_s14.json` (624), **`u16a_l8fight_t2.json` (618)**, others in section 2.
- Proof logs: `logs/fix/u16a_assemble.txt` (up16a), `u16a_assemble_up16ar2.txt`, `u16a_chk_A8s145.txt`,
  `u16a_chk_A8r2.txt` (every level end against the reference chain), `u16a_sync8_<segment>.txt` (tail scans),
  `u16a_syncnext_A9p.out`, `logs/l13solve2_A13k3.txt`, `_A13k4.txt`.
- Route files: `logs/up16a.inputs.txt`, `logs/up16ar2.inputs.txt` (+ `.events.txt`, `.trace.txt`, `video/<route>.mkv`
  written by assemble.py); copies of the input lists in `logs/fix/u16a_<route>_<frames>.inputs.txt`.
