import sys
seg, lo, hi, st = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
raw = open(f"logs/fix/l13z_ts_{seg}.bin", "rb").read()
R = lambda n: raw[(n - 1) * 0x800:n * 0x800]
for n in range(lo, min(hi, len(raw) // 0x800 + 1), st):
    r = R(n)
    o = " ".join(f"[{s}:{r[0x3C1+s]:02x} x{r[0x3FD+s]+256*r[0x3EE+s]} h{r[0x439+s]} hh{r[0x42A+s]} z{r[0x475+s]} hp{r[0x51A+s]} an{r[0x3B5+s]} st{r[0x4B1+s]}]" for s in range(15) if r[0x3C1+s])
    print(n, "0B", r[0x0B], "0C", r[0x0C], "586", r[0x586], "rng", r[0x25:0x29].hex(), o)
