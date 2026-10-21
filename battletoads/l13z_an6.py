"""toad + queen per frame with inputs, for a window"""
import sys, json
seg, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ins = json.load(open(f"logs/pbeam_{seg}.json"))["inputs"]
raw = open(f"logs/fix/l13z_ts_{seg}.bin", "rb").read()
R = lambda n: raw[(n - 1) * 0x800:n * 0x800]
for n in range(lo, hi):
    r = R(n)
    s = next((k for k in range(2, 15) if r[0x3C1 + k] in (0x7E, 0x46)), None)
    q = f"Q x{r[0x3FD+s]:3d} h{r[0x439+s]:3d} z{r[0x475+s]} vy{((r[0x4C0+s]<<8|r[0x4CF+s])+32768)%65536-32768:6d} kb{r[0x565+s]:3d} d{r[0x556+s]:3d} f{r[0x4A2+s]:3d} t{r[0x4FC+s]:3d}/{r[0x50B+s]:3d} e{r[0x4DE+s]:3d}/{r[0x4ED+s]:3d} a{r[0x3DF+s]:3d} st{r[0x4B1+s]}" if s else "Q -"
    print(f"{n:4d} {ins[n-1]:14s} 0B{r[0x0B]:3d} c{r[0x586]:3d} T x{r[0x3FD]:3d} h{r[0x439]:3d} z{r[0x475]} an{r[0x3B5]:3d} st{r[0x4B1]:3d} f{r[0x4A2]:3d} spd{r[0x565]:3d} vy{((r[0x4C0]<<8|r[0x4CF])+32768)%65536-32768:6d} | {q} rng {r[0x25:0x29].hex()}")
