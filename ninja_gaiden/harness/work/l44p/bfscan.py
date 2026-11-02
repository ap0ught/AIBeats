"""Arrival dependence: poke $BF (and/or $62, hp) at the 4-4 pre-control state, play a 4-4 row file + blank tail with a
2-f Start at stage row S, record kill / timer at kill / load / 5-1 control (first $62 change after the load) and the
enemy slots at the kill.   python work/l44p/bfscan.py <rows> <start row> <addr> <v1,v2,..|all> [--ref]"""
import sys
sys.path.insert(0, 'work/l44p')
from lib import *
rows = [tuple(sorted(r)) for r in C.rows_of(sys.argv[1])]
S = int(sys.argv[2]); addr = int(sys.argv[3], 0)
vals = range(256) if sys.argv[4] == 'all' else [int(x) for x in sys.argv[4].split(',')]
N = 800
w = list(rows[:S - 1]) + [()] * (N - len(rows[:S - 1]))
w[S - 1] = ('Start',); w[S] = ('Start',)
fc = core(PRE)
def ana(recs):
    kill = load = ctl = tk = None
    for i, r in enumerate(recs):
        if kill is None and r['bhp'] == 0 and r['st6d'] == 11: kill = i + 1; tk = r['t63']
        if load is None and r['st6d'] == 12: load = i + 1; t = r['t62']
        elif load and ctl is None and r['t62'] != t: ctl = i + 1
    return kill, tk, load, ctl
out = {}
for v in vals:
    fc.load('s'); fc.poke(addr, v); fc.save('v')
    res = fc.run_batch('v', [w], record='all', record_ram=False)
    recs = res[0].states
    k = ana(recs)
    # enemy snapshot at the kill row
    e = recs[k[0] - 1] if k[0] else None
    snap = tuple((e[f't{j}'],) for j in range(8)) if e else None
    out[v] = k
    print(v, 'kill', k[0], 'timer', k[1], 'load', k[2], '5-1 ctl', k[3], flush=True)
fc.close()
import collections
print('summary', collections.Counter(out.values()).most_common())
