"""python work/l22c/en.py <mst> <hist> "<spec>" [every]  enemies + Ryu along a spec"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from ng.solve import common as C, legality as L, hitbox as H
from ng import fastcore as F
from wlib import spec
SHORT='--short' in sys.argv
if SHORT: sys.argv.remove('--short')
out=[]
mst,hf,sp=sys.argv[1:4]; ev=int(sys.argv[4]) if len(sys.argv)>4 else 5
hist=C.rows_of(hf); en=L.Enforcer(list(hist)[-1900:]); rows=[tuple(sorted(en.emit(w))) for w in spec(sp)]
fc=F.FastCore(boot_rows=None); fc.put('s',open(mst,'rb').read()); fc.load('s')
for i,r in enumerate(rows):
    fc.step([r],record='last'); m=fc.ram()
    if i%ev==0 or i==len(rows)-1:
        s52=m[0x52]-256 if m[0x52]>=128 else m[0x52]; sc=s52*256+m[0x51]
        if SHORT: out.append(f"{i+1}:{sc+m[0x86]},{m[0x8A]}" + (f",h{m[0x65]}" if m[0x65]!=16 else '') + ''.join(f"|b{sc+e['x']},{e['y']}" for e in H.enemies(m)))
        else: print(i+1,'+'.join(r) or '-','ryu X',sc+m[0x86],'y',m[0x8A],'hp',m[0x65],'bf',m[0xBF],'sc',sc,'en',[(e['slot'],e['type'],sc+e['x'],e['y']) for e in H.enemies(m)])
fc.close()
if SHORT: print(' '.join(out))
