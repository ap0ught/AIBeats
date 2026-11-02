"""Quick test from TAS 22,124 with $BF after the control row = c: base = variant-D legalized TAS rows (blank control row),
overrides 'f=ROW,f2-f3=ROW' (ROW like A+Right or -); prints hits, goal frame, tosser-1 x track.
python work/l51p/tv.py c "22289-22290=Left" [--n 520] [--goal 600] [--track 22288:22400:8]"""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
N = opt('--n', 520); GOAL = opt('--goal', 600); TRK = opt('--track', ''); RAWOK = opt('--raw', 0)
c = int(a[0]); ov = {}
for it in (a[1].split(',') if len(a) > 1 and a[1] else []):
    k, v = it.split('=')
    k1, k2 = (k.split('-') + [k])[:2]
    for f in range(int(k1), int(k2) + 1): ov[f] = row(v)
hist = [()] * 60
want = []
for f in range(22125, 22125 + N):
    w = set(T(f))
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    if f in (22289, 22793): w = {'Right'}
    if f == 22126: w = {'Right'}
    if f == 22125: w = set()
    if f in ov: w = set(ov[f])
    want.append(tuple(sorted(w)))
en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(w))) for w in want]
lg = legal_ok(rows, hist)
if lg: print('ILLEGAL', lg)
for f in sorted(ov):
    if tuple(sorted(rows[f-22125])) != tuple(sorted(ov[f])): print('enforcer changed', f, P(ov[f]), '->', P(rows[f-22125]))
fc = core(tas_mst(22124)); fc.poke(0xBF, (c - 1) % 256)
_, recs, _ = fc.step(rows, record='all')
TG = next(f for f in range(22126, 22126 + 600) if tas_xy(f)[0] >= GOAL)
hp = 16; hits = []; g = None
t1 = t2 = st = 0
if TRK: t1, t2, st = map(int, TRK.split(':'))
for i, r in enumerate(recs):
    f = 22125 + i; X, y = RXY(r)
    if r['hp65'] != hp: hits.append(f'{f}:{X},{y},{hp}->{r["hp65"]}'); hp = r['hp65']
    if t1 <= f <= t2 and (f - t1) % st == 0:
        scr = X - r['x86']
        es = [f's{j}t{r[f"t{j}"]}({scr + r[f"ex{j}"]},{r[f"ey{j}"]})' for j in range(8) if r['eact'] >> j & 1]
        tm = TM(f); TX_, TY_ = XY(tm)
        print(f'  {f} X {X} y {y} hp {r["hp65"]} | TAS {TX_},{TY_} | {" ".join(es)}')
    if g is None and X >= GOAL: g = f
print(f'c {c} goal {g} (TAS+{g - TG if g else None}) hits {hits}')
fc.close()
