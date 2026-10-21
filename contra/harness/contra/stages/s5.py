"""Stage 5 (Snow Field) solver: from the frame before stage 5's first frame to stage 6's first frame.

    python -m contra.stages.s5 <start state, e.g. dbg/s5_pre> <out name> [--history <inputs.txt>]

Same machinery as stage 1 (contra/stages/s1_engine.py): a route of jump positions + legal fire cadence + auto
aim with save-state repair; searches for the two tanks, the UFO and the exit. See knowledge/s5_notes.md.

Second pass (2026-10-12; the first pass is s5.py.backup_v1):
    tanks   tank_script2 / tank_fight3: first volley on the stop frame, a jump during the drive-in, a jump
            before the kill (fallback: the first pass's tank_fight2 / tank_fight)
    UFO     ufo_fight4: B presses planned by the offline model contra/stages/s5_ufo_sim.py, replayed and refined
            in the emulator (fallbacks: ufo_fight3 = slot-aware script, then the first pass's ufo_fight2 / ufo_fight)
    lag     Repair5: a lag frame in the main run is a failure the repair search may fix by holding fire

Rule v2 (2026-10-12; the version before it is s5.py.backup_v2): the run phases no longer mash B. They press B at
an enemy ahead (soldier, sniper, runner, diver, turret man) when a volley fired on this frame is predicted to
hit it, the bullets already in flight do not cover its HP, and the look-ahead (s1_engine.Repair, engage=) has
not found that leaving it alone is as fast and as safe; on rows the repair search marked 'fire' / 'aim'; and
only while the press plan (s1_common.Fights) keeps room for the fights ahead (two tanks, the UFO). The wait for
the UFO no longer fires. Tanks and UFO are unchanged: fast / planned fire under the hard budget of s1_common.Pad.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import time

from ..emulator import LOGS_DIR, PROJECT, STATES_DIR
from ..inputs import read_inputs
from .s1_common import (Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, WINDOWS, fire, log, press_report,
                        save_seg)
from .s1_engine import Repair, Route, beam, local_beam, pit_ahead
from .s1 import AIMS_AIR, AIMS_GROUND, _ang, pick_shot, would_hit

# world X at which A is pressed: read from the fitted 1-player TAS stage (logs/dbg/mars_s5.seg.json) with
# tools/s1_trace_ref.py; the tanks' and the boss's jumps are not in this list.
JUMPS = (293, 364, 477, 541, 672, 852, 942, 1125, 1263, 1452, 1502, 1658, 1737, 1793, 1906, 1970, 2050,
         3220, 4127, 4216, 4279, 4547, 4601, 4660, 4719, 4818)

T_ITEM, T_PILLBOX, T_CAPSULE, T_SOLDIER, T_SNIPER = 0x00, 0x02, 0x03, 0x05, 0x06
T_RUNNER, T_DIVER, T_TURRETMAN, T_TM_BULLET = 0x0B, 0x0C, 0x0E, 0x0F
T_GRENGEN, T_GRENADE, T_TANK, T_UFO = 0x10, 0x11, 0x12, 0x14
TARGETS = (T_SOLDIER, T_SNIPER, T_RUNNER, T_DIVER, T_TURRETMAN)

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


def aim_for(r: Ram, route: Route, row: int):
    px, py = r.x, r.y
    air = bool(r.jumping)
    opts = AIMS_AIR if air else AIMS_GROUND
    targets, avoid = [], []
    for (s, ty, rt, hp, ex, ey, st, spr, attr) in r.enemies():
        a = attr & 7
        if ty == T_PILLBOX and 0 < hp < 0xF0 and not (st & 0x80) and a in (1, 2, 4):
            avoid.append(s)
        elif ty == T_CAPSULE and a in (1, 2, 4):
            avoid.append(s)
        elif ty in TARGETS and not (st & 0x80) and 0 < hp < 0xF0:
            targets.append((ex, ey, ty))

    def unsafe(name):
        return any(would_hit(r, name, s) for s in avoid)

    order = ["F", "U", "D"]
    tgt, bd = None, 1e9
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


LAG_KEY = 10 ** 7          # route.opts[LAG_KEY + row] = True: the lag frame on that row is accepted

# ---- the Y sub-pixel ($94) and the two jumps of a tank fight
# A jump from the tank's ground (Y 164) is above the tank's box (Y < 108) for 9-12 frames depending on the Y
# sub-pixel at take-off (0..13: 12 frames, 14..123: 11, 124..198: 10, 199..255: 9). The sub-pixel only changes in
# the air, by the sum of the velocities of the air frames. Before each tank there is one ledge (standing Y 132,
# drop to 164) that can be left by walking off or by jumping off at the same cost (one frame): the two leave
# different sub-pixels, and policy() can take the one that gives the tank fight's two jumps the longer windows
# (route.opts["ledge_jump"]). OFF by default: measured on dbg/s5_pre it made the stage 5 frames slower - the
# longer window moves the stop 2 frames earlier, but then Bill is still in the air when the turret aims, the
# tank's first bullet comes 48 frames sooner and forces a later kill jump (see tank_fight3).
TANK_LEDGES = (2271, 3327)             # world X of the last pixel of that ledge, tank 1 / tank 2


def _air(s, y0, y1, v0):
    """(sub-pixel after, air frames, frames with Y < 108) of a jump (v0 = -1040) or a ledge fall (v0 = 0) from
    standing Y y0 with sub-pixel s to a floor with standing Y y1."""
    y16, v, n, w = y0 * 256 + s, v0, 0, 0
    while n < 200:
        n += 1
        y, f = y16 >> 8, v >> 8
        if v0 and v > 0 and f >= 1 and (f >= 4 or (y & 15) < 8) and y >= y1 - 4:
            break
        v += 35
        y16 += v
        if (y16 >> 8) < 108:
            w += 1
        if not v0 and (y16 >> 8) >= y0 + 20 and (y16 >> 8) >= y1 - 4:
            break
    return y16 & 255, n, w


def tank_windows(s):
    """Frames above the tank's box of the drive-in jump and of the kill jump, for sub-pixel s at the tank."""
    s2, _, w1 = _air(s, 164, 164, -1040)
    _, _, w2 = _air(s2, 164, 164, -1040)
    return w1, w2


def jump_off_ledge(r: Ram):
    """On the last pixel of a tank ledge: is jumping off better for the tank fight than walking off?"""
    s0 = r.m[0x94]
    fall = tank_windows(_air(s0, 132, 164, 0)[0])
    jump = tank_windows(_air(s0, 132, 164, -1040)[0])
    val = lambda w: 1.3 * w[0] + 0.67 * w[1]        # frames gained per frame of window (measured, about)
    return val(jump) > val(fall) + 0.5


def policy(g: Game, route: Route):
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


def sight(g: Game):
    """For s1_engine.Repair: the hostile targets present, as (slot, type)."""
    return [(e[0], e[1]) for e in g.r.enemies() if e[1] in TARGETS and not (e[6] & 0x80) and 0 < e[3] < 0xF0]


def shoot_planned(g: Game, w: set):
    """Cadence fire for the local search's duck / stand steps, within the press plan."""
    if g.pad.held["B"] or plan_room(g):
        fire(g.pad, w)
    return w


def fail_hard(g: Game):
    r = g.r
    if r.dead:
        return "death"
    if (r.y >= 0xD4 and r.lr == 4) or pit_ahead(r):
        return "pit"
    if r.weapon != 0x13:
        return f"weapon ${r.weapon:02x}"
    if g.stall >= 4 and not r.tank_scroll and tank(r) is None:
        return "wall"
    return None


def fail(g: Game):
    """fail_hard, plus: a lag frame in the main run (not in a repair trial) that has not been accepted yet. A
    lag frame costs a whole frame; Repair5 then looks for a way round it (measured: holding fire for about 25
    frames before it removes it) and accepts it if nothing is faster."""
    why = fail_hard(g)
    if why:
        return why
    r = g.r
    opts, in_trial = getattr(g, "lag_ctx", (None, True))
    if r.lagged and r.lr == 4 and not in_trial and opts is not None:
        n = len(g.rows)
        if not opts.get(LAG_KEY + n) and opts.get("lag_seen", 0) < 12:
            return "lag"
    return None


class Repair5(Repair):
    """Repair with one more kind of failure, 'lag': the candidates are 'accept it' (first, so that it wins
    ties) and hold-fire / fixed-aim stretches before it; no jumps, no stops."""

    def _handle(self, g, route, ring, D, why):
        self._lag = why == "lag"
        if self._lag:
            route.opts["lag_seen"] = route.opts.get("lag_seen", 0) + 1
        try:
            return super()._handle(g, route, ring, D, why)
        finally:
            self._lag = False

    def candidates(self, D, t0, route=None, p0=None, p1=None):
        if not getattr(self, "_lag", False):
            return super().candidates(D, t0, route, p0, p1)
        c0 = [("opt", LAG_KEY + D, 0, True)]
        for n in (12, 25, 40, 55):
            for end in (D - 1, D - 8):
                if end - n >= t0:
                    c0.append(("nofire", end - n, n, None))
        # rule v2: a lag frame can also come from what is alive on the screen (measured from the real stage 5
        # state: one at row 1908 with only two volleys in the air), so cadence fire that kills it sooner is a
        # candidate too, and so are the planned pre-fire stretches before the enemies that appeared last
        for n in (25, 50):
            for end in (D - 1, D - 12):
                if end - n >= t0:
                    c0.append(("fire", end - n, n, None))
        for (srow, _key) in self.sightings:
            if D - 110 <= srow < D:
                for n in (7, 12, 45):
                    for t in range(srow - 44, srow - 31, 3):
                        if t >= t0 and ("fire", t, n, None) not in c0:
                            c0.append(("fire", t, n, None))
        return c0, [], []


def tank(r: Ram):
    for e in r.enemies():
        if e[1] == T_TANK:
            return e
    return None


def tank_x(e):
    """The tank's screen X; it starts off screen at 304 (9 bits: the high bit is in its state while it is hidden)."""
    return e[4] + (256 if (e[6] & 0x80) and e[3] == 0xF0 and e[4] < 128 else 0)


def tank_state(r: Ram):
    """('none' | 'drive' | 'stopped' | 'dead', x, hp)"""
    e = tank(r)
    if e is None:
        return ("none", 999, 0)
    if e[3] == 0xF0:
        return ("drive", tank_x(e), 71)
    if e[3] == 0 or e[2] >= 4:
        return ("dead", e[4], 0)
    return ("stopped", e[4], e[3])


TANK_ACTIONS_GROUND = ("R", "RJ", "N", "T", "L", "P")
TANK_ACTIONS_AIR = ("R", "N", "L")


def tank_rows(g: Game, a: str, k: int):
    """R run right firing; RJ the same with a jump; N no direction, firing; T two frames right then stand,
    firing (turns Bill to face the tank); L move left, no fire; P prone, firing. B follows the legal cadence."""
    w = set()
    if a in ("R", "RJ"):
        w.add("Right")
    elif a == "L":
        w.add("Left")
    elif a == "T" and k < 2:
        w.add("Right")
    elif a == "P":
        w.add("Down")
    if a == "RJ" and k < 2:
        w.add("A")
    if a != "L":
        fire(g.pad, w)
    return w


def tank_fight(g: Game, width=8, step=5):
    """Beam search from the frame a tank is created to the frame it is destroyed: scroll while it drives in
    (it arrives three times faster while the screen scrolls), get out of its way, and fire point blank once it
    has stopped (71 HP, vulnerable only then)."""
    def score(g):
        r = g.r
        st, x, hp = tank_state(r)
        if st == "drive":
            return (1000 + x, 0)
        if st == "stopped":
            return (hp, abs(r.x - (x - 46)))
        return (-1, 0)

    def acts(g):
        return TANK_ACTIONS_AIR if g.r.air else TANK_ACTIONS_GROUND

    def dedupe(g):
        r = g.r
        return (tank_state(r), r.x, r.y, r.m[0xA0], r.m[0xC2], tuple(r.bullets()), g.pad.since["B"])

    return beam(g, acts, tank_rows, score, lambda g: tank_state(g.r)[0] in ("dead", "none"), width=width,
                max_steps=240, step=step, dedupe=dedupe, fail=lambda g: g.r.dead, tag="s5 tank",
                lookahead=[("L",), ("N",), ("R",)], look_steps=6, max_seconds=900)


def tank_script(g: Game, sj: int, sl: int, limit: int = 330):
    """One scripted tank fight from the frame the tank is created: scroll right firing; jump on row sj (still
    holding Right, so the screen keeps scrolling and the tank keeps coming at 1.5 px/f while Bill is above its
    box); steer left from row sl until landing; then walk to 46 px from the stopped tank and fire until it is
    destroyed. sj = None: no jump (back off on the ground from row sl). Returns rows played, or None (death)."""
    n0 = len(g.rows)
    landed = False
    while True:
        k = len(g.rows) - n0
        r = g.r
        st, x, hp = tank_state(r)
        if st in ("dead", "none"):
            return k
        if k >= limit:
            return None
        w = set()
        if not landed:
            if k < sl:
                w.add("Right")
                fire(g.pad, w)
            else:
                if st == "drive" or r.x > x - 47 or r.air:
                    w.add("Left")
                if not r.air and (st != "drive" or r.x <= x - 60):
                    landed = True
            if sj is not None and k in (sj, sj + 1):
                w.add("A")
            if sj is not None and k > sj + 2 and k >= sl and not r.air:
                landed = True
        if landed:
            w = set()
            if st == "drive":
                if r.x > x - 50:
                    w.add("Left")
                elif r.x < x - 56:
                    w.add("Right")
                    fire(g.pad, w)
            else:
                if r.x < x - 46:
                    w.add("Right")
                fire(g.pad, w)
                if r.aim not in (2, 1, 3, 0, 4) and "Right" not in w and r.x <= x - 48:
                    w.add("Right")            # facing left: turn round
        g.step(w)
        if g.r.dead:
            return None


def y_after(r: Ram, n: int = 1):
    """Bill's Y after n more frames of a jump or fall (16-bit position $31A:$94, velocity $C6:$C4, gravity $23
    per frame, added before the move). Exact while he stays in the air."""
    v = r.m[0xC6] * 256 + r.m[0xC4]
    if v >= 32768:
        v -= 65536
    y16 = r.y * 256 + r.m[0x94]
    for _ in range(n):
        v += 0x23
        y16 += v
    return y16 >> 8


TANK_TOP = 108         # a jumping Bill is above the tank's box while his Y < 108 (box: Y 108..177, X -44..+43)
TANK_REACH = 45        # on the ground, or lower in a jump, he must be at X <= tank X - 45
TANK_STOP_X = 159      # where a tank stops when the last pixels are driven without the player's scroll
TANK_SAFE = TANK_STOP_X - TANK_REACH       # 114


def tank_script2(g: Game, sj, sl, hj, dl=0, yf=114, xk=112, limit=330, upto=None):
    """Second-pass tank fight, from the frame the tank is created to the frame its HP is 0 (or <= upto).

    A  scroll right (the tank comes at 1.5 px/f) until it would touch Bill. With sj: jump on row sj and keep
       scrolling above its box (Y < 108 for 9-12 frames, depending on the Y sub-pixel at take-off) until row
       sl, then steer left until it stops.
    B  no jump: back off to X xk - 2 and wait, no firing, so that all bullet slots are free when it stops.
    C  the frame it stops: fire point blank (71 HP, 14 hits per 15 frames under the press cap): in the air
       down-right in 5-frame cycles (Right+Down+B two frames, Left three), on the ground facing it. When its HP
       is hj or less: jump straight up, still firing right (first press delayed dl frames; no press while the
       muzzle is above Y yf, where half the fan flies over the tank), then right + down-right fire from the
       frame that puts him over the box exactly when he is above it, so that he is 9-12 px nearer the scroll
       point when it dies.
    Returns rows played, or None (death / too slow)."""
    n0 = len(g.rows)
    phase = "A"
    kj = None
    hold_b = 0
    going = False
    pad = g.pad
    while True:
        k = len(g.rows) - n0
        r = g.r
        st, x, hp = tank_state(r)
        if st in ("dead", "none") or (upto is not None and st == "stopped" and hp <= upto):
            return k
        if k >= limit or r.dead:
            return None
        w = set()
        safe_x = x - TANK_REACH
        stop_next = st == "stopped" or (st == "drive" and x - ((r.fc + 1) & 1) < 160)
        if phase == "A":
            w.add("Right")
            if sj is not None:
                if k in (sj, sj + 1):
                    w.add("A")
                if k >= sl:
                    phase = "B"
            elif x - 1 - ((r.fc + 1) & 1) - TANK_REACH < 128:
                phase = "B"
        if phase == "B":
            w = set()
            if stop_next:
                phase = "C"
            elif r.air:
                w.add("Left")
            elif r.x > xk - 2:
                w.add("Left")
        if phase == "C":
            w = set()
            if r.air and kj is None:                 # still in the drive-in jump: 5-frame cycles
                if pad.held["Right"]:
                    if pad.run["Right"] < 2:
                        w |= {"Right", "Down"}
                    else:
                        w.add("Left")
                elif (not pad.held["B"]) and pad.can_press("B") and pad.can_press("Right") and r.x + 2 <= TANK_SAFE:
                    w |= {"Right", "Down", "B"}
                else:
                    w.add("Left")
                if pad.held["B"] and pad.run["B"] < 2:
                    w.add("B")
            elif not r.air:
                if kj is None and st == "stopped" and hp <= hj:
                    kj = k
                    hold_b = dl
                if kj is not None and k in (kj, kj + 1):
                    w.add("A")
                if kj is None and (r.aim != 2 or (pad.held["Right"] and pad.run["Right"] < 2)):
                    if r.x + 2 <= TANK_SAFE or pad.held["Right"]:
                        w.add("Right")              # turn to face the tank (a press lasts two frames)
                    else:
                        w.add("Left")
                    if r.aim == 2 or pad.can_press("Right"):
                        fire(pad, w)
                else:
                    if hold_b > 0 and not pad.held["B"]:
                        hold_b -= 1
                    else:
                        fire(pad, w)
            else:                                    # the kill jump
                m = max(0, TANK_SAFE - r.x)          # frames he may move right before he is over the box
                if not going and y_after(r, m + 1) < TANK_TOP and y_after(r, 1) <= y_after(r, 0):
                    going = True
                if going:
                    w |= {"Right", "Down"}
                    fire(pad, w)
                    if y_after(r, 1) >= TANK_TOP and r.x + 1 > safe_x:
                        w = {"Left"}                # too early: the tank is alive and he is coming down
                else:
                    if hold_b > 0 and not pad.held["B"]:
                        hold_b -= 1
                    elif r.y >= yf or pad.held["B"]:
                        fire(pad, w)
        g.step(w)
        if g.r.dead:
            return None


def tank_fight3(farm: Farm, g: Game, tag="s5"):
    """Second-pass tank fight: grid over tank_script2's parameters in two stages on all emulators - (1) the
    drive-in (no jump, or jump row sj / steer-left row sl), judged by the row its HP is down to 40; (2) the
    HP at which the last jump starts, judged by the row the scroll is 60 px past the tank's stop (holding
    Right after the kill). Plays the best on g up to the kill. Returns rows or None."""
    st = g.save_file(f"tmp/{tag}_tank")
    pad, keep = g.pad.copy(), list(g.rows)
    scr0 = g.r.scr
    tank_fight3.last = None          # (rows until the scroll is 60 px past the stop, rows until its HP is 0) of the fight played

    def ev1(gg, job):
        keep_ = gg.rows
        try:
            gg.load_file(st, pad)
            return tank_script2(gg, job[0], job[1], 0, upto=40)
        finally:
            gg.rows = keep_

    def ev2(gg, job):
        keep_ = gg.rows
        try:
            gg.load_file(st, pad)
            n = tank_script2(gg, *job)
            if n is None:
                return None
            k = n
            while gg.r.scr < scr0 + 145 + 60:
                gg.step({"Right"})
                k += 1
                if gg.r.dead or k > 420:
                    return None
            return (k, n)
        finally:
            gg.rows = keep_
    jobs1 = [(None, 0)] + [(sj, sj + d) for sj in range(58, 67) for d in range(27, 34)]
    res1 = farm.map(ev1, jobs1)
    ok1 = sorted((r_, i) for i, r_ in enumerate(res1) if r_ is not None)
    if not ok1:
        g.load_file(st, pad, rows=keep)
        return None
    # The tank's first bullet (created at tank X - 46, Y 124, flying left) comes 56 frames after the stop when
    # its turret already points at Bill 8 frames after the stop - that is when he is still in the air from the
    # drive-in jump - and 48 frames later otherwise. It kills a jumping Bill whose Y is 114..125 (a standing
    # Bill is under it), i.e. the kill jump at its best timing. So several drive-ins (the earliest stop is
    # not always the best fight) and a wide range of kill-jump timings are tried: a later jump is still on the
    # ground when the bullet passes and only gives up some of the walk it saves.
    cands = []
    for r_, i in ok1[:5]:
        if jobs1[i] not in cands:
            cands.append(jobs1[i])
    early = [i for r_, i in ok1 if jobs1[i][0] is not None and jobs1[i][0] <= 61]
    if early and jobs1[early[0]] not in cands:
        cands.append(jobs1[early[0]])                # the best drive-in that lands before the turret aims
    if (None, 0) not in cands and res1[0] is not None:
        cands.append((None, 0))
    jobs2 = [(sj, sl, hj, 0) for (sj, sl) in cands for hj in (15, 18, 21, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37)]
    res2 = farm.map(ev2, jobs2)
    ok2 = sorted((r_, i) for i, r_ in enumerate(res2) if r_ is not None)
    log(f"tank: drive-in (jump row, steer-left row) -> row HP 40: " + ", ".join(f"{jobs1[i]}={r_}" for r_, i in ok1[:4])
        + f" (no jump: {res1[0]}); whole fight (.., jump at HP, delay) -> (row scroll +60, row dead): "
        + ", ".join(f"{jobs2[i]}={r_}" for r_, i in ok2[:4]) + f"; {len(ok2)}/{len(jobs2)} survive")
    g.load_file(st, pad, rows=keep)
    if not ok2:
        return None
    n = tank_script2(g, *jobs2[ok2[0][1]])
    assert n == ok2[0][0][1], (n, ok2[0])
    tank_fight3.last = ok2[0][0]
    return g.rows[len(keep):]


tank_fight3.last = None


def tank_fight2(farm: Farm, g: Game, tag="s5"):
    """Grid search over tank_script's two parameters on all emulators; plays the best on g. Rows or None."""
    st = g.save_file(f"tmp/{tag}_tank")
    pad, keep = g.pad.copy(), list(g.rows)

    def ev(gg, job):
        keep_ = gg.rows
        try:
            gg.load_file(st, pad)
            return tank_script(gg, *job)
        finally:
            gg.rows = keep_
    jobs = [(None, sl) for sl in range(80, 93)]
    jobs += [(sj, sj + d) for sj in range(56, 80, 2) for d in (20, 23, 26, 29, 32, 36)]
    res = farm.map(ev, jobs)
    ok = sorted((r_, i, job) for i, (r_, job) in enumerate(zip(res, jobs)) if r_ is not None)
    log(f"tank scripts (jump row, steer-left row) -> rows to destroy it: {len(ok)}/{len(jobs)} survive; best "
        + ", ".join(f"{job}={r_}" for r_, _, job in ok[:6]))
    g.load_file(st, pad, rows=keep)
    if not ok:
        return None
    n = tank_script(g, *ok[0][2])
    assert n == ok[0][0], (n, ok[0])
    return g.rows[len(keep):]


# ------------------------------------------------------------------------------------------------ UFO
def ufo(r: Ram):
    for e in r.enemies():
        if e[1] == T_UFO:
            return e
    return None


def pending_box(r: Ram, cx, cy, half, tmax=40):
    """Player bullets whose straight path crosses the box (cx +- half, cy +- half)."""
    m = r.m
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
        for t in range(1, tmax):
            x, y = bx + vx * t, by + vy * t
            if x >= 251 or y >= 232 or y < 5 or x < 5:
                break
            if cx - half <= x < cx + half and cy - half <= y < cy + half:
                n += 1
                break
    return n


def ufo_rows(g: Game, a: str, k: int):
    """a = direction (R / L / -) + 'U' if firing upward + 'J' if jumping, e.g. 'RUJ', '-U', 'L'."""
    w = set()
    if a[0] == "R":
        w.add("Right")
    elif a[0] == "L":
        w.add("Left")
    if "U" in a and k < 2:
        w.add("Up")
        w.add("B")
    if "J" in a and k < 2:
        w.add("A")
    return w


UFO_GROUND = ("-U", "-UJ", "RU", "LU", "RUJ", "LUJ", "R", "L", "-")
UFO_AIR = ("-U", "RU", "LU", "R", "L", "-")


def ufo_fight(g: Game, width=8):
    """From the frame the UFO exists to the frame its HP reaches 0."""
    while g.pad.held["B"] or not g.pad.rate_ok("B"):     # the burst rule only: the budget may refuse for long
        g.step(set())

    def score(g):
        r = g.r
        e = ufo(r)
        if e is None:
            return (-1, 0) if r.bossdef else (900, abs(r.x - 128))
        if e[3] == 0:
            return (-1, 0)
        if e[6] & 0x80:
            return (200.0, abs(r.x - e[4]))
        return (e[3] - min(pending_box(r, e[4], e[5], 17), 5) * 0.9, abs(r.x - e[4]))

    def done(g):
        e = ufo(g.r)
        return g.r.bossdef or (e is not None and e[3] == 0)

    def dedupe(g):
        r = g.r
        e = ufo(r)
        return (e[3] if e else -1, r.x, r.y, r.m[0xA0], tuple(r.bullets()))

    return beam(g, lambda g: UFO_AIR if g.r.air else UFO_GROUND, ufo_rows, score, done, width=width, max_steps=200,
                dedupe=dedupe, fail=lambda g: g.r.dead, tag="s5 ufo",
                lookahead=[("-",), ("R",), ("L",), ("-UJ", "-")], look_steps=4, max_seconds=900)


def ufo_script(g: Game, th: int, dx: int, j: int, ph: int, rr: int = 999, limit: int = 400):
    """One scripted UFO fight from the frame the UFO exists. th = rows from now until it can be hit (measured by
    a dry run). Stand dx px from its X, fire straight up at the legal cadence (press phase ph) from 24 frames
    before th, jump straight up j frames before th and again on every landing. rr = fire only while the muzzle
    is at most rr px under the UFO's box (from further away the outer pellets miss and hold their slots).
    Returns rows played until its HP is 0, or None (dead / too slow)."""
    n0 = len(g.rows)
    while True:
        k = len(g.rows) - n0
        r = g.r
        e = ufo(r)
        if e is None or k >= limit:
            return None
        if e[3] == 0 or r.bossdef:
            return k
        w = set()
        ux = e[4]
        if ux == 240 and k < 8:                      # its X is set a few frames after it is created
            g.step(w)
            continue
        tx = max(28, min(200, ux + dx))
        if not r.air:
            if r.x < tx:
                w.add("Right")
            elif r.x > tx:
                w.add("Left")
        if k >= th - 24 and r.x == tx or r.air:
            if not ({"Right", "Left"} & w):
                w.add("Up")
                muzzle_y = r.y - (16 if r.air else 27)
                if (k - ph) % 5 in (0, 1) and (muzzle_y - (e[5] + 17) <= rr or g.pad.held["B"]):
                    w.add("B")
        if k >= th - j and not r.air and r.x == tx:
            w.add("A")
        g.step(w)
        if g.r.dead:
            return None


def ufo_fight2(farm: Farm, g: Game, tag="s5"):
    """Grid search over ufo_script's parameters on all emulators; plays the best on g. Returns rows or None."""
    st = g.save_file(f"tmp/{tag}_ufo")
    pad, keep = g.pad.copy(), list(g.rows)
    # dry run: when does it become hittable?
    th = None
    for k in range(1, 260):
        g.step(set())
        e = ufo(g.r)
        if e is not None and not (e[6] & 0x80):
            th = k
            break
    if th is None:
        g.load_file(st, pad, rows=keep)
        return None
    ux = ufo(g.r)[4]

    def ev(gg, job):
        keep_ = gg.rows
        try:
            gg.load_file(st, pad)
            return ufo_script(gg, th, *job)
        finally:
            gg.rows = keep_
    jobs = [(dx, j, ph, rr) for rr in (999, 42) for dx in (-8, -4, 0, 4) for j in (6, 10, 14, 18, 22, 26, 30)
            for ph in range(5)]
    res = farm.map(ev, jobs)
    ok = sorted((r_, job) for r_, job in zip(res, jobs) if r_ is not None)
    log(f"UFO at X {ux}: hittable {th} rows after it appears; {len(ok)}/{len(jobs)} scripts kill it; best "
        + ", ".join(f"{job}={r_}" for r_, job in ok[:6]))
    g.load_file(st, pad, rows=keep)
    if not ok:
        return None
    n = ufo_script(g, th, *ok[0][1])
    assert n == ok[0][0], (n, ok[0])
    return g.rows[len(keep):]


def pad_free(pad: Pad, b: str):
    return pad.held[b] or pad.can_press(b)


UFO_BOX_BOTTOM = 65        # its bullet box: X -16..+17, Y -16..+17 around (X, 48) on its first appearance
S_SPEED = 3.48             # Spread + Rapid pellet speed, px per frame


def ufo_script3(g: Game, th: int, dx: int, j1: int, m_hi: int, m_lo: int, early: int = 2, waste: int = 0,
                d_hi: int = 41, limit: int = 400):
    """Second-pass scripted UFO fight from the frame the UFO exists; th = rows from now until it can be hit.
    Stand dx px from its X holding Up; jump straight up j1 rows before th and again on every landing.
    A B press is made only when it is worth its bullet slots (10 slots; a pellet that misses keeps its slot
    until it leaves the screen, one that hits for 7 more frames):
      - not before its centre pellet would reach the box `early` rows ahead of th;
      - high in the jump (muzzle at most d_hi px under the box: all five pellets go in): when at least m_hi
        slots are free;
      - lower: only the centre and the two inner pellets can hit, so press when 1..3 slots are free (at least
        m_lo), or with `waste` also when more are free (the outer pellets are then lost).
    Returns rows played until its HP is 0, or None (death / too slow)."""
    n0 = len(g.rows)
    pad = g.pad
    while True:
        k = len(g.rows) - n0
        r = g.r
        e = ufo(r)
        if e is None or k >= limit or r.dead:
            return None
        if e[3] == 0 or r.bossdef:
            return k
        w = set()
        ux = e[4]
        if ux == 240 and k < 8:                      # its X is set a few frames after it is created
            g.step(w)
            continue
        tx = max(28, min(158, ux + dx))
        if not r.air and r.x != tx:
            w.add("Right" if r.x < tx else "Left")
        else:
            w.add("Up")
            if not r.air and k >= th - j1:
                w.add("A")
            if pad.held["B"]:
                if pad.run["B"] < 2:
                    w.add("B")
            elif pad.can_press("B") and pad_free(pad, "Up"):
                nfree = sum(1 for s in range(10) if not r.m[0x388 + s])
                my = r.y - (16 if r.air else 27)
                d = my - (e[5] + 17)
                arrive = k + max(0, d) / S_SPEED
                if nfree and arrive >= th - early:
                    if d <= d_hi:
                        if nfree >= m_hi:
                            w.add("B")
                    elif m_lo <= nfree <= 3 or (waste and nfree > 3):
                        w.add("B")
        g.step(w)
        if g.r.dead:
            return None


def ufo_fight3(farm: Farm, g: Game, tag="s5", jobs=None):
    """Grid search over ufo_script3's parameters on all emulators; plays the best on g. Returns rows from the
    frame the UFO exists to the frame its HP is 0, or None."""
    st = g.save_file(f"tmp/{tag}_ufo")
    pad, keep = g.pad.copy(), list(g.rows)
    th = None
    for k in range(1, 260):
        g.step(set())
        e = ufo(g.r)
        if e is not None and not (e[6] & 0x80):
            th = k
            break
    if th is None:
        g.load_file(st, pad, rows=keep)
        return None
    ux = ufo(g.r)[4]

    def ev(gg, job):
        keep_ = gg.rows
        try:
            gg.load_file(st, pad)
            return ufo_script3(gg, th, *job)
        finally:
            gg.rows = keep_
    jobs = jobs or [(dx, j1, m_hi, m_lo, early, waste) for dx in (0, -3) for j1 in (22, 24, 26, 28, 30, 32)
                    for m_hi in (3, 4) for m_lo in (1, 2) for early in (0, 3) for waste in (0, 1)]
    res = farm.map(ev, jobs)
    ok = sorted((r_, job) for r_, job in zip(res, jobs) if r_ is not None)
    log(f"UFO at X {ux}: hittable {th} rows after it appears; {len(ok)}/{len(jobs)} scripts kill it; best "
        "(dx, jump lead, m_hi, m_lo, early, waste) = rows after hittable: "
        + ", ".join(f"{job}={r_ - th}" for r_, job in ok[:6]))
    g.load_file(st, pad, rows=keep)
    if not ok:
        return None
    n = ufo_script3(g, th, *ok[0][1])
    assert n == ok[0][0], (n, ok[0])
    return g.rows[len(keep):]


class UfoSchedule:
    """A UFO fight as a schedule: `prefix` rows from the frame the UFO exists (walking under it), then Up held
    on every row with new B presses on rows P and new A presses on rows J (row numbers count from the frame
    the UFO exists; each press is held two rows). Rows are made legal by a Pad that carries the history."""

    def __init__(self, st, pad: Pad, prefix):
        self.st, self.pad = st, pad
        self.prefix = [tuple(r_) for r_ in prefix]
        self.k0 = len(self.prefix)
        self.pad0 = pad.copy()
        for r_ in self.prefix:
            self.pad0.push(r_)

    def rows(self, P, J, n):
        pd = self.pad0.copy()
        out = []
        ps, js = set(P) | {x + 1 for x in P}, set(J) | {x + 1 for x in J}
        for k in range(self.k0 + 1, n + 1):          # row k is played on frame k after the UFO appeared
            w = {"Up"}
            if k in ps:
                w.add("B")
            if k in js:
                w.add("A")
            row = pd.legal(w)
            pd.push(row)
            out.append(row)
        return self.prefix + out

    def ev(self, gg: Game, job):
        """job = (P, J, n_ref) -> (row on which its HP is 0, HP five rows before n_ref); 10**5: not by n_ref + 3."""
        P_, J_, n_ref = job
        keep_ = gg.rows
        try:
            gg.load_file(self.st, self.pad)
            allrows = self.rows(P_, J_, n_ref + 3)
            cp = max(self.k0, n_ref - 5)
            gg.run_raw(allrows[:cp])
            e = ufo(gg.r)
            if gg.r.dead or (e is None and not gg.r.bossdef):
                return (10 ** 6, 99)
            hp_cp = 0 if (e is None or gg.r.bossdef) else e[3]
            if hp_cp == 0:                           # dead before the checkpoint: find the row
                gg.load_file(self.st, self.pad)
                gg.run_raw(allrows[:self.k0])
                for k in range(self.k0, cp):
                    gg.step_raw(allrows[k])
                    e = ufo(gg.r)
                    if gg.r.bossdef or (e is not None and e[3] == 0):
                        return (k + 1, 0)
                return (cp, 0)
            for k in range(cp, len(allrows)):
                gg.step_raw(allrows[k])
                e = ufo(gg.r)
                if gg.r.dead:
                    return (10 ** 6, hp_cp)
                if gg.r.bossdef or (e is not None and e[3] == 0):
                    return (k + 1, hp_cp)
            return (10 ** 5, hp_cp)
        finally:
            gg.rows = keep_

    def moves(self, P_, J_):
        k0 = self.k0 + 1
        out = []
        for i, p_ in enumerate(P_):
            lo = P_[i - 1] + 5 if i else k0
            hi = P_[i + 1] - 5 if i + 1 < len(P_) else 10 ** 6
            for d in (-3, -2, -1, 1, 2, 3):
                if lo <= p_ + d <= hi:
                    out.append((P_[:i] + [p_ + d] + P_[i + 1:], J_))
            out.append((P_[:i] + P_[i + 1:], J_))
            if i + 1 < len(P_) and P_[i + 1] - p_ >= 10:
                for q in range(p_ + 5, P_[i + 1] - 4):
                    out.append((P_[:i + 1] + [q] + P_[i + 1:], J_))
            if i + 1 < len(P_):                      # this press and all later ones together
                for d in (-1, 1):
                    if lo <= p_ + d:
                        out.append((P_[:i] + [x + d for x in P_[i:]], J_))
        if P_:
            for q in (P_[0] - 5, P_[0] - 6, P_[0] - 7):
                if q >= k0:
                    out.append(([q] + P_, J_))
            out.append((P_ + [P_[-1] + 5], J_))
        for i, j_ in enumerate(J_):
            for d in (-2, -1, 1, 2):
                if j_ + d >= k0:
                    out.append((P_, J_[:i] + [j_ + d] + J_[i + 1:]))
        return out

    def refine(self, farm: Farm, P, J, cur, passes=3):
        """Hill climbing in the emulator: single changes of the schedule (a press 1..3 rows earlier or later,
        dropped, added in a long gap, all later presses shifted, a jump 1..2 rows earlier or later); the best
        change that kills sooner (or leaves less HP five rows before the old kill) is kept."""
        t0 = time.time()
        n_best = cur[0]
        for it in range(passes):
            cands = self.moves(P, J)
            res = farm.map(self.ev, [(p_, j_, n_best) for (p_, j_) in cands])
            best = min(range(len(cands)), key=lambda i: res[i])
            if res[best] >= cur:
                break
            P, J = cands[best]
            if res[best][0] < n_best:
                n_best = res[best][0]
                cur = farm.map(self.ev, [(P, J, n_best)])[0]
            else:
                cur = res[best]
            log(f"   UFO refine pass {it + 1}: {len(cands)} changes tried, kill row {cur[0]} (HP {cur[1]} five rows earlier), "
                f"{time.time() - t0:.0f} s")
        return P, J, cur


UFO_LEADS = tuple(range(22, 36))


def ufo_fight4(farm: Farm, g: Game, tag="s5", width=2000, passes=3, procs=4):
    """Planned UFO fight: the offline model (contra/stages/s5_ufo_sim.py) searches the B presses for several
    jump timings; every plan is replayed in the emulator, the best is refined there by hill climbing, and played
    on g. Returns rows from the frame the UFO exists to the frame its HP is 0, or None."""
    st = g.save_file(f"tmp/{tag}_ufo")
    pad, keep = g.pad.copy(), list(g.rows)
    th = None
    for k in range(1, 260):
        g.step(set())
        e = ufo(g.r)
        if e is not None and not (e[6] & 0x80):
            th = k
            break
    if th is None:
        g.load_file(st, pad, rows=keep)
        return None
    ux, uy = ufo(g.r)[4], ufo(g.r)[5]
    g.load_file(st, pad, rows=keep)
    k0 = max(8, th - 45)
    while True:                                      # walk under it, then hold Up
        k = len(g.rows) - len(keep)
        r = g.r
        e = ufo(r)
        if e is None or r.dead or k > th - 20:
            g.load_file(st, pad, rows=keep)
            return None
        tx = max(28, min(158, e[4]))
        inplace = (not (e[4] == 240 and k < 8)) and r.x == tx and not r.air
        if k >= k0 and inplace and g.pad.held["Up"] and r.nbullets() == 0 and not g.pad.held["B"]:
            break
        w = set()
        if not (e[4] == 240 and k < 8):
            if r.x < tx:
                w.add("Right")
            elif r.x > tx:
                w.add("Left")
            elif pad_free(g.pad, "Up"):
                w.add("Up")
        g.step(w)
    k0 = len(g.rows) - len(keep)
    r = g.r
    sched = UfoSchedule(st, pad, g.rows[len(keep):])
    acc = [(r.m[0x3A8 + s], r.m[0x398 + s]) for s in range(10)]
    gdx = -5 if r.aim == 9 else 5
    jobs = [(k0, r.y * 256 + r.m[0x94], r.x, acc, th, ux, uy, th - lead, width, gdx) for lead in UFO_LEADS if th - lead > k0]
    t0 = time.time()
    plans = []
    try:                                             # one interpreter per worker, results as JSON on stdout
        running = []
        for i in range(procs):
            chunk = jobs[i::procs]
            if not chunk:
                continue
            path = LOGS_DIR / "s5" / f"tmp_{tag}_plan{i}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(chunk), encoding="utf-8")
            running.append((i, path, subprocess.Popen([sys.executable, "-m", "contra.stages.s5_ufo_sim", str(path)],
                                                      cwd=str(PROJECT), stdout=subprocess.PIPE, text=True)))
        got = {}
        for i, path, pr in running:
            out_, _ = pr.communicate(timeout=600)
            for n_, p_ in enumerate(json.loads(out_.strip().splitlines()[-1])):
                got[i + n_ * procs] = p_
            path.unlink(missing_ok=True)
        plans = [got.get(n_) for n_ in range(len(jobs))]
    except Exception as ex_:                         # noqa: BLE001
        log(f"UFO planner failed ({ex_!r})")
        plans = []
    plans = [(p_[0], p_[1], p_[2], jb[7]) for p_, jb in zip(plans, jobs) if p_ is not None]
    g.load_file(st, pad, rows=keep)
    if not plans:
        return None
    res = farm.map(sched.ev, [(p_[1], p_[2], p_[0] + 8) for p_ in plans])
    order = sorted(range(len(plans)), key=lambda i: res[i])
    log(f"UFO at X {ux}: hittable {th} rows after it appears; model plans (jump lead: model / emulator rows after hittable): "
        + ", ".join(f"{th - plans[i][3]}: {plans[i][0] - th} / {res[i][0] - th if res[i][0] < 10 ** 5 else None}" for i in order[:8])
        + f"; planning {time.time() - t0:.0f} s")
    i = order[0]
    if res[i][0] >= 10 ** 5:
        return None
    P, J = list(plans[i][1]), list(plans[i][2])
    cur = farm.map(sched.ev, [(P, J, res[i][0])])[0]
    if passes:
        P, J, cur = sched.refine(farm, P, J, cur, passes=passes)
    rows = sched.rows(P, J, cur[0])
    g.load_file(st, pad, rows=keep)
    g.run_raw(rows)
    e = ufo(g.r)
    if not (g.r.bossdef or (e is not None and e[3] == 0)) or g.r.dead:
        log("UFO: the planned rows do not replay on the main emulator")
        g.load_file(st, pad, rows=keep)
        return None
    return g.rows[len(keep):]


# ------------------------------------------------------------------------------------------------ exit
def exit_want(g: Game, strat, k, c):
    r = g.r
    if strat[0] == "ground":
        return {"Right"}
    if strat[0] == "jump":
        w = {"Right"}
        if k in (c - strat[1], c - strat[1] + 1):
            w.add("A")
        return w
    if strat[0] == "stop":
        return {"Right"} if r.x < strat[1] else set()
    return set()


def exit_eval(g: Game, job):
    state, pad, strat, c, limit = job
    keep = g.rows
    try:
        g.load_file(state, pad)
        k = 0
        lost = None
        while g.r.bossdef != 2 and k < limit:
            g.step(exit_want(g, strat, k, c) if g.r.lr != 9 else set())
            k += 1
            if lost is None and g.r.lr == 9:
                lost = k
            if g.r.dead:
                return {"strat": strat, "frames": 10 ** 6, "lost": lost}
        return {"strat": strat, "frames": k if g.r.bossdef == 2 else 10 ** 6, "lost": lost}
    finally:
        g.rows = keep


def exit_search(farm: Farm, g: Game, tag="s5"):
    """From the frame the UFO dies to the frame Bill is off the screen: where to be when control is lost."""
    st = g.save_file(f"tmp/{tag}_exit")
    pad = g.pad.copy()
    keep = list(g.rows)
    r0 = exit_eval(g, (st, pad, ("ground",), 10 ** 6, 900))
    c = r0["lost"]
    strats = [("ground",)] + [("jump", d) for d in (1, 2, 3, 4, 6, 8, 10, 14, 18, 24, 30, 38, 46, 54, 58, 60)]
    strats += [("stop", x) for x in (150, 156, 158, 159)]
    res = farm.map(exit_eval, [(st, pad, s_, c, 900) for s_ in strats])
    res.sort(key=lambda x: x["frames"])
    log(f"exit: control lost {c} rows after the kill; ground = {r0['frames']} rows to hidden; best "
        + ", ".join(f"{x['strat']}={x['frames']}" for x in res[:6]))
    best = res[0]
    g.load_file(st, pad, rows=keep)
    k = 0
    while g.r.bossdef != 2:
        g.step(exit_want(g, best["strat"], k, c) if g.r.lr != 9 else set())
        k += 1
    return best


# ------------------------------------------------------------------------------------------------ whole stage
def run_to(farm: Farm, g: Game, route: Route, done, tag, info, pre=None, trig=None):
    """pre / trig: keep a file state of the main run about 88 px before world X `trig` (the next tank) in the
    dict `pre` (state, pad, rows), for solve()'s try of the other tank parity."""
    def mark(gg):
        if pre is not None and trig is not None and not gg.r.air and trig - 92 <= gg.r.prog < trig - 84:
            pre.update(state=gg.save_file(f"tmp/{tag}_pretank"), pad=gg.pad.copy(), rows=list(gg.rows))
        return None
    rep = Repair5(farm, policy, fail, tag=tag, local=local_beam(policy, fail_hard, tag=tag, shoot=shoot_planned),
                  engage=engage, fail_look=fail_hard, sight=sight, mark=mark)
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


def solve(start="dbg/s5_pre", out="d0", n=3, history=None, width=8, parity=True, windows=WINDOWS):
    """history = the real rows before the solver's first row (at least the last HISTORY_ROWS of them): the press
    budget counts them. windows = the budget's ((rows, most presses), ...), rule v2 by default."""
    farm = Farm(n, name=f"s5_{out}")
    info = {"start": start, "marks": {}}
    try:
        g = farm.g0
        history = [tuple(r_) for r_ in (history or [])][-HISTORY_ROWS:]
        g.load_file(start, pad=Pad.from_rows(history, windows))
        info["windows"] = [list(x) for x in windows]
        lag_pre = g.r.lagc
        log(f"start {start}: {g.r.summary()}; press history {len(history)} rows, B presses in its last 600 / 1800 "
            f"rows {g.pad.count('B', 600)} / {g.pad.count('B', 1800)}")
        THROTTLED.clear()
        route = Route(JUMPS)
        ntank = 0
        to_tank = lambda g: tank_state(g.r)[0] == "drive" or g.r.auto > 0 or g.r.lr not in (3, 4)     # noqa: E731
        while True:
            pre = {}
            trig = next((x for x, _ in PLAN.fights[:2] if x > g.r.prog + 100), None)
            ok = run_to(farm, g, route, to_tank, f"s5_{out}_run{ntank}", info, pre=pre, trig=trig)
            save_seg(f"s5/{out}_partial", g.rows, info)
            if not ok:
                return None
            if g.r.auto > 0:
                break
            ntank += 1
            created = len(g.rows)
            g.save_file(f"s5/{out}_tank{ntank}")
            t1 = time.time()
            res = tank_fight3(farm, g, tag=f"s5_{out}")
            if res is not None and tank_fight3.last is not None and pre and parity:
                # the other parity: one extra jump before the tank (one frame later, another Y sub-pixel)
                plain = (g.save_file(f"tmp/s5_{out}_tankplain"), g.pad.copy(), list(g.rows))
                best_abs, taken = created + tank_fight3.last[0], False
                try:
                    g.load_file(pre["state"], pre["pad"], rows=pre["rows"])
                    route2 = route.copy()
                    route2.opts["dec"] = list(route.opts.get("dec", ()))
                    route2.add_over(len(g.rows), ("add", "A"))
                    route2.add_over(len(g.rows) + 1, ("add", "A"))
                    info2 = {}
                    if run_to(farm, g, route2, to_tank, f"s5_{out}_run{ntank - 1}p", info2) and tank_state(g.r)[0] == "drive":
                        created2 = len(g.rows)
                        g.save_file(f"tmp/s5_{out}_tankalt")
                        res2 = tank_fight3(farm, g, tag=f"s5_{out}")
                        alt_abs = None if res2 is None or tank_fight3.last is None else created2 + tank_fight3.last[0]
                        log(f"tank {ntank}: scroll 60 px past it on row {best_abs} as it came (created on row {created}); "
                            f"with one extra jump before it on row {alt_abs} (created on row {created2})")
                        if alt_abs is not None and alt_abs < best_abs:
                            taken = True
                            route, created, res = route2, created2, res2
                            info.setdefault("repairs", []).extend(info2.get("repairs", []))
                            info["run_presses"] = info.get("run_presses", 0) + info2.get("run_presses", 0)
                            info["lag_run"] = info.get("lag_run", 0) + info2.get("lag_run", 0)
                            info.setdefault("tank_parity_jump", []).append(ntank)
                            try:
                                shutil.copyfile(STATES_DIR / "tmp" / f"s5_{out}_tankalt.State",
                                                STATES_DIR / "s5" / f"{out}_tank{ntank}.State")
                            except OSError:
                                pass
                except Exception as ex_:                 # noqa: BLE001
                    log(f"tank {ntank}: the try of the other parity failed ({ex_!r}); keeping the plain fight")
                if not taken:
                    g.load_file(plain[0], plain[1], rows=plain[2])
            info["marks"][f"tank{ntank}_created"] = created
            if res is None:
                log(f"tank {ntank}: the second-pass scripts fail, trying the first-pass grid")
                res = tank_fight2(farm, g, tag=f"s5_{out}")
            if res is None:
                log(f"tank {ntank}: no script destroys it, trying the beam search")
                res = tank_fight(g, width=width)
                res = None if res is None else res[0]
            if res is None:
                log(f"tank {ntank}: no kill found")
                return None
            info["marks"][f"tank{ntank}_dead"] = len(g.rows)
            log(f"tank {ntank}: destroyed at row {len(g.rows)} ({len(res)} rows after it was created), search "
                f"{time.time() - t1:.0f} s; {g.r.summary()}")
            save_seg(f"s5/{out}_partial", g.rows, info)
        info["marks"]["auto"] = len(g.rows)
        g.save_file(f"s5/{out}_boss")
        info["ufo_wait"] = wait_for_ufo(g, route)
        if info["ufo_wait"] is None:
            log("boss: died / no UFO while waiting")
            return None
        info["marks"]["ufo_created"] = len(g.rows)
        e = ufo(g.r)
        log(f"UFO created at row {len(g.rows)}: x={e[4]} y={e[5]} hp {e[3]} state ${e[6]:02x}; rng {g.r.rng} fc {g.r.fc}")
        g.save_file(f"s5/{out}_ufo")
        t1 = time.time()
        res = ufo_fight4(farm, g, tag=f"s5_{out}")
        if res is None:
            log("UFO: no plan from the model replays, trying the scripted grid")
            res = ufo_fight3(farm, g, tag=f"s5_{out}")
        if res is None:
            log("UFO: the second-pass scripts fail, trying the first-pass grid")
            res = ufo_fight2(farm, g, tag=f"s5_{out}")
        if res is None:
            log("UFO: no script kills it, trying the beam search")
            res = ufo_fight(g, width=width)
            res = None if res is None else res[0]
        if res is None:
            log("UFO: no kill found")
            save_seg(f"s5/{out}_partial", g.rows, info)
            return None
        info["marks"]["ufo_dead"] = len(g.rows)
        log(f"UFO: HP 0 at row {len(g.rows)} ({len(res)} rows after it appeared), search {time.time() - t1:.0f} s; {g.r.summary()}")
        save_seg(f"s5/{out}_partial", g.rows, info)
        best = exit_search(farm, g, tag=f"s5_{out}")
        info["exit"] = str(best)
        info["marks"]["hidden"] = len(g.rows)
        while not (g.r.level == 5 and g.r.lr == 4):
            g.step(())
            if len(g.rows) > 12000:
                log("exit: stage 6 never started")
                return None
        info["frames"] = len(g.rows) - 1
        info["weapon"] = g.r.weapon
        pr = press_report(g.rows, history, windows=windows or WINDOWS)
        info["presses"] = pr
        info["pad_refused"] = g.pad.refused
        info["plan_refused_rows"] = sorted(x for x in THROTTLED if x < len(g.rows))
        info["lag_total"] = g.r.lagc - lag_pre
        log(f"stage 6's first frame after {len(g.rows)} rows: stage 5 = {len(g.rows) - 1} frames; weapon ${g.r.weapon:02x}, "
            f"lives {g.r.lives}, fc {g.r.fc}, rng {g.r.rng}; marks {info['marks']}")
        log(f"B presses {pr['presses']} ({info.get('run_presses', 0)} in the run phases), most in 600 / 1800 rows "
            f"{pr.get('most_600')} / {pr.get('most_1800')} (history counted); presses refused by the pad's budget "
            f"{g.pad.refused}, by the press plan on {len(info['plan_refused_rows'])} rows; look-ahead verdicts "
            f"{info.get('verdicts')}; lag frames {info.get('lag_run', 0)} in the run phases, {info['lag_total']} in all; "
            f"UFO wait: {info.get('ufo_wait')}")
        save_seg(f"s5/{out}", g.rows, info)
        return g.rows
    finally:
        farm.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    hist = None
    if "--history" in a:
        i = a.index("--history")
        hist = read_inputs(a[i + 1])
        del a[i:i + 2]
    win = WINDOWS
    if "--windows" in a:                 # the press budget, e.g. --windows 600:109,1800:246 (rule v2, the default)
        i = a.index("--windows")
        win = tuple((int(x.split(":")[0]), int(x.split(":")[1])) for x in a[i + 1].split(",") if x)
        del a[i:i + 2]
    solve(a[0] if a else "dbg/s5_pre", a[1] if len(a) > 1 else "d0", history=hist, windows=win)
