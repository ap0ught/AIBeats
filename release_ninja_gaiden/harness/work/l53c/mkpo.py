"""l53c: power-on file = rows 1..F0 of <base poweron> (blank-padded) + my rows (from F0+1). python work/l53c/mkpo.py base.txt F0 mine.txt out.txt"""
import sys
sys.path.insert(0, '.')
from ng.inputs import read_inputs, write_inputs
base, F0, mine, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
b = list(read_inputs(base))[:F0]; b += [()] * (F0 - len(b))
m = [tuple(sorted(l.strip().split('+'))) if l.strip() not in ('-', '') else () for l in open(mine) if l.strip() and not l.startswith('#')]
rows = b + m
import inspect
try:
    write_inputs(out, rows, header=f'power-on: {base} rows 1-{F0} + l53c {mine}')
except TypeError:
    write_inputs(out, rows)
print(len(rows))
