"""python work/l22a/cat.py <out> <desc> <rows file>[:n] ...  concatenate stage rows"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C
out=[]
for a in sys.argv[3:]:
    f,n=(a.split(':')+[None])[:2] if ':' in a[2:] else (a,None)
    r=list(C.rows_of(f)); out+=r[:int(n)] if n else r
C.write_inputs(sys.argv[1],out,sys.argv[2]); print(len(out))
