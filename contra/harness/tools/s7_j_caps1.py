"""Job: the F flying capsule after the first cart: where is it relative to Bill, and a grid of single volleys that
destroy it so that the F item lands BEHIND Bill."""
from contra.stages.s6ctl import Ctl
from contra.stages.s7b import _fr, grounded, Fail
from contra.stages.s7lab import line

f0 = sim.load("s7/n4_ph90_cart1")
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()
txt = []
for i in range(96):
    _fr(c, ("Right",))
    cp = [e for e in c.f.enemies() if e["type"] == 3]
    if i % 6 == 0 and cp:
        txt.append((i, c.f.wx, c.f["y"], cp[0]["x"] - c.f["x"], cp[0]["y"]))
print("(t, wx, y, capsule dx, capsule y):", txt)
ok = []
for t0 in range(0, 110, 3):
    for aim in ((), ("Up",)):
        c.restore(base)
        try:
            hit = None
            for i in range(230):
                want = {"Right"}
                if t0 <= i < t0 + 2:
                    want.add("B")
                    want.update(aim)
                elif t0 - 2 <= i < t0 + 4:
                    want.update(aim)
                if c.f.wx >= 762 and grounded(c.f) and c.can("A") and i > 100:
                    pass
                _fr(c, want)
                if c.f["weapon"] != 0x13:
                    raise Fail("weapon")
                cp = [e for e in c.f.enemies() if e["type"] == 3 and e["hp"] and e["routine"] < 3]
                it = [e for e in c.f.enemies() if e["type"] == 0 and (e["attr"] & 7) == 2]
                if hit is None and it:
                    hit = (i, c.f.wx, it[0]["x"] - c.f["x"], it[0]["y"])
                if c.f.wx >= 712:
                    break
            it = [e for e in c.f.enemies() if e["type"] == 0 and (e["attr"] & 7) == 2]
            if hit:
                ok.append((t0, aim, hit, "item now dx", it[0]["x"] - c.f["x"] if it else None, "y", it[0]["y"] if it else None))
        except Fail as ex:
            ok.append((t0, aim, "FAIL", str(ex), c.f.wx))
for o in ok:
    print(o)
