"""Second-pass patch 4: s7b.jump_choice (pick the fastest of a few jump points on save states) + cart landings."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
a = s.index("# ----------------------------------------------------------------------------- claw corridor before the cart")
new = '''# ----------------------------------------------------------------------------- choose a jump point by trial
def jump_choice(x_goal, cands, label="", need_y=None):
    """Runner Proc factory: from the current state hold Right to world x >= x_goal (on the ground, at standing Y
    need_y if given), with one jump at the first frame Bill is on the ground at world x >= cand (None = no jump).
    Every candidate is played on a save state; the one that needs the fewest rows is kept (ties: the first)."""
    def proc(r):
        c = r.c
        sod = c.stop_on_death
        c.stop_on_death = False
        base = c.snap()
        best = None
        res = {}

        def play(jx):
            jumped = jx is None
            n = 0
            while not (c.f.wx >= x_goal and grounded(c.f) and (need_y is None or c.f["y"] == need_y)):
                want = {"Right"}
                if not jumped and c.f.wx >= jx and grounded(c.f) and c.can("A"):
                    want.add("A")
                    jumped = True
                _fr(c, want)
                n += 1
                if n > 500:
                    raise Fail("never arrived")
            return n

        try:
            for jx in cands:
                c.restore(base)
                try:
                    n = play(jx)
                except Fail as ex:
                    r.frames_simulated += len(c.rows) - base["n"]
                    res[str(jx)] = str(ex)[:12]
                    continue
                r.frames_simulated += n
                res[str(jx)] = n
                if best is None or n < best[0]:
                    best = (n, jx)
            if best is None:
                raise Stuck(f"{label}: no jump point works: {res}")
            c.restore(base)
            play(best[1])
        finally:
            c.free(base)
            c.stop_on_death = sod
        r.user.setdefault("jump_choice", {})[label] = {"jump_at": best[1], "rows": best[0], "all": res}
        r.log(f"[{r.name}] {label}: jump at {best[1]} -> {best[0]} rows to wx {x_goal} ({res})")
    return proc


'''
s = s[:a] + new + s[a:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)


rep('''        Run(608), Land(),                           # off the step: onto the cart at 624 (or the floor)
''', '''        # SECOND PASS: a jump from the step that lands on the cart's REAR edge (boards at 613 instead of 625:
        # 27 frames on the cart instead of 15, 8 frames faster than walking off the step at 608)
        Jump(p.get("a_cart", 550), skip_y=176), Land(),
''')
rep('''        Run(1792), Land(),                          # off the ledge (cart at 1824 below)
        Mark("cart3"),
''', '''        # cart 1824: a jump from the ledge that lands on its rear edge (29 frames on it) or the walk off at 1792
        Proc(s7b.jump_choice(1920, (None, 1741, 1742, 1743, 1744, 1745), "cart 1824", need_y=196), "cart 1824"),
        Mark("cart3"),
''')
rep('''        Jump(p.get("d_pit", 2318)), Land(),         # the pit 2320..2367 (cart at 2376 beyond it)
        Mark("alley"),
''', '''        # the pit 2320..2367 and the cart at 2376 beyond it: the jump point that reaches wx 2470 soonest
        Proc(s7b.jump_choice(2470, (2318, 2316, 2312, 2308, 2306, 2305, 2304, 2303, 2302, 2301, 2300, 2298, 2296),
                             "pit + cart 2376", need_y=196), "pit"),
        Mark("alley"),
''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
