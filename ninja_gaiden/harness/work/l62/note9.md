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
