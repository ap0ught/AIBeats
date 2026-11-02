"""Room-exit damage boosts (TAS launches into rooms 19 / 20): legalized TAS rows from a TAS state vs the TAS itself.
python work/l43p/boost.py <state frame> <last row>"""
import sys; sys.path.insert(0, 'work/l43p')
from lib import *
s, e = int(sys.argv[1]), int(sys.argv[2])
rows = legalize_tas(s + 1, e, [()] * 60)
print('legal (fresh history):', legal_ok(rows, [()] * 60) or 'PASS')
fc = core(tas_mst(s))
_, recs, _ = fc.step(rows, record='all'); fc.close()
first = None
for i, r in enumerate(recs):
    f = s + 1 + i
    m = TM(f); X, y = XY(r); tX, ty = XY(m)
    same = (X, y, r['hp65'], r['room6e']) == (tX, ty, m[0x65], m[0x6E])
    if not same and first is None: first = f
    if not same or i % 4 == 0 or P(rows[i]) != P(T(f)):
        print(f, 'ours', P(rows[i]), 'TAS', P(T(f)), '| rm', r['room6e'], 'X', X, 'y', y, 'hp', r['hp65'], 'vy', r['vy'], 'rf', hex(r['rf84']),
              '|| TAS rm', m[0x6E], 'X', tX, 'y', ty, 'hp', m[0x65], '' if same else 'DIFF')
print('first divergence', first)
