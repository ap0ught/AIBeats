"""Tosser-1 gate, first look: TAS Mesen state 22,124 (pre-control) with $BF poked so that $BF after the control row = c,
then legalized TAS rows (22,126 blank -> Right (variant R) or Right,-,- release-2 (variant B); 1-f Left 22,289 -> Right;
1-f A/B -> 2 f). Reports first frame at X >= GOAL, hits (frame, X, y, hp), y at X 460.
python work/l51p/scan1.py R|B|D (D = blank control row, Right from row 2 = the TAS's positions) [c ...]"""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
var = sys.argv[1]; vals = [int(v) for v in sys.argv[2:]] or list(range(256))
GOAL = 600; N = 520
hist = C.rows_of('logs/a34/4-4_p2.inputs.txt')[-200:] if False else [()] * 60
want = []
for f in range(22125, 22125 + N):
    w = set(T(f))
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    if f in (22289, 22793): w = {'Right'}
    if f == 22126: w = {'Right'} if var in 'RD' else set()
    if var == 'D' and f == 22125: w = set()
    if var == 'B' and f == 22127: w = set()
    want.append(tuple(sorted(w)))
en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(w))) for w in want]
assert not legal_ok(rows, hist), legal_ok(rows, hist)
fc = core(tas_mst(22124)); fc.save('b'); fc._ka_slot = 'b'
TG = next(f for f in range(22126, 22126 + 600) if tas_xy(f)[0] >= GOAL)
print('TAS reaches X', GOAL, 'at', TG, flush=True)
for c in vals:
    fc.load('b'); fc.poke(0xBF, (c - 1) % 256)
    _, recs, _ = fc.step(rows, record='all')
    hp = 16; hits = []; g = None; y460 = None; sp = None
    for i, r in enumerate(recs):
        f = 22125 + i; X, y = RXY(r)
        if r['hp65'] != hp: hits.append(f'{f}:{X},{y},{hp}->{r["hp65"]}'); hp = r['hp65']
        if y460 is None and X >= 460: y460 = y
        if sp is None and any(r['eact'] >> j & 1 and r[f't{j}'] == 2 for j in range(8)): sp = (f, X, r['bf'])
        if X >= GOAL: g = f; break
    print(f'c {c:3d} spawn {sp} goal {g} (TAS+{g - TG if g else None}) y@460 {y460} hits {hits}', flush=True)
fc.close()
