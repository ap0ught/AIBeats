"""Real-chain Mesen states: power-on replay of the locked file to row 22,628 (5-1 control = row 22,629).
Saves states/mesen/l51b_real22628.mst and compares RAM with the TAS state 22,124 (TAS 5-1 control 22,125)."""
import sys, time
sys.path.insert(0, 'work/l51p')
from lib import *
B = C.rows_of('logs/l44p_r1920_c2_poweron.inputs.txt')
print('rows', len(B)); t = time.time()
fc = F.FastCore(boot_rows=B[:22628], ticks=True, fields=FLD)
print('boot', time.time() - t)
fc.save('r'); fc.save_file('r', 'states/mesen/l51b_real22628.mst', frame=22628)
r = fc.ram()
fc.put('t', open(tas_mst(22124), 'rb').read()); fc.load('t'); t_ = fc.ram()
d = [(hex(i), r[i], t_[i]) for i in range(2048) if r[i] != t_[i]]
print('diffs', len(d), d[:80])
fc.close()
