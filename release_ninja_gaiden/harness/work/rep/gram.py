"""materialize a fixed grammar 'ROW*n;...' as legal rows after a history: python work/rep/gram.py hist "<g>" out"""
import sys
sys.path.insert(0,'.')
from ng.solve import common as C, legality as L
hist=C.rows_of(sys.argv[1]); w=[]
for sg in sys.argv[2].split(';'):
    r,n=sg.rsplit('*',1); w+=[() if r=='-' else tuple(r.split('+'))]*int(n)
en=L.Enforcer(hist[-1900:]); lg=[tuple(sorted(en.emit(x))) for x in w]
C.write_inputs(sys.argv[3], hist+lg, f'hist + {sys.argv[2]}'); print(len(hist+lg))
