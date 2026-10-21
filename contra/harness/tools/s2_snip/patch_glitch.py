import os

ROOT = ""


def patch(path, reps):
    p = ROOT + path
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)


patch("contra/stages/base_boss4.py", [
    ("def attack(S: Sess, slot, x_target, W, tj, phase, limit, rejump=True):",
     "def attack(S: Sess, slot, x_target, W, tj, phase, limit, rejump=True, g=None):"),
    ('''        if S.pad.len["B"] == 1 or (S.pad.len["B"] == 0 and S.pad.can_press("B") and (n - phase) % 5 == 0):
            row.append("B")''',
     '''        if g is not None and W + g - 28 <= n <= W + g:
            # hold fire so that five slots are free, then one full spray from the ground at exactly W + g: its
            # outer pellet is meant to reach the OTHER helmet on the frame that helmet's timer runs out
            if S.pad.len["B"] == 1 or (n == W + g and S.pad.can_press("B")):
                row.append("B")
        elif S.pad.len["B"] == 1 or (S.pad.len["B"] == 0 and S.pad.can_press("B") and (n - phase) % 5 == 0):
            row.append("B")'''),
    ('''    out.sort(key=lambda r: (r[0] if r[0] is not None else 10 ** 6 + r[1] * 1000))
    return W, out, snap''',
     '''    if other is not None and waiting and not any(r[2] for r in out):
        # no ordinary attack left the other helmet open: try the dedicated full spray from the ground
        for x in (hx, hx - 4, hx + 4):
            for g in range(-16, -1):
                for tj in (g + 2, g + 8):
                    for phase in range(5):
                        S.restore(snap)
                        kill, hp = attack(S, slot, x, W, tj, phase, W + limit_after, g=g)
                        oth = False
                        if kill is not None:
                            while len(S.rows) < W + 37:
                                if S.step(S.pad.fix(()))["death"] & 1:
                                    break
                            ho = helmets(S.s).get(other)
                            oth = bool(ho and ho[2] and ho[1] > 0)
                        if oth:
                            out.append((kill, hp, oth, (x, tj, phase, g)))
    out.sort(key=lambda r: (r[0] if r[0] is not None else 10 ** 6 + r[1] * 1000))
    return W, out, snap'''),
    ("        attack(S, first, par[0], W, par[1], par[2], W + 150)\n        inf = {",
     "        attack(S, first, par[0], W, par[1], par[2], W + 150, g=par[3] if len(par) > 3 else None)\n        inf = {"),
])
print("patched")
