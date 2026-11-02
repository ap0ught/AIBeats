"""first frame each 4-3 dump reaches (room, X >= thr): python work/l43p/xcmp.py a.bin b.bin"""
import sys
def load(fn):
    d = open(fn, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
    out = []; prm = None; ent = 0
    for i in range(len(d)//2048):
        m = d[i*2048:(i+1)*2048]
        hi = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]
        if m[0x6E] != prm: prm = m[0x6E]; ent = f0 + 1 + i
        if f0 + 1 + i < ent + 25: continue
        out.append((f0 + 1 + i, m[0x6E], hi*256 + m[0x51] + m[0x86], m[0x8A], m[0x65], m[0x6D]))
    return out
L = [load(f) for f in sys.argv[1:]]
for rm, xs in ((18, range(100, 950, 50)), (19, list(range(150, 1200, 50)) + [1179]), (20, range(150, 760, 50))):
    for X in xs:
        fs = [next((f for f, r, x, y, h, st in l if r == rm and x >= X and st == 10), None) for l in L]
        print(f'rm {rm} X {X:5d} ' + '  '.join(f'{v!s:>6s} {"" if v is None or fs[0] is None else v - fs[0]:>5}' for v in fs))
for l in L:
    for rm in (18, 19, 20, 21):
        print('enter', rm, next((f for f, r, *_ in l if r == rm), None))
