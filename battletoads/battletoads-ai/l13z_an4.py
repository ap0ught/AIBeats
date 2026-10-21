"""queen slot tables over time"""
import sys
seg, lo, hi, st = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
slot = int(sys.argv[5]) if len(sys.argv) > 5 else None
raw = open(f"logs/fix/l13z_ts_{seg}.bin", "rb").read()
R = lambda n: raw[(n - 1) * 0x800:n * 0x800]
bases = list(range(0x3C1, 0x5A0, 15))
print("n    0B  586 | " + " ".join(f"{b:03x}" for b in bases))
for n in range(lo, hi, st):
    r = R(n)
    s = slot
    if s is None:
        s = next((k for k in range(2, 15) if r[0x3C1 + k] in (0x7E, 0x46)), None)
    if s is None:
        print(n, "no queen"); continue
    print(f"{n:4d} {r[0x0B]:3d} {r[0x586]:3d} | " + " ".join(f"{r[b + s]:3d}" for b in bases))
