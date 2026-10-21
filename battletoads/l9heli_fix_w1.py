"""Water pocket probe: from the stage-AB end (L9heli_AB0: L9c 7873, (861, 6438) falling) wait d frames then hold Right (or Right for r frames
then nothing).  Does the toad get into the water under the (884-904, 6406) ledge (anim 98/99)?  Print the track."""
from l9heli_fix_lib import *
import l9heli_fix_tail as T
e = BizHawk(log_name="l9heli_fix_w1.log", fields=T.FLD); e.load("L9heli_AB0"); root = e.msave()
for d in range(0, 24, 2):
    for r in (60,):
        e.mload(root); out = []; swim = None; dead = None
        seq = [""] * d + ["Right"] * r
        for i, b in enumerate(seq):
            s = e.step(bt(b), 1); x = s.x | s.xh << 8; H = s.h | s.hh << 8
            if s.hp < 47: dead = (i + 1, x, H); break
            if swim is None and s.an in (98, 99): swim = (i + 1, 7873 + i + 1, x, H)
            if i % 4 == 3: out.append((x, H, s.an, s.spd))
        print(f"d {d}: swim {swim} dead {dead} track {out[:16]}", flush=True)
e.close()
