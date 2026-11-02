import sys; sys.path.insert(0, 'work/r15')
from rlib import *
base = C.rows_of('work/l41/c2a.txt')
S = 16466; pre = base[:S - F0]
cands = {
 'cycle': seq('Right,Right+Up,Right+Up,A+Left+Up,A+Left') * 12,
 'upright': seq('Right+Up*60'),
 'up': seq('Up*60'),
}
names = list(cands)
res = run([cands[k] for k in names], pre, n=1)
for k, st in zip(names, res):
    print('==', k, legal(pre, cands[k]))
    for s, r in zip(st, cands[k]): print(fmt(s, r))
close()
