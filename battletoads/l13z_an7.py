"""hit list of a segment from a full RAM dump (l13z_dump.py): time, gap, toad anim/pos, queen pos, freeze, knockback"""
import sys
seg = sys.argv[1]
raw = open(f"logs/fix/l13z_full_{seg}.bin", "rb").read(); N = len(raw) // 0x800
R = lambda n: raw[(n - 1) * 0x800:n * 0x800]
prev_hit = None
for n in range(2, N + 1):
    r, p = R(n), R(n - 1)
    s = next((k for k in range(2, 15) if p[0x3C1 + k] == 0x7E), None)
    if s is None: continue
    killed = r[0x3C1 + s] == 0x46
    if r[0x586] > p[0x586] or (killed and p[0x586] >= 240):
        k = n
        while k < N and R(k + 1)[0x0B] == R(k)[0x0B]: k += 1
        print(f"hit {r[0x586]//12 if not killed else 21:2d} at {n:4d} gap {'' if prev_hit is None else n - prev_hit:>3} toad ({p[0x3FD]:3d},{p[0x439]:3d}) z{p[0x475]} an {p[0x3B5]:2d}->{r[0x3B5]:2d} | queen ({p[0x3FD+s]:3d},{p[0x439+s]:3d}) z{p[0x475+s]} e {p[0x4DE+s]}/{p[0x4ED+s]} | freeze {k-n} kb {r[0x565+s]}")
        prev_hit = n
        if killed: break
