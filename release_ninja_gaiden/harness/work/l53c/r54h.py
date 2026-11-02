"""l53c: 5-4 fight vs $BF (poked at row 29105 on our line) and vs RNG-ish bytes: kill frame and 6-1 load with Start 29907-08."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
FLD['bh'] = 0x66
L, R, S = ('Left',), ('Right',), ('Start',)
fc = core_at(28843)
base = [()] * 23 + [R] * (29099 - 28867 + 1) + [()] * 4 + [S, S]
fc.step(base, record='last'); fc.save('r'); fc._ka_slot = 'r'
b13 = [row(l.strip()) for l in open('logs/a56_5-4_b13.inputs.txt') if not l.startswith('#')]
b13 = [tuple(sorted(x for x in rr if x != 'Start')) for rr in b13]
rows = [()] * (29258 - 29105) + [L] + b13[:600]
rows = (rows + [()] * 900)[:29920 - 29105]
rows[29907 - 29106] = S; rows[29908 - 29106] = S
res = {}
for v0 in range(0, 256, 16):
    for v in range(v0, v0 + 16):
        fc.load('r'); fc.poke(0xBF, v); fc.save(f'p{v}')
    rr = [fc.run_batch(f'p{v}', [rows], record='all')[0] for v in range(v0, v0 + 16)]
    for v, r in zip(range(v0, v0 + 16), rr):
        st = r.states
        kill = next((29106 + i for i, s in enumerate(st) if 29106 + i > 29270 and s['bh'] == 0 and s['room6e'] == 34), None)
        ld = next((29106 + i for i, s in enumerate(st) if s['st6d'] == 16), None)
        hpmin = min(s['hp65'] for s in st if s['room6e'] == 34)
        res[v] = (kill, ld, hpmin)
    for v in range(v0, v0 + 16): fc.drop(f'p{v}')
from collections import Counter
print(Counter(res.values()))
print({v: res[v] for v in res if res[v] != (29313, 29910, 16)})
fc.close()
