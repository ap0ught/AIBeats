"""Poke ninpo +5 at frame P on a rows file (stage rows), play to END with optional --set edits; list spins/hits/ninpo
changes and TAS-distance. python work/l42a/np5.py <rows> P END [--set row=SPEC,..] [--add 5]"""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
a = sys.argv[1:]; sets = {}; add = 5
if '--set' in a:
    i = a.index('--set')
    for q in a[i+1].split(','):
        k, v = q.split('='); sets[int(k)] = row(v)
    del a[i:i+2]
if '--add' in a: i = a.index('--add'); add = int(a[i+1]); del a[i:i+2]
rows = [tuple(r) for r in C.rows_of(a[0])]; P, END = int(a[1]), int(a[2])
for k, v in sets.items(): rows[k - 1] = v
fc = core(); fc.step(rows[:P - F0], record='last'); r0 = fc.ram(); fc.poke(0x64, r0[0x64] + add)
_, st, _ = fc.step(rows[P - F0:END - F0], record='all'); fc.close()
prev = None
for i, s in enumerate(st):
    f = P + 1 + i; t = TT[f - 316]
    key = (s['hp'], s['ninpo'], s['item'])
    if key != prev or f % 50 == 0: print(f, 'row', f - F0, '+'.join(rows[f - F0 - 1]), 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'it', s['item'], '| TAS d', C.abs_x(t) - C.abs_x(s))
    prev = key
