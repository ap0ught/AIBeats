"""5-1 -> 5-2 transition on Mesen run_batch (TAS state 24,147): trigger, load, control; Start presses; Left early."""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
fc = core(tas_mst(24147)); fc.save('b'); fc._ka_slot = 'b'
N = 300   # rows 24148 .. 24447
def mk(ov):
    r = [()] * N
    for f, v in ov.items(): r[f - 24148] = row(v)
    return r
def lefts(f0): return {f: 'Left' for f in range(f0, 24148 + N)}
cands = {'TAS (Left from 24427)': lefts(24427), 'Left from 24426': lefts(24426), 'Left from 24400': lefts(24400),
         'Left from 24300': lefts(24300), 'Left from 24428': lefts(24428)}
for s in (24148, 24149, 24160, 24200, 24276, 24277, 24300, 24350, 24420):
    d = lefts(24427); d[s] = 'Start'; d[s + 1] = 'Start'; cands[f'Start {s}-{s+1} + Left 24427'] = d
rr = fc.run_batch('b', [mk(v) for v in cands.values()], record='all')
for nm, r in zip(cands, rr):
    st = r.states; ld = next((24148 + i for i, s in enumerate(st) if s['st6d'] == 13), None)
    mv = next((24148 + i for i, s in enumerate(st) if s['st6d'] == 13 and s['x86'] != st[i-1]['x86']), None)
    tr = next((24148 + i for i, s in enumerate(st) if s['e5c'] == 0), None)
    print(f'{nm:32s} 5C=0 at {tr}  stage13 at {ld}  first x move {mv}  BF@24427 {st[24427-24148]["bf"]}')
fc.close()
