"""python work/r1920/addrows.py <in> <rows> <out>"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C
a=[tuple(x) for x in C.rows_of(sys.argv[1])]+[tuple(x) for x in C.rows_of(sys.argv[2])]
C.write_inputs(sys.argv[3], a, f'{sys.argv[1]} + {sys.argv[2]}'); print(len(a), 19295+len(a))
