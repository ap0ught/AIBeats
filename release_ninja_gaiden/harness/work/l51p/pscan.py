"""Fast gate scan: the head-start rows work/l51p/pre51_22490.txt (TAS +2 at X 600) for every c ($BF after the 5-1 control row);
reports X600 frame / hits.  python work/l51p/pscan.py [c ...]"""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
rows = [tuple(sorted(r)) for r in C.rows_of('work/l51p/pre51_22490.txt')] + [('Right',)] * 20
vals = [int(v) for v in sys.argv[1:]] or list(range(256))
fc = core(tas_mst(22124)); fc.save('b'); fc._ka_slot = 'b'
for c in vals:
    fc.load('b'); fc.poke(0xBF, (c - 1) % 256)
    _, recs, _ = fc.step(rows, record='all')
    hp = 16; hits = []; g = None
    for i, r in enumerate(recs):
        f = 22125 + i; X, y = RXY(r)
        if r['hp65'] != hp: hits.append(f'{f}:{X},{y},{hp}->{r["hp65"]}'); hp = r['hp65']
        if g is None and X >= 600: g = f
    print(f'c {c:3d} spawnBF {(c + 163) % 256:3d} X600 {g} {"OK TAS%+d" % (g - 22488) if g else "FAIL"} hits {hits}', flush=True)
fc.close()
