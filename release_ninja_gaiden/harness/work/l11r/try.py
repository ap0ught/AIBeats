"""python work/l11r/try.py N 'spec1' 'spec2' ... [--every 3] : from intro + BASE[:N], run each spec (legalized), print path."""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'work/l11r')
from lib import *
a = sys.argv[1:]
ev = 3
if '--every' in a:
    i = a.index('--every'); ev = int(a[i + 1]); del a[i:i + 2]
pre = sys.argv and a[0]
if pre.endswith('.txt'):
    base = C.rows_of(pre); a = a[1:]
else:
    base = BASE
N = int(a[0])
assert N <= len(base), (N, len(base))
assert N <= len(base), (N, len(base))
hist = INTRO + base[:N]
fc = F.FastCore(boot_rows=hist)
fc.save('s')
for sp in a[1:]:
    rows = enforce(hist, spec_rows(sp))
    r = fc.run_batch('s', [rows], record='all', record_ram=False)[0]
    print('SPEC', sp)
    line = []
    for j, s in enumerate(r.states):
        if j % ev == 0 or j == len(r.states) - 1:
            line.append(f"{N+j+1}:{fmt(s)}h{s['hp']}n{s['ninpo']}")
    print(' '.join(line))
fc.close()
