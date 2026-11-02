"""python work/l22c/tr.py <mst> <hist> "<spec>" [every]  compact trace: row X y coll hp np (every k + changes of coll)"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from ng.solve import common as C, legality as L
from ng import fastcore as F
from wlib import spec, fmt
mst,hf,sp=sys.argv[1:4]; ev=int(sys.argv[4]) if len(sys.argv)>4 else 5
hist=C.rows_of(hf) if hf!='-' else [()]*60
en=L.Enforcer(list(hist)[-1900:]); rows=[tuple(sorted(en.emit(w))) for w in spec(sp)]
fc=F.FastCore(boot_rows=None); fc.put('s',open(mst,'rb').read()); fc.load('s')
_,recs,_=fc.step(rows,record='all'); fc.close()
ab={'Right':'R','Left':'L','Up':'U','Down':'D','A':'A','B':'B'}
out=[]; pc=None
for i,(s,r) in enumerate(zip(recs,rows)):
    if i%ev==0 or s['coll']!=pc or i==len(rows)-1:
        out.append(f"{i+1}{''.join(ab[b] for b in r) or '-'}:{C.abs_x(s)},{s['y']},c{s['coll']}" + (f",hp{s['hp']}" if s['hp']!=recs[0]['hp'] else '') + (f",r{s['room']}" if s['room']!=recs[0]['room'] else ''))
    pc=s['coll']
print(' '.join(out))
