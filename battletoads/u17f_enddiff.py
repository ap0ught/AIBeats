"""Final builder probe: the Queen segment from two entry bookmarks; which RAM bytes differ after the last input, and on which frames
the dice / the frame counters differ.   python u17f_enddiff.py <segment> <bookmark A> <bookmark B>   No memory writes."""
import sys
from u17f_lib import *
name, A, B = sys.argv[1], sys.argv[2], sys.argv[3]
sg = seg(name)
e = BizHawk(log_name="u17f_enddiff.log")
runs = []
for bm in (A, B):
    e.load(bm)
    rows = []
    for b in sg:
        e.step(bt(b), 1)
        rows.append(bytes(e.ram(0, 0x800)))
    runs.append(rows)
a, b = runs
d = diff(a[-1], b[-1], skip_stack=False)
print(f"{name}: end RAM from {A} vs from {B}: {len(d)} bytes differ: {[(hex(i), a[-1][i], b[-1][i]) for i in d]}")
per = {}
for n in range(len(sg)):
    for i in diff(a[n], b[n]):
        per.setdefault(i, []).append(n + 1)
print("bytes that differ on any frame (stack page aside): " + ", ".join(f"{hex(i)}: {len(v)} frames ({v[0]}..{v[-1]})" for i, v in sorted(per.items())))
e.close()
