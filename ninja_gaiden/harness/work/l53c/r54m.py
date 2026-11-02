"""Does a Start during the 5-4 tally do anything? chain c53_tas3 (TAS state 28417 + np 20/hp 3): kill 29371, standard Start 29965-66."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
rows = [row(l.strip()) for l in open('work/l53c/c53_tas3.txt') if l.strip() and not l.startswith('#')]
K = 29371
fc = core_at(28417); fc.poke(0x64, 20); fc.poke(0x65, 3)
fc.step(rows[:K - 28417], record='last'); fc.save('k'); fc._ka_slot = 'k'
tail = rows[K - 28417:] + [()] * 20
res = []
cands = []
for s in range(K + 1, K + 594, 7):
    rr = list(tail); i = s - K - 1
    if rr[i] or rr[i + 1]: continue
    rr[i] = ('Start',); rr[i + 1] = ('Start',)
    cands.append((s, rr))
for j in range(0, len(cands), 16):
    ch = cands[j:j+16]
    out = fc.run_batch('k', [c[1] for c in ch], record='all')
    for (s, _), o in zip(ch, out):
        ld = next((K + 1 + i for i, x in enumerate(o.states) if x['st6d'] == 16), None)
        res.append((s, ld))
from collections import Counter
print(Counter(ld for s, ld in res)); print([q for q in res if q[1] != 29968][:20])
fc.close()
