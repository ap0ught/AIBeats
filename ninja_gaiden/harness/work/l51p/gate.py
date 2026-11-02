"""5-1 tosser-1 gate: cost by c = $BF after the 5-1 control row (our 5-1 control row F -> c = (F - 23) mod 256;
tosser-1 spawn BF b = c + 163 on the TAS-pace line).
Per c: TAS state 22,124 with $BF poked, D-variant legal rows (blank control row, Right from row 2) to 22,284, then
candidates = sink stop (rows after the spawn left blank / Left, which make the tosser sink into the pillar) x jump frame j
(Right, A+Right x2 at j, Right; a late j = waiting at the pillar face) -> 'up' = first frame on the pillar/wall top (y <= 128, X >= 448).
The best 'up' candidates continue with legalized TAS rows (22,390.. at lag up - 22,389) to X >= 600 (TAS 22,488).
python -u work/l51p/gate.py c1 c2 ... [--jmax 22430]"""
import sys, time
sys.path.insert(0, 'work/l51p')
from lib import *
a = sys.argv[1:]
JMAX = 22440
if '--jmax' in a: i = a.index('--jmax'); JMAX = int(a[i+1]); del a[i:i+2]
vals = [int(v) for v in a]
STOPS = {'blank2@22290': {22290: '-', 22291: '-'}, 'Left2@22289': {22289: 'Left', 22290: 'Left'}}
pre = []
for f in range(22125, 22285):
    w = set(T(f))
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    if f == 22126: w = {'Right'}
    if f == 22125: w = set()
    pre.append(tuple(sorted(w)))
en = A.Enforcer([()] * 60); pre = [tuple(sorted(en.emit(w))) for w in pre]
def cand(stop, j):
    want = []
    for f in range(22285, 22426):
        w = {'Right'}
        if f < 22350:
            w = set(T(f))
            if f == 22289: w = {'Right'}
        if f in STOPS[stop]: w = set(row(STOPS[stop][f]))
        if j <= f < j + 2: w = {'A', 'Right'}
        want.append(tuple(sorted(w)))
    e2 = A.Enforcer([()] * 60 + pre); return [tuple(sorted(e2.emit(w))) for w in want]
def cont(rows, up, dl=0):
    want = [set(r) for r in rows[:up - 22284 + dl]]
    for f in range(22390, 22560):
        w = set(T(f))
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        want.append(w)
    e2 = A.Enforcer([()] * 60 + pre); return [tuple(sorted(e2.emit(w))) for w in want]
fc = core(tas_mst(22124)); fc._ka_slot = "s"
for c in vals:
    t0 = time.time()
    fc.load('s'); fc.poke(0xBF, (c - 1) % 256); fc.step(pre, record='last'); fc.save('b'); fc._ka_slot = 'b'
    bf_spawn = (c + 163) % 256
    names, cands = [], []
    for st in STOPS:
        for j in range(22350, JMAX):
            r = cand(st, j)
            if legal_ok(pre + r, [()] * 60): continue
            names.append((st, j)); cands.append(r)
    res = fc.run_batch('b', cands, record='all')
    ups = []
    for nm, r in zip(names, res):
        hp = 16; hits = []; up = None
        for i, s in enumerate(r.states):
            f = 22285 + i; X, y = RXY(s)
            if s['hp65'] != hp: hits.append(f); hp = s['hp65']
            if up is None and y <= 128 and X >= 448 and f > 22340: up = f
        if up: ups.append((up, -hp, nm, hits))
    ups.sort()
    best = []
    for up, mhp, nm, hits in ups[:4]:
      for dl in (0, 1, 2):
        r = cont(cand(*nm), up, dl)
        rr = fc.run_batch('b', [r], record='all')[0]
        hp = 16; hl = []; g = None
        for i, s in enumerate(rr.states):
            f = 22285 + i; X, y = RXY(s)
            if s['hp65'] != hp: hl.append(f'{f}:{hp}->{s["hp65"]}'); hp = s['hp65']
            if X >= 600 and g is None: g = f
        best.append((g or 99999, nm + (dl,), up, hl))
    best.sort()
    b0 = best[0] if best else None
    print(f'c {c:3d} spawnBF {bf_spawn:3d} delay {bf_spawn >> 1:3d} | best up {ups[0][0] if ups else None} ({ups[0][2] if ups else ""}) | '
          f'X600 {b0[0] if b0 else None} = TAS{(b0[0] - 22488) if b0 else 0:+d} via {b0[1] if b0 else ""} hits {b0[3] if b0 else ""} | '
          f'others {[(q[0] - 22488, q[1]) for q in best[1:]]} {time.time()-t0:.0f}s', flush=True)
    fc._ka_slot = None
fc.close()
