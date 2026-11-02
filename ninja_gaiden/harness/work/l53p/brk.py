"""TAS 5-3 rule breaks grouped into spans: python work/l53p/brk.py -> spans of L+R / U+D (with room, X,y at start/end, hp)
and per-room counts of 1-frame holds / fast re-presses."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l53p')
import a56_common as A
from lib0 import *
TR = A.tas_rows()
def T(f): return frozenset(TR[f - 1])
F0, F1 = 26608, 29100
spans = []; cur = None
cnt = {}
last = {}; prev = frozenset()
for f in range(F0, F1 + 1):
    s = T(f); m = TM(f); rm = m[0x6E]
    k = ('LR' if {'Left','Right'} <= s else '') + ('UD' if {'Up','Down'} <= s else '')
    if k:
        if cur and cur[0] == k and cur[2] >= f - 3: cur[2] = f; cur[4] = (XY(m), m[0x65])
        else:
            cur = [k, f, f, rm, (XY(m), m[0x65]), (XY(m), m[0x65]), sorted(s)]; spans.append(cur)
    c = cnt.setdefault(rm, {'1f': 0, 'P<5': 0, 'R1': 0, 'LR': 0, 'UD': 0})
    if 'LR' in k: c['LR'] += 1
    if 'UD' in k: c['UD'] += 1
    for b in s - prev:
        if b in last and f - last[b] < 5: c['P<5'] += 1
        last[b] = f
        if b not in T(f + 1): c['1f'] += 1
    for b in prev - s:
        if b in T(f + 1): c['R1'] += 1
    prev = s
for k, a, b, rm, p0, p1, s in spans:
    print(f'{k:4s} {a}-{b} ({b-a+1:3d}) rm {rm} start {p0} end {p1} e.g. {"+".join(s)}')
for rm, c in sorted(cnt.items()): print('room', rm, c)
