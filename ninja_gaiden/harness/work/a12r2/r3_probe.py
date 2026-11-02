"""2-1 room 3: from the room-3 entry (t1 snapshot rows[:1040]) climb the pillar's left face with the 7-frame cycle,
then search: jump off left (L+A), drift, then jump right (R+A) over the pillar top. Report the earliest frame on the
pillar top (x >= 170, y <= 130, standing)."""
import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs, write_inputs
from ng.mode import TICKS
rows=[tuple(r) for r in read_inputs('states/tmp/a12r2_2-1_t1_snap1.inputs.txt')][:1040]
hist=[tuple(r) for r in read_inputs('logs/a12_chain.inputs.txt')]
e=C.open_emu('a12r2_probe.log')
best=None
try:
    e.tick(TICKS); e.load('a12_chain_1-2_end'); e.run(rows)
    cyc=[('Left','A'),('Left','A')]+[('Right',)]*5
    for ph in (2,3,4):
        for climb in range(30,75,3):
            want0=(cyc*20)[ph:ph+climb]
            for n1 in range(0,16,2):
                for gap in range(0,24,2):
                    for jdir in ('Right',):
                        want=want0+[('Left','A'),('Left','A')]+[('Left',)]*n1+[()]*gap+[('Right','A'),('Right','A')]+[('Right',)]*40
                        en=C.Enforcer((hist+rows)[-1900:]); rr=[en.emit(w) for w in want]
                        e.load('a12_chain_1-2_end') if False else None
                        if 'base' not in dir(): base=None
                        e.mload(sid) if 'sid' in dir() else None
                        if 'sid' not in dir():
                            sid=e.msave()
                        e.trace(True); e.run(rr); tr=e.last_trace
                        hit=next((s for s in tr if C.abs_x(s)>=170 and s['y']<=130 and s['room']==3), None)
                        if hit and (best is None or hit['frame']<best[0]):
                            best=(hit['frame'],ph,climb,n1,gap,len(tr)); print('NEW',best,hit['y'],flush=True)
                            write_inputs('states/tmp/a12r2_r3_best.inputs.txt', rows+rr[:hit['frame']-4469], f'r3 probe best {best}')
                        e.mload(sid)
    print('BEST',best)
finally:
    e.close()
