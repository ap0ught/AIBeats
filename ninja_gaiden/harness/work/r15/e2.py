import sys; sys.path.insert(0, 'work/r15')
from rlib import *
base = C.rows_of('work/l41/c2a.txt')
S = 16466; pre = base[:S - F0]
cyc = seq('Right,Right+Up,Right+Up,A+Left+Up,A+Left') * 12   # 16467.. ; A+L+U at 16470,16475,...
def dep(a, k, tail):
    n = a - S + 1   # rows through the A+Left after A+L+U at frame a  (a+1 = A+Left)
    r = cyc[:a + 1 - S] + [('A', 'Left')] if False else cyc[:a + 2 - S - 1 + 1]
    r = cyc[:(a + 1) - S]          # frames S+1..a+1  (a+1 = A+Left)
    r += [('Left',)] * k + seq(tail)
    return r
tests = [
 ('a16475 k3 -', dep(16475, 3, '-*6,A+Right*2,Right*40')),
 ('a16475 k6 -', dep(16475, 6, '-*4,A+Right*2,Right*40')),
 ('a16475 k2 slash', dep(16475, 2, 'Down+B+Left*2,-*4,A+Right*2,Right*40')),
 ('a16470 k6 -', dep(16470, 6, '-*4,A+Right*2,Right*40')),
 ('a16480 k3 -', dep(16480, 3, '-*6,A+Right*2,Right*40')),
]
res = run([t[1] for t in tests], pre, n=1)
for (nm, rr), st in zip(tests, res):
    print('==', nm, legal(pre, rr))
    for s, r in zip(st, rr):
        if s['frame'] >= 16468: print(fmt(s, r))
close()
