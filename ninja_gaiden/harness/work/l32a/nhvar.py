"""NesHawk: variants of TAS-row compositions from a NesHawk state at k0 rows of <prefix>.
python work/l32a/nhvar.py <prefix> <state> k0 n --lags .. --var "SETSPEC" --var "SETSPEC" ... [--keep ..]
SETSPEC = r=SPEC,r1-r2=SPEC,...  Prints per variant: first hp loss, X/y at n, frames to reach --gx."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l32a'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C, legality as L
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows(); TT = A.tas_trace()
a = sys.argv[1:]
vars_ = []
while '--var' in a:
    i = a.index('--var'); vars_.append(a[i + 1]); del a[i:i + 2]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
lags = sorted([tuple(map(int, q.split(':'))) for q in opt('--lags', '').split(',') if q]); keep = {int(q) for q in opt('--keep', '').split(',') if q}
GX = opt('--gx', 99999)
pre = [tuple(r) for r in C.rows_of(a[0])]; stn = a[1]; k0, n = int(a[2]), int(a[3])
HIST = C.rows_of('logs/l31_alt_b2r_poweron.inputs.txt'); F0 = len(HIST)
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
def lagf(r):
    L_ = 160
    for r0, l0 in lags:
        if r >= r0: L_ = l0
    return L_
def comp(spec):
    sets = {}
    for q in spec.split(','):
        if not q: continue
        k, v = q.split('=')
        if '-' in k:
            p, r = map(int, k.split('-'))
            for x in range(p, r + 1): sets[x] = row(v)
        else: sets[int(k)] = row(v)
    want = list(pre[:k0])
    for k in range(k0, n):
        w = tuple(TR[F0 + k - lagf(k + 1)])
        if 'Up' in w and 'B' in w and (k + 1) not in keep: w = ('Right',)
        if (k + 1) in sets: w = sets[k + 1]
        want.append(w)
    en = L.Enforcer((list(HIST) + want[:k0])[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want[k0:]]
def X(m): return (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51] + m[0x86]
e = C.open_emu('l32a_nhvar.log')
try:
    e.tick(TICKS); st = e.load(stn); sid = e.msave(); hp0 = None
    for v in vars_:
        lg = comp(v); e.mload(sid); _, rams = e.run_ram(lg)
        hp0 = rams[0][0x65]
        hit = next((k0 + i + 1 for i, m in enumerate(rams) if m[0x65] < hp0), None)
        gx = next((F0 + k0 + i + 1 for i, m in enumerate(rams) if X(m) >= GX), None)
        m = rams[-1]; f = F0 + n
        print(v[:60], '| hit', hit, 'gx', gx, 'end X', X(m), 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'xsub', m[0x85], flush=True)
finally:
    e.close()
