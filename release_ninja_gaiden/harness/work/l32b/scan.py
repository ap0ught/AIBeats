"""scan edits on a rows file. python work/l32b/scan.py <mst> <hist> <rows> <n> "<edits1>" "<edits2>" ...
edits: 'frame:ROW;frame:ROW' (our absolute frames). Each run: legalize (history) and play n rows; report."""
import sys
sys.path.insert(0, 'work/l32b'); sys.path.insert(0, '.')
import xp
from ng.solve import common as C, legality as L
from ng import fastcore as F
mst, hf, rf, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
H = C.rows_of(hf); f0 = len(H); base = C.rows_of(rf)[:n]
cands = []; names = []
for spec in sys.argv[5:]:
    want = list(base)
    for q in spec.split(';'):
        if not q: continue
        f, r = q.split(':'); want[int(f) - f0 - 1] = () if r == '-' else tuple(sorted(r.split('+')))
    en = L.Enforcer(H[-1900:]); cands.append([tuple(sorted(en.emit(w))) for w in want]); names.append(spec)
fc = F.FastCore(boot_rows=None, ticks=True, fields=xp.FLD); fc.put('s', open(mst, 'rb').read()); fc.load('s')
res = fc.run_batch('s', cands, record='all'); fc.close()
for nm, r in zip(names, res):
    st = r.states; s = st[-1]
    hit = next((f0 + i + 1 for i, q in enumerate(st) if q['hp'] < st[0]['hp']), None)
    print(f"{nm:40s} end X {C.abs_x(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} it {s['item']} st {s['stage']} firsthit {hit}")
