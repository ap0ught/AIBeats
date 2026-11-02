"""Real 6-5 arrival after the r4k2 6-4b kill (not the TAS's): RAM at control-1 vs the TAS arrival (Start delay matched so bf is
comparable), to list every byte that differs."""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
r4 = rows_of('work/l63p/jq_r4k2_kill.txt')
fc = core_at(38086); fc.save('a')
r = fc.run_batch('a', [r4 + [()] * 700], record='all')[0]
st = r.states
K = next(i for i, s in enumerate(st) if s['boss'] == 0) + 1      # row number of the kill (1 = control)
T = st[K - 1]['t63']
print('kill row', K, 'frame', 38086 + K, 'T', T)
res = {}
for d in (0, 1, 2, 5):
    S = 38086 + K + 3 * T + 146 + d       # Start frame
    rows = r4[:K] + [()] * (S - 38087 - K) + [('Start',), ('Start',)] + [()] * 300
    r = fc.run_batch('a', [rows], record='all')[0]
    st = r.states
    idx = [i for i, s in enumerate(st) if s['st6d'] == 21]
    if not idx: print('Start', S, 'no load'); continue
    load = 38087 + idx[0]; ctl = load + 152
    fc.load('a'); fc.step(rows[:ctl - 1 - 38086]); m = fc.ram()
    res[d] = m
    print('Start', S, 'load', load, 'ctl', ctl, 'bf', m[0xBF], '3e', m[0x3E], '62', m[0x62], '63', m[0x63], 'hp', m[0x65], flush=True)
T0 = TM(38932)
for d, m in res.items():
    diff = [(hex(a), T0[a], m[a]) for a in range(2048) if T0[a] != m[a] and not (0x100 <= a < 0x300)]
    print(d, diff)
fc.close()
