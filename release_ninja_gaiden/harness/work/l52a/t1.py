"""physics test: legal wall-jump-off at y~72 then Left, from TAS states."""
import sys; sys.path.insert(0, 'work/l52p')
from lib import *
F0 = int(sys.argv[1])
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
AR, L, Z, R = ('A','Right'), ('Left',), (), ('Right',)
tests = {}
for k in range(0, 6):
    tests[f'L{k} AR2 L'] = [L]*k + [AR, AR] + [L]*40
    tests[f'Z{k} AR2 L'] = [Z]*k + [AR, AR] + [L]*40
names = list(tests)
rs = fc.run_batch('b', [tests[n] for n in names], record='all')
for n, r in zip(names, rs):
    out = []
    for k, s in enumerate(r.states):
        X, y = RXY(s)
        out.append(f"{X},{y},{s['room6e']},{fc_t if False else ''}")
        if s['room6e'] != 23: break
    s = r.states[-1]
    print(n, 'rm', s['room6e'], 'n', len(out), ' '.join(o.rstrip(',') for o in out[:45]))
fc.close()
