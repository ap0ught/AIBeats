"""Second-pass patch 17: boss_try gets `hover`: once on the ground at screen x >= hover Bill keeps his place
(up-forward volley for two frames, two frames Left, one still) instead of walking on to the cap, where the
up-forward volleys do less damage."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('def boss_try(c, j1, phase, j2=None, band=(112, 144), above="Down", up_s=60, limit=330, log=None):',
    'def boss_try(c, j1, phase, j2=None, band=(112, 144), above="Down", up_s=60, limit=330, log=None, hover=None):')
rep('''            elif s >= up_s:
                want.add("Up")
            s += 1''', '''            elif s >= up_s:
                want.add("Up")
            if hover is not None and g and "A" not in want and f["x"] >= hover:
                k = (t - phase) % 5
                if k in (0, 1):
                    want = {"Up", "Right"} | ({"B"} if "B" in want else set())
                elif k in (2, 3):
                    want = {"Left"} if f["x"] > hover else set()
                else:
                    want = set()
            s += 1''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
