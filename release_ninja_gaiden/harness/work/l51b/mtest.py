"""Macro tests: python work/l51b/mtest.py <mst> F0 <hist> 'spec1' 'spec2' ... ; spec = 'R:5 AR:2 L:6 ...' (A B L R U D letters, '-' blank)
prints per frame trace for the first spec with --trace, else summary (first y<=100 frame, hits, final X,y)."""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
a = sys.argv[1:]
TR = '--trace' in a
if TR: a.remove('--trace')
mst, F0, H = a[0], int(a[1]), a[2]
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
AB = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}
def parse(sp):
    rows = []
    for tok in sp.split():
        k, n = tok.split(':'); r = () if k == '-' else tuple(sorted(AB[c] for c in k))
        rows += [r] * int(n)
    return rows
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
for sp in a[3:]:
    rows = parse(sp); lg = legal_ok(rows, hist)
    fc.load('b'); _, recs, _ = fc.step(rows, record='all')
    top = next((F0 + 1 + i for i, r in enumerate(recs) if r['y8a'] <= 100 and RXY(r)[0] >= 1505), None)
    print(f'{sp!r}: legal {lg or "ok"} top {top} hits {trackhits(recs, F0 + 1)} end {RXY(recs[-1])}', flush=True)
    if TR:
        for i, r in enumerate(recs): print('  ', F0 + 1 + i, RXY(r), 'an', r['anim'], 'co', r['coll'], 'rf', hex(r['rf84']), 'hp', r['hp65'])
fc.close()
