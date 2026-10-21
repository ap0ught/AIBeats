"""Stage 7 second pass: scripted procedures for the runner (contra/stages/s7.py), each found by a small grid on
save states: capsule_proc (F capsule at the first cart), walls2_proc (wall-top jumps), precart_proc (claw corridor
before the cart 1424), bgrab_proc (the Barrier), jump_choice (cart landings), alley_proc, trio_proc, boss_proc2
(the door). memo() makes a procedure replay its result when the runner calls it again from the same state.

Measured facts used here (2026-10-12, NesHawk):
* A jump rises 59 px in 30 frames; on level ground it lasts about 62 frames.
* "Chariot Hop": pressing A on the floor 15-17 px left of a stationary cart's centre puts Bill ON the cart two
  frames later (standing Y 176) at its rear edge; with Right held he then rides 29 frames at about 1.72 px/frame.
* The B pill box (world x 1552, y 96) is created when the camera reaches 1312, gets HP 1 49 frames later and is
  open for 81 frames. Its item flies up 3 px/frame, bounces off the pillar at x 1584 and lands back on the pill
  box's own ledge: it cannot be collected from the floor.
"""
from __future__ import annotations

from .s6ctl import Stuck
from .s6run import Done as _Done

T_CART, T_PILL, T_ITEM = 0x15, 0x02, 0x00


def grounded(f):
    return (f["jump"] & 15) == 0 and f["fall"] == 0


def find(f, typ, wx=None, tol=48):
    for e in f.enemies():
        if e["type"] == typ and (wx is None or abs(e["x"] + f.cam - wx) <= tol):
            return e
    return None


class Fail(Exception):
    pass


def _fr(c, want, log=None):
    f = c.frame(want)
    if log is not None:
        log.append(f)
    if f.dead:
        raise Fail("dead")
    if f["weapon"] != 0x13 and f["lroutine"] == 4:
        raise Fail("weapon changed")          # an item was picked up: never acceptable (Spread + Rapid must stay)
    return f


def bgrab_try(c, k_ride, wait2, t_fire, hop=16, t_fire2=None, aim=("Down",), log=None, verbose=None):
    """Play the B grab from the current state (Bill on the lower floor left of the cart at 1424). Raises Fail.
    Returns a dict (rows used, final wx ...). The emulator is left where the attempt ended."""
    n0 = len(c.rows)
    f = c.f
    cart = find(f, T_CART, 1425, 60)
    if cart is None or not (0 < cart["hp"] < 0xF0) or cart["routine"] >= 5:
        raise Fail("no cart")
    cx = cart["x"] + f.cam
    g = 0
    while c.f.wx < cx - hop or not c.can("A") or not grounded(c.f):
        _fr(c, ("Right",), log)
        g += 1
        if g > 200:
            raise Fail("never reached the cart")
    _fr(c, ("Right", "A"), log)
    _fr(c, ("Right", "A"), log)
    g = 0
    while not c.f["onen"]:
        _fr(c, ("Right",), log)
        g += 1
        if g > 8:
            raise Fail("not on the cart")
    board = (len(c.rows) - n0, c.f.wx)
    for _ in range(k_ride):
        _fr(c, ("Right",), log)
        if not c.f["onen"]:
            raise Fail("left the cart")
    g = 0
    while not c.can("A"):
        _fr(c, ("Right",), log)
        g += 1
        if not c.f["onen"]:
            raise Fail("left the cart")
    j1 = (len(c.rows) - n0, c.f.wx)
    _fr(c, ("Right", "A"), log)
    _fr(c, ("Right", "A"), log)
    g = 0
    while not grounded(c.f) or g < 3:
        _fr(c, ("Right",), log)
        g += 1
        if g > 90:
            raise Fail("jump 1 never landed")
    if c.f["y"] != 132:
        raise Fail(f"jump 1 landed at y {c.f['y']} wx {c.f.wx}")
    land1 = (len(c.rows) - n0, c.f.wx)
    for _ in range(wait2):
        _fr(c, ("Right",), log)
        if not grounded(c.f):
            raise Fail("fell off the small ledge")
    while not c.can("A"):
        _fr(c, ("Right",), log)
    j2 = (len(c.rows) - n0, c.f.wx)
    _fr(c, ("Right", "A"), log)
    _fr(c, ("Right", "A"), log)
    t = 2
    got = None
    fires = [x for x in (t_fire, t_fire2) if x is not None]
    while True:
        want = ["Right"]
        if any(x <= t < x + 2 for x in fires):
            want += list(aim) + ["B"]
        elif any(x - 2 <= t < x + 3 for x in fires):
            want += list(aim)
        _fr(c, want, log)
        t += 1
        if c.f["barrier"] and got is None:
            got = (len(c.rows) - n0, c.f.wx, c.f["y"], t)
        if t > 6 and grounded(c.f):
            break
        if t > 100:
            raise Fail("jump 2 never landed")
    land2 = (len(c.rows) - n0, c.f.wx, c.f["y"])
    if got is None:
        raise Fail(f"no barrier (landed y {c.f['y']} wx {c.f.wx})")
    if c.f["y"] == 100:
        # on the pill box's ledge: drop through it (Down+A), keep Right
        while not c.can("A"):
            _fr(c, ("Right",), log)
        y0 = c.f["y"]
        _fr(c, ("Down", "A"), log)
        _fr(c, ("Down", "A"), log)
        g = 0
        while True:
            _fr(c, ("Right",), log)
            g += 1
            if g > 3 and grounded(c.f):
                if c.f["y"] == y0:
                    raise Fail("drop did not start")
                break
            if g > 120:
                raise Fail("drop never landed")
    return {"rows": len(c.rows) - n0, "wx": c.f.wx, "y": c.f["y"], "board": board, "j1": j1, "land1": land1,
            "j2": j2, "got": got, "land2": land2, "loss": (len(c.rows) - n0) - (c.f.wx - (cx - hop)),
            "barrier": c.f["barrier"], "fc": c.f["fc"]}

# ----------------------------------------------------------------------------- memoised procedures
def memo(fn, label):
    """Wrap a runner Proc so that a second call from the same state replays the rows found the first time.
    (The runner replays the route, Procs included, for every remedy trial that starts before the Proc.)"""
    def proc(r):
        c = r.c
        store = r.__dict__.setdefault("_memo", {})
        f = c.f
        key = (label, len(c.rows), f["fc"], f["rng"], f.wx, f["x"], f["y"], f["barrier"], f.nbullets(),
               tuple(sorted(c.pr.held)), c.can("A"), c.can("B"), c.can("Start"))
        hit = store.get(key)
        if hit is not None:
            base = c.snap()
            sod = c.stop_on_death
            c.stop_on_death = False
            try:
                for row in hit["rows"]:
                    c.frame(row)
                    if c.f.dead:
                        break
            finally:
                c.stop_on_death = sod
            g = c.f
            if (g.wx, g["y"], g["fc"], g["rng"]) == hit["end"] and not g.dead:
                c.free(base)
                r.frames_simulated += len(hit["rows"])
                r.user.update(hit["user"])
                r.marks.extend(hit["marks"])
                return
            c.restore(base)
            c.free(base)
        if getattr(r, "_in_trial", False):
            raise _Done()                     # a remedy trial got here alive: that is all the trial has to show
        n0, m0 = len(c.rows), len(r.marks)
        u0 = dict(r.user)
        fn(r)
        g = c.f
        store[key] = {"rows": list(c.rows[n0:]), "end": (g.wx, g["y"], g["fc"], g["rng"]),
                      "user": {k: v for k, v in r.user.items() if u0.get(k) != v},
                      "marks": [(m[0], m[1] - n0) + tuple(m[2:]) for m in r.marks[m0:]], "n0": n0}
        store[key]["marks"] = list(r.marks[m0:])
    return proc


# ----------------------------------------------------------------------------- the F capsule at the first cart
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


# ----------------------------------------------------------------------------- choose a jump point by trial
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
        limit = max(200, x_goal - c.f.wx + 200)

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
                if n > limit:
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


# ----------------------------------------------------------------------------- two rising walls on the step 800
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
            for jx in (0, 813, 815, 817, 819):
                for lf in (12, 16, 9):
                    for ln in (0, 1, 2, 3, 4):
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
                    if best is not None and tried >= 25:
                        break
                if best is not None and tried >= 25:
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


# ----------------------------------------------------------------------------- the trio of rising walls
T_RISE = 0x11


def trio_try(c, x_goal, phase, jx, stop_d=16, up_until=0, limit=420, fire_from=0):
    """From the step at 2592: jump to the ledge when on the ground at world x >= jx, hold Right, a new B press on
    every frame with t % 5 == phase (forward; up-forward while t < up_until), and stand still (still firing)
    whenever a live wall is closer than stop_d px ahead and the Barrier is off. Ends on the ground at
    world x >= x_goal. Returns the rows used."""
    t = 0
    jumped = False
    while not (c.f.wx >= x_goal and grounded(c.f)):
        f = c.f
        want = {"Right"}
        g = grounded(f)
        if not jumped and g and f["y"] == 164 and f.wx >= jx and c.can("A"):
            want.add("A")
            jumped = True
        if (t % 5) == phase and c.can("B") and f.wx >= fire_from:
            want.add("B")
        if t < up_until:
            want.add("Up")
        if not f["barrier"] and g and f["y"] == 132:
            for e in f.enemies():
                if e["type"] != T_RISE or not (0 < e["x"] - f["x"] < stop_d):
                    continue
                if e["hp"] == 0 and e["x"] - f["x"] >= 17:
                    continue                    # dying: gone in 3 frames, only its last 16 px are still lethal
                want.discard("Right")
        _fr(c, want)
        t += 1
        if t > limit:
            raise Fail("trio: too long")
    return t


def trio_proc(r, x_goal=2800):
    """Runner Proc: the trio, by a grid over the fire phase and the jump point."""
    c = r.c
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    best = None
    res = {}
    try:
        for fire_from in (0, 2646):
            for jx in (2612, 2618):
                for phase in range(5):
                    for stop_d in (17, 22):
                        c.restore(base)
                        try:
                            n = trio_try(c, x_goal, phase, jx, stop_d, fire_from=fire_from)
                        except Fail as ex:
                            r.frames_simulated += len(c.rows) - base["n"]
                            res[f"{fire_from}/{jx}/{phase}/{stop_d}"] = str(ex)[:8]
                            continue
                        r.frames_simulated += n
                        res[f"{fire_from}/{jx}/{phase}/{stop_d}"] = n
                        if best is None or n < best[0]:
                            best = (n, jx, phase, stop_d, fire_from)
        if best is None:
            raise Stuck(f"trio: nothing worked: {res}")
        c.restore(base)
        trio_try(c, x_goal, best[2], best[1], best[3], fire_from=best[4])
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["trio"] = {"rows": best[0], "jump_at": best[1], "phase": best[2], "stop_d": best[3],
                      "fire_from": best[4], "all": res}
    r.log(f"[{r.name}] trio: {best[0]} rows to wx {x_goal} (jump at {best[1]}, fire phase {best[2]}, stop at "
          f"{best[3]} px, firing from wx {best[4]}); worst {max(v for v in res.values() if isinstance(v, int))}")


# ----------------------------------------------------------------------------- Heartbreak Alley with the Barrier
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


# ----------------------------------------------------------------------------- claw corridor before the cart
T_MCART, T_CLAW = 0x14, 0x10


def corridor_try(c, x_end, w0=0, kill=(), fire_d=24, maxvol=1, off=3, limit=420, need_cart=1425, soldier_d=44):
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
        elif c.can("B") and any(e["type"] in (0x05, 0x06) and 0 < e["hp"] < 0xF0 and e["routine"] < 5
                                and 0 < e["x"] - f["x"] < soldier_d and abs(e["y"] - f["y"]) < 20
                                for e in f.enemies()):
            want.add("B")                 # a soldier walking at Bill: one level volley
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


# ----------------------------------------------------------------------------- procedures for the runner

def bgrab_proc(r):
    """Runner Proc: the Barrier grab. Tries the parameter grid on save states and keeps the attempt that reaches the
    floor behind the pill box in the fewest rows per pixel; among equals the one that picks the Barrier up latest."""
    c = r.c
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    best = None
    tried = 0
    why = {}
    try:
        for w0 in (0, 3, 6, 10, 16, 24, 32):
            for hop in (16, 15, 17, 14):
                for k in (28, 27, 29):
                    stage_ok = False
                    early = False
                    for w2 in (0, 1, 2, 4):
                        if early:
                            break
                        for tf in (42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22):
                            c.restore(base)
                            tried += 1
                            try:
                                for _ in range(w0):
                                    _fr(c, ())
                                res = bgrab_try(c, k, w2, tf, hop)
                            except Fail as ex:
                                r.frames_simulated += len(c.rows) - base["n"]
                                msg = str(ex)
                                why[msg[:40]] = why.get(msg[:40], 0) + 1
                                if msg.startswith(("jump 1", "left the cart", "not on the cart", "never reached",
                                                   "no cart")) and "barrier" not in msg:
                                    early = True
                                    break                   # the first jump failed: the fire frame does not matter
                                continue
                            r.frames_simulated += res["rows"]
                            stage_ok = True
                            key = (res["rows"] - res["wx"], -res["got"][0])
                            if best is None or key < best[0]:
                                best = (key, (w0, hop, k, w2, tf), res)
                            break                           # fire frames are tried latest first
                        if stage_ok:
                            break
                    if best is not None and best[1][0] == w0:
                        break
                if best is not None:
                    break
            if best is not None:
                break
        if best is None:
            raise Stuck(f"B grab: none of {tried} attempts worked: {why}")
        w0, hop, k, w2, tf = best[1]
        c.restore(base)
        for _ in range(w0):
            _fr(c, ())
        res = bgrab_try(c, k, w2, tf, hop)
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["bgrab"] = {"params": best[1], "tried": tried, **{k2: v for k2, v in res.items()}}
    r.log(f"[{r.name}] B grab: wait {w0} hop {hop} ride {k} wait2 {w2} fire {tf}: {res['rows']} rows to wx "
          f"{res['wx']}, Barrier at row {len(c.rows) - res['rows'] + res['got'][0]} ({tried} attempts)")
    r.marks.append(("bgot", len(c.rows) - res["rows"] + res["got"][0], c.f["fc"], res["got"][1], res["got"][2]))


T_DOOR = 0x16


def door_of(f):
    for e in f.enemies():
        if e["type"] == T_DOOR:
            return e
    return None


def boss_try(c, j1, phase, j2=None, band=(112, 144), above="Down", up_s=60, limit=330, log=None, hover=None):
    """Scripted door fight from a state shortly before the reveal scroll. Right is always held.
    j1      scroll frame of the first jump (None = never)
    j2      None = no further jump; a number = jump again when on the ground at screen x >= j2
    phase   a new B press on frames with t % 5 == phase (t counts from the first frame of the script)
    band    Y range in which an airborne shot is aimed forward (the core's height); higher up it is aimed
            `above` ("Down" = down-forward, "" = forward), lower it is aimed up-forward
    up_s    on the ground the shots are aimed up-forward from this scroll frame on
    Returns the number of rows until the door's HP is 0 (BOSS_DEFEATED set), or raises Fail."""
    n0 = len(c.rows)
    s = -1                       # frames since the scroll started
    t = 0
    jumps = 0
    while not c.f["bossdef"]:
        f = c.f
        if f["stop"] == 0xFF:
            if f["auto"] > 0:
                s = 95 - f["auto"]          # scroll frame, also when the script starts inside the scroll
            elif s < 0:
                s = 96
        g = grounded(f)
        want = {"Right"}
        if s >= 0:
            if g and c.can("A"):
                if jumps == 0 and j1 is not None and s >= j1:
                    want.add("A")
                    jumps += 1
                elif jumps > 0 and j2 is not None and f["x"] >= j2:
                    want.add("A")
                    jumps += 1
            air = (not g) or ("A" in want) or ("A" in c.pr.held and c.pr.must_hold("A"))
            if (t % 5) == phase and c.can("B"):
                want.add("B")
            if air:
                y = f["y"]
                if y < band[0]:
                    if above:
                        want.add(above)
                elif y > band[1]:
                    want.add("Up")
            elif s >= up_s:
                want.add("Up")
            if g and "A" not in want:
                # a soldier walking at Bill on the ground: a level volley (the Spread kills it in one hit)
                for e in f.enemies():
                    if (e["type"] == 0x05 and 0 < e["hp"] < 0xF0 and e["routine"] < 5 and 0 < e["x"] - f["x"] < 56
                            and abs(e["y"] - f["y"]) < 20):
                        want.discard("Up")
                        want.discard("Down")
                        if c.can("B"):
                            want.add("B")
                        break
            if hover is not None and g and "A" not in want and f["x"] >= hover:
                k = (t - phase) % 5
                if k in (0, 1):
                    want = {"Up", "Right"} | ({"B"} if "B" in want else set())
                elif k in (2, 3):
                    want = {"Left"} if f["x"] > hover else set()
                else:
                    want = set()
            if f["auto"] == 0:
                s += 1
        fr = _fr(c, want, log)
        t += 1
        if t > limit:
            raise Fail("door not dead in time")
    return len(c.rows) - n0


BOSS_GRID = [(j1, ph, j2, band, ab, hv) for j1 in (None, 40, 43, 45, 47, 50, 54, 58)
             for ph in range(5) for j2 in (None,) for band in ((112, 144),) for ab in ("Down",)
             for hv in ((None, 166) if j1 is None else (None,))]


def boss_proc2(r):
    """Runner Proc: the door fight by a parameter grid, then a refinement around the best."""
    c = r.c
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    best = None
    tried = 0
    seen = set()
    why = {}

    def run(par):
        nonlocal best, tried
        if par in seen:
            return
        seen.add(par)
        c.restore(base)
        tried += 1
        j1, ph, j2, band, ab, hv = par
        try:
            n = boss_try(c, j1, ph, j2, band, ab, hover=hv)
        except Fail as ex:
            r.frames_simulated += len(c.rows) - base["n"]
            k = f"{str(ex)[:12]} after {len(c.rows) - base['n']} rows at x {c.f['x']}"
            why[k] = why.get(k, 0) + 1
            return
        r.frames_simulated += n
        if best is None or n < best[0]:
            best = (n, par)

    try:
        for par in BOSS_GRID:
            run(par)
        if best is None:
            # emergency: earlier first jumps (something on the ground kills every line of the normal grid)
            for j1 in (18, 22, 26, 30, 34, 37):
                for ph in range(5):
                    for j2 in (None, 150):
                        run((j1, ph, j2, (112, 144), "Down", None))
        if best is None:
            raise Stuck(f"door: no scripted fight worked: {why}")
        for _ in range(2):
            j1b, phb, j2b, bandb, abb, hvb = best[1]
            near = [j1b] if j1b is None else [j1b - 1, j1b + 1, j1b - 3, j1b + 3]
            for j1 in near:
                for ph in range(5):
                    run((j1, ph, j2b, bandb, abb, hvb))
            j1b, phb, j2b, bandb, abb, hvb = best[1]
            if _ == 0:
                for hv in (164, 170):               # measured: hovering never beat the best jump line
                    run((j1b, phb, j2b, bandb, abb, hv))
            j1b, phb, j2b, bandb, abb, hvb = best[1]
            for j2 in (None, 150, 160, 168, 176):
                for band in ((112, 144), (106, 150), (116, 140)):
                    for ab in ("Down", ""):
                        run((j1b, phb, j2, band, ab, hvb))
        c.restore(base)
        j1, ph, j2, band, ab, hv = best[1]
        boss_try(c, j1, ph, j2, band, ab, hover=hv)
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["boss"] = {"rows": best[0], "params": list(best[1]), "tried": tried}
    r.log(f"[{r.name}] door: {best[0]} rows: first jump at scroll frame {j1}, fire phase {ph}, second jump {j2}, "
          f"band {band}, above {ab!r}, hover {hv} ({tried} attempts)")
    r.marks.append(("boss_killed", len(c.rows), c.f["fc"], c.f.wx, c.f["y"]))
