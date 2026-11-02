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
