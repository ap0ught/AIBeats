"""enemy divergence timeline: python work/l42p/endiff.py <dump.bin> <state.mst> <bf> [from] [to]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
dump, mst, bf = sys.argv[1], sys.argv[2], int(sys.argv[3])
fa = int(sys.argv[4]) if len(sys.argv) > 4 else 0; fb = int(sys.argv[5]) if len(sys.argv) > 5 else 99999
d = open(dump, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
FL = {'x': 0x86, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'hp': 0x65, 'np': 0x64, 'en': 0x73, 'BF': 0xBF}
for j in range(8):
    FL[f't{j}'] = 0x400 + j; FL[f's{j}'] = 0x410 + j; FL[f'ex{j}'] = 0x460 + j; FL[f'ey{j}'] = 0x480 + j; FL[f'z{j}'] = 0x418 + j
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
def run(b):
    fc.load('s')
    if b is not None: fc.poke(0xBF, b)
    fc.save('p'); return fc.run_batch('p', [pads], record='all', stops=[(0x6D, 'changed', 0)])[0].states
def ek(s, j):
    if not (s['en'] >> j & 1): return None
    return (s[f't{j}'], s[f's{j}'], s[f'ex{j}'] + s['sl'] + 256*s['sh'], s[f'ey{j}'])
A = run(None); B = run(bf)
last = {}
for i, (s, t) in enumerate(zip(A, B)):
    f = f0 + 1 + i
    if f < fa or f > fb: continue
    X = s['sh']*256 + s['sl'] + s['x']; X2 = t['sh']*256 + t['sl'] + t['x']
    dd = [(j, ek(s, j), ek(t, j)) for j in range(8) if ek(s, j) != ek(t, j)]
    key = tuple((j, (a[0] if a else None), (b[0] if b else None)) for j, a, b in dd)
    if key != last.get('k') or (X, s['y'], s['hp']) != (X2, t['y'], t['hp']):
        print(f, 'ryu', (X, s['y'], s['hp']), (X2, t['y'], t['hp']), 'diff', dd)
    last['k'] = key
fc.close()
