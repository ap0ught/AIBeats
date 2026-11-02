"""l53a: same legalized TAS room-28 rows (27,036..27,120) from my room-28 arrival state and from the TAS state 27,035; first X/y difference.
python work/l53a/cmp28.py <my mst (after room change + 22)>"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
hist = [T(f) for f in range(26886, 27036)]
rows = legalize_tas(27036, 27120, [tuple(sorted(set(r) - ({'Left'} if {'Left','Right'} <= set(r) else set()) - ({'Up','Down'} if {'Up','Down'} <= set(r) else set()))) for r in hist])
a = core(sys.argv[1]); _, sa, _ = a.step(rows, record='all'); a.close()
b = core_at(27035); b.poke(0x65, 3); _, sb, _ = b.step(rows, record='all'); b.close()
d = [(27036 + i, RXY(x), RXY(y)) for i, (x, y) in enumerate(zip(sa, sb)) if RXY(x) != RXY(y)]
print('rows', len(rows), 'first diffs', d[:5])
print('end mine', RXY(sa[-1]), sa[-1]['hp65'], 'TAS-state', RXY(sb[-1]), sb[-1]['hp65'])
