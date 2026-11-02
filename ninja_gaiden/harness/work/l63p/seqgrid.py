"""Mesen: explicit candidate row lists from TAS state F0 (agent l63p). Candidates from a python generator expression in a file
(--gen file.py defines CANDS = {name: [rows]}); goal on X,y,s,hp,rm,np,it. python work/l63p/seqgrid.py F0 'goal' --gen f.py [--top 15] [--poke a=v,..]"""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
GEN = opt('--gen', ''); TOP = opt('--top', 15); PK = opt('--poke', ''); HISTF = opt('--hist', '')
F0 = int(a[0]); G = compile(a[1], 'g', 'eval')
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
ns = {'rr': rr, 'row': row}
exec(open(GEN).read(), ns)
CANDS = ns['CANDS']
if HISTF: hist = [row(l.strip()) for l in open(HISTF) if not l.startswith('#')][-150:]
else: hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
ok = {k: v for k, v in CANDS.items() if not legal_ok(v, hist)}
print('cands', len(CANDS), 'legal', len(ok), flush=True)
fc = core_at(F0)
for kv in [p for p in PK.split(',') if p]:
    k_, v_ = kv.split('='); fc.poke(int(k_, 0), int(v_, 0))
fc.save('b'); fc._ka_slot = 'b'
names = list(ok); res = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [ok[n] for n in names[i:i+64]], record='all')
    for n, r in zip(names[i:i+64], rs):
        for k, s in enumerate(r.states):
            X, y = RXY(s)
            if eval(G, dict(X=X, y=y, s=s, hp=s['hp65'], rm=s['room6e'], it=s['item'], np=s['np64'])):
                res.append((F0 + 1 + k, s['hp65'], s['np64'], X, y, n)); break
res.sort()
for x in res[:TOP]: print(x, flush=True)
if not res: print('no goal')
print('done', len(res), 'of', len(ok))
fc.close()
