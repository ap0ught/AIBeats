"""Earliest Start in the act-end cutscene + 5-1 control rule, on the p2 kill rows."""
import sys
sys.path.insert(0, 'work/l44p')
from run import *
rows = [tuple(sorted(r)) for r in C.rows_of('work/l44p/p2L.txt')][:40]
fc = core(PRE)
for sa in [int(x) for x in sys.argv[1].split(',')]:
    print(sa, fin(fc, rows, start_at=sa, maxf=1000), flush=True)
fc.close()
