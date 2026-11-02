"""Cyclic legal climb patterns (Mesen): every cyclic pattern of length L (5..LMAX) over {A} x {Left, Right, -} where each button,
cyclically, is held >= 2 and released >= 2 (so period >= 5 is automatic) is repeated k times after a prefix, then a tail.
python work/l63p/cyc.py F0 'goal' [--pre 'Row*n,...'] [--lmax 6] [--kmax 12] [--tail Left] [--n 140] [--top 12]"""
import sys, itertools
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
PRE = opt('--pre', ''); LMAX = opt('--lmax', 6); KMAX = opt('--kmax', 12); TAIL = opt('--tail', 'Left'); N = opt('--n', 140)
TOP = opt('--top', 12); BOTH = opt('--both', 0); KMIN = opt('--kmin', 1); BF = opt('--bf', -1); KS = opt('--ks', '')
F0 = int(a[0]); G = compile(a[1], 'g', 'eval')
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
pres = [rr(p) for p in PRE.split('|')] if PRE else [[]]
def cyc_ok(seq, b):
    on = [b in s for s in seq]
    if all(on) or not any(on): return not all(on)
    L = len(on); i0 = on.index(False)
    runs = []; cur = on[i0]; n = 0
    for k in range(L):
        v = on[(i0 + k) % L]
        if v == cur: n += 1
        else: runs.append((cur, n)); cur = v; n = 1
    runs.append((cur, n))
    return all(n >= 2 for _, n in runs)
OPTS = [(), ('Left',), ('Right',), ('A',), ('A', 'Left'), ('A', 'Right')]
pats = set()
for L in range(5, LMAX + 1):
    for seq in itertools.product(OPTS, repeat=L):
        if not any('A' in s for s in seq): continue
        if BOTH and not (('A', 'Left') in seq and ('A', 'Right') in seq): continue
        if all(cyc_ok(seq, b) for b in ('A', 'Left', 'Right')):
            # canonical rotation
            rots = [seq[i:] + seq[:i] for i in range(L)]
            pats.add(min(rots))
pats = sorted(pats)
print('patterns', len(pats), flush=True)
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
fc = core_at(F0)
if BF >= 0: fc.poke(0xBF, BF)
fc.save('b'); fc._ka_slot = 'b'
tl = row(TAIL)
cands = {}
for pi, pre in enumerate(pres):
    for p in pats:
        L = len(p)
        for rot in range(L):
            q = p[rot:] + p[:rot]
            for k in ([int(x) for x in KS.split(',')] if KS else range(KMIN, KMAX + 1)):
                body = (pre + list(q) * k + [tl] * N)[:N]
                cands[(pi, q, k)] = body
ok = {k: v for k, v in cands.items() if not legal_ok(v, hist)}
print('cands', len(cands), 'legal', len(ok), flush=True)
names = list(ok); res = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [ok[n] for n in names[i:i+64]], record='all')
    for n, r in zip(names[i:i+64], rs):
        for k, s in enumerate(r.states):
            X, y = RXY(s)
            if eval(G, dict(X=X, y=y, s=s, hp=s['hp65'], rm=s['room6e'], it=s['item'], np=s['np64'])):
                res.append((F0 + 1 + k, s['hp65'], n[0], ' '.join(P(x) for x in n[1]), n[2])); break
res.sort()
for x in res[:TOP]: print(x, flush=True)
if not res: print('no goal')
fc.close()
