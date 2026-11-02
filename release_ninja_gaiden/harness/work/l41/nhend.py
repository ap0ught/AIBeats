"""NesHawk from a saved state: play stage rows to the end, report divergences from Mesen and stage-9 frame.
python work/l41/nhend.py <rows> <state> [--mst ...]"""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
from ng.mode import TICKS
BITS = dict(A=0x80, B=0x40, Select=0x20, Start=0x10, Up=0x08, Down=0x04, Left=0x02, Right=0x01)
def mask(r): return sum(BITS[b] for b in r)
rows = C.rows_of(sys.argv[1]); stn = sys.argv[2]
fc = core(); _, recs, _ = fc.step(rows, record='all'); fc.close()
mend = next((F0 + i + 1 for i, r in enumerate(recs) if r['stage'] == 9), None)
e = C.open_emu('l41_nh.log')
try:
    e.tick(TICKS); st = e.load(stn); f0 = st['frame']
    _, rams = e.run_ram(rows[f0 - F0:])
finally:
    e.close()
nend = None; div = None; confs = []
for j, m in enumerate(rams):
    f = f0 + j + 1; i = f - (F0 + 1); r = recs[i]
    if m[0x6D] == 9 and nend is None: nend = f
    if m[0x2A] != mask(rows[i]) and (i == 0 or rows[i] != rows[i - 1]): confs.append(f)
    if div is None and (X(m), m[0x8A], m[0x65]) != (r['x'] + 256*r['scr_hi'] + r['scr_lo'], r['y'], r['hp']): div = f
print('mesen stage9', mend, 'neshawk stage9', nend, 'first div', div, 'eaten edges', confs[:10])
