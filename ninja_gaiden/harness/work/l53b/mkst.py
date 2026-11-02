"""l53b: play rows files in order from a .mst and save .mst at the end (pad blanks to reach a frame).
python work/l53b/mkst.py <mst> F0 out.mst END rows1 [rows2 ...]  (rows padded with blanks to END)"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
src, F0, out, END = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
rows = []
for p in sys.argv[5:]: rows += [row(l.strip()) for l in open(p) if l.strip() and not l.startswith('#')]
assert F0 + len(rows) <= END, (F0 + len(rows), END)
rows += [()] * (END - F0 - len(rows))
fc = core(src); fc.step(rows, record='last'); m = fc.ram()
print(END, XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'BF', m[0xBF], '5C', m[0x5C])
fc.save('a'); fc.save_file('a', out, END); fc.close()
