"""Heart-down row per bf after a pod line (Mesen): rows file + blank; heart down = first row with $487 == 168."""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
FLD['pst6'] = 0x42E
rows = rows_of(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 250
rows = rows + [()] * (n - len(rows))
fc = core65()
out = {}
for v in range(256):
    fc.load('c0'); fc.poke(0xBF, v); fc.save('x')
    st = fc.run_batch('x', [rows], record='all')[0].states
    hd = next((i + 1 for i, s in enumerate(st) if s['ey7'] == 168), None)
    pk = next((i + 1 for i, s in enumerate(st) if s['t6'] != 38 or s['pst6'] == 60), None)
    sp = [i + 1 for i in range(1, len(st)) for j in range(8) if st[i][f't{j}'] == 41 and st[i - 1][f't{j}'] != 41]
    hpl = next((i + 1 for i in range(1, len(st)) if st[i]['hp65'] < st[i-1]['hp65']), None)
    out[v] = hd
    print(v, 'pod', pk, 'heart', hd, 'first hit', hpl, 'spawns', sp[:8], flush=True)
from collections import Counter
print('hist', sorted(Counter(out.values()).items(), key=lambda q: (q[0] is None, q[0] or 0)))
fc.close()
