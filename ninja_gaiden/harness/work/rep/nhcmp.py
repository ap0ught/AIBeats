"""NesHawk trace (tools/trace_run.py) vs Mesen replay of the same power-on rows: first differing frame + conflicts.
    python work/rep/nhcmp.py <power-on rows> <tag>"""
import csv, subprocess, sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng import fastcore as F
rows = C.rows_of(sys.argv[1]); tag = sys.argv[2]
subprocess.run([sys.executable, 'tools/trace_run.py', sys.argv[1], tag], check=True, stdout=subprocess.DEVNULL)
T = list(csv.DictReader(open(f'logs/{tag}.trace.csv')))
pads = F.neshawk_pads(f'logs/{tag}.trace.csv', len(rows)); m = F.masks_of(rows)
print('NesHawk conflicts:', [i + 1 for i, (a, b) in enumerate(zip(pads, m)) if a != b])
fc = F.FastCore(boot_rows=[]); _, recs, _ = fc.step(rows, record='all'); fc.close()
first = None
for s, t in list(zip(recs, T))[174:]:
    tt = {k: int(v) for k, v in t.items() if v.lstrip('-').isdigit()}
    if (C.abs_x(s), s['y'], s['hp'], s['ninpo'], s['stage']) != (C.abs_x(tt), tt['y'], tt['hp'], tt['ninpo'], tt['stage']):
        first = (t['frame'], C.abs_x(s), s['y'], s['hp'], C.abs_x(tt), tt['y'], tt['hp']); break
print('first Mesen/NesHawk difference:', first)
t = {k: int(v) for k, v in T[-1].items() if v.lstrip('-').isdigit()}
print('NesHawk end: frame', t['frame'], 'stage', t['stage'], 'X', C.abs_x(t), 'y', t['y'], 'hp', t['hp'], 'np', t['ninpo'], 'item', t['item'])
