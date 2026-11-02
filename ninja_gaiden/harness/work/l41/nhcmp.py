"""NesHawk vs Mesen for stage rows from control: first divergence + eaten edges.
python work/l41/nhcmp.py <rows> [--to f] [--from state]"""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
from ng.mode import TICKS
BITS = dict(A=0x80, B=0x40, Select=0x20, Start=0x10, Up=0x08, Down=0x04, Left=0x02, Right=0x01)
def mask(r): return sum(BITS[b] for b in r)
a = sys.argv[1:]
rows = C.rows_of(a[0]); to = int(a[a.index('--to') + 1]) if '--to' in a else F0 + len(rows)
stn = a[a.index('--from') + 1] if '--from' in a else 'lock_41q_ctlR'
fc = core(); _, recs, _ = fc.step(rows[:to - F0], record='all'); fc.close()
e = C.open_emu('l41_nhc.log')
try:
    e.tick(TICKS); st = e.load(stn); f0 = st['frame']
    _, rams = e.run_ram(rows[f0 - F0:to - F0])
finally:
    e.close()
eaten = []; div = None
for j, m in enumerate(rams):
    f = f0 + j + 1; i = f - F0 - 1; s = recs[i]
    if m[0x2A] != mask(rows[i]) and rows[i] != rows[i - 1]: eaten.append(f)
    if div is None and (X(m), m[0x8A], m[0x65]) != (C.abs_x(s), s['y'], s['hp']):
        div = (f, 'NH', X(m), m[0x8A], m[0x65], 'M', C.abs_x(s), s['y'], s['hp'])
st9 = next((f0 + j + 1 for j, m in enumerate(rams) if m[0x6D] == 9), None)
m9 = next((F0 + i + 1 for i, s in enumerate(recs) if s['stage'] == 9), None)
print('eaten', eaten[:12], 'first div', div, 'NH stage9', st9, 'Mesen stage9', m9)
