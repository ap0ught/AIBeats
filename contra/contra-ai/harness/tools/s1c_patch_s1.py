"""One-off patch of contra/stages/s1.py for rule v2 (purposeful fire, press budget). utf-8, temp file then rename;
the previous version is s1.py.backup_v2."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s1.py"
s = p.read_text(encoding="utf-8")


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''search on where to be when control is lost. See knowledge/s1_notes.md.
"""''', '''search on where to be when control is lost. See knowledge/s1_notes.md.

Rule v2 (2026-10-12; the version before it is s1.py.backup_v2): the run phase no longer mashes B. It presses B
  * for the two pickups (the S capsule in the jump at world X 1439, the planned shot at the R capsule),
  * at an enemy ahead (soldier, sniper, rotating gun, red turret) when a volley fired on this frame is predicted
    to hit it, the bullets already in flight do not cover its HP, and the look-ahead (s1_engine.Repair, engage=)
    has not found that leaving it alone is as fast and as safe,
  * on rows the repair search marked 'fire' / 'aim' (the old cadence, locally),
and only while the press plan (s1_common.Fights) still has room for the core fight. The core fight itself is
unchanged: fast fire, under the hard budget of s1_common.Pad.
"""''')
rep('''from .s1_common import Farm, Game, Pad, Ram, fire, log, save_seg
''', '''from .s1_common import Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, fire, log, press_report, save_seg
''')
rep('''BOSS_FROM = 3090                   # the run phase hands over to the boss search here (auto-scroll starts at 3104)
''', '''BOSS_FROM = 3090                   # the run phase hands over to the boss search here (auto-scroll starts at 3104)
CORE_PRESSES = 34                  # B presses the core fight may need (measured: 23-25 from the hand-over to HP 0)
PLAN = Fights([(BOSS_FROM, CORE_PRESSES)])
''')
# ---- shared helpers after would_hit
rep('''def aim_for(r: Ram, route: Route, row: int):
    """Aim to hold while B goes down: 'F', 'U', 'D' (running aims), 'DN', 'UP' (straight, only in a jump), or
    None = do not fire now (every aim would hit a capsule / pill box whose letter must not be picked up)."""
    px, py = r.x, r.y
    air = bool(r.jumping)
    opts = AIMS_AIR if air else AIMS_GROUND
    have_s = (r.weapon & 15) == 3
    rapid = bool(r.weapon & 0x10)
    targets, avoid, want, kill_behind = [], [], [], []
    for (s, ty, rt, hp, ex, ey, st, spr, attr) in r.enemies():
''', '''def pending_on(r: Ram, slot: int, tmax=50, box=12):
    """Player bullets in flight whose straight path meets the enemy in `slot` (its own motion extrapolated; the
    scroll moves both alike)."""
    m = r.m
    ex, ey = m[0x33E + slot], m[0x324 + slot]
    evx = m[0x508 + slot] + m[0x518 + slot] / 256.0
    evy = m[0x4E8 + slot] + m[0x4F8 + slot] / 256.0
    if evx >= 128:
        evx -= 256
    if evy >= 128:
        evy -= 256
    n = 0
    for s in range(10):
        if not m[0x388 + s] or m[0x438 + s] != 1:
            continue
        bx, by = m[0x3C8 + s], m[0x3B8 + s]
        vx = m[0x408 + s] + m[0x3E8 + s] / 256.0
        vy = m[0x3F8 + s] + m[0x3D8 + s] / 256.0
        if vx >= 128:
            vx -= 256
        if vy >= 128:
            vy -= 256
        for t in range(0, tmax):
            x, y = bx + vx * t, by + vy * t
            if x >= 251 or x < 5 or y >= 232 or y < 5:
                break
            if abs(x - (ex + evx * t)) <= box and abs(y - (ey + evy * t)) <= box:
                n += 1
                break
    return n


HP_COVER = 6           # bullets in flight on a target beyond which no further press is made for it


def pick_shot(r: Ram, route: Route, row_abs: int, targets, unsafe, reach=150):
    """The volley worth a press on this frame, or None. targets = [(slot, type, hp, x, y)] (hostile, alive).
    Nearest first: a target ahead that the look-ahead has not let pass, whose HP the bullets in flight do not
    cover yet, and that a volley fired now with one of the running aims is predicted to hit (and that aim does
    not open a carrier of an unwanted letter). Returns (aim, slot, type)."""
    px, py = r.x, r.y
    opts = AIMS_AIR if r.jumping else AIMS_GROUND
    cand = []
    for (s, ty, hp, ex, ey) in targets:
        dx, dy = ex - (px + 14), ey - (py - 4)
        if dx < -10 or dx > reach:
            continue
        cand.append((abs(dx) + abs(dy), s, ty, hp, ex, ey))
    cand.sort()
    for (_, s, ty, hp, ex, ey) in cand:
        if route.verdict(row_abs, s, ty) == "pass":
            continue
        if pending_on(r, s) >= min(hp, HP_COVER):
            continue
        order = sorted(("F", "U", "D"), key=lambda n: _ang((ex - (px + opts[n][0][0]), ey - (py + opts[n][0][1])), opts[n][1]))
        for n in order:
            if would_hit(r, n, s, box=12, grow=0.3) and not unsafe(n):
                return n, s, ty
    return None


def _sort_enemies(r: Ram):
    """(targets [(slot, type, hp, x, y)], avoid [slots], want [(x, y, slot)], kill_behind [slots]) - see aim_for."""
    px = r.x
    have_s = (r.weapon & 15) == 3
    rapid = bool(r.weapon & 0x10)
    targets, avoid, want, kill_behind = [], [], [], []
    for (s, ty, rt, hp, ex, ey, st, spr, attr) in r.enemies():
        a = attr & 7
        if ty == T_CAPSULE:
            if not have_s:
                if a == 3:
                    want.append((ex, ey, s))
                elif a in (2, 4):
                    avoid.append(s)
            elif a in (1, 2, 4):
                (kill_behind if ex <= px - 24 else avoid).append(s)
            elif a == 0 and not rapid:
                avoid.append(s)
        elif ty == T_PILLBOX and 0 < hp < 0xF0 and not (st & 0x80):
            if (have_s and a in (1, 2, 4)) or (not have_s and a == 2):
                avoid.append(s)
        elif ty in TARGETS and not (st & 0x80) and 0 < hp < 0xF0:
            targets.append((s, ty, hp, ex, ey))
    return targets, avoid, want, kill_behind


def shot_for(r: Ram, route: Route, row_abs: int):
    """Rule v2: the press worth making on this frame, (aim, enemy slot, enemy type), or None.
    1. the S capsule within pickup reach in a jump: straight down / up, so that the item spawns on Bill;
    2. a hostile target ahead (pick_shot). Nothing else is fired at: no capsule or pill box with an unwanted
       letter is opened, and a capsule that is behind Bill is left alone (its item would fall behind him)."""
    px, py = r.x, r.y
    have_s = (r.weapon & 15) == 3
    targets, avoid, want, kill_behind = _sort_enemies(r)
    if r.jumping:
        for (ex, ey, s) in want:
            if abs(ex - px) <= 10:
                if 0 < ey - py <= 44:
                    return "DN", s, T_CAPSULE
                if -44 <= ey - py < 0:
                    return "UP", s, T_CAPSULE
    if not have_s:
        avoid = avoid + [s for (_, _, s) in want]
    avoid = avoid + kill_behind
    return pick_shot(r, route, row_abs, targets, lambda n: any(would_hit(r, n, s) for s in avoid))


def aim_for(r: Ram, route: Route, row: int):
    """Aim to hold while B goes down: 'F', 'U', 'D' (running aims), 'DN', 'UP' (straight, only in a jump), or
    None = do not fire now (every aim would hit a capsule / pill box whose letter must not be picked up).
    Rule v2: used only on rows the repair search marked 'fire' (the old cadence fire)."""
    px, py = r.x, r.y
    air = bool(r.jumping)
    opts = AIMS_AIR if air else AIMS_GROUND
    have_s = (r.weapon & 15) == 3
    rapid = bool(r.weapon & 0x10)
    targets, avoid, want, kill_behind = [], [], [], []
    for (s, ty, rt, hp, ex, ey, st, spr, attr) in r.enemies():
''')
# ---- policy
old_pol = s[s.index("def policy(g: Game, route: Route):"):s.index("DEBUG = {\"g\": None, \"log\": []}")]
new_pol = '''def plan_room(g: Game):
    """Is there room in the press plan for one more B press of the run phase (headroom for the core fight)?"""
    return PLAN.room(g.pad, g.r.prog)


def _in_trial(route: Route):
    return "row0" in route.opts or "_look" in route.opts


def policy(g: Game, route: Route):
    r, pad, i = g.r, g.pad, len(g.rows)
    row_abs = i + route.opts.get("row0", 0)
    w = {"Right"}
    eds = route.over.get(i, ())
    if r.prog in route.jumps and not r.air and not any(e[0] == "nojump" for e in eds):
        w.add("A")
    do_fire = route.fire_at(r.prog) and not any(e[0] == "nofire" for e in eds)
    forced = any(e[0] in ("fire", "aim") for e in eds)       # the repair search's rows of cadence fire
    aim = route.aim_at(r.prog)
    for e in eds:
        if e[0] == "aim":
            aim = e[1]
    rs = route.opts.get("rshot")
    if rs:                                      # the one planned shot at the R capsule: (row, aim)
        t = rs[0] - route.opts.get("row0", 0)
        if t - 5 <= i < t:
            do_fire = False
        elif t <= i < t + 2:
            do_fire, forced, aim = True, True, rs[1]
    shot = None
    if do_fire:
        if pad.held["B"]:
            if pad.run["B"] < HOLD:
                w.add("B")                      # second frame of a press: the pad keeps its aim buttons down
        elif pad.rate_ok("B"):
            if not plan_room(g):
                if not _in_trial(route):
                    THROTTLED.add(row_abs)      # the press plan refuses: headroom for the core fight
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
            elif shot == "DN" and r.jumping:
                w.add("Down")
                w.discard("Right")              # in the air the last direction persists: no loss
            elif shot == "UP" and r.jumping:
                w.add("Up")
                w.discard("Right")
    for e in eds:
        if e[0] == "add":
            w.add(e[1])
        elif e[0] == "set":
            w = set(e[1])
            if "B*" in w:
                w.discard("B*")
                if pad.held["B"] or plan_room(g):
                    fire(pad, w)
    if DEBUG["g"] is g:
        DEBUG["log"].append((i, r.prog, r.x, r.y, shot, "+".join(sorted(w)),
                             [(e[1], e[8] & 7, e[4], e[5]) for e in r.enemies() if e[1] in (0, 2, 3)],
                             [(b[1], b[2]) for b in r.bullets()]))
    return w


def engage(g: Game, route: Route):
    """For the look-ahead of s1_engine.Repair: (slot, type) of the enemy the policy would open fire on with this
    row's press and that has no verdict yet, or None."""
    r, pad, i = g.r, g.pad, len(g.rows)
    if pad.held["B"] or not pad.rate_ok("B") or not route.fire_at(r.prog) or not plan_room(g):
        return None
    rs = route.opts.get("rshot")
    if rs and rs[0] - 5 <= i < rs[0] + 2:
        return None
    sh = shot_for(r, route, i)
    if sh is None or sh[2] not in TARGETS or route.verdict(i, sh[1], sh[2]) is not None:
        return None
    return sh[1], sh[2]


def shoot_planned(g: Game, w: set):
    """Cadence fire for the local search's duck / stand steps, within the press plan."""
    if g.pad.held["B"] or plan_room(g):
        fire(g.pad, w)
    return w


THROTTLED = set()                   # rows of the main run on which the press plan refused a press the pad allowed


'''
s = s.replace(old_pol, new_pol)
rep('''    for _ in range(delay):
        g.step({"Right"})
    while g.pad.held["B"] or not g.pad.can_press("B"):
        g.step({"Right"})
''', '''    for _ in range(delay):
        g.step({"Right"})
    while g.pad.held["B"] or not g.pad.rate_ok("B"):     # the burst rule only: the budget may refuse for long
        g.step({"Right"})
''')
rep('''        g = farm.g0
        g.load_file(start, pad=Pad.from_rows(history[-12:]) if history else None)
        f_pre = g.r.frame
        route = Route(JUMPS)
        rep = Repair(farm, policy, fail, tag=f"s1_{out}", plan=plan, mark=mark,
                     local=local_beam(policy, fail, tag=f"s1_{out}"))
        t0 = time.time()
        ok = rep.run(g, route, lambda g: g.r.prog >= BOSS_FROM or g.r.lr not in (3, 4), ring_len=50)
        r = g.r
        log(f"run phase: ok={ok} rows {len(g.rows)} ({r.summary()}), repairs {len(rep.repairs)}, evals {rep.evals}, "
            f"{time.time() - t0:.0f} s")
''', '''        g = farm.g0
        history = [tuple(r_) for r_ in (history or [])][-HISTORY_ROWS:]
        g.load_file(start, pad=Pad.from_rows(history) if history else None)
        f_pre = g.r.frame
        lag_pre = g.r.lagc
        route = Route(JUMPS)
        THROTTLED.clear()
        rep = Repair(farm, policy, fail, tag=f"s1_{out}", plan=plan, mark=mark,
                     local=local_beam(policy, fail, tag=f"s1_{out}", shoot=shoot_planned), engage=engage)
        t0 = time.time()
        ok = rep.run(g, route, lambda g: g.r.prog >= BOSS_FROM or g.r.lr not in (3, 4), ring_len=50)
        r = g.r
        thr = sorted(x for x in THROTTLED if x < len(g.rows))
        pr = press_report(g.rows, history)
        log(f"run phase: ok={ok} rows {len(g.rows)} ({r.summary()}), repairs {len(rep.repairs)}, evals {rep.evals}, "
            f"{time.time() - t0:.0f} s; B presses {pr['presses']} (most in 600 / 1800 rows: {pr['most_600']} / "
            f"{pr['most_1800']}), room left for the core fight {g.pad.room('B')}; look-ahead verdicts {rep.verdicts} "
            f"({rep.look_rows} rows looked ahead); press plan refused on {len(thr)} rows, pad on {g.pad.refused}")
        info["run_presses"] = pr
        info["verdicts"] = dict(rep.verdicts)
        info["plan_refused_rows"] = thr
        info["lag_run"] = g.r.lagc - lag_pre
''')
rep('''        info["frames"] = len(g.rows) - 1
        info["weapon"] = g.r.weapon
        log(f"stage 2's first frame after {len(g.rows)} rows: stage 1 = {len(g.rows) - 1} frames; weapon ${g.r.weapon:02x}, "
            f"lives {g.r.lives}, fc {g.r.fc}, rng {g.r.rng}")
''', '''        info["frames"] = len(g.rows) - 1
        info["weapon"] = g.r.weapon
        pr = press_report(g.rows, history)
        info["presses"] = pr
        info["pad_refused"] = g.pad.refused
        info["lag_total"] = g.r.lagc - lag_pre
        log(f"stage 2's first frame after {len(g.rows)} rows: stage 1 = {len(g.rows) - 1} frames; weapon ${g.r.weapon:02x}, "
            f"lives {g.r.lives}, fc {g.r.fc}, rng {g.r.rng}; B presses {pr['presses']}, most in 600 / 1800 rows "
            f"{pr['most_600']} / {pr['most_1800']}; presses refused by the budget {g.pad.refused}; lag frames "
            f"{info['lag_run']} in the run phase, {info['lag_total']} in all")
''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("s1.py patched")
