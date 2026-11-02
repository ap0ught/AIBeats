"""room-15 cycle from A at 16422 with one long cycle (6/7 f) at index i (to dodge NesHawk misreads), then departure grid.
python work/r15/g5.py <out json> [a1]"""
import sys, json; sys.path.insert(0, 'work/r15')
from rlib import *
base = C.rows_of('work/r15/st_topA.txt'); S = 16400; pre = base[:S - F0]
outj = sys.argv[1]; A1 = int(sys.argv[2]) if len(sys.argv) > 2 else 16422
pat = seq('A+Left+Up,A+Left,Right,Right+Up,Right+Up')
def cyc_rows(starts, end):
    r = {}
    for k, a in enumerate(starts):
        nxt = starts[k + 1] if k + 1 < len(starts) else end
        for f in range(a, nxt):
            i = f - a
            r[f] = pat[i] if i < 5 else ('Right', 'Up')
    return r
cands = []; desc = []
variants = [()]
for i in range(0, 4):
    for g in (1, 2):
        variants.append((i, g))
for var in variants:
    starts = [A1]
    while starts[-1] < 16500:
        k = len(starts) - 1
        L5 = 5 + (var[1] if var and var[0] == k else 0)
        starts.append(starts[-1] + L5)
    cr = cyc_rows(starts, 16505)
    r = [('A', 'Left')]
    for fr in range(16402, A1):
        x = pat[(fr - A1) % 5]
        if fr < 16405 and 'A' in x: x = ('Right',)
        r.append(x)
    r += [cr[f] for f in range(A1, 16500)]
    for dep in [a for a in starts if 16465 <= a <= 16482]:
        for s in range(dep + 2, dep + 6):
            for k in (5, 7, 8):
                for j in range(dep + 10, dep + 15):
                    rr = list(r[:dep + 1 - S]); rr.append(('A', 'Left'))
                    rr += [('Left',)] * k
                    while S + len(rr) < j - 1: rr.append(('Right',))
                    rr += [('A', 'Right')] * 2 + [('Right',)] * 30
                    for fr in (s, s + 1):
                        if 'A' in rr[fr - S - 1]: break
                        rr[fr - S - 1] = ('B', 'Down')
                    if legal(pre, rr): cands.append(rr); desc.append((var, dep, s, k, j))
print('cands', len(cands), flush=True)
t = time.time(); res = run(cands, pre)
print('time', round(time.time() - t), flush=True)
out = []
for i, st in enumerate(res):
    v = None
    for s_ in st:
        if s_['hp'] == 0 or s_['item'] != 133: break
        if s_['room'] == 15 and s_['X'] >= 140 and s_['y'] <= 100: v = round(s_['frame'] - (s_['X'] - 140) / 1.5, 1); break
    out.append((v, desc[i], st[-1]['ninpo'], st[-1]['hp']))
out.sort(key=lambda t: (t[0] is None, t[0] or 0))
for o in out[:25]: print(o, flush=True)
json.dump({'out': out, 'cands': {str(desc[i]): cands[i] for i in range(len(cands))}}, open(outj, 'w'))
close()
