"""prefix (to P) + TAS rows at lag d to E; Mesen: stage-9 frame, hp/np/item. python work/l41/gend.py <prefix> <P> <d1,d2,..> [--out pattern]"""
import sys
sys.path.insert(0, 'work/l41')
from graft import *
pf, P = sys.argv[1], int(sys.argv[2]); ds = [int(q) for q in sys.argv[3].split(',')]
outp = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else ''
fc = core()
fc.save('c0')
for d in ds:
    rows = compose(pf, P, d, 16950)
    fc.load('c0'); _, recs, _ = fc.step(rows, record='all')
    e9 = next((F0 + i + 1 for i, s in enumerate(recs) if s['stage'] == 9), None)
    last = [s for s in recs if s['stage'] == 8][-1]
    hps = sorted(set((s['hp'], s['ninpo'], s['item']) for s in recs[P - F0:]))
    print('d', d, 'stage9', e9, 'end X', C.abs_x(last), last['y'], 'hp/np/item seen', hps[:6], flush=True)
    if outp: C.write_inputs(outp.replace('D', str(d)), rows[:(e9 - F0) if e9 else len(rows)], f'{pf}[:{P}] + TAS rows lag {d}')
fc.close()
