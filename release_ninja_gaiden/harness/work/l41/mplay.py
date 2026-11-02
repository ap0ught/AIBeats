"""Mesen: play stage rows from l41_ctl, report room changes, hits, ninpo/item changes, end.
python work/l41/mplay.py <rows> [mst] [--n N]"""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
BITS = dict(A=0x80, B=0x40, Select=0x20, Start=0x10, Up=0x08, Down=0x04, Left=0x02, Right=0x01)
a = sys.argv[1:]
rows = C.rows_of(a[0]); mst = a[1] if len(a) > 1 and not a[1].startswith('--') else MST
fc = core(mst)
_, recs, _ = fc.step(rows, record='all'); fc.close()
prev = None; nconf = 0
for i, r in enumerate(recs):
    f = F0 + i + 1
    k = (r['stage'], r['room'], r['hp'], r['ninpo'], r['item'])
    if prev is None or k != prev:
        print(f, 'stage', r['stage'], 'room', r['room'], 'X', r['x'] + 256*r['scr_hi'] + r['scr_lo'], 'y', r['y'], 'hp', r['hp'], 'np', r['ninpo'], 'item', r['item'], 'gm', r['gm'])
    prev = k
    if r['pad2a'] != sum(BITS[b] for b in rows[i]): nconf += 1
print('end frame', F0 + len(recs), 'conflicts(mesen)', nconf)
