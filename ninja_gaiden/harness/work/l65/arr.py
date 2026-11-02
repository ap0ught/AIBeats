"""Real 6-5 arrivals from the TAS 6-4b tally (state 38,778): Start (2 f) on 38,779 + k, then blank; find the 6-5 control
(load = first $6D 21; control = load + 152) and diff the RAM at the checkpoint before the control row across k."""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
ks = list(range(0, 13))
base = core_at(38778); base.save('t0')
rams = {}
for k in ks:
    rows = [()] * k + [('Start',), ('Start',)] + [()] * 200
    base.load('t0')
    r = base.run_batch('t0', [rows], record='all')[0]
    st = r.states
    load = next(i for i, s in enumerate(st) if s['st6d'] == 21)   # index i -> frame 38779 + i
    ctl = 38779 + load + 152
    base.load('t0'); base.step(rows[:ctl - 1 - 38778])
    m = base.ram(); rams[k] = m
    print(k, 'load', 38779 + load, 'ctl', ctl, 'bf', m[0xBF], '3e', m[0x3E], '62', m[0x62], '63', m[0x63], flush=True)
ref = rams[0]
for k in ks[1:]:
    d = [(hex(a), ref[a], rams[k][a]) for a in range(2048) if ref[a] != rams[k][a] and not (0x100 <= a < 0x200)]
    print(k, d[:30])
