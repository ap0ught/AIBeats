"""Stage 7 (Hangar) solver.

    from contra.stages.s7 import solve
    res = solve(sim, start_state_name, history=())

Same machinery as stage 6 (s6run.Runner: closed-loop route + death-driven save-state search). Route and
measurements: knowledge/s7_notes.md.

SECOND PASS (2026-10-12): the record's route - the Barrier from the pill box at x 1552 - and scripted procedures
(contra/stages/s7b.py), each found by a small grid on save states and memoised: the F capsule at the first cart,
the wall-top jumps over the two rising walls, the claw corridor before the cart 1424, the Barrier grab, the cart
landings, Heartbreak Alley, the trio and the door fight. The first pass's version is s7.py.backup_pass1.
Parameters: lead_pause (phase scans), b_step, a_cart, e_fire_range, boss_beam (the first pass's beam search).
"""
from __future__ import annotations

from .s6lib import Fr, Sim
from .s6run import (Call, Drop, Hold, Jump, JumpSteer, Land, Mark, Proc, Remedy, Run, Runner, Set, Step, Stuck,
                    Until, beam_search, make_fire_policy)
from .s6 import exit_proc as _exit_proc
from . import s7b

T_CLAW, T_RISE, T_WALL, T_CARTGEN, T_MCART, T_CART, T_DOOR, T_MORTAR = 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17
T_SOLDIER, T_SNIPER, T_TURRETMAN, T_CAPSULE, T_ITEM, T_PILLBOX = 0x05, 0x06, 0x0E, 0x03, 0x00, 0x02


def target_box(e, r=None):
    t = e["type"]
    if t == T_MCART and r is not None and r.user.get("shoot_mcart") and 0 < e["hp"] < 0xF0 and e["routine"] < 5:
        return (16, 12)                 # the rolling cart on the lower floor of screen 5 (3 HP): in the way
    if e["state"] & 0x80 or not (0 < e["hp"] < 0xF0):
        return None
    if t in (T_SOLDIER, T_SNIPER):
        return (6, 14)
    if t == T_TURRETMAN:
        return (10, 12)
    if t == T_WALL:
        return (8, 60) if (e["attr"] & 3) == 2 else (8, 30)
    if t == T_RISE:
        if r is not None and r.user.get("spare_walls"):
            return None              # the first rising wall must stay whole: Bill lands on its top
        return (8, 30, -20)          # the wall grows upward from its base: aim at its body, not its foot
    if t == T_DOOR:
        return (12, 14)
    return None


def avoid_box(e, r=None):
    t = e["type"]
    if t == T_CART:
        return (16, 12)                 # stationary carts are ridden: never shot
    if t == T_MCART:
        if r is not None and r.user.get("shoot_mcart"):
            return None
        return (16, 12)
    if t == T_CAPSULE and (e["attr"] & 7) in (1, 2, 4):       # M, F, L capsules: an item we must not release
        return (12, 12)
    return None


target_box.wants_runner = True
avoid_box.wants_runner = True
_base_fire_policy = make_fire_policy(target_box, avoid_box)


def fire_policy(r, want, aim_over):
    """The generic Spread auto-aim, silenced while a flying capsule that holds M, F or L is on screen ahead of
    Bill (or just behind him): the capsule flies right at 1.5 px/frame through the line of fire for about 250
    frames, and the prediction in avoid_box is not exact for its sine path."""
    f = r.c.f
    for e in f.enemies():
        if e["type"] == T_CAPSULE and (e["attr"] & 7) in (1, 2, 4) and e["x"] > f["x"] - 24:
            return want
    return _base_fire_policy(r, want, aim_over)

P = {}


def set_user(**kw):
    def fn(r, st):
        r.user.update(kw)
        if "fire_range" in kw:
            r.fire_range = kw["fire_range"]
        return None
    return Call(fn, f"user {kw}")


def route_a(p=P):
    """Start -> the first cart (world x about 620). Lower route under the five claws of screen 1."""
    return [
        Mark("start"),
        Run(256), Land(y=196),                      # off the first floor (stand 132) to the lower floor
        Mark("lower1"),
        Jump(p.get("a_step", 458)), Land(y=164),    # up the step at 480 (after the last claw at 438)
        Mark("step1"),
        # SECOND PASS: a jump from the step that lands on the cart's REAR edge (boards at 613 instead of 625:
        # 27 frames on the cart instead of 15, 8 frames faster than walking off the step at 608)
        Jump(p.get("a_cart", 550), skip_y=176), Land(),
        Mark("cart1"),
        Proc(s7b.memo(s7b.capsule_proc, "F capsule"), "F capsule"),
    ]


def route_b(p=P):
    """Floor after the first cart -> the step with the two rising walls -> the ledge with the three tall walls.
    MEASURED (first pass): the first rising wall (852) can be jumped and LANDED ON (its top, x 848..864, is
    safe, 32 px above the step); from its top a second jump clears the second wall (884) and lands on the step at
    920, and a third jump reaches the ledge at 928 (Bill is held by the ledge's side wall until it has risen).
    SECOND PASS: the jump to the step starts at 762 (the first point clear of the claw at 758), so Bill lands at
    811 and the wall-top jump needs no pull-back: on the wall's top 6 frames sooner (s7b.walls2_proc)."""
    return [
        set_user(spare_walls=True),                 # the rising walls are not shot: wall 1 is landed on
        Jump(p.get("b_step", 762)), Land(y=164),    # up the step at 800 (after the claws at 742 / 758)
        Mark("step2"),
        Proc(s7b.memo(s7b.walls2_proc, "rising walls"), "rising walls"),      # wall-top jumps, parameters by trial
        set_user(spare_walls=False),
        Mark("walls3"),
        Run(1216), Land(y=196),                     # past the three tall walls, off the ledge to the floor
        Mark("lower2"),
    ]


def route_c(p=P):
    """SECOND PASS. Lower floor under the claws of screen 5 -> cart 1424 ("Chariot Hop") -> small ledge -> the
    Barrier pill box (s7b.bgrab_proc) -> floor -> step 1632 -> ledge 1696 -> off at 1792 (cart 1824)."""
    return [
        Set(aim_mode="off"),
        Proc(s7b.memo(s7b.precart_proc, "claw corridor"), "claw corridor"),    # claws 1270..1398, the rolling cart; the cart 1424 must live
        Mark("precart"),
        Proc(s7b.memo(s7b.bgrab_proc, "B grab"), "B grab"),
        Mark("bgrab"),
        Set(aim_mode="off"),                        # invincible from here to the trio: no shots (they only lag)
        Jump(p.get("c_step", 1596)), Land(y=164),   # step at 1632
        Jump(p.get("c_up", 1652)), Land(y=132),     # ledge at 1696 (claws at 1718, 1750 above it)
        Mark("ledge3"),
        # cart 1824: a jump from the ledge that lands on its rear edge (29 frames on it) or the walk off at 1792
        Proc(s7b.memo(s7b.jump_choice(1920, (None, 1741, 1742, 1743, 1744, 1745), "cart 1824", need_y=196), "cart 1824"), "cart 1824"),
        Mark("cart3"),
    ]


def route_d(p=P):
    """Bottom floor of screens 7-9 with the Barrier: under two hanging walls, the pit at 2320 (cart at 2376),
    Heartbreak Alley straight through (the seeking claws cannot hurt), step 2592, ledge 2656, the trio."""
    return [
        # the pit 2320..2367 and the cart at 2376 beyond it: the jump point that reaches wx 2470 soonest
        # (measured: jumps from 2305 or earlier fall into the pit; 2306 lands on the cart's rear edge)
        Run(2284),
        Proc(s7b.memo(s7b.jump_choice(2470, (2306, 2307, 2308, 2310, 2313, 2318), "pit + cart 2376", need_y=196),
                      "pit"), "pit"),
        Mark("alley"),
        Proc(s7b.memo(s7b.alley_proc, "alley"), "alley"),   # to the step at 2592; an aim tap picks the soldier luck
        Mark("trio"),
        Proc(s7b.memo(s7b.trio_proc, "trio"), "trio"),                # ledge at 2656 with the three rising walls (fire phase grid)
        Set(aim_mode=None),
        Run(2816), Land(y=196),
        Mark("lower4"),
    ]


def route_e(p=P):
    """Six claws, the rising wall, the low roof with two gunners, the last step, two more gunners."""
    return [
        Run(p.get("e_far_from", 3100)),
        # SECOND PASS: from here the auto-aim reaches further, so the gunners (10 HP, first shot about 60 frames
        # after they scroll in) are hit from the moment they appear
        set_user(fire_range=p.get("e_fire_range", 130)),
        Jump(p.get("e_step", 3316)), Land(y=164),   # step at 3360
        Mark("last"),
    ]


def door_of(f):
    for e in f.enemies():
        if e["type"] == T_DOOR:
            return e
    return None


def _act(dirs, a=False):
    def fn(k, c):
        w = set(dirs)
        if k < 2:
            w.add("B")
            if a:
                w.add("A")
        return w
    return fn


BOSS_ACTIONS = [("stand", _act(())), ("right", _act(("Right",))), ("up", _act(("Up",))),
                ("upright", _act(("Up", "Right"))), ("jump", _act((), True)), ("jumpR", _act(("Right",), True)),
                ("jumpUR", _act(("Up", "Right"), True)), ("left", _act(("Left",))), ("prone", _act(("Down",)))]


def boss_actions(m):
    return BOSS_ACTIONS


def boss_score(f, tr, parent):
    """Door HP first (x3). Shaping for the delay between a shot and its hit: bullets flying at the core's
    height, Bill's progress toward the right cap (x 176) once the reveal scroll is over."""
    if f["bossdef"]:
        return 1000.0
    d = door_of(f)
    sc = 0.0
    if f["stop"] != 0xFF:
        sc += 0.2 * (f.cam - 3400)             # not yet at the place where the reveal scroll starts: go right
    else:
        sc += 0.2 * 88 + 0.1 * (96 - f["auto"])
        sc += 0.4 * (f["x"] - 118)             # hold Right through the scroll, then walk to the cap (x 176)
    if d is not None:
        sc += float(32 - d["hp"]) * 3.0
        for (_, bx, by, br) in f.bullets():
            if br != 1 or bx > d["x"] + 10:
                continue
            dy = abs(by - d["y"])
            dx = d["x"] - bx
            if dy < 14 or (dx < 50 and abs((by - d["y"]) - dx) < 16):     # level with it, or on the 45-degree line
                sc += 0.8
    return sc


def boss_key(f):
    d = door_of(f)
    return (f.cam, f["x"], f["y"], f["rng"], f.nbullets(), d["hp"] if d else -1, f["jump"], f["aim"])


def boss_proc(r):
    c = r.c
    beam_search(r, boss_actions, boss_score, lambda f: bool(f["bossdef"]), boss_key, step=5,
                width=r.user.get("boss_width", 14), max_steps=160, log=r.log, label=r.name + " boss")
    r.marks.append(("boss_killed", len(c.rows), c.f["fc"], c.f.wx, c.f["y"]))


def exit_proc(r):
    _exit_proc(r, level=6)


def route_boss(p=P):
    return [
        Mark("boss_in"),
        # second pass: the door procedure takes over 16 frames into the reveal scroll (camera 3504); the first
        # pass's beam search started 24 px before the scroll
        Until((lambda r: r.c.f.cam >= 3488 - 24) if p.get("boss_beam") else (lambda r: r.c.f.cam >= 3504),
              ("Right",), "boss approach"),
        Mark("boss_beam"),
        Set(aim_mode="off"),
        Proc(boss_proc if p.get("boss_beam") else s7b.memo(s7b.boss_proc2, "boss"), "boss"),
        Mark("boss_dead"),
        Proc(exit_proc, "exit"),
        Mark("next_stage"),
    ]


def tag_route(route):
    """end_wx for every positional step: the world x by which the step is surely over (used to skip steps
    after a local beam search has carried Bill past them). A jump counts as over only well past its take-off
    point, so a jump the beam did not make is still made."""
    last = 0
    for st in route:
        if isinstance(st, Run):
            st.end_wx = last = st.wx
        elif isinstance(st, Jump):
            if st.wx > 0:
                last = st.wx
            st.end_wx = last + 44
        elif isinstance(st, JumpSteer):
            last = st.wx
            st.end_wx = last + 60
        elif isinstance(st, Land):
            st.end_wx = last + 62
    return route


def full_route(p=P):
    return tag_route(route_a(p) + route_b(p) + route_c(p) + route_d(p) + route_e(p) + route_boss(p))


def claw_start_row(r, slot, D):
    """Row on which the claw in `slot` last started to come down before row D (its 'frame' value leaves 0)."""
    tr = r.c.tr
    for n in range(min(D, len(tr)) - 1, 0, -1):
        a, b = tr[n - 1], tr[n]
        if b.get(f"et{slot}") != T_CLAW or not b.get(f"er{slot}"):
            return None
        if b[f"er{slot}"] != a[f"er{slot}"] and a[f"er{slot}"] <= 2 < b[f"er{slot}"]:
            return n
    return None


def candidates(r, D, s_lo, killer):
    """Cheap remedies only (a pause over a claw's trigger frame, a jump, a stop of up to 6 frames); when none
    works the runner falls back to the local beam search."""
    ktype = killer[1] if killer else None
    gen = r.candidates(D, s_lo, killer)
    out = []
    if ktype == T_CLAW:
        tau = claw_start_row(r, killer[2], D)
        if tau is not None and tau - 2 > s_lo:
            out.append([Remedy(tau - 2, "pause", 5)])
    shifts = [c for c in gen if c[0].kind == "shift"][:8]
    # second pass: never a jump against a claw (it "passes" under an idle one and then shifts the next scripted
    # jump into the rising walls); a claw is answered by a pause over its trigger frame or a short stop
    jumps = [] if ktype == T_CLAW else [c for c in gen if c[0].kind == "jump"][:10]
    waits = [c for c in gen if c[0].kind == "wait" and c[0].n <= 6][:10]
    ducks = [c for c in gen if c[0].kind == "duck"][:6] if ktype == 0x0F else []
    if ktype in (T_RISE, T_WALL):
        # a wall in the way: stop just outside its spikes and shoot it down (16 HP)
        for n in (8, 12, 16, 20, 25, 30, 36, 44):
            for back in (3, 8):
                if D - back > s_lo:
                    waits.append([Remedy(D - back, "wait", n)])
    return out + shifts + jumps + waits + ducks


def horizon(r, killer, default):
    return 60


def weapon_guard(r):
    """Picking up M / F / L (or losing Rapid) counts as a failure: checked by the runner after every frame."""
    return r.c.f["weapon"] == 0x13


def make_runner(sim, history=(), route=None, name="s7", log=print, params=None):
    p = dict(P)
    p.update(params or {})
    r = Runner(sim, route if route is not None else full_route(p), history, fire_policy, name=name, log=log)
    r.candidates_fn = candidates
    r.horizon_fn = horizon
    r.guard_fn = weapon_guard
    r.fire_range = p.get("fire_range", 60)
    r.greedy = True
    r.max_combo = 1
    r.use_local = True
    r.repair_budget = 40
    r.local_kinds = ("R", "J", "S", "D", "L")
    r.local_steps = 100
    r.local_over = 45
    r.repair_budget = 60
    r.progress_check = True          # second pass: charge a remedy the frames it really loses
    return r


SAVE_MARKS = ("cart1", "walls3", "lower2", "bgrab", "cart3", "alley", "trio", "lower4", "last", "boss_beam",
              "boss_dead")


def solve(sim, state, history=(), name="s7", log=print, params=None, save_prefix=None, max_deaths=80):
    f0 = sim.load(state)
    r = make_runner(sim, history, name=name, log=log, params=params)
    if save_prefix:
        r.save_states = True
        for st in r.route:
            if isinstance(st, Mark) and st.label in SAVE_MARKS:
                st.save = f"{save_prefix}_{st.label}"
    lead = int((params or {}).get("lead_pause", 0))
    if lead:
        # phase scans only: a pause of `lead` frames on row 40, while Bill is still dropping in (on row 0 the game
        # does not take the Start press). The frame counter runs on while the game stands still, so the stage
        # is then played as if it had started `lead` frames later in $1A terms.
        r.remedies.append(Remedy(40, "pause", lead))
    res = r.solve(max_deaths=max_deaths, back=110)
    c = r.c
    out = {"ok": res == "done", "lead_pause": lead, "frames_without_lead_pause": len(c.rows) - lead,
           "lead_pause_frames_seen": sum(1 for f in c.tr[:lead + 60] if f["pause"]), "result": res, "rows": list(c.rows), "frames": len(c.rows),
           "marks": [list(m) for m in r.marks], "remedies": [repr(x) for x in r.remedies],
           "shifts": dict(r.shifts), "lag": sum(f["lagged"] for f in c.tr), "deaths": r.deaths,
           "trials": r.trials, "local_fixes": list(r.local_fixes),
           "simulated": r.frames_simulated, "violations": c.check(), "start_fc": (f0["fc"] + 1) & 255,
           "start_rng": f0["rng"], "weapon_out": c.f["weapon"], "lives_out": c.f["lives"],
           "saved": list(r.saved), "procs": {k: v for k, v in r.user.items()
                                              if k in ("capsule", "precart", "bgrab", "walls2", "alley", "trio", "boss", "jump_choice")}}
    if save_prefix and res == "done":
        sim.save(f"{save_prefix}_end")
    return out
