import sys; sys.path.insert(0,'.')
from ng.solve import common as C
r=C.rows_of(sys.argv[1]); s=int(sys.argv[2]) if len(sys.argv)>2 else 0
out=[];prev=None;n=0
for x in list(r[s:])+[None]:
    k=''.join({'Right':'R','Left':'L','Up':'U','Down':'D','A':'A','B':'B','Start':'S'}[b] for b in sorted(x)) if x else '-'
    if x is None or k!=prev:
        if prev is not None: out.append(f'{prev}:{n}' if n>1 else prev)
        prev=k;n=1
    else: n+=1
print(len(r), ' '.join(out))
