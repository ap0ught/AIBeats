"""Second-pass patch 14: s7b.capsule_proc - destroy the F flying capsule from the first cart with one aimed volley
so that the F item lands behind Bill; the auto-aim is then free again at the rising walls."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
a = s.index("# ----------------------------------------------------------------------------- choose a jump point by trial")
new = '''# ----------------------------------------------------------------------------- the F capsule at the first cart
T_CAPS = 0x03


def capsule_try(c, t0, aim, x_end=708, limit=140):
    """Hold Right; one volley (B two frames, with `aim`) on frame t0. Returns (frame the item appeared, item dx at
    the end, item y at the end, Bill y at the end) once Bill is at world x >= x_end. Fails if Bill dies, the weapon
    changes or the capsule survives."""
    hit = None
    i = 0
    while c.f.wx < x_end:
        want = {"Right"}
        if t0 <= i < t0 + 2:
            want.add("B")
            want.update(aim)
        elif t0 - 2 <= i < t0 + 4:
            want.update(aim)
        _fr(c, want)
        if c.f["weapon"] != 0x13:
            raise Fail("weapon changed")
        if hit is None and any(e["type"] == T_ITEM and (e["attr"] & 7) == 2 for e in c.f.enemies()):
            hit = i
        i += 1
        if i > limit:
            raise Fail("too long")
    if hit is None:
        raise Fail("capsule not hit")
    it = next((e for e in c.f.enemies() if e["type"] == T_ITEM and (e["attr"] & 7) == 2), None)
    return hit, (it["x"] - c.f["x"]) if it else -999, it["y"] if it else 0, c.f["y"]


def capsule_proc(r):
    """Runner Proc (called on the first cart): one volley that releases the F item where Bill cannot touch it -
    behind him, or high above his path. Nothing is done if no volley works (the auto-aim then stays silent while
    the capsule is ahead: see s7.fire_policy)."""
    c = r.c
    f = c.f
    if not any(e["type"] == T_CAPS and (e["attr"] & 7) == 2 for e in f.enemies()):
        r.user["capsule"] = {"done": False, "why": "no F capsule on screen"}
        return
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    best = None
    tried = 0
    try:
        for t0 in list(range(0, 44, 2)) + list(range(54, 72, 2)):
            for aim in (("Up",), ()):
                c.restore(base)
                tried += 1
                try:
                    hit, dx, iy, by = capsule_try(c, t0, aim)
                except Fail:
                    r.frames_simulated += len(c.rows) - base["n"]
                    continue
                r.frames_simulated += len(c.rows) - base["n"]
                # safe: the item is behind Bill; second best: well above his head and not ahead by much
                rank = 0 if dx <= -10 else (1 if (iy < by - 45 and dx < 14) else 2)
                if rank < 2 and (best is None or (rank, dx) < (best[0], best[1])):
                    best = (rank, dx, t0, aim, hit)
            if best is not None and best[0] == 0 and best[1] <= -30:
                break
        c.restore(base)
        if best is not None:
            _, dx, t0, aim, hit = best
            for i in range(hit + 2):
                want = {"Right"}
                if t0 <= i < t0 + 2:
                    want.add("B")
                    want.update(aim)
                elif t0 - 2 <= i < t0 + 4:
                    want.update(aim)
                _fr(c, want)
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["capsule"] = ({"done": True, "volley_frame": best[2], "aim": list(best[3]), "item_dx_at_x708": best[1],
                          "tried": tried} if best else {"done": False, "why": "no safe volley", "tried": tried})
    r.log(f"[{r.name}] F capsule: {r.user['capsule']}")


'''
s = s[:a] + new + s[a:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old = '''        Jump(p.get("a_cart", 550), skip_y=176), Land(),
        Mark("cart1"),
'''
new = '''        Jump(p.get("a_cart", 550), skip_y=176), Land(),
        Mark("cart1"),
        Proc(s7b.memo(s7b.capsule_proc, "F capsule"), "F capsule"),
'''
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace('if k in ("precart", "bgrab", "walls2", "trio", "boss", "jump_choice")}}',
              'if k in ("capsule", "precart", "bgrab", "walls2", "trio", "boss", "jump_choice")}}')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
