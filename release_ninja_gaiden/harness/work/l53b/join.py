"""l53b: run rows from a state and report the first join with the TAS (same Ryu key) within TAS frames TJ0..TJ1.
python work/l53b/join.py <mst|tasF> F0 rows.txt TJ0 TJ1 [--poke 65=3] [--n N]"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
a = sys.argv[1:]
POKE = ''; N = 0
if '--poke' in a: i = a.index('--poke'); POKE = a[i+1]; del a[i:i+2]
if '--n' in a: i = a.index('--n'); N = int(a[i+1]); del a[i:i+2]
src, F0, rf, TJ0, TJ1 = a[0], int(a[1]), a[2], int(a[3]), int(a[4])
rows = [row(l.strip()) for l in open(rf) if l.strip() and not l.startswith('#')]
if N: rows = rows[:N]
KEYS = (0x86, 0x85, 0x8A, 0x89, 0x87, 0x84, 0x8C, 0x51, 0x52)
FN = {0x86: 'x86', 0x85: 'xsub', 0x8A: 'y8a', 0x89: 'vy', 0x87: 'vy_sub', 0x84: 'rf84', 0x8C: 'coll', 0x51: 'scr_lo', 0x52: 'scr_hi'}
TK = {}
for g in range(TJ0, TJ1 + 1): TK.setdefault(tuple(TM(g)[k] for k in KEYS), g)
fc = core(src) if src.endswith('.mst') else core_at(F0)
for p in [q for q in POKE.split(',') if q]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('b'); fc._ka_slot = 'b'
st = fc.run_batch('b', [rows], record='all')[0].states
fc.close()
js = []
for t, s in enumerate(st):
    key = tuple(s[FN[q]] for q in KEYS)
    if key in TK: js.append((F0 + 1 + t, TK[key], F0 + 1 + t - TK[key]))
print('joins (our frame, TAS frame, lag):', js[:12])
s = st[-1]; print('end', F0 + len(st), RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'rm', s['room6e'])
