from l9heli_fix_lib import *
import l9heli_fix_tail as T
e = BizHawk(log_name="l9heli_fix_t15.log", fields=T.FLD); e.load("L9heli_7819")
for b in T.TRUNK + ["Left"] * 18: s = e.step(bt(b), 1)
for i in range(22):
    s = e.step(("A",) if i < 4 else (), 1)
    print(i + 1, 134 + 18 + i + 1, "x", s.x | s.xh << 8, s.sub, "dH", (s.h | s.hh << 8) - 6182, "spd", s.spd, "hp", s.hp, "an", s.an, "mine", T.mine(e), flush=True)
e.close()
