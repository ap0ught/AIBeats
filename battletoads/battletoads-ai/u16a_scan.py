"""Chain A: banned-press scan of a route's input list.

    python u16a_scan.py <route> [segment names in order...]
        logs/<route>.inputs.txt (one line per frame; '#' lines are comments; buttons joined by '+' or ',')
    Counts Left+Right, Up+Down, Start (with the frames), frames with Select, unknown button names.  With the segment names
    the Start presses are attributed to the intro / each segment, and the file is compared with intro + those segments.
    The bridge drives controller 1 only, so nothing can be on controller 2.
"""
import sys

from u16a_lib import *

route, segs = sys.argv[1], sys.argv[2:]
lines = [l.rstrip("\n") for l in open(LOGS_DIR / f"{route}.inputs.txt") if not l.startswith("#")]
OK = {"Up", "Down", "Left", "Right", "Select", "Start", "B", "A"}
lr, ud, st, sel, unk = [], [], [], [], []
for f, l in enumerate(lines, 1):
    t = set(bt(l))
    if {"Left", "Right"} <= t:
        lr.append(f)
    if {"Up", "Down"} <= t:
        ud.append(f)
    if "Start" in t:
        st.append(f)
    if "Select" in t:
        sel.append(f)
    if t - OK:
        unk.append((f, l))
print(f"{route}: {len(lines)} frames; Left+Right {len(lr)} {lr[:10]}; Up+Down {len(ud)} {ud[:10]}; Start {len(st)}; frames with Select {len(sel)}; unknown buttons {len(unk)} {unk[:5]}")
if segs:
    want = route_inputs(segs)
    print(f"  file equals intro + {' '.join(segs)}: {[b.replace(',', '+') for b in lines] == want} ({len(want)} inputs)")
    bounds, off = [("intro", 1, 1917)], 1917
    for nm in segs:
        n = len(seg(nm))
        bounds.append((nm, off + 1, off + n))
        off += n
    for nm, a, b in bounds:
        s_here = [f for f in st if a <= f <= b]
        l_here = [f for f in sel if a <= f <= b]
        print(f"  {nm:16s} frames {a:6d}-{b:6d}: Start {len(s_here):2d} {('(' + str(s_here[0]) + '..' + str(s_here[-1]) + ')') if s_here else ''}  Select {len(l_here)}")
