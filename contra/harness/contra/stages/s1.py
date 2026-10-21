"""Stage 1 (Jungle) solver: from the frame before stage 1's first frame to stage 2's first frame.

    python -m contra.stages.s1 <start state, e.g. s1/pre_w0> <out name, e.g. w0> [--open logs/s1/open_w0.inputs.txt]

Closed loop: route (jump positions in world X) + legal fire cadence + auto aim, with save-state repair around
deaths; the weapon pickups (S capsule on screen 4, R capsule on screen 9); a beam search on the boss wall; a small
search on where to be when control is lost. See knowledge/s1_notes.md.

Rule v2 (2026-10-12; the version before it is s1.py.backup_v2): the run phase no longer mashes B. It presses B
  * for the two pickups (the S capsule in the jump at world X 1439, the planned shot at the R capsule),
  * at an enemy ahead (soldier, sniper, rotating gun, red turret) when a volley fired on this frame is predicted
    to hit it, the bullets already in flight do not cover its HP, and the look-ahead (s1_engine.Repair, engage=)
    has not found that leaving it alone is as fast and as safe,
  * on rows the repair search marked 'fire' / 'aim' (the old cadence, locally),
and only while the press plan (s1_common.Fights) still has room for the core fight. The core fight itself is
unchanged: fast fire, under the hard budget of s1_common.Pad.
"""
from __future__ import annotations

import math
import sys
import time

from ..inputs import read_inputs, write_inputs
from ..emulator import LOGS_DIR
from .s1_common import (Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, WINDOWS, fire, log, press_report,
                        save_seg)
from .s1_engine import Repair, Route, beam, local_beam

# world X (screen*256 + scroll + player x) at which A is pressed. From the 1-player TAS's route (movie 4623M,
# read with tools/s1_trace_ref.py): 14 jumps and 3 ledge landings before the boss.
JUMPS = (743, 802, 1049, 1108, 1439, 2032, 2271, 2365, 2431, 2500, 2557, 2782, 2894, 2966)

T_ITEM, T_PILLBOX, T_CAPSULE, T_GUN, T_SOLDIER, T_SNIPER, T_TURRET = 0x00, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07
T_BOMBTURRET, T_DOOR = 0x10, 0x11
TARGETS = (T_SOLDIER, T_SNIPER, T_GUN, T_TURRET)
S_BY, R_BY = 1560, 3080            # world X by which S / S+Rapid must be held
BOSS_FROM = 3090                   # the run phase hands over to the boss search here (auto-scroll starts at 3104)
CORE_PRESSES = 34                  # B presses the core fight may need (measured: 23-25 from the hand-over to HP 0)
PLAN = Fights([(BOSS_FROM, CORE_PRESSES)])
DOOR_WX, DOOR_Y = 3232, 176        # the core: world X, screen Y (box +-11 px)

D45 = 0.7071
AIMS_GROUND = {"F": ((16, -5), (1.0, 0.0)), "U": ((13, -16), (D45, -D45)), "D": ((13, 6), (D45, D45))}
AIMS_AIR = {"F": ((16, 0), (1.0, 0.0)), "U": ((15, -15), (D45, -D45)), "D": ((15, 15), (D45, D45)),
            "DN": ((0, 16), (0.0, 1.0)), "UP": ((0, -16), (0.0, -1.0))}


def _ang(v, d):
    n = math.hypot(*v)
    if n < 4:
        return 0.0
    c = (v[0] * d[0] + v[1] * d[1]) / n
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


PELLETS_S = (0.0, 11.25, -11.25, 22.5, -22.5)


def would_hit(r: Ram, aim: str, slot: int, tmax=46, box=13, grow=0.6):
    """Would a volley fired now with this aim hit the enemy in `slot`? Straight-line pellets (S: five, 11.25
    degrees apart) against the enemy's position extrapolated with its current velocity; the Y margin grows with
    time because capsules fly a sine. Screen X of everything drifts -1 px a frame while the screen scrolls."""
    m = r.m
    air = bool(r.jumping)
    (mx, my), d = (AIMS_AIR if air else AIMS_GROUND)[aim]
    have_s = (r.weapon & 15) == 3
    rapid = bool(r.weapon & 0x10)
    speed = (3.48 if rapid else 2.99) if have_s else (4.0 if rapid else 3.0)
    scroll = 1.0 if r.x >= 128 else 0.0
    ex, ey = m[0x33E + slot], m[0x324 + slot]
    evx = m[0x508 + slot] + m[0x518 + slot] / 256.0
    evy = m[0x4E8 + slot] + m[0x4F8 + slot] / 256.0
    if evx >= 128:
        evx -= 256
    if evy >= 128:
        evy -= 256
    evx -= scroll
    base = math.atan2(d[1], d[0])
    x0, y0 = r.x + mx, r.y + my
    for da in (PELLETS_S if have_s else (0.0,)):
        a = base + math.radians(da)
        vx, vy = speed * math.cos(a) - scroll, speed * math.sin(a)
        for t in range(0, tmax):
            x, y = x0 + vx * t, y0 + vy * t
            if x >= 251 or x < 5 or y >= 232 or y < 5:
                break
            cx, cy = ex + evx * t, ey + evy * t
            if abs(x - cx) <= box + 1 and abs(y - cy) <= box + min(20.0, grow * t):
                return True
    return False


def pending_on(r: Ram, slot: int, tmax=50, box=12):
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
        a = attr & 7
        if ty == T_CAPSULE:
            if not have_s:
                if a == 3:
                    want.append((ex, ey, s))
                elif a in (2, 4):
                    avoid.append(s)
            elif a in (1, 2, 4):
                # its item is harmless once the capsule is well behind the player: he outruns it
                (kill_behind if ex <= px - 24 else avoid).append(s)
            elif a == 0 and not rapid:
                avoid.append(s)                    # shot only by the planned 'rshot' (see policy)
        elif ty == T_PILLBOX and 0 < hp < 0xF0 and not (st & 0x80):
            if (have_s and a in (1, 2, 4)) or (not have_s and a == 2):
                avoid.append(s)
        elif ty in TARGETS and not (st & 0x80) and 0 < hp < 0xF0:
            targets.append((ex, ey, ty))
    # 1. the S capsule within pickup reach in a jump: straight down / up so the item spawns on the player
    if air:
        for (ex, ey, s) in want:
            if abs(ex - px) <= 10:
                if 0 < ey - py <= 44:
                    return "DN"
                if -44 <= ey - py < 0:
                    return "UP"
    if not have_s:                                  # ... and it must not be shot from anywhere else
        avoid += [s for (_, _, s) in want]

    def unsafe(name):
        return any(would_hit(r, name, s) for s in avoid)

    # 2. an unwanted capsule that is behind: a straight-down volley in a jump reaches back and below
    if air and kill_behind and not unsafe("DN"):
        if any(would_hit(r, "DN", s, box=10, grow=0.0) for s in kill_behind):
            return "DN"
    order = ["F", "U", "D"]
    tgt = None
    bd = 1e9
    for (ex, ey, ty) in targets:
        dx, dy = ex - (px + 14), ey - (py - 4)
        if dx < -10 or dx > 150:
            continue
        d = abs(dx) + abs(dy)
        if d < bd:
            tgt, bd = (ex, ey), d
    if tgt is not None:
        order.sort(key=lambda n: _ang((tgt[0] - (px + opts[n][0][0]), tgt[1] - (py + opts[n][0][1])), opts[n][1]))
    for n in order:
        if not unsafe(n):
            return n
    return None


def plan_room(g: Game):
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


def sight(g: Game):
    """For s1_engine.Repair: the hostile targets present, as (slot, type)."""
    return [(t[0], t[1]) for t in _sort_enemies(g.r)[0]]


def shoot_planned(g: Game, w: set):
    """Cadence fire for the local search's duck / stand steps, within the press plan."""
    if g.pad.held["B"] or plan_room(g):
        fire(g.pad, w)
    return w


THROTTLED = set()                   # rows of the main run on which the press plan refused a press the pad allowed


DEBUG = {"g": None, "log": []}


def fail(g: Game):
    r = g.r
    if r.dead:
        return "death"
    if r.water:
        return "water"
    if r.y >= 0xD8 and r.lr == 4:
        return "pit"
    if r.prog >= S_BY and (r.weapon & 15) != 3:
        return f"weapon ${r.weapon:02x}"
    if r.prog >= R_BY and r.weapon != 0x13:
        return "noR"
    return None


RLOG = {}                           # row -> (x, y, jumping, capsule x, capsule y) of the main game while the R capsule lives


def mark(g: Game):
    r = g.r
    if r.prog > 2300:
        for e in r.find(T_CAPSULE):
            if (e[8] & 7) == 0:
                RLOG[len(g.rows)] = (r.x, r.y, bool(r.jumping), e[4], e[5])
                return "rcap"
    return None


def plan(g, route, D, why, marks):
    """No Rapid by the deadline: try one planned shot at the R capsule, at every row and aim whose fan covers it
    on the recorded pass; the item must then be collected on the way (no extra jump)."""
    if why == "noR" and "rcap" in marks:
        i0 = marks["rcap"][0]
        cands = []
        for t in sorted(RLOG):
            if t < i0 + 5 or t >= D or (t - i0) % 2:
                continue
            px, py, air, ex, ey = RLOG[t]
            opts = AIMS_AIR if air else AIMS_GROUND
            for n, ((mx, my), d) in opts.items():
                v = (ex - (px + mx), ey - (py + my))
                dist = math.hypot(*v)
                if dist <= 150 and (_ang(v, d) <= 26 or dist <= 14):
                    cands.append(("opt", "rshot", 0, (t, n)))
        log(f"   R capsule: {len(cands)} planned-shot candidates over rows {i0}..{D}")
        return [("rcap", cands)]
    return None


# ------------------------------------------------------------------------------------------------ boss wall
def door(r: Ram):
    for e in r.enemies():
        if e[1] == T_DOOR:
            return e
    return None


def door_hp(r: Ram):
    if r.bossdef:
        return 0
    e = door(r)
    return e[3] if e else 32


def pending_hits(r: Ram):
    """Player bullets whose straight path crosses the core's box (the box and the bullets get the same scroll)."""
    m = r.m
    e = door(r)
    cx = e[4] if e else DOOR_WX - r.scr
    wait = 0 if e else max(0, 2992 - r.scr)          # frames until the door exists (created at screen 11 offset $B0)
    if cx > 300:
        return 0
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
        for t in range(1, 60):
            x, y = bx + vx * t, by + vy * t
            if x >= 251 or y >= 232 or y < 5 or x < 5:
                break
            if t >= wait and cx - 11 <= x < cx + 11 and DOOR_Y - 11 <= y < DOOR_Y + 11 and abs(cx - x) < 128:
                n += 1
                break
    return n


BOSS_ACTIONS = ("RD", "RF", "RU", "PR", "P", "N")
BOSS_ACTIONS_GROUND = BOSS_ACTIONS + ("JD", "JF")
PRONE_BOX = (113, 142, 168, 181)       # x0, x1, y0, y1: where a bomb hits Bill lying at the right end of the ledge


def bomb_danger(r: Ram, horizon=75):
    """Number of the wall's bombs (enemy bullets with collision code 5: ballistic, gravity 1/16 px per frame^2)
    whose path comes down through the spot where the core is shot from. Their launch speed is RANDOM_NUM & 3;
    the slow ones land exactly there about 45 frames after the launch, too late to see with a short lookahead."""
    m = r.m
    n = 0
    scroll_left = r.auto
    for s in range(16):
        if not m[0x4B8 + s] or m[0x528 + s] != 0x01 or (m[0x588 + s] & 0x0F) != 5:
            continue
        x, y = float(m[0x33E + s]), float(m[0x324 + s])
        vx = m[0x508 + s] + m[0x518 + s] / 256.0
        vy = m[0x4E8 + s] + m[0x4F8 + s] / 256.0
        if vx >= 128:
            vx -= 256
        if vy >= 128:
            vy -= 256
        for t in range(horizon):
            x += vx - (1.0 if t < scroll_left else 0.0)
            y += vy
            vy += 0.0625
            if y > 200 or x < 8:
                break
            if PRONE_BOX[0] <= x <= PRONE_BOX[1] and PRONE_BOX[2] <= y <= PRONE_BOX[3]:
                n += 1
                break
    return n


def boss_rows(g: Game, a: str, k: int):
    """RD/RF/RU run right firing down-right / forward / up-right; PR = prone shot then 3 steps right; P = stay
    prone firing; N = run without firing; JD/JF = jump right firing down-right / forward."""
    w = set()
    if a in ("RD", "RF", "RU", "N", "JD", "JF"):
        w.add("Right")
    if a == "PR" and k >= 2:
        w.add("Right")
    if a in ("JD", "JF") and k < 2:
        w.add("A")
    if a != "N" and k < 2:
        w.add("B")
        if a in ("RD", "JD"):
            w.add("Down")
        elif a == "RU":
            w.add("Up")
        elif a == "PR":
            w.add("Down")
    if a == "P":
        w.add("Down")
    return w


def boss_fight(g: Game, width=8, delay=0, jump_at=None, air_plan=None, pre_fire=True):
    """Beam search from the hand-over point to the frame the core's HP reaches 0. `delay` frames are run first
    without firing (a different firing phase: another roll of the wall's bombs and bullets). jump_at = world X of
    one forced jump from the top ledge straight down to the ledge in front of the core (instead of walking down
    the two steps, where the first bomb crosses); None = the search decides."""
    for _ in range(delay):
        g.step({"Right"})
    while g.pad.held["B"] or not g.pad.rate_ok("B"):     # the burst rule only: the budget may refuse for long
        g.step({"Right"})
    state = {"jumped": False}
    plan_ = None if air_plan is None else set(air_plan) | {x + 1 for x in air_plan}

    def air_n(r):
        """Frames since the take-off of the jump from the top ledge (from the 16-bit Y velocity), or None."""
        if not r.jumping:
            return None
        v = r.m[0xC6] * 256 + r.m[0xC4]
        if v >= 32768:
            v -= 65536
        return (v + 1040) // 35

    def actions(g):
        r = g.r
        if plan_ is not None and r.jumping:
            return ("AIR",)
        if not pre_fire and r.y == 100 and not r.air:
            return ("N",) if (jump_at is None or r.prog < jump_at) else ("JN",)
        if r.air:
            return BOSS_ACTIONS
        if jump_at is not None and r.y == 100:
            if r.prog >= jump_at:
                return ("JD", "JF")
            return BOSS_ACTIONS
        return BOSS_ACTIONS_GROUND if jump_at is None else BOSS_ACTIONS

    def score(g):
        r = g.r
        return (door_hp(r) - min(pending_hits(r), 6) * 0.9 + 6.0 * bomb_danger(r), -r.prog)

    def dedupe(g):
        r = g.r
        return (door_hp(r), r.prog, r.y, tuple(r.bullets()))

    def rows_(g, a, k):
        if a == "AIR":                              # scripted jump: down-right volleys on the planned air frames
            w = {"Right"}
            n = air_n(g.r)
            if n is not None and (n + 1) in plan_:
                w |= {"Down", "B"}
            return w
        if a == "JN":
            return {"Right", "A"} if k < 2 else {"Right"}
        return boss_rows(g, a, k)

    res = beam(g, actions, rows_, score, lambda g: door_hp(g.r) == 0, width=width, max_steps=90,
               dedupe=dedupe, fail=lambda g: g.r.dead, tag=f"s1 boss w{width} d{delay} j{jump_at}", verbose=False,
               lookahead=[("P",), ("RF",), ("PR",), ("N",)], look_steps=5, max_seconds=420)
    return res


LEDGE_END_WX = 3199        # right end of the ledge in front of the core (world X; standing Y 164)


def boss_script(g: Game, jx: int, stop: int, toff: int, ph: int = 0, limit: int = 260):
    """Second-pass scripted boss fight from the hand-over point to the frame the core's HP is 0.
    Run right firing down-right at the legal cadence; jump from the top ledge at world X jx (72 frames in the
    air, landing on the ledge in front of the core); stop firing `stop` frames after the take-off (so that the
    pellets that miss have left the screen and all ten slots are free at the landing); on the ledge fire prone
    (Down + B two frames) and step right in the three frames between presses until its right end; `toff`
    frames after the landing walk off the ledge and keep firing while falling in front of the core (prone
    height while Y <= 177, standing height below). ph = frames to wait before the first prone press.
    Returns rows played, or None (death / too slow)."""
    n0 = len(g.rows)
    pad = g.pad
    k_jump = landed = None
    wait = ph
    while True:
        k = len(g.rows) - n0
        r = g.r
        if door_hp(r) == 0:
            return k
        if r.dead or k >= limit:
            return None
        w = set()
        if landed is None and not (k_jump is not None and not r.air and k > k_jump + 5):
            w.add("Right")
            if k_jump is None and not r.air and r.prog >= jx:
                k_jump = k
            if k_jump is not None and k in (k_jump, k_jump + 1):
                w.add("A")
            if k_jump is None or k - k_jump < stop:
                fire(pad, w)
                if "B" in w:
                    w.add("Down")
        else:
            if landed is None:
                landed = k
            t = k - landed
            newb = (not pad.held["B"]) and pad.can_press("B")
            holdb = pad.held["B"] and pad.run["B"] < 2
            if t >= toff or r.air:                   # walk off the ledge / falling in front of the core
                if newb or holdb:
                    w.add("B")
                    if r.y <= 177:
                        w.add("Down")
                    else:
                        w.add("Right")
                else:
                    w.add("Right")
            elif holdb or (newb and wait <= 0):
                w |= {"Down", "B"}
            else:
                if newb:
                    wait -= 1
                if r.prog < LEDGE_END_WX:
                    w.add("Right")
                else:
                    w.add("Down")
        g.step(w)
        if g.r.dead:
            return None


def boss_fight2(farm: Farm, g: Game, st, pad: Pad, rows0, tag="s1"):
    """Grid search over boss_script's parameters on all emulators. Returns all rows (rows0 + the fight) of the
    fastest kill, or None."""
    def ev(gg, job):
        keep_ = gg.rows
        try:
            gg.load_file(st, pad)
            return boss_script(gg, *job)
        finally:
            gg.rows = keep_
    jobs = [(jx, stop, toff, ph) for jx in (3105, 3107, 3109, 3111, 3113, 3115, 3117, 3121) for stop in (44, 54, 64)
            for toff in (14, 19, 24, 29, 999) for ph in (0, 1)]
    res = farm.map(ev, jobs)
    ok = sorted((r_, i) for i, r_ in enumerate(res) if r_ is not None)
    log(f"boss scripts (jump X, stop firing, walk off, wait) -> rows to the kill: {len(ok)}/{len(jobs)} survive; best "
        + ", ".join(f"{jobs[i]}={r_}" for r_, i in ok[:6]))
    if not ok:
        return None
    g.load_file(st, pad, rows=rows0)
    n = boss_script(g, *jobs[ok[0][1]])
    if n != ok[0][0]:
        log(f"boss script: replay on the main emulator gave {n}, the trial {ok[0][0]}")
        if n is None:
            return None
    return list(g.rows)


# ------------------------------------------------------------------------------------------------ row refinement
def row_intervals(rows):
    """rows -> [(button, first row, last row + 1)] for every press, in row order."""
    out = []
    open_ = {}
    for i, r_ in enumerate(list(rows) + [()]):
        for b in list(open_):
            if b not in r_:
                out.append((b, open_.pop(b), i))
        for b in r_:
            if b not in open_:
                open_[b] = i
    out.sort(key=lambda t: (t[1], t[0]))
    return out


def rows_from_intervals(iv, n, pad: Pad):
    """Rows 0..n-1 from press intervals, made legal by a copy of `pad` (the press history before row 0)."""
    want = [set() for _ in range(n)]
    for (b, a, e) in iv:
        for i in range(max(0, a), min(n, e)):
            want[i].add(b)
    pd = pad.copy()
    out = []
    for w in want:
        row = pd.legal(w)
        pd.push(row)
        out.append(row)
    return out


def refine_rows(farm: Farm, st, pad: Pad, rows, hp_of, passes=2, extra=3, tag="refine", max_moves=160, block_span=70):
    """Hill climbing in the emulator on a fight that is already solved. rows = the rows from saved state `st`
    (press history `pad`) to the frame hp_of(ram) reaches 0. Every press becomes an interval; single changes
    (a press 1-2 rows earlier / later, a direction held 1-2 rows longer / shorter at either end, a B press
    dropped) are replayed on all emulators; the change that kills soonest (ties: least HP five rows before the
    old kill) is kept, until nothing improves. A death is a failure. Returns rows at least as good."""
    n_best = len(rows)
    iv = row_intervals(rows)

    def ev(gg, job):
        iv_, n_ref = job
        keep_ = gg.rows
        try:
            gg.load_file(st, pad)
            rr = rows_from_intervals(iv_, n_ref + extra, pad)
            cp = max(0, n_ref - 5)
            gg.run_raw(rr[:cp])
            if gg.r.dead:
                return (10 ** 6, 99)
            hp_cp = hp_of(gg.r)
            if hp_cp == 0:
                gg.load_file(st, pad)
                for k in range(cp):
                    gg.step_raw(rr[k])
                    if gg.r.dead:
                        return (10 ** 6, 99)
                    if hp_of(gg.r) == 0:
                        return (k + 1, 0)
                return (cp, 0)
            for k in range(cp, len(rr)):
                gg.step_raw(rr[k])
                if gg.r.dead:
                    return (10 ** 6, hp_cp)
                if hp_of(gg.r) == 0:
                    return (k + 1, hp_cp)
            return (10 ** 5, hp_cp)
        finally:
            gg.rows = keep_

    def moves(iv_):
        out = []
        for i, (b, a, e) in enumerate(iv_):
            def put(t):
                out.append(iv_[:i] + [t] + iv_[i + 1:])
            for d in (-2, -1, 1, 2):
                if a + d >= 0:
                    put((b, a + d, e + d))
            if b in ("Left", "Right", "Up", "Down"):
                for d in (-2, -1, 1, 2):
                    if a + d >= 0 and a + d < e:
                        put((b, a + d, e))
                    if e + d > a:
                        put((b, a, e + d))
            if b == "B":
                out.append(iv_[:i] + iv_[i + 1:])
        if len(out) > max_moves:                      # keep the changes nearest the end of the fight
            out = out[-max_moves:]
        # everything from row r on played 1..3 rows earlier (a beam search in 5-row steps leaves such slack,
        # e.g. between a landing and the first shot), or 1 row later
        last = max(e for (_, _, e) in iv_)
        for r in range(max(1, last - block_span), last - 3, 2):
            for d in (-3, -2, -1, 1):
                out.append([(b, a + d, e + d) if a >= r else ((b, a, e + d) if e > r else (b, a, e)) for (b, a, e) in iv_])
        return out

    cur = farm.map(ev, [(iv, n_best)])[0]
    if cur[0] != n_best:
        log(f"   {tag}: the interval form replays to row {cur[0]}, the search gave {n_best}; not refining")
        return rows
    t0 = time.time()
    for it in range(passes):
        cands = moves(iv)
        res = farm.map(ev, [(c, n_best) for c in cands])
        best = min(range(len(cands)), key=lambda i: res[i])
        if res[best] >= cur:
            break
        iv = cands[best]
        if res[best][0] < n_best:
            n_best = res[best][0]
            cur = farm.map(ev, [(iv, n_best)])[0]
        else:
            cur = res[best]
        log(f"   {tag} pass {it + 1}: {len(cands)} changes tried, kill row {cur[0]} (HP {cur[1]} five rows earlier), "
            f"{time.time() - t0:.0f} s")
    return rows_from_intervals(iv, n_best, pad)


# ------------------------------------------------------------------------------------------------ exit
def exit_want(g: Game, strat, k, c):
    """Buttons wanted on row k after the kill; c = row (same count) on which control is lost with strategy 'ground'."""
    r = g.r
    kind = strat[0]
    if kind == "ground":                       # run to the wall and wait there
        return {"Right"}
    if kind == "jump":                         # ... and jump right d frames before control is lost
        w = {"Right"}
        if k in (c - strat[1], c - strat[1] + 1):
            w.add("A")
        return w
    if kind == "ledge":                        # wait at screen X strat[2] on the Y=164 ledge (X 96..127), walk
        if k >= c - strat[1]:                  # off it d frames before control is lost
            return {"Right"}
        if r.air:
            return set()
        if r.y == 164:
            return {"Right"} if r.x < strat[2] else ({"Left"} if r.x > strat[2] else set())
        # on the ground under the ledge: go under it and jump straight up through it
        if r.x > 124:
            return {"Left"}
        if r.x < 104:
            return {"Right"}
        return {"A"}
    if kind == "stop":                         # stand still at screen X strat[1]
        return {"Right"} if r.x < strat[1] else set()
    return set()


def exit_eval(g: Game, job):
    state, pad, strat, c, limit = job
    g.load_file(state, pad)
    k = 0
    lost = None
    while g.r.bossdef != 2 and k < limit:
        w = exit_want(g, strat, k, c) if g.r.lr != 9 else set()
        g.step(w)
        k += 1
        if lost is None and g.r.lr == 9:
            lost = k
        if g.r.dead:
            return {"strat": strat, "frames": 10 ** 6, "lost": lost, "x": g.r.x}
    return {"strat": strat, "frames": k if g.r.bossdef == 2 else 10 ** 6, "lost": lost, "x": g.r.x}


def exit_search(farm: Farm, g: Game, tag="s1"):
    """From the frame the core dies: where to be when control is lost so that the scripted walk into the door
    is shortest. Plays the best strategy on g up to the frame Bill is hidden (BOSS_DEFEATED_FLAG = 2)."""
    st = g.save_file(f"tmp/{tag}_exit")
    pad = g.pad.copy()
    base = exit_eval(farm.g0 if farm.g0 is not g else g, (st, pad, ("ground",), 10 ** 6, 900)) if False else None
    keep = g.rows
    r0 = exit_eval(g, (st, pad, ("ground",), 10 ** 6, 900))
    g.rows = keep
    c = r0["lost"]
    strats = [("ground",)]
    strats += [("jump", d) for d in (1, 2, 3, 4, 6, 8, 10, 14, 18, 24, 30, 38, 46, 54, 58, 60)]
    for xs in (127, 126, 125, 124, 120):
        strats += [("ledge", d, xs) for d in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24)]
    strats += [("stop", x) for x in (128, 132, 136, 140, 143)]
    jobs = [(st, pad, s_, c, 900) for s_ in strats]

    def ev(gg, job):
        keep_ = gg.rows
        try:
            return exit_eval(gg, job)
        finally:
            gg.rows = keep_
    res = farm.map(ev, jobs)
    res.sort(key=lambda x: x["frames"])
    log(f"exit: control lost {c} rows after the kill; ground = {r0['frames']} rows to hidden; best "
        + ", ".join(f"{x['strat']}={x['frames']}" for x in res[:6]))
    best = res[0]
    g.load_file(st, pad, rows=keep)
    k = 0
    while g.r.bossdef != 2:
        g.step(exit_want(g, best["strat"], k, c) if g.r.lr != 9 else set())
        k += 1
    return best, res


# ------------------------------------------------------------------------------------------------ whole stage
def solve(start="s1/pre_w0", out="w0", n=3, history=None, width=8, refine=0, windows=WINDOWS):
    """history = the real rows before the solver's first row (at least the last HISTORY_ROWS of them): the press
    budget counts them. windows = the budget's ((rows, most presses), ...), rule v2 by default."""
    farm = Farm(n, name=f"s1_{out}")
    info = {"start": start}
    try:
        g = farm.g0
        history = [tuple(r_) for r_ in (history or [])][-HISTORY_ROWS:]
        g.load_file(start, pad=Pad.from_rows(history, windows))
        info["windows"] = [list(x) for x in windows]
        f_pre = g.r.frame
        lag_pre = g.r.lagc
        route = Route(JUMPS)
        THROTTLED.clear()
        rep = Repair(farm, policy, fail, tag=f"s1_{out}", plan=plan, mark=mark,
                     local=local_beam(policy, fail, tag=f"s1_{out}", shoot=shoot_planned), engage=engage, sight=sight)
        t0 = time.time()
        ok = rep.run(g, route, lambda g: g.r.prog >= BOSS_FROM or g.r.lr not in (3, 4), ring_len=50)
        r = g.r
        thr = sorted(x for x in THROTTLED if x < len(g.rows))
        pr = press_report(g.rows, history, windows=windows or WINDOWS)
        log(f"run phase: ok={ok} rows {len(g.rows)} ({r.summary()}), repairs {len(rep.repairs)}, evals {rep.evals}, "
            f"{time.time() - t0:.0f} s; B presses {pr['presses']} (most in 600 / 1800 rows: {pr.get('most_600')} / "
            f"{pr.get('most_1800')}), room left for the core fight {g.pad.room('B')}; look-ahead verdicts {rep.verdicts} "
            f"({rep.look_rows} rows looked ahead); press plan refused on {len(thr)} rows, pad on {g.pad.refused}")
        info["run_presses"] = pr
        info["verdicts"] = dict(rep.verdicts)
        info["plan_refused_rows"] = thr
        info["lag_run"] = g.r.lagc - lag_pre
        for x in rep.repairs:
            log("   ", x)
        info["repairs"] = [str(x) for x in rep.repairs]
        info["run_rows"] = len(g.rows)
        if not ok:
            save_seg(f"s1/{out}_partial", g.rows, info)
            return None
        st_boss = g.save_file(f"s1/{out}_boss")
        pad_boss, rows_boss = g.pad.copy(), list(g.rows)
        t1 = time.time()

        def variant(gg, job):
            w_, d_, j_ = job
            gg.load_file(st_boss, pad_boss, rows=rows_boss)
            res_ = boss_fight(gg, width=w_, delay=d_, jump_at=j_)
            return None if res_ is None else list(gg.rows)
        # the walk down the two steps (forced jump None) crosses the first bomb's path and was 30+ frames slower
        # in every try; the variants differ in where the jump from the top ledge starts and in the firing phase
        # second pass: (.., 0, 3125) never won in six solves and was replaced by one more firing phase at 3113
        # (the search's 5-frame steps should fall on the landing frame). Jumps from 3109 / 3105 land sooner but
        # the search then often runs into its time limit (measured: None after 420 s), so they are not used.
        # rule v2: three more firing phases (the kill row moves by 3-6 frames with the wall's bomb rolls, and the
        # quiet run phase no longer hands over in a random firing phase)
        jobs = [(width, 3, 3113), (width, 0, 3113), (width, 0, 3121), (width, 1, 3113), (width, 2, 3117),
                (width + 2, 0, 3121), (width, 4, 3113), (width, 2, 3113), (width + 2, 3, 3113)]
        outs = farm.map(variant, jobs)
        log("boss variants (width, delay, forced jump) -> kill row: "
            + ", ".join(f"{j}: {None if o is None else len(o)}" for j, o in zip(jobs, outs)))
        outs = [o for o in outs if o is not None]
        if not outs:
            log("boss: no kill found")
            g.load_file(st_boss, pad_boss, rows=rows_boss)
            save_seg(f"s1/{out}_partial", g.rows, info)
            return None
        best_rows = min(outs, key=len)
        if refine:
            part = [tuple(r_) for r_ in best_rows[len(rows_boss):]]
            better = refine_rows(farm, st_boss, pad_boss, part, door_hp, passes=refine, tag="boss refine")
            if len(better) < len(part):
                g.load_file(st_boss, pad_boss, rows=rows_boss)
                g.run_raw(better)
                if door_hp(g.r) == 0 and not g.r.dead:
                    log(f"boss refined: kill row {len(best_rows)} -> {len(rows_boss) + len(better)}")
                    best_rows = rows_boss + better
                else:
                    log("boss refine: the refined rows do not replay on the main emulator; keeping the search result")
        g.load_file(st_boss, pad_boss, rows=rows_boss)
        g.run_raw(best_rows[len(rows_boss):])
        assert door_hp(g.r) == 0, "boss replay diverged"
        info["boss_kill_row"] = len(g.rows)
        log(f"boss: core dead at row {len(g.rows)} (t = {len(g.rows) - 1}), search {time.time() - t1:.0f} s; {g.r.summary()}")
        g.save_file(f"s1/{out}_kill")
        save_seg(f"s1/{out}_tokill", g.rows, info)
        best, allres = exit_search(farm, g, tag=f"s1_{out}")
        info["exit"] = str(best)
        info["hidden_row"] = len(g.rows)
        lag0 = g.r.lagc
        while not (g.r.level == 1 and g.r.lr == 4):
            g.step(())
            if len(g.rows) > 6000:
                log("exit: stage 2 never started")
                return None
        info["frames"] = len(g.rows) - 1
        info["weapon"] = g.r.weapon
        pr = press_report(g.rows, history, windows=windows or WINDOWS)
        info["presses"] = pr
        info["pad_refused"] = g.pad.refused
        info["lag_total"] = g.r.lagc - lag_pre
        log(f"stage 2's first frame after {len(g.rows)} rows: stage 1 = {len(g.rows) - 1} frames; weapon ${g.r.weapon:02x}, "
            f"lives {g.r.lives}, fc {g.r.fc}, rng {g.r.rng}; B presses {pr['presses']}, most in 600 / 1800 rows "
            f"{pr.get('most_600')} / {pr.get('most_1800')}; presses refused by the budget {g.pad.refused}; lag frames "
            f"{info['lag_run']} in the run phase, {info['lag_total']} in all")
        save_seg(f"s1/{out}", g.rows, info)
        return g.rows
    finally:
        farm.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    hist = None
    if "--open" in a:
        i = a.index("--open")
        hist = read_inputs(a[i + 1])
        del a[i:i + 2]
    win = WINDOWS
    if "--windows" in a:                 # the press budget, e.g. --windows 600:109,1800:246 (rule v2, the default)
        i = a.index("--windows")
        win = tuple((int(x.split(":")[0]), int(x.split(":")[1])) for x in a[i + 1].split(",") if x)
        del a[i:i + 2]
    solve(a[0] if a else "s1/pre_w0", a[1] if len(a) > 1 else "w0", history=hist, windows=win)
