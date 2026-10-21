"""Analyse a l13z_probe1 RAM dump: object table per frame around the kill and through the ending."""
import json, sys
tag = sys.argv[1]
idx = json.load(open(f"logs/fix/l13z_{tag}_ram.json"))
raw = open(f"logs/fix/l13z_{tag}_ram.bin", "rb").read()
i0 = idx["from"]
N = len(raw) // 0x800
R = lambda n: raw[(n - i0) * 0x800:(n - i0 + 1) * 0x800]     # RAM after input n
def objs(r):
    o = []
    for s in range(0, 15):
        if r[0x3C1 + s]:
            o.append((s, r[0x3C1 + s], r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s], r[0x41B + s], r[0x475 + s], r[0x51A + s], r[0x3B5 + s], r[0x4B1 + s]))
    return o
lo, hi, st = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
for n in range(lo, min(hi, i0 + N), st):
    r = R(n)
    print(n, "lv", r[0x10], "0B", r[0x0B], "586", r[0x586], "585", r[0x585], " ".join(f"[{s}:{i:02x} x{x} h{h} y{y} z{z} hp{hp} an{an} st{stt}]" for s, i, x, h, y, z, hp, an, stt in objs(r)))
