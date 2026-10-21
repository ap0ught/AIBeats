"""Track C: a bookmark = <start bookmark> + the inputs of one or more segments.   python u17c_mkbm.py <out bookmark (C...)> <start bookmark> <segment> [...]"""
import sys
from u17c_lib import *
out, bm, segs = sys.argv[1], sys.argv[2], sys.argv[3:]
assert out.startswith("C")
e = BizHawk(log_name=f"u17c_mkbm_{out}.log")
e.load(bm)
n = 0
for s in segs:
    for b in seg(s):
        e.step(bt(b), 1)
        n += 1
e.save(out)
print(f"saved states/{out}.State = {bm} + {' '.join(segs)} ({n} inputs): {toad(e.ram(0, 0x800))}")
e.close()
