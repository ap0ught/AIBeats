"""From <rows file>[:N] (start state + history given), try wall-climb cycle families, report earliest frame reaching
(X >= gx, y <= gy)."""
import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs, write_inputs
from ng.mode import TICKS
start, f, N, gx, gy, hist_f = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
rows=[tuple(r) for r in read_inputs(f)][:N]; hist=[tuple(r) for r in read_inputs(hist_f)]
e=C.open_emu('a12r2_probe.log'); best=None
try:
    e.tick(TICKS); e.load(start); st=e.run(rows); sid=e.msave(); print('at',st['frame'],C.abs_x(st),st['y'])
    fams=[]
    for away,back in (('Left','Right'),('Right','Left')):
        for k in (4,5,6,7,8):
            fams.append((f'{away[0]}A2,{back[0]}{k}',[(away,'A'),(away,'A')]+[(back,)]*k))
        fams.append((f'{back[0]}A..',[(back,'A'),(back,'A')]+[(back,)]*6))
    for tail in ([('Right','A'),('Right','A')]+[('Right',)]*10, [('Right',)]*12, [('Left','A'),('Left','A')]+[('Right',)]*10):
      for nm,c in fams:
        for ph in range(len(c)):
          for L in range(0,64,4):
            want=(c*20)[ph:ph+L]+tail
            en=C.Enforcer((hist+rows)[-1900:]); rr=[en.emit(w) for w in want]
            e.mload(sid); e.trace(True); e.run(rr); tr=e.last_trace
            if any(s.get('dw') for s in tr): continue
            hit=next((i for i,s in enumerate(tr) if C.abs_x(s)>=gx and s['y']<=gy), None)
            if hit is not None and (best is None or hit<best[0]):
                best=(hit,nm,ph,L,tail[0]); print('NEW',best,tr[hit]['frame'],C.abs_x(tr[hit]),tr[hit]['y'],flush=True)
                write_inputs(sys.argv[7], rows+rr[:hit+1], f'wall probe {best} frame {tr[hit]["frame"]}')
    print('BEST',best)
finally: e.close()
