"""Probe 14 (snapshot poke on the OLD run): after the second corridor mine the ground is dry (the vertical sub-pixel $466 drops 79 per ground
frame).  If our repair there waits w more frames, $466 is off by -79*w from then on.  Which w does the rest of the level tolerate?
From the old run at L9c 8785 set $466 := old - 79*w and replay the old inputs to 9987: frames whose toad track differs, first hp/level diff."""
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p14.log"); goto(e, OFF + 8785, ins); e.save("L9heli_8785"); base = e.msave()
m0 = bytes(R[OFF + 8785 - 1])
for w in list(range(-8, 25)):
    e.mload(base); e.poke(0x466, (m0[0x466] - 79 * w) & 255)
    nd = 0; first = None; hpd = None
    for k in range(8785, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if a != c:
            nd += 1
            if first is None: first = (k + 1, a, c)
            if hpd is None and a[3:] != c[3:]: hpd = (k + 1, a, c)
    print(f"w {w:+d} ($466 {(m0[0x466] - 79 * w) & 255}): diff frames {nd} first {first} hp/level first {hpd} end level {m[0x10]}", flush=True)
e.close()
