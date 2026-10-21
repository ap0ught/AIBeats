"""Probe 5 (snapshot, debug poke): which hidden toad bytes matter for the rest of Level 9?  From the old route at L9c 8264
(running on the floor) poke one byte, replay the old inputs to the level end (index 9987) and report: frames whose toad track
(x, H, z, hp) differs from the old run, first/last such frame, level byte at the end, non-volatile RAM diffs at the end."""
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
VOL = set(range(0x100, 0x300)) | set(range(0x700, 0x800)) | {0x0B, 0x0C, 0x25, 0x26, 0x27, 0x28}
e = BizHawk(log_name="l9heli_fix_p5.log"); e.load("L9heli_8264"); base = e.msave()
def run(tag, pokes):
    e.mload(base)
    for a, v in pokes: e.poke(a, v)
    nd = 0; first = last = None; hurt = None
    for k in range(8264, 9987):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); b = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
        if a != b:
            nd += 1; last = k + 1
            if first is None: first = (k + 1, a, b)
            if hurt is None and a[3] != b[3]: hurt = (k + 1, a, b)
    d = [x for x in range(0x800) if x not in VOL and m[x] != ref[x]]
    print(tag, "| diff frames", nd, "first", first, "last", last, "hp/level diff first", hurt, "| end level", m[0x10], "ram diffs", len(d), [hex(x) for x in d[:12]], flush=True)
m0 = bytes(R[OFF + 8264 - 1])
run("control", [])
for d in (8, 40, 79, 128, 177, 248):
    run(f"$466 +{d}", [(0x466, (m0[0x466] + d) & 255)])
for d in (1, 3, 7):
    run(f"$3DF +{d}", [(0x3DF, (m0[0x3DF] + d) & 255)])
run("$592 = 0", [(0x592, 0)])
run("cam x -6", [(0x87, (m0[0x87] - 6) & 255)])
run("cam x +6", [(0x87, (m0[0x87] + 6) & 255)])
run("timer $0B +100", [(0x0B, (m0[0x0B] + 100) & 255)])
run("timer $0C +50", [(0x0C, (m0[0x0C] + 50) & 255)])
run("dice $25-28 = 1,2,3,4", [(0x25, 1), (0x26, 2), (0x27, 3), (0x28, 4)])
e.close()
