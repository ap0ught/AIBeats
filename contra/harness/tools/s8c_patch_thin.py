"""One-off patch: bursts accepted as a PARTIAL repair (the failure only moves later) are thinned too.
utf-8, temp file then rename."""
import os
from pathlib import Path
p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s8.py"
s = p.read_text(encoding="utf-8")
reps = [
("""        if ok and demand and len(c["fires"]) > len(ov["fires"]):
            # rule v2: a burst that works is thinned: wider gaps between its volleys, half of it, single
            # volleys - whatever still gives the same progress with fewer presses
""", """        if (ok or fi > f + 20) and demand and len(c["fires"]) > len(ov["fires"]):
            # rule v2: a burst that works is thinned: wider gaps between its volleys, half of it, single
            # volleys - whatever still gives the same progress with fewer presses (for a burst that only moves
            # the failure later: whatever moves it at least as far)
"""),
("""                    if fi2 is not None and not (gi is not None and gi <= fi2):
                        continue
                    nb2 = b_starts(rows_c)
                    if progress(t[-1]) >= prog and nb2 < nb0 and (pick is None or nb2 < pick[0]):
                        pick = (nb2, o)
""", """                    if gi is not None and (fi2 is None or gi <= fi2):
                        fi2 = None
                    if ok and (fi2 is not None or progress(t[-1]) < prog):
                        continue
                    if not ok and fi2 is not None and fi2 < fi:
                        continue
                    nb2 = b_starts(rows_c)
                    if nb2 < nb0 and (pick is None or nb2 < pick[0]):
                        pick = (nb2, o)
"""),
]
for a, b in reps:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(tmp, p)
print("patched")
