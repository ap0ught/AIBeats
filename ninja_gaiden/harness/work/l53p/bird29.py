"""Room-29 exit with a BIRD boost: from TAS state F0 (Ryu on the pillar top), wait w frames, then approach rows
(Left a, A+Left x2, Left ...) and idle/Left; exit = room 30. The bird (type 11) spawns ~27898 by scroll and homes on Ryu.
python work/l53p/bird29.py [F0=27880] [--wmax 80] [--room 30]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
WMAX = opt('--wmax', 80); RM = opt('--room', 30)
F0 = int(a[0]) if a else 27880
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
L, AL, R = 0x02, 0x82, 0x01
X0 = tas_xy(F0)[0]
cands = []; meta = []
for w in range(WMAX + 1):
    for pre in range(0, 16, 2):          # walk left 'pre' frames before the jump
        for tail in (0, L):
            cands.append([0] * w + [L] * pre + [AL, AL] + [L] * 14 + [tail] * 80); meta.append((w, pre, tail))
res = []
for i in range(0, len(cands), 64):
    rr = fc.run_batch('b', cands[i:i+64], record='all')
    for (w, pre, tail), r in zip(meta[i:i+64], rr):
        st = r.states; hits = []; ex = None
        for j, s in enumerate(st):
            if j and s['hp65'] < st[j-1]['hp65']: hits.append((F0 + 1 + j, RXY(st[j-1])))
            if s['room6e'] == RM: ex = F0 + 1 + j; break
        if ex: res.append((ex, w, pre, tail, hits[:2]))
        elif hits: print('hit-no-exit', w, pre, tail, hits[:2], RXY(st[-1]), flush=True)
res.sort(); print('EXITS', len(res), res[:15])
fc.close()
