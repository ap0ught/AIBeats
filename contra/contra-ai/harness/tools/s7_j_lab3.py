"""Job: from ph90_lower2 walk (w=0) with one volley at the moving cart; print what happens to the carts."""
from contra.stages.s7lab import seq, show, line

base_f = sim.load("s7/ph90_lower2")
base = sim.msave()
for w, fire_d in ((0, 24), (0, 40), (0, 0)):
    sim.mload(base)
    f = base_f
    fired = -9
    hold = 0
    n = 0
    print("---- w", w, "fire_d", fire_d)
    while f.wx < 1402 and n < 400:
        row = [] if n < w else ["Right"]
        mc = [e for e in f.enemies() if e["type"] == 0x14 and e["hp"] and e["routine"] < 5]
        if hold:
            row.append("B")
            hold -= 1
        elif mc and 0 < mc[0]["x"] - f["x"] < fire_d and fired <= n - 5:
            row.append("B")
            hold = 1
            fired = n
        f = sim.run([tuple(row)])[-1]
        n += 1
        if "B" in row or f.dead or n % 12 == 0:
            print(line(n, f, (0x14, 0x15)), "+".join(row))
        if f.dead:
            break
sim.mfree(base)
