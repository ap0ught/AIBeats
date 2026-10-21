"""One-off patch of contra/stages/s5.py for rule v2 (purposeful fire, press budget). utf-8, temp file then rename;
the previous version is s5.py.backup_v2."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s5.py"
s = p.read_text(encoding="utf-8")


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''    lag     Repair5: a lag frame in the main run is a failure the repair search may fix by holding fire
"""''', '''    lag     Repair5: a lag frame in the main run is a failure the repair search may fix by holding fire

Rule v2 (2026-10-12; the version before it is s5.py.backup_v2): the run phases no longer mash B. They press B at
an enemy ahead (soldier, sniper, runner, diver, turret man) when a volley fired on this frame is predicted to
hit it, the bullets already in flight do not cover its HP, and the look-ahead (s1_engine.Repair, engage=) has
not found that leaving it alone is as fast and as safe; on rows the repair search marked 'fire' / 'aim'; and
only while the press plan (s1_common.Fights) keeps room for the fights ahead (two tanks, the UFO). The wait for
the UFO no longer fires. Tanks and UFO are unchanged: fast / planned fire under the hard budget of s1_common.Pad.
"""''')
rep('''from .s1_common import Farm, Game, Pad, Ram, fire, log, save_seg
from .s1_engine import Repair, Route, beam, local_beam, pit_ahead
from .s1 import AIMS_AIR, AIMS_GROUND, _ang, would_hit
''', '''from .s1_common import Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, fire, log, press_report, save_seg
from .s1_engine import Repair, Route, beam, local_beam, pit_ahead
from .s1 import AIMS_AIR, AIMS_GROUND, _ang, pick_shot, would_hit
''')
rep('''TARGETS = (T_SOLDIER, T_SNIPER, T_RUNNER, T_DIVER, T_TURRETMAN)
''', '''TARGETS = (T_SOLDIER, T_SNIPER, T_RUNNER, T_DIVER, T_TURRETMAN)

# The press plan: world X at which each fight begins and the B presses it may need (measured: 16 per tank, 10-11
# for the UFO). The run policy presses B only while every window keeps that much room for the fights ahead.
TANK_PRESSES, UFO_PRESSES = 22, 18
PLAN = Fights([(2432, TANK_PRESSES), (3456, TANK_PRESSES), (5240, UFO_PRESSES)])
THROTTLED = set()                   # rows of the main run on which the press plan refused a press the pad allowed


def plan_room(g: Game):
    return PLAN.room(g.pad, g.r.prog)


def _in_trial(route: Route):
    return "row0" in route.opts or "_look" in route.opts


def shot_for(r: Ram, route: Route, row_abs: int):
    """Rule v2: the press worth making on this frame, (aim, enemy slot, enemy type), or None (see s1.pick_shot)."""
    targets, avoid = [], []
    for (s_, ty, rt, hp, ex, ey, st, spr, attr) in r.enemies():
        a = attr & 7
        if ty == T_PILLBOX and 0 < hp < 0xF0 and not (st & 0x80) and a in (1, 2, 4):
            avoid.append(s_)
        elif ty == T_CAPSULE and a in (1, 2, 4):
            avoid.append(s_)
        elif ty in TARGETS and not (st & 0x80) and 0 < hp < 0xF0:
            targets.append((s_, ty, hp, ex, ey))
    return pick_shot(r, route, row_abs, targets, lambda n: any(would_hit(r, n, s_) for s_ in avoid))
''')
old_pol = s[s.index("def policy(g: Game, route: Route):"):s.index("def fail_hard(g: Game):")]
new_pol = '''def policy(g: Game, route: Route):
    r, pad, i = g.r, g.pad, len(g.rows)
    row_abs = i + route.opts.get("row0", 0)
    g.lag_ctx = (route.opts, _in_trial(route))           # read by fail(): which lag frames are accepted
    w = {"Right"}
    eds = route.over.get(i, ())
    if r.prog in route.jumps and not r.air and not any(e[0] == "nojump" for e in eds):
        w.add("A")
    if r.prog in TANK_LEDGES and r.y == 132 and not r.air and route.opts.get("ledge_jump", False) and jump_off_ledge(r):
        w.add("A")
    do_fire = route.fire_at(r.prog) and not any(e[0] == "nofire" for e in eds)
    forced = any(e[0] in ("fire", "aim") for e in eds)       # the repair search's rows of cadence fire
    aim = route.aim_at(r.prog)
    for e in eds:
        if e[0] == "aim":
            aim = e[1]
    shot = None
    if do_fire:
        if pad.held["B"]:
            if pad.run["B"] < HOLD:
                w.add("B")                      # second frame of a press: the pad keeps its aim buttons down
        elif pad.rate_ok("B"):
            if not plan_room(g):
                if not _in_trial(route):
                    THROTTLED.add(row_abs)      # the press plan refuses: headroom for the next fight
            else:
                if not _in_trial(route):
                    THROTTLED.discard(row_abs)
                if forced:
                    shot = aim_for(r, route, i) if aim == "auto" else aim
                else:
                    sh = shot_for(r, route, row_abs)
                    shot = sh[0] if sh else None
        if shot is not None:
            w.add("B")
            if shot == "U":
                w.add("Up")
            elif shot == "D":
                w.add("Down")
    for e in eds:
        if e[0] == "add":
            w.add(e[1])
        elif e[0] == "set":
            w = set(e[1])
            if "B*" in w:
                w.discard("B*")
                if pad.held["B"] or plan_room(g):
                    fire(pad, w)
    return w


def engage(g: Game, route: Route):
    """For the look-ahead of s1_engine.Repair: (slot, type) of the enemy the policy would open fire on with this
    row's press and that has no verdict yet, or None."""
    r, pad, i = g.r, g.pad, len(g.rows)
    if pad.held["B"] or not pad.rate_ok("B") or not route.fire_at(r.prog) or not plan_room(g):
        return None
    sh = shot_for(r, route, i)
    if sh is None or route.verdict(i, sh[1], sh[2]) is not None:
        return None
    return sh[1], sh[2]


def shoot_planned(g: Game, w: set):
    """Cadence fire for the local search's duck / stand steps, within the press plan."""
    if g.pad.held["B"] or plan_room(g):
        fire(g.pad, w)
    return w


'''
s = s.replace(old_pol, new_pol)
rep('''        c0 = [("opt", LAG_KEY + D, 0, True)]
        for n in (12, 25, 40, 55):
            for end in (D - 1, D - 8):
                if end - n >= t0:
                    c0.append(("nofire", end - n, n, None))
        for a in ("U", "D", "F"):
            if D - 26 >= t0:
                c0.append(("aim", D - 26, 25, a))
        return c0, [], []
''', '''        c0 = [("opt", LAG_KEY + D, 0, True)]
        for n in (12, 25, 40, 55):
            for end in (D - 1, D - 8):
                if end - n >= t0:
                    c0.append(("nofire", end - n, n, None))
        return c0, [], []                        # rule v2: an 'aim' stretch is cadence fire, no cure for lag
''')
rep('''    while g.pad.held["B"] or not g.pad.can_press("B"):
        g.step(set())

    def score(g):
        r = g.r
        e = ufo(r)
''', '''    while g.pad.held["B"] or not g.pad.rate_ok("B"):     # the burst rule only: the budget may refuse for long
        g.step(set())

    def score(g):
        r = g.r
        e = ufo(r)
''')
rep('''def run_to(farm: Farm, g: Game, route: Route, done, tag, info):
    rep = Repair5(farm, policy, fail, tag=tag, local=local_beam(policy, fail_hard, tag=tag))
    t0 = time.time()
    n0 = len(g.rows)
    ok = rep.run(g, route, done, ring_len=50)
    r = g.r
    log(f"{tag}: ok={ok} rows {n0}->{len(g.rows)} ({r.summary()}), repairs {len(rep.repairs)}, evals {rep.evals}, "
        f"{time.time() - t0:.0f} s")
    for x in rep.repairs:
        log("   ", x)
    info.setdefault("repairs", []).extend(str(x) for x in rep.repairs)
    return ok
''', '''def run_to(farm: Farm, g: Game, route: Route, done, tag, info):
    rep = Repair5(farm, policy, fail, tag=tag, local=local_beam(policy, fail_hard, tag=tag, shoot=shoot_planned),
                  engage=engage, fail_look=fail_hard)
    t0 = time.time()
    n0 = len(g.rows)
    lag0 = g.r.lagc
    ok = rep.run(g, route, done, ring_len=50)
    r = g.r
    nb = sum(1 for k in range(max(1, n0), len(g.rows)) if "B" in g.rows[k] and "B" not in g.rows[k - 1])
    log(f"{tag}: ok={ok} rows {n0}->{len(g.rows)} ({r.summary()}), repairs {len(rep.repairs)}, evals {rep.evals}, "
        f"{time.time() - t0:.0f} s; B presses {nb}, room left for the next fight {g.pad.room('B')}, in the last 600 / "
        f"1800 rows {g.pad.count('B', 600)} / {g.pad.count('B', 1800)}; look-ahead verdicts {rep.verdicts} "
        f"({rep.look_rows} rows looked ahead); lag frames {g.r.lagc - lag0}")
    for x in rep.repairs:
        log("   ", x)
    info.setdefault("repairs", []).extend(str(x) for x in rep.repairs)
    for k_, v_ in rep.verdicts.items():
        info.setdefault("verdicts", {})[k_] = info.get("verdicts", {}).get(k_, 0) + v_
    info["run_presses"] = info.get("run_presses", 0) + nb
    info["lag_run"] = info.get("lag_run", 0) + g.r.lagc - lag0
    return ok


def wait_for_ufo(g: Game, route: Route):
    """From the frame the boss auto-scroll starts to the frame the UFO exists (95 frames, fixed). Rule v2: no
    firing (the old solver mashed straight up here for nothing: 19 presses); if that gets Bill killed, the run
    policy's fire at targets, then the old cadence fire. Returns the name of what was played, or None."""
    tok = g.snap()
    ways = (("no fire", lambda: {"Right"}), ("policy", lambda: policy(g, route)),
            ("cadence fire", lambda: fire(g.pad, {"Right", "Up"})))
    for name, want in ways:
        g.restore(tok)
        ok = True
        while ufo(g.r) is None:
            g.step(want() if g.r.auto else {"Right"})
            if g.r.dead or len(g.rows) > 9000:
                ok = False
                break
        if ok:
            g.free(tok)
            return name
        log(f"boss: waiting for the UFO with '{name}' fails ({g.r.summary()})")
    g.free(tok)
    return None
''')
rep('''        g = farm.g0
        g.load_file(start, pad=Pad.from_rows(history[-12:]) if history else None)
        route = Route(JUMPS)
''', '''        g = farm.g0
        history = [tuple(r_) for r_ in (history or [])][-HISTORY_ROWS:]
        g.load_file(start, pad=Pad.from_rows(history) if history else None)
        lag_pre = g.r.lagc
        log(f"start {start}: {g.r.summary()}; press history {len(history)} rows, B presses in its last 600 / 1800 "
            f"rows {g.pad.count('B', 600)} / {g.pad.count('B', 1800)}")
        THROTTLED.clear()
        route = Route(JUMPS)
''')
rep('''        info["marks"]["auto"] = len(g.rows)
        g.save_file(f"s5/{out}_boss")
        while ufo(g.r) is None:
            g.step(fire(g.pad, {"Right", "Up"}) if g.r.auto else {"Right"})
            if g.r.dead or len(g.rows) > 9000:
                log("boss: died / no UFO while waiting")
                return None
        info["marks"]["ufo_created"] = len(g.rows)
''', '''        info["marks"]["auto"] = len(g.rows)
        g.save_file(f"s5/{out}_boss")
        info["ufo_wait"] = wait_for_ufo(g, route)
        if info["ufo_wait"] is None:
            log("boss: died / no UFO while waiting")
            return None
        info["marks"]["ufo_created"] = len(g.rows)
''')
rep('''        info["frames"] = len(g.rows) - 1
        info["weapon"] = g.r.weapon
        log(f"stage 6's first frame after {len(g.rows)} rows: stage 5 = {len(g.rows) - 1} frames; weapon ${g.r.weapon:02x}, "
            f"lives {g.r.lives}, fc {g.r.fc}, rng {g.r.rng}; marks {info['marks']}")
''', '''        info["frames"] = len(g.rows) - 1
        info["weapon"] = g.r.weapon
        pr = press_report(g.rows, history)
        info["presses"] = pr
        info["pad_refused"] = g.pad.refused
        info["plan_refused_rows"] = sorted(x for x in THROTTLED if x < len(g.rows))
        info["lag_total"] = g.r.lagc - lag_pre
        log(f"stage 6's first frame after {len(g.rows)} rows: stage 5 = {len(g.rows) - 1} frames; weapon ${g.r.weapon:02x}, "
            f"lives {g.r.lives}, fc {g.r.fc}, rng {g.r.rng}; marks {info['marks']}")
        log(f"B presses {pr['presses']} ({info.get('run_presses', 0)} in the run phases), most in 600 / 1800 rows "
            f"{pr['most_600']} / {pr['most_1800']} (history counted); presses refused by the pad's budget "
            f"{g.pad.refused}, by the press plan on {len(info['plan_refused_rows'])} rows; look-ahead verdicts "
            f"{info.get('verdicts')}; lag frames {info.get('lag_run', 0)} in the run phases, {info['lag_total']} in all; "
            f"UFO wait: {info.get('ufo_wait')}")
''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("s5.py patched")
