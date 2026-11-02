import sys, itertools; sys.path.insert(0,'.'); sys.path.insert(0,'work/l12')
from lib import *
base=C.rows_of('logs/tk_1-2_s11.inputs.txt')[:100]
# base offsets: rows index i-1 = offset i
pre=[tuple(r) for r in base[:76]]  # offsets 1..76
opts=['','Left','Right','A','B','A+B','Left+A','Left+B','Left+A+B','Right+A','Right+B','Right+A+B']
cands=[];meta=[];seen=set()
for a77,a78,a79,a80,a81 in itertools.product(['','Left'],opts,opts,opts,opts):
    w=pre+[row(a77),row(a78),row(a79),row(a80),row(a81)]
    w+= [row('Left+B')]*2+[row('Left')]*12
    lg=legalize(w)
    if lg in seen: continue
    seen.add(lg);cands.append(lg);meta.append((a77,a78,a79,a80,a81))
print(len(cands),flush=True)
P=pool(2); res=run(P,cands); P.close()
out=[]
for m,r in zip(meta,res):
    k=kill(r); out.append(((k[0] if k else 999), [s['bosshp'] for s in r.states[76:84]], m))
out.sort(key=lambda z:(z[0],z[1][-1]))
for o in out[:15]: print(o)
