"""NesHawk vs Mesen on 4-2 stage rows from lock_42_pre (16,997). python work/l42a/nhchk.py <rows> [to frame] [--save name]
Prints misread frames (NesHawk pad != row, only where the row changes), first X/y/hp divergence vs Mesen, end state."""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
from ng.mode import TICKS
from ng.inputs import to_mask
a = sys.argv[1:]
save = None
if '--save' in a: i = a.index('--save'); save = a[i+1]; del a[i:i+2]
rows = [tuple(r) for r in C.rows_of(a[0])]
to = int(a[1]) if len(a) > 1 else F0 + len(rows)
rows = rows[:to - F0]
fc = core(); _, recs, _ = fc.step(rows, record='all'); fc.close()
e = C.open_emu('l42a_nhchk.log')
try:
    e.tick(TICKS); st = e.load('lock_42_pre'); assert st['frame'] == F0
    _, rams = e.run_ram(rows)
    if save: e.save(save)
finally:
    e.close()
mis = []; div = None
for i, m in enumerate(rams):
    f = F0 + 1 + i
    if m[0x2A] != to_mask(rows[i]) and (i == 0 or rows[i] != rows[i-1]): mis.append(f)
    s = recs[i]
    nv = (X(m), m[0x8A], m[0x65], m[0x64]); mv = (C.abs_x(s), s['y'], s['hp'], s['ninpo'])
    if div is None and nv != mv: div = (f, 'NH', nv, 'M', mv)
m = rams[-1]
print('rows', len(rows), 'to', to, 'misreads', mis[:20], 'first div', div)
print('NH end X', X(m), 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'st', m[0x6D], 'BF', m[0xBF])
