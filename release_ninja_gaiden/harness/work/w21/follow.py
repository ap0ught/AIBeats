"""Legalized TAS rows after a Mesen state.  python -u work/w21/follow.py <hist rows file> <mst> <TAS k0> <n> [--out rows] [--print 25]
hist = power-on rows up to the mst frame. Prints divergence vs TAS (dx,dy)."""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'ng/stages')
from ng.solve import common as C, legality as L
from ng import fastcore as F
import a56_common as A
a=[x for x in sys.argv[1:] if x!='--all']
out=None; pr=25
if '--out' in a: i=a.index('--out'); out=a[i+1]; del a[i:i+2]
if '--print' in a: i=a.index('--print'); pr=int(a[i+1]); del a[i:i+2]
H=C.rows_of(a[0]); k0=int(a[2]); n=int(a[3])
T=A.tas_trace(); TR=A.tas_rows()
rows=L.legalize(TR[k0:k0+n], H[-1900:])
fc=F.FastCore(boot_rows=None); fc.put('s',open(a[1],'rb').read()); fc.load('s')
_,recs,_=fc.step(rows,record='all'); fc.close()
div=None
for i,s in enumerate(recs):
    t=T[k0+i+1]
    dx=C.abs_x(s)-C.abs_x(t); dy=s['y']-t['y']
    bad = s['room']!=t['room'] or abs(dx)>2 or abs(dy)>2
    if bad and div is None: div=i
    if i%pr==0 or i==div:
        print(f"i {i} f {len(H)+i+1} r{s['room']} X {C.abs_x(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} bf {s['rng']} | TAS {k0+i+1} r{t['room']} X {C.abs_x(t)} y {t['y']} hp {t['hp']} np {t['ninpo']}"+(' <== div' if i==div else ''))
print('first div', div)
if out: C.write_inputs(out, list(rows[:n] if '--all' in sys.argv else rows[:div if div is not None else n]), f'legal TAS {k0}..')
