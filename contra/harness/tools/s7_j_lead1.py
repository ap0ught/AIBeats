"""Job: check the leading-pause method: route a+b from the real start ph90 (fc 152) and from ph80 (fc 142) with a
10-frame pause on row 40. The marks should be 10 rows apart with the same frame counter values."""
from contra.stages import s7
from contra.stages.s6run import Remedy

for state, lead in (("s7/ph90", 0), ("s7/ph80", 10), ("s7/ph100", 22)):
    f0 = sim.load(state)
    r = s7.make_runner(sim, route=s7.tag_route(s7.route_a() + s7.route_b()), name=f"lead{lead}")
    if lead:
        r.remedies.append(Remedy(40, "pause", lead))
    res = r.solve(max_deaths=20, back=110)
    c = r.c
    seen = sum(1 for f in c.tr[:lead + 60] if f["pause"])
    print(state, "lead", lead, res, "rows", len(c.rows), "minus lead", len(c.rows) - lead, "paused frames seen", seen,
          "start fc", (f0["fc"] + 1) & 255)
    print("   marks (label, row - lead, fc):", [(m[0], m[1] - (lead if m[1] > 40 else 0), m[2]) for m in r.marks])
    print("   remedies", [repr(x) for x in r.remedies], "procs", {k: v for k, v in r.user.items() if k in ("capsule",)})
