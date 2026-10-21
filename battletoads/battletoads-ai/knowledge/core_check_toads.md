# Core check: does the run play on BizHawk's accurate NES core (NesHawk)?

Track CORE, 2026-10-09. Tool: `core_check_toads.py`. Raw output: `logs/fix/core_*` (per-frame 2 KB RAM captures
`core_<tag>.ram`, lag flags `core_<tag>.meta.tsv`, summaries `core_<tag>.json`, run logs `core_run_<tag>.txt`).
Everything below was run on this machine, BizHawk 2.11.1, ROM SHA-1 5C3A497A (file) / D85C9FF4 (without header).
Which core actually loaded was checked in every run from inside the emulator (NesHawk has a "PPU Bus" memory domain
and reports board `AxROM`; quickerNES has neither and reports `aorom`).

## Verdict

1. **The published input file does NOT play on NesHawk.** `up14` (and its movie `battletoads_ai_12m23s.bk2`) is a
   quickerNES movie. On NesHawk it never gets past the title screen at the right time: the Start press comes one frame
   before the title looks at the controller. When the input list runs out the game is in the title/attract loop
   (level byte 254, no toad).
   No blank lead-in fixes it: +0 and +1 miss the title, +2 and +3 start the game and then lose Level 1.
2. **The cause is not the game's speed and not a glitch that only the fast core allows. It is two small things:**
   - *Lag frames.* NesHawk needs 1 frame more to boot, 1 more to bring the title up, and 1-2 frames more or fewer at
     most level loads. Over the whole run the two cores take the **same number of frames, within 2, at every level
     boundary**; between the landing (frame 2,074 on both) and the cut to the Queen's speech (frame 46,751 on both) each
     has exactly 2,530 lag frames. A fixed input list cannot follow a load that is a frame longer.
   - *Dice.* The game's random numbers (`$25-$28`) are scrambled in the idle loop, so they follow the CPU time of every
     frame. They differ between the cores on practically every frame of play (identical on 50 of 13,714 compared frames).
     Everything that does not roll dice plays identically; the first thing that does - the toad's random attack on
     Robo-Manus - comes out differently.
3. **The route itself is sound on the accurate core.** With the inputs fed by *polled* frame (lag compensated) and
   39 extra Select presses (the project's own re-roll method, `rngfit.py`'s idea), the same route was played to the end on
   NesHawk and **verified from power-on: two straight replays with identical RAM SHA-1 and one hands-off movie
   playback with the same final RAM.** Every trick works there with the same inputs: the Turbo Tunnel skip, the
   Level 4 spike-pit boost and mega warp, Karnath's Lair, the Terra Tubes line and death exit, the rat boot,
   Clinger-Winger, The Revolution, the Queen.
4. **Times on NesHawk** (clock from the landing, frame 2,074, to the cut to Professor T. Bird):

   | route | quickerNES | NesHawk port (verified) | |
   |---|---|---|---|
   | `up14` as published | T. Bird cut 47,253 = **12:31.75** | 47,228 = 12:31.33 | 25 frames less is the ending's dice (final wait 114 instead of 137, speech 9 instead of 11), not the core |
   | `up14e` (track END's steered ending) | 47,170 = **12:30.36** | **47,170 = 12:30.36** (`p14e`); 47,169 = 12:30.35 (`p14f`, ported from scratch in one command) | ending re-steered on NesHawk with END's own tool |
   | the record | 12:29.25 = cut at 47,102 or earlier | | neither route beats it on either core |

5. **For the claim:** a time measured on quickerNES is a fair time (the accurate core gives the same frame counts), but
   an input file is only proof on the core it was made for. The corrected run should be published with a NesHawk
   movie next to the quickerNES one, and the headline number should be the one that holds on NesHawk. Section 7.

## 1. What was run

| tag | what | core | result |
|---|---|---|---|
| `q` | `up14` inputs + 800 frames of A every other frame, through the bridge | quickerNES | frame 46,751: RAM SHA-1 **e2a1d2dc** (the published hash); T. Bird cut 47,253 |
| `n0` | the same, same frame numbers | NesHawk | title missed; Level 1 entered at 9,761 by accident; ends in the attract loop |
| `n1` | one blank frame first (+1) | NesHawk | title missed (Start is released one frame before the title's first poll); the same end |
| `n2`, `n3` | +2, +3 blank frames (first 12,000 frames) | NesHawk | Start taken, Level 1 at 1,414, but the toad never finishes Level 1 (quickerNES leaves it at 2,469) |
| `mv_keep` | the published `.bk2`, hands-off (`verify_movie.lua` style), config prefers NesHawk | **quickerNES loaded** | reproduces e2a1d2dc: see section 6, this is a trap |
| `mv_nes` | the same movie with its header changed to `Core NesHawk` | NesHawk | same failure as `n0` (title missed, never plays) |
| `e4` | lag-compensated replay (inputs by polled frame), no other change | NesHawk | Levels 1, 3, 4, 6 and the Level 8 climb identical; parts for good at Robo-Manus, frame 15,999 (reference 16,000) |
| `p1`, `p2` | port: lag compensation + Select re-rolls | NesHawk | `p2` complete: 49,384 frames incl. the reference's 800-frame tail, 39 Select toggles, 0 banned presses |
| `pv1`, `pv2` | `p2`'s input list replayed straight from power-on, twice | NesHawk | both SHA-1 **aaab52ab** at the end, equal at all 82 600-frame marks; T. Bird cut 47,228 |
| `p2mv` | `p2` as a `.bk2` (`Core NesHawk`, one lead-in frame), hands-off, no bridge | NesHawk | same RAM at the T. Bird cut and at the end as `pv1` |
| `q14e` | `up14e` inputs | quickerNES | SHA-1 **a1b291b6** at 47,200 (track END's hash); T. Bird cut 47,170 |
| `p14e` | port of `up14e`; ending searched on NesHawk by END's `end_tail.append_tail` at the last hit | NesHawk | 47,200 frames, 0 banned presses, T. Bird cut **47,170** |
| `v14e1`, `v14e2` | `p14e`'s input list straight from power-on, twice | NesHawk | both SHA-1 **2c596a7d** at 47,200; T. Bird cut 47,170 |
| `m14e` | `p14e` as a `.bk2` (`Core NesHawk`, one lead-in frame), hands-off, no bridge | NesHawk | same RAM as `v14e1` at the T. Bird cut (movie frame 47,171) and at the end |
| `p3`, `v3a`, `v3b` | first from-scratch port of `up14` with the final options, and two replays of its input list | NesHawk | **the replays did not reproduce the session** (they agree with each other and leave the reference's track at frame 15,975). A bug in the tool, see section 4; found only because the result was replayed |
| `p5` | from-scratch port of `up14` with the fixed tool (35 re-rolls, 1,834 s), replayed twice by the tool itself | NesHawk | both replays SHA-1 **d715c509** = the session's; Level 13 at 45,055; T. Bird cut 47,226 (plain ending) |
| `p14f` | from-scratch port of `up14e` with the ending search, one command (2,732 s + the replays) | NesHawk | 47,199 frames, 0 banned presses; last hit 46,083, T. Bird cut **47,169**; replays SHA-1 **32cd3dab** = the session's |
| `v14f`, `m14f` | `p14f`'s input list: a third straight replay with the per-frame capture, and hands-off as a `.bk2` | NesHawk | SHA-1 32cd3dab again; the movie's RAM equals the replay's at both cuts (movie frames 46,750 and 47,170) and at the end |
| `psmoke` | the tool as delivered (after the last edits), `up14e` with `p14f`'s toggles and a 120 s ending search | NesHawk | writes the same input list as `p14f`; replay MATCH 32cd3dab |

Input lists: `logs/fix/core_p2.inputs.txt`, `core_p14e.inputs.txt`, `core_p5.inputs.txt`, `core_p14f.inputs.txt`;
movies `logs/fix/core_p2_NesHawk.bk2`, `core_p14e_NesHawk.bk2`, `core_p14f_NesHawk.bk2` (test movies, one empty
lead-in frame like the published one). `core_p3.inputs.txt` is the bad list of the bug in section 4: do not use it.

## 2. The straight replay: where it breaks and what differs

Same frame numbers (`n0` against `q`):
- Frame 0: the power-on RAM differs (quickerNES mostly `FF`, NesHawk the `00 00 00 00 FF FF FF FF` pattern: 1,025 of
  the 2,048 bytes). The game clears its RAM; this does not matter afterwards.
- From the first frames NesHawk is **one frame behind**: the game's frame timer `$0B` reads 7 where quickerNES reads 8
  at frame 20. First controller poll: frame 1,162 on quickerNES, 1,163 on NesHawk.

One blank frame first (`n1`, NesHawk frame f+1 against quickerNES frame f):
- The same game state from frame 1 to frame **1,170**: dice, one idle-loop counter `$75` and the stack aside, a
  single byte (`$76`, `$19` or `$05`) differs on 12 of those frames and nothing on the others; on 125 frames the whole
  2 KB is identical, dice included.
- **First divergence: frame 1,171.** The title screen needs 13 frames to come up on NesHawk and 12 on quickerNES, so it
  first reads the controller on NesHawk frame 1,176. The input file holds Start on 1,171-1,174 (1,172-1,175 with the
  blank frame): released before the title looks. quickerNES starts the game there; NesHawk stays on the title.
- After that nothing matches: SHA-1 at every later 600-frame mark and level change differs
  (`logs/fix/core_cmp_q_n1_s1.json`, `core_cmp_q_n0.json`; first rows below).

| quickerNES frame | level byte q / NesHawk(+1) | SHA-1 q | SHA-1 NesHawk | bytes differing (not dice) |
|---|---|---|---|---|
| 1 | 0 / 0 | 075918c5ea | 075918c5ea | 0 (0) |
| 600 | 0 / 0 | d8e117bc1f | a827c33701 | 5 (1) |
| 1,161 (0 -> 255) | 255 / 255 | db616e40a2 | 01acfaee31 | 6 (2) |
| 1,173 (254 -> 255) | 255 / 254 | 8c832b3b05 | d4834d0ddc | 44 (40) |
| 1,185 (255 -> 0, game started) | 0 / 255 | 726279585f | 80e1613a5b | 368 (364) |
| 1,200 and every later mark | differ | | | hundreds |

## 3. With the lag taken out: where the GAME first differs

`core_check_toads.py elastic` feeds the reference's inputs by polled frame: the k-th frame on which the game reads the
controller gets the input that quickerNES's k-th polled frame got; a lag frame is given the same input again. Nothing
else is changed. (quickerNES reports one controller read on frame 1, before any game code looks at it; NesHawk does
not. That one is skipped.)

- **Levels 1, 3, 4, 6 and the whole Level 8 climb play identically on NesHawk**: the toad's x, y, height, depth and
  health, the camera, the lives and the level byte are equal on all 13,495 polled frames from Level 1's start to
  frame 15,998; on 6,175 of them the whole RAM is equal apart from the dice, the idle counter, the stack and a sound
  buffer. The Turbo Tunnel skip (pointer corruption), the spike-pit boost (the game reads collision out of video
  memory there) and both warps are in that stretch.
- **First real divergence: NesHawk frame 15,999 = reference frame 16,000, 3,541 frames into Level 8, in the
  Robo-Manus fight.** The toad stands at x 103 beside the boss (x 109, health 7) and presses B: the game rolls which
  attack. quickerNES rolls the jump-smash (the toad's animation `$3B5`, then its height: 33, 35, 38 ...); NesHawk
  rolls a different blow that knocks the boss away (boss x 113, 117, 121 ...). **It is the dice, not lag and not
  position**: lag flags and positions were equal up to that frame. From there the old inputs fight a boss that is
  somewhere else, and the run is lost.
- Harmless dice differences before that: one cosmetic object byte (`$3B3`) from frame 5,470 of Level 4 on, and
  short-lived debris/particle objects.

Lag, measured on the complete NesHawk port against quickerNES (runs `pv1` and `v14e1`, the same up to the last
hit; `logs/fix/core_pcmp_q14e_v14e1.md` lists 131 marks - every level change and every 600 frames - with both
SHA-1s): 20 places differ, all by 1 or 2 frames.
- At loads and pages (14): boot +1, title +1, then -1, -1, -1, +1, +1, -2, +1, -1, +2, +1, +1, -1 (NesHawk minus
  quickerNES; net +2).
- In play (6): quickerNES drops a frame NesHawk does not at 15,090 (Level 8), 22,019 and 22,080 (Terra Tubes) and
  41,049 (The Revolution); NesHawk drops one quickerNES does not at 40,851 and 41,853 (The Revolution). Net -2.
- Together: 0 at Level 13's first frame, and never more than 2 apart on the way.

## 4. The port to NesHawk

`core_check_toads.py port` = the lag-compensated feed plus the project's re-roll method: when the toad's track (x,
height, y, z, health), the tracked enemies (Robo-Manus 0x7D, Buzzball 0x7B, Hornhead 0x5C, walker 0x62, Queen 0x7E:
id, position, health) or the Queen's hit counter leaves the reference's, go back up to 180 polled frames, toggle Select
on one earlier frame (then 2-4 frames), and keep the first variant that follows the reference for 12 more frames.
Savestates are used for the search only; the result is an ordinary input list replayed from power-on afterwards.

| level | re-rolls needed on NesHawk, run `p1`+`p2` | run `p5` (from scratch, final tool) |
|---|---|---|
| 1, 3, 4, 6, 10 (Rat Race) | 0 | 0 |
| 8 (Robo-Manus) | 17 | 15 |
| 9 (Terra Tubes) | 1 | 1 |
| 11 (Buzzball) | 2 | 4 |
| 12 (The Revolution) | 5 (one needed three presses, 1,209 tries) | 7 (1 exact, then 6 with the loose key) |
| 13 (Dark Queen) | 10 with her exact position in the key, then **stuck**; 2 more once only the toad's track, her health and the hit counter are asked for | 8 (loose key from the start) |

- 39 Select toggles in all (`p5`: 35), 0 Left+Right / Up+Down frames, no other input changed up to the last hit.
  The toad's own track is the reference's on every polled frame of the run (43,399 of 43,399 for `up14e`, run
  `v14e1`).
- The Queen cannot be put back on her exact path by re-rolls (1,680 tries failed at reference frame 45,845). It is not
  needed: with the loose key the same blows land on the same frames. `port` now uses the loose key in Level 13 from
  the start, and falls back to it in any level where the strict key cannot be restored.
- A from-scratch port of a 47,000-frame route took 31 minutes (`p5`: 35 re-rolls, 2,337 tries), 46 minutes with
  the ending search (`p14f`), plus 8 minutes for each verification replay, on one emulator (NesHawk runs at
  100-160 frames/s here with the per-frame RAM read). Two ports of the same route need not be identical: `p1` kept
  the enemies' exact positions through The Revolution (one re-roll needed 1,209 tries) and reached Level 13 on frame
  45,057 like quickerNES; `p5`/`p14f` gave that up after 1,200 tries, went on with the loose key, and reached it on
  45,055 (two lag frames fall differently when a walker stands elsewhere). `port` now gives up on the exact position
  after 300 tries.
- **A bug the replay caught.** The first from-scratch run (`p3`) reported COMPLETE, and its input list did not replay:
  a rejected trial that had started from an earlier savestate than the accepted one left its Select in the list that
  was written out. The search now rewinds to the earliest state any trial touched, and `port` replays its own result
  from power-on twice (`--verify 2`) and prints MATCH or MISMATCH against the session. `p2` and `p14e` were made before
  the fix; they are trusted because their written lists were replayed (`pv1/pv2`, `v14e1/v14e2`, and hands-off as
  movies) and gave the session's RAM. Nothing here is claimed from a search session alone.
- **The ending has to be searched per core.** Its length is a lottery on the same dice (track END,
  `knowledge/end_timing.md`: the game waits for the Queen's whirl timer `$4ED+3` to reach zero). The plain port of
  `up14` therefore ends 25 frames *sooner* on NesHawk (final wait 114 instead of 137, speech 9 frames instead of 11) -
  an independent confirmation of END's model on another core. For `up14e` the port hands the live NesHawk emulator to
  END's `end_tail.append_tail` on the last-hit frame (`--end-steer 900`): it found the floor again in 598 s (Select at
  46,445, Down 46,537, Up 46,550, Up 46,749, A 46,760: final wait 56, speech 9, reload 14), T. Bird cut 47,170.

## 5. Level by level: both cores, same route (`up14e`)

Frame on which the level byte changes, from the `run` logs of `q14e` and `v14e1`
(`logs/fix/core_pcmp_q14e_v14e1.md` has all 131 marks - every level change and every 600 frames - with both SHA-1s;
the toad/enemy key is the same at every one of them). Lag frames from the landing to the T. Bird cut: 2,551 on each.

| event | quickerNES | NesHawk | difference |
|---|---|---|---|
| first controller poll after power-on | 1,162 | 1,163 | +1 |
| Level 1 (level byte 1) | 1,413 | 1,414 | +1 |
| landing = clock start | 2,074 | 2,074 | 0 |
| Level 3 | 2,491 | 2,491 | 0 |
| Level 4 | 4,753 | 4,754 | +1 |
| Level 6 (byte 8) | 9,863 | 9,862 | -1 |
| Level 8 (byte 7) | 12,458 | 12,458 | 0 |
| Level 9 (byte 11) | 17,340 | 17,339 | -1 |
| Level 10 (byte 9) | 27,326 | 27,324 | -2 |
| Level 11 (byte 10) | 29,273 | 29,273 | 0 |
| Level 12 (byte 5) | 36,152 | 36,151 | -1 |
| Level 13 | 45,057 | 45,057 | 0 (whole RAM identical on that frame, SHA-1 79fe4516 on both cores) |
| last hit on the Queen | 46,085 | 46,085 | 0 |
| cut to the Queen's speech | 46,751 | 46,751 | 0 |
| back on the tower | 46,760 | 46,760 | 0 |
| **cut to Professor T. Bird** | **47,170** | **47,170** | **0** |

The from-scratch port `p14f` differs from this column only after Level 12 begins: The Revolution is played with the
loose key there, two lag frames fall differently, Level 13 starts on 45,055, the last hit is on 46,083, the Queen's
speech cut on 46,749, and the cut to T. Bird on **47,169** (final wait 57 instead of 56). Its toad/enemy key equals
the reference's on 43,398 of 43,399 polled frames; the one that differs is the T. Bird cut itself
(`logs/fix/core_pcmp_q14e_v14f.md`).

## 6. A trap when checking a movie on another core

BizHawk plays a `.bk2` on **the core named in the movie's header**, whatever the config's preferred core is. The
published movie says `Core quickerNES`. Played hands-off with a config that prefers NesHawk it loaded quickerNES and
reproduced the published hash - which looks like "passes on NesHawk" and is not. To test another core the header line
has to be changed (`core_check_toads.py movie` does that on a copy) or the inputs sent through the bridge
(`TOADS_CORE=NesHawk`, which is what `run`/`port` do). Always read back which core loaded.

## 7. What this means for a credible record claim

- **The time is not an artefact of the fast core.** The accurate core plays the same route in the same number of
  frames (0-2 frames apart at every level boundary, 0 or 1 at the finish). Whoever says "quickerNES is inaccurate, so
  the time is fake" is answered by a NesHawk movie.
- **But the published file is proof on quickerNES only.** A viewer who opens the `.bk2` in BizHawk gets quickerNES
  without asking (section 6), so the release keeps working as its README says. Whoever checks it deliberately on
  NesHawk - the first thing an emulation-minded critic does - sees it sit on the title screen. The corrected release
  should ship a NesHawk movie as well and say that each movie is for its core.
- **The corrected route should be claimed on NesHawk.** The margin being fought for is one to two seconds; the two
  cores agree to the frame at the finish only when the ending is steered on each (a plain port can land up to 256
  frames apart there). Procedure, about an hour of machine time:
  1. `cp logs/<route>.inputs.txt logs/fix/core_<route>.inputs.txt`
  2. `python core_check_toads.py run qR --core quickerNES --inputs logs/fix/core_<route>.inputs.txt --tail 0`
     (must print the route's SHA-1 and T. Bird cut)
  3. `python core_check_toads.py port pR --ref qR --core NesHawk --end-steer 900`
     (it ends with two replays from power-on: both must say MATCH; the second `13 -> 254` they print is the T. Bird
     cut. `--mods-from <earlier port>` skips the search only when the route is identical up to the re-rolled frames.)
  4. For the per-frame captures and the table: `python core_check_toads.py run vR1 --core NesHawk --inputs
     logs/fix/core_pR.inputs.txt --tail 0` (its SHA-1 at the end must be the one step 3 printed).
  5. `python core_check_toads.py bk2 pR` and `python core_check_toads.py movie mR logs/fix/core_pR_NesHawk.bk2 --keep-header`
     (hands-off playback), `python core_check_toads.py pcmp qR vR1` (the table of section 5).
- **Say what it is.** Tool-assisted, emulator, under the human category's rules; verified on BizHawk 2.11.1 on both
  NES cores. That statement is true today for `up14e` at 12:30.36 (12:30.35 for the NesHawk port `p14f`) - which is
  still 1.1 s short of the record.

## 8. Limits

- Two emulator cores, one machine, one BizHawk version. No console, no other emulator (Mesen, FCEUX). The dice follow
  CPU time so closely that any other emulator, or a console, will need its own re-rolls and its own ending; what
  carries over is the route and, as measured here, the frame counts.
- The re-rolled fights are matched on the toad's track and the enemies' health, not on every byte: random debris and
  one cosmetic byte differ, and in Level 13 the Queen's position differs between the cores while every blow lands on
  the same frame.
- `port` leans on `end_tail.py` / `end_model.py` (track END) for the ending; if those change, re-run step 3.
- The 800 frames of A-mashing after `up14`'s inputs (`q`, `p2`) are a measuring tail, not part of any route; `up14e`
  (`q14e`, `p14e`) carries its own ending and needs none.
