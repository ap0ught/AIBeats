"""Probe 8 (snapshot poke): is the leftover propeller bug in slot 4 why the old inputs get hit at 8574 after our join?  From the T' bookmark
remove object slot 4 (id := 0), replay the old inputs and compare with the old run."""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p8.log")
for tag, pokes in [("control", []), ("slot 4 id=0", [(0x3C1 + 4, 0)]), ("slot 4 and 6 id=0", [(0x3C1 + 4, 0), (0x3C1 + 6, 0)])]:
    e.load(sys.argv[1])
    for a, v in pokes: e.poke(a, v)
    first = None; nd = 0; hpd = None
    for k in range(8279, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if a != c:
            nd += 1
            if first is None: first = (k + 1, a, c)
            if hpd is None and a[3:] != c[3:]: hpd = (k + 1, a, c, ostr(m), ostr(ref))
    print(tag, "| diff frames", nd, "first", first, "hp/level first", hpd, "| end level", m[0x10], flush=True)
e.close()
