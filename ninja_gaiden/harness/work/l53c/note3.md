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
