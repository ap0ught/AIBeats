"""Second-pass patch 5: s7b.trio_proc (the three rising walls on the ledge 2656) + route change."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
a = s.index("# ----------------------------------------------------------------------------- claw corridor before the cart")
new = '''# ----------------------------------------------------------------------------- the trio of rising walls
T_RISE = 0x11


def trio_try(c, x_goal, phase, jx, stop_d=16, up_until=0, limit=420):
    """From the step at 2592: jump to the ledge when on the ground at world x >= jx, hold Right, a new B press on
    every frame with t % 5 == phase (forward; up-forward while t < up_until), and stand still (still firing)
    whenever a live wall is closer than stop_d px ahead and the Barrier is off. Ends on the ground at
    world x >= x_goal. Returns the rows used."""
    t = 0
    jumped = False
    while not (c.f.wx >= x_goal and grounded(c.f)):
        f = c.f
        want = {"Right"}
        g = grounded(f)
        if not jumped and g and f["y"] == 164 and f.wx >= jx and c.can("A"):
            want.add("A")
            jumped = True
        if (t % 5) == phase and c.can("B"):
            want.add("B")
        if t < up_until:
            want.add("Up")
        if not f["barrier"] and g and f["y"] == 132:
            for e in f.enemies():
                if e["type"] == T_RISE and 0 < e["hp"] < 0xF0 and 0 < e["x"] - f["x"] < stop_d:
                    want.discard("Right")
        _fr(c, want)
        t += 1
        if t > limit:
            raise Fail("trio: too long")
    return t


def trio_proc(r, x_goal=2800):
    """Runner Proc: the trio, by a grid over the fire phase and the jump point."""
    c = r.c
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    best = None
    res = {}
    try:
        for jx in (2612, 2616, 2620, 2608):
            for phase in range(5):
                for stop_d in (16, 17):
                    c.restore(base)
                    try:
                        n = trio_try(c, x_goal, phase, jx, stop_d)
                    except Fail as ex:
                        r.frames_simulated += len(c.rows) - base["n"]
                        res[f"{jx}/{phase}/{stop_d}"] = str(ex)[:8]
                        continue
                    r.frames_simulated += n
                    res[f"{jx}/{phase}/{stop_d}"] = n
                    if best is None or n < best[0]:
                        best = (n, jx, phase, stop_d)
        if best is None:
            raise Stuck(f"trio: nothing worked: {res}")
        c.restore(base)
        trio_try(c, x_goal, best[2], best[1], best[3])
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["trio"] = {"rows": best[0], "jump_at": best[1], "phase": best[2], "stop_d": best[3], "all": res}
    r.log(f"[{r.name}] trio: {best[0]} rows to wx {x_goal} (jump at {best[1]}, fire phase {best[2]}, stop at "
          f"{best[3]} px); all: {res}")


'''
s = s[:a] + new + s[a:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old = '''        Set(aim_mode="always"),                     # the trio: fire forward at every opportunity
        Jump(p.get("d_up", 2612)), Land(y=132),     # ledge at 2656 with the three rising walls
        Mark("trio"),
        Run(2800),
        Set(aim_mode=None),
'''
new = '''        Mark("trio"),
        Proc(s7b.trio_proc, "trio"),                # ledge at 2656 with the three rising walls (fire phase grid)
        Set(aim_mode=None),
'''
assert s.count(old) == 1
s = s.replace(old, new)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
