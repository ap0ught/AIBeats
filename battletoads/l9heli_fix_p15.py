"""Probe 15 (snapshot poke on the OLD run): how exact must the vertical sub-pixel $466 be at the join T' (L9c 8279, old value 118)?
$466 := 118 + d for small d, replay the old inputs to 9987."""
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p15.log"); e.load("L9heli_8279"); base = e.msave()
for d in (-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 10, 16):
    e.mload(base); e.poke(0x466, (118 + d) & 255)
    nd = 0; first = None; hpd = None
    for k in range(8279, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if a != c:
            nd += 1
            if first is None: first = (k + 1, a, c)
            if hpd is None and a[3:] != c[3:]: hpd = (k + 1, a, c)
    print(f"d {d:+d}: diff frames {nd} first {first} hp/level first {hpd} end level {m[0x10]}", flush=True)
e.close()
