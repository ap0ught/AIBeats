"""Is an arrival shift equivalent to a $BF change? rows R = head start without the blank control row (Right on row 1, all rows
1 frame earlier), S2 = 2 extra blank rows after the control row (all rows 2 frames later). Compare X600/hit frames.
python work/l51p/shift.py c1 c2 ..."""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
D = [tuple(sorted(r)) for r in C.rows_of('work/l51p/pre51_22490.txt')] + [('Right',)] * 20
V = {'D': D, 'R': D[1:] + [('Right',)], 'S2': [(), (), ()] + D[1:-2]}
for k, v in V.items(): print(k, 'legal', legal_ok(v, [()] * 60) or 'ok')
fc = core(tas_mst(22124)); fc.save('b'); fc._ka_slot = 'b'
for c in [int(x) for x in sys.argv[1:]]:
    out = []
    for k, rows in V.items():
        fc.load('b'); fc.poke(0xBF, (c - 1) % 256)
        _, recs, _ = fc.step(rows, record='all')
        hp = 16; hits = []; g = None
        for i, r in enumerate(recs):
            f = 22125 + i; X, y = RXY(r)
            if r['hp65'] != hp: hits.append(f); hp = r['hp65']
            if g is None and X >= 600: g = f
        out.append(f'{k}: X600 {g} hits {hits}')
    print(f'c {c:3d} |', ' | '.join(out), flush=True)
fc.close()
