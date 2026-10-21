"""Final builder probe: a page frame by frame.  python u17f_pagetrace.py <bookmark> <segment> <frames> [pressless]
prints per input: index, input, level byte $10, health $51A, toad x, $0B after the frame; with 'pressless' the same frames with no input"""
import sys
from u17f_lib import *
bm, name, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
sg = seg(name)
e = BizHawk(log_name="u17f_pagetrace.log")
e.load(bm)
rows = []
for i in range(n):
    b = "" if len(sys.argv) > 4 else sg[i]
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    rows.append(f"{i}:{b or '-'}:{m[0x10]}/{m[0x51A]}/{m[0x3FD] | m[0x3EE] << 8}/{m[0x0B]}")
print(" ".join(rows))
e.close()
