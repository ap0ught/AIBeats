"""python work/l33/fix.py <tag> <rows in> <rows out>: append Enforcer-forced rows so the last presses meet min hold."""
import sys
sys.path.insert(0, 'work/l33')
from lib import CANDS, C, L
tag, fi, fo = sys.argv[1:4]
h = C.rows_of(CANDS[tag]['pow']); r = [tuple(sorted(x)) for x in C.rows_of(fi)]
en = L.Enforcer((h + r)[-1900:])
# replay to sync enforcer state
en = L.Enforcer(h[-1900:])
out = [tuple(sorted(en.emit(x))) for x in r]
assert out == r, 'rows not legal under the enforcer'
for _ in range(3):
    out.append(tuple(sorted(en.emit(()))))
C.write_inputs(fo, out, f'{fi} + enforcer tail')
chk = L.check(h + out); print('judge', chk['pass'])
