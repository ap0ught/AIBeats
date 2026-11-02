"""E1: chain 4-3 control state + legalized TAS rows (lag 340) for room 17 up to the climb; compare with the TAS."""
import sys; sys.path.insert(0, 'work/l43p')
from lib import *
H = hist_chain()
f2 = int(sys.argv[1]) if len(sys.argv) > 1 else 19037
rows = legalize_tas(18959, f2, H)
print('legal:', legal_ok(rows, H) or 'PASS')
fc = core(CHAIN_MST)
_, recs, _ = fc.step(rows, record='all')
for i, r in enumerate(recs):
    f = 18959 + i
    X, y = XY(r); tX, ty = tas_xy(f) if f > 18960 else (0, 0)
    if i % 5 == 0 or (X, y) != (tX, ty):
        print('tas row', f, 'chain', f + LAG, P(rows[i]), 'TAS', P(T(f)), 'X', X, 'y', y, '| TAS', tX, ty, 'hp', r['hp65'], 'BF', r['bf'])
fc.save('e'); fc.save_file('e', f'states/mesen/l43p_c{f2 + LAG}.mst', frame=f2 + LAG)
fc.close()
