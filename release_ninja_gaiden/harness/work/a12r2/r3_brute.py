import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs, write_inputs
from ng.mode import TICKS
rows=[tuple(r) for r in read_inputs('states/tmp/a12r2_2-1_t1_snap1.inputs.txt')][:1040]
hist=[tuple(r) for r in read_inputs('logs/a12_chain.inputs.txt')]
e=C.open_emu('a12r2_probe.log'); best=None
try:
    e.tick(TICKS); e.load('a12_chain_1-2_end'); e.run(rows); sid=e.msave()
    cyc=[('Left','A'),('Left','A')]+[('Right',)]*5
    for ph in range(7):
      for climb in range(54,70):
        for n1 in range(24,32):
          for pre in (1,2,3):
            want=(cyc*20)[ph:ph+climb]+[('Left','A'),('Left','A')]+[('Left',)]*n1+[('Right',)]*pre+[('Right','A'),('Right','A')]+[('Right',)]*45
            en=C.Enforcer((hist+rows)[-1900:]); rr=[en.emit(w) for w in want]
            e.mload(sid); e.trace(True); e.run(rr); tr=e.last_trace
            hit=next((i for i,s in enumerate(tr) if C.abs_x(s)>=168 and s['y']==128 and s['room']==3), None)
            if hit is not None and (best is None or hit<best[0]):
                best=(hit,ph,climb,n1,pre); print('NEW',best,tr[hit]['frame'],flush=True)
                write_inputs('states/tmp/a12r2_r3_best.inputs.txt', rows+rr[:hit+1], f'2-1 room 3 pillar: {best}, frame {tr[hit]["frame"]}')
    print('BEST',best)
finally: e.close()
