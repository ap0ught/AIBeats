"""room-15 cycle phase at the room appear (rows 16,401-16,421 are transition rows), then departure/slash/jump grid."""
import sys, json; sys.path.insert(0, 'work/r15')
from rlib import *
base = C.rows_of('work/r15/st_topA.txt'); S = 16400; pre = base[:S - F0]
pat = seq('A+Left+Up,A+Left,Right,Right+Up,Right+Up')
cands = []; desc = []
for a1 in range(16420, 16427):          # first room-15 A+L+U frame
    for alt in (0, 1):
        r = [('A', 'Left')]                 # 16401 (hold of c2's 16400 A)
        # transition filler with legal A presses ending >= 5 before a1
        for fr in range(16402, a1):
            x = pat[(fr - a1) % 5]
            if fr < 16405 and 'A' in x: x = ('Right', 'Up') if alt else ('Right',)
            r.append(x)
        cyc = [pat[(fr - a1) % 5] for fr in range(a1, 16500)]
        r += cyc
        # find A+L+U frames and y via a first pass later; enumerate departures from frames with A+L+U in 16465..16482
        for dep in range(16465, 16483):
            if pat[(dep - a1) % 5] != ('A', 'Left', 'Up'): continue
            for s in range(dep + 2, dep + 6):
              for k in (0, 3, 5, 7, 8):
                for j in range(dep + 10, dep + 15):
                    rr = list(r[:dep + 1 - S])         # through the A+L+U at dep
                    rr.append(('A', 'Left'))           # dep+1
                    rr += [('Left',)] * k
                    while S + len(rr) < j - 1: rr.append(('Right',))
                    rr += [('A', 'Right')] * 2 + [('Right',)] * 30
                    for fr in (s, s + 1):
                        if 'A' in rr[fr - S - 1]: break
                        rr[fr - S - 1] = ('B', 'Down')
                    if legal(pre, rr): cands.append(rr); desc.append((a1, alt, dep, s, k, j))
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
for o in out[:30]: print(o, flush=True)
json.dump({'out': out, 'cands': {str(desc[i]): cands[i] for i in range(len(cands))}}, open('work/r15/g4.json', 'w'))
close()
