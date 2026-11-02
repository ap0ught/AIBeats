"""Play legalized TAS 3-1 rows from our 3-1 control; print divergence vs the TAS trace.
python work/l31alt/tasfol.py [n] [every]"""
import sys; sys.path.insert(0, 'work/l31alt')
from lib import *
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500; ev = int(sys.argv[2]) if len(sys.argv) > 2 else 10
TR = A.tas_rows(); TT = A.tas_trace()
want = [tuple(TR[TAS_CTL + i]) for i in range(n)]
rows = legal_after([], want)
fc = core()
for i, r in enumerate(rows):
    fc.step([r], record='last'); m = fc.ram(); t = TT[TAS_CTL + i + 1]
    tx = C.abs_x(t)
    if i % ev == 0 or m[0x65] != t['hp'] or m[0x6D] != 5:
        print(F0 + i + 1, 'in', '+'.join(r) or '-', 'X', X(m), 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], '| TAS X', tx, 'y', t['y'], 'hp', t['hp'], 'np', t['ninpo'], 'en', enemies(m))
    if m[0x6D] != 5 or m[0x65] < t['hp'] - 3: break
fc.close()
