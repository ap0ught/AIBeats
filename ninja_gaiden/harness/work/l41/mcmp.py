"""Mesen replay of a stage-rows file (rows after control) vs a NesHawk dump: python work/l41/mcmp.py <rows> <nh.bin> [mst]"""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
rows = C.rows_of(sys.argv[1]); nb = sys.argv[2]; mst = sys.argv[3] if len(sys.argv) > 3 else MST
d = open(nb, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
N = [d[i*2048:(i+1)*2048] for i in range(len(d)//2048)]
fc = core(mst)
_, recs, _ = fc.step(rows, record='all'); fc.close()
n = 0
for i, r in enumerate(recs):
    if i >= len(N): break
    m = N[i]
    a = (r['room'], r['x'] + 256*r['scr_hi'] + r['scr_lo'], r['y'], r['hp'], r['pad2a'])
    b = (m[0x6E], X(m), m[0x8A], m[0x65], m[0x2A])
    if a != b:
        print('frame', f0 + i + 1, 'row', rows[i], 'mesen', a, 'neshawk', b); n += 1
        if n > 12: break
print('rows', len(rows), 'recs', len(recs))
