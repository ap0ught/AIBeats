* **l62 (2026-10-28 ~04:30) TASK 1 DONE: 6-1 arrival on our line = Start 2 f later than the earliest, head start TAS-exact on NesHawk to room 37.**
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
