"""Probe 7 (snapshot pokes): does the global frame counter's phase matter for the old route after L9c 8279?  $0B += d for several d,
dice alone, $0C alone.  Replay to 9987 and report toad-track diffs."""
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p7.log"); e.load("L9heli_8279"); base = e.msave()
m0 = bytes(R[OFF + 8279 - 1])
def run(tag, pokes):
    e.mload(base)
    for a, v in pokes: e.poke(a, v & 255)
    nd = 0; first = None; hurt = None
    for k in range(8279, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); b = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if a != b:
            nd += 1
            if first is None: first = (k + 1, a, b)
            if hurt is None and a[3:] != b[3:]: hurt = (k + 1, a, b)
    print(f"{tag:22s} diff frames {nd:4d} first {first} hp/level first {hurt}", flush=True)
for d in (1, 2, 3, 4, 6, 8, 16, 32, 64, 128, 229, 244, 250):
    run(f"$0B +{d}", [(0x0B, m0[0x0B] + d)])
run("$0C +1", [(0x0C, m0[0x0C] + 1)])
for dice in ((9, 9, 9, 9), (1, 2, 3, 4), (200, 100, 50, 25), (0, 0, 0, 0)):
    run(f"dice {dice}", [(0x25 + i, v) for i, v in enumerate(dice)])
e.close()
