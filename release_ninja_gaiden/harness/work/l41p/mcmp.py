"""Compare a Mesen replay (from a .mst) of rows vs a NesHawk RAM dump. python work/l41p/mcmp.py <mst> <rows> <bin>"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
from ng import fastcore as F
from ng.solve import common as C
mst, rf, binf = sys.argv[1:4]
rows = C.rows_of(rf)
d = open(binf, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open(mst, 'rb').read()); fc.load('s')
pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
st = fc.run_batch('s', [pads if len(sys.argv) > 4 else rows], record='all', stops=[(0x6D, 'changed', 0)])[0].states
fc.close()
for i, s in enumerate(st):
    m = d[i*2048:(i+1)*2048]
    nk = (m[0x86], m[0x8A], m[0x65], m[0x64], m[0x6E], m[0xBF])
    mk = (s['x'], s['y'], s['hp'], s['ninpo'], s['room'], s['rng'])
    if nk != mk:
        print('first diff frame', f0 + i + 1, 'mesen', mk, 'neshawk', nk, 'row', rows[i]); break
else:
    print('identical', len(st))
