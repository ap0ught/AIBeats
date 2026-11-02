"""l53b: run stage rows (row 1 = 27,360) from l53a_e4_27359.mst on Mesen; print room/hp/np/item events and the end.
python work/l53b/runst.py stage.txt [pad] [--save f1,f2 tag]"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
a = sys.argv[1:]
SAVE = []
if '--save' in a: i = a.index('--save'); SAVE = [int(x) for x in a[i+1].split(',')]; TAG = a[i+2]; del a[i:i+3]
rows = [row(l.strip()) for l in open(a[0]) if l.strip() and not l.startswith('#')]
pad = int(a[1]) if len(a) > 1 else 0
rows += [()] * pad
fc = core('states/mesen/l53a_e4_27359.mst')
f = 27359; st = []
for k in sorted(SAVE) + [27359 + len(rows)]:
    seg = rows[f - 27359:k - 27359]
    if seg:
        _, rr, _ = fc.step(seg, record='all'); st += rr
    if k in SAVE: fc.save('x'); fc.save_file('x', f'states/mesen/l53b_{TAG}_{k}.mst', k); print('saved', k)
    f = k
fc.close()
prev = None
for i, s in enumerate(st):
    ev = []
    if prev:
        for k in ('hp65', 'np64', 'item', 'room6e', 'e5c'):
            if s[k] != prev[k]: ev.append(f'{k} {prev[k]}->{s[k]}')
    if ev: print(27360 + i, RXY(s), ' '.join(ev))
    prev = s
print('end', 27359 + len(st), RXY(st[-1]), 'hp', st[-1]['hp65'], 'np', st[-1]['np64'])
