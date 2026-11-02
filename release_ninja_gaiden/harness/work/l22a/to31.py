"""python work/l22a/to31.py <2-2 stage rows (to 2-3 control)> <out power-on file>: last row -> Left, + l23_t12_va, power-on"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C
h=list(C.rows_of('logs/l21f_fol_v4_poweron.inputs.txt')); r=[tuple(x) for x in C.rows_of(sys.argv[1])]
assert r[-1]==(), r[-1]
r[-1]=('Left',)
l23=list(C.rows_of('logs/l23_t12_va.inputs.txt'))
C.write_inputs(sys.argv[2], h+r+l23, f'power-on: locked to 2-2 control + {sys.argv[1]} (last row Left) + logs/l23_t12_va (2-3)')
print(len(h+r+l23), 'rows; 2-3 control at', len(h)+len(r))
