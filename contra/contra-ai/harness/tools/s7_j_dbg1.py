"""Job: why does walls2_proc see 'weapon changed' in the n2 solve? Run route_b from s7/n2_ph90_cart1."""
from contra.stages import s7, s7b
from contra.stages.s7lab import line

f0 = sim.load("s7/n2_ph90_cart1")
print("start", line(0, f0, (0x00, 0x03, 0x15)), "weapon", hex(f0["weapon"]))
r = s7.make_runner(sim, route=s7.tag_route(s7.route_b()), name="dbg")
orig = s7b.walls2_proc


def spy(r):
    c = r.c
    print("proc starts:", line(len(c.rows), c.f, (0x00, 0x03, 0x11)), "weapon", hex(c.f["weapon"]))
    for i in range(max(0, len(c.tr) - 30), len(c.tr), 3):
        print("   ", line(i, c.tr[i], (0x00, 0x03)), "w", hex(c.tr[i]["weapon"]), "+".join(c.rows[i]))
    return orig(r)


for st in r.route:
    if getattr(st, "label", "") == "rising walls":
        st.fn = spy
res = r.solve(max_deaths=10)
print(res, len(r.c.rows), r.user.get("walls2"))
