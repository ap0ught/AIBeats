# Ninja Gaiden legal-run toolkit (`ng/solve/`)

## CHAINED 4-1 CONTROL STATE (Acts 1-3, power-on chain)

* **Round 5 (chain), 2026-10-23 ~04:45-06:00, PAUSED by the owner: chain UNCHANGED (still 3-3 control 15,140, no 4-1
  control state).** Nothing new verified. Partial (Mesen only, NOT on NesHawk): 2-2 rows 0-403
  `states/tmp/c5_p22_prefix.inputs.txt` (tk rows 0-206 + segga r6c) reach room 6 X<=384 at t 404 (old 437, TAS 392),
  hp 16, ninpo 5 (+5 lantern); NesHawk replay of it matches (state `states/c5_22t404`, frame 6,753). Details/resume:
  legal_a12_notes.md and legal_a34_notes.md "Round 5 (chain)".
  New tools: `work/c5/segga.py` (Mesen segment GA: earliest goal, ninpo bonus, hp/item constraints),
  `work/c5/segpipe.py` (+ spec `work/c5/p22_spec.json`), `work/c5/b33ga.py` / `b33grid.py` / `b33lib.py` (3-3),
  `work/c5/mboot.py` (Mesen boot with NesHawk pads), `work/c5/nhstate.py`, `hbwatch.py`, `mwatch.py`, `trcmp.py`.
  `ng/solve/fast.py`: `run_chunked()` (chunked batches + progress + pool restart when a Mesen dies) - fixes the
  128-candidate time-out (it was the caller's command time-out on one huge blocking batch). Launch long Mesen jobs
  with the Bash tool's run_in_background, NOT `nohup ... &` (two such jobs hung with idle Mesen processes).

* **NOT REACHED** in this session (10-hour time-box; 3-3 Basaquer unsolved on the chain). Furthest VERIFIED
  power-on chain: **3-3 control, frame 15,140**
  - inputs `logs/tk_to33.inputs.txt` (15,140 rows; `assemble.py --serial`: two power-on replays MATCH, RAM sha1
    65646d4152d0, trace sha1 8196d29c708c; `check_inputs.py ... --period 5 --hold 2 --release 2 --windows
    600:109,1800:246` PASS; 0 deaths, 3 cutscenes skipped)
  - state `states/tk_3-2_c1_end.State` (3-3 control: hp 8, ninpo 23, Art of the Fire Wheel); history = that file
    (also `states/tmp/tk_hist33n.inputs.txt`).
  - stages (control -> control; logs/results.json; record = record_events.json split):

    | stage | file | frames | vs TAS | vs record |
    |---|---|---|---|---|
    | 1-1 | logs/tk_1-1_s11 (coordinator's fastcore 1-1) | 2,373 | +79 | +63 |
    | 1-2 | logs/tk_1-2_s11 (round-1 rows) | 838 | +4 | **-3** |
    | 2-1 | logs/tk_2-1_s11 (a12r3 rows) | 2,964 | +162 | +59 |
    | 2-2 | logs/tk_2-2_m2 | 3,448 | +553 | +347 |
    | 2-3 | logs/tk_2-3_bh2 (sword only, 0 ninpo) | 1,105 | +275 | +272 |
    | 3-1 | logs/tk_3-1_a2 | 1,638 | +33 | +35 |
    | 3-2 | logs/tk_3-2_c1 | 2,600 | +293 | +272 |
    Cumulative at 3-3 control: 15,140 vs the record's ~14,093 on our axis = **record +1,047 f**.
  - Next: 3-3 from `tk_3-2_c1_end` (hp 8 makes Basaquer hard: the boss beam / jump planner kept getting hit;
    a34's TAS-state rows do not graft), then 4-1 control. Biggest recoverable losses: 2-2 (+347: room 6 end hits,
    room 7 start, room 8 start camera), 2-3 (+272: get 10 ninpo in 2-2 room 8 -> TAS-pace J&S kill exists),
    3-2 (+272).

## What it is

One documented package over the three act agents' solvers. It imports their modules read-only and wraps them; it
does not edit `ng/legal.py`, `ng/stages/a34_*`, `ng/stages/a56_*`, `work/a34*`, `work/a56*`.
Every module has its own docstring; most have a CLI (`python -m ng.solve.<module> ...`, run from the project root).

| module | what | built on |
|---|---|---|
| `common` | paths, stage names / rooms, TAS split (`tas4751.events.json`), record split / control on our frame axis (`record_events.json`), rows I/O, `open_emu` | `ng.stages`, `ng.inputs` |
| `legality` | the rules in ONE place: `Enforcer` (online, legal by construction), `legalize` / `project` (open loop), `Legality`, `check` / `check_file` (the judge = `check_inputs.check` on history + rows) | `a56_common.Enforcer`, `ng.legal` |
| `hitbox` | Ryu / sword / enemy / lantern / thrown-weapon boxes from RAM; hurt / sword / spin / lantern-slash / pickup tests; the `$300` collision map | the two community Lua scripts + bank07 code (below) |
| `items` | every lantern of the game from the ROM tables, index of the owner's maps (`knowledge/maps_index.json`), ninpo / weapon planner over a route | ROM banks 0/2/7, `resources/maps/` |
| `beam` | one stage with the TAS-guided legal beam, ANY stage, reference modes `tas` / `record` / `hybrid` (+`--ud`), boss mode on boss stages, wall-climb macros; finishes, verifies, records | `a56_beam.StageBeam`, `ng.legal.Waypoints/hybrid_ref` |
| `astar` | macro A* over stable states (C8 climb `A+away x2, back x6`, jump-offs, runs, jumps, air slashes, throws) for ANY stage, with any prefix / history file | `a34r2_astar` (unchanged; patched loader dir + stage table) |
| `boss` | whole-jump boss planner (pre-move, jump, slash-cancel cycle or throw), any boss state; `--finish` records the stage | `work/a56r2/jplan.py` (unchanged; config registered at run time) |
| `verify` | `finish`: rows -> next control (earliest legal Start skip) -> open-loop replay from the start state -> judge -> `states/<out>_end`, `logs/<out>.json`, results entry; `chain`: power-on concatenation + judge + `assemble.py --serial` | `a12r2_solve.to_control/verify`, `assemble.py` |
| `compare` | per-room / per-column first-reach times vs the TAS, hp / ninpo / item changes (where is time lost?) | |
| `record` | record splits, traced record route json per stage, Waypoints; how to trace a new stage | `work/a56r2/record_trace.py` |
| `fast` | Mesen search backend (`ng/fastcore.py`): `boot`/`pool` from a power-on history (+ NesHawk pads from a trace -> exact), `legal_cands`, `slash` CLI (batch slash/jump timing search on FastPool(2)); results are candidates until replayed on NesHawk | `ng.fastcore` (coordinator) |
| `jobq` | RAM-gated job queue: start only with free RAM >= 2.5 GB, <= `--max` jobs (1 while `logs/HOLD_FARMS` or Contra's exists), PIDs to `logs/tk/pids.txt`, `kill_tracked()` | the act agents' `runq.py` |
| `results` | `logs/results.json` - the standard per-stage record | |

Other one-purpose tools kept where they are (documented in their files): `work/a12r3/wbrute.py` (brute force over
segment lengths of a small input grammar, earliest goal), `work/a12r3/tasfollow.py` (legalized TAS rows from TAS
frame k0 after our rows; first desync), `work/a12r3/r3_pipe.py`, `work/a34r3/graft.py` (graft rows found from a TAS
room-entry state onto our run: room entries are fixed points), `work/a56r3/jq3.py` (Jaquio geometric planner),
`work/tk/snap.py` (hitbox snapshot + screenshot at chosen rows), `work/tk/hitbox_check.py` (model vs game),
`work/tk/tiles.py` (the `$300` collision map around Ryu as text), `work/tk/try.py` (play a row spec, print Ryu every k
frames), `work/tk/scan.py` (rows where Ryu stands in a box), `work/tk/slashsearch.py` (B / jump / stop timing grid on
NesHawk, goal + `--np` ninpo; `ng.solve.fast slash` is the Mesen version), `work/tk/bh2.py` (Bomberhead sword grid),
`work/tk/legal_follow.py` (legalized TAS rows from a state), `work/tk/rngtest.py` (DEBUG: does a boss depend on `$BF`).

## The rules (APPROVED, `knowledge/project_rules.md`)

Per button: a new press at most every 5 frames (start to start), held >= 2, released >= 2; <= 109 presses in any
600 frames and <= 246 in any 1,800; never L+R, never U+D; controller 1 only; power-on start, no savestates in the
final list. The judge: `python check_inputs.py <power-on file> --period 5 --hold 2 --release 2 --windows 600:109,1800:246`.
The windows cross stage boundaries, so every generator takes the power-on history (`--history` / `--hist`).

## Standard result record (`logs/results.json`)

One entry per finished stage attempt (`ng.solve.results.record`, written by `verify.finish`, `beam`, `boss --finish`):
`stage, file, start_state, start_frame, history, load_frame, control_frame, frames, vs_tas, vs_record,
vs_record_cum, hp, ninpo, item, legal, verified, end_state, tool, note, time`.
`vs_record` = our split - the record's split; `vs_record_cum` = our next control - the record's next control on our
frame axis (174 + its cumulative NES frames). `python -m ng.solve.results` prints the table.

## Typical commands

    # a stage with the beam (TAS line where legal, record route around banned TAS moves)
    python -u -m ng.solve.beam 2-2 <start state> --history <power-on rows> --ref hybrid --ud --width 8 --chunk 8 --explore 4000 --hours 2 --tag h1
    # a hard spot with A* (goal = standing near a point, or the next room)
    python -u -m ng.solve.astar 2-2 <start state> <prefix rows|-> pos:6:599:160:10 <out> --hist <power-on rows> --w 1.3 --max-exp 900 --fine --hmax --switch
    # boss
    python -u -m ng.solve.boss 3-3 <control state> --history <power-on rows> --modes slash,throw,throwslash --width 4 --hours 1 --finish
    # finish + verify + record any rows
    python -u -m ng.solve.verify finish 2-2 <start state> <history> <rows file> [N] <out name>
    # power-on chain: concatenate, judge, two independent replays (assemble.py --serial)
    python -u -m ng.solve.verify chain <route> logs/a12r3_to22.inputs.txt logs/<2-2 file> ...
    # where is time lost / what is on screen
    python -m ng.solve.compare <start state> <rows file> --col 64
    python work/tk/snap.py <state> <rows> 60,120,150 --shot name
    # lanterns / ninpo plan
    python -m ng.solve.items 3-1 3-2
    # queue (jobs = shell lines in a file; appended lines are picked up)
    python -u -m ng.solve.jobq logs/tk/jobs.txt --max 3

## Hitbox model (`ng/solve/hitbox.py`)

Ported from `resources/lua_hitbox_viewer/NG1 - Hitbox Viewer.lua` and `resources/lua_hitboxes_detail/NG1 - Hitboxes +
Platform boxes.lua` (feos 2014 et al.), every formula re-read in `dl/NinjaGaidenNES/prg/bank07.asm`:

* The Lua size arrays ARE the ROM tables bank 0 `$B300` (half width) / `$B400` (height), file offsets 0x3310 /
  0x3410 (checked byte for byte); index = enemy pose `$438+i`. Enemy box `[x-XR, x+XR] x [y-YR, y]` (y = feet).
* `hurt_ryu` `$E144`: `|ex-rx| < XR` and Ryu's line `[ry-$90, ry]` meets the enemy box. Skipped while ryu_flags bit 1
  (invincible), weapon `$84` (Invincible Fire-Wheel) or action 7 (J&S spin). Order in the frame: the enemy moves
  first, then the test (a check with the enemy's previous position misses hits).
* `sword_hit` `$DECF` only on poses 7 and `$0A`: the enemy's NEAR edge (x-XR facing right, x+XR facing left) must be
  0..31 px ahead of Ryu's x; vertically `0 <= ey-ry < $92` or `0 < ry-ey < max($91,$92)` (`$91/$92` = reach set per
  action: spin `$20/$20`, actions 3/6 `$18/$10`, 4 `$18/$18`). The Lua draws the blade as `[rx, rx+32] x
  [ry-$90, ry-$90+16]` - close, but it ignores the near-edge rule.
* `spin_hit` `$DE7B` (action 7 or weapon `$84`): `-(XR+8) < ex-rx < XR+12`, `0 <= ey-ry < YR` or `0 < ry-ey <= 24`
  (the Lua's `rx +- 9` box with pose `$0C-$0F` is an approximation).
* Lanterns `$DAA2`: sword poses 7 / `$27`: 0..31 px ahead and `|(ry-8) - ly| < 16`; spin / `$84`: `|dx| < 16`,
  `|dy| < 17`; thrown weapon: `|dx|, |dy| < $E605[weapon & 7]` (star / fire wheel 14, Windmill 18); a Windmill keeps
  flying after a hit. Pickup `$DB8A`: `|dx| < 12`, `|dy| < 17`. Weapon pickups REPLACE `$C9`.
* Check against the game (`work/tk/hitbox_check.py`, TAS replays 3-1 9829+1400 f and 4-2 16682+2100 f): sword hits
  predicted 21 of 21 real ones (1 false positive); the one real hurt (4-2 bird, 18658) is predicted with the enemy's
  position of the same frame.
* The Lua's platform view (`$300` map, 32 columns x 12 quarter-rows of 16 px, kinds 1 right wall, 2 left wall,
  3 both, 4-6 corners, 7 floor, 8 ejecting, 9 ladder, 12-15 exits) is `hitbox.tile_kinds(ram)`.

## Lanterns / items (`ng/solve/items.py`, `knowledge/maps_index.json`)

ROM: count `bank0 $AE10[room]`, column list `bank2 $8700[room]`, y/item `bank2 $8760[room]` (high nibble y/16, low
nibble item). World x = column * 16 = the icon x on the owner's maps (checked: every ROM lantern has its icon at that
x in the one-row maps 1-1, 3-1, 3-2, 4-2, 5-1, 6-1). Items: 0 ninpo+5, 1 ninpo+10, 2 1-UP, 3 health, 4 hourglass,
5/6 points, 7 Inv. Fire-Wheel, 8 Star (3/throw), 9 Windmill (5), 10 Fire Wheel (5), 11 Jump & Slash (5/spin).
`items.plan(stages, ninpo_in, needs, route, weapon)` costs every lantern against a route (default the TAS line:
1 frame if the route passes within sword reach, else a detour estimate) and picks the cheapest set that meets the
ninpo needs; weapon lanterns that would replace the wanted weapon are flagged AVOID.

Ninpo available on the TAS line (cost <= 1 f): 2-2 room 6 +5 (x 672) +10 (x 608), room 7 +10 (x 272) +5,
room 8 +5 +10 +5 +5; 3-1 +5 +5 +10 +10 (+10 at x 1328 for ~15 f); 3-2 +5 +10 +5 +5 +10 (+10 x 2832 ~8 f, +10 x 1152 ~18 f).
The record: 3-1 00 -> 10 -> Star, one throw -> 07 -> +10 -> 17 -> Fire Wheel; 3-2 -> 27 at 3-3.

## Lessons carried over from the act agents

* Where the TAS line is legal, follow it lazily (TAS reference); use the record's route only around banned moves
  (`--ref hybrid`). Once 25+ frames late, enemies (frame-counter driven) differ and TAS rows stop helping.
* Short hard spots: brute force over press timings (`wbrute.py`) or A* (`astar`) beat the beam's explore.
* Do not trust the beam's printed lag after an explore; measure first-reach times (`compare`).
* Room entries are fixed points: rows found from a TAS room-entry state can be grafted (`work/a34r3/graft.py`)
  when the enemies agree.
* Legal climbing: single wall `A+away, A+away, back x6` (C8, 1.54 px/f) or alternating walls; 5-frame cycles do not
  re-grab some walls (7-frame needed). Sub-weapon throw: Up+B with NO left/right on that frame.

## Chain status

(see the top; details per stage below)

### Boss facts measured this round (tk)
* 2-3 Bomberhead and 3-3 Basaquer do not depend on `$BF` (DEBUG research, `work/tk/rngtest.py`: `$BF` poked +37 / +101 at
  the TAS control state, the same rows -> identical boss x/y/HP to the kill; 3-3 differs by 1 HP display frame at
  +101 only). BUT `$BF` is not the only difference: grafting a34's `3-3_p2` rows onto the chained 3-3 state
  (hp 8, ninpo 23, Fire Wheel) desynced at once (Ryu hit, no kill). Treat TAS-state boss rows as a starting guess
  only; re-solve on the chained state.
* 2-3 legal kill at TAS pace: `ng.legal.project` of the TAS rows 9000-9071 (first J&S spin, boss 16 -> 7) + the boss
  planner's step (`python -m ng.solve.boss 2-3 ref4751/04_2-3_control --prefix states/tmp/tk_23_proj72.inputs.txt
  --prefix-frames 72 --modes slash,throw`): boss 0 at 9080 (TAS ~9079), hp 15, rows
  `states/tmp/a56r2_tk_2-3_tasprobe.inputs.txt` (81 rows from the 2-3 control). Needs Jump & Slash + 10 ninpo.
* 3-3: a34's `logs/a34/3-3_p2.inputs.txt` (Fire Wheel, 20 ninpo, 4 wheels + jump slashes) = 978 f control->control
  (record 911.5); the a56 jump planner did worse there (Basaquer hits Ryu; 14 HP left after 97 f).

* **fastcore (Mesen 2.1.1 search core, 2026-10-22):** `ng/fastcore.py` - headless Mesen, ~240 f/s per process (2 processes ~470 f/s), batch candidates from savestate slots, exact NesHawk sync EXCEPT NesHawk's DMC pad conflicts (~1 per 700 frames of legal play): every result must be re-verified on NesHawk (`verify_on_neshawk`). Usage, limits and validation: `knowledge/fastcore.md`.

## Round 5 a56 Mesen tools (2026-10-23)
`work/r5/`: `mboot.py` (power-on -> .mst, `tas:F` exact), `mext.py`, `runbeam.py` (run-room beam), `mastar.py` (a34r2 A*
on Mesen), `mplay.py`, `nhcheck.py`, `md_search.py`, `gate.py`. Resume commands for 6-3 / 6-2 / 5-2: legal_a56_notes.md
"Round 5" -> "Resume (round 6)".
