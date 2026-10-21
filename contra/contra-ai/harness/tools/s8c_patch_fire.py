"""One-off patch (rule v2, on-demand firing): long flat bursts among the first-level shots, and a burst that moves
the failure well away is taken before any jump is tried. utf-8, temp file then rename."""
import os
from pathlib import Path
p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s8.py"
s = p.read_text(encoding="utf-8")
reps = [
("""    for a, b in wins:
        for aim in (None, "Up", "Down"):
            add(a, b, aim)
    if level >= 1:
""", """    for a, b in wins:
        for aim in (None, "Up", "Down"):
            add(a, b, aim)
    if level == 0:
        # what the first run's constant mash did for free: flat fire from far out (thinned afterwards)
        for d in (100, 160, 240):
            add(D - d, D + 12, None)
    if level >= 1:
"""),
("""            if any(z[0] for z in scored):
                break
        cands = [None] * ncand
""", """            if any(z[0] for z in scored):
                break
            if demand and len(groups) > 1 and cands is groups[0] and max(z[1] for z in scored) > f + 40:
                break           # a shot moves the failure 40+ rows away: take it before a jump (a frame) is tried
        cands = [None] * ncand
"""),
]
for a, b in reps:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(tmp, p)
print("patched")
