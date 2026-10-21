"""hit statistics over all dumped segments: attack anim, freeze, knockback, queen height, gap to the next hit"""
import sys, glob, os, collections
st = collections.defaultdict(list)
for fn in sorted(glob.glob("logs/fix/l13z_ts_*.bin")):
    seg = os.path.basename(fn)[8:-4]
    raw = open(fn, "rb").read(); N = len(raw) // 0x800
    R = lambda n: raw[(n - 1) * 0x800:n * 0x800]
    hits = []
    for n in range(2, N + 1):
        r, p = R(n), R(n - 1)
        s = next((k for k in range(2, 15) if p[0x3C1 + k] == 0x7E), None)
        if s is None: continue
        killed = r[0x3C1 + s] == 0x46
        if r[0x586] > p[0x586] or (killed and p[0x586] >= 240):
            k = n
            while k < N and R(k + 1)[0x0B] == R(k)[0x0B]: k += 1
            hits.append(dict(n=n, an=r[0x3B5], tz=p[0x475], th=p[0x439], tx=p[0x3FD], qx=p[0x3FD + s], qh=p[0x439 + s], qz=p[0x475 + s], fr=k - n,
                             kb=r[0x565 + s], kd=r[0x556 + s], hov=(p[0x4C0+s], p[0x4CF+s], p[0x4ED+s]), kill=killed))
            if killed: break
    if len(sys.argv) > 1 and seg in sys.argv[1:]:
        for i, h in enumerate(hits):
            print(seg, i + 1, h, "gap", hits[i + 1]["n"] - h["n"] if i + 1 < len(hits) else None)
    for i, h in enumerate(hits[:-1]):
        st[(h["an"], h["fr"], h["kb"])].append((hits[i + 1]["n"] - h["n"], h["qh"], hits[i+1]["an"]))
for k in sorted(st):
    v = st[k]
    print(k, "n", len(v), "gaps", sorted(g for g, _, _ in v))
