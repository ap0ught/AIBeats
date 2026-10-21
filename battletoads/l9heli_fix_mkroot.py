"""Make the root for the fall beam: L9heli_7819 + the S1 tunnel pass (Right x18, Right+A x2, Right x17 = 37 frames) -> bookmark L9heli_s1end
(L9c index 7856).  Also prints a few alternative S1 endings."""
from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_mkroot.log")
for name, seq in [("L9heli_s1end", ["Right"] * 18 + ["Right+A"] * 2 + ["Right"] * 17), ("L9heli_s1end_b", ["Right"] * 19 + ["Right+A"] * 3 + ["Right"] * 15)]:
    e.load("L9heli_7819")
    for b in seq: e.step(bt(b), 1)
    m = e.ram(0, 0x800); print(name, len(seq), tstr(m), "vy", m[0x4C0], m[0x4CF], "subH", m[0x466], "|", ostr(m)); e.save(name)
e.close()
