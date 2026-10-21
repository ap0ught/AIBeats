"""per hit: toad anim, queen pos/state before, freeze length (frames $0B stalls), queen trajectory after"""
import sys
seg = sys.argv[1]
raw = open(f"logs/fix/l13z_ts_{seg}.bin", "rb").read()
N = len(raw) // 0x800
R = lambda n: raw[(n - 1) * 0x800:n * 0x800]
def q(r):
    for s in range(2, 15):
        if r[0x3C1 + s] in (0x7E, 0x46):
            return s
    return None
prevc = 0
lagtot = 0
for n in range(2, N + 1):
    r, p = R(n), R(n - 1)
    if r[0x0B] == p[0x0B]:
        lagtot += 1
    if r[0x586] > p[0x586] or (r[0x586] == 240 and q(r) and r[0x3C1 + q(r)] == 0x46 and p[0x3C1 + q(r)] == 0x7E):
        s = q(r)
        k = n
        while k < N and R(k + 1)[0x0B] == R(k)[0x0B]:
            k += 1
        # queen vertical speed bytes guess: print several per-slot tables before the hit
        print(f"hit at {n}: ctr {r[0x586]} toad x{p[0x3FD]} h{p[0x439]} an{p[0x3B5]}->{r[0x3B5]} z{p[0x475]} | queen x{p[0x3FD+s]} h{p[0x439+s]} z{p[0x475+s]} an{p[0x3B5+s]} st{p[0x4B1+s]} -> x{r[0x3FD+s]} h{r[0x439+s]} | freeze {k-n} frames")
print("total frames", N, "frames where $0B did not advance", lagtot)
