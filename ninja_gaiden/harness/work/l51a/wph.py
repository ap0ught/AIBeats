"""Wall-bird phase by waiting: prefix (climb) rows + TAS rows at lag L0 to TAS frame tw, then k rows of W (blank/Left), then
TAS rows at lag L0+k to TAS END. Reports when Ryu reaches X>=2760 y<=100 (our frame, TAS-eq), hits, death.
python -u work/l51a/wph.py <prefix> <L0> <tw list a:b:s> <k list a:b:s> <W: -|L> [END]"""
import sys; sys.path.insert(0, 'work/l51a')
from rep import *
pre = rows_file(sys.argv[1]); L0 = int(sys.argv[2])
rg = lambda s: range(*[int(x) for x in s.split(':')])
TW = rg(sys.argv[3]); KS = rg(sys.argv[4]); W = () if sys.argv[5] == '-' else ('Left',)
END = int(sys.argv[6]) if len(sys.argv) > 6 else 23990
H = hist()
fc, _k = start_core(pre); fc.step(pre[_k:], record='last'); fc.save('p'); fc._ka_slot = 'p'
F0 = CTL + len(pre)  # first new frame
def want(t1, t2):
    out = []
    for t in range(t1, t2 + 1):
        w = set(T(t))
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
        if t in (23279, 23280): w = {'A', 'Right'}
        out.append(w)
    return out
for tw in TW:
    for k in KS:
        t0 = F0 - L0
        w = want(t0, tw - 1) + [set(W)] * k + want(tw, END)
        en = A.Enforcer(H[-1900:] + pre); rows = [tuple(sorted(en.emit(x))) for x in w]
        fc.load('p'); _, recs, _ = fc.step(rows, record='all')
        hp = recs[0]['hp65']; hits = []; goal = None; dead = None
        for i, s in enumerate(recs):
            f = F0 + i; X, y = RXY(s)
            if s['hp65'] < hp: hits.append((f, f - L0 - k, X, y, s['hp65']))
            hp = s['hp65']
            if y >= 232 or hp == 0: dead = (f, X); break
            if X >= 2760 and y <= 100: goal = (f, f - L0 - k); break
        print('tw', tw, 'k', k, 'goal', goal, 'dead', dead, 'hits', hits[:4], 'np', recs[i]['np64'], flush=True)
