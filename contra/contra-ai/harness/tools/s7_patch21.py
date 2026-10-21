"""Second-pass patch 21: the door grid reports why its attempts failed."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''        try:
            n = boss_try(c, j1, ph, j2, band, ab, hover=hv)
        except Fail:
            r.frames_simulated += len(c.rows) - base["n"]
            return''', '''        try:
            n = boss_try(c, j1, ph, j2, band, ab, hover=hv)
        except Fail as ex:
            r.frames_simulated += len(c.rows) - base["n"]
            k = f"{str(ex)[:12]} after {len(c.rows) - base['n']} rows at x {c.f['x']}"
            why[k] = why.get(k, 0) + 1
            return''')
rep('''    best = None
    tried = 0
    seen = set()

    def run(par):''', '''    best = None
    tried = 0
    seen = set()
    why = {}

    def run(par):''')
rep('''            raise Stuck("door: no scripted fight worked")''',
    '''            raise Stuck(f"door: no scripted fight worked: {why}")''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
