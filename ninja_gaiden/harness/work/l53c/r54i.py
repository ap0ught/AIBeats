"""l53c: 6-1 load vs $62 at the 5-3 trigger (poked after row 29105 on our line); per value the earliest Start (2 f) that loads."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
L, R, S = ('Left',), ('Right',), ('Start',)
fc = core_at(28843)
base = [()] * 23 + [R] * (29099 - 28867 + 1) + [()] * 4 + [S, S]
fc.step(base, record='last'); fc.save('r'); fc._ka_slot = 'r'
b13 = [row(l.strip()) for l in open('logs/a56_5-4_b13.inputs.txt') if not l.startswith('#')]
b13 = [tuple(sorted(x for x in rr if x != 'Start')) for rr in b13]
fight = [()] * (29258 - 29105) + [L] + b13[:600]
fight = (fight + [()] * 900)[:29890 - 29105]
fc.load('r'); fc.step(fight, record='last'); fc.save('k')   # after row 29889 with $62 as on our line
for v in list(range(48, 62)):
    fc.load('r'); fc.poke(0x62, v); fc.step(fight, record='last'); fc.save(f'k{v}')
    cands = [[()] * (s - 29890) + [S, S] + [()] * 12 for s in range(29890, 29925)]
    rr = fc.run_batch(f'k{v}', cands, record='all')
    out = []
    for s, r in zip(range(29890, 29925), rr):
        ld = next((s0 for s0 in [None]), None)
        for i, st in enumerate(r.states):
            if st['st6d'] == 16: ld = 29890 + i; break
        if ld: out.append((s, ld)); break
    print('$62 =', v, 'earliest Start, load:', out, flush=True)
fc.close()
