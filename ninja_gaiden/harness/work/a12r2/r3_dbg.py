import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs
from ng.mode import TICKS
rows=[tuple(r) for r in read_inputs('states/tmp/a12r2_2-1_t1_snap1.inputs.txt')][:1040]
hist=[tuple(r) for r in read_inputs('logs/a12_chain.inputs.txt')]
e=C.open_emu('a12r2_probe.log')
try:
    e.tick(TICKS); e.load('a12_chain_1-2_end'); e.run(rows)
    cyc=[('Left','A'),('Left','A')]+[('Right',)]*5
    want=(cyc*20)[2:2+int(sys.argv[1])]+[('Left','A'),('Left','A')]+[('Left',)]*int(sys.argv[2])+[()]*int(sys.argv[3])+[('Right',)]*int(sys.argv[4])+[('Right','A'),('Right','A')]+[('Right',)]*40
    en=C.Enforcer((hist+rows)[-1900:]); rr=[en.emit(w) for w in want]
    e.trace(True); e.run(rr); tr=e.last_trace
    for i,s in enumerate(tr):
        if i%3==0: print(i, rr[i], C.abs_x(s), s['y'], s.get('anim'), s.get('coll'), end=' | ')
    e.load('a12_chain_1-2_end'); e.run(rows); 
    for i in range(0,len(rr),12):
        e.run(rr[i:i+12]); e.screenshot(f'a12r2_r3_{i:03d}')
finally: e.close()
