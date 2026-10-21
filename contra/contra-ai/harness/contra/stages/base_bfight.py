"""Base boss fights (stage 2: four platings then the Eye; stage 4: three platings then the two helmets), planned on
the exact offline model (base_bsim) and executed closed-loop in the emulator.

Phase A = from the boss room's first frame to the frame the last plating's wreck is drawn (the final part starts its
64-frame count there). Phase B = from there to the frame BOSS_DEFEATED_FLAG is set. Each phase is planned by a small
portfolio of beam searches (base_bplan.Planner with different settings, one process each); the best plan is then
played in the emulator one frame at a time:

* before every frame on which the held buttons change, the emulator state is saved; if the game then turns out not
  to have read the pad on that frame (NesHawk reproduces the DMC / controller conflict: the game re-uses the previous
  frame's buttons), the frame is taken back and the rest of the phase is re-planned knowing that this frame repeats
  the previous one;
* after every frame the model is stepped with the buttons the game saw and compared with RAM; anything the model does
  not know (a lag frame, an enemy it does not track) re-loads the model from RAM, and the rest of the plan is kept
  only if the model still reaches the goal on the same frame.
"""
from __future__ import annotations

import time

from . import base_bplan as bp
from . import base_bsim as bs
from . import base_eye as be
from .base_common import BIT, Sess

E_R, E_HP, E_D, E_X, E_V1, E_V4, E_COL, E_SLOT = bs.E_R, bs.E_HP, bs.E_D, bs.E_X, bs.E_V1, bs.E_V4, bs.E_COL, bs.E_SLOT

# planner settings: (alpha, bucket size, width, far-HP weight, x bucket, jump-phase bucket)
PORTFOLIO_A = [(0.015, 2, 6000, 0.5, 4, 3), (0.03, 2, 6000, 0.25, 4, 3), (0.03, 2, 6000, 0.75, 4, 3),
               (0.02, 3, 8000, 0.25, 4, 3), (0.01, 2, 6000, 0.25, 4, 3), (0.02, 2, 6000, 1.0, 4, 3)]
# the Eye (third pass): the 4th number is now the weight of "stay under the Eye" (make_planner's far()); 0 = the
# second pass's ranking. Measured offline on four phase starts (tools/s2t_eye2.py, one setting, width 3000):
# weight 0: 149 / 145 / 151 / 187 frames from the platings' end to the flag, 1.5: 136 / 132 / 136 / 153.
# Second pass's portfolio was [(0.02, 2, 6000, 0, 4, 3), (0.01, ..), (0.03, ..), (0.02, 3, 6000, 0, 4, 2),
# (0.015, 2, 6000, 0, 6, 3), (0.02, 2, 4000, 0, 2, 3)].
PORTFOLIO_B = [(0.02, 2, 4000, 1.5, 4, 3), (0.02, 2, 4000, 0.75, 4, 3), (0.01, 2, 4000, 1.0, 4, 3),
               (0.03, 2, 4000, 2.5, 4, 3), (0.02, 3, 4000, 1.0, 4, 2), (0.02, 2, 6000, 0.0, 4, 3)]
EYE_REST = (0.02, 2, 3000, 1.5, 4, 3)      # the generic planner that finishes a prepared-jump line (base_eye)
# settings of the experimental planner _eye_planner (probe-keyed buckets; not better: 136-152 from the L2 start)
PORTFOLIO_E = [("E", 0.01, 2, 6000, 4, 3, 64, 0), ("E", 0.0, 2, 6000, 4, 3, 64, 1)]
# helmets: (alpha, bucket size, width, standing x, x tolerance, jump-phase bucket)
PORTFOLIO_H = [(0.01, 40, 5000, 128, 0, 1), (0.02, 20, 5000, 128, 0, 1), (0.02, 40, 5000, 130, 0, 1),
               (0.02, 40, 5000, 126, 0, 1), (0.02, 12, 5000, 128, 2, 1), (0.01, 20, 5000, 129, 0, 1)]
# platings + wall cannon (stage 4: the cannon is destroyed in its first opening, see s4_notes.md)
PORTFOLIO_AC = [(0.015, 2, 6000, 0.5, 4, 3), (0.01, 2, 6000, 0.25, 4, 3), (0.015, 3, 8000, 0.25, 4, 3),
                (0.012, 2, 6000, 1.0, 4, 3), (0.015, 4, 6000, 0.5, 2, 2), (0.008, 2, 6000, 0.5, 4, 3)]


def portfolio_for(sim, kill_cannon=False):
    if phase_of(sim) == "A":
        return PORTFOLIO_AC if kill_cannon else PORTFOLIO_A
    return PORTFOLIO_H if final_type(sim) == bs.T_HELMET else PORTFOLIO_B


def final_type(sim):
    return bs.T_EYE if any(e[0] == bs.T_EYE for e in sim.en) else bs.T_HELMET


def phase_of(sim):
    return "A" if sim.plates < sim.need else "B"


def frames_to_ground(sim):
    """Frames until Bill stands on the ground if nothing is pressed."""
    if not sim.jump:
        return 0
    s = sim.copy()
    n = 0
    while s.jump and n < 70:
        s.step(0, 0, 0)
        n += 1
    return n


def make_planner(sim0, phase, cfg, repeat=(), hz_margin=1, lead_b=45, x_lo=None, x_hi=None, deadline=None,
                 allow_unsafe=False, kill_cannon=False, ready_x=128, ready_by=27):
    if cfg[0] == "E":
        return _eye_planner(sim0, cfg, repeat, hz_margin, deadline)
    alpha, k, width, gamma, xb, jb = cfg
    if phase == "A":
        plates = [e for e in sim0.en if e[0] == bs.T_PLATE]
        xs = [e[E_X] for e in plates]
        closed = [e[E_D] for e in plates if e[E_R] == 2]
        t_open = sim0.t + (min(closed) + 4 if closed else 0)
        cannons = [e for e in sim0.en if e[0] == bs.T_CANNON and e[E_R] <= 3] if kill_cannon else []
        if cannons:
            xs = xs + [e[E_X] for e in cannons]
            waits = [e[E_D] + 12 for e in cannons if e[E_R] == 2]
            if waits:
                t_open = min(t_open, sim0.t + min(waits))

        def vec(s):
            v = []
            for e in s.en:
                if e[0] == bs.T_PLATE:
                    v.append(0 if e[E_R] >= 4 else (10 if e[E_HP] >= 0xF0 else e[E_HP]))
            if cannons:
                for e in s.en:
                    if e[0] == bs.T_CANNON:
                        v.append(0 if e[E_R] >= 5 else (e[E_V1] if e[E_HP] >= 0xF0 else e[E_HP]))
            return tuple(v)

        def rem_a(s):
            p, f, c = s.hp_left()
            return p + (c if cannons else 0)

        def prune_a(s):
            # a cannon that is to be destroyed must be gone before it shuts again
            for e in s.en:
                if e[0] == bs.T_CANNON and e[E_R] == 4:
                    return True
            return False

        def ready_cost(n):
            # frames (beyond ready_by) until Bill can stand at ready_x: what a late arrival costs the final part
            s = n.sim
            t = frames_to_ground(s)
            return max(0, t + max(0, abs(s.px - ready_x) - t) - ready_by)

        def far(px, v):
            t = 0.0
            for h, x in zip(v, xs):
                if h:
                    d = abs(px - x) - 40
                    if d > 0:
                        t += h * d
            return gamma * t / 48.0

        return bp.Planner(rem_a, lambda s: s.plates >= s.need, alpha=alpha, k_bucket=k, width=width,
                          vec_fn=vec, sig_fn=lambda v: tuple((h + 4) // 5 for h in v), far_fn=far if gamma else None,
                          allow_fire=lambda s: s.t >= t_open - 30, xb=xb, jb=jb, repeat=repeat, hz_margin=hz_margin,
                          cost_fn=ready_cost, deadline=deadline, prune_fn=prune_a if cannons else None)
    fin = final_type(sim0)
    if fin == bs.T_HELMET:
        return _helmet_planner(sim0, cfg, repeat, hz_margin, lead_b, deadline)
    if cfg[0] == "E":
        return _eye_planner(sim0, cfg, repeat, hz_margin, deadline)

    def allow_fire(s):
        for e in s.en:
            if e[0] == fin:
                if e[E_R] >= 3 or (e[E_R] == 2 and e[E_D] <= lead_b):
                    return True
        return False

    def vec(s):
        # (Eye HP after the bullets in the air have landed, the Eye's x then)
        for e in s.en:
            if e[0] == bs.T_EYE:
                return (0 if e[E_R] >= 5 else (16 if e[E_R] < 3 else e[E_V1] - (1 if e[E_R] == 4 else 0)), e[E_X])
        return (0, 128)

    if x_lo is None:
        x_lo, x_hi = 64, 192
    t_in = sim0.t + 60                  # Bill has until then to walk into the allowed x range

    def prune(s):
        return not (x_lo <= s.px <= x_hi) and s.t > t_in

    def far(px, v):
        # third pass: stay under the Eye (it runs at 1.25 px a frame whenever it is not being hit; a line that lets
        # it go has to wait for it to come back). gamma = 0: the second pass's ranking.
        d = abs(px - v[1]) - 6
        return gamma * d / 16.0 if d > 0 else 0.0

    return bp.Planner(lambda s: s.hp_left()[1], lambda s: s.bossdef, alpha=alpha, k_bucket=k, width=width,
                      allow_fire=allow_fire, prune_fn=prune, tie_fn=lambda n: n.sim.px + (30 if n.sim.jump else 0),
                      vec_fn=vec, sig_fn=lambda v: ((v[0] + 3) // 4,), far_fn=far if gamma else None, xb=xb, jb=jb,
                      repeat=repeat, hz_margin=hz_margin, deadline=deadline, diagonal_shots=False)


def _eye_planner(sim0, cfg, repeat, hz_margin, deadline):
    """The Eye, third pass. cfg = ("E", alpha, bucket size, width, x bucket, jump-phase bucket, lead, blockers).

    What the generic search could not find by itself: at the top of a jump a press of exactly THREE pellets puts all
    three into the Eye (centre and both +-1; the +-2 pellets of a full spray miss and hold their slots for 37
    frames), so the number of slots that are free on the frames of the jump's four presses decides the fight, and
    that is prepared long before the Eye opens (pellets fired during the 64-frame wait fly through the shut Eye and
    free their slots 22-57 frames later, at different times). So: firing is allowed from `lead` frames before the
    Eye opens, the bucket key carries the free slots on five frames around the opening (lines that prepared their
    slots differently are kept apart instead of being ranked against each other before anything has hit), busy
    slots are not penalised (alpha small or 0), and the first jump may not start more than 42 frames early."""
    _, alpha, k, width, xb, jb, lead, blockers = cfg
    eye = next(e for e in sim0.en if e[0] == bs.T_EYE)
    waiting = eye[E_D] if eye[E_R] == 2 else 0
    t_open = sim0.t + waiting
    probes = (t_open - 16, t_open - 11, t_open - 6, t_open - 1, t_open + 4) if waiting > 20 else None
    t_fire = t_open - lead
    t_in = sim0.t + 60

    def allow_fire(s):
        return s.t >= t_fire

    def allow_jump(s):
        return s.t >= t_open - 42

    def hp_of(s):
        for e in s.en:
            if e[0] == bs.T_EYE:
                return 0 if e[E_R] >= 5 else (16 if e[E_R] < 3 else e[E_V1] - (1 if e[E_R] == 4 else 0))
        return 0

    if probes is not None:
        def vec(s, probe):
            return (hp_of(s),) + tuple(probe)
    else:
        def vec(s):
            return (hp_of(s),)

    def sig(v):
        return ((v[0] + 3) // 4,) + tuple(min(5, p) for p in v[1:])

    def prune(s):
        return not (64 <= s.px <= 192) and s.t > t_in

    pl = bp.Planner(lambda s: s.hp_left()[1], lambda s: s.bossdef, alpha=alpha, k_bucket=k, width=width,
                    allow_fire=allow_fire, allow_jump=allow_jump, prune_fn=prune,
                    tie_fn=lambda n: n.sim.px + (30 if n.sim.jump else 0), vec_fn=vec, sig_fn=sig, xb=xb, jb=jb,
                    repeat=repeat, hz_margin=hz_margin, deadline=deadline, diagonal_shots=False, probe_t=probes)
    if blockers:
        t_blk = t_open - 30
        pl.shot_fn = lambda s: ((True, True) if (s.t < t_blk and not s.jump) else (False, False))
    return pl


HELMET_PEN = 30         # value of "this helmet has closed with HP left" (it would re-open some 230 frames later)


def _helmet_planner(sim0, cfg, repeat, hz_margin, lead_b, deadline):
    """The two helmets. cfg = (alpha, bucket size, width, standing x, x tolerance, jump-phase bucket): Bill walks to
    the standing x during the 64-frame wait and fights from there (the helmets can only be reached from under them;
    tools/s4_map.py). A helmet that closes with HP left is a dead end (it re-opens some 230 frames later), so the
    value counts it as HELMET_PEN extra HP while that can still be prevented and the line is dropped once it has
    happened: every line that survives has kept both helmets hittable while split (the bug of docs/Bugs.md #3)."""
    alpha, k, width, x0, tol, jb = cfg
    x0, tol = int(x0), int(tol)
    helmets = [e for e in sim0.en if e[0] == bs.T_HELMET]
    waiting = [e[E_D] for e in helmets if e[E_R] == 2]
    t_fire = sim0.t + (max(0, min(waiting) - lead_b) if waiting else 0)      # first frame a press may start
    # Bill stays on the standing x until the helmets' merged window is over, then he may move again (he has to if
    # the wall cannon is alive: its second volley comes down the middle about 85 frames after the helmets open)
    t_free = sim0.t + (min(waiting) + 36 if waiting else 0)
    # ... and he must be there from t_hold on: when firing may start, or as soon as he can get there
    # (in the air he cannot stop, only reverse: he is "there" once he has landed and walked the rest)
    t_land = frames_to_ground(sim0)
    need = t_land + max(0, abs(sim0.px - x0) - t_land) + (6 if t_land else 1)
    t_hold = max(t_fire, sim0.t + need)

    def allow_fire(s):
        return s.t >= t_fire

    def closed(e):
        return e[E_R] == 3 and not e[E_COL] and e[E_V4] > 0

    def rem(s):
        t = 0
        for e in s.en:
            if e[0] == bs.T_HELMET and e[E_R] <= 4:
                t += (e[E_V4] - (1 if e[E_R] == 4 else 0)) if e[E_R] >= 2 else 10
                if closed(e):
                    t += HELMET_PEN
        return t

    def more(s):
        # roll on until every helmet's merged window has run out (so that the value sees whether it stays open)
        for e in s.en:
            if e[0] == bs.T_HELMET and ((e[E_R] == 2) or (e[E_R] in (3, 4) and e[E_COL] and e[E_D] > 0)):
                return True
        return False

    # the shot that keeps a helmet open has to arrive on the last frame of its merged window; from jump height that
    # is about 22 frames of flight, so it is fired around t_glitch: the bucket key says how many slots a line will
    # have free then (5 = a full spray), so lines that saved slots for it are kept beside lines that spent them
    t_glitch = sim0.t + (min(waiting) + 31 - 22 if waiting else -1)

    def vec(s, probe):
        return tuple((0 if e[E_R] >= 5 else e[E_V4] - (1 if e[E_R] == 4 else 0)) for e in s.en
                     if e[0] == bs.T_HELMET) + ((min(5, probe) if probe is not None else 9),)

    def prune(s):
        if s.unsafe:
            return True
        if s.t >= t_hold and (abs(s.px - x0) > tol if s.t < t_free else not 92 <= s.px <= 164):
            return True
        for e in s.en:
            if e[0] == bs.T_HELMET and closed(e):
                return True
        return False

    return bp.Planner(rem, lambda s: s.bossdef, alpha=alpha, k_bucket=k, width=width, allow_fire=allow_fire,
                      prune_fn=prune, tie_fn=lambda n: n.sim.px + (30 if n.sim.jump else 0), vec_fn=vec,
                      sig_fn=lambda v: tuple((h + 4) // 5 for h in v[:-1]) + (v[-1],), xb=1, jb=jb, repeat=repeat,
                      hz_margin=hz_margin, deadline=deadline, diagonal_shots=False, roll_more=more, roll_horizon=80,
                      probe_t=t_glitch,
                      allow_move=(lambda s: s.t < t_hold or s.t >= t_free - 1 or s.px != x0) if tol == 0 else None)


def plan_job(job):
    """Worker (own process): one planner setting. job = dict(ram, pad, prev_act, cfg, repeat, opts).
    opts["guide"] = [(x, y)] of Bill for every frame from the first planned one: lines that leave that path by more
    than a few pixels are dropped (used to repair a plan quickly after a lost pad read)."""
    sim0 = job.get("sim") or bs.Sim.from_ram(job["ram"])
    phase = phase_of(sim0)
    opts = dict(job.get("opts", {}))
    guide = opts.pop("guide", None)
    pl = make_planner(sim0, phase, job["cfg"], repeat=job.get("repeat", ()), **opts)
    if guide:
        inner = pl.prune_fn
        t0 = sim0.t + 1
        ng = len(guide)

        def prune_g(s, inner=inner):
            i = s.t - t0
            if 0 <= i < ng:
                gx, gy = guide[i]
                if abs(s.px - gx) > 3 or abs(s.py - gy) > 14:
                    return True
            return inner(s) if inner is not None else False
        pl.prune_fn = prune_g
        pl.allow_move = None
    goals = pl.run(sim0, job["pad"], job.get("t_max", 420), extra_layers=6 if phase == "A" else 1,
                   prev_act=job.get("prev_act", 0))
    out = {"cfg": job["cfg"], "phase": phase, "stats": pl.stats, "n": None, "acts": None}
    if goals:
        g = goals[0]
        out["acts"] = g.acts()
        out["n"] = len(out["acts"])
        out["cost"] = out["n"] + (pl.cost_fn(g) if pl.cost_fn else 0)       # frames + what the end state costs later
        out["end"] = (g.sim.px, g.sim.py, g.sim.jump)
    return out


PLAN_VERSION = {"A": 0, "B": 3}      # part of the plan-cache key: bump when a phase's planner changes
LOG_FILE = None         # progress lines are also appended to this file
CACHE_DIR = None        # set to a folder to re-use plans between runs (plans are deterministic)


def plan_portfolio(pool, ram, pad, prev_act, cfgs, repeat=(), opts=None, t_max=420):
    jobs = [dict(ram=bytes(ram), pad=tuple(pad), prev_act=prev_act, cfg=c, repeat=tuple(repeat), opts=opts or {},
                 t_max=t_max) for c in cfgs]
    cf = None
    if CACHE_DIR:
        import hashlib
        import pickle
        from pathlib import Path
        # only the bytes the model reads decide the plan; hashing all of RAM is simpler and still exact
        ver = PLAN_VERSION[phase_of(bs.Sim.from_ram(ram))]
        key = hashlib.sha1(repr(((ver,) if ver else ()) + (bytes(ram), tuple(pad), prev_act, tuple(cfgs), tuple(repeat),
                                 sorted((opts or {}).items()), t_max)).encode("latin1", "replace")).hexdigest()
        cf = Path(CACHE_DIR) / f"{key}.pkl"
        if cf.exists():
            res = pickle.loads(cf.read_bytes())
            ok = [r for r in res if r["acts"] is not None]
            ok.sort(key=lambda r: (r["cost"], r["end"][0]))
            return (ok[0] if ok else None), res
    res = pool.map(plan_job, jobs) if pool is not None else [plan_job(j) for j in jobs]
    if cf is not None:
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_bytes(pickle.dumps(res))
    ok = [r for r in res if r["acts"] is not None]
    ok.sort(key=lambda r: (r["cost"], r["end"][0]))
    return (ok[0] if ok else None), res


def model_outcome(sim, pad, acts, goal_fn):
    """Frames (from now) at which the model reaches the goal when it plays acts, or None."""
    s = sim.copy()
    pad = tuple(pad)
    for i, a in enumerate(acts):
        if any(bp.PNEXT[pad[k]][a >> k & 1] < 0 for k in range(5)):
            return None
        dpad, a_new, b_new, pad = bp.sim_inputs(pad, a)
        s.step(dpad, a_new, b_new)
        if s.dead:
            return None
        if goal_fn(s):
            return i + 1
    return None


def model_matches(sim, m):
    if sim.px != m[0x334] or sim.py != m[0x31A] or sim.plates != m[0x87] or (sim.bossdef & 1) != (m[0x3B] & 1):
        return False
    for i in range(10):
        r = 0 if not m[0x388 + i] else (1 if m[0x438 + i] <= 1 else 2)
        if sim.br[i] != r:
            return False
        if r == 1 and (sim.bx[i] >> 8 != m[0x3C8 + i] or sim.by[i] >> 8 != m[0x3B8 + i]):
            return False
    for e in sim.en:
        k = e[E_SLOT]
        if e[E_R] >= 6:
            continue
        if m[0x528 + k] != e[0] or m[0x4B8 + k] != e[E_R] or m[0x578 + k] != e[E_HP] or m[0x33E + k] != e[E_X]:
            return False
        if e[0] == bs.T_HELMET and m[0x5E8 + k] != e[E_V4]:
            return False
        if e[0] == bs.T_EYE and m[0x5B8 + k] != e[E_V1]:
            return False
    return True


class BossFight:
    def __init__(self, S: Sess, pool=None, verbose=True, portfolio_a=None, portfolio_b=None):
        self.S, self.pool, self.verbose = S, pool, verbose
        self.portfolio = None       # set to a list of settings to override the built-in portfolios
        self.info = {"events": [], "plans": [], "drops": [], "resyncs": 0, "lag": 0, "backups": 0}
        self.known = set()          # row indices (in S.rows) on which the game is known not to read the pad
        self.ckpts = []             # [(snapshot, phase)] taken every CKPT frames, newest last
        self.hz_margin = 2
        self.kill_cannon = True
        self.eye_burst = True       # also try base_eye's prepared-first-jump lines for the Eye

    def say(self, *a):
        if self.verbose:
            print(*a, flush=True)
        if LOG_FILE:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a) + chr(10))

    def ram(self):
        return self.S.e.ram_all()

    def mask(self, row):
        return sum(BIT[b] for b in row)

    def plan(self, m, opts=None, quick=False):
        S = self.S
        sim = bs.Sim.from_ram(m)
        phase = phase_of(sim)
        pad = bp.pad_from_rows(S.rows)
        prev_act = bp.act_of_row(S.rows[-1]) if S.rows else 0
        t0 = time.time()
        n = len(S.rows)
        repeat = sorted(d - n for d in self.known if d >= n)
        opts = dict(opts or {})
        opts.setdefault("hz_margin", self.hz_margin)
        # stage 4: destroy the wall cannon in its first opening (while the platings are still shut); if no plan
        # manages that, plan without it
        kc = (phase == "A" and self.kill_cannon and final_type(sim) == bs.T_HELMET
              and any(e[0] == bs.T_CANNON and e[E_R] <= 3 for e in sim.en))
        if kc:
            opts["kill_cannon"] = True
        cfgs = self.portfolio or portfolio_for(sim, kc)
        if quick:
            cfgs = cfgs[:3]
        best, res = plan_portfolio(self.pool, m, pad, prev_act, cfgs, repeat=repeat, opts=opts)
        if best is None and kc and not quick:
            self.say("   no plan that destroys the cannon: planning without it")
            self.kill_cannon = False
            opts.pop("kill_cannon")
            best, res = plan_portfolio(self.pool, m, pad, prev_act, self.portfolio or portfolio_for(sim), repeat=repeat,
                                       opts=opts)
        summ = [(r["cfg"], r["n"], r["stats"]["secs"]) for r in res]
        burst = None
        if phase == "B" and not quick and "guide" not in opts and final_type(sim) == bs.T_EYE and self.eye_burst:
            # third pass: the Eye lines with a prepared first jump (base_eye), finished by the generic planner
            try:
                burst = self.burst_plan(sim, pad, prev_act, repeat, opts)
            except Exception as ex:  # noqa: BLE001
                self.say(f"   eye burst plan failed: {ex!r}")
            if burst is not None and (best is None or len(burst) < best["n"]):
                self.say(f"   prepared-jump plan: {len(burst)} frames (portfolio {best['n'] if best else None})")
                best = {"acts": burst, "n": len(burst)}
            elif burst is not None:
                self.say(f"   prepared-jump plan: {len(burst)} frames, not better than the portfolio's {best['n']}")
        self.info["plans"].append({"at": len(S.rows) - self.n0, "phase": phase, "repeat": list(repeat),
                                   "best": best["n"] if best else None, "all": summ, "secs": round(time.time() - t0),
                                   "guided": bool(quick), "burst": len(burst) if burst else None})
        self.say(f"   {'guided ' if quick else ''}plan {phase} at boss row {len(S.rows) - self.n0}: best {best['n'] if best else None} frames; "
                 f"all {[r[1] for r in summ]} ({round(time.time() - t0)} s)")
        return best["acts"] if best else None

    def burst_plan(self, sim, pad, prev_act, repeat, opts):
        """base_eye.stage1 (blocker sprays + the first jump, 20 frames past the opening) for the best few lines, each
        finished by the generic Eye planner with the tracking term. Returns the held masks to the flag or None."""
        eye = next((e for e in sim.en if e[0] == bs.T_EYE), None)
        if eye is None or eye[E_R] != 2 or eye[E_D] < 50:
            return None
        res = be.stage1(sim, pad, prev_act, repeat=set(repeat), n_exact=400, n_keep=6,
                        hz_margin=opts.get("hz_margin", 2))
        if not res:
            return None
        jobs = []
        for r in res:
            n1 = len(r[5])
            jobs.append(dict(sim=r[6], ram=None, pad=r[7], prev_act=r[5][-1], cfg=EYE_REST,
                             repeat=tuple(d - n1 for d in repeat if d >= n1),
                             opts={"hz_margin": opts.get("hz_margin", 2)}))
        out = self.pool.map(plan_job, jobs) if self.pool is not None else [plan_job(j) for j in jobs]
        best = None
        for r, o in zip(res, out):
            if o["acts"] is not None and (best is None or len(r[5]) + o["n"] < len(best)):
                best = list(r[5]) + list(o["acts"])
        return best

    def run(self):
        """From the boss room's first frame to the frame BOSS_DEFEATED_FLAG is set. Returns the info dict."""
        S = self.S
        t0 = time.time()
        self.n0 = n0 = len(S.rows)
        info = self.info
        # the room load: lag frames, then the frame on which the enemies are created
        for _ in range(40):
            s = S.step(S.pad.fix(()))
            if not s["lagged"]:
                break
            info["lag"] += 1
        m = self.ram()
        sim = bs.Sim.from_ram(m)
        info["start"] = {"row": len(S.rows) - n0, "fc": m[0x1A], "rng": m[0x34], "x": sim.px,
                         "parts": [(e[0], e[E_SLOT], e[E_X], e[bs.E_Y]) for e in sim.en]}
        acts = self.plan(m)
        if acts is None:
            info.update(ok=False, why="no plan", frames=len(S.rows) - n0)
            return info
        i = 0
        goal_a = lambda s: s.plates >= s.need            # noqa: E731
        goal_b = lambda s: s.bossdef                     # noqa: E731
        phase = "A"
        hp_prev = sim.hp_left()
        fails = 0
        CKPT = 10
        while True:
            if i < len(acts) and (len(S.rows) - n0) % CKPT == 0 and (not self.ckpts or self.ckpts[-1][2] != len(S.rows)):
                self.ckpts.append((S.snapshot(), phase, len(S.rows)))
                if len(self.ckpts) > 8:
                    S.free(self.ckpts.pop(0)[0])
            if i >= len(acts):
                # plan exhausted without the goal (should not happen): plan again from here
                acts = self.plan(self.ram())
                i = 0
                fails += 1
                if acts is None or fails > 6:
                    info.update(ok=False, why="plan exhausted", frames=len(S.rows) - n0)
                    return info
            act = acts[i]
            row = bp.act_row(act)
            prev_row = S.rows[-1] if S.rows else ()
            snap = S.snapshot() if tuple(row) != tuple(prev_row) else None
            s = S.step(row)
            if s["lagged"]:
                info["lag"] += 1
                # the game did not run this frame: say so and send the same buttons again
                S.free(snap) if snap else None
                acts = acts[:i] + [act] + acts[i:]
                i += 1
                continue
            m = self.ram()
            seen = m[0xF1]
            if seen != self.mask(row):
                info["drops"].append((len(S.rows) - n0, seen, self.mask(row)))
                if snap is not None:
                    # the game did not read the pad on this frame: take the frame back and go on knowing that this
                    # frame repeats the previous one (shift the plan by a frame if that costs at most one frame,
                    # else plan the rest of the phase again; if nothing works from here, from an earlier checkpoint)
                    S.restore(snap)
                    S.free(snap)
                    self.known.add(len(S.rows))
                    m0 = self.ram()
                    sim = bs.Sim.from_ram(m0)
                    pad0 = bp.pad_from_rows(S.rows)
                    goal = goal_a if phase == "A" else goal_b
                    prev_act = bp.act_of_row(prev_row)
                    old = len(acts) - i
                    shifted = [prev_act] + acts[i:]
                    bs.HZ_MARGIN = 0
                    sh = model_outcome(sim, pad0, shifted, goal)
                    self.say(f"   pad not read at boss row {len(S.rows) - n0 + 1}: plan needed {old} more frames, "
                             f"shifted plan gives {sh}")
                    # third pass: or only this frame's change comes a frame late and the rest keeps its timing
                    late = [prev_act] + acts[i + 1:]
                    lt = model_outcome(sim, pad0, late, goal)
                    if lt is not None and lt <= old and (sh is None or lt <= sh):
                        self.say(f"   ... this frame's change one frame late, rest unchanged: {lt} frames")
                        info.setdefault("late_repairs", 0)
                        info["late_repairs"] += 1
                        acts, i = late, 0
                        continue
                    if sh is not None and sh <= old + 1:
                        acts, i = shifted, 0
                        continue
                    # a quick search near the old plan's path first
                    g = bs.Sim.from_ram(m0)
                    gp = pad0
                    guide = []
                    for a_ in shifted:
                        if any(bp.PNEXT[gp[k]][a_ >> k & 1] < 0 for k in range(5)):
                            break
                        dpad, a_new, b_new, gp = bp.sim_inputs(gp, a_)
                        g.step(dpad, a_new, b_new)
                        guide.append((g.px, g.py))
                    new = self.plan(m0, opts={"guide": guide}, quick=True)
                    if new is not None and len(new) <= old + 2 and (sh is None or len(new) < sh):
                        acts, i = new, 0
                        continue
                    new = self.plan(m0)
                    if new is not None and (sh is None or len(new) < sh):
                        acts, i = new, 0
                        continue
                    if sh is not None:
                        acts, i = shifted, 0
                        continue
                    new = None
                    while self.ckpts and new is None:
                        ck, ph, _ = self.ckpts.pop()
                        S.restore(ck)
                        S.free(ck)
                        info["backups"] += 1
                        m0 = self.ram()
                        self.say(f"   going back to boss row {len(S.rows) - n0}")
                        new = self.plan(m0)
                    if new is None:
                        info.update(ok=False, why="no plan after a lost pad read", frames=len(S.rows) - n0)
                        return info
                    sim = bs.Sim.from_ram(m0)
                    hp_prev = sim.hp_left()
                    acts, i = new, 0
                    continue
            if snap is not None:
                S.free(snap)
            dpad, a_new, b_new = seen & 0x0F, seen & m[0xF5] & 0x80, seen & m[0xF5] & 0x40
            sim.step(dpad, 1 if a_new else 0, 1 if b_new else 0)
            i += 1
            if m[0x90] != 1 and not m[0x3B]:
                info.update(ok=False, why=f"player state {m[0x90]} at boss row {len(S.rows) - n0}", frames=len(S.rows) - n0)
                return info
            if not model_matches(sim, m):
                info["resyncs"] += 1
                sim = bs.Sim.from_ram(m)
                goal = goal_a if phase == "A" else goal_b
                if not goal(sim):
                    left = model_outcome(sim, bp.pad_from_rows(S.rows), acts[i:], goal)
                    self.say(f"   model re-loaded from RAM at boss row {len(S.rows) - n0}; rest of the plan: "
                             f"{left} frames (was {len(acts) - i})")
                    if left is None or left > len(acts) - i:
                        new = self.plan(m)
                        if new is not None and (left is None or len(new) < left):
                            acts, i = new, 0
                        elif left is None:
                            info.update(ok=False, why="no plan after a model mismatch", frames=len(S.rows) - n0)
                            return info
            hp = sim.hp_left()
            if hp != hp_prev:
                info["events"].append((len(S.rows) - n0, hp))
                hp_prev = hp
            if phase == "A" and m[0x87] >= sim.need:
                info["plates_done"] = len(S.rows) - n0
                self.say(f"   platings gone at boss row {info['plates_done']} (Bill at x {sim.px}, {'air' if sim.jump else 'ground'})")
                phase = "B"
                for ck in self.ckpts:
                    S.free(ck[0])
                self.ckpts = []
                acts = self.plan(m)
                i = 0
                if acts is None:
                    info.update(ok=False, why="no plan for the final part", frames=len(S.rows) - n0)
                    return info
                continue
            if m[0x3B]:
                break
        info.update(ok=True, frames=len(S.rows) - n0, secs=round(time.time() - t0), end_x=m[0x334],
                    end_jump=1 if m[0xA0] else 0)
        return info


def solve_boss(S: Sess, procs=None, verbose=True, **_):
    """Boss fight for the stage drivers (s2.py / s4.py): from the boss room's first frame to the frame
    BOSS_DEFEATED_FLAG is set. The portfolio runs in `procs` worker processes (env BASE_BOSS_PROCS, default 6);
    the calling script must be import-safe (if __name__ == "__main__") because the workers are spawned."""
    import multiprocessing as mp
    import os
    procs = procs or int(os.environ.get("BASE_BOSS_PROCS", "6"))
    n0 = len(S.rows)
    if procs <= 1:
        info = BossFight(S, pool=None, verbose=verbose).run()
    else:
        with mp.get_context("spawn").Pool(procs) as pool:
            info = BossFight(S, pool=pool, verbose=verbose).run()
    info["frames"] = len(S.rows) - n0
    return info
