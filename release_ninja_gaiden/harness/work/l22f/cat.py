"""python work/l22f/cat.py out file1[:n] file2[:n] ...  (concatenate stage-row files)"""
import sys
sys.path.insert(0,'.')
from ng.solve import common as C
out=[]
for a in sys.argv[2:]:
    f,_,n=a.partition(':'); r=C.rows_of(f); out+=r[:int(n)] if n else r
C.write_inputs(sys.argv[1],out,'cat '+' '.join(sys.argv[2:])); print(len(out))
