* **l62 (2026-10-28 ~09:35) room-40 pit: the floor jump is proven too short; the high route is working (paused for RAM).**
  * **Proven: a plain jump from the y-208 floor peaks at y 160 (48 px), so it can never reach the y-128 block.** Grid from our 35,300 state
    (X 494 floor): jump start 35,301-35,312, A held 2/4/8/16/30 f, Right or neutral (120 cases, `work/l62/jh.py`): apex y 160 in every case.
    The y 129-133 apexes seen in the beams came from hits / other boosts, not jumps. Floor-only beams without a boost are pointless.
  * **High route (beam `r40h1`, from the y-96 platform 35,046 = `b_r40g.txt`, floor penalised before X 620):** stays high via the X ~432
    pillar (Ryu at X 428 y 160 on 35,257, over it by 35,307) and is **on the way onto the y-96 ledge: X 477 y 84 on 35,337** (hp 12: one
    3-hp hit on the way, J&S kept, np 0). Stopped there because free RAM fell under 800 MB (owner's game). **Checkpoint rows
    `work/l62/r40h1_ckpt.txt`** (rows from 33,590 to 35,337). For comparison the floor line was at X 497 on 35,302, so the high route costs
    ~+30 f to here but avoids the thrower/ghoul and the pit.
  * Ghoul-boost wait grid (`gb.py`, 6,300 cases) was killed with the RAM drop before it reported; not run.
  * **Resume:** `python -u work/l62/b62.py 33589 0 r40h2 --mst states/mesen/l62_33589.mst --prefix work/l62/r40h1_ckpt.txt --goal
    'X>=704 and y==208 and rm==40 and it==133' --score 'X-(400 if (y>=200 and X<620) else 0)-0.2*y' --frames 300 --width 150 --minhp 2
    --dbg 10 --alpha 'Right|A+Right|B+Right|-|A|B|Left|A+Left'`, then `fin.py` -> judge -> `nhrun.py ... l62f_34900 34901 <end> 0`.
