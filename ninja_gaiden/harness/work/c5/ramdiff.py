"""RAM diff of two NesHawk states (+ boss x/y over N idle frames from each)."""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
a, b = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 0
e = C.open_emu("c5_ramdiff_emu.log")
try:
    out = {}
    for s in (a, b):
        st = e.load(s)
        r0 = e.ram_all()
        tr = []
        for k in range(N):
            e.run([()])
            r = e.ram_all()
            tr.append((r[0x460:0x468].hex(), r[0x480:0x488].hex(), r[0x497], r[0x400:0x408].hex()))
        out[s] = (st, r0, tr)
    ra, rb = out[a][1], out[b][1]
    print("frames", out[a][0]["frame"], out[b][0]["frame"])
    d = [i for i in range(0x800) if ra[i] != rb[i]]
    print(len(d), "differing bytes")
    for i in d:
        if i < 0x100 or 0x400 <= i < 0x500 or 0x500 <= i < 0x600:
            print(f"${i:03X}: {ra[i]:3d} {rb[i]:3d}")
    for k in range(N):
        if out[a][2][k] != out[b][2][k]:
            print("idle frame", k + 1, "differs:", out[a][2][k], "|", out[b][2][k])
            break
    else:
        print("idle frames identical in enemy x/y")
finally:
    e.close()
