"""Stage 6 (Energy Zone) solver.

    from contra.stages.s6 import solve
    rows, info = solve(sim, start_state_name, history=())

The start state is one frame before the stage's first playable frame (or any later frame of the stage: the
route is closed-loop on world position). Returns the input rows up to and including the frame on which the next
stage's level routine first reads 4 (segment end), and a dict of facts (marks, lag, remedies used).

Route (measured in knowledge/s6_notes.md): stairs, top ledge, drop to the bottom floor, three "towers" of
flame jets (the LEFT-pointing jets fire on the global frame counter), bottom floor to the boss.
"""
from __future__ import annotations

import math

from .s6lib import Fr, Sim
from .s6run import (Call, Drop, Hold, Jump, Land, Mark, Proc, Remedy, Run, Runner, Set, Step, Stuck, Until,
                    aim_options, beam_search, make_fire_policy, predicted_hits)

T_SOLDIER, T_SNIPER, T_TURRETMAN, T_BOSS = 0x05, 0x06, 0x0E, 0x13
T_DOWN, T_LEFT, T_RIGHT = 0x10, 0x11, 0x12
TARGET_TYPES = {T_SOLDIER: (6, 14), T_SNIPER: (6, 14), T_TURRETMAN: (10, 12), T_BOSS: (14, 28)}


def targets(r, f: Fr):
    prev = r.c.tr[-2] if len(r.c.tr) >= 2 else None
    out = []
    for e in f.enemies():
        box = TARGET_TYPES.get(e["type"])
        if box is None or e["state"] & 0x80 or not (0 < e["hp"] < 0xF0):
            continue
        vx = vy = 0.0
        if prev is not None and prev.get(f"er{e['slot']}", 0) and prev[f"et{e['slot']}"] == e["type"]:
            vx = e["x"] - prev[f"ex{e['slot']}"]
            vy = e["y"] - prev[f"ey{e['slot']}"]
            if abs(vx) > 8 or abs(vy) > 8:
                vx = vy = 0.0
        out.append((e["x"], e["y"], box[0], box[1], vx, vy, e["hp"]))
    return out


def fire_policy(r, want, aim_over):
    """Spread auto-aim: fire only when some pellet is predicted to hit, with the aim that hits most."""
    c = r.c
    f = c.f
    if "B" in c.pr.held or not c.can("B"):
        return want
    tg = targets(r, f)
    mode = r.aim_mode
    if not tg and mode != "always":
        return want
    grounded = c.grounded and "A" not in want
    moving = ("Right" in want) or ("Left" in want)
    scroll = 1.0 if ("Right" in want and f["x"] >= 0x80 and f["stop"] != 0xFF) else 0.0
    best = None
    for btn, ang, mdx, mdy in aim_options(grounded):
        if aim_over and not set(btn) <= want:
            continue
        if btn and not moving and grounded:
            continue            # Up/Down alone on the ground = straight up / prone: handled by the route, not here
        ok = True
        for b in btn:
            if b not in c.pr.held and not c.can(b):
                ok = False
            if b == "Up" and "Down" in c.pr.held and c.pr.must_hold("Down"):
                ok = False
            if b == "Down" and "Up" in c.pr.held and c.pr.must_hold("Up"):
                ok = False
        if not ok:
            continue
        if (("Up" in want) or ("Down" in want)) and not set(btn) >= (want & {"Up", "Down"}):
            continue            # the route already holds a vertical direction: do not fight it
        h = predicted_hits(f["x"], f["y"], ang, mdx, mdy, tg, scroll)
        key = (h, -len(btn))
        if best is None or key > best[0]:
            best = (key, btn)
    if best is None:
        return want
    if best[0][0] <= 0 and mode != "always":
        return want
    want = set(want)
    want.add("B")
    want.update(best[1])
    return want


# ----------------------------------------------------------------------------- route
P = {
    "stairs_x0": 226,
}


def route_a(p=P):
    """Start -> the foot of the first flame tower (bottom floor, world x about 1300)."""
    return [
        Mark("start"),
        Jump(p["stairs_x0"]), Land(),
        Jump(0), Land(),
        Jump(0), Land(),
        Mark("stairs"),
        Run(528),
        Land(y=196),
        Mark("bottom"),
        Jump(p.get("a_j1", 659), skip_y=148), Land(y=148),     # over the first gunner's shot, onto the middle ledge
        Jump(p.get("a_j2", 792)), Land(y=148),     # across the gap to the next middle ledge (second gunner's shot)
        Run(976), Land(y=196),
        Jump(p.get("a_pit", 1071)), Land(y=196),   # the pit under the L box
        Mark("pit"),
        Jump(p.get("a_j3", 1143)), Land(y=196),    # over the third gunner's shot, landing before the ledge at 1200
        Run(1300, y=196),
        Mark("tower1"),
    ]


def route_t1(p=P):
    """First flame tower: under the wall, three jumps up inside it (beams at y 184 / 136 / 88), over the top,
    down the shaft to the floor."""
    return [
        Mark("t1_in"),
        Jump(p.get("t1_x0", 1405)), Land(y=148),   # floor 196 -> platform 148
        Jump(0), Land(y=100),                       # -> 100
        Jump(0), Land(y=52),                        # -> top 52 (moves right over the wall while above it)
        Mark("t1_top"),
        Run(1504), Land(y=196),                     # down the shaft
        Mark("t1_out"),
    ]


def route_t2(p=P):
    """Second tower: step 164, platform 116, top 68, then the jump over the DOWN jet at 1688 to the sniper ledge."""
    return [
        Jump(p.get("t2_x0", 1568)), Land(y=164),    # floor 196 -> step 164 (ceiling at y 144 until x 1568)
        Jump(0), Land(y=116),                       # -> 116
        Jump(0), Land(y=68),                        # -> top 68
        Mark("t2_top"),
        Jump(p.get("t2_x1", 1660)), Land(y=52),     # over the DOWN jet's emitter to the sniper ledge (52)
        Mark("ledge"),
    ]


def route_t3(p=P):
    """Third tower: off the ledge onto platform 68, two Down+A drops (116, 164), out to the right on the floor."""
    return [
        Run(1826), Land(y=68),
        Drop(y=116), Mark("t3_a"),
        Drop(y=164), Mark("t3_b"),
        Run(1873), Land(y=196),
        Mark("t3_out"),
    ]


def route_b(p=P):
    """After the third tower: bottom floor, the pit under the random jet ("Leap of Faith"), then up to the
    middle ledge, down to the floor before the last platform, up onto it."""
    return [
        Mark("b_in"),
        Jump(p.get("b_pit", 2126)), Land(y=196),            # the pit 2128..2175
        Mark("b_pit"),
        Jump(p.get("b_mid", 2300), skip_y=148), Land(y=148),            # up through the middle ledge (2304..2575)
        Mark("b_mid"),
        Run(2576), Land(y=196),                             # off its end to the floor 2592..2671
        Jump(p.get("b_last", 2650), skip_y=164), Land(y=164),           # up onto the last platform (2672..)
        Mark("b_last"),
    ]


def boss_of(f):
    for e in f.enemies():
        if e["type"] == T_BOSS:
            return e
    return None


def _act(dirs, a=False):
    """One 5-frame beam step: B on its first two frames (a new Spread volley), `dirs` held throughout, and A on
    the first two frames for a jump."""
    def fn(k, c):
        w = set(dirs)
        if k < 2:
            w.add("B")
            if a:
                w.add("A")
        return w
    return fn


BOSS_ACTIONS = [("stand", _act(())), ("right", _act(("Right",))), ("up", _act(("Up",))),
                ("upright", _act(("Up", "Right"))), ("prone", _act(("Down",))), ("left", _act(("Left",))),
                ("jump", _act((), True)), ("jumpR", _act(("Right",), True)), ("jumpL", _act(("Left",), True)),
                ("downright", _act(("Down", "Right")))]


def boss_actions(m):
    f = m.f
    if f["stop"] != 0xFF or f["auto"] or not f["bossdone"]:
        # still scrolling (or not yet): Right must be held or the scroll / the reveal does not happen
        return [a for a in BOSS_ACTIONS if a[0] in ("right", "upright", "downright", "jumpR")]
    return BOSS_ACTIONS


def boss_score(f, tr, parent):
    b = boss_of(f)
    if f["bossdef"]:
        return 1000.0
    if b is None:
        return parent.score if parent else 0.0
    hp = b["hp"] if (b["hp"] > 1 or b["routine"] > 1) else 88
    sc = float(88 - hp)
    mv = b["var1"] & 3
    if b["routine"] in (2, 3):              # waiting: the latched number decides the next move
        sc += {1: 5.0, 0: 0.0, 2: -4.0, 3: -4.0}[mv]
    if b["y"] >= 150:
        sc -= 0.03 * abs(b["x"] - 22 - f["x"])
    for (_, bx, by, br) in f.bullets():     # bullets on their way to him
        if br == 1 and f["x"] < bx < b["x"] + 16 and abs(by - b["y"]) < 30:
            sc += 0.35
    return sc


def boss_key(f):
    b = boss_of(f)
    return (f["x"], f["y"], f["rng"], f.nbullets(), b["hp"] if b else -1, b["x"] if b else -1, b["y"] if b else -1,
            f["jump"], f["aim"])


def boss_proc(r):
    """From shortly before the reveal scroll until the boss-defeated flag: beam search (see beam_search)."""
    c = r.c
    while c.f.cam < 2976 - 36:
        c.frame(("Right",))
    beam_search(r, boss_actions, boss_score, lambda f: bool(f["bossdef"]), boss_key, step=5,
                width=r.user.get("boss_width", 16), max_steps=110, log=r.log, label=r.name + " boss")
    r.marks.append(("boss_killed", len(c.rows), c.f["fc"], c.f.wx, c.f["y"]))


def exit_proc(r, level=5):
    """Boss dead: walk to the right cap, let the scripted exit and the score screen pass, and stop ONE FRAME
    BEFORE the next stage's first playable frame (so the next solver starts where the debug states start)."""
    c = r.c
    prev = None
    n = 0
    while True:
        f = c.f
        if f["level"] != level and f["lroutine"] == 4:
            break
        if prev is not None:
            c.sim.mfree(prev)
        prev = c.sim.msave()
        if f["level"] == level and f["lroutine"] in (4, 8):
            c.frame(("Right",))
        else:
            c.frame(())
        n += 1
        if n > 1500:
            raise Stuck("exit: the next stage never started")
    # step back one frame: the last row produced the next stage's first playable frame
    c.sim.mload(prev)
    c.sim.mfree(prev)
    c.rows.pop()
    last = c.tr.pop()
    if last["lagged"]:
        c.lag -= 1
    c.pr = type(c.pr)(c.history + c.rows)
    c.f = c.tr[-1]


def route_boss(p=P):
    return [
        Mark("boss_in"),
        Proc(boss_proc, "boss"),
        Mark("boss_dead"),
        Proc(exit_proc, "exit"),
        Mark("next_stage"),
    ]


def full_route(p=P):
    return route_a(p) + route_t1(p) + route_t2(p) + route_t3(p) + route_b(p) + route_boss(p)


def ignition_row(r, slot, etype, D):
    """Row index (into r.c.tr) of the frame on which the hazard in `slot` last switched on before row D."""
    tr = r.c.tr
    for n in range(min(D, len(tr)) - 1, 0, -1):
        a, b = tr[n - 1], tr[n]
        if b.get(f"et{slot}") != etype or not b.get(f"er{slot}"):
            return None
        if (b[f"es{slot}"] & 1) == 0 and (a[f"es{slot}"] & 1) == 1:
            return n
    return None


def burst_end_row(r, slot, etype, before):
    """Row on which the hazard in `slot` last switched OFF before row `before` (a RIGHT jet rolls the random
    gap to its next burst on that frame)."""
    tr = r.c.tr
    for n in range(min(before, len(tr)) - 1, 0, -1):
        a, b = tr[n - 1], tr[n]
        if b.get(f"et{slot}") != etype or not b.get(f"er{slot}"):
            return None
        if (b[f"es{slot}"] & 1) == 1 and (a[f"es{slot}"] & 1) == 0:
            return n
    return None


def creation_row(r, slot, etype, before):
    """Row on which the enemy in `slot` was created (first row of its current life)."""
    tr = r.c.tr
    n = min(before, len(tr)) - 1
    if n < 0 or tr[n].get(f"et{slot}") != etype or not tr[n].get(f"er{slot}"):
        return None
    while n > 0 and tr[n - 1].get(f"et{slot}") == etype and tr[n - 1].get(f"er{slot}"):
        n -= 1
    return n


def candidates(r, D, s_lo, killer):
    """Remedies for a death at row D, cheapest first (see Runner.candidates for the generic ones)."""
    out = []
    ktype = killer[1] if killer else None
    if ktype in (T_LEFT, T_RIGHT, T_DOWN):
        tau = ignition_row(r, killer[2], ktype, D)
        if ktype == T_LEFT and tau is not None:
            # the jet fires when the frame counter hits its phase: a pause over that frame deletes the burst
            if tau - 2 > s_lo:
                out.append([Remedy(tau - 2, "pause", 5)])
        gen = r.candidates(D, s_lo, killer)
        shifts = [c for c in gen if c[0].kind == "shift"]
        jumps = [c for c in gen if c[0].kind == "jump"]
        small = []
        for n in (2, 3, 4):
            for back in (10, 40, 75):
                st = D - back - n
                if st > s_lo:
                    small.append([Remedy(st, "wait", n)])
        long = []
        for n in (6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 64, 80):
            for back in (12, 60):
                st = D - back - n
                if st > s_lo:
                    long.append([Remedy(st, "wait", n)])
        if ktype == T_RIGHT:
            # the gap to this burst was rolled from the random number when the previous burst ended: a two-frame
            # change of aim before that frame (free: Bill keeps running) re-rolls it
            # MEASURED: the gap after the first burst is the random number of the frame the jet is CREATED
            # (it scrolls in 112 px ahead of Bill), so the noise has to come before that frame
            noise = []
            e1 = creation_row(r, killer[2], ktype, D)
            if e1 is not None:
                for j in range(0, 16):
                    for btn in ("Up", "Down"):
                        st = e1 - 2 - 3 * j - (1 if btn == "Down" else 0)
                        if st > s_lo:
                            noise.append([Remedy(st, "aim", 2, (btn,))])
            # ... and a pause re-rolls it too
            for back in (6, 20, 40, 60):
                if D - back > s_lo:
                    out.append([Remedy(D - back, "pause", 5)])
            return noise + shifts + jumps[:8] + small + out + long
        if ktype == T_LEFT:
            return out + small + long[:12] + shifts[:6]
        return shifts + jumps[:8] + small + out + long
    return r.candidates(D, s_lo, killer)


def horizon(r, killer, default):
    return 130 if killer and killer[1] == T_LEFT else default


def back_for(r, killer, D, default):
    """How many rows before the death the repair must be able to change."""
    if killer and killer[1] == T_RIGHT:
        e1 = creation_row(r, killer[2], T_RIGHT, D)
        if e1 is not None:
            return max(default, D - e1 + 60)
    return default


def target_box(e):
    if e["state"] & 0x80 or not (0 < e["hp"] < 0xF0):
        return None
    return TARGET_TYPES.get(e["type"])


fire_policy2 = make_fire_policy(target_box)


def make_runner(sim, history=(), route=None, name="s6", log=print, params=None):
    p = dict(P)
    p.update(params or {})
    r = Runner(sim, route if route is not None else full_route(p), history, fire_policy2, name=name, log=log)
    r.fire_range = p.get("fire_range", 60)
    r.candidates_fn = candidates
    r.horizon_fn = horizon
    r.back_fn = back_for
    r.keep_snaps = 60
    return r


def solve(sim, state, history=(), name="s6", log=print, params=None, save_prefix=None, max_deaths=60):
    """Play stage 6 from savestate `state` (one frame before the stage's first playable frame).
    Returns a dict: ok, rows (segment: len(rows) = frames from this stage's first playable frame to the next
    stage's), marks, remedies, lag, deaths, trials, simulated."""
    f0 = sim.load(state)
    r = make_runner(sim, history, name=name, log=log, params=params)
    if save_prefix:
        r.save_states = True
        for st in r.route:
            if isinstance(st, Mark) and st.label in SAVE_MARKS:
                st.save = f"{save_prefix}_{st.label}"
    res = r.solve(max_deaths=max_deaths, back=110)
    c = r.c
    out = {"ok": res == "done", "result": res, "rows": list(c.rows), "frames": len(c.rows),
           "marks": [list(m) for m in r.marks], "remedies": [repr(x) for x in r.remedies],
           "shifts": dict(r.shifts), "lag": sum(f["lagged"] for f in c.tr), "deaths": r.deaths,
           "trials": r.trials, "local_fixes": list(r.local_fixes),
           "simulated": r.frames_simulated, "violations": c.check(), "start_fc": (f0["fc"] + 1) & 255,
           "start_rng": f0["rng"], "weapon_out": c.f["weapon"], "lives_out": c.f["lives"],
           "saved": list(r.saved)}
    if save_prefix and res == "done":
        sim.save(f"{save_prefix}_end")
    return out


SAVE_MARKS = ("tower1", "t1_out", "t3_out", "b_last", "boss_dead")
