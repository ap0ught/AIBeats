"""Rebase onto k932b: Mesen state after row 19,295 / 19,296 from l42a_k18932 + k932b rows; test which row is the
first moving Left (4-3 control); replay pre2 rows from the new control row and compare with the k932a version."""
import sys; sys.path.insert(0, 'work/l43')
from lib import *
B = C.rows_of('logs/l42_w_k932b_poweron.inputs.txt')
fc = core('states/mesen/l42a_k18932.mst')
fc.step(B[18932:19294], record='last'); fc.save('p')       # after row 19,294
for k in (19295, 19296, 19297, 19298):
    rows = [() if f < k else ('Left',) for f in range(19295, 19302)]
    fc.load('p'); _, recs, _ = fc.step(rows, record='all')
    print('Left from', k, [(19295 + i, recs[i]['x']) for i in range(len(rows))])
fc.load('p'); fc.step(B[19294:19296], record='last'); fc.save('q')
fc.save_file('q', 'states/mesen/l43_k932b19296.mst', frame=19296)
r = fc.ram(); print('after 19,296: x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF])
fc.close()
