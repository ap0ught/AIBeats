"""Lines = k blank rows + a base line (default a56 r2d5); for each k the kill row / hp for every bf (Mesen; the state after row
120 is bf-independent (the first fireball spawns on row 121), so it is computed once per k and $BF is poked there).
python work/l65/lead.py <k list> [--base file] [--tag r2d5] -> work/l65/lines/<tag>_k<k>.txt, results appended to work/l65/lead.res.tsv"""
import sys, os
sys.path.insert(0, 'work/l65')
from lib65 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
BASE = opt('--base', 'work/l63p/dm_r2d5_kill.txt'); TAG = opt('--tag', 'r2d5'); VS = opt('--vals', '0-255')
ks = []
for p in a[0].split(','):
    if '-' in p: x, y = map(int, p.split('-')); ks += list(range(x, y + 1))
    else: ks.append(int(p))
vals = []
for p in VS.split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    else: vals.append(int(p))
base = rows_of(BASE)
os.makedirs('work/l65/lines', exist_ok=True)
fc = core65()
out = open('work/l65/lead.res.tsv', 'a', newline='\n')
from ng.fastcore import free_ram_gb
for k in ks:
    if free_ram_gb() < 2.0:
        print('free RAM < 2.0 GB: stopping before k', k, flush=True); break
    rows = [()] * k + base
    fn = f'work/l65/lines/{TAG}_k{k}.txt'
    with open(fn, 'w', newline='\n') as f:
        f.write(f'# l65: {k} blank rows + {BASE} (row 1 = 6-5 control row)\n')
        for r in rows: f.write(('+'.join(r) if r else '') + '\n')
    fc.load('c0'); fc.poke(0xBF, 0); fc.step(rows[:120]); fc.save('p120')
    n = 0
    for v in vals:
        fc.load('p120'); fc.poke(0xBF, (v + 120) % 256); fc.save('q')
        o = outcome(fc.run_batch('q', [rows[120:] + [()] * 20], record='last', stops=STOPS)[0])
        if o[0]:
            out.write(f'{v}\t{fn}\t{o[0] + 120}\t{o[1]}\n'); n += 1
    out.flush()
    print('k', k, 'kills', n, flush=True)
fc.close()
