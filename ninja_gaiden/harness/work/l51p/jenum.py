"""Tosser-1 body boost enumeration: base = D-variant legal rows, stop S (frames kept blank after the spawn, e.g. '22290-22291'),
then from frame J0 on: Right, A+Right at j (held h), Right; result: hit frame, first frame on y<=128 with X>=448 ('up'),
X at frame 22430. python work/l51p/jenum.py c "22290-22291=-" [j0 j1]"""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
c = int(sys.argv[1]); ovs = sys.argv[2]
j0, j1 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (22340, 22372)
ov = {}
for it in ovs.split(',') if ovs else []:
    k, v = it.split('='); k1, k2 = (k.split('-') + [k])[:2]
    for f in range(int(k1), int(k2) + 1): ov[f] = row(v)
END = 22440
def rows_for(j, h):
    want = []
    for f in range(22125, END + 1):
        if f < 22340:
            w = set(T(f))
            if 'Left' in w and 'Right' in w: w -= {'Left'}
            if f in (22289,): w = {'Right'}
            if f == 22126: w = {'Right'}
            if f == 22125: w = set()
        else:
            w = {'Right'}
            if j <= f < j + h: w = {'A', 'Right'}
        if f in ov: w = set(ov[f])
        want.append(tuple(sorted(w)))
    en = A.Enforcer([()] * 60); rr = [tuple(sorted(en.emit(w))) for w in want]
    return rr
fc = core(tas_mst(22124)); fc.poke(0xBF, (c - 1) % 256); fc.save('b'); fc._ka_slot = 'b'
names, cands = [], []
for j in range(j0, j1):
    for h in (2, 6, 12, 20):
        r = rows_for(j, h)
        if legal_ok(r, [()] * 60): continue
        names.append((j, h)); cands.append(r)
res = fc.run_batch('b', cands, record='all')
out = []
for nm, r in zip(names, res):
    hp = 16; hit = None; up = None
    for i, s in enumerate(r.states):
        f = 22125 + i; X, y = RXY(s)
        if s['hp65'] != hp and hit is None: hit = (f, X, y); hp = s['hp65']
        if up is None and f > 22340 and y <= 128 and X >= 448 and s['hp65'] > 0: up = (f, X, y)
    Xe, ye = RXY(r.states[-1])
    out.append((-(Xe), nm, hit, up, (Xe, ye, r.states[-1]['hp65'])))
out.sort()
for o in out[:25]: print('jump', o[1], 'hit', o[2], 'up', o[3], 'end@', END, o[4])
fc.close()
