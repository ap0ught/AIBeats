"""Macro enumerator (Mesen): pre x cycle^k x mid x tail, every combo; earliest frame meeting the goal.
python -u work/l52b/menum.py F0 'goal' --pre 'spec|spec' --cyc 'spec|spec' --kmin 0 --kmax 12 --mid 'spec|spec' --tail 'spec|spec'
  [--n 150] [--state f.mst] [--hist rowsfile] [--top 20] [--poke a=v] [--save tag]
spec = 'Row*n,Row*n' ('' allowed). The tail's last row is repeated to fill n rows. Only legal candidates are run.
--save tag: writes work/l52b/e_<tag>.txt with the best candidate's rows up to the goal frame."""
import sys, itertools
sys.path.insert(0, 'work/l52p')
from lib import *
if os.environ.get('MINGB'):
    import fcka as _fk; d = list(_fk._init.__defaults__); d[-1] = float(os.environ['MINGB']); _fk._init.__defaults__ = tuple(d)
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
PRE = opt('--pre', ''); CYC = opt('--cyc', ''); MID = opt('--mid', ''); TAIL = opt('--tail', '-')
KMIN = opt('--kmin', 0); KMAX = opt('--kmax', 10); N = opt('--n', 150); STATE = opt('--state', ''); HIST = opt('--hist', '')
TOP = opt('--top', 20); ORDER = opt('--order', 'pcmt'); TJ = opt('--tasjoin', ''); POKE = opt('--poke', ''); SAVE = opt('--save', ''); MINHP = opt('--minhp', 0)
F0 = int(a[0]); G = compile(a[1], 'g', 'eval')
TK = {}
if TJ:
    ta, tb = map(int, TJ.split('-'))
    for g in range(ta, tb + 1):
        m = TM(g); X_, y_ = XY(m); TK.setdefault((X_, m[0x85], y_, m[0x80], m[0x84], m[0x8C]) + (() if m[0x8C] & 16 else (m[0x89], m[0x87])), g)
def tjoin(s):
    X_, y_ = RXY(s); return TK.get((X_, s['xsub'], y_, s['anim'], s['rflags'], s['coll']) + (() if s['coll'] & 16 else (s['vy'], s['vy_sub'])))
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
def load_rows(p):
    return [row(l.strip()) for l in open(p) if l.strip() and not l.startswith('#')]
if HIST:
    hist = load_rows(HIST)[-1900:]
else:
    def want(f):
        w = set(T(f))
        if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        return tuple(sorted(w))
    hist = [want(f) for f in range(F0 - 300, F0 + 1)]
pres = PRE.split('|'); cycs = CYC.split('|'); mids = MID.split('|'); tails = TAIL.split('|')
cands = {}
for p, c, m, t in itertools.product(pres, cycs, mids, tails):
    for k in range(KMIN, KMAX + 1):
        if not c and k > 0: continue
        parts = {'p': rr(p), 'c': rr(c) * k, 'm': rr(m), 't': rr(t)}
        body = [x for o in ORDER for x in parts[o]]
        if len(body) < N: body += [body[-1] if body else ()] * (N - len(body))
        body = body[:N]
        cands[(p, c, k, m, t)] = body
ok = {}
for kk, v in cands.items():
    if not legal_ok(v, hist): ok[kk] = v
print('cands', len(cands), 'legal', len(ok), flush=True)
fc = core(STATE) if STATE else core_at(F0)
for part in [p for p in POKE.split(';') if p]:
    k_, v_ = part.split('='); fc.poke(int(k_, 0), int(v_, 0))
fc.save('b'); fc._ka_slot = 'b'
names = list(ok); res = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [ok[n] for n in names[i:i+64]], record='all')
    for n, r in zip(names[i:i+64], rs):
        for k, s in enumerate(r.states):
            X, y = RXY(s)
            if s['hp65'] < MINHP: break
            if TJ:
                g = tjoin(s)
                if g is not None:
                    res.append((F0 + 1 + k - g, -s['hp65'], n, k + 1)); break
            elif eval(G, dict(X=X, y=y, s=s, hp=s['hp65'], rm=s['room6e'], it=s['item'], np=s['np64'], f=F0 + 1 + k)):
                res.append((F0 + 1 + k, -s['hp65'], n, k + 1)); break
res.sort(key=lambda q: (q[0], q[1]))
for x in res[:TOP]: print(x[0], 'hp', -x[1], 'pre', repr(x[2][0]), 'cyc', repr(x[2][1]), 'k', x[2][2], 'mid', repr(x[2][3]), 'tail', repr(x[2][4]), flush=True)
if not res: print('no goal')
if SAVE and res:
    rows = ok[res[0][2]][:res[0][3]]
    with open(f'work/l52b/e_{SAVE}.txt', 'w') as fo:
        fo.write(f'# enum {SAVE} goal {res[0][0]} (rows from frame {F0 + 1}) {res[0][2]}\n')
        for r_ in rows: fo.write(P(r_) + '\n')
fc.close()
