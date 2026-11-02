"""l53a: Mesen state of the l52b e1 chain before the 5-3 control row: l52b_e1_26995.mst + e1 rows 26,996..F-1.
python work/l53a/mke1.py <poweron file> <F (5-3 control row)> <src mst> <src frame> <out tag>
Saves states/mesen/l53a_<tag>_<F-1>.mst and _<F>.mst (after row F)."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
pf, F, src, sf, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]
L = [l.rstrip('\n') for l in open(pf)]
rows = [row(l.strip()) for l in L if not l.startswith('#')]
fc = core(src)
seg = rows[sf:F - 1]          # rows sf+1 .. F-1 (row k = rows[k-1])
fc.step(seg, record='last')
fc.save('x'); open(f'states/mesen/l53a_{tag}_{F-1}.mst', 'wb').write(fc.get('x')) if hasattr(fc, 'get') else None
r = fc.ram(); print('after', F - 1, XY(r), 'hp', r[0x65], 'np', r[0x64], 'it', r[0xC9], 'BF', r[0xBF], 'rm', r[0x6E])
fc.step([rows[F - 1]], record='last'); fc.save('y'); open(f'states/mesen/l53a_{tag}_{F}.mst', 'wb').write(fc.get('y'))
r = fc.ram(); print('after', F, rows[F-1], XY(r), 'hp', r[0x65], 'np', r[0x64], 'BF', r[0xBF])
fc.close()
