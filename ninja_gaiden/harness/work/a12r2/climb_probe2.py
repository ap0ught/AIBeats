import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs
from ng.mode import TICKS
rows=[tuple(r) for r in read_inputs('states/tmp/a12r2_2-1_t1_snap1.inputs.txt')]
hist=[tuple(r) for r in read_inputs('logs/a12_chain.inputs.txt')]
e=C.open_emu('a12r2_probe.log')
try:
    e.tick(TICKS); e.load('a12_chain_1-2_end')
    N=int(sys.argv[1]) if len(sys.argv)>1 else 1040
    st=e.run(rows[:N]); print('at',st['frame'],C.abs_x(st),st['y'],st['room'])
    base=e.msave()
    cyc0={'LA,LA,R,R,R':[('Left','A'),('Left','A'),('Right',),('Right',),('Right',)],
         'RA,RA,L,L,L':[('Right','A'),('Right','A'),('Left',),('Left',),('Left',)],
         'LA,LA,RA,RA,RA':[('Left','A'),('Left','A'),('Right','A'),('Right','A'),('Right','A')],
         'RA,RA,LA,LA,LA':[('Right','A'),('Right','A'),('Left','A'),('Left','A'),('Left','A')],
         'LA,LA,R*8':[('Left','A'),('Left','A')]+[('Right',)]*8,
         'RA,RA,L*8':[('Right','A'),('Right','A')]+[('Left',)]*8}
    cyc={}
    for k in range(3,9):
        cyc[f'LA2,R{k}']=[('Left','A'),('Left','A')]+[('Right',)]*k
        cyc[f'LA2,-1,R{k-1}']=[('Left','A'),('Left','A'),()]+[('Right',)]*(k-1)
        cyc[f'LA3,R{k}']=[('Left','A'),('Left','A'),('Left',)]+[('Right',)]*k
    for nm,c in cyc.items():
        for ph in (2,3,4):
            e.mload(base); en=C.Enforcer((hist+rows[:N])[-1900:])
            want=(c*12)[ph:ph+60]; rr=[en.emit(w) for w in want]
            e.trace(True); e.run(rr); tr=e.last_trace
            ys=[s['y'] for s in tr]; xs=[C.abs_x(s) for s in tr]
            print(nm,ph,'y60',ys[-1],'miny',min(ys),'x',min(xs),max(xs))
finally:
    e.close()
