"""Second-pass patch 16: s7b.alley_proc - Heartbreak Alley with the Barrier: straight through, plus a two-frame
aim tap chosen by trial. The tap changes the random number (it is advanced by the idle loop), hence the soldier
waves around the trio; with five soldiers on screen every second frame at the trio is a lag frame."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
a = s.index("# ----------------------------------------------------------------------------- claw corridor before the cart")
new = '''# ----------------------------------------------------------------------------- Heartbreak Alley with the Barrier
def alley_try(c, tap, x_jump=2562, limit=260):
    """Hold Right from the floor behind the pit to the step at 2592 (jump at world x >= x_jump, land at Y 164);
    tap = None or (frame, button): that aim button is held on frames [frame, frame + 2) (no shot). Returns rows."""
    i = 0
    jumped = False
    while True:
        want = {"Right"}
        if tap is not None and tap[0] <= i < tap[0] + 2:
            want.add(tap[1])
        if not jumped and c.f.wx >= x_jump and grounded(c.f) and c.can("A"):
            want.add("A")
            jumped = True
        _fr(c, want)
        i += 1
        if jumped and i > 6 and grounded(c.f) and c.f["y"] == 164 and c.f.wx > x_jump + 20:
            return i
        if i > limit:
            raise Fail("alley: too long")


ALLEY_TAPS = [None] + [(k, "Up") for k in range(0, 96, 8)] + [(k, "Down") for k in range(4, 96, 16)]


def alley_proc(r, x_goal=2800):
    """Runner Proc: every tap variant is played to the far end of the trio with one fixed trio policy; the variant
    with the fewest rows (lag frames are rows) is kept and played to the step. The trio grid runs afterwards."""
    c = r.c
    if not c.f["barrier"]:
        raise Stuck("alley: no Barrier")
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    best = None
    res = {}
    try:
        for tap in ALLEY_TAPS:
            c.restore(base)
            try:
                n1 = alley_try(c, tap)
                n2 = trio_try(c, x_goal, 1, 2618, 17, fire_from=2646)
            except Fail as ex:
                r.frames_simulated += len(c.rows) - base["n"]
                res[str(tap)] = str(ex)[:10]
                continue
            r.frames_simulated += n1 + n2
            lag = sum(f["lagged"] for f in c.tr[base["n"]:])
            res[str(tap)] = (n1 + n2, lag)
            if best is None or n1 + n2 < best[0]:
                best = (n1 + n2, tap, lag)
            if best[2] == 0 and tap is None:
                break                       # no lag without a tap: nothing to gain
        if best is None:
            raise Stuck(f"alley: nothing worked: {res}")
        c.restore(base)
        alley_try(c, best[1])
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["alley"] = {"tap": best[1], "rows_to_2800_fixed_policy": best[0], "lag_fixed_policy": best[2], "all": res}
    r.log(f"[{r.name}] alley: tap {best[1]} -> {best[0]} rows to wx {x_goal} with the fixed trio policy, lag "
          f"{best[2]} (variants: {res})")


'''
s = s[:a] + new + s[a:]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old = '''        Jump(p.get("d_step", 2562)), Land(y=164),   # step at 2592
        Mark("trio"),'''
new = '''        Proc(s7b.memo(s7b.alley_proc, "alley"), "alley"),   # to the step at 2592; an aim tap picks the soldier luck
        Mark("trio"),'''
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace('if k in ("capsule", "precart", "bgrab", "walls2", "trio", "boss", "jump_choice")}}',
              'if k in ("capsule", "precart", "bgrab", "walls2", "alley", "trio", "boss", "jump_choice")}}')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
