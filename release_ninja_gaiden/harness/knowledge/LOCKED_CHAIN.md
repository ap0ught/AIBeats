# Locked chain (owner's stage-by-stage plan, started 2026-10-23)

The owner's rule: solve ONE stage at a time from power-on, in order. Both agents work the SAME stage with different
approaches. When a stage is at or under the record's split (or, after a solid effort, the best version we can find,
carrying the deficit), the coordinator LOCKS it here and everyone moves to the next stage. A locked stage is never
changed again: any frame change shifts the global timer `$BF` (+1/frame, wraps at 256) and every later enemy.

Old solutions (`logs/tk_*`, `logs/a12*`, `logs/a34*`, `logs/a56*`, TAS-state rows) are NOT chain material any more.
Use them only as routes, tricks, waypoints and timing references.

Before a stage is locked, look one stage ahead: exit HP, ninpo, item, and the `$BF` arrival value must suit the next
stage (1-2 Barbarian wants J&S + >= 10 ninpo; 3-3 Basaquer wants >= 30 ninpo for 6 Fire Wheels; tossers in 3-2 / 5-1 /
6-1 depend on the `$BF` arrival value).

Judge for every lock: NesHawk open-loop replay from power-on + `check_inputs.py <file> --period 5 --hold 2 --release 2
--windows 600:109,1800:246` + `assemble.py --serial` (two replays match).

## Ninpo/art budget (2026-10-24; details, lantern tables and traps: `knowledge/ninpo_budget.md`)

**Ninpo and the art are cleared after EVERY boss.** So the budget is per act: 2-2's ninpo can only help 2-3, never
3-3.

**Leftover ninpo at a boss kill costs 3 f per point** (measured: the tally runs on the kill frame, and a J&S spin
during the explosion does not avoid it). Arrive with exactly what the boss spends.

Record HUD icons, corrected: purple swirl = **J&S** (not the Windmill), orange diagonal = Windmill, orange flame =
Fire Wheel. The record's Masked Devil kill is a **J&S spin**.

Add to every lock check: "exits with `$C9` = art and `$64` = ninpo" as below.

| stage | exit art (`$C9`) | exit ninpo min / target | for |
|---|---|---|---|
| **2-2** | **J&S (133)** | **10 / exactly 10** | 2-3 Bomberhead: 2 spins, TAS pace (sword-only ~ +270 f). Each extra 5 costs 15 f at the tally |
| 3-1 | Fire Wheel (128), or none if the 3-2 FW (X 1680) is planned | 15 / 20+ | 3-3. Star throws: use 0 or 5 (each -3 breaks the multiple of 5) |
| **3-2** | **Fire Wheel (128)** | **25 / 30-35, multiple of 5** | 3-3 Basaquer: first-pass damage saturates at ~12 HP whatever the ninpo (one wheel at a time); the kill is on his 2nd sit. Spares thrown during his jump still hit once each (ninpo_budget.md section 3) |
| 4-1 / 4-2 | J&S (4-1 X 896; backup 4-2 X 2624) | 0 / 5-10 + 4-3's spins | 4-3 has NO J&S lantern |
| **4-3** | **J&S (133)** | **5 / exactly 5** | 4-4 Kelbeross: one spin (`4-4_p2` = TAS +0) |
| 5-1 | any | 30 / 40-45 | 5-3 spins (TAS 11 spins, the record ~10) |
| 5-2 | **J&S** (room 23 X 144, the only one in Act V) | 40 / 40-55 | 5-3 spins |
| **5-3** | **J&S (133)** | **5 / exactly 5** | 5-4 Bloody Malth: one spin (`5-4_b13` = TAS +2). TRAP: InvFW room 29 X 144 on the TAS line erases J&S |
| 6-1 / 6-2 | **J&S** (6-1 X 528 or 6-2 room 36 X 432; do NOT catch the room-36 Windmill X 256 the TAS takes) | 5 / 10 | 6-3 |
| **6-3** | **J&S (133)** | **5 / exactly 5** | 6-4a Masked Devil: the record's single spin (record TAS +10; our FW r5f1 +52) |
| 6-4b, 6-5 | - | 0 | sword only (always) |

**2-2 WARNING:** our 2-2 line holds the **Throwing Star** from room 6 (`$C9` = 129, ninpo 5 at room 7/8: the TAS's
room-6 spin at TAS 6580 catches the Star). So the **room-8 J&S lantern (X 1312, y 96) is mandatory**.

Room 8 runs leftward. Its lanterns, in order:
* +5 X 1616;
* +5 X 1552 (with the Star held, an air B is a free slash; never Up+B);
* **J&S X 1312**;
* +10 X 1088;
* **Fire Wheel X 944: never catch it**;
* +5 X 800.

That is up to 30 ninpo, so 4 spins are affordable in room 8 and still leave 10 at the exit.

## Locked stages

| stage | file (power-on rows to the NEXT stage's control) | control frame of next stage | stage frames | record split | vs record | cum vs record | hp / ninpo / item at exit | locked |
|---|---|---|---|---|---|---|---|---|
| intro | `logs/a12_intro.inputs.txt` (rows 1-173 + Right on 174) | 1-1 control 174 | - | - | - | 0 | 16 / 0 / - | yes (TAS-identical RAM) |
| 1-1 | `logs/l11_rep_r1_poweron.inputs.txt` -> AMENDED: use rows 1-2474 of `logs/l12_v2_poweron.inputs.txt` (rows 2473-2474 = Right instead of blank, pre-control; same control frame 2,474, same `$BF` 161, Ryu x 35 not 32) | 1-2 control 2,474 | 2,300 | 2,309.8 | **-9.8** | -9.8 | 15 / 10 / J&S | yes 2026-10-23; amended 2026-10-24 (nothing after 1-2 existed yet) |
| 1-2 | `logs/l12_v2_poweron.inputs.txt` (3,308 rows from power-on; end state `states/l12_v2_end`) | 2-1 control 3,308 | 834 (= TAS) | 841.4 | **-7.4** | **-17.2** | 16 / 0 / J&S, `$BF` 224 | yes 2026-10-24 (coordinator: judge PASS, `verify chain lock_to21_v2` two replays MATCH, RAM sha1 843274aa06d8) |
| 2-1 | `logs/l21f_fol_v4_poweron.inputs.txt` (6,130 rows from power-on; end state `states/l21f_v4_end`; follow agent, room 4 = wall agent's `work/w21/r4_rows.txt`) | 2-2 control 6,130 | 2,822 (TAS +20) | 2,904.8 | **-82.8** | **-100.0** | 16 / 10 / J&S, `$BF` 230 | yes 2026-10-24 (coordinator: judge PASS, locked rows identical, `verify chain coord_to22_v4` two replays MATCH, RAM sha1 21f1b749168e) |
| 2-2 | rows 1-9,167 of `logs/l22_art_w10_to31_poweron.inputs.txt` (= `logs/l22_art_w10_poweron.inputs.txt` with the last row = Left; main agent's w10 prefix + art agent's room 8; Star line, J&S caught at X ~1321) | 2-3 control 9,167 | 3,037 (TAS +142) | 3,101.1 | **-64.1** | **-164.1** | 15 / exactly 10 / J&S, `$BF` 195 | yes 2026-10-24 (coordinator: judge PASS, locked rows identical, `verify chain coord_to31` two replays MATCH, RAM sha1 6f295ee100aa) |
| 2-3 | `logs/l22_art_w10_to31_poweron.inputs.txt` (9,993 rows; 2-3 rows = `logs/l23_t12_va.inputs.txt`, `$BF`-independent) | 3-1 control 9,993 | 826 (TAS -4; kill control+80 = floor) | 833.3 | **-7.3** | **-171.4** | 16 / 0 / none, `$BF` 251 | yes 2026-10-24 (same chain check) |
| 3-1 | `logs/l31_alt_b2r_poweron.inputs.txt` (11,595 rows; row 9,993 = Right (3-1 control frame), last 2 rows Right; 1 Star throw breaks the FW lantern) | 3-2 control 11,595 | 1,602 (TAS -3) | 1,602.7 | **-0.7** | **-172.1** | 16 / 12 / Fire Wheel, `$BF` 61, `$62` 54; residue 2 = +6 f at the 3-3 tally (effective 11,601 vs tas5 c1b 11,604) | yes 2026-10-24 (coordinator: judge PASS, rows 1-9,992 identical, `verify chain coord_to32` two replays MATCH, RAM sha1 8a74b015f3e5) |
| 3-2 | `logs/l32_a_cB_poweron.inputs.txt` (13,930 rows; agent first: legal TAS rows lag 160/187, tosser-1 body boost onto the ladder, legal pillar, last 2 rows Right) | 3-3 control 13,930 | 2,335 (TAS +28) | 2,328 | **+7.2** | **-164.9** | 15 / 32 / Fire Wheel, `$BF` 92, `$62` 7 | yes 2026-10-25 (coordinator: judge PASS, locked rows identical, `verify chain coord_to33` two replays MATCH, RAM sha1 0946bbcb4737) |
| 3-3 | `logs/l33_q4_poweron.inputs.txt` (14,848 rows; Fire Wheel kill on his 3rd rise, row 170; 2nd-sit kill impossible: sitting boss immune) | 4-1 control 14,848 | 918 (TAS +90) | 911.5 | **+6.5** | **-158.4** | (act start: hp 16, ninpo 0, no art), `$BF` ~(F-16) | yes 2026-10-25 (coordinator: judge PASS, locked rows identical, `verify chain coord_to41` two replays MATCH, RAM sha1 08c24f6f39c2) |
| 4-1 | `logs/l41_r15_c_poweron.inputs.txt` (16,998 rows; control row 14,848 = Right; rooms 13-14 agent c2 (bird knockback over the block, 1.8 px/f ladder cycle), room 15 agent r15 (Down+B kills the bird, branch, standing jump over the block, one J&S spin on the top run), Start at stage end + 9) | 4-2 control 16,998 | 2,150 (TAS +37) | 2,191.6 | **-41.6** | **-200.0** | 16 / 0 / J&S, `$BF` ~81 | yes 2026-10-25 (coordinator: judge PASS, rows 1-14,847 identical, `verify chain coord_to42` two replays MATCH, RAM sha1 76035d5f3074) |
| 4-2 | rows 1-19,295 of `logs/l42_w_k932b_poweron.inputs.txt` (AMENDED 2026-10-26: Left on row 19,296 already moves Ryu, so 4-3's rows start with Left on 19,296 = 4-3 control; 4-2 = 2,298 f, record -5.8, cum -205.8; agent a's `b2_k3` to X 2,950 incl. the X 2,336 forward damage boost, wall agent's post jump + contact-frame wall jumps; legal bird boost proven but doesn't fit our bird phase) | 4-3 control 19,297 | 2,299 (TAS +22) | 2,303.8 | **-4.8** | **-204.8** | 15 / 10 / J&S | yes 2026-10-25 (coordinator: judge PASS, rows 1-16,997 identical, `verify chain coord_to43` two replays MATCH, RAM sha1 2ca737481fff) |
| 4-3 | rows 1-21,856 of `logs/l44p_r1920_c2_poweron.inputs.txt` (4-3 stage rows `logs/l43_r1920_c2.inputs.txt` from Left on 19,296; builder's rooms 17-18 (chimney cycle, single-wall lip climb), r1920's rooms 19-20 (stepped block kicks, thrower-blade lift into room 20, new X-392 pillar zigzag), exit J&S exactly 5) | 4-4 control 21,857 | 2,561 (TAS +167) | 2,557.2 | **+3.8** | **-202.0** | 14 / 5 / J&S, v (`$62`) 13 | yes 2026-10-26 (coordinator: judge PASS, locked rows identical (button order only), `verify chain coord_to51_c2` two replays MATCH, RAM sha1 d4e9ccff650f) |
| 4-4 | `logs/l44p_r1920_c2_poweron.inputs.txt` (22,628 rows; 4-4 rows via `work/l44p/graft.py`: one J&S spin, kill row 24 = TAS, earliest Start); 5-1 control row 22,629 = blank, Right from row 2 (5-1 plan) | 5-1 control 22,629 (best tosser band 22,629-22,643) | 772 (= TAS) | 785.3 | **-13.3** | **-215.3** | (act start: hp 16, ninpo 0, no art) | yes 2026-10-26 (same chain check) |
| 5-1 | `logs/l51_c3d_poweron.inputs.txt` (24,998 rows; 5-1 stage rows from the blank row 22,629: agent first's start-to-wall (wall bird re-spawned by the Left x2 at scroll 928-943), third's bird-phase prefix (10 f of stands so the wall bird gives the TAS's 23,714 boost onto the y-96 platform), one Windmill (Up+B 24,313) breaks the health lantern, 4-f stand at 24,425 so a bird lifts Ryu onto pillar B (hp 15->12), beam to the trigger 24,719) | 5-2 control 24,998 (`$BF` 143) | 2,369 (TAS +67) | 2,460.0 | **-91.0** | **-306.3** | 12 / 35 / Windmill | yes 2026-10-27 (coordinator: judge PASS, locked rows 1-22,628 identical, `verify chain coord_l51c3d` two replays MATCH, RAM sha1 b901e79b34f7, 0 deaths) |
| 5-2 | `logs/l52b_e4_poweron.inputs.txt` (27,360 rows; **locked rows = 1-27,359**; row 27,360 = the 5-3 control row (Left), part of 5-3. Room 23 = l52a d3 (prefix + b_r23a, free +10 at X 352, J&S pickup 25,388, left-shaft wall jumps; the TAS's over-the-wall exit proven impossible legally: 0.5 px/f drift against facing); rooms 24-26 = l52b (left-wall chimney climb, 5-f exit cycle, room-25 bullet-hit exit, room-26 bird boost onto the thrower ledge, no-spin fall s26c, 4-f stand so the bird boosts Ryu into the exit)) | 5-3 control 27,360 (`$BF` 201) | 2,362 (TAS +181) | 2,458 | **-96.0** | **-402.3** | 3 / 45 / J&S | yes 2026-10-27 (coordinator: judge PASS, locked rows 1-24,997 identical, `verify chain coord_l52e4` two replays MATCH, RAM sha1 7b83b5e25e73, 0 deaths; hp 3 accepted: l53a verdict 'no hits planned in 5-3'; insurance e5 = +24 f for hp 5) |
| 5-3 | `work/l53c/v1c_cn1_poweron.inputs.txt` (30,905 rows; **locked rows = 1-30,251**; row 30,252 = the 5-4 control row. Room 27 = l53a ch1_both (X-672 ladder face + y-112 platform over the pit, both lanterns, np 45); rooms 28-30 = l53b v1c (legal chimney/ladder entries, room-28 throwers passed with 0 hits on the fast entry, room-29 exit under the wall up the '9' face, two NesHawk DMC pad-read repairs); rooms 31-33 = l53c (walk under the wall, 7-f climb cycle `[A+Right x4, A+Left, Left, -]` 1.86 px/f, two 1-hp hits instead of spins (np 5), 1-f ground turn in room 32, Start on trigger+5)) | 5-4 control 30,252 | 2,892 (TAS +241) | 2,985 | **-93.0** | **-495.3** | 16 (refilled) / exactly 5 / J&S (133) | yes 2026-10-28 (coordinator: judge PASS, rows 1-27,359 identical to e4, `verify chain l53c_v1c_cn1` two replays MATCH, RAM sha1 78541bb1a8a1, 0 deaths; NesHawk = Mesen every frame 27,361-30,905) |
| 5-4 | `logs/l61_LOCKED_l62_to62_poweron.inputs.txt` (= rows 1-32,631 of `work/l62/l62_po_r40f.inputs.txt`; 5-4 rows = l53c's fight (one J&S spin, boss 0 on 30,306 = control + 54, all `$BF`), **Start on 30,903-04 (kill + 597)**: kill + 594..596 make 6-1 die at head-start row 553 (`nh_late.py`, k 2-7 good)) | 6-1 control 31,057 | 805 (TAS +1) | 805.3 | **-0.3** | **-495.6** | (act start: hp 16, np 0, no art) | yes 2026-10-28 (coordinator: judge PASS, rows 1-30,251 identical to 5-3 lock, `verify chain l62_r40f` two replays MATCH, RAM sha1 60cad6ce57fd, 0 deaths) |
| 6-1 | same file (6-1 + room 36 = l61p head start `pre61_32595.txt`, TAS-exact; 6-2 control row 32,632 = Left) | 6-2 control 32,632 | 1,575 (= TAS) | 1,584.6 | **-9.6** | **-505.2** | 15 / 20 / J&S | yes 2026-10-28 (same chain check; **locked rows = 1-32,631**) |
| 6-2 | `logs/l62_LOCKED_v2_to63_poweron.inputs.txt` (= rows 1-35,798 of `work/l62/l62_v2_poweron.inputs.txt`; **locked rows = 1-35,798**; row 35,799 = 6-3 control row (Right). l62: room-37 chimney wall jumps + pillar cycle, room 38 6-f cycle, room 39 entry cycle + beams, room 40 HIGH route (over the X-432 pillar, the y-96 ledge, over the pit; a floor jump peaks at y 160 in all 120 cases, so it can never reach the y-128 block; 6,300 ghoul/axe boost cases found no crossing)) | 6-3 control 35,799 (room-41 `$BF` 188, outside l63p's good runs) | 3,167 (TAS +244) | 3,153.2 | **+13.8** | **-491.4** | 11 / 0 / J&S (133) | yes 2026-10-28 (coordinator: judge PASS, rows 1-32,631 identical, `verify chain l62_v2` two replays MATCH, RAM sha1 6ada68899a66, 0 deaths; NesHawk = Mesen at 35,799) |
| 6-3 | `logs/NG_FINAL_v2_poweron.inputs.txt` (41,390 rows = the FINAL RUN; 6-3 rows from 35,799: l63p head start rooms 41-42, room 43 beams + bird boost onto the X-1,040 pillar, room 44 beams, +10 / +5 lanterns; trigger 38,645) | 6-4a control 38,805 | 3,006 (TAS +145) | 2,912.8 | **+93.2** | **-398.2** | 3 / 10 / J&S | yes (coordinator 2026-10-28: judge PASS, rows 1-35,798 identical, `verify chain NG_FINAL_v2` two replays MATCH (RAM sha1 d5d58c8792b7), 0 deaths; INDEPENDENT `work/verify/final_check.py`: PROBLEMS none, BEATS) |
| 6-4a | same file (Start 38,650-51; `md_js10` two-spin kill on 38,879 = control + 74) | 6-4b control 39,625 | 820 | 819.3 | **+0.7** | **-397.5** | - | yes (same) |
| 6-4b | same file (Start 39,470-71; a56 `r4k2` kill on 39,878) | 6-5 control 40,639 (Start 40,485-86 = earliest + 23 so the Demon arrival has a kill; depends on `$400-$4FF` leftovers too) | 1,014 | 997.6 | **+16.4** | **-381.1** | - | yes (same) |
| 6-5 | same file (l65 `lines/r2d5_k2.txt`, Demon dead 40,947, hp 16 -> 12; P 41,382, END seen 41,385) | **END seen 41,385 = 11:25.704** | 746 | 755.2 | **-9.2** | **-389.4** | - | yes (same) |

## RUN COMPLETE (2026-10-28): `logs/NG_FINAL_v2_poweron.inputs.txt` = **11:25.704**, 6.479 s (389.4 f) under TheRetroRunner's 11:32.183; independently verified (`work/verify/run/final/final_check.txt`)

### Candidates (5-3, LOCKED = l53c v1c_cn1)

On `logs/l52b_e4_poweron.inputs.txt`. Record pace: **5-4 control <= 27,360 + 2,985 = 30,345**. TAS pace: 5-3 = 2,651 f (5-4 control 30,011 on our axis at TAS speed).

| time | agent | file | 5-4 control | frames | vs record | hp/ninpo/art at exit | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|

## 5-2 round (LOCKED 2026-10-27 = e4). Older notes:

### Candidates (5-2)

On the locked chain `logs/l51_c3d_poweron.inputs.txt` (24,998 rows; **locked rows = 1-24,997**; row 24,998 = the 5-2 control row, blank in c3d: 5-2 stage rows start ON row 24,998, Left there moves Ryu x 180 -> 178, as the TAS's 24,427). Record pace: **5-3 control <= 24,998 + 2,458 = 27,456** (trigger <= 27,177). TAS pace: 5-3 control 26,608 + 571 = 27,179 (our frame = TAS + 571).

| time | agent | file | 5-3 control | frames | vs record | hp/ninpo/art at exit | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-27 16:30 | l52b (rooms 24-26) on l52a d3 | **`logs/l52b_e4_poweron.inputs.txt`** (27,360 rows; trigger 27,081, Left on the control row) | **27,360** (TAS 26,608 + 752) | 2,362 (TAS +181) | **-96** (cum ~ -402) | **3** / **45** / J&S (`$C9` 133), `$BF` 201 at the control | yes: `verify chain coord_l52b_e4` two replays MATCH (RAM sha1 7b83b5e25e73), 0 deaths, 5-3 load 27,209; `nhchk.py` NesHawk = Mesen every frame 25,519-27,360 (0 differing, end RAM equal); NesHawk states `l52b_e4_{26848,26995,27081,27360}` | PASS (locked 1-24,997 and d3 1-25,495 identical) | **BEST.** = e1 with (a) a no-spin, no-hit fall to the wall-jump spot (beam s26c: X 377 y 176 on 26,848, 4 f earlier than e1, +5 np) and (b) the exit bird boost back (`Right x16, - x4, Right x12, A+Right x2, Right...` from the e1 rows at 26,991: bird hit 27,051 from the left, hp 6 -> 3, into the exit). Room 26 = TAS +64 (record +89). Same continuation e2 (27,366) / e3 (27,364) on the s26b spin line, np 40 |
| 2026-10-27 14:20 | l52b (rooms 24-26) on l52a d3 | **`logs/l52b_e1_poweron.inputs.txt`** (27,397 rows = d3 rows 1-25,495 + blanks + l52b rooms 24-26; trigger 27,118, Left on the control row) | **27,397** (TAS 26,608 + 789) | 2,399 (TAS +218) | **-59** (cum ~ -365) | **6** / 35 / J&S (`$C9` 133), `$BF` 238 at the control | yes: `verify chain coord_l52b_e1` two replays MATCH (RAM sha1 da385e22dc32), 0 deaths, 5-3 load 27,246; `work/l52b/nhchk.py` NesHawk = Mesen on every frame 25,519-27,397 (0 differing, end RAM equal); NesHawk states `l52b_e1_{26025,26506,26852,27118,27397}` | PASS (locked rows 1-24,997 and d3 rows 1-25,495 identical) | rooms vs TAS: 23 +50 (l52a d3), 24 +43, 25 +24, 26 +101. Room-25 exit takes the bullet hit (hp 11 -> 9); no-hit version = +10 f, hp +2. Room 26: bird boost onto the ledge (hp 9 -> 6), two spins kill birds (both needed: removing either = hits/death), +10 lantern broken, no hit at the exit (climbs the '9' face instead of the TAS's bird boost). Thrower spawn `$BF` 60 (in the prep's TAS band, harmless on our rows) |

### Agent notes (5-2)
* **l52b HP PRICES on e4 (5-3 control 27,360, hp 3 / np 45):**
  * **(b) room-25 no-hit exit = +24 f for +2 hp -> e5 `logs/l52b_e5_poweron.inputs.txt`: 5-3 control 27,384 (record -72), hp 5 / np 45 / J&S.**
    The 10 f later room 26 shifts the thrower (`$BF` +10) so e4's room-26 rows get an axe at the ledge end; a wait at the room-26 entry
    of 14 f restores a working phase (0-13 f all fail, Mesen scan). Verified: judge PASS, d3/locked rows identical, `verify chain
    coord_l52b_e5` two replays MATCH (RAM sha1 f7a973b3775e), 0 deaths, NesHawk = Mesen every frame (0 differing, end RAM equal).
  * **(c) no exit bird boost (climb the exit face) = +40 f for +3 hp -> e6 `logs/l52b_e6_poweron.inputs.txt`: 27,400, hp 6 / np 45.** Judge PASS,
    Mesen OK, but **NesHawk FAILS**: a pad-read conflict at 27,049-50 (B+Down then B+Down+Right) turns the pure slash into a spin on
    NesHawk (np 40) and the line dies. Not fixed yet (RAM < 2 GB). e1-style finish (spin at the end, np 40) would be ~+33 f for +3 hp.
  * **(a) room-26 health lantern (X 256 y 80): >= +28 f, unfinished.** Beam hl1 gets it on 26,756 via a bird hit at X ~216 that lifts
    Ryu to y 89 (hp 9 -> 7 -> 13, one extra spin, np -5); beam hl2 then reaches the ledge ~20 f behind e4 but finds no way past the
    thrower's axe to the wall-jump spot within 120 f (e4 is there on 26,848). So at least +28 f, +7 hp, -5 np; the rest of the room
    would also need new bird timing.
  * Cheapest per hp: (b) 12 f/hp, (c) ~11-13 f/hp. No other hp source in 5-2 (room 26 health is the only one).
* **l52b HANDOVER 3 (16:30): e4 = `logs/l52b_e4_poweron.inputs.txt`, 5-3 control 27,360 (record -96), exit hp 3 / np 45 / J&S. Verified.**
  * Room-26 rows from 26,529: `work/l52b/r26_pre_m26d.txt` + `r26_s26c.txt` (no-spin fall, setup on 26,848) + `r26_x26e_to26995.txt` +
    `r26_bb3.txt` (exit bird boost). The last two are e1's/bb3's rows unchanged: the faster setup shifts everything by -4 f and the
    birds/boost still line up.
  * (1) Exit bird boost: Mesen grid of stands/jump timings (`menum.py`, 702 + 423 cases from e1's state 26,995): best = 4-f stand
    -> bird hits from the left at X 638 (hp 6 -> 3) -> trigger. **Saves 31 f vs the face climb for 3 hp** (no-boost, no-spin climb =
    +7 f vs e1's spin line). Stands of 0-3 f do not give the boost.
  * (2) Ninpo: exit 45 (target 40, one spare spin). The s26b spin is gone (s26c, beam 250 wide: no spin, no hit). The 26,884 spin
    (kills the bird after the column) and the 26,702 TAS spin stay: removing either = hits/death (tested). The room-25 +5 costs >= 12 f.
  * (3) Column crossing: s26c is 4 f faster than e1's; the fall + wall jump under the column is the only legal way found (over the top
    = drift 0.5 px/f after the jump-off). Room 26 now = TAS +64 (entry +11, ledge ~+9, crossing ~+20, end ~+24).
  * hp trade-off: e4 exits hp 3 (TAS 3). Alternatives: +31 f for hp 6 (no exit boost); the room-25 no-hit exit adds +2 hp for +10 f.
* **l52b HANDOVER 2 (14:20): full 5-2 candidate e1 on d3 = `logs/l52b_e1_poweron.inputs.txt`, 5-3 control 27,397 (record pace 27,456 -> -59),
  exit hp 6 / np 35 / J&S, `$BF` 238 at the 5-3 control. Verified (see Candidates).**
  * Room 26 rows (from 26,529): `work/l52b/r26_pre_m26d.txt` (entry + TAS rows + bird boost onto the ledge, to 26,803) +
    `work/l52b/r26_s26b.txt` (beam s26b: one spin, fall along the ledge wall to X 376 y 176 on 26,852) + `work/l52b/b_x26e.txt` (beam x26e:
    wall jump under the '2' column -> floor X 421 on 26,882, spin kills the bird at 26,888, slash-break of the +10 lantern 26,992, spin
    at 27,052 (bird), cling to the exit's '9' face and climb -> trigger 27,118 = TAS +101). Two 1-f Left rows at goal frames (26,506
    room change, 27,118 trigger) were extended to 2 f in the power-on file (inputs ignored there; judge PASS).
  * Ninpo: 35 at exit (target 40; 35 is enough if both room-27 +5s are taken). The room-25 +5 (X 96) costs >= 12 f (ground slash
    freezes Ryu; air slashes miss it: 117 cases). Every room-26 spin is a kill (removing one = hits/death, tested).
  * hp: 6 at exit. Options: room-25 no-hit exit (+10 f, +2 hp: `work/l52b/b_x25d.txt` from TAS 25,761 at lag 7).
  * Where room 26 still loses (+101): entry +11, bird boost/ledge ~+9, the column crossing ~+24 (TAS moonwalks over it), and ~+57
    after landing (the TAS's 26,303 bird boost into the exit; ours climbs the exit face ~40 f). A beam that reproduces the exit bird
    boost (bird phase via stands, l51c's `sgrid3.py` method) is the next gain.
* **l52b (rooms 24-26) PAUSED 06:20 (owner needs the PC). RESUME NOTE.** All my emulators stopped.
  * **Rebased on d3 (offset +621):** `work/l52b/chain.py 25517 work/l52b/R24_v1.txt work/l52b/R25_v1.txt --state states/mesen/l52a_d3_25517.mst`
    -> room 25 change 26,025, room 26 change **26,506** (= TAS 25,818 + 688), room-26 control 26,529; hp 9 / np 45 / J&S. Mesen state after
    26,528 `states/mesen/l52b_d3_26528.mst`; rows 25,518-26,528 `work/l52b/ch_d3_to26528.txt`; power-on history to 26,528
    `work/l52b/hist_d3_26528.txt`. Rooms 24/25 = TAS +43 / +24 (record +82 / +34). NesHawk = Mesen (0 diffs, end RAM equal) was shown on c1
    (`work/l52b/nhchk.py`, states `l52b_v1_26029/26532`); not yet re-run on d3 (rows are the same; arrival state = TAS's).
  * **Room 26 so far (d3), rows from 26,529 `work/l52b/r26_pre_m26d.txt` (275 rows) -> on the thrower ledge X 345 y 128 at 26,803, hp 6 / np 40**,
    Mesen `states/mesen/l52b_d3_26803.mst`, history `work/l52b/hist_d3_26803.txt`. = entry (cross to the left wall, `[Right, A+Right, A+Left,
    Left x2] x6`, wall jump onto the cap, jump from the cap to the y-192 floor: X 126.5 on the floor = TAS +10/11, 0.5 px phase off so no
    exact TAS join) + legal TAS rows (spin at TAS-eq 26,003 kills the jump kicker) + beam m26d (bird hit from the left, hp 9 -> 6, knockback
    onto the ledge): ledge X 345 = ~TAS +20.
  * **Thrower band on d3: spawn `$BF` = 60 (spawn frame 26,707; c1 was 64)**, i.e. L = 128, inside the prep's 120-129 band for the TAS
    rows. On OUR rows the line to the ledge is unchanged (same hp 6); on d3 the axe that hit at the ledge end on c1 (TAS-eq 26,120) does
    not come (beam s26b had Ryu at X 374 y 128 on 26,824 with hp 6). Still to check to the trigger. Fallback: a 4-f wait at the room-26
    entry restores `$BF` 64 (costs 4 f).
  * **Open: the '2' column (X 400-415, y 64-159).** The TAS moonwalks over its top (illegal: facing left after the jump-off = 0.5 px/f
    drift). Legal = the record's UNDER route: fall along the right face of the ledge's wall (col 22, X 352-367) to y 176-188 with Ryu at
    X 372-376, then `A+Right x2, Right...` (jump-off) passes under the column and lands on the y-192 floor at X 415-421 ~28 f later
    (tested with enemies removed: works for y 176-188, X 372-376; y <= 170 hits the column face). Enumerations c26a/b/c (4,387 macro
    cases from the c1 ledge state) found no goal because the thrower's axe / bird hit Ryu on the way; beam s26b (goal = that setup box,
    from the d3 ledge state) was running when paused: 26,844 X 377 y 147 hp 6 np 35.
  * **Next:** (1) rerun s26b (`bb.py 26803 s26b --state states/mesen/l52b_d3_26803.mst --hist work/l52b/hist_d3_26803.txt --goal
    "372<=X<=377 and 174<=y<=190 and hp>=4" ...`), then `A+Right x2, Right` to the floor; (2) the end (floor X 416+ -> col-30 wall jump ->
    '5774' platform, +10 lantern spin-break, bird boost into the exit): exploratory beam x26a from TAS 26,177 got the trigger at TAS +33
    (np wasted; rerun with keep np>=40) - redo from our real state; (3) assemble on d3 (`logs/l52a_d3_poweron.inputs.txt` rows to 25,495
    + blanks + `ch_d3_to26528` + room 26 + Left at trigger + 279), verify chain / judge / NesHawk; (4) hp option: room-25 no-hit exit
    (beam x25d, `work/l52b/b_x25d.txt`) = +10 f for +2 hp. Estimate: room 26 ~TAS +50..+70 (record +89) -> 5-3 control ~TAS + 571 + 50 +
    43 + 24 + 60 = record pace with ~100 f to spare.
  * Tools (`work/l52b/`): `bb.py` (beam, --state/--hist/--keep), `menum.py` (macro enumerator, --tasjoin exact-TAS-join goal), `sync.py`
    (join + splice legal TAS rows), `chain.py` (room files -> chained rows + state), `play.py`, `birds.py`, `nhchk.py`, `gate.sh` (RAM gate).
* **l52a (room 23) HANDOVER d3 (BEST, supersedes c2): room 24 on 25,495 = TAS +50 (record ~+72 -> 22 f better), hp 12 / np 50 / J&S.**
  Same line as c2 to 25,389 (J&S caught 25,388), then a wider chimney beam (`b23.py` d3, width 400, no-spin). Rows from 24,998:
  `work/l52a/d3_stage.txt` (498 rows, last = 25,495); power-on `logs/l52a_d3_poweron.inputs.txt`. Judge PASS; NesHawk = Mesen every
  frame to 25,525, end RAM equal; NesHawk states `l52a_d3_25495`, `l52a_d3_25518`; Mesen `states/mesen/l52a_d3_25517.mst` (after
  row 25,517). **Offset for rooms 24-26 = +621: room-24 control row 25,518 = TAS row 24,897.** Ryu enters room 24 in action 12
  (steps) instead of the TAS's 5 (`$80`, `$82` differ; everything else of Ryu equal); scripts Up/Left/Right/A/A+L/A+R/blank x40 and the
  legalized TAS rows 24,897-24,976 give identical X/y/xsub/hp on our state and the TAS's. Your c1 grafts move by -4 rows (c1 offset 625).
  **Option d1: room 24 on 25,493 (TAS +48) but np 45** (one J&S spin at 25,452 near the X-48 column): `work/l52a/d1_stage.txt`,
  `logs/l52a_d1_poweron.inputs.txt`, offset +619 (control row 25,516), NesHawk-checked the same way. 2 f for 5 ninpo; d3 is my pick
  (the 5-3 target is J&S + 40).
* **l52a (room 23) HANDOVER c2 (supersedes c1): room 24 on 25,496 = TAS +51 (record ~+72 -> 21 f better), hp 12 / np 50 / J&S.**
  = c1 with a cheaper J&S: 2 blank rows at 25,351-52 (instead of 5) + B 25,360-61 -> pickup 25,388 (`jstest3.py`, 1,386 legal
  variants: 0 blanks never catches it, 1 blank breaks the Left release rule), then c1's rows from 25,393 shifted -3.
  Rows from 24,998: `work/l52a/c2_stage.txt` (499 rows, last = 25,496); power-on `logs/l52a_c2_poweron.inputs.txt`. Judge PASS;
  NesHawk = Mesen every frame to 25,526, end RAM equal; NesHawk states `l52a_c2_25496`, `l52a_c2_25519`; Mesen
  `states/mesen/l52a_c2_25518.mst` (after row 25,518). **Offset for rooms 24-26 = +622: room-24 control row 25,519 = TAS row 24,897**
  (Ryu X 43 y 232, `$80/$83/$84/$85/$8C/$93/$95`, scroll, hp 12, J&S equal to the TAS after 24,896; np 50 vs 45).
* **l52b (rooms 24-26) HANDOVER 1: rooms 24 + 25 grafted on l52a c1 -> room 26 change on 26,510 = TAS 25,818 + 692 (rooms 24/25 = TAS +43 / +24; record +82 / +34), hp 9 / np 45 / J&S.**
  Row files (row 1 = the room's control row = room change + 23): `work/l52b/R24_v1.txt` (from our 25,522), `work/l52b/R25_v1.txt`
  (from our 26,052). Chained with `work/l52b/chain.py 25521 R24_v1 R25_v1 --state states/mesen/l52a_c1_25521.mst` (blank rows pad each
  room change to change + 22): room 25 change 26,029, room-25 control state = TAS's exactly (x/sub/y/vy/action/facing/touch), room 26
  change 26,510. Rows 24,998-26,532 (l52a c1 + mine, Mesen) `work/l52b/ch_v1_to26532.txt` from 25,522; Mesen state after 26,532
  `states/mesen/l52b_v1_26532.mst`. NOT yet NesHawk-checked (will do with room 26).
  * Room 24 (+43): chimney = cross to the LEFT wall first (`-, A+Left x2, Left x11`), climb it with `[Right, A+Right, A+Left, Left x2] x6`
    (1.6 px/f), wall jump `A+Right x2` over the cap, `Right x4, Left x2` (half-pixel phase fix so Ryu joins the TAS run exactly),
    lands on the cap: joins the TAS run at lag 37 (TAS +33 without the phase fix but then the X-616 pit kills Ryu: 0.5 px matters).
    `menum.py` (2,632 + 240 macro cases) and beams: 37 is the best exact join; the TAS chimney is a moonwalk (L+R inside the '9'
    column). Then legal TAS rows (= TAS exactly, spin-break +5 kept: a pure Down+B slash misses the lantern and takes hits), exit
    cycle `[Right, Right, Left, A+Left, A+Right] x6` from TAS-eq row 25,335 (prep's) = +6.
  * Room 25 (+24): entry `-, [Left, A+Left, A+Right, Right x2] x3, Left, A+Left x2, Left...` joins the TAS at lag 7 (`menum.py`, 264
    cases; cyc.py had no A+Left x2 tail). TAS rows (both spins needed: dropping either = hits/death). Exit = the UNDER route (beam
    `bb.py` x25c): walk left under the X-48 column, jump at X ~70, cling to the '9' face from the left at X 43 y 112, climb; a low
    bullet hits on the face (hp 11 -> 9) and boosts Ryu to the exit: +17 vs TAS. **No-hit version (beam x25d, hp 11): +27 (10 f for
    2 hp).** Over-the-top beams (x25a/x25b): +31 / +36 (facing right above y 72 = 0.5 px/f drift).
  * Thrower band: L ~ 54 + 43 + 24 + 14 (room-26 entry) = 135 -> spawn `$BF` ~67, outside both bad bands on the TAS rows; re-scan on our rows coming.
* **l52a (room 23) HANDOVER c1: room 24 on 25,499 = TAS +54 (record ~+72 -> 18 f better; old fallback r4_52_h2 +108 -> 54 f better), hp 12 / np 50 / J&S (133).**
  Rows from 24,998: `work/l52a/c1_stage.txt` (502 rows, last row = 25,499); power-on file `logs/l52a_c1_poweron.inputs.txt`
  (25,499 rows = locked 1-24,997 + c1). Judge PASS (`check_inputs.py ... --windows 600:109,1800:246` on the power-on file).
  NesHawk `work/l52a/nhchk.py`: NesHawk = Mesen on every frame 24,998-25,529, end RAM equal (0 diffs). NesHawk states
  `l52a_c1_{25196,25392,25499,25522}`; Mesen `states/mesen/l52a_c1_25521.mst` (after row 25,521, blank rows after 25,499).
  Line: prefix + `b_r23a` (+ B 25,218-19 for the free +10) -> legal TAS rows to the y-96 platform -> walk off its left edge
  (no jump), 5 blank rows in the air at 25,352 + B 25,361-62 breaks the J&S lantern, pickup 25,390 at X 134 -> beam `b23.py` c1:
  floor jump over the waiting ghoul (no hit), through the X-48 column, contact-frame wall jumps up the left wall (X ~24),
  jump right onto the X-48 steps (X 44 y 89), Up, A+Left / A+Right -> exit tile at X 43 y 84.
  **Arrival for rooms 24-26: our frame = TAS + 625 from the room change on.** Room-24 control: our row 25,522 = TAS row 24,897
  (Ryu appears at X 43 y 232 on 25,520 = TAS 24,895). State after row 25,521 vs TAS after 24,896: Ryu x/xsub/y, facing ($84),
  touching ($8C), action ($80), hp 12, item J&S all EQUAL; differs only in np (50 vs 45), $BF (154 vs 41), timer, $87/$89
  (vertical fraction/speed, overwritten by the first grab/jump) and junk in empty enemy/lantern slots. Tested: Up x40, Right x40,
  A+Left/A+Right scripts, blanks and the legalized TAS rows 24,897-24,936 give identical X/y/hp on both states. So graft TAS-based
  room-24 rows at offset +625 (our row = TAS row + 625). Thrower band: F = 24,998, our room-26 lag L = 625 - 571 + (rooms 24-26 lag).
* **l52a (room 23) 1st note: the +10 lantern X 352 y 96 is FREE.** On prefix + `b_r23a` (rows from 24,998: `work/l52p/pre52_24625.txt` rows 1-174 + `work/l52p/b_r23a.txt`), a B on rows 25,218-25,219 (mid-air, TAS-eq 24,647-48; any 2-3 f B in 25,217-25,223 works) breaks it and Ryu catches it: np 40 -> **50**, same position (X 303 y 128 on 25,272 either way). Base states: Mesen `states/mesen/l52a_c3d_24997.mst` (after row 24,997) = NesHawk `l52a_c3d_24997` (0 RAM diffs incl. $400-$4FF); `states/mesen/l52a_pre_25196.mst` (prefix end, = TAS 24,625 positions exactly on our state, legal with the real 5-1 history). Over-the-wall exit: proof it is not legal (no knockback source near the wall top) coming in the write-up; I am building the floor + left-shaft line. The J&S on the floor line costs ~5 f (walk off the y-96 platform, 5 blank rows in the air, slash -> pickup at X 134).

## 5-1 round (LOCKED 2026-10-27 = c3d). Older notes:

### Candidates (5-1)

On the locked chain `logs/l44p_r1920_c2_poweron.inputs.txt` (5-1 control row 22,629 = blank). Record pace: **5-2 control <= 22,629 + 2,460 = 25,089** (trigger <= 24,810). TAS pace: trigger 24,652, 5-2 control 24,931 (our frame = TAS + 504).

| time | agent | file | 5-2 control | frames | vs record | hp/ninpo/art at exit | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-27 04:10 | l51c (third: bird phase) | **`logs/l51_c3d_poweron.inputs.txt`** (24,998 rows; stage rows `logs/l51_c3d.inputs.txt`; = `work/l51c/h_pb5_24481.inputs.txt` + beam `work/l51c/gb_pb5.inputs.txt`) | **24,998** (trigger 24,718) | 2,370 | **-91** (c3b - 6) | **12** / 35 / Windmill | yes: `verify chain l51_c3d_poweron` two replays MATCH (RAM sha1 b901e79b34f7), 0 deaths; `nhchk` NesHawk = Mesen every frame (0 differing, end RAM equal); states `states/l51a_c3d_{24481,24718}` | PASS | **Fastest, but exit hp 12 (c3b: 15).** c3a prefix to 24,270, then ONE Windmill later (Up+B 24,313-14, jump 24,276-77: breaks health 24,371, kills the bat, keeps BOTH birds), stand 24,425-28 on the floor, jump 24,432: a bird hits from the left at 24,460 (hp 15 -> 12) and lifts Ryu onto pillar B (on top X 2,694 on 24,482; c3b 24,487), beam pb5 to the trigger dodging the birds. NesHawk note: a Right after a 3-f stand ending on 24,427 was read 1 f late (pad conflict on 24,428); c3d uses the 4-f stand that NesHawk actually played |
| 2026-10-27 01:40 | l51c (third: bird phase) | **`logs/l51_c3b_poweron.inputs.txt`** (25,004 rows; stage rows `logs/l51_c3b.inputs.txt`; `work/l51c/graft.py "23875:9,24201:1" 24270 13 logs/l51_a_c4_poweron.inputs.txt`) | **25,004** (trigger 24,724) | 2,376 | **-85** (c4 - 13) | **15** / 35 / Windmill | yes: `verify chain l51_c3b_poweron` two replays MATCH (RAM sha1 d20830f94ad1), 0 deaths; `nhchk` NesHawk = Mesen every frame (0 differing, end RAM equal); NesHawk states `states/l51a_c3b_{24391,24724}` | PASS | **BEST.** c3a's bird-phase prefix (9 + 1 blank rows -> the wall bird's own 23,714 boost; floor X 2,596 on 24,391) + c4's no-hit end rows from 24,405 unchanged |
| 2026-10-27 00:25 | l51a (+ l51b) | **`logs/l51_a_c4_poweron.inputs.txt`** (25,017 rows; stage rows `logs/l51_a_c4.inputs.txt`, from `work/l51a/c4_stage.txt`) | **25,017** (verify axis; trigger 24,737) | 2,389 (assemble 2,388) | **-71** (cum ~ -286) | **15** / 35 / Windmill | yes: verify finish (0 deaths, legal, control OK); `verify chain l51_a_c4_poweron` two replays MATCH (RAM sha1 54111d3890e7) | PASS | **BEST.** = c3 with a 2-f faster pillar climb (`pclimb3.py`: Right x13, A+Right x2, Right x22, [A+Left x2, Right x4], [A+Left x2, Right x6], [A+Left x2, Right x4], A+Right x2 -> top 24,500), beam e11 to X 2,801 y 52 on 24,571, then c3's no-hit end rows (e10) -> trigger 24,737, no hit after 24,404 |
| 2026-10-26 23:35 | l51a (+ l51b) | **`logs/l51_a_c3_poweron.inputs.txt`** (25,019 rows; stage rows `logs/l51_a_c3.inputs.txt`, from `work/l51a/c3_stage.txt`) | **25,019** (verify axis; trigger 24,739) | 2,391 (assemble 2,390) | **-69** (cum ~ -284) | **15** / 35 / Windmill | yes: verify finish (0 deaths, legal, control OK); `verify chain l51_a_c3_poweron` two replays MATCH (RAM sha1 30f82a1d5b48) | PASS | = c2 to 24,573, then a NO-HIT end (beam e10, hpmin 15): 1 f slower than c2 but exits with hp 15 instead of 12 (3 more HP for 5-2 / 5-3 boosts). Recommended over c2 unless 5-2 / 5-3 need no HP |
| 2026-10-27 00:30 | l51c (third: bird phase) | **`logs/l51_c3a_poweron.inputs.txt`** (25,004 rows; stage rows `logs/l51_c3a.inputs.txt`; builder `work/l51c/graft.py "23875:9,24201:1" 24270 13 logs/l51_a_c2_poweron.inputs.txt`) | **25,004** (trigger 24,724) | 2,376 | **-85** (c2 - 14) | 12 / 35 / Windmill | yes: `verify chain l51_c3a_poweron` two replays MATCH (RAM sha1 6998a3c6756e), 0 deaths, 5-2 load 24,852; `nhchk` NesHawk = Mesen on every frame to 25,004 (0 differing, end RAM equal); NesHawk states `states/l51a_c3a_{24254,24391,24724}` | PASS | = c1 to 23,874, then **9 blank rows before row 23,875 (TAS-eq 23,345, on the y-96 ground before the 23,355 slash) + 1 blank row on the y-160 step**: the slash misses the WALL bird, which then gives the TAS's own 23,714 boost (hit 24,254 X 2,400 y 132 from the left, hp 12 -> 9, on the y-96 platform 24,268); c1's Windmill/health rows shifted -13 (health 24,383); floor X 2,596 on **24,391 (c1/c2: 24,404)**; c2's end rows from 24,405 graft unchanged (pillar climb, hit at 3,016) |
| 2026-10-26 23:20 | l51a (+ l51b) | **`logs/l51_a_c2_poweron.inputs.txt`** (25,018 rows; stage rows `logs/l51_a_c2.inputs.txt`, from `work/l51a/c2_stage.txt`) | **25,018** (verify axis; trigger 24,738) | 2,390 (assemble 2,389) | **-70** (cum ~ -285) | 12 / 35 / Windmill | yes: verify finish (0 deaths, legal, control OK); `verify chain l51_a_c2_poweron` two replays MATCH (RAM sha1 f85afabf1b98); nhchk RAM-equal to 24,502 | PASS | = c1 to 24,404, then the single-wall pillar climb (on top 24,502, no hit), beam e8 to X 2,801 y 52 on 24,573, beam e9 to the trigger (one hit 15 -> 12 at X 3,013 on 24,715). **41 f better than c1** |
| 2026-10-26 21:55 | l51a (+ l51b) | **`logs/l51_a_c1_poweron.inputs.txt`** (25,059 rows; stage rows `logs/l51_a_c1.inputs.txt`, from `work/l51a/c1_stage.txt`) | **25,059** (verify axis; trigger 24,779) | 2,431 (assemble: control-to-control 2,430) | **-29** (cum ~ -244) | 11 / 35 / Windmill | yes: `verify finish` (0 deaths, control OK, legal); `verify chain l51_a_c1_poweron` two replays MATCH (RAM sha1 171c45df17d6); nhchk to 24,615 RAM-equal | PASS | BASELINE. l51a w2a to 23,588 (wall bird spawned) + l51b v2 (gb_w2a climb, the 23,355 slash kills the wall bird, tosser-3 fix, 24-f wait for the #19 bird boost onto the y-96 platform, 1 Windmill breaks the health lantern) to X 2,596 on 24,404 + l51a end beam e4 (no bird: hit hp 15 -> 14 at 24,477 lifts Ryu, y-96 platform, X 2,800 y 74 on 24,615) + beam e5 to the trigger (hit 14 -> 11 at 24,758 X 3,015) |

### Agent notes (5-1)
* **l51c 04:20: c3b (25,004, hp 15, = c3a prefix + c4's end) and c3d (24,998, hp 12, bird boost onto pillar B) in
  Candidates; write-up "5-1 lock round (third: bird phase)" in `knowledge/legal_a56_notes.md`.** Bird rules (exact,
  simulator `work/l51c/bsim2.py`/`sgrid3.py`): a type-11 bird's x-orbit depends only on Ryu's x(t) since its spawn; only
  stands/Left moves change it (jumps steer y only); enemies freeze on frames with a pending scroll column (`$4C` bit 6).
  Hit: |dx| < 10, bird within 25 px above / 8 px below Ryu's feet; knockback away from the bird, pad ignored. Cheapest
  stands for the 23,714 boost from the left: 10 f (c3b); the faster `cla` climb needs 15 f (same lag). c3d's late
  Windmill (Up+B 24,313) keeps both birds and still breaks health; a 4-f stand at 24,425 gives the pillar-B lift (hp -3).
* **l51c (third: bird phase) 00:30: c3a = c2 - 14 (25,004), see Candidates.** The bird phase is set by WAITS (proof below);
  a 9-f stand on the y-96 ground at our 23,875 (TAS-eq 23,345) + 1 f on the y-160 step makes the 23,355 slash miss the
  wall bird, and the wall bird then gives the TAS's own 23,714 boost from the left (the 24-f step wait is gone; net -13 at
  X 2,436). **For first: the X-2,596 floor arrival is now 24,391** (13 f earlier than v2's 24,404; c2's end rows from 24,405
  graft unchanged, trigger 24,724): NesHawk `states/l51a_c3a_24391`, Mesen `states/mesen/l51c_c3a_24391.mst`, history
  `work/l51c/h_c3a_24391.inputs.txt`, hp 15 np 35 W. Any end improvement on v2's 24,404 should re-graft on 24,391 (check:
  the batter on pillar B spawns ~3 f differently because the spawn iterator is frame-phased). Next (l51c): a bird at the
  pillar-B spot (TAS 23,905) on this line.

* l51a 17:30 (owner of 5-1 control -> the X-1,504 wall; tools `work/l51a/`: `lib.py` (CTL 22,629, LAG 504, base
  `states/mesen/lock_51_pre.mst`), `tr.py` trace, `fol.py` legalized TAS rows at a lag, `gbeam.py` (r1920's generic beam with
  the 5-1 TAS dump for `TP()`), `nhchk.py` (NesHawk vs Mesen from `states/lock_51_pre`, saves `states/l51a_<tag>_<f>`)).
  * Base states: NesHawk `states/lock_51_pre.State` (after row 22,628; x 64 y 64 hp 16 np 0); Mesen
    `states/mesen/lock_51_pre.mst` (22,628) and `lock_51_ctl.mst` (after the blank row 22,629, `$BF` 78 = (F-23) mod 256).
  * **Prep's head start grafts as is**: `work/l51p/pre51_22490.txt` -> X 601 y 128 on 22,994 (TAS-eq 22,490), hp 15, np 20.
    NesHawk: the tosser-1 hit lands 1 frame earlier (22,878 vs Mesen 22,879), Ryu 1 px off for 14 frames, re-converges on
    22,893; identical afterwards (to 23,100). NesHawk state `states/l51a_p_22994` (X 601).
  * `work/l51a/p23100.txt` = head start + prep's `b_r880n` rows to 23,100 (X 760 y 208, Windmill taken at 23,077, np 20),
    NesHawk = Mesen at 23,100. Prep's `b_r880` / `b_r880n` beams END IN THE PIT (X 1,000 y 196-204, falling): don't use their
    tails. Legal TAS rows at lag 504-506 after 23,100: the X-880 bird hits (as prep found); beams running.
  * **HANDOVER w1 (18:15): wall approach, NesHawk = Mesen (only the 22,878-92 tosser-1 transient), judge PASS.**
    Stage rows `work/l51a/w1_23589.txt` (961 rows from the control row 22,629 to 23,589). States (NesHawk `states/l51a_w1_<f>`,
    Mesen `states/mesen/l51a_w1_<f>.mst`, power-on history `work/l51a/h_w1_<f>.inputs.txt` = rows 1..f):
    | our f | TAS-eq (lag 509) | X, y | hp / np / art | `$BF` |
    |---|---|---|---|---|
    | 23,335 | 22,826 | 1,104, 128 (after the pit) | 15 / 30 / Windmill | 16 |
    | 23,559 | 23,050 | 1,440, 205 | 15 / 30 / W | 240 |
    | 23,574 | 23,065 | 1,463, 176 | 15 / 30 / W | 255 |
    | 23,584 | 23,075 | 1,478, 160 (= TAS's X,y exactly at lag 509) | 15 / 30 / W | 9 |
    | 23,589 | 23,080 | 1,485, 160 | 15 / 30 / W | 14 |
    = **TAS +5 at the wall with the TAS's ninpo (30) and hp 15**. Line: head start + b_r880n rows to 23,100 + legal TAS rows
    lag 505 with 4 edits (`work/l51a/fix.py` greedy hit repair): jumps TAS 22,644 -> 22,647, 22,687 -> 22,690, 22,730 -> 22,733
    and Left x2 on 22,697-98 (air turn) -> X 1,104 at 23,335 hp 15 np 30 (both +5s X 864 / 944 taken); then legal TAS rows at
    lag 509 pass tosser 2 untouched (lag 511 is hit at X 1,221). Includes the Left x2 at TAS 22,793-94. **On this line the
    TAS's wall bird does NOT hit Ryu** at TAS-eq 23,081-84 (Ryu stands at X 1,485 and drops to y 208 with the TAS's blank rows).
  * **HANDOVER w2 (19:00): WITH the wall bird (hit at 23,589, hp 15 -> 12 = the TAS's 23,081 hit at lag 508).** NesHawk = Mesen
    (only the tosser-1 transient), incl. the hit (NesHawk replay of `work/l51a/w2a_ext.txt` to 23,604: hp 12, X 1,480 y 144),
    judge PASS. Stage rows `work/l51a/hc_w2a.txt` (960 rows, control 22,629 -> 23,588); states NesHawk `states/l51a_w2a_<f>`,
    Mesen `states/mesen/l51a_w2a_<f>.mst`, history `work/l51a/h_w2a_<f>.inputs.txt`, f = 23,302 (bird spawned), 23,335, 23,560,
    23,575, 23,585 (X 1,479 y 160), **23,588 (X 1,484 y 160 = the TAS's X,y at 23,079, lag 509; the hit comes on the next
    frame with Right held)**; hp 15, np 30, Windmill. Variant w2b (`work/l51a/hc_w2b.txt`, turn at TAS-eq 22,800 instead of
    22,796): hit at 23,591-92 (X 1,488-90); states `l51a_w2b_23585` / `l51a_w2b_23590` (X 1,487 y 162, the frame before the hit).
    * **Why w1 had no bird (spawn rule, bank 7 `spawn_enemies` $E560):** each frame the spawn scan compares 8 table entries with
      `$00` = screen column (scroll / 16); while the camera moves LEFT, `$00` = screen column - 13 and the enemy is placed
      mirrored at the right side. **The wall bird is the X-773 bird's table entry (column 45) re-spawned by a 1-px camera move
      left at screen column 58 (scroll 928-943)**; its "out" bit is free again only because the 22,755 slash killed the X-773
      bird (and the t13). The TAS's air Left at 22,793 does that at scroll 929 -> 928. On w1 our turn came at scroll 923 -> 922
      (column 57 - 13 = 44 = the X-940 walker's entry), so the walker came back instead. Fix = the same Left x2 three frames
      later (TAS-eq 22,796-97, our 23,301-02, scroll 929 -> 928): the bird spawns at (1,136, 64) on 23,302, no time cost.
      Turns at TAS-eq 22,796/97/800/801/804-806 all spawn it (the iterator `$B5` covers the entry on those frames); the wall hit
      then comes at 23,589-96 with the TAS's later presses shifted +3..+5.
  * **w2c / w2d (19:35): wall arrivals with the bird hit LOWER and nearer the wall** (Left x2 at TAS-eq 22,804 / 22,805, rest = w2a):
    the hit comes on 23,595 / 23,596 with Right held (X 1,493-1,494, y 168-172; blank rows give the same frame). NesHawk = Mesen,
    judge PASS. Rows `work/l51a/hc_w2c.txt` / `hc_w2d.txt`; states `states/l51a_w2c_23594` (X 1,493 y 168) and
    `states/l51a_w2d_23595` (X 1,494 y 170) + Mesen `.mst` + `work/l51a/h_w2c_23594.inputs.txt` / `h_w2d_23595`. hp 15 / np 30 / W.
    (A turn at 22,801 diverges on NesHawk: the Left on 23,306 is read as Right, a pad-read conflict. Don't use it.)
    Also at 23,560 / 23,575 / 23,585 (`states/l51a_w2c_<f>`, `l51a_w2d_<f>` + `.mst` + histories): same Ryu as w2a (X 1,442 y 208
    at 23,560), but the wall bird spawned 8 f later (23,310), so its phase differs. Use them for climb beams with a different bird phase.
  * **Bird facts for the wall -> 23,905 part (bank 7 $C735 `bird`):** a type-11 bird moves y 1 px/f toward Ryu's height and
    accelerates x by 1/16 px/f^2 toward Ryu's x, with no speed cap: a bang-bang pendulum around Ryu. Ryu's x-speed is fixed
    (1.5 px/f whenever Right is held), so only waits and Ryu's height (jumps) steer it. On w2a + l51b's climb (lag 530) the
    wall bird is ~35 px AHEAD at TAS-eq 23,359 (TAS: ~50 px behind), so the TAS's 23,355 slash kills it. Without that slash it
    survives but hits from the front at TAS-eq 23,498 (X 2,078 y 85). Room 22 spawn table (bank 2 $9FF6/$A013/$A030, 29
    entries): the type-11 entries are #9 (column 45 = the X-773 / wall bird) and #19 (column 114, appears at X ~2,000 y 207
    at scroll 1,824 = TAS 23,416).
  * **Climb cla (20:00): on top X 1,531 y 92 on 23,658 (5 f better than gb_w2a's 23,663; TAS 23,133 + 525).** Beam
    `work/l51a/gbeam.py` from `l51a_w2a_23575` (goal X >= 1,530 y <= 96, h = max((1530-X)/1.5, (y-96)/2), width 300, cell 3, hpw 0;
    alphabet R|AR|L|AL|-|A). Full stage rows `work/l51a/cla_full.txt` (1,030 rows to 23,658); NesHawk = Mesen, judge PASS;
    states `states/l51a_cla_{23589,23620,23658}` + `states/mesen/l51a_cla_23658.mst` + `work/l51a/h_cla_23658.inputs.txt`.
    The same beam from w2c (bird 8 f later) is worse: 23,671. With legal TAS rows at lag 525 after cla, the wall bird hits
    again at 23,695 (hp 9) and Ryu falls at TAS-eq 23,365, so the bird phase still needs work after the climb.
  * **(20:55) All l51a Mesen states are now RAM-equal to NesHawk** (thanks second): the tosser-1 transient left $47D/$485 (slot-5
    x/y fraction) and $2E/$3B different. New base `states/mesen/l51a_p23100N.mst` = Mesen after `work/l51a/p23100.txt` (23,100)
    patched with NesHawk's RAM; with it, w2a to 23,588 has ZERO game-RAM differences ($000-$7FF outside stack/OAM). Every
    `states/mesen/l51a_{w1,w2a,w2b,w2c,w2d,cla}_*.mst` was regenerated from it (same names). `work/l51a` tools start from it
    automatically (`lib.start_core`). `nhchk.py` now also prints the full end-RAM diff (cla: none).
  * **END piece (22:00-23:10), on second's v2 (X 2,596 y 208 on 24,404, TAS 23,850 + 554):** with no bird for the 23,905
    boost, Ryu has to climb the X-2,656 pillar (left face, top y 128). Beams cling-loop at the X-2,784 wall. Geometry: floor
    to X 2,783; wall X 2,784-2,799 (top y 96); the y-96 block runs to X 2,911 with a pit under it; floor again from X 2,912;
    y-96 platform X 2,720-2,751.
    * c1's end (beam e4): an enemy hit (hp 15 -> 14 on 24,477) lifts Ryu; pillar top 24,544; X 2,800 y 74 on 24,615.
    * **Single-wall pillar climb (`work/l51a/pclimb2.py` enumeration, 3,000+ variants):** Right x17, A+Right x2, Right x18
      (cling), [A+Left x2, Right x6] x3, A+Right x2 -> on the pillar top X 2,694 y 128 on **24,502** (TAS 23,919 + 583), no hit,
      hp 15. That is 42 f better than c1. NesHawk = Mesen (RAM-equal), `states/l51a_pc1_24502`, rows `work/l51a/pc1.txt`.
      Then beam e8: X 2,801 y 52 on **24,573** (hp 15; `work/l51a/pc1e8.txt`). The TAS rows from the pillar top don't work
      here (Ryu lands against the X-2,784 wall).

* second (l51b) 18:40 (owner of the X-1,504 wall -> stage end; tools `work/l51b/`: `lb.py` (helpers, our axis = TAS + 504),
  `mkst.py` (research state from a TAS state with the `$BF` poke for c = 78 + lag), `fol.py` (legal TAS rows at a lag from any
  state, events + slots), `gbeam.py` (r1920's beam with the 5-1 dump), `climb.py` (wall-climb enumeration), `thr3.py`
  (Windmill-throw grid)). **l51a: please post Mesen + NesHawk states with history at the wall (TAS-eq ~23,050-23,080, before
  the wall-bird hit) as soon as you have them; I re-solve the climb and everything after on them.**
  * Real 5-1 control state = the poked TAS state (Mesen `states/mesen/l51b_real22628.mst`, power-on replay): the head start
    + legal rows reproduce prep's chain test exactly (hit at X 881, death at 1,011).
  * TAS-state research (c 93 = lag 15): prep's `b_e23` end beam (built on c 86) does NOT transfer: at c 93 it is hit at
    23,936 and misses the y-96 platform (X 2,779 on the floor). The 23,905 spot depends on the type-11 birds (s6/s7), whose
    phase is set by the whole history. A no-hit line from the floor (X 2,597 at 23,850) is slow: X 2,779 y 150 at 23,984
    (TAS X 2,760 y 96 at 23,963), so the bird boost there is worth > 25 f.
  * Windmill throws (thr2, c 98): with Up+B+**Right** (no release) the first throw at 23,744-49 and the TAS's 2nd at 23,777-78
    give the TAS's exact positions to X 2,760 at 23,963, BUT only one Windmill fires (np 35), the health lantern X 2,576 is
    not broken (no +6) and the 23,905 boost costs hp 9 -> 6. Clean grid with both throws running.
  * thr3 (clean grid, c 98, 3,090 throw variants): only ONE Windmill ever fires in the 23,738-23,800 window (the 2nd press
    comes while the first Windmill is still out); X at 23,850 = the TAS's 2,597 for every variant. The health lantern X 2,576
    breaks only with the first throw on 23,739 (Up+B, Right released) -> hp 9 -> 15 at 23,843.
  * **w2a wall climb (19:45, Mesen):** after the hit (23,589) Ryu clings to the wall at y ~137 on 23,604 (TAS: y 132 on 23,095).
    Best legal climb so far = beam `work/l51b/gb_w2a.inputs.txt` (75 rows from 23,589; chimney-ish A+L/A+R switches) -> on top
    X 1,503 y 96 on 23,645, **X 1,530 on 23,663 = TAS 23,133 + 530 (lag 509 -> 530: the climb costs 21 f; the TAS's L+R glide
    climbs y 132 -> 96 in 18 f, ours takes ~41)**. Macro enumerations (3,192 + 3,360 cycle variants of [A+L, R x n] /
    [A+L, A+R, R x n]) are 15+ f worse. Beam from 23,560 (jump timing + hit height free) running.
  * **On w2a + gb_w2a the legal TAS rows at lag 530 then match the TAS exactly to TAS-eq 23,698 (X 2,378), incl. tosser 3
    (c'' 104), but the 23,714 boost is gone: the wall bird disappears at ~23,890 (TAS-eq 23,360, ahead of Ryu at X 1,904
    when the TAS's 23,355 slash comes; in the TAS it trails 60 px behind)** -> Ryu falls into the X 2,432 pit (dead 24,264).
    The wall bird is also the TAS's 23,905 booster. Beam for the y-96 platform from 24,100 running; next: climb variants
    that keep the bird behind Ryu.
  * **(20:45) A working second half without the wall bird (w2a + gb_w2a, lag 530; the wall bird dies to the TAS's 23,355
    slash):** the #19 bird (the TAS's s6, X ~2,000 spawn) follows the TAS's s6 path exactly but is 67 px behind at the 23,714
    spot. Enumeration `work/l51b/p96.py` from `states/mesen/l51b_w2a_24200.mst` (TAS-eq 23,670, Ryu on the y-160 step X 2,336):
    **wait 24 blank frames, then A+Right x2, Right -> the #19 bird hits at 24,258 (hp 12 -> 9) and lifts Ryu onto the y-96
    platform (lands 24,272), X 2,436 on 24,295 = TAS 23,741 + 554** (the wait costs 24 f). Any bird hit near the apex of a jump
    from the y-160 step works (front or back), because the y-96 platform is one-way from below.
  * **Throws/health on that line (`thr4.py`, 1,140 variants):** jump off the platform 2 f early (A+Right on TAS-eq 23,739-40) with
    ONE Windmill Up+B on 23,738-39 (Right released) -> health lantern broken, hp 9 -> 15 on TAS-eq 23,842, np 35, no hit, X 2,611
    at TAS-eq 23,860 (TAS 2,612). A second throw never fires; it isn't needed (no bird hit at 23,775 on this line).
    State `states/mesen/l51b_p96a_24404.mst` (TAS-eq 23,850, X 2,596 y 208, hp 15, np 35), history `work/l51b/h_p96a_24404.inputs.txt`
    (power-on rows, judge PASS). No bird is left for the 23,905 boost -> no-boost beam to X 2,830 running (TAS-state test: ~+51).
    **(21:30) That line was NOT NesHawk-valid** (old Mesen base: slot-5 subpixel $47D, see first's 20:55 note): on NesHawk the
    tosser-3 type 15 hits Ryu at 24,108 (TAS-eq 23,578, hp 12 -> 10). Replaced by v2 below.
  * **HANDOVER v2 for the END piece (21:40, first): Ryu on the floor X 2,596 y 208 at 24,404 (= TAS 23,850 + 554), hp 15, np 35,
    Windmill, `$BF` 61; NesHawk = Mesen (end RAM identical outside the stack), judge PASS.** Stage rows `work/l51b/s_v2_24404.txt`
    (1,776 rows from the control row 22,629), power-on history `work/l51b/h_v2_24404.inputs.txt`; NesHawk states
    `states/l51b_v2_{24040,24200,24290,24404}`, Mesen `states/mesen/l51b_v2_{24200,24404}.mst` (built on first's regenerated
    `l51a_w2a_23588.mst`). Line: w2a -> beam climb `gb_w2a` (X 1,530 on 23,663, lag 530) -> legal TAS rows lag 530 (A+Right
    23,279-80; the wall bird dies to the TAS's 23,355 slash) with the **tosser-3 jump moved 2 f later (TAS 23,546-47 instead of
    23,544: no type-15 hit; `t15.py`, any jump 23,546-23,551 works)** -> 24,200 on the y-160 step (= TAS 23,670 exactly) -> wait 24
    blank rows, A+Right x2, Right: the #19 bird hits (hp 12 -> 9) and lifts Ryu onto the y-96 platform -> X 2,436 on 24,295 (lag
    554) -> Up+B (Windmill) on TAS-eq 23,738-39 + jump 23,739-40, then legal TAS rows lag 554: health hp 9 -> 15 at 24,396, no hit.
    Remaining losses vs the TAS on my side: climb +21, platform wait +24 (bird phase), so the cheapest gains are the bird phase
    (a bird near Ryu at TAS-eq ~23,690-23,714) and the climb.
  * **second FINAL (00:45, stopping; all my jobs stopped): nothing better than v2 (used in c1) found for my piece.** Tried, all
    worse or dead: 74 alternative beam climbs 23,665-68 + TAS rows (`evcl.py`: the wall bird survives and hits, only gb_w2a works);
    first's faster cla + no-hit repair (+20 f); keeping the wall bird alive with a TAS-path beam (lag > 560) or a stay-high beam
    (`gb_hi1`: no platform by 24,300); keeping the #19 bird for the 23,905 boost (`thr5.py`, 405 throw variants: it or the t8 then
    knocks Ryu into the pit); killing + re-spawning the #19 bird at column 127 (`resp.py`, 696 variants: it re-spawns behind Ryu and
    the type-15 hit returns). Write-up: `knowledge/legal_a56_notes.md` "5-1 lock round (second)".

### Candidates (4-3)

On k932b (4-3 control 19,297 = Left on that row). Record pace: 4-4 control <= 19,297 + 2,557 = **21,854** (trigger <= 21,575).

| time | agent | file | 4-4 control | frames | vs record | hp/ninpo/art at exit | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-26 07:30 | r1920 | **`logs/l43_r1920_c2_poweron.inputs.txt`** (21,578 rows; stage rows `logs/l43_r1920_c2.inputs.txt`, row 1 = Left on 19,296); with 4-4: `logs/l44p_r1920_c2_poweron.inputs.txt` | **21,857** (5-1 control 22,629 = best band; v 13) | 2,561 | **+3.8** | 14 / 5 / J&S | yes: nhchk 0 differing frames; verify finish OK; `verify chain l43_r1920_c2_chain` two replays MATCH (RAM sha1 d4e9ccff650f) | PASS | = c1 to the zigzag, then beam `r20B`: takes the +10 X 464 and spends ONE spin (np 5 at the y-96 platform X 571, 21,459), jump at once, no +5 X 656 -> trigger 21,578 (6 f better than c1) |
| 2026-10-26 06:40 | r1920 | `logs/l43_r1920_c1_poweron.inputs.txt` (21,584 rows = k932b rows 1-19,295 + stage rows `logs/l43_r1920_c1.inputs.txt`, row 1 = Left on 19,296); with 4-4: `logs/l44p_r1920_c1_poweron.inputs.txt` | **21,863** (5-1 control 22,635, F in the best band; v = `$62` 9) | 2,567 | **+9.8** (target 4-4 control <= 21,853) | 14 / 5 / J&S | yes: `work/l43/nhchk.py` 0 differing frames; verify finish (control 21,864 on the verify axis); `verify chain l43_r1920_c1_chain` two replays MATCH (RAM sha1 72bfaa659895) | PASS | builder s_m19 to 20,479 + block beam (top 20,523) + room-19 beams (lag 420 to the last roof) + exit by the ladder (20,962, no boost: no type-17s without the gunner) + room-20 entry grid (pillar 21,143) + legal TAS rows + zigzag chimney climb (pillar B top 21,346) + beam to the y-96 platform + jump/pause/slash for +5 X 656 -> trigger 21,584 (np 0 would be 21,575 but costs ~88 f in 4-4) |

### Agent notes (4-3)

* r1920 22:40 (rooms 19-20 owner; research on TAS states, tools `work/r1920/`: `gbeam.py` generic legal beam with goal/h/rank
  expressions incl. TAS-path progress `TP()`, `tv.py` quick row-spec tests, `fol.py` legalized-TAS follow from a state,
  `e19.py` room-19 entry macro enumeration). Findings so far (TAS states, Mesen):
  * Room-19/20 entry pillar (X 160-207, top y 128): the ladder face (X 160) tops out at a cling y 148; a jump-off from
    there peaks at y ~133 -> the top is NOT reachable from the face (both TAS and record use the box / steps).
  * Room 19 box route: Ryu lands on the box facing left; a legal turn needs a grounded Right frame before A (A+Right on
    the landing frame keeps facing left; the box edge is at X ~119, so land at X <= ~117). The TAS's U,U on the ladder
    before the kick are needed (without them the kick misses the floor top y 208 and Ryu falls into the pit).
  * Room-19 stepped block (TAS 20,085-20,126): legal beam `work/r1920/gb_blk2.inputs.txt` from `l43p_tas20085`
    (`R:6 A+L:2 R:5 A+L:2 B+R:2 R:2 A+L:2 B+R:2 R:17`, spin kills the gunner) lands on the block top X 610 at 20,125
    (TAS X 632 at 20,126) = **TAS +13.6**. The TAS's L+R is the only way to move right at 1.5 px/f while facing left;
    legal drift over the top is 0.5 px/f. No left wall in the chimney (X 576 column is not solid).
  * After that, legalized TAS rows at lag 13-15 DIVERGE (enemy phase: t20/t8 flyers hit Ryu, falls into the pit at X
    ~830-900): room 19's second half needs a beam on the real line.
  * Room 20 y-160 step -> pillar top directly: misses by 1 px (X 155 at y 129). Legal TAS route with a turn on the
    y-128 step (`L:7 R A+L:2 L:30 R:2 A+R:2 R` from `l43p_tas20570`) = pillar X>=168 at 20,677 = TAS +1.
  * Room 20 X 392 climb (TAS 20,827-20,852, kicks off pillar A's right face with 1-f A+L/A+R): legal best so far =
    C8 on pillar B's face (`R:18 A+L:2 R:5 A+L:2 R:6 A+L:2 R:6 A+L:2 R`) ~TAS +18 (drift over the top facing left).

* l43 23:50 (whole-stage solver on the chain; tools `work/l43/`: `lib.py` (k932b, CTL 19,297, base Mesen
  `states/mesen/l43_k932b19296.mst`), `beam.py` (legal beam: TAS distance at a lag, or any score/goal expression; `--mst`
  for any state), `tr.py` trace, `follow.py` / `sync.py` legalized TAS rows at a lag, `mk.py` macro rows, `nhchk.py`
  NesHawk vs Mesen + states). Segment files = stage rows from the control row 19,297 (row 1 = Left).
  * **Control row: on k932b, Left on row 19,296 already moves Ryu** (x 224 -> 222 on 19,296; Mesen, `work/l43/rebase.py`);
    `verify finish` reports control +1 (k932a: verify 19,299 vs the real 19,298). So 4-3 could start 1 row earlier if
    row 19,296 (blank, pre-control, like the 1-1 amendment) were allowed to be Left. Everything below uses 19,297.
  * Room-18 entry: chimney between the left wall and the box, cycle `(R+U, A+L+U, A+L, R, R+U) x5` after 4 blanks
    (`work/l43/s_lad1.txt`): box top y 160 at 19,485 (pre2: 19,503), X 218 at lag 364 (TAS +26; record ~+38).
  * X 218 -> chimney: legalized TAS rows at lag 364 match the TAS exactly (spin-break of +5 X 272 included) until the
    TAS's 1-f U+D at 19,281; legal chimney = single-wall C8 on the right wall X 346, and the climb itself carries Ryu
    over the lip (no L+R needed): beams ch1 + lip3 -> X 368 y <= 96 at 19,709 (= TAS-state research `lipT`, TAS +13
    for the chimney+lip).
  * After the lip: legal TAS rows at lag 376 match exactly (incl. the 19,483 spin on +10 X 592, np 15) to X 881. **The
    TAS's exit boost is not available on our line:** our type-19 flyer runs 10 px behind Ryu (TAS 35 px; it spawned
    earlier) and hits him at X 881 (20,051), knocking him into the pit. Fix used: spin at TAS-eq 19,655 (kills flyer +
    blade, np 15 -> 10), then the exit LADDER (y 80-111) climb: room 19 at 20,091 (lag 380, TAS +42) without launch.
  * Room 19 without the launch: Ryu appears on the ladder at y 232; beam e19 -> box -> turn -> jump onto the pillar
    (20,196 X 169) -> legal TAS rows at lag 396 match exactly from X 212 (run to X 212 first, don't jump at X 169) to
    X 593 at 20,480 (TAS spins 19,930 / 20,027 -> np 0).
  * Stepped block on the chain (np 0, no spin): beam blk1 -> block top 20,540 (TAS +66 cum, +8 vs the lag-396 line).
    On the TAS state with a spin: blkT +8 at 20,144 (`work/l43/b_blkT.txt`). Without the spin the type-20 flyer
    survives and hits Ryu from behind at ~X 777 -> pit; re-sync beam running.

* r1920 00:05 -> l43: to split the work: **I take rooms 19-20 on the chain from your `work/l43/s_p19.txt`** (rows to the
  block approach X 593 at 20,480, lag 396; np 0) - block, room-19 second half (type-20/t8 flyers, pit at X ~830-900),
  exit, room 20 to the trigger. Please keep improving rooms 17-18 (exit boost / room-19 entry with launch / np 15 at
  room 19); when your room-19 entry changes, post it and I re-graft (my segments are re-solved from your rows).
  TAS-state numbers so far (Mesen): room-19 entry legal = TAS +2 (`work/r1920/e19_tas.txt`, U,U then kick, box, turn);
  room-20 entry -> pillar X>=168 = TAS +6 (ladder cycle x3 to the y-192 step, y-160 step, turn on the y-128 step);
  room-20 X 392 climb = TAS +31 by C8 on pillar B (biggest legal loss found; kicks off pillar A only cling when moving
  left into it from X > 392 with vy >= 0).

* l43 02:50 -> r1920 (ack: you own rooms 19-20; I stopped my room-19/20 beams and work on rooms 17-18 now). Enemy
  mechanics found (Mesen pokes, our chain + TAS states):
  * **Room-19 type-17 flyers (the TAS's room-19 exit boost) only spawn while the type-1 gunner (slot 7, X 930 y 128,
    spawned at Ryu X ~817) is ALIVE**: TAS state 20240 + TAS rows, poke-kill t1 at 20255 -> no type 17 at all (t5 then
    takes slot 7). Our q19 beam slashed the gunner at 20,722 -> no t17 -> no launch. `$BF` pokes change nothing.
  * **The block's type-20 flyer RESPAWNS** at (625,83) when it leaves the screen (ours: gone 20,537, respawn 20,565 at
    Ryu X 680); the TAS killed it with the 20,114 spin, so it never came back. Without ninpo for that spin it chases
    Ryu at y 83.
  * **Room-18 type-19 flyer = released by the type-4 walker on the y-96 ledge (spawned at Ryu X 320) 138-139 f after
    the t4 spawn, from the t4's position (X ~372 y 82); then flies right at a constant 1.82 px/f.** Killing t4 -> no
    flyer. Our chimney+lip costs 13 f vs the TAS between the t4 spawn (X 320) and X 470, so our flyer starts 96 px
    behind Ryu instead of 116 and catches him at X 881 (20,051) in the platform-end jump (TAS: X 922 at the exit wall
    = the boost). A legal line can't make that up -> **the TAS's room-18 exit boost is out of reach unless the chimney/
    lip gets ~10 f faster**. Testing now: keep np 15 (no spin) by dodging/absorbing the flyer, ladder exit.

* l43 04:10 (handing back; rooms 17-18 + room-19 entry final, full table + resume in `legal_a34_notes.md` "4-3 lock
  round"): **prefix `work/l43/s_m19.txt` = X 593 y 165 at 20,480 (lag 396, TAS +58), hp 15, np 0, J&S**; room 19 at
  20,091 (TAS +42, record pace 20,131); NesHawk = Mesen (0 differing frames to 20,710). Entry states: Mesen
  `states/mesen/l43_s19598/19709/20091/20225/20480.mst`, NesHawk `states/l43_pb_19598/20091/20480`, history
  `work/l43/h20480.inputs.txt`.
  * Floors measured: chimney + lip = TAS +12/13 (legal cycles max 44 px / 30 f vs the TAS's 48 / 25); room-19 entry
    without the launch: pillar top 20,196 by two independent beams (e19, e19b) = +16 vs the TAS's launched entry.
  * **Free frame: Left on locked row 19,296** (the real 4-3 control row on k932b): my whole prefix replays identically
    one frame earlier (room 19 at 20,090). Coordinator's call (pre-control row, like the 1-1 amendment).
  * np 15 at room 19 is not cheap (>= 14 f, see the flyer notes); for np 5 at the block, an idea for r1920: do the TAS's
    spin #2 (type-6 pair) earlier, then break +5 X 480 y 144 with an air slash at np 0 (a slash, not a spin) on the way.

* r1920 08:40 (final): **best verified = c2** (`logs/l44p_r1920_c2_poweron.inputs.txt`, 4-4 control 21,857 = record +3.8,
  5-1 control 22,629, v 13, hp 14 / np 5 / J&S). A Mesen-only c3 (beam `r20C`, trigger 21,570 = 4-4 control 21,849, record
  -4.2) is NOT NesHawk-valid: its A press on a landing frame (21,427) jumps on Mesen but not on NesHawk; the 1-f-later
  press (`work/r1920/c3c.txt`, NesHawk = Mesen) breaks the rest and the quick re-beam (`r20D`) found nothing. Resume from
  `states/mesen/r20_c3c_21429.mst` (history `work/r1920/h_r20_c3c_21429.inputs.txt`) with a wider finish beam (np 5 plan).
  Details/resume: legal_a34_notes.md "4-3 lock round (rooms 19-20)". All my jobs are stopped.

### Candidates (4-2)

On r15_c (4-2 control 16,998, `$BF` 81). Record pace: 4-3 control <= **19,301** (trigger <= 19,022). Stage rows start
with Right on the control row 16,998; verify from `lock_42_pre` + `work/l42a/h16997.inputs.txt`.

| time | agent | file | 4-3 control | frames | vs record | hp/ninpo/art at exit | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-25 21:25 | wall | **`logs/l42_w_k932b_poweron.inputs.txt`** (19,297 rows = r15_c rows 1-16,997 + `logs/l42_w_k932b.inputs.txt`; stage rows `work/l42w/s_k932b.txt`; end state `states/l42_w_k932b_end`) | **19,297** | **2,299** | **-4.8** (cum -204.8) | 15 / 10 / J&S (133) | yes (verify finish; `verify chain l42_w_k932b_chain`: two replays MATCH, RAM sha1 2ca737481fff) | PASS | = k932a with a better wall climb (bounded beam `wb_k932c`): A+Right 18,989-90 just before the contact, A+Left 18,991 (jump off on the contact frame), then wall jumps A+Left 18,997-98 / 19,003-04 / 19,009-10 -> **trigger 19,017 (TAS +21), no boost** |
| 2026-10-25 19:50 | wall | **`logs/l42_w_k932a_poweron.inputs.txt`** (19,299 rows = r15_c rows 1-16,997 + `logs/l42_w_k932a.inputs.txt`; stage rows `work/l42w/s_k932a.txt`; end state `states/l42_w_k932a_end`) | **19,299** | **2,301** | **-2.8** (cum -202.8) | 15 / 10 / J&S (133) | yes (verify finish; `verify chain l42_w_k932a_chain`: two replays MATCH, RAM sha1 9623cc8f39bd) | PASS | agent a `b2_k3` to 18,932 (X 2,950) + wall `we_k932_nh`: land on the post, A+Right off it at 18,966, ladder contact y 129 at 18,991, 1.8 px/f ladder cycle, **trigger 19,019 (TAS +23), no boost** (no type-11 bird alive on this line; the trailing type 13 never boosts here) |
| 2026-10-25 16:55 | l42a | `logs/l42_a_rough1_poweron.inputs.txt` (19,358 rows = r15_c rows 1-16,997 + `logs/l42_a_rough1.inputs.txt`; end state `states/l42_a_rough1_end`) | 19,358 | 2,360 | +56 | 8 / 10 / J&S | yes (verify finish; `verify chain l42_a_rough1_chain`: two replays MATCH, RAM sha1 20175eefaf88) | PASS | FALLBACK only: prep sync to 18,496 + progress beams x4/x5 (hits) + wall agent `we_r963_h8` |

### Agent notes (4-2)

* l42a 14:20: **start states** (from `lock_41q_pre` + r15_c rows; Mesen from `l41q_ctl.mst` + the same rows, identical x/y/BF):
  NesHawk `states/lock_42_pre` (16,997), `states/lock_42_ctl` (16,998, blank control row = the locked file),
  `states/lock_42_ctlR` (Right on 16,998: x 65.5 = the TAS's 16,682 state except `$BF` 81 vs 21, `$62`, score);
  Mesen `states/mesen/lock_42_pre.mst`, `lock_42_ctl.mst`, `lock_42_ctlR.mst`; history rows 1-16,997
  `work/l42a/h16997.inputs.txt`. Like 4-1, the 4-2 stage rows start with the control-row Right (row 16,998; Right
  there = +1.5 px, Right earlier = nothing). Tools `work/l42a/` (lib/tmod/beam/tr/g1).
* l42a 14:20: **legal TAS rows at lag 316 (our f = TAS f + 316) track the TAS EXACTLY (d 0) from control to X 1,310
  (17,827)**; tossers 2/3: hit at 17,828 (TAS 17,512, our `$BF`). Beam `w2a` (rows 741-924) = **TAS +0 at X 1,450**
  with an EARLIER J&S spin (np 5 -> 0 at 17,828, hp 16); then TAS rows lag 316 again = d 0 to **X 2,192 at 18,418**
  through the TAS's L+R spot (Left 18,381, A+Right, Right instead of L+R) = `work/l42a/bm_w3a.txt` prefix.
  Next break: 18,423 (X 2,200): the trailing type-13 walker (slot 7) the TAS kills with a LEFT-facing air slash at
  TAS 18,075 (it holds L+R to keep facing left). Pure Right takes the hit (beam w3a: +22 at X 2,330). Grid running.
* l42a 16:05: **ROUGH real-chain states near the exit wall (for the wall agent; NesHawk = Mesen, misread only 17,074, harmless):**
  rows `work/l42a/b2_x5.txt` (stage rows, row 1 = control row 16,998; judge PASS on history + rows) = prep's
  `s42_to18180` + progress beams x4/x5 (with hits; +36 f vs TAS at X 2,950, NOT the final line).
  * frame **18,930**: X 2,901 y 192, hp 9, np 10, J&S, `$BF` 221; enemies slot 5 type 11 (X 2,939 y 171), slot 7 type
    13 (X 2,847 y 166). NesHawk `states/l42a_r18930`, Mesen `states/mesen/l42a_r18930.mst`, history
    `work/l42a/h_r18930.inputs.txt`.
  * frame **18,963**: X 2,950 y 152 (airborne), hp 9, np 10, J&S, `$BF` 254; slot 5 type 11 (X 2,901 y 153), slot 7
    type 13 (X 2,899 y 155). NesHawk `states/l42a_r18963`, Mesen `states/mesen/l42a_r18963.mst`, history
    `work/l42a/h_r18963.inputs.txt`.
  The final line should arrive ~30 f earlier (target TAS pace: X 2,950 at ~18,927) with other bird timing.
* l42a 16:40: **X 2,336 (chain 18,512): the legal options, measured (Mesen, on the real chain):**
  * **Facing is fixed in the air** (`$84` bit 0x40 never changes; Left in the air only stops/reverses x): an air slash
    always goes forward. 1,044 variants (jump 18,381-83, Left 2-4 rows at every phase, B offsets 0-4; `g2.py`) kill
    the trailing type 13 (slot 7) in **0** cases.
  * **Ground turn then jump** (Left 18,379-80, A 18,381): Ryu jumps facing left and Right in the air moves him only
    ~0.7 px/f (X 2,132 -> 2,143 in 15 f), and the type 13 hits him at 18,388 anyway. A legal L+R substitute does not exist.
  * **J&S spin with real ninpo WORKS**: with 5 ninpo, a spin anywhere 18,391-18,521 -> **no hit, TAS pace (2 f ahead)
    to X 2,708 at 18,760, hp 16** (`spin5.py`, `np5.py`, ninpo poked). **But the budget can't reach it cheaply**:
    with J&S and ninpo >= 5 EVERY air B spins (Down+B too, measured at 18,059 and 17,465), and the TAS's air slash at
    18,242 is required (it stops the type-13 jumper at X 1,957; 1,000+ no-B jump variants `g3.py` all get hit at
    18,248; a ground slash at take-off freezes Ryu). So the line needs 5 (thrower spin 17,828) + 5 (18,242) + 5
    (18,391-521) = **15 ninpo by X 1,310**. The only on-line ninpo is +5 X 704 (TAS). **+5 X 784 / X 1,152 are not
    free:** y 160 is out of reach of a ground slash (measured), and an air slash with the X-704 ninpo is a spin = net 0
    (17,465: np 5 -> 0 -> 5). So 15 needs two +10 detours (X 432 and X 768/1,248: ~8 + ~35 f). Without the thrower
    spin the thrower window costs +13 f (beam `w2ns`, hp 15).
  * **Damage boost:** the hits here come from the front/below (type-11 bird slot 5, type-8 slot 3), so the knockback
    goes LEFT (backwards); a hit from the trailing type 13 behind pushes right at 1 px/f (< 1.5 run). No gain.
  * So the best legal option is a hit-taking search line; grids/beams running now (`g4.py` jump/slash timing at
    18,470-18,545; TAS-distance beam with diversity `t1`).
* l42a 17:45: **X 2,336 SOLVED BEST AS A FORWARD DAMAGE BOOST: TAS +9 at X 2,560, hp 15 (record ~+14 there).** Skip
  the TAS's jump at 18,479 (pure Right on the y-128 ledge): the trailing type 13 (slot 7) hits Ryu from BEHIND at 18,493
  (X 2,308, hp 16 -> 15); the knockback goes RIGHT (+1 px/f) and up over the birds, and the invincibility carries him
  through: at 18,547 he lands at X 2,372 y 128 with every enemy behind him. Then a TAS-distance beam (lag 325, `k1`):
  **X 2,560 at 18,672 = TAS +9, hp 15**, NesHawk = Mesen (end X 2,560 y 163 hp 15; misread 17,074 only). Rows
  `work/l42a/b2_k1.txt` (stage rows, row 1 = control row). Every jump/slash/spin-free alternative cost +20..+45 f
  (`g4a` 594 jump/slash variants >= 1 hit and X 2,409 at 18,640; TAS-distance beams +23..+36; A* w 1.3-1.5 +15..+30).
  Continuing to X 2,950 with the +10 X 2,784 now (beams k3/k4); states for the wall agent follow.
* l42a 18:15: **BEST LINE STATES FOR THE WALL (NesHawk = Mesen; judge PASS):** rows `work/l42a/b2_k3.txt` (= b2_k1 +
  beam k3: pure pace from X 2,560, +10 X 2,784 taken, no spin) - **X 2,950 at 18,932 = TAS ~+11, hp 15, np 10, J&S**.
  * **18,880**: X 2,872 y 192, hp 15, np 10, `$BF` 171; only enemy slot 7 type 13 (X 2,839 y 118, behind). NesHawk
    `states/l42a_k18880`, Mesen `states/mesen/l42a_k18880.mst`, history `work/l42a/h_k18880.inputs.txt`.
  * **18,932**: X 2,950 y 148 (airborne), hp 15, np 10, `$BF` 223; slot 7 type 13 (X 2,898 y 147). NesHawk
    `states/l42a_k18932`, Mesen `states/mesen/l42a_k18932.mst`, history `work/l42a/h_k18932.inputs.txt`.
  * NOTE: no type-11 bird is alive here (the TAS's boost bird is slot 5); the trailing type 13 is the only enemy.
    Trigger needed for record pace: <= 19,022 (= 90 f after 18,932).
* l42a 19:05: **for the bird boost (wall agent's request): state with the type-11 bird ALIVE and BEHIND Ryu** on the
  best line: frame **18,760**: X 2,692 y 156, hp 15, np 0 (+10 X 2,784 still ahead), J&S, `$BF` 51; **bird slot 5 type 11
  at X 2,638 y 160 (54 px behind)**, slot 7 type 13 X 2,730 y 51. NesHawk `states/l42a_b18760` (= Mesen), Mesen
  `states/mesen/l42a_b18760.mst`, history `work/l42a/h_b18760.inputs.txt` (rows `work/l42a/b2_kb1.txt`, judge PASS).
  (b2_k3 and b2_kb1 both continue b2_k1 from 18,672; k3 slashed the bird at 18,720.) My bird-alive continuation `b2_kb1` reaches X
  2,950 at 18,948 but the bird hits Ryu from the FRONT at 18,844 (hp 12) - the approach from 18,760 needs steering.
* wall 15:45 (exit wall, research on TAS states `states/mesen/l42w_tas18596/18620/18642.mst`, tools `work/l42w/`):
  **the exit wall is a LADDER column (kind 9, X ~3,040, y 80-191; exit tile above y 80)**; floor y 192, the short post
  (y 176) at X ~2,977-2,992, nothing else to stand on. Trigger = first frame `$5C` 2 -> 0 (Ryu y 84 at X 3,035).
  Legal climb = the 1.8 px/f ladder cycle `A+L+U, A+L, R, R+U, R+U` (catch on the R+U/ALU frame). Best legal lines
  from TAS 18,596 (`work/l42w/wenum.py`): **no hit: land on the post, jump from it at X ~2,999 (TAS 18,641), touch the
  ladder at the jump apex y 128 at X 3,035 (18,666 = pure pace), climb -> trigger 18,694 = TAS +14, hp 16**
  (`work/l42w/we_t596_h16.inputs.txt`); **with the TAS's bird boost (hit in the air, hp -3) -> 18,683 = TAS +3**
  (`we_t596_h13`). So: arrive on the post / at pure pace; contact time + (y - 84)/1.8 + ~3 = trigger. A hit while
  clinging gives no knockback; only an air hit boosts. Re-solve on agent a's real states when posted.
* wall 16:50 **BIRD BOOST: LEGAL (on the TAS state).** The TAS's boost itself uses no banned input: A+Right jump off
  the post at 18,631, then Right only; the bird (type 11, slot 5) catches Ryu from BEHIND in the air at 18,658 (bird x
  199 y 138, Ryu x 208 y 131, hp 16 -> 13, invincible 60 f); knockback = +1 px/f TOWARD the wall and up 3,3,3,3,3,2,2,...
  px/f until Ryu touches the ladder (y 105 at 18,668-69). The L+R / 1-f presses are only in the TAS's climb AFTER the
  contact. Our legal line from `l42w_tas18596`: TAS rows' approach + Right through the knockback, R 18,669 (catch), then
  the 1.8 px/f ladder cycle -> **trigger 18,683 = TAS +3, hp 13** (`work/l42w/we_t596_h13.inputs.txt`, judge PASS,
  **NesHawk = Mesen frame for frame, trigger 18,683**, `work/l42w/nhwall.py`). No boost: 18,694 (TAS +14, hp 16);
  record ~18,706. So the boost saves 11 f for 3 HP. Now: mapping the bird window (pokes) and the post-contact climb.
* wall 17:45: **better legal climb after the boost: wall jump A+Left ON the contact frame (still in the knockback
  pose), Right x3, A+Left x2, Right -> trigger 18,682 = TAS +2** (`work/l42w/wb_t596d.inputs.txt`, judge PASS, NesHawk
  = Mesen, 18,682). Write-up: `knowledge/technique_4-2_bird_boost.md`. Bird map (522 poked bird positions): only hits
  from BEHIND with Ryu airborne at X 3,014-3,029 boost (trigger 18,681-18,693); front hits push Ryu away from the wall.
  **On agent a's rough states (18,930 / 18,963) the bird is AHEAD of Ryu and hits him from the front** (Right-only:
  hit at 18,943, knocked back); no boost there; no-boost best from 18,963 = 19,077 (hits by the type-13s). These states
  are +36 and the final line's bird phase will differ -> re-run `work/l42w/wenum.py <mst> <frame> --hist <h> ...`.
  Tool note for everyone: the prep beams' Leg.emit can force-hold a button while the other direction is chosen, i.e.
  emit Left+Right (it happened in my wbeam; fixed there by skipping L+R / U+D children) - judge every beam output.
  **Request to agent a:** the boost needs the homing bird (type 11) BEHIND Ryu (left of him, ~10-40 px, level or
  below) when he jumps off the post (X ~2,977-2,999). Its phase is set from far back (it swings around Ryu's screen x
  with ~1/16 px/f^2 bang-bang homing, period ~100-140 f). Please post NesHawk + Mesen states + history also at X
  ~2,700-2,800 on your final line (and note the bird's slot/x), so I can steer the bird with the approach.
* wall 19:55: **first full candidate `l42_w_k932a` = 4-3 control 19,299 (record -2.8), hp 15 / np 10 / J&S**, verified
  (finish + chain MATCH + judge), row in Candidates. It is b2_k3 to 18,932 + the no-boost wall (trigger 19,019 = TAS
  +23; the wall part itself = TAS +12 from X 2,950). **Why no boost on b2_k3:** the boost bird (slot 5, homing since
  ~18,300) is killed by b2_k3's Down+B at 18,720-21; left alive it swings around Ryu (period ~250 f, amplitude ~90 px)
  and hits him at 18,843 (X 2,816, from straight behind -> knocked BACK, hp -3). The trailing type 13 stays ~45 px
  behind and only jumps to y ~137, so it can't reach the post-jump apex without ~25 f of waiting (wpause search running).
  Now: beam from 18,700 that keeps the bird ALIVE without hits (bird = `$400+5` 11 and alive flag `$410+5` != 0), takes
  the +10 X 2,784, and reaches X 2,950 with the bird behind -> then the boost search.
* wall 22:10: **best candidate now `l42_w_k932b` = 4-3 control 19,297 (record -4.8, cum -204.8), hp 15 / np 10 / J&S**,
  verified (finish + chain MATCH 2ca737481fff + judge). Wall from X 2,950 = trigger 19,017 = TAS +21 (the wall part
  itself from 18,932 = 85 f; TAS-state floor without a boost was TAS +14 from TAS pace). **Bird boost on our chain:
  not reachable at a gain** (full search table + reasons in `knowledge/technique_4-2_bird_boost.md` "On our chain"):
  b2_k3 kills the bird at 18,720; kept alive (b2_k3 minus the kill, or agent a's `b18760`), it hits Ryu at
  18,738-41 / 18,839-43 or is in FRONT of Ryu at the post (18,945-58), and every hitless bird-alive line has to skip the
  +10 X 2,784; re-phasing its ~250-f swing costs 60-125 f. Waiting at the post 2-42 f (7,094 jumps) only meets the
  trailing type 13, which never boosts. Gains left at the wall: none found below 19,017 from k18932 (beam + 2 enumerations);
  earlier arrival at X 2,950 moves the trigger 1:1.

Best 3-3 so far: `logs/l33_p4t_poweron.inputs.txt` 4-1 control 14,866 (936 f, record +24.5, cum -140.4). Round 2 running: 2nd-sit kill with hits allowed (hp refills at act start).

### 3-2 (locked) section

**LOCKED START (2026-10-24): 3-2 control frame 11,595** from `logs/l31_alt_b2r_poweron.inputs.txt`, Ryu x 35 moving, hp 16, ninpo 12, Fire Wheel, `$BF` 61, `$62` 54 (make NesHawk/Mesen states at 11,595). Record 3-2 = 2,328 f -> target 3-3 control <= **13,923**. Tosser: arrival-independent here (no boost possible; no-axe line `work/l32p/noaxe_full179.txt`, ~TAS +32). Exit: Fire Wheel, ninpo 12 + lanterns so the 3-3 amount is 32 or 37 (residue 2 is already priced in), last 2 rows Right, no enemies alive at 3-3 control, compare by the 3-3 control frame + `$62` phase.

Candidates (3-2):

| time | agent | file | 3-3 control | frames | vs record | hp/ninpo/art | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 23:26 | first | `logs/l32_a_cC_poweron.inputs.txt` (13,930 rows; stage rows `logs/l32_a_cC.inputs.txt`, end state `states/l32_a_cC_end`) | **13,930** | 2,335 (TAS +28) | **+7.2** (cum -164.9) | 15 / **37** / Fire Wheel; x 51, `$73` 0x80, `$BF` 92, `$62` 7 (= cB) | yes (verify finish; `verify chain l32_a_cC_poweron` MATCH, RAM sha1 b0e3197f3151) | PASS | = cB with the ninpo variant 37: X-1504 slash dropped (rows 989-990 Right), X-2368 +10 taken (B on rows 1,589-1,590); same frames. Pick cB (32) or cC (37) by the 3-3 plan |
| 2026-10-24 23:19 | first | **`logs/l32_a_cB_poweron.inputs.txt`** (13,930 rows; stage rows `logs/l32_a_cB.inputs.txt`, end state `states/l32_a_cB_end`) | **13,930** | 2,335 (TAS +28) | **+7.2** (cum -164.9) | 15 / 32 / Fire Wheel (128); x 51 at control, `$73` 0x80 (= TAS), `$BF` 92, `$62` 7 | yes (verify finish; `verify chain l32_a_cB_poweron`: two replays MATCH, RAM sha1 0946bbcb4737) | PASS | cA without the pillar wheel: lag 187 kept through the pillar (Right-turn on the branch + air slash B on rows 1,303-1,304 kills the pillar-top type 3), np 12+10+5+5 = **32**; end beam `e5` (the end type-3: Ryu is 1 px behind the TAS there and its body touches him on the TAS line; the beam costs ~1 f) |
| 2026-10-24 22:20 | first | `logs/l32_a_cA_poweron.inputs.txt` (13,931 rows; stage rows `logs/l32_a_cA.inputs.txt`, end state `states/l32_a_cA_end`) | **13,931** | 2,336 (TAS +29) | **+8.2** (cum -163.9) | 15 / 37 / Fire Wheel (128); x 51 at control, `$73` 0x80 (= TAS), `$BF` 93, `$62` 6 | yes (verify finish; `verify chain l32_a_cA_poweron`: two replays MATCH, RAM sha1 5d54fe64939e) | PASS | legal TAS rows lag 160 -> tosser-1 BODY boost + beams (X 1252 at 12,438) -> TAS rows lag 187 (+5 X 1504 free) -> pillar via branch Right-turn (TAS +1, wheel thrown) -> lag 188 (+10 X 2368 free) -> end beam e3 (-2 f, end type-3 walker) |
| 2026-10-24 22:45 | second | `logs/l32_b_c4r_poweron.inputs.txt` (13,936 rows; stage rows `logs/l32_b_c4r.inputs.txt`, end state `states/l32_b_c4r_end`) | 13,936 | 2,341 (TAS +34) | +13.2 (cum -158.9) | **16 / 32 / Fire Wheel (128)**; x 51 moving at control, `$73` 0x80 (only Basaquer, = TAS), `$BF` 98, `$62` 60 (timer 149) | yes (verify finish; `verify chain l32_b_c4r_chain`: two replays MATCH, RAM sha1 53775bb7a277) | PASS | on first's HANDOVER v1 (X 1252 at 12,445, hp 16): legal TAS rows lag 194 (B kept: the TAS kills the X-1314 bird) -> pillar beam `f2` = **TAS +0** (X 1923 y 96 at 12,912 = TAS 12,718 + 194; FW thrown, vine -> branch -> top, no hit) -> TAS rows lag 194 + 2 repairs (B at 13,374 vs the bird at X ~2620 without touching the Windmill X 2624; free +10 X 2368 = B on 13,196) -> end beam `e1` (+1 f) -> Right to the play end (X 3035 at 13,655) + blanks + last 2 rows Right. 5 f behind cA only because of the handover (v1 vs first's 12,438 base) |

Agent notes (3-2):
* first 21:08: start states made from `logs/l31_alt_b2r_poweron.inputs.txt`: NesHawk `states/lock_32_ctl` (frame 11,595, x 35 y 192, hp 16, np 12, FW, `$BF` 61), its NesHawk trace `logs/l32_base.trace.csv`, Mesen `states/mesen/lock_32_ctl.mst` (`work/c5/mboot.py`; `$62` 54; slots 3-6 type 3, slot 7 type 0b). Working dir `work/l32a/`.
* first 21:12: **HANDOVER v1 at X 1252: frame 12,445 (stage row 850), hp 16, ninpo 22, Fire Wheel, `$BF` 143, `$62` 6, Ryu y 85 airborne (anim 5) after the jump over tosser 2; last 12 rows Right.** Rows (850 rows after 3-2 control): `work/l32a/n850.txt`; power-on history `work/l32a/h_h1252.inputs.txt` (12,445 rows, judge PASS); NesHawk state `states/l32a_h1252` (NesHawk replay identical: X 1252 at 12,445 hp 16), Mesen `states/mesen/l32a_h1252.mst`. = TAS + 34 at X 1252 (TAS 12,251 -> ours 12,411 at lag 160). How: **legalized TAS rows at lag 160 (our frame f = TAS frame f-160) stay in exact TAS sync with NO repairs from control to the pillar (X 965 at 12,215 = TAS 12,055, d 0; the +10 at X 441 taken, np 22)**; then the prep's no-axe rows `work/l32p/noaxe_full179.txt` unchanged from row 620 (tosser-1 spawn BF 170). I keep working on shaving the tosser section (floor ~TAS +32) and will post v2 if better.
* first 21:25: **HANDOVER v2 at X 1252: frame 12,439 (stage row 844) = 6 f better than v1, hp 15, ninpo 22, Fire Wheel, `$BF` 137, `$62` 12, Ryu y 93 airborne, last 2 rows B+Right (an air slash).** Rows `work/l32a/b844.txt` (844 rows after 3-2 control); power-on history `work/l32a/h_b1252.inputs.txt` (12,439 rows, judge PASS); NesHawk state `states/l32a_b1252` (NesHawk replay identical: hp 15 at 12,283, X 1252 at 12,439); Mesen: `python work/l32a/mkst.py work/l32a/b844.txt 844 b1252` -> `states/mesen/l32a_b1252.mst`. = TAS +28 at X 1252. **New trick: a BODY damage boost from walking tosser 1** (not an axe): jump at stage row 651 (`A+Right` x2), come down behind the tosser, its body hits Ryu at X 1067 y 170 (12,283, hp 16->15) and the knockback goes RIGHT (away from the enemy, 1 px/f, +29 px) onto the ladder at y 141 (vs y ~177 on the no-axe line); wall-jump left onto the branch (12,315), jump right to the top (X 1101 y 80 at 12,336, no-axe line 12,343), then a beam past tosser 2 with an air slash. Costs 1 HP (the TAS pays 1 HP here too). v1 (hp 16, 12,445) stays valid if HP matters later.
* first 21:35: **v2 extended to the pillar: legal TAS rows at lag 188 (our frame = TAS frame + 188) track the TAS EXACTLY from X 1252 to the pillar (d 0 every 20 f, NesHawk).** Rows `work/l32a/p1230.txt` (1,230 rows after 3-2 control = v2 rows 1-844 + legal TAS rows): frame 12,825, X 1831 y 103 (falling toward the pillar, = TAS 12,637), hp 15, np 22, FW, `$BF` 11, `$62` 28; NesHawk state `states/l32a_p1230`, power-on history `work/l32a/h_p1230.inputs.txt` (judge PASS). The TAS's FW throw is TAS 12,646 = our row 1,239 (in `work/l32a/c_l188.txt` it is replaced by Right). So the whole first part + the run to the pillar = **TAS +28** at the pillar. Compose more: `python work/l32a/comp.py work/l32a/b844.txt 844 <n> --lags 845:188 --out <f>`.
* first 21:38: **USE THIS ONE: `work/l32a/q1230.txt` = p1230 + a FREE +5 at X 1504 (air slash B on stage rows 990-991, collected at row 1,019, X 1515 y 113; still d 0 vs the TAS everywhere).** Frame 12,825, X 1831 y 103, hp 15, **np 27**, FW, `$BF` 11, `$62` 28 (same position as p1230). NesHawk state `states/l32a_q1230`, power-on history `work/l32a/h_q1230.inputs.txt` (judge PASS). Ninpo plan: 27 + the TAS's +5 at X 2192 = **32 at the exit (multiple of 5, >= 30) with no other lantern and no pillar wheel**; if the pillar needs the wheel (-5), add the +10 at X 2368 (32 again). second: your `l32b_p12820` base (v1 + 375 rows, X 1831 at ~12,831) is 6 f behind this; pillar rows found there should graft onto q1230 (both are in exact TAS sync at the pillar; lag 194 vs 188), re-check on q1230.
* first 21:58: **BEST BASE NOW: `work/l32a/r1229.txt` (1,229 rows) = frame 12,824 at X 1831 y 103 = TAS 12,637 at lag 187 (1 f better than q1230), hp 15, np 27 (+5 X 1504 free), FW, `$BF` 10, `$62` 29, and the enemies are IDENTICAL to the TAS's at 12,637 (type 3 X 1896 y 96, type 7 X 1743, type 20 X 1853 y 147; q1230's are 2-3 px off).** So TAS pillar rows from here behave exactly as in the TAS (our frame = TAS frame + 187). Tosser part: beam `w1` (score w2) from bo698 -> X 1252 at 12,438 (`work/l32a/w843.txt`, 843 rows), then legal TAS rows lag 187 + B on rows 989-990. NesHawk state `states/l32a_r1229` (NesHawk replay: X 1830 at 12,823, d 0 vs TAS every 30 f), Mesen `states/mesen/l32a_r1229.mst`, power-on history `work/l32a/h_r1229.inputs.txt` (12,824 rows, judge PASS). The TAS throws the FW at 12,646 = our 12,833 (row 1,238).
* first 21:57: **PILLAR SOLVED at TAS +1 on r1229, no beam (Mesen):** legal TAS rows, throw kept (Up+B rows 1,238-1,239), then **lag 188**; the TAS's 1-frame Right at TAS 12,681 (our row 1,274) -> Left; on the branch: row 1,277 = Right (one standing frame turns Ryu right), row 1,278 = A+Right (the legalizer moves A to 1,279), rows 1,279-1,312 = Right (instead of the TAS's L+R): Ryu jumps from the branch facing right and clears the pillar's left face: X 1923 y 96 at 12,907 = TAS 12,719 exactly, d 0 after. `python work/l32a/tmod.py work/l32a/r1229.txt 1229 2340 --lags 1230:187,1239:188 --keep 1238 --set "1274=Left,1277=Right,1278=A+Right,1279=Right,...,1312=Right" --out work/l32a/f1.txt`. From there legal TAS rows (lag 188) stay at d 0 to X 2941 (13,586, +5 X 2192 taken, np 27) where Ryu takes a 3-HP hit (end enemies differ) and falls: **the only open part is the end (X ~2940-3035) + exit requirements**. I'm on it now (beam from `work/l32a/f1960.txt`).
* first 22:20: **FULL CANDIDATE cA: 3-3 control 13,931 (2,336 f, TAS +29, record +8.2), hp 15, np 37, FW, x 51 at control (= TAS), `$73` 0x80 (only Basaquer, = TAS), `$BF` 93, `$62` 6** (verify finish OK; chain running). = r1229 + pillar (above) + legal TAS rows lag 188 + **free +10 at X 2368 (B on stage rows 1,590-1,591; np 27 -> 37)** + end beam `e3` from row 1,940 (the end type-3 walker is 6 px further right than the TAS's: the TAS's descent X ~2941-2960 lands on it, the beam jumps higher, **-2 f**: X 3035 at 13,650 = lag 190) + blanks + last 2 rows Right. Losses vs TAS: tosser wall +27 (lag 160 -> 187), pillar throw +1, end +2. Ninpo: 37 = 12 +10 (448) +5 (1504) -5 (pillar wheel) +5 (2192) +10 (2368); for 32 drop the X-1504 slash (rows 989-990). Rows `work/l32a/cA.txt`. Beam `e4` (from row 1,900, width 400, FW allowed) running for the 2 end frames.
* first 23:19: **cB = 13,930 (record +7.2), np 32, verified (chain MATCH, judge PASS): best so far.** e4 (lag-188 version, width 400) found nothing better than cA's end. Pillar without the wheel: TAS +0 in frames but Ryu ends 1 px behind the TAS (the standing Right-turn frame on the branch), which is exactly why the end type-3 still touches him (TAS clears it by 1 px). For 37 instead of 32 add the X-2368 slash (B on rows 1,589-1,590 in the lag-187 rows) and re-beam the end.
* first 00:16 (FINAL, stopping): **best = cB 13,930 (record +7.2; cC = same frames with np 37).** Floors found: (1) tosser wall: the body hit cannot come before 12,283 (Ryu's feet must reach the tosser box top y 168 behind it; the landing-frame jump at row 651 is the only one that does it) and the knockback state always lasts ~21 f, then wall-jump -> branch (11 f) -> top (21 f): TAS +27 is the floor without an axe (first axe +85 f); collision map: the tosser wall is a solid/ladder column X 1088-1103 from y 96 to 192 with a pit behind it, so there is no way around the top. (2) pillar: the branch landing is fixed at wall touch + 10 f and the Right-turn frame leaves Ryu 1 px behind the TAS (8 drift/turn variants, a TAS-distance beam: nothing better). (3) end: with that 1 px the TAS line touches the end type-3; beams e5/e6 (width 300/600, Left allowed) cost 1 f (X 3035 at 13,649). Wider ideas checked and rejected: tosser-1 respawn at `$BF` ~0 for an instant axe (comes after our branch time), tosser-2 hits (knock Ryu left), pillar without killing the pillar-top type 3 (hit). The record's 7-f pillar bird boost is the only known source of the remaining gap (second's notes). `$62` = 7 at 3-3 control: tune with the 3-3 kill row later. Details + resume: legal_a34_notes.md "3-2 lock round (first)".
* second 22:45 (pillar study, `work/l32b/`): **the record's pillar line is a BIRD damage boost** (video 14,494-14,556: a type-11 bird
  hits Ryu from the LEFT at the top of his jump off the X-1760 platform, ~X 1824, his life bar 13 -> 10; knock-back 1 px/f right + up,
  he lands on the branch ~X 1864 at video 14,544 and jumps to the top). It is **not reproducible from X 1252**: the record carries an
  older bird from far back (two big birds on screen at Ryu X ~1430, video 14,240; the X-1314 bird is the second). With our X-1314
  bird (exact model `work/l32b/bmodel.py`, checked frame-by-frame vs Mesen with `$84` bit 1 poked: speed +-1/16 px/f^2 toward
  Ryu's screen x, frozen on the 16-px scroll frames, freed at screen x < 8 / >= 248) a pure run frees it at its first left turn
  (screen x 10 -> <8, ~Ryu X 1455), keeping it costs >= 8 f of stops, and its left-to-right pass at Ryu X 1800-1830 costs
  **>= 35 f** of stops (`bsearch2.py` grid); the X-1557 bird spawns at screen x 16 and dies unless Ryu stands ~10+ f. So: kill
  it like the TAS. Without a boost the legal pillar = **TAS +0** (beam `pbeam.py` with spatial-cell diversity: grab the vine
  ~y 144, `A+Left` wall jump, `A+B+Left+Up` cling, land on the branch's right end X 1882 y 128, `A`, Right to the top; the
  FW throw `B+Right+Up` on the fall kills nothing that matters but is free). The pure-run loss of the TAS at the pillar is
  ~21 f, the record's ~14 f; the stage is pure running elsewhere after X 1252, so the second half has nothing more to give
  without the record's bird.
* second 23:55: **pillar on first's r1229 base: X 1923 y 96 at 12,906 (first's line: 12,907)**, i.e. TAS +0 / 1 px ahead of
  lag 188: `work/l32b/pb_f3.inputs.txt` (82 rows from frame 12,825 = after r1229's 1,229 rows; Mesen beam `f3`, np 27 -> 22
  with the throw, hp 15). After it, legal TAS rows at **lag 188** (not 187: the line is 1 px ahead of 188, 1 px behind 187,
  and 187 misses the TAS jump at 12,958) track to X 2881 at 13,545 with the +10 X 2368 (B 13,190-13,191) and the bird slash
  at X ~2620 (B 13,368-13,369; B earlier than 13,367 breaks the Windmill X 2624 -> item 130): rows `work/l32b/g3_rows.txt`.
  Only the end (X 2941-3035) is open; ideal X 3035 at 13,647-13,648 -> 3-3 control 13,928-13,929.

### 3-2 plan (l32p)

Tools and logs: `work/l32p/` (`tas32.py` NesHawk TAS RAM dump `tas32_ram.bin`; `an.py`/`det.py`/`events.py` readers;
`bfscan.py`, `noaxe_scan.py`, `noaxe_scan2.py` (+ `.out`) BF scans; `zbeam.py` = tbeam + scores `h`/`h2`/`hb`, goal
`br:X1:X2:Y`, `--pokebf`; `mkst.py`, `show.py`, `amap.py`; `nh_check.py` NesHawk check). Mesen 3-2 control state of c1b:
`states/mesen/l32p_ctl.mst` (frame 11,604, x 32, `$BF` 70, `$62` 45). Mesen TAS states `states/mesen/l32p_tas12030.mst`,
`l32p_tas12054.mst` (in exact sync with the TAS trace).

### The tosser gate (measured)

* 3-2's only `$BF`-dependent enemies are the two **axe throwers (type 2, "tossers")**; in bank07 only the thrower, its
  axe, Basaquer, Kelbeross and the final boss read `$BF` (`nmi_count`), so poking `$BF` is a clean experiment.
* Mechanics (`thrower` $C33C): on spawn (and after every throw + 12-frame hold) its delay = **`$BF >> 1`** frames, during
  which it walks toward Ryu at 0.5 px/f (contact = damage); then it throws an axe (x speed `$BF & 1`, fractions `$BF`).
* **Tosser 1** spawns at the foot of the vine wall (X 1077, ground y 192) when Ryu reaches X 965 on the pillar (TAS
  frame 12,055 = 3-2 control + 621). Geometry (collision dump): pillar top y 128 to X ~976, ground y 192 X 960-1087,
  **ladder (vine) X 1088-1103, y 112-176**, **branch X 1056-1087 y 128**, wall top y 96 from X 1088. Tosser 2 stands on
  the wall top (X ~1171 y 96), spawns at Ryu X ~1059.
* **TAS:** `$BF` 9 at tosser-1 spawn -> throws at spawn+4 and spawn+36; Ryu jumps at X 1041 (12,106), the 2nd axe hits him
  at 12,114 (hp 16 -> 15) and the boost carries him at full speed onto the wall top (X 1098 y 80 at 12,148). With the TAS's
  rows only spawn-BF **6 and 9** give that boost (`bfscan_w0.out`).
* **The record does the same boost and pays ~17 f for it**: his scroll trace (`work/a34r2/rec/r32.txt`) stalls at scroll
  796-822 (Ryu X ~930-950, on the pillar just before the spawn point) and is at full speed through the wall section after.
  He waits on the pillar for a good tosser.
* **Our arrival:** spawn BF `b` = (3-2 control frame F - 11,534 + 621 + d) mod 256, d = our lateness at X 965 vs the TAS
  pace from control (d ~ 0 when Ryu starts at x 35 moving, as `l31_alt_b2r` does; ~1-2 from x 32 standing).
  For every candidate b lands at 165-190: **the first axe comes 82-95 f after the spawn, when Ryu is already on the
  ladder: no boost is possible, and the tosser only walks at him.**
* **No-axe line** (`work/l32p/noaxe_full179.txt`, 231 rows from TAS frame 12,054 on the pillar): jump over the walking
  tosser 1, land on the ladder at y ~177 (12,133), legal ladder climb to y ~130, jump off LEFT onto the branch (X 1079,
  12,162), jump right onto the wall top (X 1100 y 80, 12,182 = TAS +34), run, jump over tosser 2 -> X 1252 at 12,285
  (TAS 12,251) = **TAS +34, hp 16** (the TAS pays 1 HP). The ladder top is at y 116: you cannot climb onto the wall from
  the ladder, the branch step is required. A pillar->branch jump is impossible (the y-128 jump lands at X ~1031).
  NesHawk check (`nh_check.py`, spawn BF 165/172/179/185): identical, X 1252 at 12,285, hp 16.
* **The same rows work unchanged for every spawn BF 163-190** (`noaxe_scan2.out`); from 191 up, tosser 2 (BF ~ b+64,
  wraps) stands and throws on the wall top and the jump over it must be retimed: b 191 and b 195 re-beamed (TAS-tracking
  beam, lag 33-34) = 12,283 (2 f better than the fixed rows, so the no-axe floor is ~TAS +32; `zb_l2u_b191`, `zb_l2t_b195`).

| 3-2 control F | `$BF` at control | spawn BF b (d = 0) | first axe after spawn | cost of the tosser section (to X 1252) |
|---|---|---|---|---|
| 11,590 | 56 | 165 | +82 | TAS +32..+34, hp 16 (no-axe line) |
| 11,593 | 59 | 168 | +84 | same |
| 11,595 (`l31_alt_b2r`, x 35 moving) | 61 | 170 | +85 | same |
| 11,596 | 62 | 171 | +85 | same |
| 11,600 | 66 | 175 | +87 | same |
| 11,604 (`l31_tas_c1b`, x 32) | 70 | 179 (+d ~1-2) | +89 | same |
| 11,610 | 76 | 185 | +92 | same |
| F + d >= 11,616 | | >= 191 | tosser 2 wraps | same cost after a retimed jump over tosser 2 (b 191 / 195: 12,283) |
| F + d = 11,687 / 11,690 | | 6 / 9 | +4 / +36 (TAS) | TAS boost, ~0 (but 83-86 f later: never worth it) |

**Conclusion: the 3-2 tossers do not care which 3-1 candidate is used (all 11,590-11,610 arrivals cost the same, ~TAS +33),
and a deliberate wait never pays (the next good tosser is ~80 f away; the record's 17-f wait was for his own `$BF`).
Choose 3-1 by its control frame + 3-3 tally residue only.** vs the record this spot is ~+16 (he loses 17 there).

### Record, TAS, banned inputs

* Record 3-2 = 38.73 s = **2,328 f** (TAS 2,307 = control 11,434 -> 3-3 control 13,741; play end X ~3,035 at ~13,460,
  control = play end + 281). Target: 3-3 control <= 3-2 control + 2,328 (11,595 -> **13,923**; 11,604 -> 13,932).
* Pure-run floor: X 33-35 -> 3,035 at 1.5 px/f = ~2,000 f, so 3-3 control >= 3-2 control + ~2,282. The TAS is pure run +
  ~25 (boost 0, throw 1, pillar ~24); the record pure run + ~46 (tosser wait 17, rest small, pillar 7 f FASTER than the TAS).
* TAS rule breaks (legal_a34_notes): **L+R 32 frames 12,685-12,717 (the pillar)**, 50 one-frame holds, 4 short releases.
  Legal TAS rows on our state diverge at row 160 (a hit at X 273: other enemy positions), so a beam is needed from the start.
* Old lines: `logs/tk_3-2_c1` (chain, other `$BF`) = record +272 (losses +97 X 1024-1152, +57 X 1152-1280 = the tosser
  wall, +64 at the pillar); a34 round 1 from the TAS state `3-2_tas3` = TAS +43 (with the good TAS tosser), pillar goal beam +10.
* Path (TAS trace, X at 1.5 px/f except where noted): +10 lantern X 448 (11,706); type-5 shooter X ~660 y 96; tosser wall
  X 965-1252 (above); pillar X ~1830-1950 (12,635-12,735: FW thrown at 12,646 from X 1843, then wall jumps + L+R to the top);
  +5 X 2192 (12,894); end X ~3,035.

### Expected losses vs the TAS

| spot | TAS | ours (expected) | note |
|---|---|---|---|
| start | x 35 moving | 0 with the pre-control Right (b2r); ~1-2 f from x 32 standing (c1b) | |
| X 0-965 | pure run | 0-10 | enemies differ (hit at X 273 on legal TAS rows); repair with B timing / beam |
| tosser wall X 965-1252 | boost (-1 HP) | **+32..+34** | no-axe line above; floor ~+30 (ladder 1.8 px/f + branch step) |
| pillar X ~1830-1950 | L+R + FW throw | +0..+10 (a34 goal beam +10; the record is 7 f faster than the TAS) | same structure as the tosser wall: vine/ladder on the pillar's left face + a branch (map `resources/maps/3-2.png` X ~1857-1888); study the record (`work/a34r2/rec/s32pillar.png`: he goes high, maybe a bird/enemy boost) |
| rest | pure run | 0-5 | Windmill traps below |
| **total** | 2,307 | **~2,345-2,360 = record +17..+32** | cum stays ~ -140..-155 |

### Lanterns and the ninpo budget (exit **Fire Wheel + 25 min / 30-35, multiple of 5**)

`python -m ng.solve.items 3-2` (use the system Python; the venv has no PIL): +5 X 352 y 128, **+10 X 448 y 96 (TAS)**,
500 X 704, **Windmill X 1008 y 96 (TRAP: right above the pillar-to-ground fall of the tosser section; no air B near
X 1008)**, +10 X 1152 y 160 (below the wall-top line: ~18 f), 1000 X 1392, +5 X 1504 y 96, FW X 1680 y 144 (backup only),
500 X 1824, 1000 X 2080, **+5 X 2192 y 96 (TAS)**, +10 X 2368 y 128, 500 X 2496, **Windmill X 2624 y 112 (TRAP, on the TAS
line at y ~141: never break it)**, +10 X 2832 y 96 (~8 f).
* From c1b (FW/15): +10 X 448 + +5 X 2192 = **30** (+10 X 2368 = 40 if the pillar wheel is thrown = 35).
* From b2r (FW/12): same pickups give 27 / 37 / 32: residue 2 stays (no Star in Act III any more): +6 f at the tally,
  already counted in b2r's "effective 11,601".
* The TAS's pillar wheel (-5) is only worth it if the legal pillar line needs it (it kills the enemy on the pillar).

### 3-2 exit requirements (beyond ninpo/art)

1. **Pre-control Right:** the last 2 rows before 3-3 control = Right (Ryu x ~51, speed 1.5 at control as in the TAS).
   c5 found the 3-3 graft fails with x 48 standing (`legal_a34_notes` round 5).
2. **No leftover enemies:** c5: leftover slots 0-2 from 3-2 (type $11) moved Basaquer's falling-rock ($1A) spawn from
   his first landing to his second. Compare `$400-$407` / `$73` at 3-3 control with the TAS's; kill or outrun the end
   enemies (type 3 / 9 at X ~2960-2975).
3. **`$BF` at 3-3 control matters a little:** `basaquer_turn` ($CEE3) fires 3 shots at the end of each sit only if he is
   the only enemy (`$72` = 1) AND `$BF` bit 7 is set on that frame. Turns at 3-3 rows ~76 and ~152, so shots come when
   (3-3 control `$BF` + 76) and (+152) are >= 128 mod 256. 3-3 control 13,923-13,932 gives `$BF` 85-94 -> shots at both
   turns (`$BF` ~161-170 / ~237-246). Avoiding both needs control `$BF` 180-231 (~90 f away): not worth it; the 3-3 search
   must simply dodge the volleys (the GA's row-82 hit is the boss body, not a shot).
4. **`$62` phase:** each 3-2 frame moves `$62` at 3-3 control by 1; once 3-3's kill row is known, a 1-2 f choice in 3-2
   can catch one more timer second (-3 f at the tally). `$62` is frozen during the 281-f transition.
5. HP: no refill before 3-3; the no-axe tosser line keeps 16.
6. Optional: a Fire Wheel thrown just before the 3-2 end persists into 3-3 (game_mechanics: "used at 3-3"); test it on the
   real 3-3 start (costs 5 ninpo and ~1-2 f, may give free hits).

### Candidates (3-3)

3-3 split = 4-1 control - 3-3 control (record 911.5, TAS 828). On cB/cC (3-3 control 13,930) the record pace is 4-1
control <= **14,841.5**, TAS pace 14,758. 4-1 control = 13,930 + kill row + 3 x (timer + ninpo at the kill) + 301
(measured, Mesen M + 301 = NesHawk). Details, mechanics and the re-apply recipe: `legal_a34_notes.md` "3-3 lock round".

| time | agent | file | 4-1 control | frames | vs record | vs TAS | kill row / timer / np left | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-25 05:25 | l33 (round 2) | **`logs/l33_q4_poweron.inputs.txt`** (on cB; stage rows `logs/l33_q4.inputs.txt`, end state `states/l33_q4_end`) | **14,848** | 918 | **+6.5** (cum -158.4) | +90 | 170 / 147 / 2 | yes (verify finish; `verify chain l33_q4_poweron`: two replays MATCH, RAM sha1 08c24f6f39c2) | PASS | p4t rows 1-89, then Ryu lets the two crawling volley shots pass at x ~87, follows them right, keeps the 6th wheel for the boss's 3rd rise and kills on row 170 (no knockback after row 95; hp 11 at the kill, refilled at 4-1). The 2nd sit itself is immune to wheels AND slashes, so no "2nd-sit kill" exists |
| 2026-10-25 03:30 | l33 | `logs/l33_p4t_poweron.inputs.txt` (on cB; stage rows `logs/l33_p4t.inputs.txt`, end state `states/l33_p4t_end`) | **14,866** | 936 | **+24.5** (cum -140.4) | +108 | 191 / 146 / 2 | yes (verify finish; `verify chain l33_p4t_poweron`: two replays MATCH, RAM sha1 18e6d0df5c57) | PASS | = p4 with the last wheel thrown 1 row EARLIER (Up+B rows 170-171): it lands 1 row LATER (row 191 = the timer tick), so the tally sees 146 instead of 147: -2 f (`work/l33/tail.py`) |
| 2026-10-25 02:00 | l33 | `logs/l33_p4_poweron.inputs.txt` (on cB; stage rows `logs/l33_p4.inputs.txt`, end state `states/l33_p4_end`) | 14,868 | 938 | +26.5 (cum -138.4) | +110 | 190 / 147 / 2 | yes (verify finish; `verify chain l33_p4_poweron`: two replays MATCH, RAM sha1 fb7c09458c74) | PASS | 6 wheels: 3 on his first descent (16 -> 9 by row 53), 1 ground wheel at the sitting boss (3 hits when he rises, row 77), 2 on his 2nd descent; last 1 HP with the 6th wheel thrown at row 171 on his 3rd jump (hit row 190). Kill in the 3rd jump like the record (his ~166) |
| 2026-10-25 01:45 | l33 | `logs/l33_f1.inputs.txt` (on cB) | 14,873 | 943 | +31.5 | +115 | 198 / 146 / 2 | yes (verify finish) | PASS | first kill found (fallback) |

Agent notes (3-3):
* l33 05:55 (round 2, FINAL): **best = q4, 4-1 control 14,848 (record +6.5, TAS +90), 18 f better than p4t.** Kill row
  170 sits far from the timer ticks (130 / 191), so the tally does not care about a 3-2 change of a few frames, and the
  fight is the same for any control `$BF` 52-103: q4's rows can be replayed unchanged if 3-2 ever changes. Ninpo residue 2
  (+6 f) is fixed by cB (32 = 6 wheels + 2). The boss's 2nd sit is immune to wheels AND slashes (measured), so no
  "2nd-sit kill" exists; the first-pass kill was not found. Beam variants q5 and a 12-min GA on q4's tail
  found nothing better than row 170.
* l33 03:35: **32 vs 37: take cB (32).** Measured: p4t's rows on cC kill on the same row with 7 ninpo left (M +15 f =
  4-1 control 14,881), and a 7th wheel added anywhere in rows 150-190 never throws or never helps (one wheel at a time,
  his sits are almost wheel-proof). **Arrival dependence:** the boss path is fixed from control and `$BF` only gates his
  volleys (bit 7 at the end of each sit: control `$BF` 92 -> shots at rows 76 and 153; any 3-2 arrival with control
  `$BF` 52-103 gives the same fight), so p4t's rows replay unchanged on a faster 3-2. What moves is the timer phase:
  `$62` = 7 at control -> ticks at rows 8, 69, 130, **191** (row = `$62` + 1 + 61k), and p4t kills exactly ON the 191
  tick. **If 3-2 gets d frames faster, `$62` = 7 + d and the tick moves to row 191 + d: p4t then tallies one more unit
  (+3 f), so the net gain is d - 3 unless the last wheel is re-timed so the hit lands on row 191 + d (`work/l33/tail.py`
  shifts the jump/last wheel and reports M in ~1 min; p4 = the same line hitting 1 row earlier). If 3-2 is 1-2 f
  slower nothing changes but the arrival.** So a 3-2 gain of 1-2 f is only worth it with a re-timed 3-3 tail (check with
  tail.py); a gain of 3+ f is always worth it.
  The first-pass kill (TAS row 84) was not found legally: the sitting boss is nearly immune to wheels (a wheel at the
  sitting boss lands <= 1 hit; hits come when he rises), air slashes on the sit need Ryu low (y >= ~184), and his volley
  at row 76 + his rise at rows 77-90 hit Ryu (40 rows of knockback). The 2nd sit (rows 133-152, ~45 f better) was also
  missed: two volley shots crawl right at 2 px/f and catch a running Ryu at ~row 127 (see legal_a34_notes).

### Candidates (4-1)

On q4 (4-1 control 14,848, `$BF` 240). Record pace: 4-2 control <= **17,039**. Details + resume: legal_a34_notes.md "4-1 lock round".

| time | agent | file | 4-2 control | frames | vs record | hp/ninpo/art at exit | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-25 14:40 | r15 | **`logs/l41_r15_c_poweron.inputs.txt`** (16,998 rows = q4 rows 1-14,847 + `logs/l41_r15_c16844.inputs.txt`, first row = control-row Right; end state `states/l41_r15_c16844_end`) | **16,998** | **2,150** | **-41.6** | 16 / 0 / J&S (133) at 4-2 control; hp 14 at the stage end; `$BF` 81 | yes (verify finish; `verify chain l41_r15_c_chain`: two replays MATCH, RAM sha1 76035d5f3074) | PASS | = r15 a with the room-15 ladder cycle started on the appear frame: A+Left+Up on **16,422** (rows 16,402-16,421 are frozen transition rows, A presses moved to 16,407/12/17) and a **6-frame first cycle** (R+U on 16,425-27, next A 16,428) so the NesHawk misread at 16,429 lands on a harmless edge; departure A+Left 16,473-74 (y ~148), Down+B 16,476-77 kills the bird, branch, jump 16,485, X 140 at 16,504; top beam `topC` pure pace, stage end freeze 16,835, Start 16,844-45 (16,843 gives the same control) |
| 2026-10-25 12:54 | r15 | **`logs/l41_r15_a_poweron.inputs.txt`** (17,000 rows = q4 rows 1-14,847 + `logs/l41_r15_a.inputs.txt`, first row = control-row Right; end state `states/l41_r15_a_end`) | **17,000** | **2,152** | **-39.6** | 16 / 0 / J&S (133) at 4-2 control; hp 14 at the stage end; `$BF` 83 at 4-2 control | yes (verify finish; `verify chain l41_r15_a_chain`: two replays MATCH, RAM sha1 50ab6cb39513) | PASS | = c3b to 16,466 (room 15 ladder cycle), then: cycle on to y 143 (16,475), wall jump A+Left 16,476, **Down+B 16,478-79 kills the bird with the regular sword (np 5 kept)**, branch 16,486, jump 16,487, top X 163 y 96 at 16,521 (c3b X 161 at 16,532); top run beam `topA` = **pure 1.5 px/f** (spin B 16,645 kills the respawned bird + the walker), stage end X 637 at 16,837 (c3b 16,856), Start 16,846-47 (end + 9, NesHawk earliest) |
| 2026-10-25 (resume) | l41 | **`logs/l41_c3b_poweron.inputs.txt`** (17,020 rows = q4 rows 1-14,847 + `logs/l41_c3b.inputs.txt`, whose first row is the control-row Right; end state `states/l41_c3b_end`) | **17,020** | **2,172** | **-19.6** | 16 / 0 / J&S (133) at 4-2 control; `$BF` 103 at 4-2 control (verify read) | yes (verify finish; `verify chain l41_c3b_chain`: two replays MATCH, RAM sha1 ba7fe3e2afd4) | PASS | = c2a cut at the stage end (X 636 at 16,856) + **Start on 16,865-66** (the 4-1 -> 4-2 cutscene skip; NesHawk's earliest, Mesen's is 16,864). c2a's +48 was NOT the ladder misreads (NesHawk = Mesen through the whole line) but the missing Start: verify's to_control pressed it late |
| 2026-10-25 06:05 | l41 | `logs/l41_c2a_poweron.inputs.txt` | 17,056 | 2,208 | +16.4 (superseded by c3b) | 16 / 0 / J&S | yes (verify finish) | PASS | same play rows as c3b, no Start skip |
| (p4t base, superseded) | l41 | `logs/l41_b0.inputs.txt` (stage rows from 14,865 on p4t) | 17,051 on p4t | 2,185 | -6.6 on p4t only | 16 / 0 / J&S | yes on p4t | PASS | r2c_fix + one NesHawk-conflict-dependent repair (A+Left 16,477-78); fails on q4 (room-15 climb breaks) |

Agent notes (4-1):
* l41 (resume): **c3b verified, 4-2 control 17,020 (record -19.6).** NesHawk = Mesen frame-for-frame through c3b (no harmful
  misreads). NesHawk-matched intermediate states on c3b (q4 axis; Mesen = `states/mesen/l41_q<f>.mst`, power-on history
  `work/l41/hq_<f>.inputs.txt`, rows = `work/l41/c3b.txt` = stage rows after the control row):
  * block exit 16,030: X 1,785 y 128, hp 15, np 10 (Mesen `l41_q16030.mst`; NesHawk `l41q_c3_16150` at 16,150);
  * room 14 entry 16,292 (TAS 16,009 + 4): NesHawk `l41q_r14`, Mesen `l41_q16292.mst`, hp 14, np 5;
  * room 15 entry 16,400 (TAS 16,107 + 14): NesHawk `l41q_r15`, Mesen `l41_q16400.mst`; Ryu appears at 16,422 (y 232);
  * room 15 at 16,468 (ladder cycle, X 122 y 157, start of the local beam): NesHawk `l41q_r15b`, Mesen `l41_q16468.mst`.
  * c3b's room 15: ladder cycle to 16,468, beam r15b (air B = J&S spin kills the bird, np 5 -> 0), top y 96 at X 161
    16,532, then beams top1/top2 (run loses ~7 f to enemies without ninpo), stage end X 636 at 16,856, Start 16,865.
  * **Split with the second agent:** I'll work on room 13 (block / TAS-graft section) and the room 14 ladder entry; room 15
    (bird boost, keep-5-ninpo top spin) is yours, start from `l41q_r15` / `l41_q16400.mst`. If I improve the room-15 entry
    I'll post the new entry state here.
* r15 12:55: **`l41_r15_a` = 4-2 control 17,000 (record -39.6), verified (finish + chain MATCH + judge PASS).** Room 15
  from c3b's entry (NesHawk = Mesen frame-for-frame on my rows, checked 16,400-16,600 from `l41q_r15`). Findings:
  * Geometry (`work/l41/dmap.py` on the TAS dump): ladder column X 128-143 from y 112 down, solid block X 128-143 y 96-111
    on top of it, branch (one-way) X 96-127 y 128, top (one-way) X 144-239 y 96. Ryu must be at feet y <= 96 when he
    crosses X ~124-128, so from the left side only a standing jump from the branch gets over (wall jumps rise 15 px; the
    ladder cycle tops out at y 99 at 16,500, blocked at X 122). One-way platforms snap Ryu up when his apex has the feet
    inside the tile (the wall jump from y 143-146 snaps onto the branch at y 128).
  * The ladder cycle is already at the max legal rate in room 15 (A on 16,425 is the first legal A after the
    transition); it reaches y 143 at 16,475, exactly the lowest wall-jump start that snaps onto the branch.
  * **Bird (type 11)**: spawns at X 16 y 80 when Ryu appears (16,424), homes on Ryu's x (+-1/16 px/f^2) and passes
    him at 16,478-16,481 (y ~134). Hits on the ladder give NO knockback (hp only). **A bird BOOST does not help a legal
    line:** hit in the air left of the column, the knockback (1 px/f right, 3 px/f up) is cut when Ryu touches the
    column (he clings at y 122 / y 114), and its full 29 px rise from y >= 134 never reaches y 96; the TAS's boost
    works only because its L+R zip put Ryu RIGHT of the column under the one-way top. **Kill it instead: Down+B (air
    regular sword, 0 ninpo) on 16,478-79 right after the wall jump** -> branch 16,486 with hp 14, np 5. Killing it
    respawns a new bird at X 16 (16,489) that catches Ryu from behind at ~X 250 (16,581): topA's J&S spin at 16,645
    kills it and the y-160 walker. Variants (`work/r15/g1.py` 2,784 departures, `g2.py` jump timing, `g3.py` direct
    A+Left at 16,475): best = jump 16,487, X >= 140 at 16,506 (c3b 16,518); landing further left/right trades 1:1
    with the block at X 124. Left alive, the bird costs >= 3 f (cling at y 122, drop, jump).
  * Top run: from the landing X 163 at 16,521 the beam `work/r15/beam.py` (copy of l41's, alphabet Right / A+Right /
    B+Right / A+B+Right / Down+B+Right / -) holds exact pure pace (X = 163 + 1.5 (f - 16,521)) to the end: X 637 at
    16,837. So with this room-15 line, **4-2 control = room-15 entry + 600** (entry 16,400 -> 17,000).
  * **Graft for c2:** `work/r15/r15a_after16400.txt` = my stage rows for frames 16,401-16,847 (room 15 entry 16,400 ->
    Start). Nothing in room 15 reads `$BF`, the bird spawns at the room appear and homes on Ryu's x, so these rows
    should replay unchanged after any earlier room-15 entry E (rows E+1..), as long as the room-14 cycle phase keeps the
    A presses legal (last A before entry = c3b's 16,395-96 / 16,400-01 phase). Re-check on NesHawk.
  * Tools: `work/r15/rlib.py` (Mesen helpers), `show.py` (per-frame trace), `nhtrace.py` (NesHawk trace from a state),
    `g1.py`/`g2.py`/`g3.py` (grids), `beam.py`; logs `work/r15/*.log`, `*.out`.
* r15 14:40: **`l41_r15_c` = 4-2 control 16,998 (record -41.6), verified (finish + chain MATCH 76035d5f3074 + judge
  PASS); best so far.** Rows 16,401-16,421 (room 14 -> 15 transition, Ryu frozen) are free apart from legality, so the
  room-15 ladder cycle can start on the appear frame 16,422 instead of 16,425 (`work/r15/g4.py`: phase 16,422 = X 140
  at 16,503, -3 f; phases 16,421/23/24/26 never land on the branch). **NesHawk misread at 16,429** (keeps the previous
  pad; also 16,418, harmless) breaks every 5-f phase that changes rows on 16,429; a 6-f first cycle (`g5.py`, variant
  (0,1)) puts 16,429 on the A+L+U -> A+L edge (read late = harmless) and keeps -2 f: X 140 at 16,504, NesHawk = Mesen to
  16,540 (`work/r15/nhcmp.py <rows> <to>` compares from `l41q_r15`). Room-15 graft rows: `work/r15/r15c_after16400.txt`
  (frames 16,401-16,845), i.e. **4-2 control = room-15 entry + 598**; the transition-row trick assumes c2's room-14
  rows keep A on 16,400-01. Re-check misreads with nhcmp.py after any graft.

## Next: 4-1 plan (prep agent l41p, 2026-10-25)

Tools, logs and dumps: `work/l41p/` (`tas41.py` + `tas41_ram.bin` = NesHawk TAS 4-1 RAM per frame; `rundump.py` = NesHawk
dump of any rows file from a ref4751 state with an optional `$BF` poke; `det.py` / `events.py` / `lagcmp.py` readers;
`bfscan2.py`, `fullchk.py`, `bslash.py`, `fullfix.py` = the `$BF` arrival scans; `pretest.py`; `blk2.py`, `blk_dbg.py`,
`c15726.py`, `bexit.py` = the 15,700-block tests). Mesen TAS states (= NesHawk trace): `states/mesen/l41p_tas14569.mst`
(4-1 control, `$BF` 217, `$62` 53), `l41p_tas14560.mst`. **Mesen replays NesHawk rows exactly only with NesHawk's
effective pads (`$2A` from a NesHawk dump)**; with the rows file it splits at 15,740 (input conflict, see the trap below).

### Splits, and where the record loses to the TAS

* **Record 4-1 = 36.47 s = 2,191.6 f** (control video 16,513 -> 4-2 control 18,701; record_events cum NES 14,830.4 ->
  17,022.0). **TAS 4-1 = 2,113 f** (control 14,569, `$BF` 217 -> 4-2 control 16,682; play ends 16,530 = 4-1 load + the
  152-f transition). Record - TAS = **+78.6**.
* Target: 4-2 control <= 4-1 control + 2,191. Our 4-1 control ~14,750-14,840 (3-2 at 13,930 + 3-3).
* Per room (record: scroll trace `work/a34r2/rec/r41.json` vs `tas41_ram.bin`; legal: `logs/a34/4-1_r2c` NesHawk dump
  `work/l41p/r2c_ram.bin`, `lagcmp.py`):

| room | TAS (frames) | record - TAS | why the record loses | legal r2c - TAS |
|---|---|---|---|---|
| 13 (4-1a, X 33 -> 2,171, right) | 1,440 (control -> room 14) | **+13**: +3 at the start (inside the +-3 of the control estimate), +4-5 at the tosser X 723-788 (he waits on the ground for its axes, then jump-kills it on its pillar, video 16,998-17,034), +2 over the 15,700 block, ~+2 elsewhere | the tosser (his `$BF`) | **+11, all at the 15,700 block** (type-8 bird hit) |
| 14 (shaft) | 98 | **+30** | TAS climbs 2 px/f with L+R and A every 2 f (16,038-16,106); legal C8 = 1.54 px/f | +28 (C8) |
| 15 (4-1c: wall, then the top run to X 636) | 423 + 152 | **+41** then 0 along the top | TAS: L+R wall zip 16,132-16,199 + bird damage boost onto the top (16,199, hp 15 -> 12). Record: single-wall climb, branch, bird boost | +33 (A*: C9, C8 x4, jump-off onto the branch, jump onto the top; a 3-HP bird hit at 16,226 on the way, no boost) |
| **total** | **2,113** | **+79** | | **+72 = record -6.6** (4-2 control 16,754 from the TAS state) |

### TAS rule breaks in 4-1 (from the TAS rows, legal_a34_notes table: 59 L+R, 0 U+D, 68 period, 101 hold)

* L+R: **15,814** (one frame, Left+Right+A = a jump; Right+A should do), **16,086-16,106** (shaft: Left+A / Left+Right
  alternating every frame), **16,132-16,199** (room-15 wall zip; ends with the bird boost).
* Fast taps: 15,059 jump (A 1 f; legal 2 f is the same), the 15,705 chimney climb (Left+A every 4 f: **no legal climb
  there**, 288 patterns, round 1), the shaft (A every 2 f).
* The record's line avoids all three: high route over the 15,700 block, C8 shaft, C8 wall + branch + bird boost.

### Legal reference line `logs/a34/4-1_r2c` (2,034 rows from `ref4751/08_4-1_control`, PASS)

Rows 1-971 = legalized TAS rows in exact TAS sync to 15,540 (+10 X 272 at 14,729, +5 X 464 at 14,864, tosser killed by a
landing slash at 15,077, J&S X 896 at 15,137, spin-break +10 X 1,168 at 15,322, spins 15,433 / 15,508); then the
record's high route over the 15,700 block (jump 15,596 from X 1,574 y 96; the type-8 bird hits at 15,631 and its
knockback puts Ryu on the middle block, y 96 X 1,667 at 15,672; off its right end at ~15,726; onto the y-128 block
15,740); room 14 at 16,020 (+11); C8 shaft; room 15 at 16,146 (+39); top at X 170 16,278; spins 15,878 and 16,392;
4-1 load 16,602. Exits **J&S / 0 ninpo**, hp 11 (the 4-2 cutscene refills HP to 16: **HP is free in 4-1**).

**TRAP (found here): r2c only works because of a NesHawk input conflict at 15,726.** Rows 15,726-15,727 = Left+A, but
NesHawk's game read the pad as 0 on 15,726, so the effective press is **one frame** (15,727). Every legal 2-frame version
(15,725-26 / 26-27 / 27-28 / 28-29) **falls into the pit at the block** (Mesen with r2c's pads, `c15726.py`), and NesHawk
itself dies there (16,063) as soon as `$BF` differs (`nh_r2c_b98.bin`: the conflict is gone). On our chain the conflict
frames will differ, so the block exit had to be re-solved: **FIXED at 0 f** (`bexit.py` + `bexit_full.py`): rows
15,719-15,720 = **Left+A**, 15,721-15,760 = Right (replaces r2c's Right+A 15,721-22 / blank / Left+A 15,726-27 / Right+A
15,731-32); the full line is identical to r2c (Mesen pads: rooms 16,020 / 16,146, load 16,602, same hits, J&S/0).
**Use `work/l41p/r2c_fix.inputs.txt`** (= r2c + the 15,068 tosser slash below + this exit; check_inputs PASS; rows from
`ref4751/08_4-1_control`). NesHawk (`work/l41p/nh_fix_<bf>.bin`, `$BF` poked at control): load 16,602 for `$BF`-at-control
128, 162, 202 and the TAS's 217 (spawn b 64, 98, 138, 153); **b 76 (`$BF` 140) diverged at 15,878** (Mesen with the same
rows is fine): another NesHawk input conflict (the conflict frames move with the sound state, which reads `$BF`) - on
the chain, re-check every press on NesHawk and nudge eaten presses by a frame (as 2-2 did with `--freeze`).

### Arrival dependence (measured)

* ROM: in 4-1 only the **type-2 tosser** (`thrower` $C35C, axe $CB0B/$CB1B) reads `$BF`. Everything else is position or
  room-timer driven, and our 4-1 control state = the TAS's (hp 16, np 0, no art, Ryu x 32, no enemies) except `$BF`,
  `$62`, score. So r2c's effective pads from our control = the TAS state with `$BF` poked (Mesen, full line).
* The tosser spawns at X 818 y 128 (on a pillar) when Ryu reaches X ~705 = control + 448; its first throw comes `b >> 1`
  frames later, b = spawn `$BF` = **(`$BF` at 4-1 control + 192) mod 256** on r2c's pace (+ any lateness at X 705).
* **Our `$BF` at 4-1 control = (F - 16) mod 256** (F = 4-1 control frame): the TAS's frame - `$BF` offset is 14 for
  3-1..3-3 and 16 from 4-1 (+2 at every boss transition), and our chain matched the TAS's 14 at 3-1, 3-2 and 3-3.
  **Read `$BF` on the real 4-1 control state to confirm.** So b = (F + 176) mod 256.
* Results (full line, end 16,602 = identical to r2c unless stated):
  * **original r2c (tosser slash on 15,077-78):** b 84-255 identical; b 0-83 mostly broken (an axe hits Ryu as he jumps
    onto the pillar at 15,074-15,087 and he is knocked into the pit / dies), except b 2, 20, 38-41, 43, 44, 47, 48, 51,
    52, 55, 57, 58, 61, 62, 64-67.
  * **repair: move the tosser slash to 15,068-69** (`work/l41p/r2c_b68.inputs.txt`, check_inputs PASS): **identical full
    line for b 55, 57, 58, 61, 62, 64-84 and every sampled b 85-250** (incl. 98, 120, 140, 153, 160, 200); still broken
    for b **54, 56, 59, 60, 63** (no slash time 15,066-15,074 helps). NesHawk: r2c_b68 with b 76 and b 98 = r2c's frames
    up to the 15,726 conflict (then the trap above).
* **Cost table of the 4-1 control frame (tosser only, with the 15,068 slash; cost = frames to wait at control for the
  next good b):**

| 4-1 control F | `$BF` at control | spawn b | cost |
|---|---|---|---|
| 14,726 / 14,728 | 118 / 120 | 54 / 56 | 1 / 1 |
| 14,727, 14,729, 14,730 | 119, 121, 122 | 55, 57, 58 | 0 |
| **14,731** | 123 | 59 | **2** |
| **14,732** | 124 | 60 | **1** |
| 14,733-14,734 | 125-126 | 61-62 | 0 |
| **14,735** | 127 | 63 | **1** |
| **14,736 - 14,810 (and on to 14,927)** | 128 - 202 (- 63) | 64 - 138 (- 255) | **0** (64-83 need the 15,068 slash; the plain r2c rows cost 16..1 f at F 14,740-14,755). From 14,928 (b 0-53) mostly broken again |

  Conclusion: **any 3-3 exit with 4-1 control 14,736-14,927 (`$BF` 128-255 or 0-63) is free for 4-1**; avoid only 14,731,
  14,732, 14,735 (and 14,726/14,728). Choose 3-3 by its own frames and the 4-4 `$62` phase.

### Lanterns and the budget (`python -m ng.solve.items 4-1`; rooms 14-15 have none)

| lantern | TAS | record | r2c | cost / rule |
|---|---|---|---|---|
| +10 X 272 y 144 | 14,729 air slash | ? | yes | 0 (on the line) |
| +5 X 464 y 144 | 14,864 | ? | yes | 0 |
| 1000 X 608, 500 X 720 | - | - | - | points |
| **J&S X 896 y 80** | 15,137 (slash 15,130) | yes | yes | 0; **take it** (backup 4-2 X 2,624) |
| **Windmill X 944 y 128** | no | no | no | **TRAP**: no slash/spin near it after the J&S |
| 1-UP X 1,008 | - | - | - | - |
| +10 X 1,168 y 96 | spin-break 15,322 (net +5) | ? | yes | 0 |
| **InvFW X 1,360 y 80** | no (spins 15,433 at X 1,329 y 141 and 15,508 at X 1,442 pass below) | no | no | **TRAP**: erases J&S after 8.6 s; keep the spins low there |
| +5 X 1,680 y 80 | no | ? | no | ~0 on a high route over the 15,700 block (Ryu passes X 1,616-1,680 at y 48-96): take it if the block re-solve slashes near it |
| 500 X 1,824, 1000 X 2,080 | - | - | - | points |

* Ninpo: on-line supply 25 (+5 at X 1,680 if free). TAS spends it all (5 spins) and exits J&S/0; the record also exits
  **J&S/00** (HUD 18,530); r2c J&S/0. Spare 4-1 ninpo carries to 4-2/4-3 (same act; only the 4-4 tally charges 3 f/pt
  over 5), so **exit J&S, ninpo 0-10 is fine**; never skip a time-saving spin to save ninpo (4-2 has 25 on the line:
  +5 X 704, +5 X 784, +5 X 1,152, +10 X 2,784; 4-3 has 30: the two spin-breaks, +10 X 464, +5 X 656).
* Act IV traps after 4-1: 4-2 Windmills X 2,224 / **X 2,976** and FW X 944 / Star X 1,248; 4-3 FW X 272 y 112 (above the
  +5 the TAS spin-breaks), room-19 Windmill X 304 / FW X 816, room-20 Windmill X 304. 4-3 has no J&S: exit 4-3 with
  **J&S + exactly 5**.

### Free frames at the act start: none

* `pretest.py` (Mesen TAS state 14,560): Right held from 14,563 / 65 / 66 / 67 / 68 or only from 14,569 gives the same x on
  every frame (32 until control, 33 on the control frame, then 1.5 px/f): **no pre-control movement at an act start**
  (unlike the 3-2/3-3 starts). The TAS's first Right is on its control row 14,569; ours must be too (as row 9,993 in 3-1).
* The 3-3 side: the TAS presses Start at 14,415 (Act IV cutscene skip; stage variable 14,417; control +152). The 3-3
  solver must Start at the earliest legal frame; nothing else before 4-1 control matters for 4-1 except the `$BF` table.

### Where 4-1 can still gain (vs r2c / r2c_fix = record -6.6)

1. **15,700 block, up to ~9 f** (r2c +11, record +2): r2c lands on the middle block only thanks to the bird's knockback.
   Grid `blk2.py` / `blk_dbg.py` from X 1,574 (jumps 15,588-15,612, any A length (the jump height is fixed), optional B):
   a jump <= 15,597 takes the same hit; a jump >= 15,600 overshoots to the floor at X 1,730 y 208 (the TAS's own spot
   under its illegal chimney); a mid-air B is a J&S spin (-5) and also ends on the floor; a 15,606 jump clings to a face
   at X ~1,681 y 183 (too low: C8 needs ~56 f). The record lands on the middle block with full HP and slashes the bird:
   **not reproduced** - needs the A* (`ng/stages/a34r2_astar.py`) from 15,585 with "on the middle block, no hit" as goal,
   on the chain (it must also replace the conflict-dependent exit at 15,726).
2. **Room 15, a few f** (r2c +33 vs the TAS's 99 f floor -> top): r2c takes the bird's 3-HP hit mid-climb without using
   it; the record and the TAS boost off that bird onto the top. HP is free (r2c ends with 11 of 16).
3. Shaft: C8 floor ~+20 (148 px at 1.54 vs 2.0 px/f); r2c +28; maybe a few frames at the shaft entry.
4. Expected: `r2c_fix` = record -6.6 as it stands (4-2 control = 4-1 control + 2,185 when the conflicts behave);
   with 1 + 2 done, ~record -15..-20. Start the 4-1 solve from `r2c_fix` rows on the real 4-1 control state (Right on
   the control row), verify on NesHawk, then attack 1 and 2.

## Next: 4-2 plan (prep agent l42p, 2026-10-25)

Tools and dumps: `work/l42p/` (`dumps.py` -> NesHawk RAM per frame `tas42_ram.bin` (TAS 4-2 from `ref4751/09_4-2_control`,
2,330 f) and `r2d_ram.bin` (legal `logs/a34/4-2_r2d`); `ev.py` spawn/hit/ninpo events; `xcmp.py` first frame at each X;
`bfscan.py` = `$BF` poke scan of a dump's effective pads (Mesen); `endiff.py` enemy divergence per frame; `beam42.py`
local legal TAS-tracking beam with a `$BF` poke (own per-button legality: press >= 5 f apart, hold/release >= 2);
`beam42c.py` = the same beam from the locked chain (Mesen `l42p_lock16997.mst` + a stage-rows prefix, TAS axis + 316);
`legtas.py` legalized TAS rows; `nh_chain.py <stage rows> <state>` = **NesHawk replay on the real chain** (from
`lock_41q_pre` + r15_c rows) vs the TAS at -316, lists misreads/hits, saves a state; `nh_tasbf.py`, `nhtrace.py`,
`nhfix.py` (misread finder/fixer); `var18065.py`, `spingrid.py`, `spintest.py`, `endiv.py`, `encmp.py` (chain vs TAS
enemies); `trans.py` + `nh_check.py` = transition / control-row tests (Mesen + NesHawk); `dump43.py` = 4-3 ninpo
events). Logs `work/l42p/*.out`.
Mesen states: `states/mesen/l42p_tas16682.mst` (TAS 4-2 control, = NesHawk RAM at 16,683); **locked chain (r15_c):
`l42p_lock16997.mst` (frame 16,997, pre-control) and `l42p_lock16998R.mst` (after Right on the control row 16,998: x 65.5
y 64, hp 16, np 0, J&S, `$BF` 81, `$62` 6)** - with that Right it equals the TAS's 4-2 control state except `$BF`
(81 vs 21), `$62`, score and sound (no enemies active). Older: `l42p_c3b17020.mst`, `l42p_c3b16870.mst` (c3b).

### Splits

* Definition (same as 4-1 -> 4-2): control = the first frame whose input moves Ryu. **TAS 4-2 = 16,682 -> 4-3 control
  18,959 = 2,277 f** (Mesen and NesHawk: Left held from 18,900 first moves Ryu on 18,959; the "18,960" elsewhere is
  one late). **Record 4-2 = 38.33 s = 2,303.8 f** (record_events control cum NES 17,022.0 -> 19,325.8, +-3).
  Record - TAS = **+26.8**.
* **4-2 is one room (16), X 65 -> 3,035, and the TAS runs it at exact pure pace**: X = 65 + 1.5 (f - 16,682) to X 3,000
  (18,642); then the exit wall: bird hit 18,658 (hp 16 -> 13) boosts Ryu up the wall, wall jumps, **stage-end trigger =
  Ryu at X 3,035 y 84 on 18,680**. 4-3 control = trigger + 279 (128-f freeze, load 18,808, 151 f) - fixed.
* **Target (locked 4-2 control 16,998): 4-3 control <= 19,301 = trigger <= 19,022** (record pace = control + 2,303 /
  trigger <= control + 2,024). TAS pace: trigger = control + 1,998 = 18,996, 4-3 control 19,275.

| section (TAS frames) | TAS | record - TAS (scroll lag, `work/a34r2/lag.py` on r42.json; scroll + ~128 = X) | why | legal `4-2_r2d` - TAS |
|---|---|---|---|---|
| control -> TAS 17,351 (X ~1,070) | pure | +6..+8 (+6 already at scroll 51: mostly the +-3 control estimate; +2 near tosser 1 X 659) | tosser 1 | 0 (legal TAS rows, exact sync) |
| 17,351 -> 17,762 (X 1,070 -> 1,685) | pure | +7 -> +15 | tossers 2/3 (X 1,205 / 1,349, spawn when Ryu is at X 1,091 / 1,235) + the type-11 birds at X 1,714 | 0 |
| 17,762 -> 18,603 (X 1,685 -> 2,946, max scroll) | pure; L+R in a jump 18,067-18,108 (X 2,140-2,200) | +15 -> +13 (no loss in the TAS's U+D section; he runs the brown top ledges) | - | 0 to X 2,200 (-2 there), then **+11**: hit 18,175 (hp 15) and **the Windmill X 2,224 caught at 18,122 (TRAP: r2d exits Windmill / 0)** |
| exit wall 18,603 -> trigger 18,680 | 2 jumps, bird boost | **+13 -> +27** | TAS: bird boost 18,658 + illegal A every frame / L+R 18,669-18,679. Record: drop to the post, jump to the brick wall, ~4 C8 cycles, no boost | +11 -> +16 (X 3,000) -> **+53** (trigger 18,733) |
| **total** | **2,277** | **+26.8** | | **+53 = record +27** (`4-2_r2d`, from the TAS state; not usable on our `$BF`, see below) |

So vs the record a legal line can win **~+13 on the TAS-pace part** (the record is +13 behind the TAS at X 2,900 and the
TAS's run to there is legal except the throwers' `$BF` and the facing trick at 18,065, see below), and **the exit wall** is where the legal lines lose most
(r2d +37 there, the record +14).

### TAS rule breaks in 4-2

* U+D+Right while running (1,163 frames): = Right (positions identical; r2d uses Right/Down+Right). Harmless.
* One-frame A/B (43): the jump height is fixed and a slash starts on the press, so 2-frame holds are equivalent
  (r2d = TAS sync to 18,029 with them). Careful: with J&S and ninpo >= 5 an air B is a **spin**; the TAS slashes in the
  air with np 0 at 17,743 / 17,926 / 17,958 / 18,075 / 18,191 / 18,282 / 18,485 - with ninpo left use **Down+B**
  (regular air sword, as 4-1 r15 found).
* L+R: 18,067-18,074 + 18,076-18,108 (in a jump from X 2,138 after a 1-frame Left on 18,065; Ryu keeps 1.5 px/f;
  r2d passes the same jump legally 2 f AHEAD) and 18,679 (exit wall).
* Exit wall 18,659-18,680: Left+A 18,669, Right+A 18,674, Left+A 18,675 (A on consecutive frames), L+R 18,679.

### Arrival dependence (`$BF`)

* ROM/pokes: the **three type-2 throwers** (spawn on y-128 ledges at X 659 / 1,205 / 1,349 when Ryu reaches X 545 /
  1,091 / 1,235) and their **type-18 thrown blades** (arcing) read `$BF` (delay `$BF >> 1` after spawn/throw, as in
  3-2/4-1). Also **every other 4-2 enemy (types 8, 11, 13) shifts by ~1 px / 1 frame with `$BF`** (spawn y 64/65 of the
  type-13 droppers, type-11 bird x), so after ~X 1,700 the exact TAS sync is chaotic in `$BF` (the TAS rows survive
  only `$BF`-at-control 16-32 and 43 out of 0-124; failures elsewhere at 18,175-18,486 are 1-px enemy differences:
  small local repairs, as r2d's A* did).
* Our `$BF` at 4-2 control = **(F - 21) mod 256** (**locked r15_c 16,998 -> 81**, read on the state; c3b 17,020 -> 103; the TAS has the same offset:
  16,682 -> 21). On TAS pace the spawn `$BF` of the throwers are b1 = c + 64, b2 = c + 172, b3 = c + 12 (c = `$BF` at
  control, + d frames of lateness at the spawn point).
* **TAS rows with our `$BF` (scan c 0-126, `work/l42p/bf_tas.out`):** thrower 1 hits the TAS line only for c 0, 3, 4,
  7, 8, 10, 13, 14 (it passes unchanged for every other c scanned); for **every c 73-113 (F 16,990-17,030) the TAS line is hit by the throwers 2/3**:
  at 17,434-17,448 (blade of thrower 2, Ryu at X ~1,170: c 84, 87, 88, 103, 104, 107, 108, 111, 112) or at
  17,512-17,520 (thrower 3's blades at X ~1,310-1,320: all other c). So the window X 1,090 -> 1,450 must be re-solved
  for our c; cost table from `beam42.py <c> 2` (TAS state, `$BF` poked to c + 673 at 17,355, TAS pads to 17,440, legal
  beam width 24 to X 1,450; lag = frames behind the TAS at X 1,450 (TAS 17,605); np at the goal):

| `$BF` at control c | 4-2 control F | window-2 cost (Mesen beam) |
|---|---|---|
| 73-76, 78-80 | 16,990-16,993, 16,995-16,997 | 0 f, hp 16 (spin, np 5 -> 0) |
| **81** | **16,998 (LOCKED r15_c)** | **0 f, hp 16** (NesHawk-confirmed on the real chain, below) |
| 82 | 16,999 | 0 f, hp 16 |
| 99-102 | 17,016-17,019 | 0 f, hp 16 |
| 103 | 17,020 (c3b) | no beam goal within 200 f (bad) |
| 77, 83-98, 104-113 | | not run (4-1 locked before they were needed) |

* **The locked arrival is free: c = 81.** The only change the throwers need is **the J&S spin 12 f earlier** (TAS
  17,512-13 instead of 17,524-25 = chain 17,828-29): it kills thrower 3 / its blade before the 17,512 hit.
* **Legal exact TAS sync on the locked chain (NesHawk, `work/l42p/nh_chain.py`):** `work/l42p/s42_sync81.inputs.txt`
  = 1,383 4-2 stage rows (row 1 = Right on the control row 16,998) = the TAS rows legalized (U+D dropped, A/B 2 f, L+R not
  reached) + that spin. From `lock_41q_pre` + r15_c rows 14,848-16,997 + these rows: **chain frame = TAS frame + 316
  exactly, frame 18,380 X 2,138 y 128, hp 16, np 0, J&S, `$BF` 183** (NesHawk state `l42p_sync18380`; Mesen
  `states/mesen/l42p_lock16997.mst` + the rows). One NesHawk misread (17,074: the A of the jump at TAS 16,757 is read a
  frame late; 38 frames of that jump are 1-4 px off, then it re-syncs on landing, harmless) - judge on the full power-on
  file still to do. So 4-2 is at **TAS +0 at X 2,138** (TAS 18,064; the record is ~+14 behind the TAS there), with the +5 X 704 taken and spent.

### Lanterns and the budget (`python -m ng.solve.items 4-2`; TAS pass frame / Ryu y)

| lantern | TAS | cost / rule |
|---|---|---|
| +5 X 304 y 112, +10 X 432 y 112 | passes 16,847 y 144 / 16,932 y 148 | detours ~8 f each (ninpo_budget) |
| **Windmill X 688 y 96** | passes 17,103 y 177 | **TRAP**: right above/before the +5 X 704; never a high jump-slash there |
| **+5 X 704 y 160** | slash 17,101 (np 0 -> 5) | 0, take it (the thrower-3 spin spends it: TAS 17,524, **ours TAS-axis 17,512 = chain 17,828**) |
| +10 X 768 y 96 | - | ~35 f |
| +5 X 784 y 160 | passes 17,167 y 192 | ~1 f |
| **FW X 944 y 160** | passes 17,273 y 128 (on the ledge above it) | **TRAP** |
| +5 X 1,152 y 160 | passes 17,412 y 192 | ~1 f (in the thrower-2 zone) |
| +10 X 1,248 y 96 / **Star X 1,248 y 160** | passes 17,476 y 192 | Star = **TRAP** (the +10 above it ~35 f) |
| hourglass X 1,392 y 160 | passes 17,572 y 128 | don't (timestop; untested) |
| **Windmill X 2,224 y 96** | passes 18,129 y 128 | **TRAP on the line: r2d caught it (18,122)** |
| health X 2,352 y 160 | passes 18,214 y 128 | worth ~1-2 f: **HP carries into 4-3** (no refill at 4-2 -> 4-3; TAS enters 4-3 with 13) |
| 1-UP X 2,560 y 96 | - | - |
| J&S X 2,624 y 128 | passes 18,395 y 176 | backup J&S (repairs a lost J&S) |
| **+10 X 2,784 y 80** | slash 18,485 (np at 18,502) | 0, take it |
| **Windmill X 2,976 y 128** | passes 18,630 y 173, jumping | **TRAP, the last lantern before 4-3**: no slash/spin near X 2,976 at y ~110-150 |

* **4-3 needs (NesHawk dumps from `ref4751/10_4-3_control`, `work/l42p/dump43.py`):** TAS 4-3 enters J&S/10, hp 13
  and spins 7 times: room 18 spin-breaks of the +5 X 272 (19,237) and the +10 X 592 (19,483), room 19 three spins
  (19,930 / 20,027 / 20,114, np 15 -> 0), room 20 +10 X 454 (20,877), spins 20,899 / 20,938, +5 X 667 (21,019) -> exit
  J&S/5, 4-4 spin 21,361. On-line 4-3 supply = 30. Legal `r4_43q_x1` (to room 20): spin-break +5 (19,615-22), room 19
  spins 20,025 / 20,113 / 20,158 + the +5 X 480 (20,131) -> 0 at room 20, so room 20 (+10 X 464, +5 X 656) leaves 2
  spins for the exit 5. The record also enters with 10 and exits 05 (its room-19 kills are 2 spins).
* **Plan: exit 4-2 with J&S + 10** (+5 X 704 -> thrower-3 spin -> +10 X 2,784 = the TAS/record line; on c 81 the spin
  is required, so the sync line has np 0 from 17,828 until the +10 X 2,784). If the +5 X 784 / X 1,152 turn out to cost
  <= 1 f (they are not on the sync line: it passes them at y 192 without a slash), **exit with 15-20**: 4-3 is our weakest stage (legal lines
  ~+90 behind the record at room d) and every extra spin there is a free kill; any excess is burnt by a spin during a
  jump in 4-3 room 20 so 4-3 still exits with exactly 5. Never exit 4-2 with less than 10 or without J&S.
* HP: 4-2 -> 4-3 is a plain stage change, **HP carries** (4-1 -> 4-2 refilled it). The legal 4-3 lines take hits
  (r4_43q_x1 13 -> 5 before room 20), so 4-2 HP has value: prefer hp >= 13 at the exit (the TAS's exit boost costs 3).

### Transitions and Start

* **4-1 -> 4-2** (cutscene): Start skips it only from stage end + 9 (NesHawk; Mesen + 8) - as in c3b / r15.
* **4-2 -> 4-3 is a plain stage change, no cutscene, no skip**: from the trigger (X 3,035 y 84) the game freezes 128 f,
  loads 4-3 (18,808) and gives control 151 f later (18,959). Start on any frame from the trigger to control changes
  nothing (Mesen: every frame 18,680-18,700, then every 10-50 f to 18,955; NesHawk: none / 18,681 / 18,700 -> load
  18,808, control 18,959). **Start before the trigger pauses the game - never press it in 4-2.** Rows after the trigger
  are free (end the 4-2 rows at the trigger, blanks after; the 4-3 control row = first 4-3 row).

### Free frames at the 4-2 start: none, but the control row must be Right

* Ryu falls in at x 64 y 64. Right on the control row moves him (x 64 -> 65.5, as the TAS's 16,682); Right on any
  earlier row does nothing (Mesen: Right on the last 1/2/3/5/10/30/60/100/150 rows before control = identical; NesHawk:
  last 1 and 5 rows = identical). **c3b's row 17,020 is blank** (x 64 -> 64): the 4-2 stage rows must start with Right on
  the control row (same rule as 4-1), worth 1 f. **The locked `l41_r15_c_poweron` also ends with a blank row 16,998 =
  the 4-2 control row: the 4-2 stage rows must start with Right there** (as the 4-1 stage rows replaced q4's 14,848).

### Where 4-2 stands and can gain (on the locked chain, c 81)

1. **Control -> X 2,312 (TAS 18,180 = chain 18,496): solved at TAS pace, hp 16** - `work/l42p/s42_to18180.inputs.txt`
   (1,499 stage rows, row 1 = control row; legal; NesHawk on the chain: X 2,312 y 82 at 18,496 = 2 f AHEAD of the TAS,
   hp 16, np 0, J&S; NesHawk state `l42p_c18496`). Built from: legal TAS rows + spin at 17,828 + **drop the TAS's 1-frame
   Left at 18,065** (its turn costs ~2 f legally and is not needed: `work/l42p/var18065.py`, every Left/blank variant
   gets hit at 18,075-18,107) + L+R -> Right (the 18,067-18,108 jump keeps 1.5 px/f).
2. **Next problem: TAS 18,196 = chain 18,512 (X 2,336 y 94), a 3-HP hit.** Why: the TAS's 1-frame Left on 18,065 turns
   Ryu to face LEFT for the 18,066 jump (facing is fixed in the air) and its L+R keeps him moving right at 1.5 px/f while
   facing left, so its air B on 18,075 slashes BEHIND him and kills the type-13 dropper at X ~2,147 (`work/l42p/endiv.py`:
   the enemy sets differ from 18,086 on). Legally the Left turn costs (2 f of Left = hit at 18,075, `var18065.py`) and a
   right-moving jump cannot face left at full speed, so on our line that type 13 lives, slot use shifts, and a type-8
   bird (slot 3, X ~2,323 y 112, under Ryu) hits him at 18,196. A J&S spin anywhere in 18,070-18,088 (tested with 5
   ninpo poked) does not prevent it (`spintest.py`). Frame beams from 18,496 (`beam42c.py`, width 48/64, hp weight 6/25)
   lose 13-23 f by X 2,500 with 1-2 hits; r2d's fine A* lost +11 here at the TAS's `$BF`. **This stretch (TAS 18,180 ->
   ~18,330, X 2,312 -> 2,550) is the one to solve next** - A* (`ng/stages/a34r2_astar.py`, A34_FINE / ENEMYKEY /
   HMAX / SWITCH) from `l42p_c18496`; the record runs the brown ledges at the top of the screen here (video
   20,268-20,307) and slashes the bird on the way down, losing nothing vs the TAS. Take the health X 2,352 if it costs
   <= 2 f (HP carries into 4-3).
3. Exit wall: the biggest legal loss (r2d +37 from X 2,900; record +14). Options: the record's post -> brick wall + C8
   climb (~TAS +14..+26), or a legal version of the TAS's type-11 bird boost (the bird is slot 5 from 17,962, it homes on
   Ryu all the way and hits him at X 3,025 y 131 on 18,658; its position at the wall depends on the whole line).
4. Expected: TAS +0 to X 2,312 (done) + ~+5..+11 to X 2,900 + the record's exit (+14) = TAS +20..+25 = **record
   -2..-7** (4-3 control ~19,295-19,300 vs the record pace 19,301); a legal exit boost would add ~10 f more.

## Next: 4-3 plan (prep agent l43p, 2026-10-25)

Tools, dumps, states: `work/l43p/` (`lib.py` helpers; `dumps.py` -> NesHawk RAM per frame `tas43_ram.bin` (TAS 4-3 from
`ref4751/10_4-3_control`, rows 18,961-21,420) and `r4q_ram.bin` (legal `logs/a34/r4_43q_x1` from the same state); `ev.py`
spawn/hit/ninpo events (`tas43_ev.txt`); `xcmp.py` first frame per room/X; `tas43_rows_rle.txt` = TAS rows run-length
with L+R / U+D / 1-f flags (labels = row numbers); `boost.py` / `bsearch.py` = legalized TAS rows from TAS states;
`bfscan.py` / `bfdiff.py` = `$BF` pokes; `nh_trans.py` = 4-4 transition (NesHawk); `ctltest.py` = 4-3 control row;
`pre2.py` + `nh_pre2.py` = head start; `cycles.py` = w21's cycle enumerator with `--kmax/--workers`). Mesen TAS states
`states/mesen/l43p_tas<f>.mst` (state after row f) for f = 18960, 19030, 19095, 19160, 19275, 19290, 19330, 19440, 19560,
19640, 19660, 19690, 19725, 19760, 19800, 19830, 20020, 20085, 20130, 20240, 20400, 20470, 20515, 20570, 20640, 20750,
20820, 20840, 21000, 21060: **0 RAM differences vs NesHawk** at every one. Frame numbers = power-on rows (NesHawk frame k
after row k). The TAS enters 4-3 with hp 13, np 10, J&S.

### FIRST: k932a's 4-3 control is 19,298, not 19,299 (1 free frame)

* 4-2 -> 4-3: **4-3 control = trigger + 279** (TAS 18,680 -> 18,959). k932a's trigger is **19,019** (`$5C` 2 -> 0, Mesen
  from `l42a_k18932` + its rows) -> **control 19,298**. Measured on the chain (`ctltest.py` Mesen; NesHawk agrees in
  `nh_pre2.py`): Left on row 19,298 moves Ryu x 224 -> 222 on 19,298; with 19,298 blank (as the candidate file has it)
  he first moves on 19,299. Left earlier changes nothing (Left from 19,260 / 19,290 / 19,297 = Left from 19,298).
* So **`l42_w_k932a` = 4-2 2,300 f, 4-3 control 19,298 = record -3.8 (cum -203.8)**: lock rows 1-19,297 and start the
  4-3 stage rows with Left on 19,298 (= TAS row 18,959; lag **339**). Same rule for any 4-2 candidate: file = rows
  1 .. trigger + 278, the 4-3 control row = trigger + 279.
* `$BF` after the control row = (F - 21) mod 256 (19,298 -> 77; TAS 18,959 -> 250).

### Splits (control -> 4-4 control; room change = first frame with the new `$6E`)

| room | TAS rows | TAS | record (video: first picture - 23) | record - TAS | legal so far (`r4_43q_x1`, TAS state) | why the record loses |
|---|---|---|---|---|---|---|
| 17 (4-3a: run left, climb the column at X 104) | 18,959 -> 19,076 | 117 | ~137 | **+20** | 130 (+13) | TAS climbs 2 px/f (A every 4 f + L+R); legal = A every 5 f |
| 18 (4-3b: right, exit wall X 923) | 19,076 -> 19,711 | 635 | ~697 | **+62** | 715 (+80) | entry: chimney / box top instead of the TAS's in-wall zip (~+17); the X 346 chimney (~+41) |
| 19 (4-3c: right, exit X 1,179 y ~80) | 19,711 -> 20,497 | 786 | ~830 | **+44** | 912 (+126) | pillar top ~-7 (!), then the stepped block / gunner (~+51) |
| 20 (4-3d: left, then right to the trigger at X 748 y 208) | 20,497 -> 21,074 | 577 | ~614 | **+37** | not solved | entry climb (TAS U+D / L+R) |
| trigger -> 4-4 control | 21,074 -> 21,353 | 279 | 279 | 0 | 279 | fixed |
| **total** | 18,959 -> 21,353 | **2,394** | **2,557.2** | **+163** | r4q: room 20 at TAS +219 (record ~+127), hp 5 | |

* Record pace on k932a: **4-4 control <= 19,298 + 2,557 = 21,855 (trigger <= 21,576)** = TAS +163 on lag 339. Record
  cum NES: 4-3 control 19,325.8, 4-4 control 21,883.0 (`record_events.json`); record room changes t = 137, 834, 1,665 (+-3).
* Old legal lines (all from the TAS state): room 18 +13 (r4q), room 19 +93 (`r3_43b_x3` 19,804), pillar top +125
  (`r3_43c0_g2`), block top +137 (`r4_43p_x1`), room 20 +219 (r4q).
* Where a legal line can beat the record: room 17 (already -7: r4q), the room-18 X 300-350 section (**r4q passed it 19 f
  FASTER than the TAS** with a 1-HP floor-enemy boost, see the head start), the legal room-18 and room-19 exit boosts
  (TAS +0..+1), the room-19 pillar (record ~TAS -7). Where it loses: the room-18 entry (in-wall zip, record +17), the
  stepped block in room 19 and room 20's entry climb.

### TAS rule breaks in 4-3 (`tas43_rows_rle.txt`), split into the legal and the banned part

| rows | room | what the TAS does | banned part | legal part / test |
|---|---|---|---|---|
| 18,960 / 19,019 | 17 | 1-f A jumps | 1-f A | 2-f A = identical (chain + legalized TAS rows = TAS X/y exactly to 19,037, `e1.py`) |
| 19,038-19,074 | 17 | column climb X 104-107: A+Left every 4 f with L+R between | L+R, A period 4 | **legal alternating cycle** `A+R,A+R,R,R,L,A+L,A,-,-,-` (A every 5 f, 1.5 px/f; r4q's rows): room 18 at TAS +13. Single-wall cycles do NOT climb here (4,768 legal 7-9 f cycles, `cycles.py`: best +24 px in 45 f): the column is a 3-px chimney. A presses >= 5 f apart vs the TAS's 4 -> ~+10..+13 is the legal floor |
| 19,099-19,160 | 18 | entry: in-wall zip from (91,232) through the box to (152,215) | L+R 11 + 32 f | no legal in-wall movement (a34 round 1: Ryu does not move without L+R). Legal = the record's chimney onto the box top (r4q X 150 at +43, record ~+38) |
| 19,237 | 18 | spin breaks the +5 X 272 at y 160 | 1-f B | legal (2-f B); the FW X 272 y 112 is 48 px above |
| 19,281 | 18 | Down+Left+Up 1 f before the chimney | U+D | plain Left is NOT equivalent (x 329 vs 328; legalized rows then fall to X 347 y 191, `boost.py 19275 19345`) |
| 19,282-19,318 | 18 | chimney X 326-357 (left column y 96-151, right wall X 358): A+R / A+L alternating every 4-5 f with 1-f direction taps | 1-f L/R holds, A period 4 (once) | to search: alternating period-5 cycle (~1.5 px/f, y 160 -> ~100: ~+8) |
| 19,319-19,331 | 18 | L+R zip over the lip (X 358 y 96) onto the y-96 ledge | L+R 13 f | to search: jump from the left column's top, or the floor-enemy boost (head start) |
| 19,704 | 18 | exit: A+Left 1 f on the exit wall; the type-19 flyer (y 82, ~1.8 px/f, spawned 19,413 at X 372) hits from BEHIND on 19,709 (hp -2) -> room 19 on 19,711 with an upward launch (rflags 0x54) | 1-f A+Left only | **LEGAL**: legalized TAS rows (A+Left 2 f) from `l43p_tas19660`: hit 19,708, room 19,712 (TAS +1), launch present (`boost.py 19660 19760`). Copying the TAS's room-19 rows after it misses its 19,747 wall jump by 1 px; 1,088 exit-timing x jump-shift variants (`bsearch.py`) all drop to the pit floor -> re-search the room-19 start after a legal boost |
| 19,768-19,800 | 19 | pillar in-wall zip (118,160) -> (170,126) | L+R 33 f | no legal equivalent; legal = the record's route (gap between the small box and the pillar, onto the box, jump to the pillar top): record ~7 f FASTER than the TAS from the room entry (video, +-3); r4q +30. **Biggest open item** |
| 19,930 / 20,027 | 19 | spins (type 1 at X 370 y 160, the type-6 pair) | 1-f B | legal |
| 20,092-20,125 | 19 | stepped-block face X 602: A+L every 4 f with L+R; spin inside the L+R | L+R, period | climb legally (alternating / C8) + spin; r4q lost ~20 here |
| 20,480 | 19 | 1-f B; a type-17 flyer (three at y 113 from X ~900, 20,327-20,349) hits from behind (hp -1) -> room 20 with a launch | 1-f B | legal (2-f B); not replayed |
| 20,521-20,530 | 20 | 1-f A+R / A+L alternation | 1-f, period | alternating period-5 cycle |
| 20,580-20,601 | 20 | Down+Left+Up 22 f | U+D | to test (Left / Up+Left / Down+Left) |
| 20,613-20,645 | 20 | L+R 33 f (climb to y ~94 at X ~120) | L+R | to search |
| 20,827-20,837 | 20 | wall climb X 392-394, A every 3-5 f | period, 1-f | C8 / alternating |
| all other rows | | runs, jumps, slashes | 1-f A/B | legal with 2-f holds |

### Ninpo / art / HP

* Lanterns (`python -m ng.solve.items 4-3`; room 17 none): room 18 **FW X 272 y 112 (TRAP)**, +5 X 272 y 176, 500 X 464,
  +10 X 592 y 112, +5 X 688 y 96, **Windmill X 752 y 160 (TRAP; the TAS jumps past it at y 128, 19,582)**, 1000 X 848;
  room 19 **Windmill X 304 y 144 (TRAP)**, 1000 X 432, +5 X 480 y 144, health X 720 y 128, **FW X 816 y 96 (TRAP)**, 500
  X 896, 1000 X 1,136; room 20 **Windmill X 304 y 96 (TRAP: the TAS's B at 20,761 is at y 192 with np 0 = a plain
  slash; with np >= 5 it would be a spin)**, 500 X 304 y 144, +10 X 464 y 96, +5 X 656 y 96. **No J&S lantern.**
* TAS: enters 10; spin-breaks +5 X 272 (19,237: 10 -> 5 -> 10) and +10 X 592 (19,483: -> 15); room 19 spins 19,930 /
  20,027 / 20,114 (-> 0); room 20 +10 X 464 (20,877), spins 20,899 / 20,938, +5 X 656 (21,019) -> **exit J&S/5**. It never
  takes +5 X 688 or +5 X 480. Supply used 30, spent 35 (7 spins).
* With J&S and np >= 5 every air B is a spin (l42a: Down+B too): spin-breaking a +5 = net 0, a +10 = net +5.
* **Plan (enter with 10): spend like the TAS, exit with exactly 5.** Room 18: +5 X 272 (spin only from y >= 160) -> 10,
  +10 X 592 -> 15 (+5 X 688 if on the line; r4q took it at 19,622); room 19: up to 3 kill spins (+5 X 480 if free);
  room 20: +10 X 464, the kill spins, **+5 X 656 last**. Arrive at X 656 with 0 (burn any excess with spins during room-20
  jumps) or with exactly 5 and skip it. Never touch the FWs X 272 / X 816 or the Windmills X 752 / X 304 / X 304.
* **HP does NOT refill at 4-4** (TAS 4-4 control hp 10 = its 4-3 exit), but `4-4_p2` (J&S kill, control + 23) takes no
  hit: 4-3 may spend all but 1 HP. From k932a's 15 that is up to 14 HP of damage boosts (the TAS takes 2 + 1); the health
  X 720 (room 19) can top up. HP is effectively free in 4-3; boosts are the main tool.

### Arrival dependence (`$BF`)

* Readers (pokes on the TAS line, `bfscan.py` / `bfdiff.py`): the **type-2 throwers** and their **type-18 blades**
  (throw delay, as in 3-2/4-1/4-2): room 18 X 676 y 128 (spawns when Ryu reaches X ~563, TAS 19,463) and X 771 y 64
  (19,643); room 19 X 1,173 y 208 (20,411); room 20 X 499 y 112 (20,821, blade 20,856). Types 1, 5, 6, 8, 9, 20 shift by
  1 px with `$BF` (spawn x) without changing the TAS line; the type-0 floor enemies (room 18 X ~260-330), the type-19 and
  type-17 flyers follow Ryu.
* TAS-line proxy (TAS effective pads from `l43p_tas18960` with `$BF` poked to our value v = (F - 20) mod 256, F = our 4-3
  control frame on lag 339; Ryu's X/y/hp compared to the trigger):

| 4-3 control F | v | TAS line |
|---|---|---|
| 19,269 - 19,285 | 49 - 65 | thrower X 676's blade hits at TAS 19,523-19,532 (hp -1) |
| **19,286** | 66 | **unchanged to the trigger** |
| 19,287 | 67 | room-20 thrower: hit at 20,898 |
| 19,288 | 68 | blade hit at 19,531 |
| **19,289 - 19,294** | 69 - 74 | **unchanged to the trigger** |
| 19,295 - 19,304 (k932a 19,298 = v 78) | 75 - 84 | blade hit at 19,517-19,519 |

  So on the TAS line only the room-18 thrower depends on our arrival, right where the TAS already spins (19,483,
  breaking the +10 X 592): a spin a few frames earlier/later should kill the blade (as 4-2's thrower spin moved 12 f).
  A legal line reaches X ~560 40-90 f later than the TAS, so its own spawn `$BF` decides: **the 4-2 arrival cannot be
  costed for 4-3 yet; pick 4-2 by its own frames** (no 4-3 reason found to wait).

### Transitions

* **4-2 -> 4-3:** control = trigger + 279; Start after the trigger does nothing, before it pauses. Left on the control
  row is the first moving row (see FIRST).
* **4-3 -> 4-4** (NesHawk on the TAS path, `nh_trans.py`): trigger = first `$5C` 2 -> 0 = **Ryu reaching X 748 on the
  room-20 floor** (TAS 21,074, y 208); stage 11 loads at trigger + 128 (21,202); **4-4 control = trigger + 279
  (21,353)**. **Start does nothing** (2-f Start at 21,075 / 090 / 120 / 150 / 190 / 203 / 206 / 215 / 230 / 260 / 300 /
  340: same load and control). Left held from 21,210 / 21,300 / 21,340 / 21,352 = Left from 21,353 (x 32 -> 31): **no
  free frames**; the 4-4 rows start with Left on trigger + 279 (4-4_p2's first row). End the 4-3 rows at the trigger.

### Head start on the chain (verified)

* `work/l43p/pre2_19599.txt` = **302 4-3 stage rows from the real control row 19,298** (Left, A+Left x2 (= the TAS's
  1-f A), legalized TAS rows, r4q's room-17 climb and room-18 start; lag 339); full power-on file
  `work/l43p/pre2_19599_poweron.inputs.txt` (19,599 rows = k932a rows 1-19,297 + these; check_inputs PASS).
  **NesHawk = Mesen frame for frame (0 differences)**: room 18 on 19,428 (TAS +13), X 237 y 176 at 19,599 (TAS-axis
  19,260), hp 15, np 10, J&S, `$BF` 122. States: NesHawk `states/l43p_pre2_19440` (room 18, X 104 y 83) and
  `states/l43p_pre2_19599`; Mesen `states/mesen/l43p_pre2_19599.mst`, `l43p_k932a19297.mst` (pre-control 19,297).
  (`l43p_pre1_*` / `l43p_k932a19298.mst` = the older lag-340 version with a blank 19,298: don't use.)
* r4q's rows stop matching at TAS-axis 19,287: r4q is hit there by a type-0 floor enemy (X ~264-270 y ~201, from below)
  and the knockback lifts it over the X 346 chimney (X 300 -> 350 in 41 f vs the TAS's 60 f, then along y ~51-60); on
  our chain that enemy misses (1-px `$BF` shift) and the copied rows end stuck in the chimney bottom (X 347 y 157). If
  4-2 changes, rebuild with `pre2.py` from the new pre-control state (room 17 has no enemies: the rows carry over).

### Next steps for the 4-3 solver (by value)

1. Room 18 X 270-370 from `l43p_pre2_19599`: (a) the floor-enemy boost (make the type-0 at X ~265 hit Ryu from below as
   he jumps at X ~275: r4q's line, 19 f faster than the TAS there); (b) the chimney with a period-5 alternating cycle and
   a jump from the left column's top over the lip. Target X 365 y 96 by TAS-axis ~19,345 (+15).
2. Room 18 X 370 -> exit at TAS pace (legal TAS rows), the thrower blade (spin timing), the legal exit boost (type-19
   flyer from behind at the exit wall, hp -2): needs the flyer behind Ryu at X ~910, so stay near TAS pace.
3. Room 19 entry -> pillar top: the record's box route (record ~TAS -7; with or without the launch).
4. The stepped block (TAS 20,092-20,125), room 20's entry climb (20,521-20,645), then the run to X 748.
Expected: room 17 +13, room 18 +40..+60, room 19 +40..+60, room 20 ~+40 -> TAS +130..+170 = record -30..+5.

## Next: 4-4 plan (prep agent l44p, 2026-10-26)

Kelbeross (two dogs) with J&S + exactly 5 ninpo: **ONE spin, kill on stage row 24 (control + 23) = TAS = the floor;
4-4 = 772 rows (control row -> 5-1 control row), record -14.3; the fight does not depend on the arrival; only `$62` at
the 4-3 trigger (the timer tick) can cost 1-3 f.** Tools/states `work/l44p/`: `lib.py`, `mkst.py` (Mesen TAS states
`states/mesen/l44p_tas21352.mst` = pre-control, `l44p_tas21353.mst`; 0 RAM diffs vs the NesHawk dump), `tr.py` (trace),
`grid.py` (kill grid), `bfscan.py` (`$BF` / `$62` / hp pokes), `run.py`, `nh44.py` (NesHawk from `ref4751/10_4-3_control`
+ TAS rows to 21,352, pokes, Start / Right tests), **`graft.py` (graft onto a 4-3 candidate)**, templates `k44_*.txt`.
Frames = power-on rows (NesHawk frame k after row k); 4-4 stage row 1 = the control row.

### Splits

| | control row | kill (boss HP `$66` 0) | earliest Start | 5-1 load (`$6D` 12) | 5-1 control (first row Right moves Ryu, = first `$62` change) | 4-4 |
|---|---|---|---|---|---|---|
| TAS | 21,353 | 21,376 (row 24), timer 149 | 21,971 (21,970 is just as good) | 21,973 | 22,125 | **772** |
| record | | | | | | 785.3 (video, timer-start convention; TAS = 771 in it) = **TAS +14.3** |
| `logs/a34/4-4_p2` (round 1, from the TAS state) | | 21,376 | | 21,973 | 22,125 | 772 = TAS (old "-14 vs record") |
| ours: `work/l44p/k44_d0.txt` | C | C + 23 | C + 617 | C + 620 | **C + 772** | **772 = record -14.3** |

* Record pace: **5-1 control <= 4-4 control + 786**. Old `logs/a34/4-4_p1` (json "load 21,896") is junk: judge FAIL and
  its rows do not even kill on Mesen.
* The old note "4-4: do nothing after the kill" is right in effect: after the kill only the Start row matters (the tally
  and the cutscene ignore everything else; the TAS's post-kill L+R / U+D dance changes nothing).

### The fight (Mesen, NesHawk-confirmed)

* Two dogs (type 27), slot 7 at x 62 y 160 (on its pedestal), slot 6 at x 176 y 160; they appear on row 2 and **do not
  move before row 24**. Boss HP `$66` = 16, shared. Ryu x 32 y 208 at control (fixed by the stage load).
* J&S spin (`spin_hit`): -(XR+8) < ex - rx < XR+12 and ry - ey <= 24 -> Ryu's feet must be at y <= 184, i.e. 7 rows
  after the jump press (y 208, 204, ..., 185, 182). The spin then hits **1 HP per frame** -> kill = first hit + 15 =
  **jump row + 22**. Only dog 7 is in reach (dog 6 is 114 px away), so 1 HP/frame is the maximum.
* **A on the control row does NOT jump** (Mesen and NesHawk: A+Left / A on row 1 -> no jump, and holding it on row 2
  gives no jump either; it needs a fresh press on row >= 2). So the earliest jump is row 2 and **the kill floor is row
  24 (control + 23)**. Grid (`grid.py`, 1,152 legal candidates: control-row input x jump row 1-4 x A hold 2/6 x air
  direction x B row x B direction, Enforcer-legalized): best kill row 24 (56 candidates), none earlier. B on any row 3-8
  gives row 24; the B direction does not matter.
* Rows (`k44_d0.txt`): `Left` (control row), `A+Left`, `A+Left`, `-`, `B+Right`, `B+Right`, blank ..., `Start` x2 on
  rows 618-619, blank to row 772. Legal (= `4-4_p2`'s pattern, which passed the judge). Ryu ends standing in the spin
  at y 160; no hit is taken (works with hp 1).
* Ninpo: **+10 = same kill, +15 f at the tally** (a 2nd B during the spin spends nothing: np 10 -> 5 stays; the extra 5
  can only be burned in 4-3). **+0 = sword only: best found kill 21,464 = control + 111 = +88 f** (`ng.solve.boss` with
  `$64` poked 0, NesHawk, 0.4 h, width 4: `states/tmp/a56r2_tk_4-4_np0.inputs.txt`; not a proven floor). So a missing 5
  costs ~88 f, an extra 5 costs 15 f.

### Arrival dependence (Mesen `bfscan.py`, NesHawk spot checks)

* **`$BF`: none.** p2-pattern rows with `$BF` poked to every value 0-255 at the pre-control row: all 256 give kill row
  24, timer 149, load row 621, 5-1 control row 773. NesHawk with `$BF` 130 / 7 / 250 / 66: same rows.
* **HP: none** (hp 1 / 2 / 5 / 16 identical). Ryu's x/facing at control are fixed by the stage load (l43p: Left held
  before the control row changes nothing). Ninpo: see above. Score: irrelevant.
* `$BF` at the 5-1 control row = (`$BF` on the 4-4 pre-control row + 3 + extra rows) mod 256 (two frames of the
  transition do not count). `$62` through the act-end transition = (v - 24 - d) mod 61 (frozen one row after the kill, d = jump delay; TAS 59), and 5-1 counts down from it.

### Timer tick: what 4-3's exit frame should catch

* v = **`$62` on the 4-4 control row = its value on the 4-3 trigger frame** (`$62` stops on the frame before the trigger
  and is frozen through the 279-row transition; TAS: 22). In 4-4 it decrements from row 2; the timer ticks (`$63` 150 ->
  149) on row v + 2. The tally reads the timer **one row after the kill** (the row after the kill still ticks), so the
  kill on row 24 collects the tick when **v <= 23**.
* Measured (Mesen run_batch = NesHawk; `graft.py --test`, NesHawk `nh44.py`): 4-4 rows (5-1 control row - 1)

| v | best rows | 4-4 | template |
|---|---|---|---|
| 0-23 | jump row 2 (kill row 24, timer 149) | **772** | `k44_d0.txt` |
| 24 | jump 1 row later (blank on row 2; kill row 25 on the tick) | 773 | `k44_d1.txt` |
| 25 | jump 2 rows later (kill row 26) | 774 | `k44_d2.txt` |
| 26-60 | jump row 2, timer 150 | 775 | `k44_t150.txt` |

* **For 4-3: compare exits by trigger + min(3, max(0, v - 23)).** Each frame 4-3 saves raises v by 1, so a gain that
  pushes v from <= 23 into 24..26 is worth nothing (and 1-2 f slower exits that bring v from 24-26 down to 23 are free).
  On k932b: v = (`$62` at the trigger), read it with Mesen (`$62` = 0x62) on the trigger frame.

### Transitions

* **4-3 -> 4-4:** control = trigger + 279 (NesHawk, l43p); Start does nothing; nothing moves Ryu before the control row;
  the 4-3 file ends at the trigger, rows trigger+1 .. trigger+278 blank, 4-4 row 1 = Left on trigger + 279.
* **4-4 -> 5-1 (act-end cutscene):** earliest Start = **kill + 147 + 3 x timer** (= kill + 594 with timer 149; a press
  one row later gives the same load; one row earlier is ignored, and a Start held across that row blocks the next
  frame's press: it must be a fresh press). Load = kill + 150 + 3 x timer (NesHawk). 5-1 control = kill + 302 + 3 x timer (kill +
  749), measured on NesHawk with kills on rows 24-27 (no phase dependence). **Mesen's `step()` accepts the Start 1 row
  earlier and loads 2 rows earlier than NesHawk; Mesen `run_batch` matches NesHawk: use run_batch or NesHawk here.**
* **5-1 control row:** first row on which Right moves Ryu (x 64 -> 65) = first `$62` change; **Right held from 22,100
  (or any earlier row) moves him on the same row: no free frames.** The 4-4 stage file ends one row before it; 5-1's
  row 1 = Right.

### Graft onto a 4-3 candidate (ready)

`python work/l44p/graft.py <4-3 power-on rows> <Mesen state on its path> <state frame> <tag>`: plays to the trigger,
keeps the rows to the trigger, blanks to trigger + 278, reads v, picks the template, checks kill / 5-1 control with
run_batch, writes `logs/l44p_<tag>.inputs.txt` (4-4 stage rows) + `logs/l44p_<tag>_poweron.inputs.txt`, runs the judge.
Tested on the TAS path (trigger 21,074 -> control 21,353, v 22, kill row 24, 5-1 control 22,125). Then confirm on NesHawk
(`python -m ng.solve.verify chain ...`). No 4-3 candidate reached the trigger yet (2026-10-26 04:20), so nothing grafted.

## Next: 5-1 plan (prep agent l51p, 2026-10-26)

5-1 is one room (22), run right X 65 -> 3,036. **Headline: the TAS's whole 5-1 trick set has legal versions except the
two wall climbs; a legal line should land near TAS +25..+40 = record -115..-130.** The tosser-1 gate (the "5-1 manip")
works for ~80 % of arrival values at TAS +2. There is a 16-frame band of bad arrivals (table below), and a deliberate wait
skips it. Tools and data are in `work/l51p/`:
* `dumps.py` -> `tas51_ram.bin` (NesHawk TAS RAM, 22,126-24,525);
* `lib0.py` (dump reader `TM(f)`, `XY`) and `lib.py` (Mesen helpers);
* `slots.py` (Ryu + enemy slots per frame), `rle.py` -> `tas51_rows_rle.txt` (TAS rows with LR / UD / 1-f flags), `tas51_ev.txt`
  (spawn / hit / ninpo events), `reccmp.py` (record vs TAS per X), `dmap.py` (collision map from the dump);
* `mkst.py` -> Mesen TAS states `states/mesen/l51p_tas<f>.mst` (f = 22124, 22125, 22200, 22280, 22300, ... 24147; 0 RAM diffs
  vs NesHawk);
* gate tools `gate.py` / `gate2.py` / `pscan.py` / `sink.py` / `jenum.py`, beam `b51.py` (`--tas S --tpre P` starts from a TAS
  state with `$BF` poked), NesHawk `nhpre.py` / `nhsec.py` / `nhsec2.py` (`--bf` list) / `nhwall.py` / `nh_trans.py` / `nhtrace.py`.

Frames are power-on rows (NesHawk frame k = after row k), on the TAS axis unless noted. **c = `$BF` after the 5-1 control row
= (F - 23) mod 256**, where F = our 5-1 control row (TAS 22,125 -> 86).

### Splits

* **TAS 5-1 = 2,302 rows**: control row 22,125 -> trigger 24,148 (`$5C` 2 -> 0, the frame after Ryu reaches X 3,036 y 208)
  -> 5-2 control 24,427 (= trigger + 279).
* **Record 5-1 = 2,460.0 f** (`record_events.json`: control cum NES 22,668.3 -> 25,128.3, +-3) = **TAS +158**.
* Record pace: **5-2 control <= F + 2,460, i.e. trigger <= F + 2,181.**

| X (TAS frame) | record - TAS (cum) | record loses | where / why (TAS line) |
|---|---|---|---|
| 0 -> 448 (22,386) | +6 | +6 | start (+-3 calibration), small |
| 448 -> 480 (22,408) | +76 | **+70** | **tosser-1 body boost**: TAS hp 16 -> 15 at 22,375, launched onto the pillar top (X 416-447, y 128) on 22,389. The record climbs instead |
| 480 -> 1,408 | +81 | +5 | tosser 2 (X 1,152-1,216, ~+10, then partly regained) |
| 1,472 -> 1,504 (23,115) | +129 | **+48** | **the X-1,504 wall**: TAS bird boost 23,081 (hp 15 -> 12) + an L+R climb to y 96. The record uses a two-wall chimney (pillar X 1,440-1,471 / wall X 1,504, both tops y 96) |
| 1,504 -> 2,112 | +128 | 0 | |
| 2,112 -> 2,304 | +145 | +17 | tosser 3 (spawns at X 2,242 y 128) area |
| 2,304 -> 2,752 (23,963) | +159 | +14 | TAS bird boost 23,714 (X 2,402, hp 12 -> 9) onto the top route; 2 Windmill throws (23,743 / 23,778); health X 2,565 (9 -> 15); bird boost 23,905 (X 2,679, hp 15 -> 12) |
| 2,752 -> end | +158 | 0 | |

### TAS rule breaks in 5-1, split into legal and banned parts (all tested)

| TAS rows | what the TAS does | banned part | legal version (measured) |
|---|---|---|---|
| 22,125-22,126 | Right on the control row, released 1 f | 1-f release | **blank control row, Right from row 2 = the TAS's positions exactly** (Mesen: 0 differences to 22,288). Holding Right from row 1 is 1.5 px ahead, and the TAS's later rows then get hit at 22,317 / 22,377 (`scan1.py R`). An R-based line would need its own sink and jump timing (untested) |
| 22,289 | **1-f Left right after tosser 1 spawns (22,288): this is the "5-1 manip"**. With Ryu's run stopped for that frame, tosser 1 sinks into the pillar (y 128 -> 136); only then can Ryu's jump hit its body | 1-f Left + 1-f Right release | **Left x2 on 22,289-90** (tosser y 138) or blank x2 on 22,290-91 (y 136). Stops before the spawn do nothing (y <= 132), and Left x4 drops the tosser to the floor (`sink.py`). Then A+Right on 22,357-58 (TAS 22,356) -> body hit 22,374 (hp 15) -> on the pillar top 22,388 (TAS 22,389) -> **X 600 on 22,490 = TAS +2** (head start below) |
| 22,793 | 1-f Left in the air (X 1,055) | 1-f | **Left x2 on 22,793-94** (NesHawk). Without the turn (Right, or blank x2) Ryu misses the landing and falls into the pit at X ~1,125. With it, the wall bird hits 3 f later (23,084, X 1,484 y 164) |
| 23,056 | A+L+R jump, 1 f | L+R | legalized (A+Right 2 f) inside the 22,793 test: no divergence before the wall bird |
| 23,081-23,126 | bird hit from behind -> clings to the wall X ~1,499 y 132 -> 1-f A+L/A+R + 15 f of L+R up and over the top | L+R, 1-f, period < 5 | Our legal hit (23,084) comes from the FRONT and puts Ryu on the **pillar's right face** (X 1,480 y 149, 23,089). Single-wall climb `[A+Right x2, Left x6] x3` up the pillar, then A+Right off its top -> **X >= 1,530 y <= 100 on 23,146 = TAS +13** (TAS 23,133; `nhwall.py`, 738 variants; two-wall chimney cycles never got above y 125). The record pays +48 here |
| 23,280 | A+L+R jump, 1 f | L+R | **A+Right one frame EARLIER (23,279-80) = the TAS exactly by 23,400** (NesHawk). A on 23,280/81 does not jump, and Ryu falls into the pit at 23,310 |
| 23,743 / 23,778 | Up+B 1 f (Windmill throws at the birds) with Right released 1 f | 1-f holds / release | Up+B x2 with Right released 2 f. **The throws are needed**: without them a bird hits at 23,775. Ryu ends 1 px behind the TAS, and at the 23,905 boost spot the TAS rows get Ryu hit early and pinned (dead). **Beam from TAS 23,850 (`b_e23.txt`): X 2,760 on 23,978 = TAS +15, hp 12** |
| ~75 rows | 1-f A/B | 1-f | 2-f holds (Enforcer). Legal TAS rows from the TAS state track exactly 23,127 -> 23,730, incl. the 23,714 bird boost |
| - | U+D | none in 5-1 | - |

Estimate for a full legal 5-1: +2 (start / tosser 1) + ~1 (tosser 2) + 3 (wall bird) + 10 (pillar climb) + ~15 (23,905
spot) = **TAS +25..+40, about record -120**. Not yet chained end to end; the end (X 2,760 -> 3,036) is TAS pure run +
slashes, untested legally.

### The tosser gates (`$BF`)

* **Tosser 1** (type 2) spawns on 22,288 at (421, 128) on the pillar top, when Ryu reaches X 308. Its first throw comes
  `$BF >> 1` frames after the spawn (`thrower` $C33C). Spawn BF = c + 163 (TAS 249: delay 124, so no throw before the boost).
* Method: TAS state 22,124 with `$BF` poked to c - 1, then the head-start rows (blank row 1, Left x2 sink, jump 22,357,
  legal TAS rows after it). **All 256 c values** were run (`pscan.py`; `gate2.py` re-searched jump frames 22,356-60 and
  both sinks; `gate.py` also tried waits up to 22,440 on samples). Cost = frame at X 600 vs the TAS's 22,488.

| 5-1 control F (window) | c | tosser-1 cost |
|---|---|---|
| 22,380 - 22,387 | 85 - 92 | **+2** (head start as is) |
| **22,388 - 22,403** | **93 - 108** (spawn BF 0-15: immediate axes) | **BAD: no boost found** (jumps to 22,440, both sinks, pillar wall-climb grid `climb1.py`, beams). Expect a record-like climb, +40..+70. AVOID |
| 22,404 - 22,456 | 109 - 161 | alternating: **+2 when c in {109, 111, 114-115, 118-119, 122-123, 130, 132-133, 136-137, 140-141, 144-145, 148, 150-151, 154-155, 158-160}**; 126-127 = +19; the rest = bad (no boost found) |
| 22,457 - 22,489 | 162 - 194 | **+2** |
| 22,490 - 22,505 | 195 - 210 (except 200 = +2) | +19 with the fixed rows (boost works; the axe costs later); not re-searched, probably less |
| **22,506 - 22,643** | 211 - 255, 0 - 92 | **+2** |
| **22,644 - 22,659** | 93 - 108 | **BAD** (as above) |
| 22,660 - 22,712 | 109 - 161 | alternating, as above |
| 22,713 - | 162 - | +2 |

  The pattern repeats every 256 f (F and F + 256 behave the same).
* **To get a better c, wait before 5-1 control.** A later 4-4 Start delays the 5-1 load and control 1:1 and changes
  nothing else in 5-1. So from a bad c, wait k frames to the next good value (cost k). Shifting inside 5-1 is NOT
  equivalent: delayed or advanced copies of the head start (`shift.py`) get hit by the pre-tosser walkers (22,277 / 22,390).
* **Tosser 2** spawns on 22,829 at (1,222, 176). Spawn BF = c' + 192, where **c' = c + our lag vs the TAS at X ~1,100**
  (the head start is +2). The legalized TAS rows pass with no hit only for **c' = 70, 80-104, 108, 112-122** (NesHawk, even
  c' only, from the TAS state). **For other c' a beam repairs it at TAS +1, hp 15** (c' 40 and 160: X 1,300 on 22,958 vs
  TAS 22,957; `b_t2c40.txt`, `b_t2c160.txt`). So tosser 2 costs about 1 f; no need to plan around it.
* **Tosser 3** spawns on 23,532 at (2,242, 128). Spawn BF = c'' + 127, where c'' = c + lag there. The legal TAS rows pass
  (TAS-exact incl. the 23,714 bird boost) for most c''. They are **hit at c'' ~ 241-0 and ~145-165** (NesHawk, step 4);
  those need a local repair (cost not measured; the record loses ~17 here).
* Bird boosts (22,793 setup, 23,081, 23,714, 23,905) depend on the line, not directly on `$BF`.
* **Advice for 4-3 / 4-4: avoid F = 22,388-22,403 and 22,644-22,659 (+256k); inside 22,404-22,456 / 22,660-22,712 check
  the exact c. Everything else costs nothing at tosser 1.** Sweet spot (both gates on the TAS rows): **c 78-92 = F
  22,629-22,643**.

### Ninpo / art / HP (Act V: 5-1 -> 5-4)

* Lanterns (`python -m ng.solve.items 5-1`), all on or next to the TAS line:
  * +5 X 304 y 160 (TAS slash 22,274);
  * +5 X 368 y 160 (22,318), with the **Star X 368 y 96** 64 px above it (do not hit it);
  * +10 X 592 y 96 (22,468);
  * **Windmill X 736 y 160 (22,567: take it)**;
  * +5 X 864, +5 X 944 (22,655 / 22,718);
  * FW X 1,376 y 112 (**TRAP for 5-1**: it would replace the Windmill that the two required throws at X 2,438 / 2,489 use);
  * +10 X 1,648 (23,199);
  * Windmill X 2,176 (harmless);
  * **health X 2,576 y 80 (23,829, +6)**;
  * +10 X 2,976 (24,095).
  * Points lanterns: 500 X 528 / 1,040, 1000 X 656 / 1,168 / 2,752.
* TAS: 0 -> 50 picked up, 2 Windmill throws (-10) -> **exits W/40, hp 12**. The record exits W/45. The head start has np 20
  at X 600 (= TAS).
* **Target: exit 5-1 with any art and 40 (min 30; 45 only if a throw can be dropped).** Why: 5-2 is net 0 on the TAS
  (+5 +5 +5 +10 in lanterns, 5 spins incl. the spin-breaks) and gives the **J&S at room 23 X 144, the only one in Act V**.
  5-3 is the big spender: TAS 11 spins (55), +20 in lanterns -> exactly 5 for 5-4; the record entered 5-3 with 55. Extra
  ninpo is burnt by spins in 5-3; too little forces sword kills there. 5-3 must exit J&S + exactly 5; TRAP: InvFW room 29
  X 144. 5-4 = one spin (`5-4_b13`).
* HP: 5-1 starts at 16 (act refill). It carries 5-1 -> 5-2 -> 5-3 (the TAS starts 5-3 with 3!), and refills at 5-4.
  * TAS 5-1: 16 -> 15 (tosser 1) -> 12 (wall bird) -> 9 (bird 23,714) -> 15 (health) -> 12 (bird 23,905).
  * Our legal pieces take the same hits (the wall bird from the front still costs 3), so expect an exit with 12.
  * Every extra hit in 5-1 is a boost lost in 5-2 / 5-3.

### Transitions

* **4-4 -> 5-1**: as `Next: 4-4 plan`. 5-1 control = kill + 302 + 3 x timer; the earliest Start is kill + 147 + 3 x timer
  (a fresh press). **New: the 5-1 stage rows should start with a BLANK control row and Right from row 2.** That gives the
  TAS's positions exactly, and the tosser-1 manipulation and the head start are built on it. Right on row 1 is 1.5 px
  ahead and is untested with a re-timed sink. A later 4-4 Start = a pure 5-1 delay (to change c).
* **5-1 -> 5-2 (plain stage change, no cutscene; Mesen run_batch + NesHawk `nh_trans.py`)**:
  * trigger = first `$5C` 0 = the frame after Ryu reaches X 3,036 (TAS 24,148);
  * load (`$6D` 13) = trigger + 128;
  * **5-2 control = trigger + 279** (Left moves x 180 -> 178 there; TAS 24,427).
  * Left held from any earlier row = the same frames. Start anywhere from the trigger to control does nothing. **No
    free frames.** End the 5-1 rows at the trigger; the 5-2 row 1 = Left on trigger + 279.
  * `$BF` at 5-2 control = (F - 23) mod 256.

### Head start (verified)

* **`work/l51p/pre51_22490.txt` = 366 5-1 stage rows (row 1 = 5-1 control row, blank): X 600 on row 366 (TAS axis 22,490 =
  TAS +2), hp 15, np 20, no art yet.** It contains:
  * blank, then Right;
  * the TAS's legalized rows (2-f A/B), with Left x2 on 22,289-90 (the sink);
  * A+Right on 22,357-58, the tosser-1 body hit 22,374, on the pillar top 22,388;
  * legal TAS rows (lag +1) to X 600.
* `check_inputs.py --period 5 --hold 2 --release 2 --windows 600:109,1800:246`: PASS.
* **NesHawk = Mesen** (`nhpre.py`, ref4751/11_4-4_control + TAS rows to 22,124 + `$BF` poke): c 86, 0, 40 and 250 all reach
  X 600 on 22,490, hp 15, np 20. c 200 does not (it needs the jump on 22,359, as `gate.py` found); c 93-108 fail (table).
* Arrival-independent for every "+2" c in the table. Graft: rows 1..366 after our real 5-1 control row (blank row 1).

* **Chain test beyond the head start (Mesen, c 86):** legal TAS rows at lag 1/2/3 after the head start are hit at X ~881
  (TAS-axis 22,677: the X-773 bird spawned 22,656, sub-pixel / slot history differ) and die at X ~1,011.
  * Beam repair from row 516 (`b51.py --prefix work/l51p/chain_l2.txt --npre 516`): **X 1,000 on 22,764 = TAS +2, hp 15,
    but np 20** (it skips +5 X 864 / X 944; `b_r880.txt`).
  * **With both +5s: 22,773 = TAS +11, np 30** (`b_r880n.txt`).
  * So those two lanterns cost ~9 f on our line. The ninpo can be taken there, or the 5-1 exit target lowered to 30 (still
    >= the minimum).

### Next steps for the 5-1 solver (by value)

1. Chain the pieces on the real arrival:
   * the head start;
   * legal TAS rows (lag ~+2) through tosser 2, re-beamed if hit (`b51.py`);
   * Left x2 at TAS-axis 22,793;
   * the wall bird and the pillar climb (`nhwall.py`: `[A+Right x2, Left x6] x3`, then A+Right);
   * TAS rows (A+Right one frame early at 23,279);
   * the 23,714 bird boost, 2-f throws;
   * the 23,905 spot (beam);
   * the run to X 3,036.
2. Better wall: the climb starts 3 f late because the bird hits from the front; a 22,793-area variant that keeps the
   bird behind Ryu could save up to ~10 f.
3. The 23,905 spot (+15): search jump/throw timing so the bird boost lifts Ryu to y 128 at X ~2,694 like the TAS.
4. If 4-3/4-4 can only deliver a bad c: wait for a good c (cheapest), else search the bad band with a wider beam.

## Next: 5-2 plan (prep agent l52p, 2026-10-26)

5-2 = rooms 23 (runs LEFT), 24 (right), 25 (left), 26 (right). Every room starts at the bottom of an entry shaft and ends with
a climb to an exit tile near the top. **Headline: the TAS's 5-2 is ~70 % run + a few wall climbs; its banned inputs sit
almost entirely in the climbs (U+D "wall wobble", L+R mid-air moonwalks, 1-f A+L/A+R taps). The room-26 thrower is the
only `$BF` reader in the stage. The record loses +277, about +72 / +82 / +34 / +89 per room, nearly all of it at the room
entries and exits.** A verified, arrival-independent legal prefix of room 23 (199 rows, = TAS positions) is ready.
Tools and data in `work/l52p/`:
* `dumps.py` -> `tas52_ram.bin` (NesHawk TAS RAM, 24,429-26,828; `lib0.TM(f)` also reads l51p's 5-1 dump below 24,429);
* `ev.py` -> `tas52_ev.txt` (rooms / hp / ninpo / item / spawns), `rle.py` -> `tas52_rows_rle.txt` (TAS rows, LR / UD / 1-f flags),
  `slots.py f1 f2 step`, `roommap.py f1 f2` (whole-room collision map from the dump);
* `mkst.py` -> Mesen TAS states `states/mesen/l52p_tas<f>.mst` (24,300 ... 26,607, 0 RAM diffs vs NesHawk); `lib.core_at(f)` = any TAS frame;
* `tf.py` (follow legalized TAS rows, first divergence), `b52.py` (beam from a TAS state, goal / score expressions),
  `climb.py` / `cyc.py` / `en23.py` / `en23x.py` (wall-climb grammars; `cyc.py` = every cyclic legal A/L/R pattern),
  `bf26.py` (thrower `$BF` scan), `pre52.py` + `nhpre52.py` (prefix, Mesen junk/`$BF` test + NesHawk), `nh_trans53.py` (5-2 -> 5-3).

Frames are power-on rows on the TAS axis (NesHawk frame k = after row k). **TAS 5-2 control row = 24,427** (Left; note
`ref4751/13_5-2_control` is frame 24,428 = after row 24,428). `$BF` = (f - 23) mod 256 on every frame of Acts 5 (checked at
22,125 / 24,427 / 26,608).

### Splits (room change = first frame with the new `$6E`; record = first picture after the 22-f black, so TAS + 22 for rooms)

| | TAS frame (t) | TAS first picture | record t (first picture) | room: TAS | room: record | record loses |
|---|---|---|---|---|---|---|
| control (room 23) | 24,427 (0) | - | 0 (cum NES 25,128.3) | | | |
| room 24 | 24,874 (447) | 469 | 541 | 469 | 541 | **+72** (room-23 exit) |
| room 25 | 25,361 (934) | 956 | 1,110 | 487 | 569 | **+82** (entry chimney ~+48, exit climb ~+26) |
| room 26 | 25,818 (1,391) | 1,413 | 1,601 | 457 | 491 | **+34** (entry / exit climbs) |
| 5-3 control | 26,608 (2,181) | - | 2,458 | 768 | 857 | **+89** (entry ~+20, two bird boosts) |
| **5-2 total** | **2,181** | | **2,458** (+-3) | | | **+277** |

Record pace: **5-3 control <= F + 2,458** (F = our 5-2 control row), i.e. trigger <= F + 2,179.
TAS events: +5 lantern 24,564; J&S 24,820 (X 130 y 99); trigger (`$5C` 0) 26,329; hits 25,641 (bullet, 12->11),
25,791 (bullet boost over the room-25 exit wall, 11->9), 26,061 (bird boost, 9->6), 26,303 (bird boost into the exit, 6->3).

Where the record loses, and why (record trace `work/a56r2/rec/r52.json`, video y + 9 = RAM y):
* **Room 23 exit (+72)**: the TAS climbs the X-96 wall's right face with U+D+L (24,821-873) and walks over its top
  (above y 72 no wall checks run: `touch_walls` $E677 returns when Ryu's y < $48), straight into the exit tile (X 48-63,
  y 64-79). The record walks the floor to the left shaft and climbs the X-48 column's left face (~60 f of climbing).
* **Room 24 entry (~+48)**: TAS L+R climb out of the entry chimney (24,899-938); the record (and our r4 hand line) uses wall
  jumps between X ~24 and ~44. **Room 24 exit (~+26)**: the TAS climbs X ~665 at 2 px/f with 1-f A+L / A+R taps (25,337-360).
* **Room 25 (+34)**: entry climb (same tap pattern, 25,385-394); the exit is a bullet damage boost (25,791) over the wall + 12
  U+D+L frames; the record climbs.
* **Room 26 (+89)**: the TAS jumps off the entry ladder and moonwalks right with L+R (25,860-890) UNDER the ledge, climbs the
  X ~90 wall with taps and runs right (X 127 at ~25,942 = control + 101). **The record climbs the ladder to y ~190, wall-jumps
  to the left wall, goes OVER the ledge at y ~110-150 and drops to the floor: X 127 at entry + ~122 (only ~+20; legal).**
  Then the TAS's bird boosts at 26,061 (onto the thrower ledge, with 18 f of L+R while knocked back) and 26,303 (into the
  exit) - the record loses ~+70 over the rest of the room.

### TAS rule breaks in 5-2, split into legal and banned parts (tested where marked)

| TAS rows | what the TAS does | banned part | legal version / status |
|---|---|---|---|
| 24,427-24,625 | run left, 2 jumps, +5 X 480 (slash 24,563) | 1-f A/B only | **legalized TAS rows (2-f A/B) = the TAS positions exactly (Mesen + NesHawk)**: prefix below |
| 24,626-24,661 | 1-f L+R in the air at X 395 y 146, A+Left, then a 1-f A+Right at the corner (X 377 y 130) and 21 f of U+D+L (moves left while facing right) onto the y-128 ledge | L+R, U+D, 1-f | **beam `b_r23a.txt` (from 24,600): X <= 304, y <= 128 on 24,701 = TAS +12** (TAS 24,689), hp 12 np 45. Narrow grammars (`en23.py`, 3,471 cases) found nothing faster |
| 24,662-24,812 | run, jumps, the high arc over to the X-96 wall | 1-f A/B | not tested past +12 (legal TAS rows should follow at lag 12; check the X-773-style walker phase) |
| 24,813-24,820 | 1-f taps on the wall, slash (24,817) + J&S pickup 24,820 | 1-f A/L/R | untested (`b52.py` from 24,812 with goal `it==133`) |
| 24,821-24,873 | U+D+L climb of the X-96 wall face, over its top at y 57-70, into the exit (X 71 y 72) | U+D, 1-f | **not reproduced legally**: three beams from 24,820 (`b_x23*.out`, up to 220 f) reach X 104-111 at y 57-65 and stall (Ryu stays stuck to the wall: its touch flags are not refreshed above y 72). `en23x.py` tests "climb, then jump AWAY to clear the flags, then Left over the top": no exit in 4,638 legal cases (the jumps away fall to the floor; best = the left shaft at X 23, i.e. the record's line). Fallback = the record's line (floor, X-48 column) = r4_52_h2: room 24 on 24,982 = **TAS +108** (record ~+72) |
| 24,897-24,938 | room-24 entry chimney: L+R climb | L+R, 1-f | r4_52_h3 hand line (5 C8 on the right wall, hop left, 1 C8, over): x 75 on TAS-room-24 +116 f vs TAS +67 = **~+49** |
| 25,337-25,360, 25,385-25,394 | climb at 2 px/f: A pressed every 5 f (legal), Left / Right 1 f each | 1-f L / R | **room-24 exit: legal 5-f cycle `[Right, Right, Left, A+Left, A+Right] x 6` from 25,335 (Right held 3, Left 2, A 2 per 5 f), then Right -> room 25 on 25,367 = TAS +6** (`cyc.py`, 2,184 legal patterns; `cyc_r24x.out`; 3 presses / 5 f, so mind the 600-f window). Room-25 entry (from 25,384, goal X <= 600): no pattern + Left tail reached it within 90 f (`cyc_r25e.out`, 792 cases) - needs a beam |
| 25,641 / 25,791 | bullet hits (25,791 = the boost over the exit wall), then 12 f U+D+L to the exit | U+D | the boosts are legal (no banned input); U+D -> Left untested |
| 25,860-25,890 | room-26 entry: A+Left off the ladder, L+R moonwalk right (facing left, so the ladder is not re-grabbed) | L+R | **legal TAS rows die (fall at X 41)**; a beam (`b_e26.out`, 140 f) only re-climbs the ladder (stuck at y 192). Use the **record's over-the-ledge line (~+20)** |
| 25,892-25,918 | wall climb at X ~90 with taps | 1-f | as the room-24 climb |
| 26,059-26,083 | bird boost (hp 9->6) at X 298; 18 f L+R during the knockback | L+R | knockback ignores the d-pad mostly; Right (or Left) should give the same flight - untested |
| 26,130-26,176 | jump + 43 f L+R in the air | L+R | Right should match (the moonwalk only matters next to a wall) - untested |
| 26,208-26,211 | 1-f U+D on a ledge edge | U+D, 1-f | untested |
| 26,297-26,303 | B+Down slash, bird boost into the exit (6->3) | 1-f | the boost is legal |

### Arrival dependence (`$BF`)

* Disassembly (bank07, every `lda/bit nmi_count`): in level stages only the **thrower** (type 2: throw delay `$BF >> 1`) and
  its **axe** (x fraction / speed from `$BF`) read it. 5-2's enemies: batters (3), waiting ghoul (16), birds (11), running
  ninjas (13), jump kickers (6), crouching soldiers (5) + bullets (20), bats (8): none read `$BF`. **The only `$BF`-dependent
  enemy is the room-26 thrower**: spawns on TAS 26,008 at (337, 128) (on the ledge the 26,061 bird boost lands on), throw
  delay = spawn `$BF` >> 1.
* **Rooms 23-25 and the room-26 entry are arrival-independent** (checked for the room-23 prefix: `$BF` 0..222 + junk enemy
  slots, Mesen; 0 differences).
* Thrower scan (`bf26.py`, Mesen, TAS state 25,990, all 256 `$BF`, the TAS's own rows): spawn `$BF` = (F + 22 + L) mod 256,
  where F = our 5-2 control row and L = our lag vs the TAS at the thrower spawn (X ~224 in room 26; TAS: F 24,427, L 0 -> 129).

| spawn `$BF` | throws | TAS rows |
|---|---|---|
| 1, 4, 7, 8, 11, 12, 14-16, 18, 21 | 1st axe at once, 2nd ~26,034-060 (the boost window) | extra hit (hp 2-7) |
| 3, 13 | same | **dead** |
| 52, 54-56, 58, 59 | one axe ~26,037-041 | **dead** (hp 6 on the TAS line) |
| 61 | | extra hit |
| **everything else (236 of 256), incl. 0, 2, 5, 6, 9, 10, 17, 19, 20, 22-51, 53, 57, 60, 62-255** | | **= TAS** (trigger 26,329) |

  So: **avoid spawn `$BF` 0-22 and 52-61**, i.e. avoid (F + L) mod 256 in 234-255 / 0 and 30-39. With F in the expected
  24,850-25,100 and L unknown until 5-2 is solved, this cannot be fixed yet; it is a band of ~30 of 256 values on our line
  (re-run `bf26.py <F0> --rows <our rows>` from our room-26 state). If our value is bad, the cheapest fix is a k-frame wait **at the room-26 entry** (Ryu on the entry ladder, 25,841-25,858 on the TAS: room 26's enemies spawn by scroll and none is on screen yet, so only the thrower phase moves; untested). A wait at the end of 5-1 / before the 5-2 control also works (rooms 23-25 read no `$BF`) but is the same 1:1 cost and moves nothing else; waits in the middle of a room are risky (5-1 showed shifted rows get hit).

### Ninpo / art / HP

* Lanterns (`python -m ng.solve.items 5-2`): room 23: +5 X 480 y 144 (TAS, slash 24,563), 500 pts X 304, **+10 X 352 y 96
  (the TAS skips it; it passes X 352-362 at y 115-128 on 24,650-660: a slash there is in reach, pickup untested)**,
  **J&S X 144 y 112 (TAS 24,820, must take)**. Room 24: +5 X 320 y 96 (TAS breaks it with a spin at X 329 y 112, 25,111),
  **FW X 320 y 160 directly below it (TRAP)**, 1000 pts X 384, **Star X 512 y 128 (TRAP, on the line)**, 500 X 560. Room 25:
  +5 X 96 y 144, **Windmill X 224 y 128 (TRAP)**, 1000 X 288, 500 X 416, **InvFW X 448 y 96 (TRAP)**, +5 X 480 y 160 (TAS).
  Room 26: health X 256 y 80 (+6, the TAS skips it), 500 X 320, 1000 X 448, +10 X 560 y 96 (TAS spin-break 26,254).
* TAS: W/40 in; +5 (r23), J&S (24,820), spin-break +5 (r24, 25,111), spins 25,479 / 25,611 with +5 (25,512) between (r25),
  spin 26,003, spin-break +10 26,254 (r26) -> **exits J&S/40, hp 3**. 5 spins = 25 spent, 25 picked up. The record: W/45 -> J&S/55.
* **Plan: enter with any art + 40 (5-1 target), take the J&S, exit J&S + 40-55.** 5-3 spends: TAS 11 spins (55) with
  +20 in lanterns, i.e. 5-3 needs entry = 5 x spins - 15. Our legal 5-3 is unsolved; the record entered with 55 (~10
  spins). Free extra ninpo in 5-2: +10 X 352 (room 23, near the TAS line) and +5 X 96 (room 25) -> up to 55. Spins in 5-2 are
  for kills / lantern breaks only; drop any spin our line does not need (each saved spin = +5 for 5-3).
* After the J&S pickup every slash/spin must miss the FW (r24 X 320 y 160), Star (r24 X 512 y 128), Windmill (r25 X 224
  y 128) and InvFW (r25 X 448 y 96): check `$C9` = 133 at the 5-3 control.
* HP: the TAS goes 12 -> 3 (four hits, all boosts). 5-3 has no refill and the TAS plays it on 3. Our 5-1 should exit ~12.
  The room-26 health (X 256 y 80) is an option if our 5-3 needs more hp (the record's route over the room-26 ledge passes
  near it: y ~110-150 at X 41-124; untested).

### Transitions

* **5-1 -> 5-2** (l51p, NesHawk): trigger = first `$5C` 0 = the frame after Ryu reaches X 3,036; load (`$6D` 13) = trigger
  + 128; **5-2 control = trigger + 279** (Left moves Ryu x 180 -> 178 on that row; TAS 24,427). Left held earlier = same;
  Start anywhere in between does nothing. No free frames: a "wait at the end of 5-1" is a real 1:1 delay (it changes F,
  hence the thrower band) and costs its length.
* **5-2 -> 5-3** (NesHawk `nh_trans53.py`, TAS path): trigger 26,329 (Ryu reaches the exit at X 667 y ~80, `$5C` 2 -> 0;
  the room-26 exit is the top right, X 688 y 64 tile 15); load (`$6D` 14) = trigger + 128 = 26,457; **5-3 control = trigger
  + 279 = 26,608: Left on that row moves Ryu (x 176 -> 174)**. Left from 26,330 / 26,400 / 26,607 = identical; Left from
  26,609 = 1 f late. **Right on 26,608 does NOT move him until 26,609** (he faces left; room 27 runs left anyway). Start at
  26,330 / 26,460 / 26,600 does nothing. **No free frames.** End the 5-2 rows at the trigger; 5-3 row 1 = Left on
  trigger + 279. `$BF` at 5-3 control = 217 on the TAS (= (f - 23) mod 256).
* Room changes inside 5-2: control resumes 23 f after the room change (TAS 24,897 / 25,384 / 25,841); the TAS's first rows
  there are taps / Up on the entry ladder or wall.

### Prefix (verified)

* **`work/l52p/pre52_24625.txt` = 199 5-2 stage rows (row 1 = the 5-2 control row 24,427 = Left): the TAS's room-23 rows
  with 1-f A/B held 2 f (Enforcer).** Ends at X 393 y 147 on 24,625, hp 12, np 45 (+5 X 480 taken), Windmill still held.
  It equals the TAS positions on every frame (Mesen and NesHawk `nhpre52.py`: 0 divergences).
* **Arrival-independent**: Mesen, from the 5-1 TAS state 24,147 with `$BF` poked to 0/37/74/.../222 and random junk in the
  enemy slots `$400-$4A7`, then TAS rows to 24,426 + the prefix: identical positions, hp, ninpo in all 8 trials (no thrower
  in room 23). It needs the 5-1 exit to land on the TAS's 5-2 start (x 180 y 128, Windmill, any ninpo); 5-2's start
  position is fixed by the room load.
* Legality: `legal_ok` with the TAS's previous 150 rows (legalized) as history; re-judge with our real 5-1 rows (the 600/1,800
  windows cross the stage boundary).
* Continuation: `b_r23a.txt` (rows from 24,601; = prefix rows to 24,625 + beam) reaches X <= 304 on the ledge at 24,701 = TAS +12.

### Next steps for the 5-2 solver (by value)

1. **Room-23 exit (record +72, ours +108 on r4_52_h2)**: the TAS's over-the-wall exit is not reproduced legally (beams + `en23x.py`; the key fact: above y 72 no wall check runs, but a wall-clinging Ryu keeps its stale wall flag, so the way over needs Ryu to arrive above y 72 at X ~110 WITHOUT having touched the wall below y 72 - e.g. a jump from the y-96 platform (TAS 24,767) aimed higher/later, or a wall jump off the X-96 face that first moves right and only then rises; not found yet). Otherwise improve the record's line (walk the floor, climb the X-48 column's left face, enter the exit from the left): record ~+72, our r4_52_h2 +108, so ~36 f are there
2. Room-26 entry: copy the record's over-the-ledge route (~+20; ladder to y ~190, jump to the left wall, over the ledge at
   y ~110-150, drop to the floor at X ~127); beam it from 25,840 with a record reference (`work/a56r2/mk_recref.py`).
3. Room-24 entry chimney (r4_52_h3, ~+49) and the 2-px/f climbs (24 exit, 25 entry, 26 X ~90): the room-24 exit pattern above (+6) should carry to the other tap climbs (room-25 entry, room-26 X ~90); search them with `cyc.py` + a jump tail / `b52.py`. A better room-24 chimney than r4_52_h3 (+49) is worth a beam.
4. Room 26 after the entry: legalize the bird boosts (26,061 / 26,303) with Right instead of L+R during the knockback; check
   the thrower band with our real F.
5. Take +10 X 352 (room 23) if it costs < ~15 f (it is worth 5-3 spins).

## Next: 5-3 plan (prep agent l53p, 2026-10-27)

5-3 = rooms 27 (runs LEFT), 28 (right), 29 (left), 30 (right), 31 (left), 32 (right), 33 (short run right into 5-4).
**Headline: 5-3 is three copies of one leftward room end and three copies of one rightward room start. The TAS's banned
inputs are almost all in those six places, plus one pit crossing in room 27. The leftward exits have a tested legal way
(+46 f per exit). The room-27 pit is the one open problem: the TAS's way across is provably not legal, and no legal way
has been found yet. The record crosses it, so one exists.**
Tools and data are in `work/l53p/`:
* `dumps.py` -> `tas53_ram.bin` (NesHawk TAS RAM 26,610-29,409); `lib0.py` (`TM(f)`, `XY`; falls back to the 5-1 and 5-2 dumps);
* `lib.py` (Mesen helpers, `core_at(f)`); `mkst.py` -> Mesen TAS states `states/mesen/l53p_tas<f>.mst` (65 frames
  26,607-29,099, 0 RAM diffs vs NesHawk);
* `ev.py` -> `tas53_ev.txt` (rooms, hp, ninpo, spawns); `rle.py` -> `tas53_rows_rle.txt`; `brk.py` (rule breaks as spans);
  `spins.py` (spins and kills); `slots.py`;
* `roommap.py` / `roommap0.py` (room collision maps, with / without the TAS path);
* `tf.py` (follow legal TAS rows); `b53.py` (beam); `diag.py` (one row spec, printed trace);
* `bf53.py` (thrower `$BF` scan); `spintest.py`;
* `axe31.py` / `axe31bf.py` / `axe31b.py` (room-31 axe-boost tests); `bird29.py` (written, not run);
* `pitgrid.py` (room-27 ladder test); `pre53.py` / `nhpre53.py` (head start, Mesen arrival test + NesHawk).

Frames are power-on rows on the TAS axis. **TAS 5-3 control row = 26,608** (Left; = 5-2 trigger 26,329 + 279).
**`$BF` at our 5-3 control row F = (F - 23) mod 256** (TAS: 217).

### Splits

Room change = the first frame with the new `$6E`. Record = the first picture after the 22-f black, minus 22 (`record_events.json`).
The record's control estimates are +-3 f at each end.

| room | TAS frames (room change -> room change) | record | record loses | TAS t at room end (from control) |
|---|---|---|---|---|
| 27 (left) | 405 (26,608 -> 27,013) | 514.8 | **+110** | 405 |
| 28 (right) | 472 (-> 27,485) | 512.9 | +41 | 877 |
| 29 (left) | 436 (-> 27,921) | 504.8 | **+69** | 1,313 |
| 30 (right) | 473 (-> 28,394) | 504.8 | +32 | 1,786 |
| 31 (left) | 235 (-> 28,629) | 304.5 | **+70** | 2,021 |
| 32 (right) | 215 (-> 28,844) | 234.4 | +19 | 2,236 |
| 33 + transition | 415 (-> 5-4 control 29,259) | 408.7 | -6 (timing noise; it is a plain run) | 2,651 |
| **5-3** | **2,651** | **2,985** | **+334** | |

* **Record pace: 5-4 control <= F + 2,985**, i.e. 5-3 trigger <= F + 2,826. The 5-3 -> 5-4 transition: trigger = `$5C` 2 -> 4
  when Ryu reaches X 380 in room 33 (TAS 29,100); hp refill to 16 on trigger + 7; room 34 load trigger + 8;
  **5-4 control = trigger + 159** (TAS 29,259).
* **Where the TAS gains (and the record loses):**
  * the three **leftward room exits** (rooms 27, 29 and 31 share one geometry: the wall X 96-127 with the exit tile
    'M' at X 96-111 y 64-79 on top);
  * the three **rightward room entries** (rooms 28, 30 and 32: the same entry shaft and ladder);
  * the **room-27 pit** (X 480-552). Per room, the record's losses are 110 / 69 / 70 in the leftward rooms and 41 / 32 / 19
    in the rightward rooms.

### TAS rule breaks in 5-3 (`brk.py`), split into legal and banned parts

The key code is in bank07:
* `touch_walls` $E677 returns at once when Ryu's y < 72, so no wall check, floor check or exit check runs above y 72.
* The exit check needs a touch point in an exit tile:
  * (X + 5, y - 5) or (X - 9, y - 5);
  * y >= 72.
* In the air, holding the direction he does NOT face gives 0.5 px/f (`drift_speed`).
* U+D+L (and L+R) choose `ctrl_idle`: no turn and no speed change, but `move_ryu` still steps Ryu at 1.5 px/f.
  So the TAS **moves against its facing at full speed**.
* A wall jump-off needs the pad to be exactly A+away ($81 / $82). It flips his facing away from the wall.

| TAS rows | what | banned part | legal version / verdict |
|---|---|---|---|
| 26,608-26,704 | run left, jump | 1-f A | **legal TAS rows = TAS positions exactly** (head start below) |
| 26,704-26,752 | **room-27 pit** (X 496-527 between the '1' pillar X 528-543 and the '21' block X 480-511, both without floor tops): wall jump-offs every 24 f off the pillar tops with **U+D+L for 47 f** (moves left 1.5 px/f while facing right) | U+D | **The TAS's way is not legal (shown from the code and by search).** A jump-off from a wall on his left must be A+Right, so he faces right. Moving left is then 0.5 px/f, about 10 px per bounce. The 16-px gap X 512-527 has no wall to bounce on, so drift falls into the pit. Two beams (`b_pit27.out`, `b_pit27b.out`, width 150) stall at the X-543 pillar. **Not solved:** a ladder climb of the X-672 column onto the y-112 platform (X 448-639) was tried. `pitgrid.py` ran 576 walk/jump/climb variants and beam `plat27` ran 120 f; neither ever rose above y 160. The record's trace is on that platform at y ~115 from ~t 141, and the record is only ~+17 here, so a legal way up exists. **First job for the 5-3 builders.** |
| 26,855 | spin (kills 3 t0) | - | needed (`spintest.py`: without it, or with a Down+B slash, hp 3 -> 2) |
| 26,937-26,966 | climb the '84' pillar's right face (X 200), U+D+L over its top (y 123-128) | U+D, 1-f | not needed on the legal exit (below) |
| 26,995-27,012 | **leftward exit**: A+Right jump-off from the X-128 wall at y 83, then **U+D+L 12 f above y 72** over the wall top into 'M' | U+D | **No legal version from the right side (proof from the code).** To reach the exit he must cross from X >= 137 to X <= 120 above y 72 (the '8' cap at X 112-127 y 64-79 and the '1' below block Left at every y 72-192). The tools: a normal jump from the nearest floor (the y-128 pillar top) peaks at y 80; a wall jump-off (vy -2, ~14 px) faces away, so Left is 0.5 px/f for about 12 f above y 72 (6 px). A hit while clinging is cancelled into a new cling the next frame (`axe31bf.py`: axes hit him on the face for many `$BF`; no exit). Hits in the air during the jump from the pillar top gave no exit either (`axe31b.py`, 992 BF x wait cases). **Legal exit = under the wall and up the ladder face from the left**: walk left along the floor under the wall (y 192 is open), climb the '9' ladder (X 96) with `[A+Left x2, Right x6]` cycles; the exit fires at y <= 84. **Beam `b_ex27b` (from TAS 26,900, X 254 y 208): room 28 on 27,059 = TAS +46, hp 3, np unchanged (0 spins).** Rows: `work/l53p/b_ex27b_h3n35i133.txt` |
| 27,037-27,063 (r28), 27,945-..., 28,653-... | entry ladder: taps (1-f A+L / A+R, 2 px/f) | 1-f | the 5-2 legal 5-f cycle (`cyc.py`, room-24 exit = TAS +6) or the `[A+Left x2, Right x6]` cycle; untested here |
| 27,065-27,097, 27,973-28,005, 28,681-28,713 | **rightward entry**: jump from the '84' top (y 192) with **L+R 33 f** = move right 1.5 px/f while still facing LEFT (he walked left onto the ledge; an A+Right press on the ground jumps without turning) | L+R | **legal: turn on the ground first** (Right >= 2 f, then A+Right): the same arc 1-3 f later. Untested; expect +2..+5 per room |
| 27,484, 28,393 | 1-f L+R on the exit ladder (X 667) the frame before the room change | L+R, 1-f | exit-ladder taps as above; +0..+3 |
| 27,838-27,848 (r29) | climb the col-14 wall's left face with A+Left taps + L+R | L+R, 1-f | `[A+Left x2, Right x6]` cycle; a few f |
| 28,568-28,582 (r31) | U+D+L over the '84' pillar top after the axe-boost hit at 28,564 | U+D | not needed on the legal (floor + ladder) exit |
| 28,617-28,628 (r31), 27,909-27,920 (r29) | leftward exits (same as room 27) | U+D | same verdict, same legal fix: **room 29 (beam `b_ex29` from TAS 27,800): room 30 on 27,975 = TAS +54**, hp 3, 2 spins (TAS 1); **room 31 (beam `b_ex31` from TAS 28,540): room 32 on 28,692 = TAS +63**, hp 3 (the TAS takes a hit here), 3 spins (TAS 0; the beam burns ninpo freely, so fewer should do). Rows `b_ex29_h3n10i133.txt`, `b_ex31_h3n0i133.txt` |
| ~150 rows | 1-f A/B, presses < 5 f apart | press cap | Enforcer (2-f holds) |
| - | U+D in the boss tally | - | not in 5-3 |

### Ninpo, spins, J&S (sets the 5-2 exit)

* 5-3 lanterns (ROM, 60 ninpo in total):
  * room 27: **FW X 192 y 112 (TRAP)**, +5 X 240 y 160, +10 X 320 y 80, +5 X 400 y 160;
  * room 28: +5 X 288 y 96 (TAS), +10 X 496 y 144 (TAS);
  * room 29: **InvFW X 144 y 80 (TRAP; on the TAS jump to the wall)**, +10 X 272 y 80, **Star X 496 y 160 (TRAP)**;
  * room 30: +5 X 336 y 112 (TAS), **Windmill X 464 y 96 (TRAP)**, **Star X 624 y 128 (TRAP)**;
  * room 31: +5 X 64 y 144, **FW X 240 y 80 (TRAP)**;
  * room 32: **FW X 256 y 160 (TRAP)**, **Windmill X 368 y 160 (TRAP)**, +5 X 416 y 112 (past the exit, unreachable).
* **TAS: 11 spins** (26,855 / 27,199 / 27,241 / 27,327 / 27,620 / 27,712 / 27,803 / 28,145 / 28,209 / 28,508 / 28,782). It
  picks up **+20** (27,202 / 27,340 / 28,150), so J&S/40 -> J&S/5.
  Three spins also break the lanterns (27,199, 27,327, 28,145). Every spin kills 1-4 enemies.
* `spintest.py` replaced each spin, on the TAS line, by nothing or by a plain Down+B slash. **Every one of the 11 costs a
  hit (hp -1/-2) or a death** (27,803, 28,508, 28,782 die). The test at 28,145 is inconclusive.
  So on a TAS-shaped line all 11 are needed. The legal exits change three places:
  * beam `ex27b` used 0 spins from X 254 to the exit;
  * `ex29` used 2 and `ex31` used 3, where the TAS used 1 and 0 (the beams spend freely).
  So **expect 10-12 spins**.
* Formula: **5-3 entry ninpo = 5 + 5 x spins - pickups**. With the TAS's pickups (+20) and 11 spins that is 40.
* Each extra lantern taken in 5-3 lowers the entry by its value:
  * +5 X 400 y 160 and +5 X 240 y 160 (room 27) hang 48 px over the floor the line runs on: a jump + slash costs ~0-6 f each;
  * +5 X 64 y 144 (room 31) is next to the legal ladder climb (untested).
* Each spin avoided lowers it by 5.
* **5-2 exit target: J&S + 40** (= 11 spins - 20 pickups + 5). 35 is enough if both room-27 +5s are taken; 45 gives one spare spin. Up to ~55 does no harm (burn the spare spins in the air). The best 5-1 candidate exits with 35, and the TAS's 5-2 is net 0, so **5-2 must gain +5 net**: the +10 X 352 (room 23), the +5 X 96 (room 25), or one 5-2 spin fewer.
* **Entering with too much is nearly free**: an extra air spin (any B in the air without Down) costs 0 f and burns 5. But it
  breaks lanterns in passing, so burn it away from the trap lanterns above.
* **Entering with too little** costs hits: on this line every spin's job is a kill that would otherwise cost hp. Each 5 short
  is one spin lost, i.e. roughly one hit.

### Arrival dependence (`$BF`)

* bank07 readers of `nmi_count` in level stages: only the **thrower (type 2)**. Its timer is `$BF >> 1`, re-read at every
  throw cycle. Its **axe (type 18)** takes x speed `$BF & 1` + `$BF`/256 and y frac `$BF`.
* Room 27 has no thrower. **The head start is arrival-independent** (below), except a possible slot-junk effect (see Head start).
* 5-3 throwers (TAS rows, `bf53.py`, all 256 values from a TAS state shortly before the spawn).
  Spawn `$BF` = (x + k) mod 256, where **x = (F + L) mod 256**:
  * F = our 5-3 control row;
  * L = our lag vs the TAS at that spawn;
  * the TAS has x = 240.

| thrower | TAS spawn (frame, pos, `$BF`) | k | TAS-equivalent spawn `$BF` | good x = (F + L) mod 256 | bad |
|---|---|---|---|---|---|
| room 28 #1 | 27,113, (258,144), 210 | 226 | 125-255 (131 of 256) | **155-255, 0-29** | x 30-154: an early axe hits (hp -1/-2, 11 values die) |
| room 28 #2 | 27,391, (674,176), 232 | 248 | 115-255 and most odd/even pairs below (189 of 256) | **123-255, 0-7** (+ scattered) | most x 8-122: an axe hits during the exit climb (hp -1) |
| room 31 | 28,491, (189,128) on the pillar top, 52 | 68 | 130-255 and 2, 14-15, 17, 42, 44, 47-48, 51-52, 55, 62-71 | 62-187 (+ a few) | the rest: the TAS's own axe boost (28,564) does not come. Our legal exit (floor + ladder) does not use it; re-scan with legal rows (`bf53.py F0 F1 FS --rows`) |

* The room-28 throwers are the real constraint. The two bands overlap at **x = (F + L28) mod 256 in 155-255 or 0-7**,
  ~109 of 256 values. Both spawn by scroll, so **a k-frame wait at the room-28 entry** (Ryu in the entry shaft, nothing
  spawned yet) shifts x by k at a cost of k f. That is cheaper than shifting the 5-2 exit.
* **No free frames at 5-2 -> 5-3** (5-2 prep: Left on any row from trigger + 1 to trigger + 279 gives the same control
  row; Start does nothing). The timer `$62` has no effect on the arrival. Any shift of F is a 1:1 cost.
* So **the 5-2 builders need not aim the exit for 5-3**. Fix the room-28 phase with a short wait at the room-28 entry
  once our L28 is known.

### Head start (verified)

* **`work/l53p/pre53_26704.txt` = 97 stage rows from the 5-3 control row (row 1 = Left on F).** It is the legalized TAS
  rows (1-f A held 2 f) and ends at **X 545 y 161 on F + 96** (TAS 26,704, the pillar cling before the pit), hp/np unchanged.
* = TAS positions on every frame, on Mesen (`tf.py`) and on NesHawk (`nhpre53.py`: ref4751/14_5-3_control + rows,
  0 differences in 95 frames).
* **Arrival test** (`pre53.py`, Mesen, TAS state 26,607 with pokes):
  * `$BF` 0-222, invincibility `$95` 0/33/60, hp 3-16 and ninpo 35-55: **identical positions** in all clean trials.
  * With random junk in the enemy slots `$400-$4A7`, 2 of 5 junk trials differ at 26,651, where the first t0 spawns. A junk
    field is inherited by the spawned enemy.
  * On the real chain the slots hold whatever 5-2's room 26 left. **Check the head start on the real 5-2 exit state
    (NesHawk) before trusting it.**
* Not built on our 5-1 + 5-2 states: 5-2 has only its room-23 prefix so far, so there is no real 5-3 arrival state yet.
  The rows assume Ryu at the room-27 start (x 176 y 208, fixed by the load) with J&S.
* Legality: `legal_ok` with the TAS's previous 150 rows (legalized) as history. Re-judge with our real 5-2 rows.
* Next piece (not chained): **`b_ex27b_h3n35i133.txt`** = 159 rows from TAS 26,901 (X 254 y 208): the legal room-27 exit,
  room 28 on 27,059 (TAS +46). It needs the pit solved in between.

### Expected 5-3

* Leftward exits, measured from TAS states: +46 / +54 / +63, i.e. **~+163**.
* Rightward entries and ladders: ~+5..+10 each, **~+15..+30**.
* Room-27 pit: unknown; the record pays ~+17 there.

**Total ~ TAS +200..+260 = record -75..-135** (record = TAS +334), if the pit costs about what the record pays. The pit is
the risk: until it is solved there is no legal 5-3.

### Next steps for the 5-3 builders (by value)

1. **Room-27 pit (open)**: find how to get onto the y-112 platform (X 448-639) or across the pit legally. Options:
   * a beam that allows damage boosts from the hovering t0 enemies (X 500-540, y 104-112, 26,650-26,780);
   * the X-672 column (its '9' face) climbed with a better contact X (our tests never grabbed it).
2. Leftward exits 29 / 31: graft `b_ex29` / `b_ex31` (+54 / +63 from TAS states) on the real line; cut their spins to what the enemies need.
3. Rightward entries: turn-then-jump instead of L+R; ladder climbs with the 5-2 cycle patterns.
4. Take the room-27 +5 X 400 / +5 X 240 by jump-slashes if each costs < ~6 f (each lowers the 5-2 exit target by 5).
5. Re-run `bf53.py` with our rows for the room-28 throwers; pick a room-28 entry wait to land x in 155-255 / 0-7.


### Agent notes (5-3)
* **l53b FINAL (2026-10-28): v1c stands for rooms 28-30** (room 31 on 29,313, np 5; l53c's `work/l53c/v1c_cn1_poweron.inputs.txt` builds on it).
  Higher-ninpo arrivals all cost more than they save at l53c's price (np 15 at room 31 = -14 f): room 28 with +10 np = +13 f (`r28g`,
  28,339), +15 np = +25 f (`r28h`); room 29 slash line +15 np = +16 f (`b_r29s.txt`; needs a room-30 re-beam, `r30c`: room 31 on 29,331,
  np 20, not NesHawk-checked). So no np-15 line delivered. All my emulators are stopped. Section "5-3 rooms 28-30" added to
  `knowledge/legal_a56_notes.md`.
* **Coordinator (2026-10-28): l53c v1c_cn1 CHECKED - candidate for the 5-3 + 5-4 lock.** `work/l53c/v1c_cn1_poweron.inputs.txt`: judge PASS; rows 1-27,359 identical to e4 (normalized); `verify chain l53c_v1c_cn1` two power-on replays MATCH (RAM sha1 78541bb1a8a1), 0 deaths, 5-4 control 30,252 (5-3 = 2,892 f, record -93 -> cum -495.3), boss0 30,306, 6-1 load 30,903 (`logs/coord_l53c_v1c_cn1.verify.txt`). Lock waits only on l53b's np-15 line (worth ~-4 f net if rooms 28-30 pay <= ~10 f); if it is not better, lock v1c_cn1 as is.
* **l53c -> l53b (2026-10-28 ~01:40): ask for np 15 at room 31, not 20.** On my side np 15 saves 14 f vs np 5 (5-4 control 30,238 vs
  30,252 on v1c's timing) and np 20 saves only 2 f more (30,236). At your ~5 f per 5 np in room 29: np 15 = ~10 f for 14 f (**net ~-4 f**),
  np 20 = ~15-20 f for 16 f (net ~0). So **np 15 if it really costs <= ~13 f, otherwise keep v1c (np 5) - my v1c file stands.** My np-15 rows
  (`b_r31h` + `b_r32n`) are thrower-robust: avoid room-31 `$BF` (after row room-31-control - 1) = 73, 74, 77, 78, 81, 82, 85, 87, 88,
  197, 198, 201, 202, 205, 207, 208, 211, 212, 226 or I re-beam (~45 min; no time lost on the two bad phases I tried).
* **l53b HANDOVER v1c (rooms 28-30, VERIFIED), 2026-10-28 ~01:30: room 31 on 29,313, room-31 control row 29,337, hp 3 / np 5 / J&S.**
  = v1 with two NesHawk pad-read (DMC) conflicts repaired (27,878 in the room-28 entry, 28,368 in the room-29 ladder climb; both re-searched
  so Ryu reaches the identical state a few frames later, `fixnh.py`), same frames as v1 everywhere else.
  * Files: stage rows `work/l53b/v1c_stage.txt` (row 1 = 27,360); power-on `work/l53b/v1c_poweron.inputs.txt` (29,313 rows; judge PASS;
    `verify chain l53b_v1c` two replays MATCH, RAM sha1 59276bce8ab8, 0 deaths). **NesHawk = Mesen on every frame 27,361-29,336 (0 differing,
    end RAM equal; `nhconf.py`: 0 pad-read conflicts).** NesHawk states `l53b_v1c_28349` (room-29 control - 1), `l53b_v1c_28845` (room-30
    control - 1), `l53b_v1c_29313` (room-31 change). Mesen `states/mesen/l53b_v1c_29313.mst`, **`l53b_v1c_29336.mst` (room-31 control - 1,
    Ryu X 411 y 232)**.
  * Splits: room 28 = 27,839 -> 28,326 (TAS +15), room 29 -> 28,822 (TAS +60), room 30 -> 29,313 (TAS +18). 5-3 so far 1,953 f from the
    control row (record ~2,038 to the same point: about -85).
  * **Ninpo at room 31 = 5 (TAS 15).** A higher-ninpo version is being built: room 29 with the TAS's 27,803-eq spin replaced by a Down+B
    slash (no hit) and no extra spins (`b_r29s.txt`): room 30 on 28,838 (+16 f) with np 25 instead of 10 -> **room 31 with np 20 at ~+16..+20 f**.
    Room 30 must be re-beamed for it (enemy slot junk differs after the new room 29, the old room-30 rows take a bird hit), running. Tell me
    (l53b) which np l53c needs at room 31; each 5 np costs ~5 f in room 29.
  * NesHawk note: the DMC pad-read conflicts are NOT at fixed frames (they move with the sound effects), so every new piece needs
    `nhconf.py` (frames where NesHawk's `$2A` differs from the row) and a repair.
* **l53c HANDOVER on l53b v1c (2026-10-28 ~01:20): 5-3 rooms 31-33 + 5-4 + 6-1 load, NesHawk = Mesen on every frame, judge PASS.**
  Power-on file **`work/l53c/v1c_cn1_poweron.inputs.txt`** (30,905 rows = v1c rows 1-29,336 (blank after 29,313) + my rows
  `work/l53c/c53_v1_cn1.txt` from row 29,337 = room-31 control row). v1c's room-31 state = v1's (0 RAM diffs; `$BF` 129, hp 3, np 5).
  Events: **room 32 on 29,615**, room 33 on 29,837, **5-3 trigger 30,092** (`$62` 5; Start on 30,097-98), **5-4 control row 30,252 =
  record -93** (record pace <= 30,345), hp 16 / **np 5 / J&S (133)**, one J&S spin, **boss 0 on 30,306** (control + 54, timer 149), Start
  on 30,900-01 -> **6-1 load 30,903**; **6-1 control row 31,055** (= load + 152; hp 16, np 0). NesHawk from `l53b_v1c_29313`: 0 frames
  differing 29,337-30,905, end RAM equal; NesHawk states `l53c_29600`, `l53c_30251` (5-4 control - 1), `l53c_30903` (6-1 load).
  This is the np-5 version: room 31 with 0 spins and two 1-hp hits (hp 3 -> 1; refilled to 16 at the trigger), room 32 without its spin.
  **With np >= 15 at the room-31 control, 14 f are saved (5-4 control 30,238; >= 20: 30,236)** - see my price list above; send me the
  arrival and I rebuild in minutes (the np-15/20 rows are `$BF`-robust: 237 of 256 thrower phases).
* **l53c ninpo price list on l53b v1's room-31 arrival (2026-10-27 ~22:40, Mesen; `$BF` 129, timer fine in every case).** np needed at the
  room-31 control row for the 5-3 exit to be J&S + exactly 5:
  | np at room 31 | my spins (31 / 32) | 5-4 control row | vs np 20 | rows (from row 29,337) |
  |---|---|---|---|---|
  | **20** | 2 / 1 | **30,236** (record -109) | 0 | `work/l53c/c53_v1np20.txt` (np poked) |
  | **15-19** | 2 / 0 (room 32 without its spin: +2 f, `b_r32n`) | 30,238 | +2 | (rebuild with `c53.py --r32 work/l53c/b_r32n.txt`) |
  | **5-14** (v1 = 5) | 0 / 0, two 1-hp hits in room 31 (hp 3 -> 1, refilled at the trigger) | **30,252** | +16 | **`work/l53c/c53_v1_cn1.txt`** (real np 5, works as is) |
  | 5, no hits | 0 / 0 | 30,266 | +30 | `c53_v1_cn0.txt` |
  A single room-31 spin is worth little (floor beam with 1 spin, no hits: 26 f behind the 2-spin run, i.e. no better than 0 spins with
  hits). **So: +10 np at room 31 (15 instead of 5) saves 14 f; more than 15 saves 2 more; nothing in between helps.** Excess above 20 is free to burn in room 33.
  **NesHawk:** the v1 power-on rows (`work/l53b/v1_poweron.inputs.txt`) replayed on NesHawk from `l52b_e4_27360` are still in room 28 with
  hp 16 / np 22 at 29,336 (so v1 diverges on NesHawk before room 31; `states/l53b_v1_29313.State` holds that diverged state too) - my
  rooms are NesHawk-checked only from TAS states so far (0 frames differing to the 6-1 load).
* **l53c on l53b v1 (2026-10-27 ~21:00): my rows graft cleanly; ninpo is the only blocker.** From l53b v1 (room-31 control row 29,337;
  state `states/mesen/l53c_v1_29336.mst`; `$BF` 129 = a good thrower phase) with np POKED to 20: room 32 on 29,601 (+53), room 33 on
  29,821 (+5), trigger 30,076 (`$62` 21: fine), **5-4 control row 30,236 (= record -109)**, kill 30,290, 6-1 load 30,887, 6-1 control
  31,039; hp 3, no hits (Mesen, `c53_v1np20.txt`). **With the real np 5 it does not work**: my rooms spend 3 spins (room 31 x2, room 32 x1)
  and 5-4 needs 5 at the trigger. So I need **np 20 at the room-31 control (15 more than v1)**; any excess above 20 is free to burn
  (room 33: one jump + J&S spin per 45 f on the run, 0 f, no lanterns there; tested 4 spins). Now measuring what 0/1-spin versions of
  rooms 31/32 cost (beams running) so we can compare with the cost of 15 more np in rooms 28-30; numbers here within ~1 h.
* **l53b HANDOVER v1 (rooms 28-30 on l53a's 'both' line), 2026-10-27 ~21:30: room 31 on 29,313, hp 3, np 5, J&S (`$C9` 133). Mesen;
  NesHawk check running.** Stage rows `work/l53b/v1_stage.txt` (row 1 = 27,360 = l53a `ch1_both_rows` + Left on 27,840 (room-change row,
  makes l53a's 1-f Left a 2-f hold; same outcome) + mine); power-on `work/l53b/v1_poweron.inputs.txt` (judge PASS). Mesen states:
  `states/mesen/l53b_r28c_28349.mst` (room-29 control - 1), `l53b_v1_28845.mst` (room-30 control - 1). For l53c: **the room-31 control
  row is 29,337 (room change 29,313 + 24, as TAS 28,394 -> 28,418); Ryu arrives exactly as the TAS (X 411 y 232 at the load), lag vs TAS
  = 919 at the room change (5-3 control lag 752).**
  * Room 28 (`b_r28c.txt`): legal entry (ledge landing via a chimney jump-off, `b_led28.txt`; turn + 2 jumps, `b_ent28g.txt`, = TAS-eq +9 at
    X 200) then beam r28c (both throwers on our phase, **0 hits**): room 29 on 28,326 = **TAS +15** (record ~-26). 5 spins, both lanterns
    (+5 X 288, +10 X 496): np 45 -> 35.
  * Room 29 (`r29_v1.txt`, rows from the room-29 control row): entry `[A+Left x2, Right x6] x5, A+Left x2, Left` (+10), legalized TAS rows
    to TAS 27,800 (0 divergence), then beam ex29f (prep's ex29 + 4 f): room 30 on 28,822 = **TAS +60** (record ~-9). 5 spins (TAS 3): np 35 -> 10.
  * Room 30 (`b_r30b.txt`): entry like room 28 (+10 at the y-192 block), beam r30b (Windmill/Star traps avoided, 2 spins + the +5 X 336,
    like the TAS): room 31 on 29,313 = **TAS +18** (record ~-14). np 10 -> 5.
  * **Totals: rooms 28-30 = TAS +93 = record ~-49; 5-3 so far (27,360 -> 29,313) = 1,953 f vs record ~2,038 (-85).** hp 3 the whole way.
  * **Ninpo is the open problem: np 5 at room 31 (TAS 15)** - not enough for l53c's legal room-31 exit. Working on it: beam r28d (room 28
    weighting ninpo, np 50 at X 566 so far) and a room-29 exit with fewer spins (the 27,933-eq spin seems needed; the extra 27,878 one kills
    a soldier that otherwise hits for 1).
* **l53c (rooms 31-33 + 5-4) INTERIM 2026-10-27 ~19:35: rooms 31-33 and 5-4 built from TAS states, NesHawk = Mesen on every frame; waiting
  for l53b's room-31 arrival to graft.** Rows `work/l53c/c53_tas.txt` (1,556 rows from the room-31 control row = room-31 change + 24; chain
  script `work/l53c/c53.py <mst F0>` rebuilds them from any arrival). Splits vs TAS: **room 31 +54** (record +70; floor under the wall +
  a new 7-f wall-climb cycle `[A+Right x4, A+Left, Left, -]` = 1.86 px/f), **room 32 +7** (turn on the left ledge, no moonwalk), **room 33 +
  transition -1** (Right held; the stage end WAITS FOR START: Start on trigger + 5/6), **5-4 = TAS +0** (b13's kill, one Start on kill + 594
  -> 6-1 load on kill + 597; b13's own Starts cost it 2). **5-4 control row = 5-3 trigger + 160** (not + 159). Total from the room-31
  change to the 6-1 load: TAS + 60. **Needs at the room-31 control: np 20** (spins: room 31 x2 (TAS 28,508-eq + one for the bird/axe),
  room 32 x1 (TAS 28,782-eq); exit 5 for 5-4's one spin), J&S, any hp >= 2 (no hits taken; the transition refills to 16). **Room-31
  thrower: `$BF` after the row before the room-31 control row must NOT be 73, 74, 77, 78, 81, 82, 85, 87, 88, 197, 198, 201, 202, 205,
  207, 208, 211, 212 or 226** (TAS 234; 237 of 256 good). **5-4 tally:** `$62` at the 5-3 trigger <= 55 or it costs 3 f. Rooms 31-33
  rows do not depend on anything else found so far (room 32/33 and 5-4: `$BF`-free). Details: `work/l53c/sec_draft.md` (to be merged
  into legal_a56_notes.md "5-3 rooms 31-33 + 5-4").
* **l53b room-28 thrower, first answer (2026-10-27 ~19:40, on l53a's 'both' arrival `l53a_e4both_27861.mst`, np 45): SURVIVABLE on legal
  rows with no wait, no hit and no spin.** A legal entry (`ent2_best_27861.txt`: c2 climb, jump-off onto the left ledge, Right, A+Right,
  A+Right again from the column top; X 200 y 144 on 27,995 = TAS-eq +19) followed by beam `r28a` (width 150, minhp 3) passes thrower #1
  (X >= 345) on **28,092 = TAS-eq +20 (lag 846), hp 3, np 45** (no spin, no lantern; the TAS spends 2 spins here and takes the +5 at X 288,
  net 0). So the thrower costs ~1 f on this phase, not a wait. Caveats: (1) the entry is being improved (TAS's 2 px/f tap climb is
  illegal; the legal climb/ledge/turn costs +9..+19 so far), and every entry change moves the thrower phase, so `r28a` must be re-run on
  the final entry; (2) thrower #2 (exit ladder) not yet tested - beam `r28b` to the room-29 change is running. TAS rows themselves on the
  real arrival die/hit at the first axe (TAS-eq 27,158), as prep said.
* **l53b (now rooms 28-30) -> l53c handover (rooms 31-33): nothing built in 31-33 yet.** Tools that may help, `work/l53b/`: `bm.py` (beam
  from a .mst or a TAS frame, `--hist` press history, `--poke 65=3,64=..`, rows written from F0+1), `chain.py` (prefix + legalized TAS rows
  shifted + tail; prints divergence/hp/np events), `ent.py` (grid for the shared rightward entry of rooms 28/30/32: climb cycle, A+Left
  jump-off onto the left ledge, Left m, Right r, A+Right; running now), `ent29.py` (grid for a ladder-climb-then-left entry, e.g. room 29/31),
  `lb.py` (lib with the fastcore RAM floor lowered to 1.5 GB). Damage per enemy type: see my hp note above (bird / stone man / ring = 3).
  **Room 29 entry (legal): `[A+Left x2, Right x6]` x 5 (40 rows) then `A+Left x2`, Left -> on the y-208 floor at X 600 on TAS 27,582 + 10,
  same xsub; then the TAS rows (legalized) follow at lag 10 with 0 divergence to TAS 27,800 (`ch29a.txt`, from TAS state 27,508, hp 3).**
  Room 31 also starts against a ladder face (X 411 y 232) - `ent29.py` may apply.
* **l53a room 27 DONE on e4 (for l53b: room-28 arrival states).** Two verified versions, both 0 hits, hp 3, judge PASS on the power-on
  files, NesHawk = Mesen every frame (from `l52b_e4_27360`), end RAM equal:
  | version | rows (stage row 1 = control 27,360) | room 28 (change) | vs TAS | np at room 28 | NesHawk states | Mesen state (after room-28 control - 1) |
  |---|---|---|---|---|---|---|
  | **ch1** (no lanterns) | `work/l53a/ch1_rows.txt` (476) | **27,835** | **+70** | 35 | `l53a_27835`, `l53a_27857` | `states/mesen/l53a_e4_27857.mst` |
  | **ch1_both** (+5 X 400, +5 X 240) | `work/l53a/ch1_both_rows.txt` (480) | 27,839 | +74 | 45 | `l53a_27839`, `l53a_27861` | `states/mesen/l53a_e4both_27861.mst` |
  Power-on files: `work/l53a/e4_ch1_poweron.inputs.txt`, `work/l53a/e4_ch1_both_poweron.inputs.txt`. Single lanterns: `ch1_l400_rows.txt`,
  `ch1_l240_rows.txt` (27,837, np 40; Mesen only). **Room-28 control row = room change + 23** (27,858 / 27,862) = TAS 27,036 + 822 / + 826.
  The arrival equals the TAS's at 27,035 in X/y/scroll/facing; the legalized TAS rows 27,036-27,120 give the identical path from my state
  and from the TAS state (`work/l53a/cmp28.py`). Differences at arrival: np, `$BF`, Ryu anim/vy junk (`$81 $82 $87 $89 $8D-$8F $94`).
  **Pit verdict:** the X-672 column's ladder face + the y-112 platform (the record's way, which costs him ~+40, not ~+17); ours costs ~+27 (exit +46).
  Proofs, sizes and the code rules: `knowledge/legal_a56_notes.md` "5-3 room 27 (pit)". **Room-28 thrower phase:** x = (27,360 + 70) mod 256
  = 38 (ch1) / 42 (both): bad for both throwers on TAS rows; needs l53b's legal-row re-scan or an entry wait.
* **l53b (rooms 28-33) EARLY HP VERDICT (2026-10-27): hp 3 OK for rooms 28-33 as far as the data goes; e5's +2 hp buys at most one
  3-damage boost and none is planned.** Damage per touch (ROM table `enemy_damage` $B560, bank00, indexed by type; `hurt_ryu` $E144):
  thrower (t2) 1, **axe (t18) 1**, batter (t3) 1, crouching soldier (t5) 1, running soldier (t7) 1, bat (t8) 1, dog (t9) 1, jetpack
  ninja (t12) 1, its shuriken (t21) 1, machine-gun shot (t17) 1, waiting/crouched ghoul (t16/t15) 2, **bird (t11) 3, stone man (t14) 3,
  its ring (t22) 3**. So at hp 3 the birds (rooms 29-31), stone men (31-32) and rings (32) kill; everything else costs 1 (ghouls 2). The
  TAS runs rooms 28-33 at hp 3 with one 1-hp hit (room-31 axe boost, not on the legal floor+ladder exit). A 1-hp boost (axe, soldier,
  bat, ninja) stays possible on e4 (hp 3 -> 2 -> 1). Real e4 arrival checked: our room-28 state (l53a's rows, Mesen
  `states/mesen/l53b_e4_27857.mst`) = the TAS's 27,035 for Ryu; with the TAS's own rows the room-28 thrower #1 axe hits at our 27,980
  (TAS-eq 27,158), as prep predicted (spawn `$BF` 8 on e4). Working on a legal room-28 line that avoids it.
* **l53a (room 27) on e4 (5-3 control 27,360, hp 3 / np 45 / J&S): hp 3 OK for room 27 - 0 hits, NesHawk-verified.** Rows
  `work/l53a/ch1_rows.txt` (476 rows from the control row; row 1 = Left) -> **room 28 on 27,835 = stage row 476 = TAS +70**
  (record ~+110), **hp 3, np 45 -> 35** (2 spins: the y-112 platform walker + the TAS's 26,855 spin), J&S. NesHawk from
  `l52b_e4_27360` = Mesen on every frame to 27,865, end RAM equal; NesHawk states `l53a_27835` (room change), `l53a_27857`
  (room-28 control row - 1); Mesen `states/mesen/l53a_e4_27359.mst` (before the control row, 0 non-stack diffs vs NesHawk).
  Same rows on e1 (27,397, hp 6): identical path, room 28 on 27,872. **Verdict for 5-3: hp 3 OK / no hit is planned.** Room 27
  needs none; the TAS runs all of 5-3 at hp 3 (its only hit, 28,563 in room 31, is the axe boost the legal floor+ladder exit
  does not use); prep's legal exits end with no hits. What could cost hp: room-28 thrower phase (fix by an entry wait) and a
  ninpo shortfall (each missing spin ~ one hit). **Ninpo: np 45 covers the TAS's 11 spins + my 1 extra; spare only via the
  lanterns** (X 400: +5 for 2 f, Down+B plain slash; X 240 being priced). **Room-28 phase on e4:** x = (27,360 + 70) mod 256 = 38
  -> thrower #1 bad band (30-154) by 9: a 9-f faster room 27 or a re-scan with legal room-28 rows is needed (wait to 155 = 117 f: no).
* **l53a hp verdict (2026-10-27 ~15:00): hp 3 OK for 5-3 as far as I can see; no planned hit anywhere.** Room 27 (my line, below):
  0 hits, verified on the real e1 entry (hp 6) = identical to the TAS-state run on every frame. The TAS itself runs all of 5-3 at
  hp 3 and takes one 1-hp hit (28,563, room-31 axe boost) that the legal floor+ladder exit does not use; prep's legal exit beams
  (ex27b/ex29/ex31) end at hp 3 with no hits. The risks are avoidable, not needed: (1) room-28 throwers: a bad phase x = (F + L28) mod 256
  gives an axe hit of 1-2 hp (some values die) -> fix with a k-frame wait at the room-28 entry (cost k f); (2) ninpo: every TAS spin
  replaces a hit (spintest), so np must cover ~11-12 spins: my room 27 uses 2 spins (TAS 1: the extra kills the y-112 platform walker,
  0 f), so **entry np 45 = enough with nothing to spare**; the room-27 +5 lanterns add spare (X 400: +5 for 2 f by a Down+B plain slash;
  X 240 being priced). Spare hp would only buy damage boosts, and none is useful in room 27 (the only enemy near the pit walks on the
  platform; nothing reaches Ryu below it).
* **l53a (room 27, pit) PAUSED 2026-10-27 by the owner: resume note.** No rows built yet. Tools in `work/l53a/`: `tr.py`
  (trace a row spec from a TAS state or .mst: X y xsub vy `$8C` `$84` anim hp np room, `--en` enemy slots, `--poke`), `gate.py`
  (waits for free RAM >= 3 GB before running a command).
  * **The record's pit crossing is the X-672 column's ladder + the y-112 platform, and it costs ~+40, not ~+17.** From
    `work/a56r2/rec/r53.json` (record camera vs the TAS camera, RAM x = video x + cam - 2, y = video y + 9): the record's camera
    starts scrolling at t 75 (TAS t 31): **lag 44 from the first move**; then the camera moves at exactly 1.5 px/f without a stop
    (lag 44 -> 42 -> 40 through the pit). Ryu is at y 86 over X 549 at t 135 (hidden above y ~81 for t 115-133 = a jump from
    the platform), runs on the y-112 platform X 535 -> 445 (t 143-203), drops to the floor at X ~399 (t 239). So he climbed the
    ladder face before t ~58 and jumped off left at 1.5 px/f; the pit itself costs ~0 once on the platform. Later lags: 45-46
    (X 400-260), 51 around the X-240 lantern / '84' pillar, 36 at X ~180 (the record walks under the '84' pillar; the TAS climbs it).
  * **The ladder grab works (prep's `pitgrid.py` never walked far enough left: k <= 15 leaves Ryu under the column, where
    rising into the '9' tile sets the let-go bit `$80`).** Grab rule (`touch_walls` $E677): `$8F` = kind at (x+5, y-1) must be the
    '9' (X 672-687, rows y 80-191) in the same frame `$8E` (x+5, y-5) is; i.e. come in from the LEFT (x <= 666 first) with feet
    y 85-192. Verified trace (TAS state 26,607, hp 3): `Left*30, Right*2, A+Right*2, Right*...` -> walks to X 643, jumps at
    26,640, **grabs at X 667 y 165 on 26,654** (`$8C` = $20, action 10); Up climbs exactly 1 px/f (action 12). On steps only
    A+Left ($82) jumps off (vy -2, facing flips to LEFT, run speed 1.5 px/f); Down climbs down; anything else holds.
  * Arithmetic for the line: Ryu at pure 1.5 px/f leftward would be at X 444 on t 163; the TAS is on the floor at X 401 on t 194
    (~2 f behind pure running), so **cost of a platform line = frames lost vs pure leftward running**. A jump-off from the face
    at X 667 reaches the platform's edge (x <= 646) ~14 f later at y0 - 7, so it needs y0 <= ~118 at the jump-off. Grab at
    y 165 + Up 1 px/f = ~47 f of climbing -> ~+79 total (worse than the record). Faster: grab higher (a jump from further left
    peaks at y 160) and climb with jump-off/regrab cycles (`[A+Left x2, Right x6]`-type, 5-2's `cyc.py` grammar) - untested.
* **Next steps (l53a on resume):**
  1. Beam (`b53.py`-style, goal X <= 446 and y <= 112, or floor X <= 400) from TAS 26,607 with the alphabet incl. Up/Down and
     the grab prefix above; also a cycle grammar from the grab (walk-left distance k x jump frame x cycle pattern x jump-off y).
     Target: beat the record's ~+40 (record lag 40 at X 445).
  2. Try the other routes still untested: knockback from the hovering t0s (X 500-540, y 104-112, t 42-172) while above the
     pillar; a ground jump that crosses the X-528 pillar at y <= 160 (passes over it; y-1 must be < 160) then a cling on the
     '21' block's '1' face (X 511); J&S spin / slash effects on air physics (check `drift_speed`/`run_speed` $E??? at
     bank07 lines 6746-6760, `move_ryu` line 5805).
  3. Then the exit (`work/l53p/b_ex27b_h3n35i133.txt`, +46), the +5 lanterns X 400 / X 240 (y 160; on the platform line Ryu
     falls past X ~400 from y 112, so the X-400 lantern may be free), room 28 phase (bf53.py).
  4. Re-check on the real 5-2 exit state (NesHawk) once a 5-2 candidate exists; report hp 9 and hp 12.

## Next: 6-1 / 6-2 plan (prep agent l61p, 2026-10-27)

6-1 = room 35 (one long room, runs LEFT, X 1,968 -> 23). 6-2 = rooms 36 (left), 37 (left), 38 (vertical shaft), 39 (right),
40 (right). Act VI starts after the 5-4 cutscene with hp 16, ninpo 0, no art; only `$BF` and `$62` carry over.
**Headline: 6-1 and room 36 have no banned inputs except 1-f A/B, so the legalized TAS rows ARE the TAS. A verified head start
covers all of 6-1 and room 36 (2,533 rows, = TAS frames, J&S + 20 ninpo at room 37), but it is arrival-dependent: on NesHawk only
13 of 61 real 5-4 Start delays (from the TAS kill) keep it TAS-exact, and there is no free way to shift the arrival, so check it
on the real 5-4 state (`nh_late.py`) and pay the smallest good delay. All of 6-2's banned inputs are in rooms 37-40; legal
versions now exist for room 37's entry + pillar (+60), room 38 (+16), the room-39 entry (+23), the room-40 entry (+15) and the
room-40 platform (+2), all from TAS states; the room-37 run to its exit and the chaining of the pieces are still open.**
Tools and data in `work/l61p/`:
* `dumps.py` -> `tas61_ram.bin` (NesHawk TAS RAM after rows 29,261-34,760: the 5-4 fight, cutscene, 6-1, 6-2, 6-3 start);
  `lib0.py` (`TM(f)`, `XY`; falls back to the l53p dumps); `lib.py` (Mesen helpers, `core_at(f)`, `legalize_tas`);
* `mkst.py` -> Mesen TAS states `states/mesen/l61p_tas<f>.mst` (29,258 ... 34,560; 0 RAM diffs vs NesHawk; Mesen `step()`
  is 1 f off in the act-end cutscene, so the differing bytes are re-synced from the dump at 29,911-30,062);
* `ev.py` -> `tas61_ev.txt`; `rle.py` -> `tas61_rows_rle.txt`; `brk.py` -> `brk61.out` (rule-break spans); `roommap.py`;
* `tf.py` (follow legal TAS rows), `b61.py` (beam), `cyc.py` (cyclic climb patterns, `--ks`), `chtest.py` (prefix + cycle grid),
  `shift.py` (prefix + legal TAS rows at a lag), `r40g.py` (room-40 grid), `r37seq.py`, `l1024.py` (lantern test), `js61.py` (6-1 J&S fix);
* `bf61.py` (arrival scan: `$BF` poked at 30,062, any rows file, `--junk`), `cls.py` / `band.py` (classify a scan by c);
* `nh_trans61.py` (NesHawk: 5-4 kill -> Start -> 6-1 control), `nh_trans62.py` (6-1 -> 6-2, 6-2 -> 6-3), `nhpre61.py` +
  `mpre61.py` (NesHawk / Mesen listings of a head-start file, pokes), `nhdiag.py` (NesHawk slots);
* **`nh_late.py` (NesHawk k-scan of the 5-4 Start delay with a head-start file; `--state NAME --kill K` for our real 5-4)**,
  `kscan.py` (Mesen twin; NOT reliable here), `nh_arr.py` / `nh_arr2.py` (real arrivals from delayed 5-4 kills, RAM diffs,
  `--groups` byte-range swaps), `arrtest.py` / `arrtest2.py` (Mesen byte-copy tests).

Frames are power-on rows on the TAS axis (NesHawk frame k = after row k). **TAS 6-1 control row = 30,063** (Left moves Ryu
x 176 -> 174). **`$BF` in Act VI = (f - 27) mod 256** (checked at 30,063 / 31,638 / 32,573). Let **c = `$BF` on our 6-1
control row = (F - 27) mod 256**, F = our 6-1 control row (TAS: c = 84).

### Transitions (NesHawk)

* **5-4 -> 6-1 (act-end cutscene)**: same as 4-4 -> 5-1. With timer T at kill + 1 (T 149 on every tested kill): **earliest
  Start = kill + 147 + 3T = kill + 594**, a fresh 2-f press; Start one row later gives the same load. **Load = kill + 597,
  6-1 control = kill + 749 = load + 152.** Tested on kills 29,314-29,322 (`nh_trans61.py`, TAS 5-4 rows delayed d = 0-8):
  8 of 9 behave so; **the kill on 29,317 (d 3) ignores the Start on kill + 594** (and a Start held across that row is
  blocked), it needs a fresh press on kill + 595 -> control kill + 750. Not a `$BF` effect (`$BF` poked +1/+2/+3 at 5-4: same).
  So: **press Start (2 f) on kill + 595**: it gives the same load as kill + 594 for all 9 tested kills and is the only one that
  works for the 29,317 kill (or check the real kill with `nh_trans61.py`). The TAS: kill 29,314, Start 29,909,
  load 29,911, control 30,063.
* **Is the Start free / does it shift `$BF` for free? No.** A Start on kill + 594 or + 595 gives the same load; every later row
  delays the 6-1 control by 1 and shifts c by 1 (1:1 cost). Left held from the load gives the same control row (Ryu cannot move
  earlier). A later 5-4 kill also moves everything 1:1. **The only way to choose c is to pay frames** (a later Start).
* **6-1 -> 6-2**: trigger = first `$5C` 0 = the frame after Ryu reaches X 23 (y 144) (TAS 31,359); load (`$6D` 17) = trigger + 128;
  **6-2 control = trigger + 279 (Left; TAS 31,638)**. Left held from trigger + 1 or from the control row = same; Left first on
  trigger + 280 = 1 f late. Start (31,380 / 31,630) does nothing. No free frames.
* **6-2 -> 6-3**: trigger = Ryu reaches X 747 y 208 in room 40 (TAS 34,282); load = trigger + 128; **6-3 control = trigger + 279
  (Right; TAS 34,561)**. Right from trigger + 1 = same; Right first on trigger + 280 = 1 f late. No free frames.
* Room changes inside 6-2: control resumes 23 f after the room change (TAS 32,596 / 33,193 / 33,291 / 33,735).
* `$62` is frozen through every transition and carries on (it only matters at the 6-4a tally; not for 6-1/6-2).

### Splits (room change = the first frame with the new `$6E`; record = first picture after the 22-f black, minus 22, +-3)

| | TAS frame | TAS t | record t | room: TAS | room: record | record loses |
|---|---|---|---|---|---|---|
| 6-1 control (room 35) | 30,063 | 0 | 0 | | | |
| 6-1 trigger | 31,359 | 1,296 | | | | |
| **6-2 control** | **31,638** | **1,575** | **1,584.6** | 1,575 | 1,584.6 | **+9.6** (one room; the record = TAS pace, no detail) |
| room 37 | 32,573 | 935 | 991.7 | 935 | 991.7 | **+56.7** (end of room 36: the record ~+45 at X 64-127) |
| room 38 | 33,170 | 1,532 | 1,690.8 | 597 | 699.1 | **+102.1** (entry chimney + pillar climb) |
| room 39 | 33,268 | 1,630 | 1,817.0 | 98 | 126.2 | **+28.2** (ladder shaft) |
| room 40 | 33,712 | 2,074 | 2,281.8 | 444 | 464.8 | **+20.8** (entry) |
| 6-2 trigger / 6-3 control | 34,282 / 34,561 | 2,644 / 2,923 | 3,153.2 | 849 | 871.4 | **+22.4** (room 40 incl. the transition) |
| **6-2** | | **2,923** | **3,153.2** | | | **+230.2** |

Record pace: **6-2 control <= F + 1,584; 6-3 control <= F2 + 3,153** (F2 = our 6-2 control). 5-4 -> 6-1: the record's 5-4 is
805.3 f (TAS 804; our `5-4_b13` = TAS +2), so the 6-1 control should be <= 5-4 control + 805.

### TAS rule breaks in 6-1 / 6-2 (`brk61.out`), split into legal and banned parts

| TAS rows | what | banned part | legal version / verdict |
|---|---|---|---|
| 30,063-31,358 (6-1) | run left, 30 jumps/slashes | 1-f A/B only | **legalized TAS rows = TAS positions exactly** (Mesen + NesHawk, head start below) |
| 31,638-32,595 (room 36) | run left, J&S 32,353, spins 32,428 / 32,483 | 1-f A/B only | **legalized = TAS** (room 37 on 32,573). The 1-f Right turn at 32,506 held 2 f puts Ryu 1 px ahead on 32,507-32,559; he re-joins by 32,560. Drop the 32,483 spin (it breaks + catches the Windmill X 256): **0 f, J&S kept** |
| 32,596-32,628 | room-37 entry chimney: 28 f L+R (moonwalk right up the block face onto its top y 192), then to X 895 (screen x 127 starts the leftward camera, `$4C` 128 -> 129) | L+R, 1-f | **legal: the record's way** - A+Left off the block face to the pillar face (X 839), A+Right wall jump back onto the block top, walk right to X 895, Left, jump to the pillar: rows `work/l61p/r37_pre_cl.txt` (b_r37e beam to 32,646 + `r37seq.py` grid, 450 cases): pillar cling (X 842 y 144) on **32,696 = TAS +31..33**. Pure ladder (Up x n, 41 cases) and cycle grids (`cyc_r37e.out`, 4,410 legal cases) never reach the block top: the face is not a ladder |
| 32,666-32,703 | pillar right face: A+Left/A+Right taps every 4 f (2 px/f), then U+D+L 15 f over the pillar top (y 96) | period 4, U+D, 1-f | **legal cycle `[Right, A+Right, A, A+Left, A+Left, Left] x 6`, then Left** (`cyc_r37p.out`, 3,560 legal cases from TAS 32,665): top (X <= 822, y 96) on 32,725 = **TAS +22** from the TAS cling. **Chained with the entry: `work/l61p/r37_top_32763.txt` (166 rows from TAS frame 32,596, `chtest.py` 112 cases) -> pillar top on 32,763 = TAS +60** (record: room 37 +102) |
| 32,704-33,170 | room 37 rest: run left over the top, down to the y-128 ledge, into the exit (120, 80) | 1-f only | legal TAS rows at lag 58 follow to TAS 32,992, then the crouching soldiers (t5, spawn by scroll) hit (`shift.py`). Needs a repair; old hand line `logs/r4/r4_62_h2` (a56 round 4: slash the walker, jump at ~298, platform y 160, air slash, ledge y 128, jump at ~155) is the model. A -X beam (`b_r37x`, 260 f) stalls at X 231 y 169 |
| 33,194-33,268 (room 38) | ladder shaft X 89-91, y 232 -> 84: 1-f A+L / A+R taps + L+R, 2 px/f | L+R, 1-f, period < 5 | **legal 6-f cycle `[Left, A+Left, A, A+Right, A+Right, Right] x ~25` -> room 39 on 33,284 = TAS +16** (`cyc_r38.out`, 1,091 legal pattern x rotation cases, from TAS 33,193). Record +28, old A* +22 |
| 33,291-33,332 (room 39 entry) | ladder at X 91 y 232 -> L+R up the X-96 face and onto the y-160 ledge, run right | L+R, 1-f | **legal `[Right, A+Right, A+Right, A+Right, A+Left, Left] x 5`, then Right -> X >= 148 on y <= 160 on 33,375 = TAS +23** (`cyc_r39e.out`, 5,145 legal cases, from TAS 33,290; TAS 33,352). Record: room 39 +21 in total |
| 33,319 / 32,667 | Windmill throws (rooms 39 / 37) | - | we hold J&S: Up+B in the air = a spin (5 ninpo), or drop them; untested on our line |
| 33,736-33,760 | room-40 entry: up the X-160 face with taps every 4 f to y 216, jump off left, a second wall jump at X ~132, over to the y-160 floor | period 4, 1-f | legalized TAS rows fall into the pit (death at 33,765). **Legal: `[Left, A+Left, A, A+Right, Right, Right] x 4`, then A+Left held -> X <= 128 y <= 185 on 33,777 = TAS +15** (TAS 33,762; `cyc_r40e2.out`, 4,081 legal cases from TAS 33,735; hp 14). Not chained to the platform piece (which starts from the TAS state 33,792). A Left-tail grid (`cyc_r40e.out`, 3,675 cases) and an 80-f beam found nothing |
| 33,793-33,860 | jump from (82,160); **U+D+L 22 f = 0.45 px/f leftward while facing LEFT** (idle pad keeps the drift speed set by the 1-f Right at 33,794); land on the y-128 ledge at X 72; A+Right on the ground (no turn) + **L+R 33 f = 1.5 px/f right while facing left** (a right-facing Ryu would cling to the platform's left face) onto the y-96 platform | U+D, L+R | **legal: A x2, `(Left x2, blank x4) x 5` (0.5 px/f average), Right x3 (turn on the ledge), A+Right x2, Right -> on the platform X >= 123 on 33,863 = TAS +2** (`r40g.py`, 1,092 cases; 30+ variants give 33,863; `work/l61p/r40_plat_33863.txt`, rows from TAS 33,793). After it, the TAS rows at lag 1-4 meet the room-40 bird (t11, spawn 33,887) at 33,928 or fall into the pit: needs a short repair beam |
| ~180 rows | 1-f A/B, presses < 5 f apart | press cap | Enforcer (2-f holds) |

**Expected 6-2 on legal pieces (from TAS states): room 36 +0, room 37 ~+60..+80 (pillar top +60, rest unknown), room 38 +16,
room 39 +23 (entry) + rest, room 40 +15 (entry) +2 (platform) + repair -> roughly TAS +110..+150 = record -80..-120.** The record pays +102
in room 37, +28 in room 38, +21 in room 39, +22 in room 40.

### Arrival dependence (`$BF`, `$3E`, cutscene leftovers) - judge on NesHawk only

* **Readers in 6-1 / room 36 (measured):** the throwers (type 2: 6-1 at (427,144) on 31,014; room 36 at (1,214,128) on 31,761
  and (926,160) on 31,953) and their axes (type 18), and **the jetpack ninjas' shuriken (type 21) in room 36** (x moves +-1 px
  with `$BF`; NesHawk `nhdiag.py`). Also two hidden phase bytes: **`$3E` (`status_i`, 6-frame counter of the status-bar
  redraw, frozen in the cutscene)** and Start-time leftovers of the cutscene (`$394`, `$3C4`, `$3C7`, `$621`). Proof: an arrival
  from a 5-4 kill 5 f later fails even with `$BF` poked to 84, and poking only `$3E` back fixes it (NesHawk `nh_arr2.py --groups`).
* **`$BF`-poke scan (Mesen `bf61.py`, all 256 c, from the TAS arrival; the plain legal rows give the same classes):**
  136 good; H61 36 (6-1 thrower axes from 31,059), H36 65 (room-36 thrower axes), J36 19 (a shuriken hit on 32,426, 2 f before the
  32,428 spin). Good c: 1-2, 4, 6-7, 9-14, 17-22, 24-29, 32-36, 38, 40-43, 45-72, 74, 77, 81, 84-85, 88-89, 92, 94, 98, 100, 104, 108,
  118, 130, 133, 137, 139, 143-144, 147-148, 150-158, 162, 165-166, 169, 176-195, 197-198, 201, 203-204, 207-208, 211-212, 230,
  233-234, 237, 240, 243-244, 247-248, 251, 254. Full lists: legal_a56_notes. **This is an upper bound only:**
* **NesHawk, real arrivals = the TAS 5-4 with the Start delayed by k (c = 84 + k), `nh_late.py`, k 0-60: the head start is
  TAS-equivalent only for k 0, 1, 5, 8, 14, 16, 20, 34, 49, 53, 55, 59, 60 (13 of 61; c 84, 85, 89, 92, 98, 100, 104, 118, 133,
  137, 139, 143, 144).** Every NesHawk-good c is Mesen-good, but Mesen-good c 88, 94, 108, 130 fail on NesHawk (Mesen `kscan.py`
  with the same real Start delays agrees with the poke scan, not with NesHawk). Most bad k are H61 (6-1 thrower, ~rows 1,000-1,020);
  others fail early (k 3 / 17 at row 194, k 39 / 40 at row 384, k 28 / 46 at row 553, k 57 at row 757).
* **So the band cannot be precomputed for our chain:** it depends on `$BF`, `$3E` and `$62` (set by our 5-4 kill frame) and on the
  Start delay. **Procedure when 5-4 is locked: save a NesHawk state on the 5-4 kill row K, run
  `venv/Scripts/python work/l61p/nh_late.py 0,1,2,...,40 --state <name> --kill K`** (about 1.5 min per k), take the smallest good k
  (cost k f; k 0 or 1 if lucky). On the TAS kill the gaps between good k are up to 14 f (k 34 -> 49).
* **Free shifts: none** (Transitions).
* **6-1 J&S variant `pre61js_32595.txt`** (B+Left 31,015-16 breaks the J&S lantern X 528, caught 31,020; extra B+Left 31,057-58 = a
  spin at the thrower; the TAS's later 6-1 air B's become spins): Mesen, all 36 H61 c clean to 31,487; **NesHawk k 0-30: 6-1 passes
  for 29 of 31 k (k 3 / 17 still die at row 194), but room 36 is hit at row ~1,924 (TAS-eq 31,986, the dogs t9; np runs out, so
  the room-36 air B's differ).** Needs a room-36 repair before it is usable; it is the way to make 6-1 itself arrival-proof.
* Not tried: an earlier 32,428 spin for J36; spins at the room-36 throwers for H36.

### Ninpo / art / HP (Act VI: 6-1 -> 6-4a)

* Act VI starts with np 0, no art, hp 16. 6-4a needs **J&S + exactly 5** at the 6-3 exit (one spin, the record's kill);
  ninpo and art are cleared after 6-4a. Leftover ninpo at 6-2 -> 6-3 costs nothing (no boss tally); 6-3 burns the excess with
  free air spins.
* **6-1 lanterns** (`python -m ng.solve.items 6-1`; room 35 runs left, so in order of passing):
  * Star X 1,456 y 160 (TAS passes at y 208: untouched; TRAP only with J&S);
  * +5 X 1,216 (TAS 30,558);
  * **+10 X 1,024 y 160: free** - jump 6 f earlier (A+Left 30,684-85 instead of 30,690) + B+Left 30,688-89 -> +10 on 30,693,
    back on the TAS path by 30,733 (`l1024.py`, 88 cases; NesHawk);
  * Windmill X 800 y 128 (TAS passes at y 134 without a slash: never slash there);
  * +5 X 656 y 128 (TAS y 176; ~15 f, untested);
  * **J&S X 528 y 128: free** (B+Left 31,015-16, caught 31,020) - only for the H61 fix above;
  * **+5 X 240 y 96: free** - B+Left 31,203-04 in the air -> +5 on 31,208 (NesHawk: positions = TAS);
  * +10 X 112 y 96 (TAS y 144; ~15 f, untested).
* **Room 36:** +5 X 1,232 y 160 (TAS y 208: a jump + slash like X 1,024, untested); **Windmill X 1,072 y 112 (TRAP; TAS
  passes under at y 189)**; +5 X 1,056 (TAS 31,935); +10 X 800 y 176 (TAS 60 px above; ~15 f); +5 X 544 (TAS 32,285);
  **J&S X 432 y 80 (TAS 32,353: take)**; **Windmill X 256 y 128 (TRAP: the TAS's 32,483 spin breaks it and catches it -
  drop that B; verified, 0 f)**; +5 X 64.
* **Spins in room 36 (needed):** 32,428 (kills the jetpack ninjas) and 32,531 (the TAS's air slash; with J&S it is a spin).
  Without the 32,531 B, or with Down+B there, Ryu is hit and dies at the exit (tested). The 32,537 B then does nothing.
* **Head start exit: room 37 with J&S + 20, hp 15** (TAS: Windmill + 5). 
* **Rooms 37-40** (TAS line; re-check on ours): Star X 176 / Windmill X 432 / FW X 544 (room 37, TRAPS), +10 X 720 (TAS 32,764),
  +5 X 320 (~8 f); room 38 Windmill X 48 never hangs; room 39 +5 X 272, +5 X 320 (cost 1), +10 X 544 (TAS 33,617); room 40
  +5 X 304, health X 384 y 80, +10 X 512 (cost 1), **InvFW X 560 y 160 (TRAP, on the line)**.
* **6-2 exit target: J&S + >= 10** (the record: J&S/10; 6-3 then needs its own spins + exactly 5 at its exit). With 20 at room
  37 and the TAS-line lanterns (+10, +10) there is room for ~6 spins in rooms 37-40 (the TAS used 2 Windmill throws there).
* HP: the TAS takes 16 -> 15 (32,560, room 36; also on our head start), 15 -> 14 (33,699, room 39), 14 -> 12 (34,200, room 40);
  6-3 and 6-4a refill nothing until 6-4a (boss stages refill). 15 at room 37 is plenty.

### Head start (verified)

* **`work/l61p/pre61_32595.txt` = 2,533 stage rows from the 6-1 control row (row 1 = Left on F = TAS 30,063) to TAS 32,595
  (room 37, the row before its first input).** Legalized TAS rows (1-f A/B held 2 f) + the J&S line in room 36 (no 32,483 B)
  + the free lanterns +10 X 1,024 and +5 X 240.
  * 6-2 control on row 1,576 (F + 1,575 = TAS); **room 37 on row 2,511 (F + 2,510 = TAS 32,573)**; hp 15, **np 20, J&S**.
  * Positions = TAS on every frame except the X-1,024 jump (30,685-30,732) and the 1-px stretch 32,507-32,559.
  * **NesHawk = Mesen on all 2,532 frames** (`nhpre61.py` / `mpre61.py`), at c 84 and at the six spot-check c values.
  * `check_inputs.py --period 5 --hold 2 --release 2 --windows 600:109,1800:246`: PASS (alone; re-judge on the chain, the windows
    cross the 5-4 boundary). `legal_ok` with the TAS's previous rows: ok.
  * **Arrival: NOT independent.** TAS-equivalent on NesHawk for 13 of 61 real Start delays from the TAS kill (above); Mesen `$BF`
    pokes: 136/256. Realistic slot leftovers (5-4 kills delayed 2 / 5 / 11 f) alone change nothing (Mesen); `$3E` does. Fully
    random junk in `$400-$4A7` wrecks it (not a realistic arrival). **Check on the real 5-4 state with `nh_late.py` before grafting.**
* Variant `work/l61p/pre61js_32595.txt` (+ 6-1 J&S and spin, fixes the 6-1 thrower): fails in room 36 on NesHawk (above).
* Room-37 pieces (from TAS states, not chained): `r37_top_32763.txt` (166 rows from TAS 32,596, pillar top on 32,763 = +60),
  room 38 cycle (above), room 39 entry cycle, `r40_plat_33863.txt`.

### Next steps for the 6-1 / 6-2 builders (by value)

1. **Arrival first.** When 5-4 is locked, save a NesHawk state on its kill row and run `nh_late.py` (k 0-40) with
   `pre61_32595.txt`; Start on kill + 595 + k for the smallest good k and graft the head start (room 37 at F + 2,510). If no k <= ~15
   is good, the cheaper fix may be the 6-1 J&S variant with a room-36 repair (6-1 then passes for ~29/31 k).
2. Room 37 (record +102): graft `r37_top_32763.txt`, then repair the run to the exit (lag ~58; soldiers at TAS 32,931 / 32,963,
   the y-160 platform and the y-128 ledge; `r4_62_h2`'s hand line is the model). Target room 38 <= TAS +80.
3. Room 38: the 6-f cycle (+16). Room 39: entry cycle (+23), then the run (the TAS's rows; its Windmill throw 33,319 becomes a
   spin or nothing). Room 40: the entry cycle (+15), the platform line (+2), a short repair for the bird at 33,928, the run.
4. Ninpo: arrive in 6-3 with J&S + >= 10; never touch the room-37 Star/Windmill/FW or the room-40 InvFW.

### Agent notes (6-1 / 6-2)
* **l62 HANDOVER (2026-10-28 ~12:15): 6-2 v2 = complete, judge PASS, NesHawk-verified; 6-1 + 6-2 = record +4.2 (v1 was +27.2).**
  * Power-on **`work/l62/l62_v2_poweron.inputs.txt` (35,799 rows; last row = the 6-3 control row, Right)**; 6-2 stage rows from 33,590:
    `work/l62/l62_s62_v2.txt` (= v1 to the room-40 platform 35,046, then beam `r40w` (high route, width 260, floor penalised before X 620)).
    **Judge PASS. NesHawk from `l62f_34900`: hp 15 -> 12 (35,291) -> 11 (35,518), 6-3 load 35,648, 0 pad-read conflicts, RAM at 35,799 =
    Mesen (0 diffs).** NesHawk states `l62v2_35520` (trigger), `l62v2_35798` (6-3 control - 1). Rows 1-33,589 = `l62_hs_k2` (5-4 Start 30,903-04).
  * **Trigger 35,520 (X 747 y 181), 6-3 load 35,648, 6-3 control row 35,799**; exit **hp 11, np 0, J&S (133)**. `$BF` on the control row
    = **188: not a good room-41 run**; next good = 223 on row 35,834 (+35 f), so no cheap fix (the 35,578-35,610 run is before our trigger).
  * Splits: room 40 + transition 35,799 - 34,877 = 922 f (TAS 849: +73; record +22.4). **6-2 control -> 6-3 control = 3,167 f (record 3,153.2:
    +13.8). 6-1 + 6-2 (31,057 -> 35,799) = 4,742 f vs the record's 4,737.8 = +4.2. From the locked 5-4 control 30,252: 5,547 vs 5,543.1 = +3.9.**
  * Searched and not found (sizes): plain jump from the y-208 floor peaks at y 160 for every hold (proven, 120 cases) -> the y-128 block needs a
    boost or the high route; ghoul/axe boost grid `gb.py` (wait 0-45 x run 0-69 x 1-2 jumps = 6,300 cases from 35,300): no crossing (max X 682);
    room-39 wide re-beam `r39w` (width 250, score X - 3y past X 620): stalled at X 620 y 160, no goal.
  * Where more can come from: room 40's high route (still TAS +73 vs record +22: the record probably does it better), room 39 (+58 vs +21).
    Any room-39 change moves the room-40 arrival (thrower/ghoul phase), so room 40 then needs a re-beam from the platform (`b_r40g` prefix)
    and the high-route beam (`b62.py ... --score 'X-(400 if (y>=200 and X<620) else 0)-0.2*y' --minhp 2`, ~1.5 h at width 260).
* **l62 (2026-10-28 ~10:35) FIRST COMPLETE LEGAL 6-2 (v1), NesHawk-verified - but ~27 f behind the record for 6-1 + 6-2.**
  * Power-on **`work/l62/l62_v1_poweron.inputs.txt` (35,822 rows, last row = the 6-3 control row, Right)**; 6-2 stage rows from 33,590:
    `work/l62/l62_s62_v1.txt`. **Judge PASS.** NesHawk from `l62f_34900`: hp 15 -> 12 (35,292) -> 11 (35,352), 6-3 load 35,671, **0 pad-read
    conflicts, RAM at 35,822 = Mesen (0 diffs)**. NesHawk states `l62v1_35543` (trigger), `l62v1_35821` (6-3 control - 1).
  * Room 40: platform (35,046) -> **high route** (beam `r40h1` + `r40h2` with the floor penalised before X 620: over the X ~432 pillar, along the
    y-96 ledge, X 581 y 48 on 35,418, over the pit, down at X 716 on 35,521) -> end beam `r40t` (an enemy hit at X 743 on the floor knocked
    Ryu back; avoided by a jump) -> **trigger 35,543 (X 748, y 173)**, **6-3 control row 35,822** (= trigger + 279; Right from trigger + 1),
    6-3 load 35,671. Exit **hp 11, np 0, J&S (`$C9` 133)** - meets the J&S + 0..4 target.
  * **6-3 control `$BF` = 211: NOT in a good room-41 run** (113-122 / 223-255). The next good row is 35,834 (`$BF` 223) = +12 f; 35,578-35,610
    is out of reach (our trigger is later). No free frames: the control row is fixed at trigger + 279.
  * Splits (from the room changes; record = record split vs TAS): 6-1 + room 36 = TAS +0 (k 2 Start: +2); room 37 +97 (record +102.1);
    room 38 +16 (record +28.2); room 39 +58 (record +20.8); **room 40 + transition: 35,822 - 34,877 = 945 f vs TAS 849 = +96 (record +22.4)**.
    **6-2 control -> 6-3 control = 3,190 f vs the record 3,153.2 = +36.8; 6-1 + 6-2 (F -> 6-3 control) = 4,765 vs 4,737.8 = +27.2.**
    5-4 + 6-1 + 6-2 from the locked 5-4 control 30,252: 5,570 vs the record's 805.3 + 4,737.8 = 5,543.1 -> **+26.9 behind** (the chain's
    cumulative lead is large, so a lock would still be under the record overall, but 6-2 itself is not under its split).
  * Where to gain: room 40 (+96 vs record +22) and room 39 (+58 vs +21). Running next: the ghoul-boost floor route (`gb.py`; the floor line
    is ~35-40 f ahead of the high line at X ~490) and wider beams.
* **l62 (2026-10-28 ~09:35) room-40 pit: the floor jump is proven too short; the high route is working (paused for RAM).**
  * **Proven: a plain jump from the y-208 floor peaks at y 160 (48 px), so it can never reach the y-128 block.** Grid from our 35,300 state
    (X 494 floor): jump start 35,301-35,312, A held 2/4/8/16/30 f, Right or neutral (120 cases, `work/l62/jh.py`): apex y 160 in every case.
    The y 129-133 apexes seen in the beams came from hits / other boosts, not jumps. Floor-only beams without a boost are pointless.
  * **High route (beam `r40h1`, from the y-96 platform 35,046 = `b_r40g.txt`, floor penalised before X 620):** stays high via the X ~432
    pillar (Ryu at X 428 y 160 on 35,257, over it by 35,307) and is **on the way onto the y-96 ledge: X 477 y 84 on 35,337** (hp 12: one
    3-hp hit on the way, J&S kept, np 0). Stopped there because free RAM fell under 800 MB (owner's game). **Checkpoint rows
    `work/l62/r40h1_ckpt.txt`** (rows from 33,590 to 35,337). For comparison the floor line was at X 497 on 35,302, so the high route costs
    ~+35-40 f to here but avoids the thrower/ghoul and the pit.
  * Ghoul-boost wait grid (`gb.py`, 6,300 cases) was killed with the RAM drop before it reported; not run.
  * **Resume:** `python -u work/l62/b62.py 33589 0 r40h2 --mst states/mesen/l62_33589.mst --prefix work/l62/r40h1_ckpt.txt --goal
    'X>=704 and y==208 and rm==40 and it==133' --score 'X-(400 if (y>=200 and X<620) else 0)-0.2*y' --frames 300 --width 150 --minhp 2
    --dbg 10 --alpha 'Right|A+Right|B+Right|-|A|B|Left|A+Left'`, then `fin.py` -> judge -> `nhrun.py ... l62f_34900 34901 <end> 0`.
* **l62 HANDOVER (2026-10-28 ~08:30; my emulators stopped): the room-40 pit is still open; no 6-3 control row yet.**
  * After the previous bullet: 4 more beams from our real line (Mesen; low-RAM mode, 1-2 at a time), all **without a crossing**:
    `r40n` (from the 35,357 checkpoint, goal far floor X >= 704 y 208, 140 f), `r40o` (from 35,300, same goal, 220 f, width 200: best nodes
    reach X 620 y 133 on 35,391, then all fall into the pit by 35,471), `r40p` (from 35,300, goal "on the y-128 block" y <= 130 and
    636 <= X <= 690, width 250: best X 624 y 129 on 35,431, no goal), `r40q` (same with a bonus for taking hits; stopped: it picked up another
    item (`$C9` 132) on the way, a trap to avoid). Last best rows: `work/l62/b_r40p_last.txt`.
  * **What blocks it (our arrival):** at X 585-600 on the y-208 floor stand a **thrower t2 (axes t18)** and a **jumping ghoul t15** (around
    35,346-35,416; the `r40l` checkpoint takes an axe hit at 35,357). The TAS crosses the pit X ~624-703 via the **y-128 block at X ~640-671**,
    reached by a **ghoul damage boost** (hp 14 -> 12 on TAS 34,200 at X 632 y 164), then walks off its right end onto the X-704 floor. A plain
    jump from the floor tops out at ~y 133 near X 620 in our beams: about 5-15 px short of the block. **Not proven impossible without a boost.**
  * **Next steps:** (1) find the ghoul boost on our phase: a grid/beam from ~35,300 that walks into the t15 while it is near y ~165-185 with
    Ryu rising (2 hp), goal = on the block (or `X >= 704 and y == 208`); or a wait at X ~560 so the ghoul / axe phase matches the TAS's;
    (2) alternatively check the high route (y-96 ledge X ~480-575 '5777774', then a jump right onto the y-128 block: a 65-px gap dropping
    32 px); (3) then `python work/l62/fin.py <rows> <stage out> <poweron out>`, the judge, and `nhrun.py <poweron> l62f_34900 34901 <end> 0`.
    6-3 control target: a good room-41 `$BF` run, rows 35,578-35,610 (cost <= ~5 f) or 35,724-35,733 / 35,834-35,866; np <= 4 (np is 0 now).
  * Low-RAM note: `lib62.py` and `b62.py` set the Mesen free-RAM floor to 1.2 GB (fastcore's default 2.5 GB refuses to start otherwise).
* **l62 STATUS / RESUME (2026-10-28 ~07:25; all my emulators stopped).** Built and NesHawk-verified from power-on to the room-40 platform
  approach; the room-40 run to the 6-2 -> 6-3 trigger is NOT finished.
  * **Verified chain:** `work/l62/l62_po_r40f.inputs.txt` (34,924 rows; judge PASS): 5-4 Start 30,903-04, **6-1 control 31,057**, 6-2 control
    32,632 (F + 1,575 = TAS), room 37 33,567 (TAS + 994 = +0), **room 38 34,261 (+97)**, **room 39 34,375 (+113)**, **room 40 34,877 (+171 vs TAS
    33,712; the record's room-40 change is TAS +207.0 -> we are ~-36 vs the record there)**, hp 15, np 0, J&S. NesHawk = Mesen (0 RAM diffs at
    33,589 / 34,397 / 34,924). NesHawk states: `l62_k30306`, `l62_31056`, `l62_32631`, `l62_33567`, `l62_33589`, `l62e_34260`, `l62e_34397`,
    `l62f_34900` (room-40 control - 1). Mesen: `states/mesen/l62_33589.mst` (room 37), `states/mesen/l62e_34397.mst` (room-39 control - 1).
  * **Room 40 so far (Mesen only):** `work/l62/b_r40g.txt` (rows from 33,590: entry cycle x4 + staircase beam) -> on the y-96 platform
    (X >= 112) on 35,046; then beam `r40l` checkpoint **`work/l62/r40l_ckpt_35357.txt`** (rows from 33,590 to 35,357: X 578 y 208 on the
    floor, hp 14, np 0; the run along the top and down to the floor at pure 1.5 px/f, ~TAS + 27 from the platform; one 1-hp hit).
  * **Open problem = the pit X ~624-703 on the y-208 floor before the exit floor (X 704-751; trigger at X 747 y 208).** The TAS crosses it with a
    jump at X 609 (34,185) and a damage boost (hp 14 -> 12 on 34,200, enemy near X 630 y 160) up to y 128, then right to X 709 y 156. My
    X-scored beams fall in (`r40i`: best X 694 y 205, then all nodes die); a height-penalty score made a false wall at X 590 (`r40m`). Not
    tested yet: a beam from the 35,357 checkpoint (or from ~35,300) with goal `X >= 704 and y <= 208 and rm == 40` (land on the far floor),
    hits allowed (`--minhp 2`), score `X - 0.5*y`, alphabet incl. A+Right / B+Right / A. Then `python work/l62/fin.py <rows> <stage out>
    <poweron out>` (finds the trigger = `$5C` 2 -> 0 in room 40, holds Right to trigger + 279 = 6-3 control, writes the power-on file), judge,
    and `python work/l62/nhrun.py <poweron> l62f_34900 34901 <end> 0` for the NesHawk check.
  * **Expected finish:** if the pit costs ~the TAS's line, trigger ~35,47x-35,49x -> 6-3 control ~35,75x-35,77x = 6-2 control + ~3,120-3,140
    vs the record's 3,153 (about -15..-35). 6-3 control `$BF` = (row - 27) mod 256: the good runs 113-122 / 223-255 are rows 35,724-35,733 and
    35,578-35,610 / 35,834-35,866; report the real one after `fin.py`.
  * Ninpo: np 0 from room 39's exit on (coordinator's new target J&S + 0..4 at the 6-3 control is met so far; skip the room-40 +5 X 304 /
    +10 X 512 or burn them with air spins). J&S held throughout.
  * Tools: `work/l62/b62.py` (beam; `--mst`, `--poke`, `--minnp`, checkpoint file `b_<tag>_ckpt.txt` every `--dbg` frames, Mesen RAM floor
    lowered to 1.2 GB for low-RAM mode), `ch62.py` (rooms 37-40 chain), `mk40.py`, `fin.py`, `nhrun.py`, `mkm.py`, `tr.py`, `mkpo.py`/`mkpo2.py`.
* **l62 (2026-10-28 ~06:05) room 39 + room-40 entry on our real line (NesHawk-checked to room 40); room-40 rest beam running.**
  * Ninpo target noted (coordinator): **J&S + 0..4 at the 6-3 control**. Our line is at np 0 from room 39's exit on; the room-40 beam requires
    np < 5 at the trigger.
  * **Room 39** (real state; the thrower t2 / axes at X ~547 read the arrival, so TAS-state rows die): entry cycle (`r39_ent84.txt`) + beam
    `b_r39d` (score X, width 150: room 40 on 34,897) + end re-beam `b_r39f` from 34,800 (score X - 3y: the exit (667, 84) is a climb):
    **room 40 on 34,877 = room 39 in 502 f (TAS 444: +58; record +20.8)**. One spin for the batter t3 (np 5 -> 0), +10 lantern X 544 taken
    and spent (2nd spin), a 3rd spin at the exit climb. hp 15. Rows: `work/l62/b_r39f.txt` (from 33,590, through room 37-39).
    Power-on `work/l62/l62_po_r40f.inputs.txt` (34,924 rows): **judge PASS; NesHawk from `l62e_34397`: room 40 on 34,877, events = Mesen,
    0 pad-read conflicts, RAM at 34,924 = Mesen (0 diffs)**; NesHawk state `l62f_34900` (room-40 control - 1).
  * **Room 40 entry** (control = change + 23; the cycle from change + 24 = TAS's): `[Left, A+Left, A, A+Right, Right, Right] x4` then beam
    `b_r40g` (staircase y-192 -> y-160 -> y-128 ledge -> y-96 platform): **on the platform (X >= 112, y <= 96) on 35,046** = change + 169
    (TAS: X 112 on the platform ~ change + 145). Over-the-wall route (climb the X-160 face, which IS a ladder from the left at 1 px/f, to
    y 131-148, then right over the wall): **not found** (beam `r40h` width 200, 130 f; cycle grids `cyc_r40top.out` / `r40top.py` found only
    false goals = falls into the pit; not proven impossible).
* **l62 (2026-10-28 ~04:15) rooms 37-38 built on our real arrival (NesHawk-checked), room 39 being re-beamed on it.**
  * **Room 37** (from `states/mesen/l62_33589.mst` = our NesHawk room-37 state): `r37_top_32763.txt` (pillar top 33,756 = TAS-eq +58), beam
    `b_r37a` (X <= 380 on the y-208 floor at 34,073 = +79; the TAS's 32,754 slash at the X-719 t1 (a gun turret that hurts on contact and fires
    t17 shots; the TAS kill gives +10) becomes a J&S spin that misses it, so the TAS rows at lag 58 are hit at 33,819), beam `b_r37e`
    (score -X + height below X 330) -> **room 38 on 34,261 = TAS +97 (record +158.8 from the 6-2 control: -62)**, hp 15, np 20 -> 5 (4 spins,
    +10 and +5 lanterns). Rows `work/l62/b_r37e.txt` (from 33,590). With np kept >= 10 (`b_r37g`, minnp 10): 34,279 (+18 f); minnp 15: no goal.
  * **Room 38**: 6-f cycle `[Left, A+Left, A, A+Right, A+Right, Right]` from change + 24 (earlier starts are slower, `r38t.py`): **room 39 on
    34,375 (114 f, TAS +16)**. Power-on `work/l62/l62_po_r38e.inputs.txt` (to 34,397): **judge PASS; NesHawk from `l62_33589`: room 38 34,261,
    room 39 34,375, end RAM = Mesen (0 diffs)**; 1 pad-read conflict (34,357 Left read as Right) without effect. NesHawk states `l62e_34260`,
    `l62e_34397`; Mesen `states/mesen/l62e_34397.mst` (room-39 control - 1).
  * **Room 39 depends on the arrival** (thrower t2 / axes t18 at X ~547): TAS-state beams (`b_r39a` np 20: room 40 +35; `b_r39b` np 5: room 40
    on TAS 33,738 = +26, one spin for the batter t3 (the TAS's Windmill kill) + the +10 lantern skipped) die at the axes on our real state.
    Legal room-39 entry: `[Right, A+Right x3, A+Left, Left] x5` + Right (`r39_ent84.txt`, +23). Needs >= 5 np for the batter spin
    (np 0-4: hit and death later). Re-beam from our state running (`b_r39c`).
  * **Room 40 entry**: the X-160 face IS a ladder from the left (Up = 1 px/f, y 232 -> 148 by 33,819 TAS-eq) but hangs at y 148; the
    staircase line (entry cycle + y-192 -> y-160 -> platform) costs ~+35 on TAS states (`b_r40d` y-160 at 33,805 is passing, not standing;
    `r40e` platform not reached in 110 f). Cycle grid for climbing the face onto its top (`cyc_r40top.out`, 7,350 legal cases) running.
* **l62 (2026-10-28 ~03:10) TASK 1 ANSWER for the locked 5-3 (kill 30,306): press Start on 30,903-04 (kill + 597) -> 6-1 load 30,905, 6-1 control
  row F = 31,057.** Full k table (`work/l62/nh_late_k30306.out`, Start = kill + 595 + k): k 0-1 (and the file's own kill + 594) die at head-start
  row 553; **k 2-7 good**; k 8-9 bad. Cost: 2 f over the earliest control (31,055). Rows 30,252-30,899 unchanged from the locked file; rows
  30,900-30,902 blank, Start 30,903-04, blank to 31,056, head start from 31,057 = `work/l62/l62_hs_k2_poweron.inputs.txt` (judge PASS,
  NesHawk-verified to room 37 = 33,567, see the next bullet). The np-15 forecast below is obsolete (coordinator: kill 30,306 is the real one).
  The J&S variant could at best save these 2 f (needs k 0/1 + a 0-f room-36 repair); being checked on NesHawk (`nh_late_js_k30306.out`).
* **l62 (2026-10-28 ~02:40) TASK 1 DONE: 6-1 arrival on our line = Start 2 f later than the earliest, head start TAS-exact on NesHawk to room 37.**
  * **Real kill 30,306 (`work/l53c/v1c_cn1_poweron.inputs.txt`)**: NesHawk state `l62_k30306` (frame 30,308 = after the kill + the
    file's two A+Right rows; from `l53c_30251` + the file's rows). `nh_late.py --state l62_k30306 --kill 30306` (Start = kill + 595 + k):
    **k 0, 1 bad (hit at head-start row 553), k 2 good** (k 3-6 also good, 7 bad at row 384...; scan stopped at k 9). So **Start on
    30,903-04 (kill + 597), 6-1 load 30,905, 6-1 control row F = 31,057** (c = `$BF` 54; 2 f behind the earliest 31,055), 6-2 control
    32,632, room 36 change 32,481, **room 37 change 33,567 (= F + 2,510 = TAS 32,573 + 994, i.e. TAS +994 exactly, cost vs TAS = the 2 f)**,
    hp 15 / np 20 / J&S.
  * Power-on file `work/l62/l62_hs_k2_poweron.inputs.txt` (33,589 rows = candidate rows 1-30,899, Start 30,903-04, head start
    `pre61_32595.txt` from 31,057): **judge PASS**. **NesHawk full replay (`work/l62/nhrun.py` from `l62_k30306`)**: room/np/hp events = the
    head start's; positions = TAS + 994 on every frame except the known X-1,024 jump (31,679-31,726) and the 1-px stretch (33,501-33,553);
    **1 pad-read conflict (31,840, B+Left read as Left) with no effect**. NesHawk states `l62_31056` (6-1 control - 1), `l62_32631` (6-2
    control - 1), `l62_33567`, `l62_33589` (room 37, the row before its first input). **Mesen state `states/mesen/l62_33589.mst`** (from
    `l53c_v1_29336.mst` + the file with the 31,840 conflict applied, `work/l62/mkm.py`): **0 RAM diffs vs NesHawk** (stack excluded) - build
    rooms 37+ from it. Diffs vs the TAS's 32,595: `$3E` 2/3, `$62` 46/0, `$BF` 26/56, np 20/5, item 133/130, slot junk.
  * **np-15 line forecast (kill 30,292; POKED, not real):** `l53c_30251` with `$BF` -14, `$62` +14, `$3E` +2 mod 6 (`work/l62/mkfc.py`, state
    `l62_np15fc_30308`): **k 0 good** (Start kill + 595 = 30,887, 6-1 control 31,041, room 37 on 33,551); good k: 0, 6, 9, 10, 13, 14, 17, 19,
    23, 28, 31-33, 36 (`work/l62/nh_late_np15fc.out`). Re-check on the real np-15 kill state when it exists (same command, ~1.5 min per k).
  * Cost vs TAS for 6-1 + room 36: +2 (kill 30,306 line) / +0 forecast (np-15 line). Record: 6-2 control <= F + 1,584 -> we are at F + 1,575 (-9).

## Next: 6-3 / 6-4 plan (prep agent l63p, 2026-10-28)

Act VI after 6-2: **6-3** = rooms 41 (runs right), 42 (one screen: up to the top left), 43 (long, runs LEFT, X 1,976 -> 113),
44 (runs right, X 92 -> 1,003). Then the boss rush, which the game splits into three stages (`$6D` 19 / 20 / 21):
**6-4a = room 45, the Masked Devil** (target = its orb, slot 6 id 36, x 135 y 120, 16 HP); **6-4b = room 46, Jaquio**;
**6-5 = room 47, the Demon** (the pod, slot 6 id 38, first; then the heart, slot 7 id 40). The run ends in the 6-5 timer tally.
**A death at any of the three bosses sends Ryu back to 6-1** (seen in the scans: `$6E` 35).

**Headline.** We reach 6-3 about 600 f ahead of the record (6-3 control ~35,700 on l62's line vs the record's ~36,290). From its
6-3 control the record needs 5,485 f to TIMER-000, the TAS 4,969. Our legal pieces (from TAS states) add up to 6-3 = TAS +144
(record -52) plus whatever the joins cost, and the bosses run at record pace, so the run should finish ~550-600 f under the record.
**Build for safety, not frames**: hp, no deaths, arrival-proof pieces. Four findings change the plan:
1. **The TAS's 6-3 leans on its Windmill star** (thrown 35,989 / 36,126 / 36,426; `$C8` = 1 from 36,426 to 37,084, through room 44).
   On a J&S line the star is missing: Ryu is hit at X 287 (room 43, 36,319), X 891 (37,042) and X 974 (37,097) in room 44, and the
   room-44 +10 lantern (X 528, the TAS catches it on 36,767 through the star) is not broken. Fixes found (beams from TAS states with J&S
   poked): **room 43 end +3** (`r43j_36440.txt`, a jump-slash at 36,318), **+10 X 528 = an air B+Right on 36,772-73 in the TAS's own
   jump (0 f)**, **room 44 end +3** (`r44j_37121.txt`: two spins, 37,040 and 37,093, np 15 -> 5, no hit, trigger 37,121).
2. **With J&S and ninpo >= 5 every TAS air B becomes a spin** (also Down+B with a direction held; only Down+B with no direction is a
   plain slash in the air). On the TAS line that wrecks room 41 (an extra hit) and room 43 (the 35,312 spin breaks the **Star
   lantern X 1,760 and Ryu catches the Star**). **With J&S and ninpo 0-4 the TAS's air B's stay slashes and the legal TAS rows
   are TAS-exact** (rooms 41, 43a, 43b, 44a; NesHawk). So **arrive in 6-3 with J&S + 0..4**, not + 10.
3. **6-4a with J&S + 10 (two spins) kills on control + 74 = the record's kill; J&S + 5 kills on control + 89** (one spin = 11 hits,
   then 5 slashes). Both $BF / $3E-independent. So **6-3 should exit with J&S + exactly 10** (pick the ninpo up late in 6-3).
4. **6-5 (the Demon) is arrival-dependent**: the old legal kill `a56_6-5_r2d5` works for only 75 of 256 `$BF` values (the rest die
   -> back to 6-1). Jaquio (`r4k2`) and the Masked Devil are `$BF`-independent.

Tools and data in `work/l63p/` (frames = power-on rows on the TAS axis; NesHawk frame k = after row k):
* `dumps.py` -> `tas63_ram.bin` (NesHawk TAS RAM 34,563-39,700); `lib0.py` (`TM(f)`, `XY`; falls back to the l61p/l53p dumps);
  `lib.py` (Mesen helpers on top of l61p's, `core_at(f)`); `mkst.py` -> Mesen TAS states `states/mesen/l63p_tas<f>.mst` (34,560 -
  39,600, every 50-100 f + every event; 0 RAM diffs vs NesHawk in play, resynced in the load cutscenes where Mesen's step() is 1 f
  off); `ev.py` -> `tas63_ev.txt`; `tasview.py f0 f1 step` (TAS rows, X,y, hp/np/item, slots); `brk.py` -> `brk63.out`; `roommap.py`.
* NesHawk: **`nh_trans63.py`** (TAS rows to K, Start variants, pokes; load / control / P / E / END seen), `tallyscan.sh`, `endscan.sh`;
  **`nhtf.py`** (legalized TAS rows or a rows file from a TAS frame, with `--js 1`, `--poke`, `--ov`; divergences and events);
  **`nhgrid.py`** (override variants, hit / goal per variant); **`nhbf.py`** (arrival scan: poke `$BF` or any byte per value; classes
  and the first diverging enemy slot); `nhsave.py` (save a NesHawk state after a rows file). `nh_trans63.py --rows f --rows-start F
  --prepoke ..` measures the Start rule after our own rows.
* Mesen: `tf.py`, `grid.py`, `cyc.py` (`--both 1`: the cycle must hold A+Left and A+Right), `seqgrid.py` (explicit candidates from a
  generator file `gen_*.py`), `b63.py` (beam), `bossbf.py` (boss kill frame vs `$BF` / `$3E`), `mdjs2.py`-`mdjs4.py`, `mdshow.py` (6-4a).

### Transitions (NesHawk, TAS path)

* **6-2 -> 6-3** (l61p): 6-3 control = trigger + 279 (Right; TAS 34,561).
* **6-3 -> 6-4a: needs Start.** Trigger = first frame `$5C` = 4 (Ryu at the room-44 exit X 1,003 y 208; TAS 37,118).
  **Start (2 f) on trigger + 5 or + 6 -> 6-4a load (`$6D` 19) on trigger + 8**. Starts on + 1..+ 4 do nothing; without Start Ryu
  stands forever; later Starts cost 1:1 (+ 7 -> load + 9, + 8 -> + 10, + 12 -> + 14). **6-4a control = load + 152 = trigger + 160**
  (the first row on which Right moves Ryu; TAS 37,278). HP refilled to 16 on trigger + 7. Same rule as 5-3 -> 5-4. One free frame.
* **Boss kill -> next stage (6-4a -> 6-4b and 6-4b -> 6-5): needs Start.** Kill K = first frame `$66` = 0. With T = `$63` after the
  kill row and np = `$64` at the kill: **earliest Start S0 = K + 3T + 3np + c, c = 146..148** (a fresh 2-f press; Start on S0 + 1 gives
  the same load; every later row costs 1); **load = S0 + 3; next control = load + 152**. c = 146 on the TAS's 6-4a and 6-4b kills and
  on `r4k2`'s, 147 on our `md_js10` kill (37,352: Start 37,943, load 37,946, control 38,098) and on l61p's 5-4 kills, 148 on l61p's 29,317 kill:
  **measure c on the real kill** (`nh_trans63.py <state> K --rows <file> --rows-start <first row> --prepoke .. --start ..`).
  * Measured: 6-4a TAS K 37,339, T 149: Starts 37,929-31 nothing, 37,932 / 37,933 -> load 37,935, control 38,087; 6-4b TAS K 38,188,
    T 148: Start 38,778 / 38,779 -> load 38,781, control 38,933.
  * Pokes at K (6-4b): np 1 -> + 3, np 5 -> + 15, T 147 -> - 3, T 145 -> - 9; `$62` 0 / 1 / 30 / 58 / 59 / 60 and `$3E` 0-5 poked
    after the kill -> no change (so c is set before the kill). Inputs during the tally change nothing (TAS rows vs blank).
  * Old a56 files press Start late: `a56_6-4b_r4k2` (K 38,340, T 145) has Starts on 38,919 (ignored) and 38,924 -> load 38,926; the
    earliest (38,921) gives 38,924 (2 f better).
* **The timer.** `$62` counts 60 -> 0, then `$63` - 1 (61 frames per timer second); it is frozen through every load and carries on.
  T at a kill = 150 - ticks since the stage control; ticks on control + `$62`(control) + 1 + 61 j (TAS 6-5: control 38,933 with `$62`
  28 -> ticks 38,962 / 39,023 / 39,084). **A kill on a tick frame or later is 3 f better than one frame before it**; a kill d frames
  later across one tick costs d - 3. Example: our 6-4a kill on control + 74 gets T 148 only if `$62`(6-4a control) <= 12, else 149 (+3).
* **6-5 -> END: no Start.** **P = K + 3T** (first frame `$63` = 0, stage 21); **E = first frame > P with `$3E` = 1; END seen = E + 1
  = P + 2 .. P + 7** (`knowledge/clock.md`). `$3E` steps 5, 4, .., 0, 5 every frame of play and tally. NesHawk from the TAS kill
  (39,084, T 147, P 39,525) with `$3E` poked 0-5 and T 145 / 146 / 147: END seen = P + 2 .. P + 7 exactly by the rule (TAS: E 39,529,
  seen 39,530). `$3E` runs on through the fight, so END seen only depends on where P falls in the arrival's 6-frame `$3E` grid:
  **a kill up to 5 f later can be free, a kill 1 f earlier can gain 6.**
* The run beats the record iff **END seen <= 41,774** on our axis (START seen 175 + the record's 41,599.4 NES frames = 692.183 s).

### Splits (record: video frames x 60.0988/60 from its "control (est.)"; rooms: `dark_first_f` of the 22-f black = room change)

| piece | TAS f | TAS end frame | record | record - TAS | best legal piece (from TAS states, NesHawk-checked) |
|---|---|---|---|---|---|
| room 41 (control -> room 42) | 429 | 34,990 | 448.7 | +19.7 | **+2** (`r41_34992.txt`; arrival-dependent) |
| room 42 | 155 | 35,145 | 216.4 | +61.4 | TAS side: entry **+9** (`r42e_35056.txt`), exit NOT found legally; **the record's line (a56 `r4_63_h4`): 220 f = +65** |
| room 43 | 1,292 | 36,437 | 1,364.2 | +72.2 | entry C8 **+6**; X-762 face **+24**; X-569 face **+4**; rest = TAS; J&S end **+3** (`r43j_36440.txt`) -> **~+37** |
| room 44 + transition | 841 | 37,278 (6-4a ctl) | 883.5 | +42.5 | entry **+20**; X-552/572 wall **+17**; +10 X 528 0 f; J&S end **+3** (`r44j_37121.txt`) -> **~+40** |
| **6-3** | **2,717** | | **2,912.8** | **+195.8** | **sum of pieces: 2 + 65 + 37 + 40 = TAS +144 = 2,861 (record -52) + join costs** |
| 6-4a control -> kill | 61 | 37,339 | ~74 | ~+13 | **J&S + 10: 74 (`md_js10.txt`)**; J&S + 5: 89 (`md_js5.txt`) |
| 6-4a control -> next control | 809 | 38,087 | 819.3 | +10.3 | J&S + 10: **820 (record +0.7**; NesHawk: kill 37,352, T 148, Start 37,943, control 38,098); J&S + 5: ~835 |
| 6-4b control -> kill | 101 | 38,188 | ~259 | ~+158 | `r4k2`: 253 (T 145) |
| 6-4b control -> next control | 846 | 38,933 | 997.6 | +151.6 | `r4k2` + earliest Start: **989 (record -9)** |
| 6-5 control -> kill | 151 | 39,084 | ~313-318 | ~+165 | `r2d5`: 316 (T 145), only 75/256 `$BF` |
| 6-5 control -> END seen | 597 | 39,530 | 755.2 | +158.2 | `r2d5`: **753 (record -2)** |
| **6-3 control -> END seen** | **4,969** | | **5,485.1** | **+516** | **~5,430 + joins (record ~-55 + joins)** |

Record pace on our axis: **6-4a control <= F3 + 2,912; 6-4b control <= F4a + 819; 6-5 control <= F4b + 997; END seen <= F5 + 755**;
whole run END seen <= 41,774. Record kills = its bar-empty frames checked with the kill -> next-control rule (the bar empties a few
frames after `$66` = 0 in the video). TAS = 4751M replay.

### TAS rule breaks (`brk63.out`), banned vs legal, with the legal version

| TAS rows | what | banned part | legal version / verdict |
|---|---|---|---|
| 34,561-34,989 (room 41) | run right, 1-f turn Left 34,891 + 1-f B 34,893, bird hit 34,941 (hp 12 -> 11) boosts Ryu onto the y-128 ledge | 1-f presses | **Left 34,891-92 (2 f) + Right through 34,992 -> room 42 on 34,992 = TAS +2** (`grid.py`, 144 turn/slash variants: only Left 34,891-92 works). Without the boost: no way found (312 jump-pair cases from 34,930 `sg_r41n`, beam width 100 / 140 f with no hp loss `b_r41n`: Ryu never gets above the y-160 level) |
| 35,014-35,045 (room 42 entry) | wall jump off the right side, L+R 35,015 and 35,041-45 (moonwalk right onto the y-160 platform while facing left) | L+R, 1-f | **`[Right, Left, Left, A+Left, A+Right] x 4`, then Right -> platform (X >= 160, y 160) on 35,056 = TAS +9** (`cyc.py`, 604 legal cycles; NesHawk: y 160 on 35,052-54, X 18 px behind = 12 f incl. room 41's 2) |
| 35,098-35,144 (room 42 exit) | chimney X 215-235: 1-f A+Left / A+Right, L+R 35,099; **U+D+L 22 f (35,123-44): left at 1.5 px/f while facing right** over the X-208 wall to the exit (184, 75) | U+D, L+R, 1-f | **not found legally.** The chimney climb itself is legal (beam `b_r42y` from 35,097: (215, 87) on 35,116 and y 66 on 35,128 = TAS), but facing right Ryu only drifts left at 0.5 px/f and clings to the X-208 face at y 57-72; he never gets left of X 207 (beams `b_r42y` / `b_r42z` (score switches to -X above y 64), width 120-150, 90-110 f; two-wall cycles `sg_r42c` 968; wall-top cycles after the climb `sg_r42t` 768; L5-6 cycles 624; beam `b_r42x`). **Use the record's line** (a56 `logs/r4/r4_63_h4.inputs.txt`: left along the y-208 ledge, X-73 column, 4 C8 cycles, y-96 platform, exit jump): room 43 on 35,212 = TAS +67 from the stage start (NesHawk; in `pre63_35212.txt`) |
| 35,169-35,230 (room 43 entry) | chimney X 1,945-47, 1-f A taps, L+R 35,185, U+D+L 21 f | U+D, L+R, 1-f | **a56's C8: `[A+Left x2, Right x6] x 3`, A+Left x2, Left -> (1,879, 192) on 35,238 = TAS +6** (NesHawk, from TAS 35,168). L5-6 cycles: none (755 legal) |
| 35,231-35,981 | long run left; hit 35,815 (hp 11 -> 8) as in the TAS | 1-f | **legalized TAS rows = TAS** (NesHawk; with J&S np 0 too) |
| 35,982-36,007 | X-762 face: A+Right / A+Left on consecutive frames, B+Up (Windmill) | 1-f, period < 5 | **beam `b_r43y` (score -y - 0.2X): top (X <= 739, y <= 128) on 36,031 = TAS +24** (`r43w_36031.txt`, 50 rows from TAS 35,982; NesHawk = Mesen). Slower: `[A+Right x3, Left x9] x 5` +50 (`r43w_36057.txt`); L5-6 cycles none (860); beam with score -X-y none |
| 36,008-36,120 | run | - | = TAS (also J&S np 0) |
| 36,121-36,141 | X-569 face, same taps + B+Up | 1-f | **beam `b_r43y2`: `A+Right x2, A+Left, Left x12, A+Right x2, Left x4, A+Right x2, Left x2` -> top on 36,145 = TAS +4** (`r43w2_36145.txt`; NesHawk). Slower cycle `[A+Right x2, Left x8] x 6` +38 (`r43w2_36179.txt`) |
| 36,142-36,437 | run to the exit, B+Up 36,426 (Windmill) | 1-f | with the Windmill: = TAS (room 44 on 36,437). **With J&S np 0: hit at X 287 on 36,319** (the star thrown on 36,126 killed it). **Beams `b_r43j` + `b_r43k` from 36,280 (J&S np 0, star removed, no hit; a jump-slash A+B+Left on 36,318 kills it): room 44 on 36,440 = TAS +3** (`r43j_36440.txt`, NesHawk). A '-X' beam alone runs past the exit (the TAS wall-jumps at (133, 128) on 36,422; 649 jump-pair cases after it: none); score -y - 0.5X finds it |
| 36,461-36,535 (room 44 entry) | chimney X ~92-106, L+R 36,462-75 / 36,490-521 (moonwalk right over the wall while facing left) | L+R, 1-f | **`[A+Right, A+Right, A+Left, Left, -] x 5`, then Right -> floor y 208 on 36,567 (X 188) = about TAS +20** (`cyc.py`, 755 legal; NesHawk; Ryu walks over the right wall's top at y 160) |
| 36,536-36,789 | run | - | = TAS (also J&S np 0); **the +10 X 528 lantern (TAS 36,767) breaks only through the star: on J&S an air B+Right on 36,772-73 (or -74, -75) in the TAS's own jump takes it on 36,775 and Ryu reaches the wall at the TAS's (553, 160) on 36,790 = 0 f** (NesHawk, 14 slash frames tried; an extra jump + slash costs the wall height) |
| 36,790-36,849 | wall X 552-572: Left / A+Right every 4 f, U+D+L 36,801, A+Left / A+Right 1-f, then L+R over the top | period 4, 1-f, U+D, L+R | **beam `b_r44w` -> X >= 603, y <= 100 on 36,867 = TAS +17** (`r44w_36867.txt`, rows from TAS 36,791; NesHawk = Mesen). L5-6 cycles: none (1,075 legal) |
| 36,829-37,116 | 288 f L+R: running right at 1.5 px/f while facing LEFT (no wall cling; slash backwards at 37,084 kills t15 and breaks the FW X 944; FW caught 37,085, thrown 37,110 for 2 free orb hits) | L+R | **Right instead = TAS positions to 37,097** (NesHawk, Windmill item). On J&S: hits at X 891 (37,042) and X 974 (37,097), and jumps there risk the **Windmill lantern X 880 y 160 (TRAP)**. **Beams `b_r44k` + `b_r44m` from 36,990 (J&S np 15, star removed, item kept): spin (A+Right 37,039, B 37,040) clears X 891, spin B 37,093 clears X 974, no hit, trigger on 37,121 = TAS +3, np 5** (`r44j_37121.txt`; NesHawk: Start 37,126-27 -> load 37,129, 6-4a control 37,281). Without spins (Down+B only, `b_r44j`) or by grid (40 variants) nothing passes: all hit or catch the Windmill |
| 37,278-37,339 (6-4a) | Down+B every 2 f (13 hits), FW 2 free hits | press cap | **J&S + 10: `md_js10.txt`** (A, A+Right onto the left pedestal, A+Right x2 37,301, spin B+Right 37,304 (11 hits), drift, land on the middle pedestal at x 108, A x2, spin B 37,348 -> kill 37,352 = control + 74, hp 16). **J&S + 5: `md_js5.txt`** (same spin + jump + `Down|Down+B|B|-|-` slashes -> 37,367 = control + 89). One spin can do at most 11 hits here (1,352 + 1,024 cases, `mdjs2/3`) |
| 38,087-38,188 (6-4b) | U+D+L between Down+B every 2 f | U+D, cap | **a56 `r4k2`** (`jq_r4k2_kill.txt`): kill control + 253, hp 16 |
| 38,933-39,084 (6-5) | Down+B every 2 f, L+R 39,069 | cap, L+R | **a56 `r2d5`** (`dm_r2d5_kill.txt`): kill control + 316, hp 12, only for 75/256 `$BF` |
| tallies 37,340-37,932 / 38,189-38,778 | U+D junk while the tally runs | U+D | irrelevant: inputs during a tally change nothing |

### Arrival dependence (`$BF` = (f - 27) mod 256 in Act VI; `$3E`; `$62`)

* **Room 41 (`nhbf.py`, NesHawk, `r41_34992.txt`, `$BF` poked on 34,560, c = `$BF` on the control row = v + 1): TAS +2 path for 69 of
  256** (v 23, 27, 30, 35, 37, 52-53, 102-103, 106-108, 110-111, 113-122, 124-125, 127, 130-131, 133, 136, 140, 187-190, 223-255). The
  rest: 80 values miss the boost hit (hp 12, Ryu stays below the exit), 87 take an extra hit (hp 10), 19 others. First enemy-slot
  divergence: the thrower (type 2) spawning on 34,785 (then its axes / the birds); first position divergence 34,860-34,888.
  Real arrivals also differ in `$3E` and slot leftovers (as in 6-1): judge on the real state.
* **Room 42 (record's line `r42rec.txt`): independent** (16/16 `$BF`, NesHawk).
* **Room 43 (35,231-35,981, 32 sampled v):** 28 = TAS, 3 an extra hit, 1 misses the 35,815 hit; reader: a thrower (type 2) from 35,761.
  Room 44 not scanned.
* **6-4a Masked Devil: independent.** TAS rows 16/16 `$BF`; `md_js10` / `md_js5`: 8/8 `$BF` + `$3E` 0-5 (NesHawk) -> same kill.
* **6-4b Jaquio: independent.** `r4k2`: kill 38,340 for all 256 `$BF` and `$3E` 0-5 (Mesen), 7/7 on NesHawk (no RNG; a56 round 3).
* **6-5 Demon: DEPENDENT.** `r2d5` (Mesen, 256 `$BF`): kill on 39,239 for 31 values, 39,244 for 24, 39,249 for 20 (the TAS-state
  value 243); the other 181 fail (most die -> 6-1; some survive without a kill). NesHawk spot check 7 values agrees (1 kill).
  `$3E` 0-5: no effect. The first diverging object is a type-41 object (the pod's remains / the demon's shots) from 39,053. The TAS's
  own fast fight (151 f) is TAS-equal for 14/16 sampled `$BF`. **Build the demon on the real 6-5 arrival** (`jplan.py demon` /
  a beam with hp >= 1), and check it with `nhbf.py`.
* Transitions: Start rules do not depend on `$BF`, `$62` or `$3E`; the tally length only on T and np; END seen on `$3E` (above).

### Ninpo / art / hp plan (Act VI, 6-3 -> 6-4a; ninpo and the art are cleared after 6-4a; 6-4b and 6-5 are sword only)

* **6-4a wants J&S + exactly 10** (two spins, kill control + 74 = the record's 6-4a; + 5 costs 15 f; leftover costs 3 f/pt).
* **Arrive in 6-3 with J&S + 0..4** (6-2 exit: change l61p's target "J&S + >= 10" to "J&S, np < 5": burn the rest in 6-2 with
  free air spins). With np >= 5 every TAS air B in 6-3 spins (room 41 extra hit; room 43 35,312 spin catches the **Star X 1,760**).
* **Then collect late in 6-3.** On the TAS line the only automatic pickup is room 44 +10 X 528 (36,767); on J&S it needs a slash
  (the star broke it): **an air B+Right on 36,772-73 in the TAS's jump takes it on 36,775 at 0 f**. The room-44 end on J&S uses two
  spins (`r44j_37121.txt`, 10 ninpo) and 6-4a wants 10 more, so **room 44 needs 20**: +10 X 528, plus +5 X 576 and +5 X 624 (y 80,
  "cost 1" near the X-552/572 wall top; untested). Every air B after the first pickup spins: use Down+B with no direction where a
  plain slash is wanted. Other lanterns near the line: room 43 +10 X 1,312 / +5 X 1,392 (cost 1), +5 X 1,424 (8), +5 X 208 (1);
  taking them early makes the later room-43 air B's spins.
* **TRAPS on/near the line:** room 41 FW X 320 y 96 (above +5 X 320 y 144); room 43 FW X 512 y 80 (on the line), FW X 1,536 y 144,
  **Star X 1,760 y 128** (a spin at 35,312 breaks it); room 44 FW X 704 y 128, Star X 816, **Windmill X 880 y 160** (jumps near
  37,020-37,040 break it), **FW X 944 y 160** (the TAS's backward slash at 37,084).
* HP: the TAS takes 12 -> 11 (34,941, the room-41 boost), 11 -> 8 (35,815, room 43). On J&S add the room-43/44 hits unless repaired.
  6-3 -> 6-4a refills to 16; bosses refill at each stage start (6-4b and 6-5 start with 16).

### Head start (from TAS states; graft only after a NesHawk check on the real arrival)

* **`work/l63p/pre63_35212.txt`** = 652 rows from the 6-3 control row (row 1 = Right on F = TAS 34,561): room 41 legal (+2,
  `r41_34992.txt`) -> room 42 on row 432 (F + 431) -> room 42 on the record's line (a56 `r4_63_h4` rows) -> **room 43 change on
  row 652 (F + 651 = TAS 35,145 + 67)**. Judge PASS. NesHawk from the TAS arrival (also with J&S + 0 poked): room 42 on 34,992,
  room 43 on 35,212. Room 41 is arrival-dependent (69/256 c, above); room 42 has no `$BF` readers seen (it is a fixed point).
* `pre63_35065.txt` (505 rows): the TAS-side variant (room 41 + the room-42 entry cycle, up to the y-160 platform); a dead end,
  since the TAS-side exit has no legal version.
* Room-43 entry from the head start: room-43 control row = change + 23 (F + 674); C8 from the next row (`r43e_35238.txt`; one
  row early fails) -> (1,879, 192) 70 rows later. **The TAS rows after that do not re-join at lag 73** (`chain_43a.txt`: y 192 vs 185 at
  35,300, then hits from X 1,859 and a pit death; poking `$BF` at the room-43 control (64 values) changes nothing, so it is the join,
  not the phase): build room 43 on the real line with short beams between TAS-exact stretches.
* Pieces (rows from the TAS frame in each header; all PASS `check_inputs`, `r42e` only with its control-row Right before it):
  `r41_34992`, `r42rec.txt` (room 42 on the record's line, from the row after the room change), `r42e_35056`, `r43e_35238`,
  `r43w_36031` (+24), `r43w2_36145` (+4), `r43j_36440` (J&S end, +3), `r44e_36567` (+20), `r44w_36867` (+17), `r44j_37121` (J&S end, +3);
  bosses `md_js10` (6-4a, J&S + 10; `md_js10_to64b.txt` = + the Start on 37,943), `md_js5`, `jq_r4k2_kill` (6-4b to the kill),
  `dm_r2d5_kill` (6-5 to the kill; arrival-dependent). NesHawk states: `l63p_ch35235` (head start + 23 blank on the TAS arrival with
  J&S + 0 poked; room-43 control row).

### Next steps for the 6-3 / boss builders (by value)

1. **6-2 exit: J&S + 0..4 ninpo** (not >= 10): air B's in 6-3 stay plain slashes.
2. Room 41: check `r41_34992.txt` on the real 6-3 arrival (`nhbf.py`-style, or just replay); good c come in runs (113-122, 223-255):
   a few frames of waiting at the end of 6-2 move c 1:1 and are cheaper than a new route (no no-boost route exists from 34,930).
3. Room 42: the record's line (`pre63_35212.txt` rows 433-652 shift with the room-42 change frame).
4. Room 43: C8 entry, TAS-exact stretches joined by short beams (score -y - 0.2X style for climbs), the faces (+24 / +4), the end
   (`r43j_36440.txt` idea: jump-slash the X-287 enemy, wall jump at (133, 128)). With np 0 no air B spins.
5. Room 44: entry cycle (+20), the +10 X 528 air slash (0 f), +5 X 576 / +5 X 624, the wall (+17), the end with two spins
   (`r44j_37121.txt`) without touching the Windmill X 880 / FW X 944. Exit with **J&S + exactly 10**.
6. 6-3 -> 6-4a Start on trigger + 5 / + 6. 6-4a `md_js10` (kill control + 74; T 148 needs `$62`(6-4a control) <= 12). Measure c of the
   tally Start on the real kill. 6-4b `r4k2` (+ the measured earliest Start). **6-5: a new demon line on the real arrival** (hp margin;
   a death goes back to 6-1); END seen = the first `$3E` = 1 after P, + 1.


### Agent notes (6-3 / bosses, l62)
* **l62 (2026-10-28 ~19:30) THE RUN REACHES END: END seen 41,385 = 389 f under the record line (41,774). Judge PASS; NesHawk-verified, 0 deaths.**
  * **Full power-on file `work/l62/l62_FULL_v2_poweron.inputs.txt` (41,390 rows)** = locked rows 1-35,798 + `work/l62/s63_end_v2.txt` (from
    35,799). Stage-boundary files (judge PASS each): `l62_FULL_v2_to64a_poweron.inputs.txt` (38,805 rows = through the 6-4a control row),
    `_to64b_` (39,625), `_to65_` (40,639).
  * Stage marks: **6-3 trigger 38,645 (hp 3, J&S + 10), Start 38,650-51 -> 6-4a load 38,653, control 38,805; `md_js10` kill 38,879 (control +
    74, T 148); Start 39,470-71 (earliest) -> 6-4b control 39,625; `r4k2` kill 39,878 (control + 253, T 146); Start 40,485-86 (earliest
    40,462 + 23) -> 6-5 load 40,487, control 40,639; l65 `lines/r2d5_k2.txt` kill 40,947 (hp 16 -> 12), P 41,382, E 41,384, END seen 41,385.**
  * Room 44 (rows in `s63_end_v2.txt`): entry beam `r44c` (l63p's cycle fails: our arrival X 91 xsub 0) -> floor 38,027; beams `r44f`/`r44g`
    (the +10 X 528 air slash 38,248, over the X-552/572 wall via 38,342, +5 X 624 38,372) and `r44i` (end; np 15 -> 10 with a spin on the
    trigger frame) -> trigger 38,645. Two 1-f B ends held 2 f (38,646, 39,879; and 40,958 inside the demon line) for the judge.
  * **NesHawk (`nhrun.py` from `l63t2_37922` to 41,390): every event = Mesen/the search; 3 pad-read conflicts (38,650 / 39,470 first Start
    frame read as nothing, 40,487 Start read on the load frame) without effect (loads on 38,653 / 39,473 / 40,487 as planned); 0 deaths.**
    Rooms 41-44 were also checked piecewise (`l63t1`, `l63t2`, earlier bullets). NesHawk states `l62full_38645`, `_38804`, `_39624`, `_40638`.
  * **6-5 lesson: the Demon fight on our line depends on the enemy-slot leftovers ($400-$4FF), not only on `$BF`.** At the earliest Start
    (bf 135) and with l65's pick for d 0-15, every line died; poking only $400-$4FF to a TAS-path arrival's values made `dm_r2d5_kill` kill
    on row 312 (the other differing groups: no effect; `grp65.py`). So I scanned the real arrival on NesHawk (`nhdemon.py`, d 0-45, all l65
    lines per bf): kills only at d 16, 19, 23, 28, 31, 38, 41..; best **d 23 + `r2d5_k2` = END seen 41,385**. Also: a Start delayed by d
    loads on S + 2 (not S + 3) for d >= 2, so the 6-5 control row must be measured per d, not taken as C + d.
  * Splits vs the record: **6-3 3,006 f (record 2,912.8: +93.2); 6-4a 820 (819.3: +0.7); 6-4b 1,014 incl. the 23-f delay (997.6: +16.4); 6-5
    746 (755.2: -9.2); 6-3 control -> END seen 5,586 vs 5,485.1 (+100.9). Whole run: END seen 41,385 vs 41,774 = -389.**
* **l62 (2026-10-28 ~17:20) rooms 41-43 done on our real line (NesHawk-checked), room 44 running.**
  * Room-43 end: beams `r43m` (to X 212) + `r43q` (score -0.5X - y) -> **room 44 on 37,900** (TAS 36,437 + 1,238 + 225). hp 6, np 0, J&S.
    Rows from 35,799 to the room-44 control row 37,923: `work/l62/s63_to44.txt`; power-on `work/l62/l63_t2_poweron.inputs.txt` (judge PASS).
    **NesHawk from `l63t1_36450`: hp 10 -> 7 (37,119, the bird boost), 7 -> 6 (37,533), room 44 on 37,900 = Mesen; 1 pad-read conflict
    (37,479 A+Left read as Left) without effect; RAM at 37,923 = Mesen except the OAM buffer $200-$2FF (sprite order only).** NesHawk states
    `l63t2_37900`, `l63t2_37922`; Mesen `states/mesen/l63_37923.mst`.
  * 6-3 so far: room 44 at F + 2,101 vs TAS 1,876 (+225) and the record's ~+153: about **72 f behind the record inside 6-3** (margin 491).
  * Room 44: l63p's entry cycle fails on our arrival (Ryu X 91 xsub 0 vs the TAS's 92.5): beam `r44c` -> floor y 208 X >= 172 on 38,027;
    beams `r44e` (needs np >= 10 at the trigger for `md_js10`) / `r44f` (any np) running to the trigger.
  * Boss chain tool ready: `work/l62/nhboss.py` (NesHawk: trigger -> Start scans -> md / jq / demon line picked with l65's `pick.py`
    for the real bf / t62 / e3e incl. a Start delay -> END seen; writes the rows and the power-on file).
* **l62 (2026-10-28 ~16:30) room 43 on our real line, Mesen beams (NesHawk check after room 44): through the pit and both faces.**
  * Pit X 912-991 (~X 950, the a56 "knock-back spot"): a plain run and a jump-timing grid (400 + 1,056 cases) do not cross; the bird (t11)
    must hit Ryu while he is high. **Found: jump straight up at X 1,057 (A+Left x2 on 37,091, then 16 neutral rows): the bird hits on
    37,121 (hp 10 -> 7) and knocks Ryu RIGHT onto the X-1,040 pillar top (y 128) on 37,133; from there beam `r43g` jumps left over the pit
    -> X <= 905 on the floor on 37,232** (TAS-eq lag ~+100). Rows `work/l62/b_r43g.txt` (from 35,799).
  * X-762 face: beam `r43h` (score -X, then -y - 0.2X below X 800) -> top (X <= 739, y <= 128) on 37,379. X-569 face: beam `r43j` -> top
    (X <= 554, y <= 128) on 37,531 (hp 7) = TAS-eq +152. Rows `work/l62/b_r43j_h7n0i133.txt`.
  * Running: room-43 end beams `r43m` / `r43n` (to room 44; the X-287 enemy and the wall jump at (133, 128)).
* **l62 (2026-10-28 ~14:00) 6-3 rooms 41-42 = l63p's head start, NesHawk-verified on our real arrival; room 43 / 44 beams running.**
  * `work/l63p/pre63_35212.txt` from our 6-3 control row 35,799 (no wait needed): **room 42 on 36,230 (TAS +2), room 43 on 36,450 (TAS +67)**, the
    room-41 bird boost hit as planned (hp 11 -> 10). Power-on `work/l62/l63_t1_poweron.inputs.txt` (36,450 rows): judge PASS; NesHawk from
    `l62v2_35798`: same events, 0 pad-read conflicts; NesHawk state `l63t1_36450`. (Our `$BF` 188 on the control row = v 187, inside l63p's
    good set 187-190; a 0-60 f wait grid changed nothing.) **CAUTION for tools: l63p's row files use EMPTY lines for blank rows** - an earlier
    test of mine dropped them and looked like a failure.
  * Mesen states on our line: `states/mesen/l63_35798.mst` (6-3 control - 1), `l63_36473.mst` (room-43 control row 36,473 = change + 23).
    Rows from 35,799 to 36,473: `work/l62/s63_to36473.txt`; + `r43e` C8 entry -> (1,880, 192) ~36,542 (as l63p's +6).
  * Running: room 43 beams `r43a` / `r43b` (from the C8 entry to X <= 790, score -X, item kept = J&S), room 44 beam `r44t` from TAS 36,460
    (J&S / np 0 / star poked; to the trigger, to be re-run on our arrival).

### Agent notes (6-5 Demon, l65)
* **l65 round 2 (2026-10-28 ~11:20, stopped early on the coordinator's wrap-up): no faster line yet; the table, `pick.py` and the delay tables
  are unchanged (106 phases, all NesHawk-checked, best/median/worst END 747/753/777; with the Start delay the worst is 784 for t62/e3e 29/4
  and 785 for 60/5).**
  * Found the heart-jump geometry (`jgrid.py`, from podP1 + Right x33 = Ryu on the ground at X 110 on row 156, bf 243): the demon body
    (slot 5) hurts Ryu on the ground at X >= ~113 and while he is still low (y ~204) there, so the jump must go straight up first.
    **Cycle of 44 rows: A rows 0-1, Right rows 6-7, slash cycle from row 2, Left from row 40 -> 7 heart hits, no damage, back on the ground
    at X 110**. Variants that give 6 hits: (Right 7-9, slash from 0, Left 38), (6-8, 3, 38), (8-9, 1, 40), (9-10, 2, 40). 2,226 + 1,418
    + 1,920 single-jump cases. Three cycles = 16 hits, so a kill near the first jump + ~110 rows looks possible (r2d5 kills on rows 307-342).
  * The fixed template (`tmpl.py`: cycles back to back, first jump at hd + a, a -8..+8) killed 0 of 4 bf: fireballs hit Ryu in cycle 2
    (bf 243 on row 217 at (112,163)). The per-phase beam over cycles with gaps 0-8 (`hs.py`, 6 cycle specs, width 3) found no kill for
    bf 243 / 30 in its first version. Next step: re-run `hs.py` with `HSV=1` to see where it fails, then add dodges (Left/Right shifts
    inside a cycle, a cycle skipped). A pod line whose 16th hit lands in the air is still untried (it would cut the ~9-row stall after
    P1's ground swing).
* **l65 FINAL (2026-10-28 ~10:45): 106 / 256 phases have a legal kill, all 106 NesHawk-checked; with the 6-4b Start row chosen, EVERY
  arrival has a no-death 6-5.** `work/l65/demon_table.tsv` (bf, line, kill row, END seen offset for `$62` 29 / `$3E` 4, hp, NesHawk y/n),
  `demon_all.tsv` (every line per bf), `python work/l65/pick.py <bf> --t62 <$62> --e3e <$3E>` (values at the checkpoint before the 6-5
  control row), `demon_delay.tsv` / `demon_delay_r4k2.tsv` (per arrival bf: cheapest Start delay d + END(bf + d); t62/e3e 29/4 and 60/5).
  * Lines (all `check_inputs` PASS with 150 blank rows before; row 1 = 6-5 control row; all = a56 r2d5 variants, hp left 12):
    `work/l63p/dm_r2d5_kill.txt`, `work/l65/lines/r2d5_k1|k2|k3.txt` (1-3 blank rows first; k >= 4 kills nothing), `r2d5_s22..s25.txt`
    (22-25 blank rows before row 150 = a later heart; bf 9-33). Kill rows 307-342; **END seen offset best 747 (record -8), worst 777,
    median 753** (record pace 755.2). **Start-delay plan: total (delay + END) best 747, worst 784 (record +29, arrivals bf 34-38 -> delay
    to bf 71), mean 756** for t62/e3e 29/4 (785 / 756 for 60/5). Best phases (END 747): bf 71-81, 83, 96, 102, 104, 106, 142-143, 145,
    147, 150, 155, 157, 162-163, 172, 175-176, 187-189, 191-192, 194-195, 223-224, 227, 230, 233-234, 236-237 (recheck with pick.py for
    the real t62/e3e). Uncovered: bf 1-8, 11, 14, 17-18, 20-21, 23-24, 27, 29, 31, 34-70 and ~100 others (`build_table.py` prints them):
    do NOT arrive there; delay the 6-4b Start (each row +1 f, bf +1; `$62`/`$3E` frozen through the load).
  * NesHawk: every table entry (106) = Mesen kill row (`nh65.py`, pokes at 38,932); **real arrivals without pokes (`nhreal.py`, r4k2 kill
    + Start 38,921 + d, d 0/1/12/17 -> bf 130/130/141/146, t62 60, e3e 5): kills on the predicted rows, END seen 754 / 754 / 748 / 754**;
    d 4 (bf 133) correctly reports NO LINE. Pad conflicts seen on a few rows (k2 rows 70/72, k3 rows 28/53/71/78) change nothing.
  * Faster lines NOT found: P1-based searches (`jplan65.py` with walk/wait/jump-pattern steps, bf 30 / 50 / 60, widths 3-5, 4-5 levels,
    ~400-1,500 first-step candidates each) reach 6 heart hits on the first jump (heart 16 -> 10) but never another hit: the body (slot 5,
    type 43) hurts on the ground at X >= ~113 and in the air below y ~180 near X 120, and from X 108-111 the 0.6 px/f slash-drift is too
    slow; hybrid podP1 + r2d5's heart part (`hyb.py`, 8 bf x 11 jump rows): 0 kills. A per-bf heart search that starts its jumps from
    X 112-113 on the ground (1-row walk granularity) is the next try; the prize is ~50-70 f (heart down rows 136-185 on P1 vs ~182-208 on
    the r2d5 path). Also untried: a pod line whose 16th hit is in the air (P1 loses ~9 f to the ground-swing stall).
* **l65 (2026-10-28 ~07:15) no arrival needs to die: pick the 6-4b Start row.** A Start d rows later costs d f and gives bf + d (`$62` / `$3E` at the 6-5 control are frozen through the load, so END's rule is unchanged). `delay.py` -> `demon_delay.tsv`: for every arrival bf the cheapest d + END(bf + d) over the 89 covered phases: **best 747 (record -8), worst 805 (record +50, arrivals bf 13-17 -> delay ~55 to bf 71), mean 758**. Covered phases with END 747 (TAS t62/e3e): 71-81, 83, 96, 102, 104, 106, 142-143, 145, 147, 150, 155, 157, 162-163, 172, 175-176, 187-189, 191-192, 194-195, 223-224, 227, 230, 233-234, 236-237. Recompute with the real `--t62/--e3e` (r4k2 arrival: 60 / 5). All 4 line files pass `check_inputs` (150 blank rows of history). The owner's game took the RAM (0.6-1.9 GB free): `lead.py` k 3-14 waits behind `GATE_GB=2.5 gate.sh` (one Mesen) and stops itself below 2.0 GB.
* **l65 (2026-10-28 ~06:45) status + resume steps (work dir `work/l65/`, prefix `l65_`).**
  * **What the fight depends on (Mesen, TAS 6-5 control-1 state 38,932 + pokes, r2d5 on 8 bf):** only `$BF`. `$3E` 0-5, `$62` 0-60,
    `$63` 100/149, `$381`, `$394` (the Start-delay leftovers) poked at control-1: no change. Real arrivals (`arr.py`, `arr2.py`): a Start
    delay of k moves `$BF` by k only (`$3E` is frozen through the load: 4 for every k on the TAS kill); after the r4k2 6-4b kill the
    arrival has `$3E` 5, `$62` 60 and other slot leftovers ($404-$406 39 instead of 15/16/36) - the fight does not read them, but
    **END seen depends on `$62` and `$3E` at control-1** (`pick.py` takes both; TAS arrival 29 / 4). Ryu enters 6-5 with hp 16, np 0,
    no art (TAS). `$BF` runs +1 per frame through the fight. bf = `$BF` at control-1 (TAS 243).
  * **Mechanics (TAS + scans):** pod (slot 6, 16 HP) is hit only in the air from X ~71-101; at hp 4 it falls; the 16th hit kills it
    (explosion, slot freed ~10 f later). **The first fireball (type 41, from the mouth (128,108)) spawns on control-row 121 for every bf;
    the heart (slot 7) comes down (y 120 -> 168) at the first spawn after the pod's slot is free** (TAS: pod dead row 109 -> heart row
    122). Spawn #2 time depends on bf (`sched_P0.out`, `fb1.out`: heart row 136-185). Fireball paths are fixed per bf and do NOT depend
    on Ryu (`exp_fb.py`). **Ground X >= ~113 hurts** (the demon's foot, slot 5 type 43 at (136,208)): heart hits are air hits from X
    ~113-140. Each hit = 3 hp + knockback; failures of a line are missed heart timing or knockbacks, then death by fireballs.
  * **Fastest legal pod found: `podP1.txt` (123 rows): walk R 28, two straight jumps with the slash cycle, pod dead on row 123**
    (jump 1 = 7 hits, jump 2 = 8 + the kill hit on the ground; 1,400 + 540 enumerated variants `t3.py`/`t4.py`, best 123). The heart can
    then come down only at a bf-dependent spawn (rows 136-185). A pod kill by row ~110 (heart on row 122 for all bf, like the TAS)
    was not found (needs ~16 hits in ~80 f at one hit per 5 f; jump windows give 7-8 hits).
  * **Table so far (`build_table.py` -> `demon_table.tsv`, `demon_all.tsv`; `pick.py <bf> --t62 v --e3e v`): 89 / 256 bf covered**, all
    from a56 r2d5 variants: r2d5 itself (75 bf, kill rows 307/312/317, hp 12), `lines/r2d5_k1.txt` / `_k2.txt` (1-2 blank rows first;
    79 / 72 bf, k2 kills bf 243 on row 314), `lines/r2d5_s22.txt` (22 blank rows before row 150: bf 9, 10). END seen offset (TAS
    t62/e3e) best 747, worst 765, median 753 (record pace 755.2). **Uncovered: bf 0-8, 11, 13-70 and ~100 others** (list printed by
    `build_table.py`). NesHawk (`nh65.py`, `nh_ok.tsv`): r2d5 bf 74/102/123/243, r2d5_k2 bf 79/145/243/253, r2d5_s22 bf 9/10 = Mesen kill
    rows exactly (r2d5_k2 has pad conflicts on rows 70/72 that change nothing).
  * **Half done:** `lead.py` (k blank rows + r2d5, k = 3..25, results append to `lead.res.tsv`; ~4.5 min per k per Mesen) restarted
    behind `gate.sh` (waits for >= 3 GB free). `jplan65.py` (jump-step beam; landing = `$84` bit 2 clear) and `beam65.py` work, but the
    heart planner did not converge (myopic score; `--hpw 12` untried to the end). `sweep.py` (shift a P1-based heart line by hd(bf)) is
    ready but has no P1-based heart line yet. `nhreal.py` (real r4k2 arrivals with Start delay d, no pokes) is written, not yet run.
  * **Resume:** (1) `bash work/l65/gate.sh python work/l65/lead.py <k list>` for the k not yet in `lead.res.tsv`, then
    `python work/l65/build_table.py`; (2) for the bf still missing, the block 0-70 has late hearts: try r2d5 with blanks inserted before
    row 150 / leading k > 25, or a per-bf `jplan65.py --bf v --goal kill --prefix work/l65/podP1.txt --pre2 30:<hd-10>-<hd+6> --ds0
    h0_99,h15_99,h30_99,h15_30,h30_36,h99_99 --ds same,L --hpw 12`; (3) NesHawk: `nh65.py line:bfs` for each final line and `nhreal.py
    0,5,...` on real arrivals; (4) rerun `build_table.py`.

## Video pipeline (yt/)

The race video (our run left, the TAS 4751M right, one clock from power-on, stage table vs the TAS and the record's
numbers) is built by `yt/` from the final power-on input file: `python yt/final.py <final inputs.txt> --name final
--expect-sha logs/<route>.report.json` (steps and timings: `yt/README.md`; story beats: `yt/STORY_LOG.md`). Nothing in
`yt/` edits the chain; when a stage is locked, add its WHAT/WHY line to `yt/run_text.json` and its TAS reason to
`yt/race_text.json`.

## Independent verification (work/verify/)

Separate verifier agent, 2026-10-28; its own replay, clock and rule counter, no project imports. Report: `work/verify/VERIFY_REPORT.md`. Locked part (rows 1-35,799) re-derived: rules PASS, RAM sha1 6ada68899a66 = project, all loads and rooms identical, 0 deaths, START seen 175. Record re-timed from its video: Ryu first visible f1707 -> TIMER-000 first shown f43238 = 692.183 s (video clock is real time, ~16 ppm) = 41,599.4 +/- 2 NES f; record line END seen <= 41,774 confirmed. Same-event (TIMER digits first drawn) at 6-3: -489.4 f vs the record (project -491.4). Final check: `python work/verify/final_check.py logs/<final>.inputs.txt --report logs/<final>.report.json --name final`, then look at `work/verify/run/final/start_sheet.png` and `end_sheet.png`.

## History

### 3-1 round (locked: alt b2r; 0 throws impossible, 1 throw best)

**LOCKED START (2026-10-24): 3-1 control frame 9,993** from `logs/l22_art_w10_to31_poweron.inputs.txt` (9,993 rows), hp 16, ninpo 0, no art, `$BF` 251 (save a NesHawk state at 9,993 from this file; the plan below was written on t12 = 9,998 / `$BF` 0, its numbers are otherwise valid). Record split 1,602.7 -> target 3-2 control <= **11,595**; aim well under. Compare candidates by the 3-2 control frame AND the `$62` phase there (it feeds 3-3's tally).

Candidates (3-1):

| time | agent | file | 3-2 control | frames | vs record | hp/ninpo/art | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 20:05 | tas5 | `logs/l31_tas_c1b_poweron.inputs.txt` (power-on, 11,604 rows; stage rows `logs/l31_tas_c1b.inputs.txt`, end state `states/l31_tas_c1b_end`) | **11,604** | 1,611 (TAS +6) | **+8.3** (cum -163.1) | **16 / 15 / Fire Wheel (128)**; `$62` = 45 at 3-2 control (46 frozen from the play end at X 2011, frame 11,323) | yes (verify finish; `verify chain l31_tas_c1b_poweron`: two replays MATCH, RAM sha1 de128d9ffd61) | PASS | plan (a), **at its floor** (pure run 11,594 + 5 throws x 2 f): legal TAS rows (lag 165) + 3 free B repairs (type-3 walker start, type-11 flier X ~670, type-1 X ~1290) + end beam past the type-3 walker at X ~1950; 5 Star throws at the TAS's places (knife thrower, -, FW from X 1011 y 94, +10, type-2) each with ONE extra Right-released row; takes +5 X 336 too (15 at the exit, a multiple of 5) |
| 2026-10-24 20:20 | alt | **`logs/l31_alt_b2r_poweron.inputs.txt`** (power-on, 11,595 rows = locked to31 rows 1-9,992 + stage rows `logs/l31_alt_b2r.inputs.txt` (1,603 rows from frame 9,993: **row 9,993 = Right**, the free control-frame row); end state `states/l31_alt_b2r_end`; start state `states/lock_31_pre` (frame 9,992)) | **11,595** | 1,602 from the 9,993 control (TAS -3) | **-0.7** (cum -172.1) | **16 / 12 / Fire Wheel (128)**; `$62` = 54 at 3-2 control; Ryu **x 35 moving at 3-2 control** (last 2 pre-control rows = Right) | yes (verify finish from `lock_31_pre`; `verify chain l31_alt_b2r_chain`: two replays MATCH, RAM sha1 8a74b015f3e5) | PASS | **plan (b), 1 Star throw, at its floor (pure run 11,593 + 2 f for the throw)**. Effective **11,601** (residue 12 mod 5 = 2 -> +6 f at the 3-3 tally) vs c1b 11,604: **3 f better**. = TAS rows with lag 164 (row 9,993 Right puts us exactly on the TAS phase) / 161 after TAS 10,554, every TAS throw replaced by Right except the FW throw (stage row 657 from X ~1013 y 94; the legal release row follows), and 4 air slashes (B added on stage rows 503, 535, 780, 864) for the knife thrower X ~812, the jetpack ninja, the tower type-2 X ~1227 and the type-1 X ~1350. Takes +5 X 432, +10 X 576 (TAS) -> 15 - 3 = 12 |
| 2026-10-24 20:20 | alt | `logs/l31_alt_b2_poweron.inputs.txt` (same rows, pre-control rows blank; stage rows `logs/l31_alt_b2.inputs.txt`) | 11,595 | 1,602 | -0.7 | 16 / 12 / FW; `$62` 54; x 32 standing at control | yes (`verify chain l31_alt_b2_chain` MATCH, RAM sha1 4148c5a28ae2) | PASS | b2r without the pre-control Right (use b2r) |
| 2026-10-24 19:50 | alt | `logs/l31_alt_b1_poweron.inputs.txt` (row 9,993 blank; stage rows `logs/l31_alt_b1.inputs.txt`) | 11,596 | 1,603 | +0.3 | 16 / 17 / FW; `$62` 53 | yes (`verify chain l31_alt_b1_chain` MATCH, RAM sha1 3a5126411cbf) | PASS | first plan-(b) line on the locked row 9,993 (lag 165); superseded by b2r |

Agent notes (3-1):
* alt 17:45: start states made from `logs/l22_art_w10_to31_poweron.inputs.txt`: NesHawk `states/lock_31_ctl` (frame 9,993, x 32 y 192, hp 16, np 0, `$BF` 251), its NesHawk trace `logs/l31_base.trace.csv`, Mesen `states/mesen/lock_31_ctl.mst` (`work/c5/mboot.py` from those pads; `$62` = 44 at control).
* tas5 18:20 (analysis, TAS trace): **3-1 is pure running.** The TAS moves 1.5 px/f on every frame from control to X 2011
  (play ends there; 3-2 control = that frame + 281) EXCEPT the 5 Up+B throw frames (no Right = 0 px): TAS 1,605 = pure
  run + 5. Our start is **1 f behind the TAS phase** (TAS row 9,829 = Right moves x 32 -> 33 on its control frame; our
  locked row 9,993 is blank, x 32), so our rows = TAS rows with **lag 165** (TAS row k = our row k+165), not 164.
  Floor: pure run = 3-2 control **11,594** (record -1). Every frame without Right costs 1 f; a legal throw releases Right
  2 frames = **2 f per throw**. So plan (a) (5 throws) >= 11,604 (record +9); 1 throw >= 11,596 (record +1, + 6 f at the
  3-3 tally); 0 throws needs the FW (X 1184 y 96) by sword. Mesen TAS state at 3-1 control-1: `states/mesen/l31t_tas9828.mst`.
* tas5 19:10 (TOOL BUG, all agents): **Mesen's Lua dies (ConnectionReset / hang / garbage reply) when Python leaves a
  core idle for more than ~1 s** (measured: `run_batch`, sleep 1 s, `ram()` -> reset; 0.5 s ok). The fastcore server
  waits for the next command inside the NMI exec callback, and a callback over ~1 s is killed. Wide beams (Python think
  time per generation > 1 s) die after 10-150 generations; it is not memory. Fix without touching ng/: `import fcka`
  from `work/l31t/fcka.py` before creating FastCores and set `core._ka_slot = '<a slot that exists>'`: a thread sends a
  1-row RUN to any core idle > 0.3 s (only for code that always runs from slots, as the beams do). With it, idle 8 s ok.
* tas5 20:05: **plan (a) done at its floor: `l31_tas_c1b` = 3-2 control 11,604** (record +8.3), FW/15, hp 16, judge PASS,
  chain MATCH. Method that worked (greedy X-progress beams were myopic: the dog/knife-thrower/FW need planned moves):
  legalized TAS rows with lag 165 + **one extra row with Right released after every TAS throw** (`work/l31t/tfol.py`);
  with that, all 5 throws hit what the TAS's hit (knife thrower X ~811, FW from X 1011 y 94, +10, type-2) on our `$BF`,
  and only 4 spots needed repairs: B timing on TAS rows (`work/l31t/sync.py`, 0 cost) for the type-3 at X ~240 (beam),
  the type-11 flier X ~670 (beam `b2`), the type-1 X ~1290 (B on row 840); end: 80-row beam past the type-3 at X ~1950.
  The type-9 dog that chases Ryu from X ~356 (faster than Ryu) must be jumped at the TAS's times (land X ~777 and jump
  again): our first beams were hit there. Plan (a) cannot go lower: every throw needs 2 frames without Right, and the
  mod-5 rule needs 0 or 5 throws. vs plan (b) (`l31_alt_b1`, 11,596, residue 2 = +6 f at the 3-3 tally): c1b is 2 f
  worse overall unless the `$62` phase at 3-3 says otherwise; c1b exits with 15 (3-2 can skip 5 more of its ~1 f lanterns).
* alt 20:20: **plan (b) at its floor: `l31_alt_b2r` = 3-2 control 11,595 (record -0.7), FW/12, effective 11,601** (+6 f
  residue at 3-3). Findings:
  * **Plan (c) (0 throws) is impossible:** a lantern slash needs Ryu's feet y in (88, 120) with X in (1152, 1184] facing
    right or [1184, 1216) facing left (ng.solve.hitbox). A floor jump peaks at y 125; the "towers" at X 1215 / 1280 are
    background (Ryu runs through them at y 189); the high platform's jump (y ~80) ends at X ~1046. A point-target beam
    (W 48, 160 f, full alphabet incl. Left/air slashes, from X 1076, `work/l31alt/c_fw1.log`) never broke it.
  * **1 throw can never leave a multiple of 5** (lanterns are 5/10, a throw is 3): t throws leave 2t mod 5 = 2 (1 throw,
    +6 f), 4 (2), 1 (3 throws: 6 f + 3 f), 3 (4), 0 (5 throws: 10 f). So 1 throw (2 + 6 = 8 f over the 11,593 floor) is the
    best item plan; 3 throws = 9, 5 throws = 10.
  * **FW from range: the star must be thrown at X 1012-1016 with Ryu at y 94-103** (the jump off the X 832-960 platform),
    because the FW lantern only spawns when it scrolls in (Ryu X ~1057); earlier stars fly past an empty slot.
  * **Pre-control Right (all candidates):** the last 2 rows before 3-2 control set to Right -> Ryu is at x 35, speed 1.5
    on the 3-2 control frame (x 32 standing otherwise; NesHawk `work/l31alt/pretest.py`). Ryu already moves on control-2
    and control-1: ~2 f of free head start for 3-2. Applies to c1b too.
  * Method: `work/l31alt/tmod.py` (prefix + TAS rows at a piecewise lag, throws not kept -> Right, B added on rows) and
    `tscan.py` (scan one extra B row for the first hit): 4 slash fixes, no beam needed. X-greedy beams (`beam.py`) were
    myopic at the type-9 dog (needs the TAS's land-and-rejump at X ~713 / ~777).

### 3-1 plan (analysis, l23)

Start = the locked 2-3 exit: hp 16, ninpo 0, no art; on t12+va: 3-1 control 9,998, `$BF` 0 (the TAS has 87 there, so the
TAS rows will not stay in sync from the start: enemies differ). Record split 1,602.7 f, TAS 1,605 (no L+R / U+D in the
TAS's 3-1; only 46 one-frame A/B/Up holds, repairable at 0 cost, and 5 one-frame Right releases for the Star throws, ~1 f
each legally). Round 1 from the TAS state: TAS +5 (`beam_3-1_v2`, FW/10). Old chained line `logs/tk_3-1_a2` 1,638 (TAS +33,
other `$BF`) - route reference only. Target: 3-2 control <= 3-1 control + 1,602.

Lanterns (ROM, `python -m ng.solve.items 3-1`), who takes them (TAS: NesHawk trace from `ref4751/05_3-1_control`,
`work/l23/tas31.out`; record: HUD montage `work/l23/rec/hud31.png`, timed by the on-screen TIMER):

| lantern | TAS | record | cost |
|---|---|---|---|
| +5 X 336 y 160 | no (runs under it) | no | ~1 (air slash on the line) |
| +5 X 432 y 160 | yes (TAS 10080, air slash) | no | 1 |
| +10 X 576 y 160 | yes (10191, air Right+B) | **yes** (00 -> 10 at TIMER ~144, same time as the TAS) | 1 |
| hourglass X 640 | no | no | harmless |
| **Star X 768 y 128** | yes (10299/10313) | yes (TIMER ~142) | 1 |
| 1000 pts X 896 y 96 | broken by a slash at 10388 (no effect) | ? | - |
| +10 X 1152 y 160 | yes, broken by a thrown star (10525), caught 10577 | yes (07 -> 17 at TIMER ~137) | 1 by star |
| **Fire Wheel X 1184 y 96** | yes, broken by a thrown star (10521), caught 10594 | yes (with the +10, TIMER ~137) | 1 by star, ~15 by sword |
| +10 X 1328 y 96 | no | no | ~15 |
| health X 1664, 500 pts X 1856 | no | no | - |

TAS ninpo: 0 -> 5 -> 15 -> Star -> 5 throws (10329, 10345 kill a type-2 and the type-18 jetpack ninja at X ~780-810;
10485, 10501 break the FW and +10 lanterns from X ~1010-1035; 10554 kills a type-2 at X ~1110) -> 0 -> +10 -> **FW/10**.
Record: +10 X 576 only, Star, ONE throw (10 -> 07 at TIMER ~140), +10 and FW -> **FW/17** (remainder 2: 6 f at the 3-3
tally; he then arrives at 3-3 with 27).

Plan:
1. Exit 3-1 with the **Fire Wheel** (X 1184, broken by a thrown Star as both runs do). Ninpo at the 3-1 exit only has to keep
   the Act III total a multiple of 5: 3-2's cheap lanterns (+5 352, +10 448, +5 1504, +5 2192, +10 2368 = 35, minus 5 if the
   TAS's pillar wheel at 12646 is used) already cover the 30-35 that 3-3 needs. So 3-1 ninpo is only Star-throw ammo.
2. Star throws: **0 or 5** (each -3). Candidates: (a) TAS line, 5 throws (+5 432, +10 576 = 15 = 5 throws), exit FW/10,
   ~5 f of legal throw cost; (b) record line, 1 throw: ~1 f, but remainder 2 = 6 f at 3-3 (total ~7); (c) 0 throws needs
   the FW by a jump slash (~15 f) and handles the jetpack ninja / type-2s with the sword (round-2 no-throw beam stalled
   at the FW pickup, 80 f behind). Start with (a) as the beam's item plan (`--items` Star then FW, `--keepitem 128` from X
   1184), fall back to (b) if the enemies on our `$BF` make the extra throws useless.
3. Never catch the hourglass (harmless) or anything after the FW; keep `$C9` = 128 to the exit. 3-2 then decides the
   exact 3-3 amount (avoid the Windmills at 3-2 X 1008 and X 2624).
4. Method: legalized TAS rows from 3-1 control (lag 0, `work/l21f/fbeam.py` / `work/l22a/abeam.py` style beam with the
   TAS-track score and item rules) and repair where our `$BF` changes the enemies; the throws must have no L/R on the Up+B
   frame (2 f released). Compare candidates by the 3-2 control frame AND the `$62` phase there (it carries into 3-3's tally).

### 2-2 round (locked: art w10, 2-3 control 9,167)

Start: `states/l21f_v4_end` = 2-2 control frame 6,130 (hp 16, ninpo 10, J&S, `$BF` 230), power-on history
`logs/l21f_fol_v4_poweron.inputs.txt`. Record split 3,101.1 f; TAS ~2,895 (record = TAS +206: biggest record loss
of the game). Old best 3,448 (+347, other `$BF`, reference only). Target: 2-3 control <= frame 6,130 + 3,101 =
**9,231**; aim far under.
Look-ahead: 2-3 Bomberhead wants J&S + >= 10 ninpo for the TAS-pace kill (we ARRIVE at 2-2 with 10: don't drop
below 10 at the 2-2 exit; more is a bonus for later). 3-3 Basaquer later wants >= 30 ninpo (Fire Wheels).
**[budget 2026-10-24: CORRECTION]** More than 10 is NOT a bonus. Ninpo is tallied to 0 after Bomberhead (3 f per
leftover point) and never reaches Act III. Exit with J&S + exactly 10. We hold the Star from room 6, so the room-8
J&S lantern is mandatory. See "Ninpo/art budget" above.
Known (record_route_a12.md "2-2", legal_a12_notes.md): room 6 leftward (record level with the TAS; TAS exit uses L+R
in the air at TAS 6709-6712); room 7 the TAS goes straight LEFT at the top with L+R / U+D+L (record goes right/up
first: +110, then +125..131); room 8 starts clinging in a chimney (x 48-79) left of a pillar, camera only scrolls
once Ryu reaches screen x ~127 (record +165..+197 at entry, then constant). Lanterns: room 6 +5 (X 672) / +10
(X 608), room 7 +10, room 8 (`python -m ng.solve.items 2-2`). New legal ladder climb 1.8 px/f
`R, R+U, R+U, A+L+U, A+L` (2-1 wall agent) - check every ladder/wall here.

Candidates (2-2):

| time | agent | file | 2-3 control | frames | vs record | hp/ninpo/item | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 14:01 | art | `logs/l22_art_t12_poweron.inputs.txt` (power-on, 9,172 rows; stage rows `logs/l22_art_t12.inputs.txt`, end state `states/l22_art_t12_end`) | 9,172 | **3,042** | **-59.1** (TAS +147; cum -159.1) | 15 / **10 / J&S (133)**, `$BF` 200 | yes (verify finish + `verify chain l22_art_t12_chain`: two replays MATCH, RAM sha1 d8fff3461f7b; nhcheck NesHawk = Mesen) | PASS | = main's `work/l22c/t9.txt` (Star line, room 8 at X 1399 / 7,982; row 1370 Left instead of blank: t9 has a 1-frame Left at 7,499 = judge FAIL) + art room 8: free Star slashes took +5 +5 (30), J&S caught at X 1320 (8,035, beam `fb_t9j`), then spins only where the beam needed them; +10 / +5 taken; FW X 944 left; exit X 40 at 8,891 (TAS +173) with exactly 10 |
| 2026-10-24 16:05 | art | `logs/l22_art_v9_poweron.inputs.txt` (power-on, 9,185 rows; stage rows `logs/l22_art_v9.inputs.txt`) | 9,185 | 3,055 | -46.1 | 15 / 10 / J&S, `$BF` 213 | yes (verify finish + chain MATCH 7514bda1291f) | PASS | superseded: main's v9 prefix + art room 8, but Ryu reached X 40 IN THE AIR (y 144) at 8,890 and the stage end waits for the landing (+14). Exit beams now require `g:8:0:40:192` |
| 2026-10-24 16:20 | art | `logs/l22_art_v9b_poweron.inputs.txt` (power-on, 9,171 rows; stage rows `logs/l22_art_v9b.inputs.txt`, end state `states/l22_art_v9b_end`) | **9,171** (3-1 control 9,997: `logs/l22_art_v9b_to31_poweron.inputs.txt`, chain MATCH 28a90f0014ac, judge PASS) | **3,041** | **-60.1** (TAS +146; cum -160.1) | 15 / **10 / J&S (133)**, `$BF` 199 | yes (verify finish + `verify chain l22_art_v9b_chain`: two replays MATCH, RAM sha1 d57a5e7279ba; nhcheck NesHawk = Mesen) | PASS | = main's `work/l22c/v9.txt` (X 1400 at 7,978, Star/30) + art room 8: J&S caught X 1321 at 8,031 (width-48 beam; width 64 found none), X 900 at 8,313, exit landed X 40 y 192 at 8,890 (`--needs 816:30` = no spin before the X-800 lantern; spins X 1219, 1118, 926, 809, 644, 511, 352 = 7) |
| 2026-10-24 17:05 | art | `logs/l22_art_v9m_poweron.inputs.txt` (power-on, 9,169 rows; stage rows `logs/l22_art_v9m.inputs.txt`, end state `states/l22_art_v9m_end`); **to 3-1: `logs/l22_art_v9m_to31_poweron.inputs.txt`** (last 2-2 row Left + `logs/l23_t12_va.inputs.txt`) | **9,169** (3-1 control **9,995**) | **3,039** | **-62.1** (TAS +144; cum -162.1) | 15 / **10 / J&S (133)**, `$BF` 197 | yes (verify finish; `verify chain l22_art_v9m_chain` MATCH 94cb516e2e5c; `verify chain l22_art_v9m_to31` MATCH f104b179e64a: 2-3 = 826 f, 3-1 control 9,995 = bar -3) | PASS (both files) | = v9b with the X-900 segment re-beamed (8,312) and the exit re-beamed (landed X 40 at 8,888). nhcheck: one Mesen/NesHawk ninpo-timing difference at 8,180 (pad conflict), end state identical; the NesHawk replays are the judge |
| 2026-10-24 17:33 | art | `logs/l22_art_w10_poweron.inputs.txt` (power-on, 9,167 rows; stage rows `logs/l22_art_w10.inputs.txt`, end state `states/l22_art_w10_end`); **to 3-1: `logs/l22_art_w10_to31_poweron.inputs.txt`** (last 2-2 row Left + `logs/l23_t12_va.inputs.txt`) | **9,167** (3-1 control **9,993**) | **3,037** | **-64.1** (TAS +142; cum -164.1) | 15 / **10 / J&S (133)**, `$BF` 195 | yes (verify finish; `verify chain l22_art_w10_chain` MATCH 10ac2d69f9eb; `verify chain l22_art_w10_to31` MATCH 6f295ee100aa: 2-3 = 826 f, 3-1 control 9,993 = bar -5) | PASS (both files) | **BEST.** = main's `work/l22c/w10.txt` (w9 prefix + legal TAS rows through the J&S catch, X 968 at 8,264, J&S/30) + art: X 900 at 8,310 (`fb_w10b`), exit landed X 40 y 192 at 8,886 (`fb_w10c`, `--needs 816:30`). nhcheck: Mesen/NesHawk ninpo-timing difference at 8,384 (pad conflict), end state identical |

Agent notes (2-2): share segment finds here (agent, room/segment, rows file, entry/exit frames, what it needs).

* puzzle 05:25 (Mesen, WARNING for room 6 exit): `work/l22f/p1.txt` (622 rows) changes to room 7 at row 622 but Ryu DIES in the
  exit pit (after the fade: item `$C9` 0, ninpo 2, frozen; the room-7 change still happens). The pit only lets Ryu through at
  x >= ~92 while crossing y ~240 with no leftward speed (TAS uses L+R in the air); otherwise he lands on the y-192 block
  (x <= ~86) or clings to its right face. Check `$C9`/ninpo ~25 f after the room change, not just the room id.
* puzzle 06:30 (Mesen, room 7 TOP = no legal TAS line): the TAS crosses the right pillar (X 800-831, y 64-144) at y 66-87
  with U+D+L in the air: the idle handler moves Ryu at 1.5 px/f while FACING RIGHT, and walls only block in the facing
  direction, so it passes through the pillar top. Legal attempts all fail: ladder kick A+L from the highest ladder point
  (Up to y 85; y 84 = exit back to room 6) peaks at y 70 and is stopped at X 835 (needs <= ~64); the pillar face is only
  grabbable from y 81 (rows 64-79 are a corner tile: Ryu slides), its A+R kick peaks at y 66; legal Left drift (0.5) cannot
  pass the wall; B slashes in the air do not let Ryu in (288-candidate grammar `work/l22p/g_r7b.py`). => Use the RECORD route:
  `D:8 R:74 L:113` from spawn+3 (TAS state 6747; Ryu walks off the y-128 floor's right end X ~972, lands on y 192, runs
  left under the right pillar) = X 828 at row 195; then the gap between the pillars (left pillar X ~747-778, top y 128):
  `L:26 AL:2 L:8 AR:2 R:11 AL:2 L:14` (ground jump, kick off the left pillar's face, kick off the right pillar's left face) ->
  standing on the left pillar top (X <= 782, y 128) 65 rows later (`work/l22p/x_r7d.txt`, 10,368-candidate grammar
  `work/l22p/g_r7d.py`). Total spawn+3 -> left pillar top 260 rows = TAS +~128 (record ~+130 there). Geometry only (TAS
  state, blank history): enemies (type 8 bird near X 755 y 77-104) differ on our `$BF`.
* puzzle 06:30 (Mesen, room 8 chimney, geometry from TAS state 7376 = spawn+2): `work/l22p/x_r8a.txt` (100 rows) = ladder
  U-cycle `R:2 (RU:2 ALU AL R) x7 RU:2 ALU AL:2` then Right: last ladder kick at y 168, drift right 0.5 onto the pillar top
  (y 160, X ~1858), run right -> screen x >= 127 (camera engaged) at row 100 (TAS 80: +20; old legal ~+70). Equal (+21/+22):
  kick left to the chimney's left wall (x 39) after 6 cycles, A+R kick at contact. After that the TAS reaches the y-96
  platform with a DAMAGE BOOST from the type-8 bird (hp 16->15 at TAS 7516, knocked up from y 118); the record does the
  same kind of thing. Without it the only way up is the ladder at X 1984 (~+110), so room 8's start depends on the bird.
* follow 06:20 (Mesen): room 6 = legalized TAS rows from TAS 6102 (lag 28: TAS 6102 has our X) replay IN SYNC, hp 16,
  ninpo 5 (+10 lantern broken, two spins as the TAS) to TAS 6707 = frame 6735 (`work/l22f/f0.txt`, 600 rows). Room 6 exit
  mechanics (RAM pokes): Ryu must be at screen x ($86) >= 93 on the frame he reaches y 240 while FACING LEFT (facing right at
  x >= 93 grabs the ladder = right shaft wall, coll 32; from a grab at y 240, Down x11 reaches room 7 alive). Falling off the
  y-160 edge, Right does not turn Ryu and drifts only 0.5 px/f; the type-7 jumper (slot 6) hits Ryu at frame 6734 unless his
  x <= 84 then, so x 93 at y 240 is 1 px out of reach -> no straight-fall legal exit on this arrival. Killing both jumpers
  needs a ground turn+slash on the platform (`Left*4-8, Right*1-2, B*2` from row 580 kills both, hp 16, ~13 f freeze).
* follow 06:55 (Mesen + NesHawk power-on trace, 0 conflicts): **room 6 exit at ZERO loss** (beats the kill line above by 17 f):
  `work/l22f/p3b.txt` (711 stage rows) = TAS rows to row 580 + `work/l22f/s_r6k.txt` (41 rows, fbeam with air slashes
  B+Left/B+Right that keep Ryu facing left, dodging the jumper) -> room 7 at frame 6,751 (= TAS 6723 + 28, Ryu alive, hp 16,
  ninpo 5), then legalized TAS rows in sync to frame 6,841 = TAS 6813 + 28 (top of the room-7 tower, X 842 y 80; the next
  TAS rows U+D+L clip through the wall corner at X 836, not legal). Room 7 spawn now at frame 6,772 (TAS 6744 + 28):
  puzzle agent, please rebuild room 7 on `p3b` (row 642 = spawn+0) instead of `p3`.
* puzzle 06:55 (PAUSED, Mesen only, nothing NesHawk-checked): real room 7 on l22f `p3.txt[:638]` + 23 blank: `D:9 R:74 L:115`
  + `work/l22p/x_r7d2.txt` -> left pillar top at frame 7,053 (TAS lag 180), then TAS-score beam `work/l22p/fb_r7e.inputs.txt`
  -> room 8 change at 7,537 (TAS +184), hp 16, np 5, J&S. All 1,407 rows from 2-2 control: `work/l22p/p22_to_r8.txt`.
  Room 8 platform part (bird damage boost) not done. Details + resume: legal_a12_notes.md "2-2 lock round (puzzle)".
* r78 (agent continuing follow+puzzle; Mesen + NesHawk power-on trace `logs/l22c_s5.trace.csv`, NesHawk = Mesen, 2 harmless
  pad conflicts 7240/7433): room 7 rebuilt on p3b -> room 8 change at frame 7,499 (TAS 7353 +146 = 2-2-local TAS +120;
  old 7,537), hp 16, ninpo 20, item = Throwing Star (`$C9` 129, from room 6; J&S lantern X 1312 needed).
  Room-8 arrival for others: stage rows `work/l22c/s5.txt` (+21 blank = spawn, `work/l22c/s5b.txt`, Mesen state
  `states/mesen/l22f_c8s.mst` = spawn frame 7,520, history `work/l22f/h_c8s.inputs.txt`), NesHawk-matched. `work/l22c/s5.txt` (1,369 stage rows) = p3b[:642] + `R:1 DR:1 D:9 R:28 AR:2 R:41 L:101`
  (a floor JUMP at X ~900 so Ryu turns on the floor block's corner at X 967 and lands on y 192 already running left: X 828
  at spawn+183, old run 199) + gap-climb beam (58 rows, old grammar 64) -> left pillar top at 7,013 (TAS +137), legal TAS
  rows in sync (+5 lantern) to X ~341, fbeam B-slash past the type-1 walker that hits us there (+10 lantern, hp 16), TAS-score
  beam to room 8. Room 8 next.
* art 2026-10-24 (Mesen; NesHawk trace running): **room 6 that KEEPS J&S at ZERO cost.** In p3b/s5 move the room-6 spin
  from rows 478-479 (B+Left, X 258: breaks + catches the Star at X 256) to **rows 489-490** (B+Left, X 242; rows 478-479
  = Left). The spin still kills the type-1 walker at the landing (that is why the TAS spins there; with no spin Ryu takes
  2 hits), the Star is NOT caught. Ryu's X/y/hp are IDENTICAL to s5 on every row to the room-8 change at 7,499 (RAM
  differs only in ninpo/art/OAM/sound + dead slot-7 leftovers). With J&S held, the air B presses of s5 become spins while
  ninpo >= 5 (rows 581, 1142, 1272, 1334: positions unchanged) -> **room 8 starts with J&S + ninpo 0** (s5: Star + 20).
  So the room-8 J&S lantern is NOT needed; room 8 must collect exactly 10 + 5 per spin used there. Rows:
  `work/l22a/p3j.txt` (= p3b edited), `work/l22a/s5j.txt` (= s5 edited; judge PASS). Main agent: please use p3j as
  your room-6 base (same frames). Tools: `work/l22a/var.py` / `cmp.py` (play with row edits, compare two lines).
  **art 13:25 CORRECTION: the J&S variant costs 20 ninpo, so it is the WORSE base.** The 4 air B presses in rooms 6-7
  (581/605 room-6 exit, 1142, 1272, 1334/1359) are NEEDED (stripping B moves the hit/divergence; each stripped press
  just moves the spin to the next B) and with J&S they are spins: J&S/0 at room 8 vs Star/20. On J&S/0 the room-8 beam
  (`work/l22a/r8f2.log`) runs out of spins and dies at X ~1215 (enemy where the TAS spins at TAS 7937). Plan now: keep
  the **Star line (s7/s9)**, free Star slashes on +5 X 1616 / +5 X 1552 (30 ninpo), catch J&S at X 1312 as the TAS
  does, then the TAS's spins; never Up+B with the Star (throw -3). Room-8 beam with item rules: `work/l22a/abeam.py`
  (`--items 129,133 --jsby 1270`: Star or J&S only, J&S required left of X 1270; `--need 10`: prune when ninpo +
  untaken lanterns ahead < 10; `--npeq 10` at the goal).

* r78 (Mesen + NesHawk power-on trace `logs/l22c_s7j.trace.csv`: s7j NesHawk = Mesen to the platform at 7,718, hp 15, J&S/0;
  pad conflicts 7240/7315/7323/7433 harmless): **room-8 bird damage boost found on our arrival.** From `work/l22c/s6e.txt[:1488]`
  (chimney U-cycle as puzzle's x_r8a, run right off the pillar top; state `states/mesen/l22f_c8e.mst`, X 1912 y 165 in the
  air) `R:10 L:1 AL:2 L:32 AL:2 L:53` (`work/l22p/x_c8b.txt`): go right to X 1926 (engages the camera), turn, jump so Ryu
  crosses X 1903 (= the bird's spawn trigger, scroll 1776) HIGH (y ~151: the bird spawns ~12 px above Ryu's y, sine top),
  land on the pillar top, jump again: the bird hits from the right at X 1827 y 115 (hp 15), knock-up onto the y-96 platform
  at X 1802 = **frame 7,718 (TAS 7541 +177; room-8 start costs +31 vs TAS)**. Rows: `work/l22c/s7.txt` (1,588) = art's
  `work/l22a/s7j.txt` (same positions, J&S). After it, legal TAS rows (lag 176) stay in sync to X 1478 (+5 +5 lanterns), an
  enemy hit there is dodged by fbeam to X 1400 at no loss (`work/l22c/s9.txt`, Star base). Split with the art agent: I keep
  improving the PACE parts (room 7 pillar, room-8 start/bird); art agent owns room 8 from the platform (ninpo plan).
  Idea for art: s7j's room-7 air B presses at rows 1142/1272/1334 come from my beams and may be removable (keep ninpo 20
  into room 8) - check they don't kill something needed (1142-1234 = walker dodge beam).

* r78 (Mesen + NesHawk power-on trace `logs/l22c_t9.trace.csv`: NesHawk = Mesen to the end, harmless conflicts 7240/7433):
  **NEW room-8 base, STAR line, 4 f faster than s9: `work/l22c/t9.txt` (1,852 stage rows) -> X 1399 y 128 at frame 7,982
  (s9: X 1400 at 7,986), hp 15, Star (129) + ninpo 30.** = s5b[:1390] (spawn) + joint chimney/bird grammar `work/l22p/x_c8d.txt`
  (no blank rows after the spawn: `R:2 (RU:2 ALU AL R)x7 ... AL:2 R:62 L:1 AL:2 L:32 AL:2 L:53` -> platform X 1801 at 7,714)
  + legal TAS rows from TAS 7543 (lag 171, +5 +5 lanterns) + fbeam past the X-1477 hit (`--freeze 7914`: a NesHawk DMC
  conflict ate an A press there). Art agent: please rebase room 8 on t9 (same pace as the TAS from here, lag 171-172).

* r78 (Mesen + NesHawk power-on trace `logs/l22c_v9.trace.csv`: NesHawk = Mesen, only conflict 7240 harmless; judge PASS):
  **faster Star prefix `work/l22c/v9.txt` (1,848 stage rows) -> X 1400 y 128 at frame 7,978 (t9: X 1399 at 7,982), hp 15,
  Star + 30.** Room 7: the type-1 walker at X ~341 is now KILLED by an air slash on TAS rows (B on TAS-follow rows 280-281
  from TAS 6877) instead of dodged, so legal TAS rows stay in sync to the exit ladder (+10 lantern); a NesHawk DMC conflict
  ate the A press at 7315 -> re-beamed that bit with `--freeze 7315` (+1); exit ladder beam width 128 -> room 8 at 7,496
  (was 7,499); then the same chimney/bird rows (`work/l22p/x_v8.txt`, platform X 1799 at 7,711) + TAS rows lag 167 + fbeam
  past the X-1477 hit. Running `work/l22a/r8pipe.sh work/l22c/v9.txt v9 167` now.

* r78: r8pipe's J&S stage FAILED on v9 (`v9j`: no J&S by X 1250). Plain legal TAS rows from TAS 7810 (lag 168) stay in sync
  from v9 through the J&S catch to X 953: `work/l22c/v10.txt` (2,136 rows, X 968 y 192 at 8,266, J&S 133 + 30, hp 15) =
  v9 + TAS rows. Running stages b+c of r8pipe from it (`work/l22c/r8tail.sh`, tag v10). Art: no need to redo v9's J&S part.

* r78: my v10 tail run finished anyway: `work/l22a/v10_full.txt` exits room 8 at X 40 on frame 8,891 (J&S + 10, hp 15) =
  the same exit frame as art's t12 (the 4 f gained before X 1400 were lost in the beam's X 900 -> 40 part). Not verified;
  left for the art agent. I stop room-8 work and stay on the prefix.

* r78 (Mesen + NesHawk power-on trace `logs/l22c_w10.trace.csv`: NesHawk = Mesen to the end, only conflict 7240; judge PASS):
  **prefix w, 2 f faster than v9: `work/l22c/w9.txt` (1,846 rows) -> X 1400 y 128 at 7,976 (Star/30), and `work/l22c/w10.txt`
  (2,134 rows) = w9 + legal TAS rows from TAS 7810 through the J&S catch -> X 968 y 192 at 8,264 (v10: 8,266), J&S 133 + 30,
  hp 15.** Gain = room-7 exit ladder 38 rows instead of 40 (`L:3 AL:2 L:17 RU:2 ALU AL - BR BRU ALU:2 L R RU ARU AR` from
  X 108 y 160: no mid-air A presses before the wall kick, so the kick/grab/jump A presses sit exactly 5 apart) -> room 8 at
  7,494. Same chimney/bird rows (`work/l22p/x_w8.txt`). Art: please finish room 8 on w10 (or w9).

### 2-3 round (locked: l23_t12_va) (prepared on the 2-2 candidate t12, agent l23, 2026-10-24)

Bomberhead with J&S + 10 ninpo, 2 spins. Record split 833.3 f, TAS 830. Tools `work/l23/` (`lib.py` Mesen states at
2-3 control/control-1, `play.py`, `grid.py`, `bftest.py`, `bftest2.py`, `subt.py`, `mkctl.py`).

Candidates (2-3):

| time | agent | file | 3-1 control | frames | vs record | hp/ninpo/item at 3-1 | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 16:05 | l23 | `logs/l23_t12_va_poweron.inputs.txt` (power-on, 9,998 rows = `logs/l23_t12_hist.inputs.txt` (= t12 power-on with row 9,172 = **Left**) + stage rows `logs/l23_t12_va.inputs.txt` (826 rows from 2-3 control); end state `states/l23_t12_va_end`) | 9,998 | **826** (TAS -4) | **-7.3** (cum -166.4 on t12) | 16 / 0 / -, `$BF` 0 | yes (verify finish from `states/l23_t12L_ctl`; `verify chain l23_t12_va_poweron`: two replays MATCH, RAM sha1 80237be8b2f5; boss 0 at 9,252 = control+80) | PASS | kill = TAS probe + the 2nd jump ON the landing frame (`Left+A`, `Up+Left+B+A`, `Up+Left+B` one row earlier than the TAS): control+80 vs TAS +81. Needs the 2-2 change below (row 9,172 Left). 3 of the 4 f vs the TAS are the timer tally (see "timer phase") |
| 2026-10-24 16:30 | l23 | fallback on t12 UNCHANGED: `logs/l23_t12_np.inputs.txt` (827 rows; end state `states/l23_t12_np_end`) | 9,999 | 827 | -6.3 | 16 / 0 / - | yes (verify finish from `states/l22_art_t12_end`) | PASS (verify) | same rows shifted 1 later (kill control+81); use only if the 2-2 lock keeps its last row blank |

Notes (2-3), all measured on Mesen, the va line also on NesHawk:
* **2-2 change for the coordinator (pre-control Left):** set the LAST row of the 2-2 stage file (power-on row 9,172 on t12 =
  stage row 3,042 of `logs/l22_art_t12.inputs.txt`) to `Left` instead of blank. NesHawk (`work/l23/mkctl.py`): 2-3 control
  frame stays 9,172, `$BF` stays 200, only Ryu x 206 instead of 208 (TAS: x 206 at the same point). Judge PASS. Worth 1 f in
  2-3. Left on the last TWO rows gives x 205 but no further gain (grid of 10,608 jump/spin/stop timings with x 205: best
  kill still control+80). The same edit applies to any 2-2 candidate whose last rows are the blank cutscene tail.
* **Kill floor = control+80.** First spin hit needs Ryu within 18 px right of Bomberhead; he walks right 0.5 px/f and stops
  when Ryu is ~34 px away, so the first hit is at control+64 whatever the jump; hits only while Ryu's feet are below y 168
  (12 frames before landing), so 12 + landing frame + 4 = 16 HP at +80. The TAS loses 1 f by jumping one frame after
  landing. Spin = invulnerable to contact (action 7), so no damage.
* **`$BF`-independent (task 2):** the va rows with `$BF` poked at control-1 by +1/37/56/101/128/200/255 (`bftest.py`) and
  400 frames before control, in room 8 before the boss spawns, by +13/77/150/222 (`bftest2.py`): Ryu, all 8 enemy slots,
  boss HP, timer and stage are IDENTICAL on every row through the 3-1 load (kill +80, load row 673). Ryu's x at control is
  fixed by the stage start (208, or 206 with the pre-control Left), hp is irrelevant (no hit). Needs: J&S held and ninpo
  exactly 10 at 2-3 control (2 spins; 5 more = +15 f at the tally).
* **Timer phase (NEW, affects every boss stage):** the post-kill tally counts the stage timer `$63` (3 f per unit, like
  ninpo). The sub-counter `$62` (59..0, timer -1 on the wrap) is NOT reset at stage loads; it is frozen while the game is
  not in play (stage end, intro) and runs during play. So its value at 2-3 control = its value when 2-2's play ended,
  i.e. it depends on the 2-2 (and earlier) frame count mod 60. Measured (`subt.py`, `$62` poked at control-1, timer 150):
  `$62` <= 19 -> timer 148 at the kill -> **826**; `$62` >= 20 -> 149 -> **829**. t12 arrives with `$62` = 0 (best edge).
  A 2-2 that is 1-19 f faster keeps 826; 20-60 f faster gives 829; ANY slower 2-2 gives 829 (wraps to 59). So compare
  2-2 candidates by the 3-1 control frame (2-2 + 2-3), not by the 2-3 control frame alone.

### 2-1 round (locked; v4 chosen over v3 2,818 f/0 ninpo and wall w2 2,823 f)

Start: `states/l12_v2_end` = 2-1 control frame 3,308 (hp 16, ninpo 0, J&S, `$BF` 224), power-on history
`logs/l12_v2_poweron.inputs.txt`. Record split 2,904.8 f (TAS ~2,802; record TAS +103). Old best 2,964 (+59, on a
different `$BF`, reference only). Target: 2-2 control <= frame 3,308 + 2,904 = **6,212**; aim well under.
Look-ahead: 2-2 needs no ninpo to start but its lanterns (room 6 +5/+10, room 7 +10, room 8) feed 2-3 Bomberhead
(J&S + >= 10 ninpo for the TAS-pace kill). Prefer 2-1 exits with more hp/ninpo when equally fast.

Candidates (2-1):

| time | agent | file | 2-2 control | frames | vs record | hp/ninpo/item | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 03:33 | wall | `logs/l21_wall_w1_poweron.inputs.txt` (power-on, 6,130 rows; stage rows `logs/l21_wall_w1.inputs.txt`, end state `states/l21_wall_w1_end`) | 6,130 | **2,822** | **-82.8** (TAS +20) | 16 / 5 / J&S (133), `$BF` 230 | yes (verify finish + `verify chain l21_wall_w1_poweron`: two replays MATCH, RAM sha1 2f1da2a672be) | PASS | room 2 = follow's `work/l21f/s_f2.txt` (room 3 at 4,280, TAS +9); pillar U-cycle climb (+7); TAS rows in sync through room 3 (+0); exit ladder (+4); room 4 wall rows (+6); room 5 TAS rows in sync (+0) |
| 2026-10-24 04:00 | wall | `logs/l21_wall_w2_poweron.inputs.txt` (power-on, 6,131 rows; stage rows `logs/l21_wall_w2.inputs.txt`, end state `states/l21_wall_w2_end`) | 6,131 | **2,823** | **-81.8** (TAS +21) | **16 / 10 / J&S**, `$BF` 231 | yes (verify finish + `verify chain l21_wall_w2_poweron`: two replays MATCH, RAM sha1 4fa94546f429) | PASS | = w1 + a J&S spin (Up+B, Up+B+Right on pillar rows 122-123, just before the pillar-top landing) that breaks room 3's +10 lantern at X 272 (the TAS does this spin on the ladder at 4296); TAS rows from 4387 instead of 4388 keep sync. Costs 1 f, exits with the TAS's 10 ninpo (2-3 Bomberhead wants >= 10) |
| 2026-10-24 04:05 | follow | `logs/l21f_fol_v3_poweron.inputs.txt` (power-on, 6,126 rows; stage rows `logs/l21f_v3.inputs.txt`, end state `states/l21f_v3_end`) | 6,126 | **2,818** | **-86.8** (TAS +16) | 16 / 0 / J&S (133), `$BF` 226 | yes (verify finish + `verify chain l21f_fol_v3_poweron`: two replays MATCH, RAM sha1 1e01710aceb4) | PASS | room 2 TAS rows + 2 mbrute repairs (club guy, +5 lantern) + pole/wall Mesen beam (room 3 at 4,280, +3); room 3 start climb + ledge beam (NesHawk-clean variant, +4 at the ledge turn); TAS rows in sync to the exit; exit beam (+3); room 4 = beam rows (125 f from the room change, +6); room 5 TAS rows. Ninpo 0: no +10 lantern in room 3 (see wall w2's spin) |
| 2026-10-24 04:55 | follow | `logs/l21f_fol_v4_poweron.inputs.txt` (power-on, 6,130 rows; stage rows `logs/l21f_v4.inputs.txt`, end state `states/l21f_v4_end`) | 6,130 | **2,822** | **-82.8** (TAS +20) | **16 / 10 / J&S**, `$BF` 230 | yes (verify finish + `verify chain l21f_fol_v4_poweron`: two replays MATCH, RAM sha1 21f1b749168e) | PASS | = v3 + Up+B on row 1091 (frame 4400, landing on the pillar top; breaks room 3's +10 lantern) + 1 Right (sync shift, +1); room-3 exit re-beamed WITHOUT spending ninpo (`--npmin 10`; v3's B+Right climb cycles spent 2 J&S spins, +4 incl. shift); room 4 = wall agent's `work/w21/r4_rows.txt` (v3's room-4 rows had B+Right = spins); room 5 TAS rows. 1 f faster than w2 with the same 10 ninpo |

Agent notes (2-1): share segment finds here (agent, room/segment, rows file, entry/exit frames, what it needs).

* wall 02:50 (technique, Mesen-measured): all three 2-1 climbs (room 2's end wall at the exit, room 3's pillar, room 4's
  start) are LADDER tiles (kind 9, coll 32 = "steps"). Fastest legal ladder climb found (cycle enumeration, ladder on
  Ryu's right): `R, R+U, R+U, A+L+U, A+L` repeated (A+L = the jump-off, A+L+U = grab frame that also climbs 1 px) =
  **1.8 px/f** (TAS 2.0; `L, A+L, A+R, R, R` 1.6; C8 ~1.55). Legal with any history that has no R/U/A/L press in the
  4 frames before. Tool: `work/w21/cycles.py`.
* wall 03:35 (NesHawk-confirmed inside `l21_wall_w1`): segments after follow's room-2 prefix `work/l21f/s_f2.txt` (room 3
  change at 4,280): (a) pillar `work/w21/p3c2_best.txt` (124 rows from 4,280: 19 blank, `R RU RU ALU AL` x9 ladder
  climb, Left 24 to the ledge, turn R 1, A+Right, Right -> pillar top X 170 y 128 at 4,404 = TAS 4388 +16);
  (b) legalized TAS rows from TAS 4388 replay IN SYNC through room 3 to TAS 5071 (`work/w21/r3f_rows.txt`, 683 rows;
  hp 16, but the +10 lantern at TAS ~4449 is NOT broken: ninpo 20 -> 5 by the room exit); (c) room 3 exit ladder
  `RU:2 ALU AL R RU:2 ALU AL R RU:2 ALU` (13 rows) -> room 4 at 5,100 (TAS +20); (d) ROOM 4 (no enemies, graft at room change
  + 20 frames): `work/w21/r4_rows.txt` (105 rows; TAS 99, old 186): `-:3 U:2 A+L:2 L:13 R A+R:2 R` lands on the right
  platform (159,160) at row 43, then `L A+L:2 L:27 -:2 R:4 A+R:2 R` -> room 5 at row 105 (land on the y-128 floor, turn, jump right);
  (e) room 5 = legalized TAS rows from TAS 5199 in sync to the stage end. Rows in order: `work/w21/r34x_rows.txt`
  (= c + 20 blank + d), `work/w21/r5f_rows.txt`.

* follow 04:05: `work/l21f/fbeam.py` = frame-synchronous legal beam on Mesen (every frame each node tries an alphabet row
  through its own Enforcer copy; dedupe by state; scores: `tas --lag L` (track the TAS trajectory), `wp --wps x:y,..`
  (waypoint chain), `z`/`y`; goals room:R, g:R:xlo:xhi:y (on ground), x:..; `--freeze f1,f2` = keep the previous row on
  those frames (to dodge a known NesHawk DMC conflict)). Found the 2-px/f legal climb cycle `A+L, L, -, B+R, A+B+R`
  (B+Right air slash pulls Ryu back to the wall in 2 frames). NesHawk conflicts cluster after slashes (DMC samples):
  re-run the beam at another width and check each solution with `work/l21f/nhseg.py` (NesHawk from a segment state)
  instead of freezing (freeze cost +5 at room 3's start, a different beam width cost +2 and was clean).

### 1-2 round (locked)

1-1 locked 2026-10-23 (repair agent, 2,300 f, record -9.8). Start: `states/l11_rep_r1_end` = 1-2 control frame 2,474
(hp 15, ninpo 10, J&S, `$BF` 161), history `logs/l11_rep_r1_poweron.inputs.txt`.
Baseline: round 1's rows `logs/tk_1-2_s11.inputs.txt` replay unchanged: 838 f (record 841.4 -> -3.4; TAS 834),
2-1 control 3,312 (verify chain `lock_to21`). Target: < 838 if possible (TAS floor ~834); else lock 838.
Look-ahead for 2-1/2-2/2-3: 2-3 Bomberhead wants J&S + >= 10 ninpo (TAS-pace kill); 2-1 starts with hp 16.

Candidates (1-2):

| time | agent | file | 2-1 control | frames | vs record | hp/ninpo/item | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 01:10 | l12 | `logs/l12_s1_poweron.inputs.txt` (power-on, 3,310 rows = locked 1-1 UNCHANGED + stage rows `logs/l12_s1.inputs.txt`; end state `states/l12_s1_end`) | 3,310 | **836** | **-5.4** (TAS +2) | 16 / 0 / - | yes (verify finish + `verify chain l12_s1_poweron`: two replays MATCH, RAM sha1 308fa1a48c28) | PASS | = round-1 kill rows (boss 0 at 2,562) + the earliest legal Start (2 f earlier than the old rows). Strict-lock floor: kill 88 is minimal (see note below) |
| 2026-10-24 01:40 | l12 | `logs/l12_v2_poweron.inputs.txt` (power-on, 3,308 rows; 1-1 part `logs/l12_v2_11.inputs.txt`, stage rows `logs/l12_v2.inputs.txt`; end state `states/l12_v2_end`) | 3,308 | **834** | **-7.4** (TAS +0) | 16 / 0 / - | yes (verify finish + `verify chain l12_v2_poweron`: two replays MATCH, RAM sha1 843274aa06d8) | PASS | **VARIANT - touches the locked 1-1 file**: rows 2473-2474 Right instead of blank (as the TAS does). Same 1-1 control frame 2,474, same `$BF` 161, only Ryu x 35 instead of 32; boss 0 at 2,560. Coordinator's call |

1-2 lock round note (l12, 2026-10-24): with the locked 1-1 rows untouched the floor is 836 (kill at control+88: the spin only reaches Barbarian once Ryu x >= 140 = offset 72, a jump's spin gives at most 12 hits, so 16 hits + 1 landing frame = 88; Mesen grids over jump/B/turn timing and landing-frame inputs found nothing below 88). The 2 f to the TAS sit in the last two rows of the locked 1-1 file (the TAS already holds Right on 1-2 control-1 and control); the 834 variant needs them. Details: legal_a12_notes.md "1-2 lock round".


### 1-1 round (locked)

Target: 1-2 control at or before frame 174 + 2,309 = **2,483** (record split 2,309.8 f; TAS 2,294; our old best
2,373 = `logs/tk_1-1_s11`, +63). Exit with J&S and >= 10 ninpo (1-2 Barbarian rows `logs/tk_1-2_s11` = 838 f, record
-3, need J&S + 10 and were found deterministic; re-check them on the new 1-1 exit).

Candidates (each agent appends; coordinator locks):

| time | agent | file | 1-2 control | frames | vs record | hp/ninpo/item | NesHawk verified | judge | note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-23 22:56 | repair | `logs/l11_rep_r1_poweron.inputs.txt` (power-on, 2,474 rows; stage rows `logs/l11_rep_r1.inputs.txt`, end state `states/l11_rep_r1_end`) | 2,474 | 2,300 | **-9.8** (TAS +6) | 15 / 10 / J&S (133) | yes (verify finish + `verify chain l11_rep_r1_chain`: two power-on replays MATCH, RAM sha1 f9dd2f174249) | PASS | 1-2 rows `logs/tk_1-2_s11` replay unchanged from it: 838 f, 2-1 control 3,312 (hp 16). Exit `$BF`/rng 161 at control |
