"""Probe 10 (snapshot poke): frame-counter parity.  Our join leaves the propeller bugs in slots 4 and 6, so the corridor mines land in ODD
slots (7, ...) instead of the old run's even ones.  If collision tests run on (frame + slot) parity, shifting the frame counter $0B by one at
T' should make the old inputs work again.  Test $0B += d for d in 0, 1, 2, 3, 5."""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p10.log")
e.load(sys.argv[1]); m0 = e.ram(0, 0x800); print("at T': $0B", m0[0x0B], "old $0B at 8279:", R[OFF + 8279 - 1][0x0B], flush=True)
for d in (0, 1, 2, 3, 5, 255):
    e.load(sys.argv[1]); e.poke(0x0B, (m0[0x0B] + d) & 255)
    first = None; nd = 0; hpd = None
    for k in range(8279, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if a != c:
            nd += 1
            if first is None: first = (k + 1, a, c)
            if hpd is None and a[3:] != c[3:]: hpd = (k + 1, a, c)
    print(f"$0B +{d}: diff frames {nd} first {first} hp/level first {hpd} | end level {m[0x10]}", flush=True)
e.close()
