"""room-15 departure variants around 16475 (direct A+Left wall jump), slash + jump grid. metric: X>=140 and y<=100"""
import sys, json; sys.path.insert(0, 'work/r15')
from rlib import *
base = C.rows_of('work/r15/t_g2a.txt'); S = 16466; pre = base[:S - F0]
head = seq('Right,Right+Up,Right+Up,A+Left+Up,A+Left,Right,Right+Up,Right+Up')   # 16467-16474
cands = []; desc = []
for dep in ('A+Left', 'A+Left+Up', 'A'):
    for d1 in ('Left', '', 'Right'):
        for s in [0] + list(range(16476, 16483)):
            for sdir in ('', 'Left', 'Right'):
                if not s and sdir: continue
                for j in range(16482, 16492):
                    r = list(head) + [R(dep)] * 2          # 16475-16476
                    while F0 + len(pre) + len(r) < j - 1: r.append(R(d1) if d1 else ())
                    r += [('A', 'Right')] * 2 + [('Right',)] * 30
                    if s:
                        for f in (s, s + 1):
                            i = f - S - 1
                            if 'A' in r[i]: break
                            r[i] = tuple(sorted({'Down', 'B'} | ({sdir} if sdir else set())))
                    if legal(pre, r): cands.append(r); desc.append((dep, d1, s, sdir, j))
print('cands', len(cands), flush=True)
t = time.time(); res = run(cands, pre)
print('time', round(time.time() - t), flush=True)
out = []
for i, st in enumerate(res):
    v = None
    for s_ in st:
        if s_['hp'] == 0 or s_['item'] != 133: break
        if s_['room'] == 15 and s_['X'] >= 140 and s_['y'] <= 100: v = s_['frame'] - (s_['X'] - 140) / 1.5; break
    out.append((v, desc[i], st[-1]['ninpo'], st[-1]['hp']))
out.sort(key=lambda t: (t[0] is None, t[0] or 0))
for o in out[:30]: print(o, flush=True)
json.dump(out, open('work/r15/g3.json', 'w'))
close()
