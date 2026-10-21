"""Face 3's lap (2026-10-03): the toad lands on the circling platform at old frame 8616 and rides a whole lap before the
bounce-launch to the small sinking platform at x 64 (old 8892-8959). Scan launches on the FIRST pass: wait w, then
A / dir+A alternations (the arming), then dir+A held; success = standing on the small platform (x 40..90, h 4928..4946).
    python l12lap.py -> knowledge/l12_lap_launch.json (inputs from L12_lap), prints the landing state"""
import itertools, json
from toads.emulator import BizHawk
e = BizHawk(log_name="l12lap_scan.log"); e.load("L12_lap"); root = e.msave()
def rd():
    m = e.ram(0, 0x800)
    return m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x11], m[0x565]
hp0, lives0 = rd()[3], rd()[4]
best = None
for w, d, s0, mm, hold in itertools.product(range(0, 90, 2), ("Left", "Right"), (0, 2, 4), (0, 2, 4, 6, 8, 10, 12, 14), (60, 120)):
    if best and w > best[0]: break
    e.mload(root); seq = [""] * w + ["A"] * s0 + [d + "+A", "A"] * mm + [d + "+A"] * hold + [""] * 40
    air = False
    for i, b in enumerate(seq):
        e.step(tuple(v for v in b.split("+") if v), 1); x, h, z, hp, lives, spd = rd()
        if hp < hp0 or lives < lives0: break
        if z: air = True
        if air and z == 0:
            if 40 <= x <= 90 and 4928 <= h <= 4946:
                tot = i + 1
                if best is None or tot < best[0]:
                    best = (tot, seq[:tot], (w, d, s0, mm, hold), (x, h, spd))
                    print("LANDED", best[2], "at", tot, "state", best[3], flush=True)
                    json.dump(best[1], open("knowledge/l12_lap_launch.json", "w"))
            break
print("best", best[0] if best else None, "(old: 8959 - 8616 = 343)")
e.close()
