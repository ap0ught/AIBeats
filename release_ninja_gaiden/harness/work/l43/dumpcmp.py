"""print TAS vs r4q (both from TAS state 18960) per frame: python work/l43/dumpcmp.py f1 f2 [step]"""
import sys; sys.path.insert(0, '.')
from ng.solve import hitbox as H
def load(p):
    d = open(p, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); return f0, d[4:]
T0, TD = load('work/l43p/tas43_ram.bin'); R0, RD = load('work/l43p/r4q_ram.bin')
def M(f0, d, f):
    i = f - f0 - 1
    return d[i*2048:(i+1)*2048] if 0 <= i < len(d)//2048 else None
def XY(r):
    s = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]; sc = s*256 + r[0x51]; return sc + r[0x86], r[0x8A], sc
def en(r):
    sc = XY(r)[2]; return ' '.join(f"s{e['slot']}t{e['type']}@{sc+e['x']},{e['y']}" for e in H.enemies(r))
f1, f2 = int(sys.argv[1]), int(sys.argv[2]); st = int(sys.argv[3]) if len(sys.argv) > 3 else 1
for f in range(f1, f2 + 1, st):
    a = M(T0, TD, f); b = M(R0, RD, f)
    s = f'{f}'
    for r, nm in ((a, 'TAS'), (b, 'r4q')):
        if r is None: s += f' | {nm} -'; continue
        X, y, _ = XY(r); s += f' | {nm} rm{r[0x6E]} X{X} y{y} hp{r[0x65]} np{r[0x64]} pad{r[0x2A]:02x} ' + (en(r) if len(sys.argv) > 4 else '')
    print(s)
