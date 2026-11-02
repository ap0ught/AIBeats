"""python work/l11r/mkseed.py N tag 'spec' [base rows file] : writes hist (intro+base[:N]) states/tmp/l11_<tag>_hist.inputs.txt,
Mesen state states/mesen/l11_<tag>.mst, seed rows states/tmp/l11_<tag>_seed.inputs.txt (spec applied after base[N:M])
spec may start with 'base:M' = copy base rows N..M first."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l11r')
from lib import *
N, tag, spec = int(sys.argv[1]), sys.argv[2], sys.argv[3]
base = C.rows_of(sys.argv[4]) if len(sys.argv) > 4 else BASE
assert N <= len(base), (N, len(base))
hist = INTRO + base[:N]
seed = []
toks = spec.split()
if toks and toks[0].startswith('base:'):
    M = int(toks[0][5:]); seed = list(base[N:M]); spec = ' '.join(toks[1:])
seed += spec_rows(spec)
C.write_inputs(f'states/tmp/l11_{tag}_hist.inputs.txt', hist, f'intro + 1-1 rows to frame {len(hist)}')
C.write_inputs(f'states/tmp/l11_{tag}_seed.inputs.txt', seed, f'seed from frame {len(hist)}')
fc = F.FastCore(boot_rows=hist)
fc.save('s'); fc.save_file('s', f'states/mesen/l11_{tag}.mst', frame=len(hist))
fc.close()
print('hist', len(hist), 'seed', len(seed))
