"""Job: ground-based scripted door fight: Right to x_stop, B every 5 frames, Up+Right from scroll frame up_s."""
from contra.stages.s6ctl import Ctl
from contra.stages import s7b
from contra.stages.s7b import _fr, grounded, Fail, door_of

f0 = sim.load("s7/ph90_boss_beam")
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()


def fight(c, phase, up_s, x_stop, limit=330, jump_at=None):
    n0 = len(c.rows)
    s = -1
    t = 0
    jumped = False
    while not c.f["bossdef"]:
        f = c.f
        if f["stop"] == 0xFF and s < 0:
            s = 0
        want = set()
        if f["x"] < x_stop:
            want.add("Right")
        if s >= 0:
            if (t % 5) == phase and c.can("B"):
                want.add("B")
            if s >= up_s and grounded(f):
                want.add("Up")
                if "Right" not in want and f["x"] >= x_stop:
                    pass
            if jump_at is not None and not jumped and s >= jump_at and grounded(f) and c.can("A"):
                want.add("A")
                want.discard("Up")
                jumped = True
            s += 1
        _fr(c, want)
        t += 1
        if t > limit:
            raise Fail("door not dead in time")
    return len(c.rows) - n0


res = []
for up_s in (40, 60, 75, 90):
    for x_stop in (158, 162, 166, 170, 176):
        line = []
        for ph in range(5):
            c.restore(base)
            try:
                n = fight(c, ph, up_s, x_stop)
                line.append(n)
                res.append((n, up_s, x_stop, ph))
            except Fail as ex:
                line.append(str(ex)[:6])
        print("up_s", up_s, "x_stop", x_stop, line)
res.sort()
print("best", res[:6])
n, up_s, x_stop, ph = res[0]
c.restore(base)
fight(c, ph, up_s, x_stop)
s = -1
for i, f in enumerate(c.tr):
    d = door_of(f)
    if f["stop"] == 0xFF and s < 0:
        s = i
    if d and (i % 5 == 0 or f["bossdef"]):
        print(i, "s", i - s, "x", f["x"], "y", f["y"], "door", d["x"], d["hp"], "nb", f.nbullets(), "+".join(c.rows[i]))
