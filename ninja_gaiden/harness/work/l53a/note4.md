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
