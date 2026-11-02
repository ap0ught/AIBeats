"""show a candidate from rows file: python work/r15/show.py <stage rows> <from> <to>  (Mesen, prints per frame)"""
import sys; sys.path.insert(0, 'work/r15')
from rlib import *
rows = C.rows_of(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3])
pre = rows[:a - 1 - F0]
st = run([rows[a - 1 - F0:b - F0]], pre, n=1)[0]
for s, r in zip(st, rows[a - 1 - F0:b - F0]): print(fmt(s, r))
close()
