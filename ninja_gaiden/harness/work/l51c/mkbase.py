"""make a Mesen state on the c1 line: python work/l51c/mkbase.py <from.mst> F0 F1 <out.mst>"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
mst, F0, F1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
rows = c1rows()
fc = core(mst)
r = fc.run_batch('s', [rows[F0:F1]], record='last', keep=True, prefix='o')[0]
print(line(F1, r.states[-1]))
fc.save_file('o1', out, F1)
fc.close()
