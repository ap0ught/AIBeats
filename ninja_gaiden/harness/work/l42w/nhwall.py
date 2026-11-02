"""NesHawk vs Mesen on wall rows: python -u work/l42w/nhwall.py <neshawk state> <mesen mst> <rows file> [--save name]
rows = the rows played from the state. Prints the first (X, y, hp) divergence, misread pads (NesHawk $2A != row),
and the trigger frame ($5C 2 -> 0) on both."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/l42w')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import to_mask
from wlib import FL, X
a = sys.argv[1:]
save = None
if '--save' in a:
    i = a.index('--save'); save = a[i + 1]; del a[i:i + 2]
nhs, mst, rf = a
rows = [tuple(r) for r in C.rows_of(rf)]
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
mres = fc.run_batch('s', [rows], record='all')[0].states
fc.close()
e = C.open_emu('l42w_nhwall.log')
try:
    e.tick(TICKS); st = e.load(nhs); f0 = st['frame']
    _, rams = e.run_ram(rows)
    if save: e.save(save)
finally:
    e.close()
div = None; mis = []; tn = tm = None
for i, (m, s) in enumerate(zip(rams, mres)):
    f = f0 + 1 + i
    if m[0x2A] != to_mask(rows[i]): mis.append(f)
    nv = (m[0x52] * 256 + m[0x51] + m[0x86], m[0x8A], m[0x65])
    mv = (X(s), s['y'], s['hp'])
    if div is None and nv != mv: div = (f, 'NH', nv, 'Mesen', mv)
    if tn is None and m[0x5C] == 0: tn = f
    if tm is None and s['c5'] == 0: tm = f
m = rams[-1]
print('NesHawk', nhs, 'from', f0, 'rows', len(rows), '| trigger NH', tn, 'Mesen', tm, '| misreads', mis[:12], '| first div', div)
print('end NH X', m[0x52] * 256 + m[0x51] + m[0x86], 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'item', m[0xC9], 'BF', m[0xBF])
