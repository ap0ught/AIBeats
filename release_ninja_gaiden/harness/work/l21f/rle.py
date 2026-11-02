import sys
sys.path.insert(0,'.')
from ng.solve import common as C
r=C.rows_of(sys.argv[1]); a=int(sys.argv[2]) if len(sys.argv)>2 else 0
out=[];prev=None;n=0
for x in r[a:]:
    k='+'.join(x) or '-'
    if k==prev: n+=1
    else:
        if prev is not None: out.append(f'{prev}*{n}')
        prev=k;n=1
out.append(f'{prev}*{n}'); print(';'.join(out))
