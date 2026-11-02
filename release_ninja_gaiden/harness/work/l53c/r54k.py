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
fight = (fight + [()] * 900)[:29890 - 29106]
print('len', len(fight), 'last row frame', 29105 + len(fight))
for s in (29905, 29906, 29907):
    rows = fight + [()] * (s - 29890) + [S, S] + [()] * 12
    st = fc.run_batch('r', [rows], record='all')[0].states
    ld = next((29106 + i for i, x in enumerate(st) if x['st6d'] == 16), None)
    print('one run: Start', s, 'load', ld, 'start rows at', 29106 + len(fight) + (s - 29890))
fc.close()
