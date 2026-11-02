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
