"""first frame each dump reaches world X thresholds: python work/l42p/xcmp.py a.bin b.bin ..."""
import sys
def load(fn):
    d = open(fn, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
    out = []
    for i in range(len(d)//2048):
        m = d[i*2048:(i+1)*2048]
        if m[0x6D] != 9: break
        out.append((f0 + 1 + i, m[0x52]*256 + m[0x51] + m[0x86], m[0x8A], m[0x65]))
    return out
L = [load(f) for f in sys.argv[1:]]
print('X     ' + '  '.join(f'{f[-14:]:>14s}' for f in sys.argv[1:]))
for X in list(range(100, 3001, 100)) + [3035]:
    fs = []
    for l in L:
        fs.append(next((f for f, x, y, h in l if x >= X), None))
    print(f'{X:5d} ' + '  '.join(f'{v!s:>8s} {"" if v is None or fs[0] is None else v - fs[0]:>5}' for v in fs))
for l in L: print('last', l[-1])
