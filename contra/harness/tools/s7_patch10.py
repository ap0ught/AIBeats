"""Second-pass patch 10: memoised procedures (the runner replays a Proc on every remedy trial that starts before
it), a distance-based limit in jump_choice, a smaller door grid."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''                _fr(c, want)
                n += 1
                if n > 500:
                    raise Fail("never arrived")
            return n
''', '''                _fr(c, want)
                n += 1
                if n > limit:
                    raise Fail("never arrived")
            return n
''')
rep('''        base = c.snap()
        best = None
        res = {}

        def play(jx):''', '''        base = c.snap()
        best = None
        res = {}
        limit = max(200, x_goal - c.f.wx + 200)

        def play(jx):''')
rep('''BOSS_GRID = [(j1, ph, j2, band, ab) for j1 in (None, 40, 44, 46, 48, 50, 52, 54, 56, 58, 60)''',
    '''BOSS_GRID = [(j1, ph, j2, band, ab) for j1 in (None, 40, 43, 45, 47, 50, 54, 58)''')
a = s.index("# ----------------------------------------------------------------------------- choose a jump point by trial")
new = '''# ----------------------------------------------------------------------------- memoised procedures
def memo(fn, label):
    """Wrap a runner Proc so that a second call from the same state replays the rows found the first time.
    (The runner replays the route, Procs included, for every remedy trial that starts before the Proc.)"""
    def proc(r):
        c = r.c
        store = r.__dict__.setdefault("_memo", {})
        f = c.f
        key = (label, len(c.rows), f["fc"], f["rng"], f.wx, f["x"], f["y"], f["barrier"], f.nbullets(),
               tuple(sorted(c.pr.held)), c.can("A"), c.can("B"), c.can("Start"))
        hit = store.get(key)
        if hit is not None:
            base = c.snap()
            sod = c.stop_on_death
            c.stop_on_death = False
            try:
                for row in hit["rows"]:
                    c.frame(row)
                    if c.f.dead:
                        break
            finally:
                c.stop_on_death = sod
            g = c.f
            if (g.wx, g["y"], g["fc"], g["rng"]) == hit["end"] and not g.dead:
                c.free(base)
                r.frames_simulated += len(hit["rows"])
                r.user.update(hit["user"])
                r.marks.extend(hit["marks"])
                return
            c.restore(base)
            c.free(base)
        n0, m0 = len(c.rows), len(r.marks)
        u0 = dict(r.user)
        fn(r)
        g = c.f
        store[key] = {"rows": list(c.rows[n0:]), "end": (g.wx, g["y"], g["fc"], g["rng"]),
                      "user": {k: v for k, v in r.user.items() if u0.get(k) != v},
                      "marks": [(m[0], m[1] - n0) + tuple(m[2:]) for m in r.marks[m0:]], "n0": n0}
        store[key]["marks"] = list(r.marks[m0:])
    return proc


'''
s = s[:a] + new + s[a:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
import re
n = 0
out = []
for line in s.splitlines(keepends=True):
    m = re.search(r'Proc\((s7b\.[a-z0-9_]+(?:\(.*\))?), ("[^"]+")\)', line)
    if m and "memo(" not in line and "boss_proc if" not in line:
        line = line.replace(m.group(0), f"Proc(s7b.memo({m.group(1)}, {m.group(2)}), {m.group(2)})")
        n += 1
    out.append(line)
s = "".join(out)
old = 'Proc(boss_proc if p.get("boss_beam") else s7b.boss_proc2, "boss"),'
assert s.count(old) == 1
s = s.replace(old, 'Proc(boss_proc if p.get("boss_beam") else s7b.memo(s7b.boss_proc2, "boss"), "boss"),')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("wrapped", n)
