"""Final builder probe: where the page at the end of a segment begins.   python u17f_lv.py <segment>[@bookmark] ...
For each segment (replayed from its bookmark): every change of the level byte $10 and of the toad's health in its last 700
inputs, and the inputs there (run lengths).   -> logs/fix/u17f_lv.txt (appended).  No memory writes."""
import sys

from u17f_lib import *

e = BizHawk(log_name="u17f_lv.log")
f = open(FIX / "u17f_lv.txt", "a", encoding="utf-8")
for spec in sys.argv[1:]:
    name, _, bm = spec.partition("@")
    sj, sg = segj(name), seg(name)
    e.load(bm or sj["bookmark"])
    prev, ev = None, []
    for i, b in enumerate(sg):
        e.step(bt(b), 1)
        if i >= len(sg) - 700:
            m = e.ram(0, 0x800)
            cur = (m[0x10], m[0x51A], m[0x11])
            if cur != prev:
                ev.append((i + 1, cur))
            prev = cur
    s = f"{name} ({len(sg)} inputs from {bm or sj['bookmark']}): (inputs done, (level byte, health, lives)) changes in the last 700: {ev}"
    print(s, flush=True)
    f.write(s + "\n")
f.close()
e.close()
