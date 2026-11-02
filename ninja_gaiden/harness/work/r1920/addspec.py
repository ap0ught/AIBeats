"""Append spec rows (truncated to n) to a stage rows file: python work/r1920/addspec.py <in> <out> "<spec>" <n>"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/r1920')
from ng.solve import common as C
from gbeam import row
def spec(sp):
    out=[]
    for tok in sp.split():
        k,n=tok.split(':') if ':' in tok else (tok,'1'); out+=[row(k)]*int(n)
    return out
a=[tuple(x) for x in C.rows_of(sys.argv[1])]
b=spec(sys.argv[3])[:int(sys.argv[4])]
C.write_inputs(sys.argv[2], a+b, f'{sys.argv[1]} + spec {sys.argv[3]}[:{sys.argv[4]}]')
print(len(a+b), 19295+len(a+b))
