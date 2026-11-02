import sys; sys.path.insert(0,'.'); sys.path.insert(0,'ng/stages')
from ng.solve import common as C
import a56_common as A
T=A.tas_trace(); TR=A.tas_rows()
a,b=int(sys.argv[1]),int(sys.argv[2]); st=int(sys.argv[3]) if len(sys.argv)>3 else 1
ab={'Right':'R','Left':'L','Up':'U','Down':'D','A':'A','B':'B','Start':'S','Select':'s'}
for f in range(a,b,st):
    t=T[f]; r=TR[f-1] if f-1<len(TR) else ()
    print(f, ''.join(ab.get(x,x) for x in r) or '-', 'st',t['stage'],'r',t['room'],'X',C.abs_x(t),'x',t['x'],'y',t['y'],'vy',t.get('vy'),'coll',t.get('coll'),'anim',t.get('anim'),'hp',t['hp'],'np',t['ninpo'],'bf',t['rng'])
