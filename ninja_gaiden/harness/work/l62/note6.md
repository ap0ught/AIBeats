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
