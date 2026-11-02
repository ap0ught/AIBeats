"""room 33: burn extra ninpo with jump + J&S spins on the run (0 f?). From TAS 28843, np poked; Right from 28867; jumps at j, spins."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
R, AR, BR = ('Right',), ('A', 'Right'), ('B', 'Right')
fc = core_at(28843); fc.poke(0x64, 25); fc.save('b'); fc._ka_slot = 'b'
def mk(jumps):   # jumps: list of (jump frame, [spin offsets])
    rows = [()] * 23 + [R] * (29110 - 28867 + 1)
    for j, sp in jumps:
        rows[j - 28844] = AR; rows[j - 28843] = AR
        for o in sp:
            rows[j + o - 28844] = BR; rows[j + o - 28843] = BR
    return rows
cands = {'none': mk([])}
for k in (1, 2, 3, 4):
    cands[f'{k} jumps x1 spin'] = mk([(28880 + 45 * i, [5]) for i in range(k)])
cands['1 jump x2 spins'] = mk([(28880, [5, 20])])
cands['2 jumps x2 spins'] = mk([(28880, [5, 20]), (28940, [5, 20])])
names = list(cands)
rr = fc.run_batch('b', [cands[n] for n in names], record='all')
for n, r in zip(names, rr):
    st = r.states
    trig = next((28844 + i for i, s in enumerate(st) if s['e5c'] == 4), None)
    print(f'{n:20s} trigger {trig} np {st[-1]["np64"]} item {st[-1]["item"]} legal {legal_ok(cands[n]) or "ok"}')
fc.close()
