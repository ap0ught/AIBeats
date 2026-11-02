"""Evaluate climb goal files: python work/l51b/evcl.py <glob of goal files> [--end 23670]
Each file = rows from 23,589 (w2a_23588 base). Lag = goal frame - 23,133; then legal TAS rows (tosser-3 fix) to TAS END."""
import sys, glob
sys.path.insert(0, 'work/l51b')
from lb import *
a = sys.argv[1:]; END = 23670
if '--end' in a: i = a.index('--end'); END = int(a[i+1]); del a[i:i+2]
hist = [tuple(sorted(r)) for r in C.rows_of('work/l51a/h_w2a_23588.inputs.txt')]
fc = core('states/mesen/l51a_w2a_23588.mst'); fc.save('b'); fc._ka_slot = 'b'
mods = {23279: {'A', 'Right'}, 23280: {'A', 'Right'}, 23544: {'Right'}, 23545: {'Right'}, 23546: {'A', 'Right'}, 23547: {'A', 'Right'}}
out = []
for fn in sorted(glob.glob(a[0])):
    cl = [tuple(sorted(r)) for r in C.rows_of(fn)]
    g = 23588 + len(cl)
    for L in (g - 23133, g - 23133 + 1):
        rows = cl + enforce(tasleg(g + 1 - L, END, mods), hist + cl)
        if legal_ok(rows, hist): continue
        st = fc.run_batch('b', [rows], record='all')[0].states
        hits = trackhits(st, 23589)
        X, y = RXY(st[-1]); TX, TY = tas_xy(END)
        r = st[-1]; scr = X - r['x86']
        birds = [(scr + r[f'ex{j}'], r[f'ey{j}']) for j in range(8) if r['eact'] >> j & 1 and r[f't{j}'] == 11]
        dead = any(s['y8a'] >= 232 for s in st)
        out.append((dead, len(hits) > 1, END + L if (X, y) == (TX, TY) else 99999, fn.split('_')[-1], L, hits, (X, y), birds))
out.sort(key=lambda q: q[:3])
for o in out[:40]: print(o, flush=True)
fc.close()
