# NesHawk port of route up17 (track "NESHAWK PORT", 2026-10-10 12:55 - 15:49)

Owner of this file: the NesHawk port of up17. Files: `u17p_*.py`, `logs/fix/core_u17*`, this file. Nothing of another
owner was edited (core_check_toads.py is imported and subclassed in `u17p_port.py`; `u16p_*.py` were copied to `u17p_*.py`).
All commands from `../toads`. Nothing here writes memory; savestates are used for the search only and every
list named below was replayed from power-on afterwards.

## 0. Result

**up17 on NesHawk: T. Bird cut on frame 44,994, landing 2,074 -> 42,920 frames / 60.0988 = 714.157 s = 11:54.16**
(quickerNES: 44,986 = 11:54.02; the port is 8 frames = 0.13 s slower). Under 12:00.00 by 5.84 s (351 frames), under the
record's 749.25 s by 35.09 s.

| | file | sha1 |
|---|---|---|
| NesHawk input list, de-mashed (RELEASE THIS ONE) | `logs/fix/core_u17pd.inputs.txt` (45,024 frames = cut + 30 idle) | cb6b61dc8db48a4895d32779f458a3fa708cf8d4 |
| NesHawk movie, de-mashed | `logs/fix/core_u17pd_NesHawk.bk2` (= `core_u17vd_NesHawk.bk2`; `Core NesHawk`, one empty lead-in frame, 45,025 rows) | |
| NesHawk input list, mashed (the port of `logs/up17.inputs.txt` as it is) | `logs/fix/core_u17p.inputs.txt` | c1839ca532a648575e7d8faab3abcef6930c061e |
| NesHawk movie, mashed | `logs/fix/core_u17p_NesHawk.bk2` | |
| reference capture (quickerNES, `logs/up17.inputs.txt` copied to `logs/fix/core_u17.inputs.txt`, sha1 2344f9b4) | `core_u17q.*`: end RAM sha1 cfa6cb83, T. Bird cut 44,986 | |

Final RAM sha1 after the last input, both NesHawk lists: **789ff9f389125785a8c188505c6f92ef6484410d**.

Proof, all on NesHawk (read back in every run: board `AxROM`, memory domain `PPU Bus` present):
- `core_check`-style port log `logs/fix/core_u17_run_p.txt`: COMPLETE, then
  `verify 1: straight replay from power-on on NesHawk: 45024 frames, SHA-1 789ff9f3 MATCH; 13 -> 254 at [44575, 44994]`
  `verify 2: straight replay from power-on on NesHawk: 45024 frames, SHA-1 789ff9f3 MATCH; 13 -> 254 at [44575, 44994]`
- Mashed list, third replay with per-frame RAM capture `u17v1` (`core_u17_run_v1.txt`): 789ff9f3.
- De-mashed list, three more replays from power-on: captures `u17vd`, `u17vd2` (`core_u17_run_vd.txt`, `_vd2.txt`) and the
  screenshot replay (`core_u17pd_shots.txt`): all 789ff9f3; `u17vd` = `u17vd2` on every frame (`core_u17pd_ramcmp2.txt`).
- **De-mashed = mashed, byte for byte, on all 45,025 captured frames** (`core_u17pd_ramcmp.txt`: `u17v1` against `u17vd`,
  lag flags equal too).
- **Hands-off movie playback** (no bridge, no joypad calls; `core_check_toads.py movie ... --keep-header`): both movies loaded
  NesHawk and give the replay's RAM at all 129 marks (every level-byte change and every 600 frames), cuts on movie frames
  44,576 and 44,995 = replay frames 44,575 and 44,994: `core_u17m_moviecmp.txt` (mashed), `core_u17md_moviecmp.txt` (de-mashed),
  both `VERDICT: MOVIE MATCHES THE REPLAY on NesHawk`.
- Scan (`core_u17pd_scan.txt`, `core_u17p_scan.txt`): Left+Right 0, Up+Down 0, tokens other than the 8 controller-1 buttons 0,
  Start on 13 frames, all on the title screen (1164-1176, one press held; the game's pad byte has the Start bit on 1176-1185
  only), Select on 176 frames (115 presses). De-mashed list: at most 5 A presses and 4 B presses in any 60 frames (mashed: 30).
  Second-pad bytes: `$2C` nonzero only on frame 1 (NesHawk's power-on RAM pattern, before the game clears it), `$2A` = 1 on
  the game's own five forced walks, as in the reference.
- Lives / health / score when each level ends equal the reference's, level by level (`core_u17pd_levels.txt`):
  3/47/004000, 2/0/043600, 2/31/086600, 2/47/091600, 3/47/143600, 3/47/168600, 3/47/179600, 4/47/233800, 4/47/284550,
  5/47/334550; the same six lives changes.
- The toad's own track equals the reference's on 40,175 of 40,237 polled frames up to the Queen's last hit
  (`core_u17pd_track.txt`); the 62 others are in Level 8 after Robo-Manus is dead (section 2).
- Pictures on NesHawk (`logs/fix/core_u17_shots/u17pd_f*.png`): toad standing on picture 2075 (landing 2074); picture 44994 =
  status bar and tower tip on black; 44995-45003 black; **Professor T. Bird's screen from picture 45004 (cut + 10)**, text
  "OKAY" on 45014.

Level by level (frame on which the level byte arrives; NesHawk minus quickerNES):

| level | quickerNES | NesHawk | |
|---|---|---|---|
| landing | 2,074 | 2,074 | 0 |
| Turbo Tunnel | 2,488 | 2,490 | +2 (warp animation 180 lag frames instead of 179, card +1) |
| Arctic Caverns | 4,748 | 4,750 | +2 |
| Karnath's Lair | 9,852 | 9,854 | +2 |
| Level 8 | 12,313 | 12,317 | +4 (Karnath's load +1, card +1) |
| Terra Tubes | 16,186 | 16,195 | +9 (two heavy frames lag on NesHawk only, +2; the last blow lands 2 frames later, +2; card +1) |
| Rat Race | 25,969 | 25,978 | +9 |
| Clinger-Winger | 27,912 | 27,922 | +10 (card +1) |
| The Revolution | 34,788 | 34,799 | +11 (card +1) |
| Dark Queen | 42,965 | 42,974 | +9 (the tower lags 2 frames less) |
| Queen's last hit | 43,906 | 43,915 | +9 |
| cut to the Queen's speech | 44,566 | 44,575 | +9 |
| **cut to Professor T. Bird** | **44,986** | **44,994** | **+8** (ending 1,079 frames instead of 1,080: final wait 56 = the floor, speech 9 + 14, first rise 171) |

## 1. How it was made (repeat it with these commands)

    cp logs/up17.inputs.txt logs/fix/core_u17.inputs.txt
    python core_check_toads.py run u17q --core quickerNES --inputs logs/fix/core_u17.inputs.txt --tail 0     # cfa6cb83, cut 44986
    python u17p_port.py port u17p --ref u17q --core NesHawk --end-steer 3600      # 2,156 s + two verify replays
    python core_check_toads.py run u17v1 --core NesHawk --inputs logs/fix/core_u17p.inputs.txt --tail 0
    python u17p_scan.py logs/fix/core_u17p.inputs.txt u17v1
    python u17p_demash.py u17p u17v1 logs/fix/u17v_demashed_up17.inputs.txt u17pd
    python core_check_toads.py run u17vd  --core NesHawk --inputs logs/fix/core_u17pd.inputs.txt --tail 0     # and u17vd2
    python u17p_ramcmp.py u17v1 u17vd ; python u17p_ramcmp.py u17vd u17vd2
    python u17p_scan.py logs/fix/core_u17pd.inputs.txt u17vd ; python u17p_levels.py u17q u17vd
    python core_check_toads.py bk2 u17p ; python core_check_toads.py bk2 u17vd      # copy core_u17vd_NesHawk.bk2 -> core_u17pd_NesHawk.bk2
    python core_check_toads.py movie u17m  logs/fix/core_u17p_NesHawk.bk2  --keep-header ; python u17p_moviecmp.py u17m u17v1
    python core_check_toads.py movie u17md logs/fix/core_u17pd_NesHawk.bk2 --keep-header ; python u17p_moviecmp.py u17md u17vd
    python u17p_shots.py u17vd u17pd

The port: 42 Select re-rolls (Level 8: 15, Terra Tubes 3, Clinger-Winger 4, tower 6 - from polled index 33,372 with the loose
key -, Queen 14), 1 re-alignment (2 idle polled frames, section 2), 8,709 tries. Ending searched on NesHawk by `end_tail`
(128 s of the 3,600 s budget): Up on 44,299, Down+Select on 44,373 (timer draws (57, 3), (32, -1): parks on the floor),
Up on 44,573 (speech polls on its 9th frame), A on 44,584.

## 2. Three things that are new against the up16b2 port (facts for the next port)

1. **`core_check_toads.py port` gets STUCK on up17** (first try, `logs/fix/core_u17_run_p_first_stuck.txt`): at the end of
   Level 8 the level byte turns 254 two polled frames later on NesHawk than the polled-frame mapping expects, every later
   input would be fed two polled frames early, and no Select re-roll can repair a shift. Cause: the toad's LAST attack on
   Robo-Manus is rolled by the dice (B in the air on reference frame 15,717). quickerNES rolls animation 24 -> 28 (kill on
   game frame `$0B` = 146), NesHawk rolled 38 -> 87 (kill on 148). The toad's height track is the same for those frames, so the
   port's key saw only "boss alive 2 frames longer", called it a passing difference, and went on 2 game frames late.
   `u17p_port.py` (subclass of the Porter) adds a RE-ALIGNMENT step: when the tracks part for good and the level bytes differ
   (or a load lies just behind), try inserting n idle polled frames on this core / skipping n reference polled frames, and keep
   the first variant after which the track holds 300 polled frames. Here: 2 idle polled frames before reference frame 16,176.
2. **The de-mash by polled-frame mapping is not automatically harmless on another core.** Because of the 2-frame shift the
   reference's cosmetic A,B mash (meant for the forced walk) reaches two frames on which the toad still obeys: NesHawk frames
   15,897 (A: the toad jumps) and 15,898 (B). Dropping them gives another run (the first de-mashed list,
   `core_u17pd_nokeep_diverges.inputs.txt`, takes one frame longer through the next card and dies in Terra Tubes).
   `u17p_demash.py` therefore KEEPS a press when the frame is polled on NesHawk and the game's own pad byte `$29` shows the
   button: exactly those 2 frames (two single presses, not turbo). With them the de-mashed list is byte-identical in RAM to
   the mashed one on every frame. A/B presses 677/361 -> 476/162.
3. **Lag is a lottery on NesHawk.** Two more searches of the same route (`u17p2`, `u17p3`, section 3) reached the Queen's
   last hit on 43,916 and 43,920 (this port: 43,915) although both killed Robo-Manus 2 frames sooner: Terra Tubes and
   Clinger-Winger each cost 0 or 2 frames more depending on the dice, the tower -2 to +6. Two heavy frames of Level 8
   (reference frames 14,479 and 14,494, objects despawning) lag on NesHawk and not on quickerNES (seen frame by frame in this
   port; the Level 8 totals of the other two runs agree). A card page's length depends on the
   alignment it is entered with on NesHawk too: measured in run `u17p2` with one Select toggle on each of the 90 polled frames before it
   (frames against that run's untouched page): 1 -> 3: 0 / -1 / -2; 3 -> 4: 0 / +1; 4 -> 6: 0 / +1 / +3; 6 -> 8: 0 / +1 / +2; a toggle
   inside a forced end-of-level walk (8 -> 9, 9 -> 10, 10 -> 11, 11 -> 12, tower -> Queen) changes nothing at all.

## 3. What else was tried (not the result; do not use these lists)

- `u17p_port.py --strict-hits`: a passing difference in which a tracked enemy's (id, health) differs goes to the re-roll
  search first. It finds the kill on the reference's frame at once (Select 7 polled frames earlier, 8 tries): Level 8 ends on
  16,172 instead of 16,174, no re-alignment needed. Run `u17p3` (strict hits only) was stopped by me in the ending search:
  last hit 43,920 (tower +6), it could not beat 44,994.
- `u17p_port.py --page-opt`: one Select toggle before each card page, chosen for the earliest arrival 60 polled frames into
  the next level. Run `u17p2` (strict hits + page-opt): 2 frames gained on the 1 -> 3 page, none elsewhere, session cut 44,995.
  **Its written list did NOT replay (verify 1: MISMATCH)**: a bookkeeping bug of mine (a rejected trial's Select stayed in the
  list when no toggle was better; the same kind of bug the first `port` had). Fixed in `u17p_port.py` (comment "BUG FIXED") and
  checked on a 5,200-frame run with both kinds of page (`u17pt`: session RAM sha1 07695168 = straight replay `u17vt`);
  `core_u17p2.*` is a dead list. The result of section 0 was made with neither option (plain port + re-alignment).
- Run `u17p5` (strict hits, tower with the loose key from its first frame): Level 12 on 34,796 (3 frames ahead of the
  result port), tower +1 against quickerNES (result port -2), Level 13 on 42,974 and last hit on 43,915 = the result
  port's frames exactly; stopped in the ending search, it could only tie.
  So four searches of this route end within 5 frames of each other at the last hit (43,915 / 43,915 / 43,916 / 43,920):
  44,994 is what NesHawk gives for up17 without a lag-aware search; 2 to 4 frames more would need one.
- `core_u17p4`, `core_u17v2`, `core_u17pt`, `core_u17vt`: stopped or test runs. `core_u17qd` = quickerNES capture of the
  verifier's de-mashed list (byte-identical to `u17q` on every frame, my own check).

## 4. Tools

`u17p_port.py` (port + re-alignment; options `--strict-hits`, `--page-opt`; refuses tags that do not start with `u17`),
`u17p_demash.py` (the other list by the port's own mapping, incl. inserted polls; keeps presses the game reads on this core;
`--no-keep` for the plain mapping), `u17p_ramcmp.py`, `u17p_moviecmp.py`, `u17p_scan.py` (copies of `u16p_*`),
`u17p_levels.py` (lives / health / score at every level end, two captures), `u17p_shots.py` (replay with pictures around the
landing and the T. Bird cut). `*.backup` copies sit next to the scripts that were patched by script.

## 5. Caveats

- One machine, BizHawk 2.11.1, the two NES cores. No console, no other emulator.
- The port is not the same play frame for frame as up17 in Level 8's last 450 frames: Robo-Manus dies 2 game frames later
  (other final attack) and the toad makes one extra jump before the fanfare. Everything else is the reference's play; the
  Queen's exact position also matches on all 801 polled frames of the fight.
- Like up17 itself: tool-assisted, frame-exact, not humanly performable. 115 single Select presses.
- The list has 30 idle frames behind the T. Bird cut; the movies one empty lead-in frame (movie frame = list frame + 1).
