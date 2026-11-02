import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs
from ng.mode import TICKS
rows=[tuple(r) for r in read_inputs('states/tmp/a12r2_w6_comb.inputs.txt')][:1981]; hist=[tuple(r) for r in read_inputs('logs/a12_chain.inputs.txt')]
e=C.open_emu('a12r2_probe.log')
try:
    e.tick(TICKS); e.load('a12_chain_1-2_end'); st=e.run(rows); sid=e.msave()
    en=C.Enforcer((hist+rows)[-1900:]); print('canA', en.can_press('A'), en.held, en.run)
    want=[('Left','A')]*2+[('Left',)]*20
    rr=[en.emit(w) for w in want]; print(rr[:4])
    e.trace(True); e.run(rr); print([(C.abs_x(s),s['y'],s.get('dw'),s['hp']) for s in e.last_trace][:22])
finally: e.close()
