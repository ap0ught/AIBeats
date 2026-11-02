"""python work/l51c/show.py <mst> F0 f1 f2 [step] [rowsfile]: play rows (default c1) from state at F0, print frames f1..f2"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
mst, F0, f1, f2 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
st = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rows = [tuple(sorted(r)) for r in C.rows_of(sys.argv[6])] if len(sys.argv) > 6 else c1rows()
fc = core(mst)
r = fc.run_batch('s', [rows[F0:f2]], record='all')[0]
for i, s in enumerate(r.states):
    f = F0 + 1 + i
    if f >= f1 and (f - f1) % st == 0: print(line(f, s), '|', P(rows[f-1]))
fc.close()
