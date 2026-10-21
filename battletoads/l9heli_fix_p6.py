"""Probe 6 (snapshot, debug pokes): tolerance of the old route after L9c 8279 (running left at 96, one frame before its jump) to
(a) a camera-x offset, (b) the floor mine's position/absence, (c) the shark's position, (d) anim timer, (e) global timer/dice.
Replay old inputs to index 9987; report toad-track diff frames and the first hp/level diff."""
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p6.log"); e.load("L9heli_8279"); base = e.msave()
m0 = bytes(R[OFF + 8279 - 1])
def run(tag, pokes):
    e.mload(base)
    for a, v in pokes: e.poke(a, v & 255)
    nd = 0; first = last = None; hurt = None; camd = []
    for k in range(8279, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); b = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if (k - 8279) in (20, 60, 100, 140, 180, 400): camd.append((m[0x87] | m[0x88] << 8) - (ref[0x87] | ref[0x88] << 8))
        if a != b:
            nd += 1; last = k + 1
            if first is None: first = (k + 1, a, b)
            if hurt is None and a[3:] != b[3:]: hurt = (k + 1, a, b)
    print(f"{tag:28s} diff frames {nd:4d} first {first} hp/level first {hurt} cam delta at +20/60/100/140/180/400: {camd} end level {m[0x10]}", flush=True)
run("control", [])
cam0 = m0[0x87] | m0[0x88] << 8
for d in (-16, -12, -9, -6, -3, -2, -1, 1, 2, 3, 6):
    c = cam0 + d; run(f"cam {d:+d}", [(0x87, c & 255), (0x88, c >> 8)])
q = [q for q in range(2, 15) if m0[0x3C1 + q] == 0x72][0]; mx = m0[0x3FD + q] | m0[0x3EE + q] << 8
for d in (-30, 40, 120):
    x = mx + d; run(f"mine x {d:+d} (was {mx})", [(0x3FD + q, x & 255), (0x3EE + q, x >> 8)])
run("mine removed (id=0)", [(0x3C1 + q, 0)])
q = [q for q in range(2, 15) if m0[0x3C1 + q] == 0x70][0]; sx = m0[0x3FD + q] | m0[0x3EE + q] << 8
for d in (-20, 20):
    x = sx + d; run(f"shark x {d:+d} (was {sx})", [(0x3FD + q, x & 255), (0x3EE + q, x >> 8)])
for d in (1, 2, 4, 8):
    run(f"anim timer $3DF +{d}", [(0x3DF, m0[0x3DF] + d)])
run("$0B +77, dice 9,9,9,9", [(0x0B, m0[0x0B] + 77), (0x25, 9), (0x26, 9), (0x27, 9), (0x28, 9)])
e.close()
