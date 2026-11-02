"""Trace stage rows from the 5-1 base: python work/l51a/tr.py <rows file> [every] [from] [to]"""
import sys; sys.path.insert(0, 'work/l51a')
from lib import *
rows = rows_file(sys.argv[1]); ev = int(sys.argv[2]) if len(sys.argv) > 2 else 20
a0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0; a1 = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
tr = trace(rows); prev = None
for i, t in enumerate(tr):
    f = t[0]
    k = (t[3], t[4], t[5], t[7], t[8])
    if (a0 <= f <= a1) and (i % ev == 0 or k != prev or i == len(tr) - 1):
        tf = f - LAG
        tx = XY(TM(tf)) if TF0 < tf <= TF0 + NF else None
        print(f, 'tas', tf, 'X,y', t[1], t[2], 'hp', t[3], 'np', t[4], 'it', t[5], 'bf', t[6], 'rm', t[7], 'st', t[8], 'TAS', tx, P(rows[i]))
    prev = k
