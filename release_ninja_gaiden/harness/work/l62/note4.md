* **l62 (2026-10-28 ~06:05) room 39 + room-40 entry on our real line (NesHawk-checked to room 40); room-40 rest beam running.**
  * Ninpo target noted (coordinator): **J&S + 0..4 at the 6-3 control**. Our line is at np 0 from room 39's exit on; the room-40 beam requires
    np < 5 at the trigger.
  * **Room 39** (real state; the thrower t2 / axes at X ~547 read the arrival, so TAS-state rows die): entry cycle (`r39_ent84.txt`) + beam
    `b_r39d` (score X, width 150: room 40 on 34,897) + end re-beam `b_r39f` from 34,800 (score X - 3y: the exit (667, 84) is a climb):
    **room 40 on 34,877 = room 39 in 502 f (TAS 444: +58; record +20.8)**. One spin for the batter t3 (np 5 -> 0), +10 lantern X 544 taken
    and spent (2nd spin), a 3rd spin at the exit climb. hp 15. Rows: `work/l62/b_r39f.txt` (from 33,590, through room 37-39).
    Power-on `work/l62/l62_po_r40f.inputs.txt` (34,924 rows): **judge PASS; NesHawk from `l62e_34397`: room 40 on 34,877, events = Mesen,
    0 pad-read conflicts, RAM at 34,924 = Mesen (0 diffs)**; NesHawk state `l62f_34900` (room-40 control - 1).
  * **Room 40 entry** (control = change + 23; the cycle from change + 24 = TAS's): `[Left, A+Left, A, A+Right, Right, Right] x4` then beam
    `b_r40g` (staircase y-192 -> y-160 -> y-128 ledge -> y-96 platform): **on the platform (X >= 112, y <= 96) on 35,046** = change + 169
    (TAS: X 112 on the platform ~ change + 145). Over-the-wall route (climb the X-160 face, which IS a ladder from the left at 1 px/f, to
    y 131-148, then right over the wall): **not found** (beam `r40h` width 200, 130 f; cycle grids `cyc_r40top.out` / `r40top.py` found only
    false goals = falls into the pit; not proven impossible).
