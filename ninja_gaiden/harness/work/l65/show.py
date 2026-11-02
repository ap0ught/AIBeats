"""python work/l65/show.py <bf> <rowsfile> [--every N] [--pre a=v,..] : per-frame view of the 6-5 fight from the TAS control state."""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
EV = int(opt('--every', '10')); PRE = opt('--pre', '')
pre = [(int(k, 0), int(v, 0)) for k, v in (p.split('=') for p in PRE.split(',') if p)]
bf = None if a[0] == '-' else int(a[0]); rows = rows_of(a[1])
fc = core65(bf, pre)
st = []
for k in range(0, len(rows), 100):
    st += fc.step(rows[k:k+100], record='all')[1]
fc.close()
prev = None
for i, s in enumerate(st):
    f = F0 + 1 + i
    ev = []
    if prev:
        if s['hp65'] != prev['hp65']: ev.append(f"HP {prev['hp65']}->{s['hp65']}")
        if s['boss'] != prev['boss']: ev.append(f"heart {s['boss']}")
        if s['eh6'] != prev['eh6'] and s['t6'] == 38: ev.append(f"pod {s['eh6']}")
        if s['st6d'] != prev['st6d'] or s['room6e'] != prev['room6e']: ev.append(f"STAGE {s['st6d']} room {s['room6e']}")
    if ev or (EV and i % EV == 0):
        print(f, i + 1, P(rows[i]), RXY(s), 'bf', s['bf'], 'T', s['t63'], s['t62'], ' '.join(ev), slots(s))
    prev = s
