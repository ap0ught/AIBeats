"""Second-pass patch 7: s7b.walls2_proc (the two rising walls on the step 800: wall-top jumps by a grid)."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
a = s.index("# ----------------------------------------------------------------------------- the trio of rising walls")
new = '''# ----------------------------------------------------------------------------- two rising walls on the step 800
def walls2_try(r, jx, lf, ln, fire=True, limit=320):
    """From the step at 800 (standing Y 164): jump at world x >= jx holding Right, hold Left instead on air frames
    [lf, lf + ln), land on top of the first wall (standing Y 132); jump again at once (over the second wall,
    down to the step at about 920, Y 164) and a third time up to the ledge at 928 (Y 132). The runner's fire
    policy (walls spared) adds shots at soldiers / the gunner if fire is set. Returns the rows used."""
    c = r.c
    n0 = len(c.rows)

    def fr(want):
        want = set(want)
        if fire and r.fire_policy is not None:
            want = r.fire_policy(r, want, False)
        f = _fr(c, want)
        if len(c.rows) - n0 > limit:
            raise Fail("walls: too long")
        if c.f["weapon"] != 0x13:
            raise Fail("weapon changed")
        return f

    g = 0
    while not (grounded(c.f) and c.f["y"] == 164):
        fr(("Right",))
        g += 1
        if g > 80:
            raise Fail("never on the step")
    while c.f.wx < jx or not c.can("A"):
        fr(("Right",))
        if not grounded(c.f):
            raise Fail("left the step")
    fr(("Right", "A"))
    fr(("Right", "A"))
    air = 2
    while True:
        air += 1
        fr(("Left",) if lf <= air < lf + ln else ("Right",))
        if air > 6 and grounded(c.f):
            break
    if c.f["y"] != 132:
        raise Fail(f"jump 1 landed at y {c.f['y']} wx {c.f.wx}")
    top = (len(c.rows) - n0, c.f.wx)
    for want_y in (164, 132):
        while not c.can("A"):
            fr(())
        fr(("Right", "A"))
        fr(("Right", "A"))
        air = 2
        while True:
            air += 1
            fr(("Right",))
            if air > 6 and grounded(c.f):
                break
        if c.f["y"] != want_y:
            raise Fail(f"landed at y {c.f['y']} wx {c.f.wx}, wanted {want_y}")
    return len(c.rows) - n0, top


def walls2_proc(r):
    c = r.c
    sod = c.stop_on_death
    c.stop_on_death = False
    saved_user = dict(r.user)
    r.user["spare_walls"] = True
    base = c.snap()
    best = None
    res = {}
    tried = 0
    try:
        for fire in (True, False):
            for jx in (817, 816, 818, 815, 819):
                for lf in (12, 11, 13, 10, 14):
                    for ln in (3, 2, 4):
                        c.restore(base)
                        tried += 1
                        try:
                            n, top = walls2_try(r, jx, lf, ln, fire)
                        except Fail as ex:
                            r.frames_simulated += len(c.rows) - base["n"]
                            k = str(ex)[:14]
                            res[k] = res.get(k, 0) + 1
                            continue
                        r.frames_simulated += n
                        key = n - c.f.wx
                        if best is None or key < best[0]:
                            best = (key, (jx, lf, ln, fire), n, c.f.wx)
                    if best is not None and tried >= 30:
                        break
                if best is not None and tried >= 30:
                    break
            if best is not None:
                break
        if best is None:
            raise Stuck(f"rising walls: none of {tried} attempts worked: {res}")
        c.restore(base)
        jx, lf, ln, fire = best[1]
        walls2_try(r, jx, lf, ln, fire)
    finally:
        c.free(base)
        c.stop_on_death = sod
        r.user = saved_user
    r.user["walls2"] = {"params": list(best[1]), "rows": best[2], "wx": best[3], "tried": tried, "fails": res}
    r.log(f"[{r.name}] rising walls: jump at {jx}, Left on air frames {lf}..{lf + ln - 1}, fire {fire}: {best[2]} rows "
          f"to wx {best[3]} ({tried} attempts, fails {res})")


'''
s = s[:a] + new + s[a:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old_a = s.index("        JumpSteer(p.get(\"b_w1\", 817)")
old_b = s.index("        set_user(spare_walls=False),")
s = s[:old_a] + "        Proc(s7b.walls2_proc, \"rising walls\"),      # wall-top jumps, parameters by trial\n" + s[old_b:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
