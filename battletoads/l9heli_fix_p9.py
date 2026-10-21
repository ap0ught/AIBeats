"""Probe 9 (snapshot pokes): which slot layouts let the old inputs replay after the join?  From the T' bookmark:
 a) remove bug 2 (slot 6) only          -> corridor mine in slot 6
 b) move bug 1 from slot 4 to slot 12   -> corridor mine in slot 4, bug still exists
 c) move the floor mine (slot 5) to 12  -> corridor mine in slot 5
 d) put a dummy copy of bug 2 into slot 7 too (slots 4,6,7 used) -> corridor mine in slot 8"""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p9.log")
def move(m, src, dst):
    out = []
    for base in range(0x3C1, 0x5EC, 15):
        out.append((base + dst, m[base + src])); out.append((base + src, 0))
    return out
def copy(m, src, dst):
    return [(base + dst, m[base + src]) for base in range(0x3C1, 0x5EC, 15)]
e.load(sys.argv[1]); m0 = e.ram(0, 0x800)
tests = [("a) bug 2 removed", [(0x3C1 + 6, 0)]), ("b) bug 1 -> slot 12", move(m0, 4, 12)), ("c) floor mine -> slot 12", move(m0, 5, 12)), ("d) bug 2 copied to slot 7", copy(m0, 6, 7)),
         ("e) bug 1 -> slot 7", move(m0, 4, 7)), ("f) bug 1 -> slot 8", move(m0, 4, 8))]
for tag, pokes in tests:
    e.load(sys.argv[1])
    for a, v in pokes: e.poke(a, v)
    first = None; nd = 0; hpd = None; slots = None
    for k in range(8279, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        if k + 1 == 8460: slots = " ".join(f"{m[0x3C1 + q]:02x}" if m[0x3C1 + q] else "--" for q in range(2, 15))
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if a != c:
            nd += 1
            if first is None: first = (k + 1, a, c)
            if hpd is None and a[3:] != c[3:]: hpd = (k + 1, a, c)
    print(tag, "| slots at 8460:", slots, "| diff frames", nd, "first", first, "hp/level first", hpd, "| end level", m[0x10], flush=True)
e.close()
