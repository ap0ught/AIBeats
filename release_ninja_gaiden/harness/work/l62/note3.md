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
