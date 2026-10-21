"""Second-pass patch 3: s7b.precart_proc (claw corridor 1245 -> 1392 with the cart kept alive) + route change."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
a = s.index("# ----------------------------------------------------------------------------- procedures for the runner")
new = '''# ----------------------------------------------------------------------------- claw corridor before the cart
T_MCART, T_CLAW = 0x14, 0x10


def corridor_try(c, x_end, w0=0, kill=(), fire_d=24, maxvol=1, off=3, limit=420, need_cart=1425):
    """Walk right to world x >= x_end from the current state: stand w0 frames first; a 5-frame pause over every
    global-timer trigger value in `kill` ($00/$20/$40/$60, first occurrence only) deletes that claw drop; one
    Spread volley (at most maxvol) when the rolling cart is closer than fire_d px. Fails if Bill dies or the
    stationary cart near `need_cart` is not alive at the end."""
    n = 0
    vol = 0
    todo = set(kill)
    unpause = False
    while c.f.wx < x_end:
        f = c.f
        hit = next((T for T in todo if ((f["fc"] + off) & 127) == T), None)
        if hit is not None and c.can("Start") and not unpause:
            todo.discard(hit)
            held = tuple(b for b in c.pr.held if b in ("Left", "Right", "Up", "Down"))
            _fr(c, held + ("Start",))
            _fr(c, held + ("Start",))
            for _ in range(3):
                _fr(c, held)
            unpause = True
            n += 5
            continue
        want = set() if n < w0 else {"Right"}
        if unpause:
            want.add("Start")
            unpause = False
        mc = next((e for e in f.enemies() if e["type"] == T_MCART and 0 < e["hp"] < 0xF0 and e["routine"] < 5), None)
        if mc is not None and 0 < mc["x"] - f["x"] < fire_d and vol < maxvol and c.can("B"):
            want.add("B")
            vol += 1
        _fr(c, want)
        n += 1
        if n > limit:
            raise Fail("corridor: too long")
    if c.f["pause"]:
        raise Fail("still paused")
    if need_cart is not None:
        cart = find(c.f, T_CART, need_cart, 60)
        if cart is None or not (0 < cart["hp"] < 0xF0) or cart["routine"] >= 5:
            raise Fail("cart lost")
    return n


def corridor_plans():
    """Plans in order of the frames they cost: (cost, w0, kill set)."""
    out = [(0, 0, ())]
    out += [(w, w, ()) for w in (2, 4)]
    out += [(5, 0, (T,)) for T in (0x00, 0x20, 0x40, 0x60)]
    out += [(w, w, ()) for w in (6, 8)]
    out += [(5 + w, w, (T,)) for w in (2, 4) for T in (0x00, 0x20, 0x40, 0x60)]
    out += [(10, 0, (a, b)) for a in (0x00, 0x20, 0x40, 0x60) for b in (0x00, 0x20, 0x40, 0x60) if a < b]
    out += [(w, w, ()) for w in range(10, 16, 2)]
    out += [(15, 0, (a, b, d)) for a in (0, 0x20) for b in (0x20, 0x40) for d in (0x40, 0x60) if a < b < d]
    out += [(w, w, ()) for w in range(16, 72, 2)]
    return sorted(out, key=lambda t: t[0])


def precart_proc(r, x_end=1392):
    """Runner Proc: the lower floor of screen 5 (five claws, the rolling cart) up to the stationary cart, which
    must survive. Cheapest plan that works."""
    c = r.c
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    done = None
    tried = 0
    why = {}
    try:
        for cost, w0, kill in corridor_plans():
            for (fire_d, maxvol) in ((24, 1), (20, 1), (30, 1), (24, 2), (36, 2), (16, 1)):
                c.restore(base)
                tried += 1
                try:
                    n = corridor_try(c, x_end, w0, kill, fire_d, maxvol)
                except Fail as ex:
                    r.frames_simulated += len(c.rows) - base["n"]
                    why[str(ex)[:20]] = why.get(str(ex)[:20], 0) + 1
                    if str(ex).startswith("dead") and (c.f.wx < 1300 or c.f.wx > 1372):
                        break                     # a claw, not the rolling cart: the fire rule does not matter
                    continue
                r.frames_simulated += n
                done = (cost, w0, kill, fire_d, maxvol, n)
                break
            if done:
                break
        if done is None:
            raise Stuck(f"claw corridor: none of {tried} plans worked: {why}")
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["precart"] = {"cost": done[0], "wait": done[1], "pauses": list(done[2]), "fire_d": done[3],
                         "volleys": done[4], "rows": done[5], "tried": tried}
    r.log(f"[{r.name}] claw corridor: wait {done[1]}, pauses over {[hex(x) for x in done[2]]}, volley at "
          f"{done[3]} px x{done[4]}: {done[5]} rows ({tried} plans tried)")


'''
s = s[:a] + new + s[a:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old = '''        set_user(shoot_mcart=True, fire_range=p.get("c_fire_range", 100)),
        Run(p.get("c_pre", 1392)),                  # claws 1270..1398 (runner remedies), the rolling cart is shot
        set_user(shoot_mcart=False, fire_range=p.get("fire_range", 60)),
        Proc(s7b.bgrab_proc, "B grab"),
'''
new = '''        Set(aim_mode="off"),
        Proc(s7b.precart_proc, "claw corridor"),    # claws 1270..1398, the rolling cart; the cart 1424 must live
        Mark("precart"),
        Proc(s7b.bgrab_proc, "B grab"),
'''
assert s.count(old) == 1
s = s.replace(old, new)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
