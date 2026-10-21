"""One-off patch: the wall search's second pass (a jump over the M item) only for the 24 lines that are furthest
on 130 rows after the kill. utf-8, temp file then rename."""
import os
from pathlib import Path
p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s8.py"
s = p.read_text(encoding="utf-8")
reps = [
("""                out_.append((fi is None and not t[-1]["jump"] and not t[-1]["edge"],
                             hpos(t[-1]) if fi is None else 0, c, fi))
            return out_
""", """                out_.append((fi is None and not t[-1]["jump"] and not t[-1]["edge"],
                             hpos(t[-1]) if fi is None else 0, c, fi, hpos(t[min(len(t) - 1, 130)])))
            return out_
"""),
("""            c2 = [ov_add(c, jumps=ck.i + fi - q) for _ok, _p, c, fi in sc[::2] if fi is not None and fi > 20
                  for q in (2, 4, 7, 11)]
""", """            top = sorted((z for z in sc if z[3] is not None and z[3] > 20), key=lambda z: -z[4])[:24]
            c2 = [ov_add(c, jumps=ck.i + fi - q) for _ok, _p, c, fi, _p130 in top for q in (2, 4, 7, 11)]
"""),
]
for a, b in reps:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(tmp, p)
print("patched")
