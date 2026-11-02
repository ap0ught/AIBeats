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
