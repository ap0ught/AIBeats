"""stage 1: departure grid from the ladder cycle; find branch landing frame. python work/r15/g1.py <base rows> <S> <out>"""
import sys, json; sys.path.insert(0, 'work/r15')
from rlib import *
bf, S, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
base = C.rows_of(bf); pre = base[:S - F0]
# continue the cycle in phase with the base: find the last A+Left+Up frame <= S in base
last = max(f for f in range(S - 30, S + 1) if base[f - F0 - 1] == ('A', 'Left', 'Up'))
pat = seq('A+Left+Up,A+Left,Right,Right+Up,Right+Up')
def cyc(f): return pat[(f - last) % 5]
cands = []; desc = []
for a in range(last, S + 40, 5):
    if a + 1 <= S: continue
    for k in range(0, 8):
        for d in ('Left', '', 'Right'):
            for s in [0] + list(range(a + 2, a + 10)):
                for sd in (('Left',), ()) if s else ((),):
                    r = [cyc(f) for f in range(S + 1, a + 2)]
                    r += [('Left',)] * k
                    while len(r) < 45 + (a - S): r.append(R(d) if d else ())
                    if s:
                        for f in (s, s + 1):
                            i = f - S - 1
                            if i < len(r): r[i] = tuple(sorted((set(r[i]) - {'Right', 'Left', 'Up'}) | {'Down', 'B'} | set(sd)))
                    if legal(pre, r): cands.append(r); desc.append((a, k, d, s, ''.join(sd)))
print('cands', len(cands), flush=True)
t = time.time(); res = run(cands, pre)
print('time', round(time.time() - t), flush=True)
rows = []
for i, st in enumerate(res):
    land = None; hp = None
    for s in st:
        if s['hp'] == 0: break
        if s['room'] == 15 and s['y'] == 128 and s['anim'] not in (5, 6, 7, 10, 11, 12):
            land = s['frame']; hp = s['hp']; break
    kill = all(s['t7'] != 11 or not (s['eact'] >> 7 & 1) for s in st[-3:])
    rows.append((land, desc[i], hp, kill, st[-1]['ninpo']))
rows.sort(key=lambda t: (t[0] is None, t[0] or 0))
for r in rows[:40]: print(r, flush=True)
json.dump({'S': S, 'base': bf, 'rows': rows, 'cands': [cands[desc.index(r[1])] for r in rows if r[0]][:300],
           'desc': [r[1] for r in rows if r[0]][:300]}, open(out, 'w'))
close()
