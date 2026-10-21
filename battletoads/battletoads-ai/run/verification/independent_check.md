# Independent check of route up17 (verifier, 2026-10-10)

Verdict: **PASSED** (points 1-5 all hold). up17 replays from power-on, uses only legal inputs, visits the levels of the
category's route, and ends on the cut to Professor T. Bird 42,912 frames after the toad lands in Level 1:
**714.024 s = 11:54.02, 35.23 s under the record's 749.25 s (12:29.25) and 5.98 s under 12:00.00.**

Everything below was produced by my own scripts (`u17v_*.py`, own replay loop over `toads.emulator.BizHawk`). assemble.py,
the builders' scripts and the earlier verifier's scripts were not run. My loop sends only `step`, `ram`, `screenshot`
(and `msave`/`mload` in the one picture-only run): the bridge's `poke` is never called, nothing is set on controller 2.

| | value |
|---|---|
| input list | `logs/up17.inputs.txt`, frozen copy `logs/fix/u17v_up17.inputs.txt`, file sha1 `2344f9b48fdfbb2e13209f9aef4fb6bf53c6a1b2`, 44,986 frames |
| clock start: toad lands in Level 1 (`$3B5` 5 -> 4, height stops at 144, pad byte first live) | frame **2074** (first standing picture: 2075) |
| Queen's last hit (slot-3 id 0x7e -> 0x46) | frame 43,906 |
| FIRST level byte 13 -> 254 (cut to the Dark Queen's speech, not the end) | frame 44,566 (11:47.04) |
| SECOND level byte 13 -> 254 (cut to Professor T. Bird = end) | frame **44,986** = the last input of the list |
| run time | 42,912 frames / 60.0988 = **714.024 s = 11:54.02** |
| record 749.25 s | under by **35.226 s** (2,117 frames) |
| 12:00.00 = 720.00 s (cut on 45,345 or earlier) | under by **5.976 s** (359 frames) -> under_12_minutes TRUE |
| final RAM sha1 (after the last input) | `cfa6cb835332349340cadef04fbf72639e61b85a` (builders: cfa6cb83) |
| per-frame RAM capture sha1 (44,986 x 2,048 bytes) | `ec890be213a57d9525d7ce754184d396772cf372` (run1 = run2 = de-mashed run) |

Builders' line (their log `logs/fix/u17f_assemble_up17.txt`, read only, agrees with my numbers): "up17: RUN TIME 11:54.02 =
42912 frames (landing 2074 -> cut to Professor T. Bird 44986); queen_speech_cut 44566 ...".

## 1. Replays from power-on

BizHawk 2.11.1, core quickerNES (TOADS_CORE unset; "quickerNES: Booted" in each `logs/fix/u17v_*_emu.log`), ROM sha1
`5c3a497a82be60704dedf45248b6ad9b32c855ab`, no cheat / movie / state autoload in the config, no .cht files, fresh EmuHawk
process per run, one bridge `step` per frame. (EmuHawk has emulated one empty frame before the bridge takes over;
"frame N" = the Nth line of the list, as in assemble.py.)

| run | what | final RAM sha1 | capture sha1 |
|---|---|---|---|
| run1 | plain replay, whole 2 KB RAM after every frame (`u17v_run1.ram`) | cfa6cb83...1b85a | ec890be2...f372 |
| run2 | same + 813 screenshots + 90 no-input frames after the list | cfa6cb83...1b85a | ec890be2...f372 |
| run3 | same + 26 no-input branches from in-memory snapshots (pictures only) | cfa6cb83...1b85a | (differs, see caveat 4) |
| demash | the de-mashed list of section 6 | cfa6cb83...1b85a | ec890be2...f372 |
| ref16b2 | the verified up16b2 replayed by the same loop, for comparison | 10722e85...46d221 | f1938279...f56d (= the earlier verifier's capture) |

run1 and run2 are **byte-identical on all 44,986 frames**, not only at the end. Logs: `u17v_run1.stdout.txt`,
`u17v_run2.stdout.txt`, `u17v_run3.stdout.txt`, `u17v_run1.json`, `u17v_analysis_run1.txt`.

## 2. Input scan (`u17v_scan.py` -> `u17v_scan.txt`)

- 44,986 lines, CRLF, ASCII only; tokens other than Up Down Left Right Select Start B A: **none**.
- Left+Right on one frame: **0**. Up+Down on one frame: **0**. Repeated tokens: 0.
- **Start: frames 1171-1174 only** (the title screen, one press held 4 frames). No Start on any between-level page or later.
  The game's own pad byte `$29` has the Start bit on frames 1174-1184 and never again.
- Select: 206 frames (Fk1b 1, Fk4u 2, Fk6v 1, Fk8u 38, Fk9u 8, Fk10u 1, A11r 20, T12a 54, A13r_k0p16 81).
- Controller 2: nothing is ever set. The game's second-pad new-press byte `$2C` is zero on every frame; `$2A` is nonzero
  (value 1 = Right) only on 601 frames in five stretches (16041-16175, 25610-25669, 25821-25958, 27768-27901, 34643-34776):
  the end-of-level walks and the Terra Tubes death, where the game itself forces both pad bytes (up16b2: 599 frames, same places).
- The list equals the fixed intro (1,917 frames) + `Fk1b Fk3b Fk3t Fk4u Fk6v Fk8u Fk9u Fk10u A11r T12a A13r_k0p16`
  (`logs/pbeam_*.json`) frame for frame; segment frame ranges in `u17v_scan.txt`.

## 3. Events from RAM, and the pictures I looked at

Every change of the level byte `$10` (frame: from -> to; 254/255 are the pages between levels):

    1413 0->1 | 2469 1->254 .. 2488 ->3 | 4728 3->254 .. 4748 ->4 | 9833 4->254 .. 9852 ->8 | 12294 8->254 .. 12313 ->7 |
    16166 7->254 .. 16186 ->11 | 25950 11->254 .. 25969 ->9 | 27893 9->254 .. 27912 ->10 | 34768 10->254 .. 34788 ->5 |
    42965 5->13 | 44566 13->254, 44574 ->255, 44575 ->13 | 44986 13->254        (full list: u17v_analysis_run1.txt)

| level byte | level (named by the game's own card, nothing pressed, `u17v_sheet_pages_1/2.png`) | frames | run clock at entry |
|---|---|---|---|
| 1 | Level 1 Ragnarok's Canyon | 1413-2468 (landing 2074) | 0:00.00 |
| 3 | "LEVEL 3 - TURBO TUNNEL" | 2488-4727 | 0:06.89 |
| 4 | "LEVEL 4 - ARCTIC CAVERNS" | 4748-9832 | 0:44.49 |
| 8 | "LEVEL 6 - KARNATH'S LAIR" | 9852-12293 | 2:09.42 |
| 7 | "LEVEL 8 - INTRUDER EXCLUDER" | 12313-16165 | 2:50.37 |
| 11 | "LEVEL 9 - TERRA TUBES" | 16186-25949 | 3:54.81 |
| 9 | "LEVEL 10 - RAT RACE" | 25969-27892 | 6:37.60 |
| 10 | "LEVEL 11 - CLINGER-WINGER" | 27912-34767 | 7:09.93 |
| 5 | "LEVEL 12 - THE REVOLUTION" | 34788-42964 | 9:04.34 |
| 13 | Level 13 Armageddon (the Dark Queen) | 42965-44565, 44575-44985 | 11:20.40 |

Pictures (all under `logs/fix/`, single frames in `logs/fix/u17v_shots/`; a picture taken after frame N shows the game
state of frame N-1 for sprites):

- **Landing**: `u17v_sheet_landing.png`, `u17v_sheet_landing_zoom.png` (frames 2068-2079, 3x): rope pose up to picture 2071,
  falling pose with a shadow under it 2072-2074, **standing on the ground from picture 2075** = RAM landing 2074.
- **First cut, no input for 480 frames from a snapshot**: `u17v_sheet_cut1_noinput.png`: black to +8, from +10 **the Dark
  Queen's speech** ("WHAT ?! I LOST! THIS CAN'T BE! I'M THE DARK QUEEN ! ... I HATE YOU, BATTLETOADS! I'M OUTTA HERE !"),
  black at +442, back on the tower at +456. Not the end of the run.
- First cut as the route plays it (`u17v_sheet_cut1_route.png`): picture 44566 = status bar and tower tip on black, A read on
  44575, tower back from picture 44591.
- **Second cut**: `u17v_sheet_cut2_tbird.png`: picture 44986 = status bar and tower tip on black, +1..+9 black, **+10..+90 =
  Professor T. Bird's dialogue screen** ("WHOO! ALRIGHT GUYS ! THERE'S NOTHIN..."). Singles `u17v_shots/run2_cut2_f44986.png`,
  `run2_post_p010.png` .. `run2_post_p090.png`. The frames after the list were stepped with no input.
- **One picture per level**: `u17v_sheet_levels.png`; more of each level in `u17v_sheet_play_<level>_NN.png`.
- Last 240 frames of each level: `u17v_sheet_exits_warps.png` (Levels 1, 4, 6), `u17v_sheet_exits_b.png` (Levels 3, 8, 9),
  `u17v_sheet_exits_c.png` (Levels 10, 11, 12); `u17v_sheet_death_turbo.png`, `u17v_sheet_death_terra.png`.
- New parts every 40 / 45 / 90 frames: `u17v_sheet_play_karnath_01..03.png`, `u17v_sheet_play_level8_01..04.png`,
  `u17v_sheet_play_tower_01..04.png`, `u17v_sheet_play_queen_01.png`.

## 4. Alive, no game over, levels, and what is new against up16b2

- Lives `$11`: 3 at the start; 3->2 at 4312 (Turbo Tunnel skip death), 2->3 at 15239 (score passes 100,000), 3->4 at 23960
  (1-up in Terra Tubes), 4->3 at 25928 (the planned death on Terra Tubes' last spikes), 3->4 at 31284 (200,000), 4->5 at 43346
  (300,000). **Minimum 2: never a game over or a continue.** The score (`$5F4-$5F9`) never decreases; every level byte occurs once.
- Health `$51A`: full (47) on every frame of Karnath's Lair, Level 8, Rat Race, Clinger-Winger, the tower and both Level 13
  stretches; one hit in Level 4 (47 -> 31 at 7530, the damage boost, as in up16b2); zero only at the two deliberate deaths
  (4231, 25599).
- Lives / health / score on the last frame of each level, **equal to up16b2's level by level** (`u17v_compare.txt`):
  3/47/004000, 2/0/043600, 2/31/086600, 2/47/091600, 3/47/143600, 3/47/168600, 3/47/179600, 4/47/233800, 4/47/284550, 5/47/334550.
  (The builders write 4/0/284550 for Level 12: health is 47 on the last tower frame 42964 and zeroed by the load on 42965 - a
  different reading frame, not a different run.)
- **Levels visited: 1, 3, 4, 6, 8, 9, 10, 11, 12, 13.** Three Mega Warps: the pictures before the level byte leaves Level 1,
  Level 4 and Level 6 read "MEGA WARP ADVANCE 2 LEVELS" (`u17v_sheet_exits_warps.png`). Level 3 ends through the Turbo Tunnel
  skip (death at the bikes, respawn, white flash, level end), Level 9 by the death on the last spikes (room stays, no toad,
  level ends). The record's video shows the same ten levels and the same empty spike room at the end of Terra Tubes
  (`u17v_wr_route_overview.jpg`, `u17v_wr_terra_end_25620_26010.jpg`).
- What is new (`u17v_align.py` -> `u17v_align.txt`: toad track + camera of up17 against my up16b2 replay, per level):
  Level 1 identical (1,056 frames); Turbo Tunnel identical for 1,932 frames, the last 295 differ (one Left press);
  Arctic Caverns identical (5,071); **Karnath's Lair: 1,128 new frames, 130 frames shorter**; **Level 8: the climb identical for
  2,807 frames (whole RAM identical on 2,791 of them), the Robo-Manus fight and exit new (1,032 frames, 21 shorter)**;
  Terra Tubes 9,484 of 9,764 frames identical; Rat Race identical (1,924); Clinger-Winger 6,769 of 6,856;
  **the tower: frames 35715-37226 new (plus three short stretches, 267 frames, later), the rest is the old play 257-259
  frames earlier (level 259 frames shorter)**; the Queen fight new (9 frames shorter), ending 1 frame longer.
- Continuity of the new parts (`u17v_compare.txt`, per-frame steps of toad x / height and of the camera, both routes):
  - Karnath's Lair: toad x steps -6..+5 px a frame plus one +9 (the snap onto the snake's head, up16b2 has +8), height steps
    -4..+7 (up16b2: the same range); 217 frames at 3 px/frame (run speed; up16b2 121). The only jump in position is the
    game's own room change: caught in the exit hole at (369, 8099), set down at (76, 7486) in the warp room on frame 11858
    (up16b2: (369, 8120) -> (76, 7486)). Score +5000 at the hole, health 47 throughout. Pictures: snakes ridden in order,
    "OUT" hole, warp room, flight past the stars, warp pad.
  - Level 8: camera 4028 -> 12 without ever going back, at most 4 px a frame; toad height steps -4..+12, x steps <= 5;
    no life lost; score 91,600 -> 143,600 = 21 smashes of 2,000 + 10,000 for the kill.
  - Tower: camera 5888 -> 4 without ever going back, at most 4 px a frame; toad height steps -9..+13 (up16b2: the same
    maximum), x steps -7..+8 apart from the wrap of the cylinder (24 wrap frames; up16b2: -7..+8, 24); health 47 throughout;
    score 233,800 -> 284,550 in steps of 750 / 1,000 / 2,000 / 5,000.
  - Queen: 20 hits of 2,000 + 10,000, health 47 on every frame, toad alive at x 238 on both cuts.
  No teleport, no speed outside what the verified up16b2 shows in the same levels.

## 5. The time, the clock convention, and the record's video

(44,986 - 2,074) / 60.0988 = **714.024 s**; 749.25 - 714.024 = **35.23 s under the record**; 720.00 - 714.024 = **5.98 s
under 12:00** (359 frames).

I re-read the record's video myself (youtube A7czTlY7OI0, "Battletoads Any% Speedrun in 12:29 (World Record)", Jay_cee,
848.04 s, 1280x720 at 60 fps; frame n read at n/60 + 0.008 s by drawing the paused video to a canvas; read-only; my tab closed):

| event in the record's video | video frame | same event in up17 |
|---|---|---|
| toad on the rope (last) | 1241 | picture 2071 |
| falling pose | 1242-1244 | pictures 2072-2074 |
| **toad standing on the ground (first)** | **1245** | picture 2075 = RAM landing 2074 |
| cut to the Queen's speech (status bar + tower tip on black; playfield brightness 56.6 -> 1.6) | 45,684 | picture 44,566 |
| **cut to T. Bird: status bar + tower tip on black** (playfield 56.3 -> 3.0, status bar still lit) | **46,202** | picture 44,986 (the same picture) |
| fully black | 46,203-46,211 (9 frames) | +1..+9 (9 frames) |
| T. Bird's dialogue screen (first) | 46,212 | +10 |

- Record, first standing picture -> T. Bird cut picture: 44,957 video frames = 749.28 s; the board's 749.25 s = 44,955
  frames. **The record is measured at the landing and at the cut to Professor T. Bird**, the two events up17 is timed at;
  the Queen's-speech cut is 8.6 s earlier. Pictures: `u17v_wr_landing_1238_1245.jpg`, `u17v_wr_landing_1244_1251.jpg`,
  `u17v_wr_queen_cut_45683_45760.jpg`, `u17v_wr_tbird_cut_46201_46300.jpg`, `u17v_wr_route_overview.jpg`.
- **Uncertainty of the clock-start convention: 2-4 frames (0.03-0.07 s).** RAM landing 2074 against the first standing picture
  2075 is 1 frame; the board's retime is 2 video frames shorter than my picture-to-picture count of the same video. Timed
  picture to picture up17 is 42,911 frames = 714.01 s; with 4 frames against us it is 714.09 s. **"Under 12:00" survives
  every reading by more than 5.9 s (355 frames)**; "under the record" by more than 35 s.

## 6. De-mashed list (release this one)

`u17v_demash.py` -> **`logs/fix/u17v_demashed_up17.inputs.txt`** (sha1 `9a80dba1f75c30161599868549d70e19cd7c7dfa`), plan in
`u17v_demash_plan.json`. The route holds six turbo-like stretches (A,B,A,B on every frame, or A every other frame):
9659-9829 (Level 4 warp animation, controller not read at all), 16024-16162, 25852-25946, 27794-27889 (end-of-level walks:
the port is read but the game forces its pad byte to Right), 34670-34813 (Clinger-Winger's walk + the page to Level 12) and
44567-44575 (the Queen's speech). **640 presses removed, 5 kept**: B on 34777, B on 34787, A on 34788, B on 34801 (the page's
three cards; 34787 is the held B the game still reads) and A on 44575 (the first frame the speech reads the pad).
Replayed from power-on (`u17v_demash.stdout.txt`): final RAM sha1 cfa6cb83...1b85a and the per-frame capture is
**byte-identical to the mashed run on all 44,986 frames** (capture sha1 ec890be2...f372); the lag-frame list is identical too.
Scan of the de-mashed list: clean, Start 1171-1174 only (`u17v_scan_demashed.txt`). The other pages of up17 are already three
single presses each. So removing these 640 presses does not move the hidden alignment.
Side test (`u17v_demash_t1.stdout.txt`): with the held B on 34787 removed as well the run still ends in the same RAM
(cfa6cb83), but the dice `$25-$28`, `$75` differ on the 14 page frames 34787-34800 until the level load zeroes them - a press
on a frame the game reads does move the dice, so that B stays in the released list to keep every frame identical.

## 7. Caveats (none changes the verdict)

1. **quickerNES only.** The NesHawk port of up17 does not exist yet; earlier routes were about 11 frames slower there
   (0.18 s: still under 12:00).
2. **Not humanly performable.** After the de-mash the list still has 134 single Select presses (up to 17 in one second in the
   ending), 920 frames whose input differs from both neighbours, and frame-exact play throughout.
3. The list ends on the cut frame itself, with no idle frames behind it.
4. An in-memory savestate reload is not fully transparent: in run3 (branches) RAM bytes `$100` (1,573 frames, Level 3) and
   `$1A` (6 frames) differ from the plain replays, the final RAM is the same. Numbers rest on run1 / run2 only.
5. T. Bird's picture appears at cut +10 (the task text expected +11).
6. Score digits are at `$5F4-$5F9` (found by searching the RAM; the HUD in the pictures shows the same numbers).

## 8. Files

Scripts: `u17v_replay.py`, `u17v_scan.py`, `u17v_analyze.py`, `u17v_plan.py`, `u17v_sheets.py`, `u17v_compare.py`,
`u17v_align.py`, `u17v_demash.py`. Data in `logs/fix/`: `u17v_run1.ram`, `u17v_run2.ram`, `u17v_run3.ram`, `u17v_demash.ram`,
`u17v_ref16b2.ram` (2,048 bytes per frame), `u17v_run1_analysis.json`, `u17v_run*_lag.json`, `u17v_scan.txt`,
`u17v_analysis_run1.txt`, `u17v_analysis_ref16b2.txt`, `u17v_compare.txt`, `u17v_align.txt`, `u17v_demash_plan.json`,
`u17v_result.json`, sheets `u17v_sheet_*.png`, record-video pictures `u17v_wr_*.jpg`, singles `u17v_shots/`.
