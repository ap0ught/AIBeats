"""From <rows>[:N]: try  Right x n1, Right+A x2, Right x n2, [Right+A x2, Right x 40]  -> earliest frame with
X >= gx and y == gy (standing).  python work/a12r2/jump_brute.py <start> <rows> N gx gy <hist> <out> [maxn1]"""
import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs, write_inputs
from ng.mode import TICKS
start, f, N, gx, gy, hf, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], sys.argv[7]
mx = int(sys.argv[8]) if len(sys.argv) > 8 else 40
rows=[tuple(r) for r in read_inputs(f)][:N]; hist=[tuple(r) for r in read_inputs(hf)]
e=C.open_emu('a12r2_probe.log'); best=None
try:
    e.tick(TICKS); e.load(start); st=e.run(rows); sid=e.msave(); print('at',st['frame'],C.abs_x(st),st['y'],flush=True)
    for n1 in range(0,mx):
        for n2 in list(range(4,40,3))+[200]:
            want=[('Right',)]*n1+[('Right','A')]*2+[('Right',)]*n2+[('Right','A')]*2+[('Right',)]*60
            en=C.Enforcer((hist+rows)[-1900:]); rr=[en.emit(w) for w in want][:n1+n2+70]
            e.mload(sid); e.trace(True); e.run(rr); tr=e.last_trace
            if any(s.get('dw') for s in tr): continue
            hit=next((i for i,s in enumerate(tr) if C.abs_x(s)>=gx and s['y']==gy), None)
            if hit is not None and (best is None or hit<best[0]):
                best=(hit,n1,n2); print('NEW',best,tr[hit]['frame'],flush=True)
                write_inputs(out, rows+rr[:hit+1], f'jump brute {best} frame {tr[hit]["frame"]}')
    print('BEST',best)
finally: e.close()
