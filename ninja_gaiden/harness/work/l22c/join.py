"""python work/l22c/join.py <out> <file>[@n] ...  concatenate row files (optionally first n rows)"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C
rows=[]; parts=[]
for a in sys.argv[2:]:
    f,_,n=a.partition('@')
    r=C.rows_of(f); r=r[:int(n)] if n else r; rows+=r; parts.append(f"{f}[:{len(r)}]")
C.write_inputs(sys.argv[1], rows, ' + '.join(parts)); print(len(rows))
