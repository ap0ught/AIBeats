"""6-1 +10 X 1024 y 160 lantern: replace the TAS jump at 30690 by an earlier jump J (A+Left 2 f) + air slash B+Left at J+k (2 f);
compare with the base J&S rows (Mesen, TAS state 30650) to 31487: first position difference, np at 31487."""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
base = [row(l.strip()) for l in open('work/l61p/js_30063_32595.txt') if l.strip() and not l.startswith('#')]
F0, F1 = 30650, 31487
def sl(r): return r[F0 + 1 - 30063: F1 + 1 - 30063]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
b0 = fc.run_batch('b', [sl(base)], record='all')[0].states
cands = {}
for J in range(30670, 30691, 2):
    for k in range(4, 20, 2):
        r = list(base)
        for f in (30690, 30691): r[f - 30063] = ('Left',)
        for f in (J, J + 1): r[f - 30063] = ('A', 'Left')
        for f in (J + k, J + k + 1): r[f - 30063] = ('B', 'Left')
        cands[(J, k)] = sl(r)
names = list(cands)
for i in range(0, len(names), 32):
    rr = fc.run_batch('b', [cands[n] for n in names[i:i+32]], record='all')
    for n, r in zip(names[i:i+32], rr):
        st = r.states
        d = next((F0 + 1 + j for j, (s, t) in enumerate(zip(st, b0)) if RXY(s) != RXY(t)), None)
        last = next((F0 + 1 + j for j in range(len(st) - 1, -1, -1) if RXY(st[j]) != RXY(b0[j])), None)
        print(n, 'np', st[-1]['np64'], 'hp', st[-1]['hp65'], 'first diff', d, 'last diff', last, 'end', RXY(st[-1]), 'base', RXY(b0[-1]), flush=True)
fc.close()
