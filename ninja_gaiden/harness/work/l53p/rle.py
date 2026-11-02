"""TAS 5-1 rows run-length with flags (LR / UD / 1f = a press held 1 frame / P<5 = new press < 5 f after the last press of that button, R1 = released 1 f).
python work/l53p/rle.py > work/l51p/tas51_rows_rle.txt"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l53p')
import a56_common as A
from lib0 import *
TR = A.tas_rows()
def T(f): return frozenset(TR[f - 1])
F0, F1 = 26600, 29270
last_press = {}; prevset = frozenset()
runs = []
for f in range(F0, F1):
    s = T(f); fl = []
    if 'Left' in s and 'Right' in s: fl.append('LR')
    if 'Up' in s and 'Down' in s: fl.append('UD')
    for b in s - prevset:
        if b in last_press and f - last_press[b] < 5: fl.append(f'P{f-last_press[b]}{b[0]}')
        last_press[b] = f
        if b not in T(f + 1): fl.append(f'1f{b[0]}')
    for b in prevset - s:
        if b in T(f + 1): fl.append(f'R1{b[0]}')
    m = TM(f) if f > TF1 else None
    pos = XY(m) + (m[0x65],) if m else None
    if runs and runs[-1][1] == s and not fl:
        runs[-1][3] = f
    else:
        runs.append([f, s, fl, f, pos])
    prevset = s
for f, s, fl, fe, pos in runs:
    print(f'{f}-{fe} ({fe-f+1:3d}) {"+".join(sorted(s)) or "-":20s} {" ".join(fl):16s} X,y,hp {pos}')
