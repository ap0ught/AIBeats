"""Which legal stops make tosser 1 sink to y 136 (the TAS's 1-f Left at 22,289 does)? From the TAS state 22,124 ($BF c),
D-variant legalized rows with Right instead of the 1-f Left, plus a stop (2+ frames of '-' or Left) at frame k.
python work/l51p/sink.py c"""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
c = int(sys.argv[1]) if len(sys.argv) > 1 else 86
K1, K2 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (22240, 22300)
def base(N=300, ov={}):
    want = []
    for f in range(22125, 22125 + N):
        w = set(T(f))
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        if f in (22289,): w = {'Right'}
        if f == 22126: w = {'Right'}
        if f == 22125: w = set()
        if f in ov: w = set(ov[f])
        want.append(tuple(sorted(w)))
    en = A.Enforcer([()] * 60); return [tuple(sorted(en.emit(w))) for w in want]
fc = core(tas_mst(22124)); fc.poke(0xBF, (c - 1) % 256); fc.save('b'); fc._ka_slot = 'b'
cands = []; names = []
for kind in ('-', 'Left', 'Down'):
    for n in (2, 3, 4):
        for k in range(K1, K2):
            ov = {k + i: row(kind) for i in range(n)}
            rows = base(200, ov)
            if legal_ok(rows, [()] * 60): continue
            cands.append(rows); names.append((kind, n, k))
cands.append(base(200)); names.append(('none', 0, 0))
rr = fc.run_batch('b', cands, record='all')
for nm, r in zip(names, rr):
    ys = [s['ey5'] for s in r.states[160:200] if s['eact'] >> 5 & 1 and s['t5'] == 2]
    X, y = RXY(r.states[-1])
    print(nm, 'tosser y max', max(ys) if ys else None, 'Ryu X at 22324', X, y, 'hp', r.states[-1]['hp65'])
fc.close()
