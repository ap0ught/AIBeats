import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs
from ng.mode import TICKS
f,N=sys.argv[1],int(sys.argv[2]); seq=sys.argv[3]
rows=[tuple(r) for r in read_inputs(f)][:N]; hist=[tuple(r) for r in read_inputs('logs/a12_chain.inputs.txt')]
want=[]
for tok in seq.split(','):
    b,n=tok.split('*'); want+=[tuple(x for x in b.split('+') if x)]*int(n)
e=C.open_emu('a12r2_probe.log')
try:
    e.tick(TICKS); e.load('a12_chain_1-2_end'); st=e.run(rows); print('at',st['frame'],C.abs_x(st),st['y'],st['room'])
    en=C.Enforcer((hist+rows)[-1900:]); rr=[en.emit(w) for w in want]
    e.trace(True); e.run(rr)
    print(' | '.join(f"{i}:{'+'.join(r) or '-'} {C.abs_x(s)},{s['y']} r{s['room']}{' D' if s.get('dw') else ''}" for i,(r,s) in enumerate(zip(rr,e.last_trace))))
finally: e.close()
