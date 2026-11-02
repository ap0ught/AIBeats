"""play a spec from a Mesen state: python work/l43p/try.py <mst> "<spec>" [f0]   spec tokens like L:5 AL:2 -:3 (A B U D L R)"""
import sys; sys.path.insert(0, 'work/l43p'); sys.path.insert(0, 'work/w21')
from lib import *
from try_ import spec_rows
mst, spec = sys.argv[1], sys.argv[2]; f0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
rows = spec_rows(spec)
fc = core(mst)
_, recs, _ = fc.step(rows, record='all'); fc.close()
for i, (s, r) in enumerate(zip(recs, rows)):
    X, y = XY(s)
    print(f0 + i + 1, P(r), 'rm', s['room6e'], 'X', X, 'y', y, 'vy', s['vy'], 'coll', s['coll'], 'anim', s['anim'], 'rf', hex(s['rf84']), 'hp', s['hp65'], 'np', s['np64'], 'en', hex(s['eact']))
