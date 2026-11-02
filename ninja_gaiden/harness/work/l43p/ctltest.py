"""4-3 start: does input before the control row 19,299 move Ryu? (Mesen, k932a chain)"""
import sys; sys.path.insert(0, 'work/l43p')
from lib import *
Pw = C.rows_of(CHAIN_POW)
fc = core('states/mesen/l42a_k18932.mst')
fc.step(Pw[18932:19250], record='last'); fc.save('b')
for tag, k, extra in (('blank', None, None), ('Left from 19297', 19297, None), ('Left from 19290', 19290, None), ('Left from 19260', 19260, None),
                      ('Left+A from 19295', 19295, 'A'), ('Right from 19290', 19290, 'R')):
    rows = []
    for f in range(19251, 19306):
        r = set()
        if k and f >= k and f < 19299: r.add('Right' if extra == 'R' else 'Left')
        if extra == 'A' and k and 19295 <= f < 19297: r.add('A')
        if f >= 19299: r.add('Left')
        rows.append(tuple(sorted(r)))
    fc.load('b'); _, recs, _ = fc.step(rows, record='all')
    print(f'{tag:20s}', ' '.join(f"{19251+i}:{XY(r)[0]},{XY(r)[1]}" for i, r in enumerate(recs) if 19296 <= 19251 + i <= 19303))
fc.close()
