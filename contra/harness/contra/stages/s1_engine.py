"""Run-with-repair search shared by the stage 1 and stage 5 solvers.

Route       what a run policy follows: jump positions, aims, and the per-frame edits found by this run's search
Repair      greedy closed-loop run with save-state backtracking around every failure (death, wrong weapon, pit...)
beam        beam search over short fixed steps (fights; local fallback of Repair)
local_beam  the fallback: run / jump / duck / wait choices on top of the run policy
pit_ahead   early pit detection from the background collision map

Rule v2 (2026-10-12; the version before it is s1_engine.py.backup_v2):
  * the press budget lives in s1_common.Pad: a press the budget refuses is missing from the row that is played, so
    every search here sees it as "cannot fire now";
  * the run policies no longer mash. New edit kind for the repair search: 'fire' (rows on which the policy fires
    at the fastest legal cadence whatever it sees - the old behaviour, locally) next to 'nofire'; among edits that
    reach the goal on the same row the one with the fewest B presses wins;
  * Repair(engage=...): "let it pass". When the policy is about to open fire on an enemy for the first time, the
    main run looks ahead with save states - once without ever firing at it, once firing - and fires only if not
    firing gets Bill killed or costs frames. The verdicts are kept in route.opts['dec'].
"""
from __future__ import annotations

import os
import time

from .s1_common import Farm, Game, Pad, Ram, fire, log


class Route:
    """jumps   set of world X (screen*256 + scroll + x) at which A is pressed, on the ground
    aims    [(prog_lo, prog_hi, aim)]: aim while firing in that stretch ('auto' = the policy's own choice)
    nofire  [(prog_lo, prog_hi)]: no B there
    over    {row index: [edit, ...]}: per-frame edits found by the repair search in THIS run
            edit = ('add', button) | ('set', buttons) | ('aim', a) | ('nofire',) | ('nojump',) | ('fire',)
            ('fire',) and ('aim', a) = fire on this row at the fastest legal cadence, target or not
    opts    free-form options the stage's policy reads (copied with the route; the values are shared)
            'dec' = [(enemy slot, enemy type, first row, last row, 'pass' | 'shoot')]: the look-ahead verdicts
    """

    def __init__(self, jumps=(), aims=(), nofire=(), opts=None):
        self.jumps = set(jumps)
        self.aims = list(aims)
        self.nofire = list(nofire)
        self.over = {}
        self.opts = dict(opts or {})

    def copy(self):
        r = Route(self.jumps, self.aims, self.nofire, self.opts)
        r.over = {k: list(v) for k, v in self.over.items()}
        return r

    def add_over(self, i, edit):
        self.over.setdefault(i, []).append(edit)

    def apply_edit(self, ed):
        """ed = (kind, t0, n, arg): rows t0 .. t0+n-1; kind 'opt' sets opts[t0] = arg; 'jump+', 'jump-',
        'jumpmove' edit the jump set (t0 = world X)."""
        kind, t0, n, arg = ed
        if kind == "opt":
            self.opts[t0] = arg
            return
        if kind == "jump+":
            self.jumps.add(t0)
            return
        if kind == "jump-":
            self.jumps.discard(t0)
            return
        if kind == "jumpmove":
            self.jumps.discard(t0)
            self.jumps.add(arg)
            return
        for i in range(t0, t0 + n):
            if kind == "J":
                self.add_over(i, ("add", "A"))
            elif kind == "aim":
                self.add_over(i, ("aim", arg))
            elif kind == "set":
                self.add_over(i, ("set", arg))
            elif kind == "nofire":
                self.add_over(i, ("nofire",))
            elif kind == "fire":
                self.add_over(i, ("fire",))
            elif kind == "nojump":
                self.add_over(i, ("nojump",))
            elif kind == "add":
                self.add_over(i, ("add", arg))

    def aim_at(self, prog):
        for lo, hi, a in self.aims:
            if lo <= prog < hi:
                return a
        return "auto"

    def fire_at(self, prog):
        for lo, hi in self.nofire:
            if lo <= prog < hi:
                return False
        return True

    def verdict(self, row, slot, etype):
        """'pass' / 'shoot' if a look-ahead verdict covers this enemy slot on this (absolute) row, else None."""
        for d in reversed(self.opts.get("dec", ())):
            if d[0] == slot and d[1] == etype and d[2] <= row <= d[3]:
                return d[4]
        return None


class Repair:
    """Greedy run with save-state backtracking: play policy(g, route); when fail(g) is true, go back and look for
    the change that gets the player `ahead` px past the failure point soonest:
      1. single free edits (aim, hold fire, move or drop a planned jump), then single extra jumps;
      2. otherwise the better of a single short stop and a local beam search (run / jump / duck / wait);
      3. otherwise the same edits from further back, or the edit that at least gets furthest."""

    NEAR = ((0, 60), (0, 110), (1, 60), (1, 110))
    STOPS = ((2, 60), (2, 110))
    FAR = ((0, 180), (1, 180), (2, 180), (0, 300), (1, 300), (2, 300))

    def __init__(self, farm: Farm, policy, fail, ahead=110, tag="rep", verbose=True, plan=None, mark=None,
                 local=None, engage=None, look=170, fail_look=None, sight=None):
        self.farm, self.policy, self.fail = farm, policy, fail
        self.sight = sight          # sight(g) -> [(enemy slot, enemy type)] of the hostile targets present
        self.sightings = []         # [(row of the main run on which a target first appeared, (slot, type))]
        self._seen = None
        self.engage = engage        # engage(g, route) -> (enemy slot, enemy type) the policy is about to open fire on, or None
        self.look = look            # rows of look-ahead for a "let it pass" verdict
        self.fail_look = fail_look or fail
        self.verdicts = {"pass": 0, "shoot": 0}
        self.look_rows = 0
        self.ahead, self.tag, self.verbose = ahead, tag, verbose
        self.plan = plan            # plan(g, route, D, why, marks) -> [(mark name, [edits])] or None for the default
        self.mark = mark            # mark(g) -> name or None: keep a snapshot under that name (first time only)
        self.local = local          # local(g, route, until(g)) -> rows played from g's state, or None
        self.marks = {}
        self.repairs = []
        self.evals = 0
        self.done = None

    # ---- one trial on any emulator of the farm
    def _eval(self, g: Game, job):
        keep = g.rows                           # g may be the main game: its row list must survive the trial
        try:
            return self._eval2(g, job)
        finally:
            g.rows = keep

    def _eval2(self, g: Game, job):
        state, pad, n0, route, limit, ptarget = job
        g.load_file(state, pad)
        base = g.r.prog
        t_load = g.pad.t
        why, reached, k = None, False, 0
        rt = route.copy()                       # rows in this game count from the loaded state: shift the edits
        rt.over = {i - n0: v for i, v in route.over.items() if i >= n0}
        rt.opts = dict(route.opts)
        rt.opts["row0"] = n0
        while k < limit:
            g.step(self.policy(g, rt))
            k += 1
            why = self.fail(g)
            if why:
                break
            if g.r.prog >= ptarget or (self.done is not None and self.done(g)):
                reached = True
                break
        return {"ok": reached, "why": why or ("" if reached else "slow"), "frames": k, "prog": g.r.prog - base,
                "aprog": g.r.prog, "presses": sum(1 for x in g.pad.starts["B"] if x >= t_load)}

    # ---- "let it pass": look ahead on the main game before the first shot at an enemy
    def _look(self, g: Game, route: Route, n, slot, etype):
        """Play n rows of the policy from g's state. Returns (survived, world X reached, rows until the enemy in
        `slot` was gone)."""
        gone = None
        route.opts["_look"] = True
        try:
            for k in range(n):
                g.step(self.policy(g, route))
                self.look_rows += 1
                if self.fail_look(g):
                    return False, g.r.prog, gone if gone is not None else k + 1
                e = g.r.enemy(slot)
                if gone is None and (e is None or e[1] != etype):
                    gone = k + 1
                if self.done is not None and self.done(g):
                    break
        finally:
            route.opts.pop("_look", None)
        return True, g.r.prog, gone if gone is not None else n

    def _decide(self, g: Game, route: Route):
        i = len(g.rows)
        if i < route.opts.get("decide_from", 0) or i in route.over:
            return
        eng = self.engage(g, route)
        if eng is None:
            return
        slot, etype = eng
        dec = route.opts.setdefault("dec", [])
        tok = g.snap()
        dec.append((slot, etype, i, i + self.look, "pass"))
        ok_a, prog_a, gone_a = self._look(g, route, self.look, slot, etype)
        g.restore(tok)
        verdict = "shoot"
        gone = self.look
        if ok_a:
            dec[-1] = (slot, etype, i, i + self.look, "shoot")
            ok_b, prog_b, gone = self._look(g, route, self.look, slot, etype)
            g.restore(tok)
            if not ok_b or prog_a >= prog_b:
                verdict, gone = "pass", gone_a
        # the verdict holds while this enemy is in its slot (as seen in the look-ahead that was chosen)
        dec[-1] = (slot, etype, i, i + max(8, gone), verdict)
        self.verdicts[verdict] += 1
        g.free(tok)
        if os.environ.get("S1_REPAIR_DEBUG"):
            log(f"      verdict row {i}: enemy slot {slot} type ${etype:02x} -> {verdict} (until row {i + max(8, gone)})")

    def candidates(self, D, t0, route=None, p0=None, p1=None):
        """Edits to try from row t0 for a failure at row D: (free, jumps, stops). With the route and the world X
        at t0 / at the failure, the free tier also moves or drops the planned jumps in between."""
        span = max(20, D - t0)
        st = max(10, span // 6)
        c0, c1, c2 = [], [], []
        if route is not None and p0 is not None:
            for P in sorted(route.jumps):
                if p0 < P <= p1 + 12:
                    for dd in (-3, 3, -6, 6, -10, 10, -15, 15, -22, 22, -30, 30):
                        if P + dd > p0 and (P + dd) not in route.jumps:
                            c0.append(("jumpmove", P, 0, P + dd))
                    c0.append(("jump-", P, 0, None))
        for t in range(D - 4, max(t0, D - 120), -3):
            c1.append(("J", t, 2, None))
        for t in range(D - 124, t0, -8):
            c1.append(("J", t, 2, None))
        for n in (12, 40, 100):
            for t in range(D - 6, t0, -st):
                for a in ("U", "D", "F"):
                    if t - n >= t0:
                        c0.append(("aim", t - n, n, a))
        for n in (10, 25, 60):
            for t in range(D - 6, t0, -st):
                if t - n >= t0:
                    c0.append(("nofire", t - n, n, None))
        for n in (10, 25, 60):
            for t in range(D - 6, t0, -st):
                if t - n >= t0:
                    c0.append(("fire", t - n, n, None))
        # planned pre-fire: volleys timed to arrive when an enemy that appeared shortly before the failure appears
        for (srow, _key) in self.sightings:
            if D - 90 <= srow < D:
                for n in (7, 12, 45, 80):
                    for t in range(srow - 46, srow - 29, 2):
                        if t >= t0 and ("fire", t, n, None) not in c0:
                            c0.append(("fire", t, n, None))
        for n in (4, 6, 10, 16):                   # short stops that end after the failure row (duck under a shot)
            for end in (D + 2, D + 6, D - 2):
                if end - n >= t0:
                    c2.append(("set", end - n, n, ("Down", "B*")))
                    c2.append(("set", end - n, n, ("B*",)))
        for n in (8, 16, 32, 48):
            for t in range(D - 8, t0, -max(8, span // 5)):
                if t - n >= t0:
                    c2.append(("set", t - n, n, ("Down", "B*")))
                    c2.append(("set", t - n, n, ("B*",)))
        return c0, c1, c2

    def _try(self, g, route, tok, i0, cands, D, ptarget, label):
        """Evaluate edits from snapshot tok (row i0). Returns (best edit, row it reaches the target on, n ok,
        (furthest world X of a failing edit, that edit))."""
        if not cands:
            return None, None, 0, None
        g.restore(tok)
        st = g.save_file(f"tmp/{self.tag}_base")
        pad = g.pad.copy()
        limit = (D - i0) + self.ahead + 80
        jobs = []
        for c in cands:
            rt = route.copy()
            rt.apply_edit(c)
            jobs.append((st, pad, i0, rt, limit, ptarget))
        res = self.farm.map(self._eval, jobs)
        self.evals += len(jobs)
        # the soonest arrival wins; among equals the one that pressed B least, then the first in the list
        oks = [(x["frames"], x.get("presses", 0), n, c) for n, (c, x) in enumerate(zip(cands, res)) if x["ok"]]
        if os.environ.get("S1_REPAIR_DEBUG"):
            log(f"      try {label} from row {i0} (D {D}): " + "; ".join(
                f"{c[0]}{c[1:]}:{'ok' if x['ok'] else x['why']}@{x['frames'] + i0}/X{x['aprog']}" for c, x in
                sorted(zip(cands, res), key=lambda t: -t[1]["aprog"])[:8]))
        if oks:
            oks.sort(key=lambda t: t[:3])
            return oks[0][3], oks[0][0] + i0, len(oks), None
        far = max(zip(cands, res), key=lambda t: (t[1]["aprog"], -t[1]["frames"]))
        return None, None, 0, (far[1]["aprog"], far[0])

    def _search(self, g, route, ring, D, why, ptarget, combos, pfail, best_fail):
        """Tiers x look-back distances in the given order. Returns ((tok, i0, edit, arrival row) or None, best_fail)."""
        tried = set()
        for tier, back in combos:
            idx = [k for k, (i, tok) in enumerate(ring) if i <= D - back]
            i0, tok = ring[idx[-1] if idx else 0]
            if (tier, i0) in tried:
                continue
            tried.add((tier, i0))
            cands = self.candidates(D, i0, route, tok[3].prog, pfail)[tier]
            cands = [c for c in cands if c[1] >= i0 or c[0] in ("jumpmove", "jump-")]
            ed, arrive, nok, bf = self._try(g, route, tok, i0, cands, D, ptarget, f"back {back} tier {tier}")
            if ed is not None:
                if self.verbose:
                    log(f"   repair @{D} ({why}) back {back} tier {tier}: {ed} reaches X {ptarget} on row {arrive} "
                        f"({nok}/{len(cands)} ok)")
                return (tok, i0, ed, arrive), best_fail
            if bf is not None and (best_fail is None or bf[0] > best_fail[0]):
                best_fail = (bf[0], tok, i0, bf[1])
        return None, best_fail

    def _commit(self, g, route, ring, fix, D, why):
        tok, i0, ed, arrive = fix
        route.apply_edit(ed)
        self.repairs.append((D, why, ed, arrive))
        # the trial that chose this edit made no new look-ahead verdicts: neither does the main run until it is
        # past the row the trial reached, so that it replays the trial exactly
        route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive if arrive is not None else D)
        self.sightings = [x for x in self.sightings if x[0] <= i0]
        self._seen = None
        in_ring = any(t is tok for (_, t) in ring)
        for (i, t) in ring:
            if i > i0:
                g.free(t)
        ring[:] = [(i, t) for (i, t) in ring if i <= i0]
        for name in [n for n, (i, t) in self.marks.items() if i > i0]:
            g.free(self.marks.pop(name)[1])
        g.restore(tok)
        if not ring or not in_ring:
            ring.append((i0, g.snap()))

    def _handle(self, g, route, ring, D, why):
        """Find and apply a fix for the failure at row D. False if nothing works."""
        pfail = g.r.prog
        ptarget = pfail + self.ahead
        plans = self.plan(g, route, D, why, self.marks) if self.plan else None
        if plans:
            for name, cands in plans:
                if name not in self.marks:
                    continue
                i0, tok = self.marks[name]
                ed, arrive, nok, bf = self._try(g, route, tok, i0, cands, D, ptarget, name)
                if ed is not None:
                    if self.verbose:
                        log(f"   repair @{D} ({why}) from mark {name}: {ed} reaches the goal on row {arrive} ({nok}/{len(cands)} ok)")
                    self._commit(g, route, ring, (tok, i0, ed, arrive), D, why)
                    return True
        fix, best_fail = self._search(g, route, ring, D, why, ptarget, self.NEAR, pfail, None)
        if fix is not None:
            self._commit(g, route, ring, fix, D, why)
            return True
        fix, best_fail = self._search(g, route, ring, D, why, ptarget, self.STOPS, pfail, best_fail)
        if self.local is not None:
            for back in (100, 200):
                idx = [k for k, (i, tok) in enumerate(ring) if i <= D - back]
                i0, tok = ring[idx[-1] if idx else 0]
                g.restore(tok)
                t_b = time.time()
                res = self.local(g, route, lambda gg: gg.r.prog >= ptarget or (self.done is not None and self.done(gg)))
                if res is None:
                    g.restore(tok)
                    continue
                arrive = len(g.rows)
                route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive)
                self.sightings = [x for x in self.sightings if x[0] <= i0]
                self._seen = None
                log(f"   local search @{D} ({why}) from row {i0}: reaches X {ptarget} on row {arrive}, {time.time() - t_b:.0f} s"
                    + (f" (single stop: row {fix[3]})" if fix else ""))
                if fix is not None and fix[3] <= arrive:
                    break                         # the single stop is at least as fast
                self.repairs.append((D, why, ("local", i0, len(res), None), arrive))
                # keep the found rows as per-frame 'set' edits, so that a later repair that goes back into
                # this stretch replays them exactly; then replay from the snapshot to rebuild the ring
                for k, row in enumerate(res):
                    route.over[i0 + k] = [("set", tuple(row))]
                for (i, t) in ring:
                    if i > i0:
                        g.free(t)
                ring[:] = [(i, t) for (i, t) in ring if i <= i0]
                for name in [n for n, (i, t) in self.marks.items() if i > i0]:
                    g.free(self.marks.pop(name)[1])
                g.restore(tok)
                if not ring:
                    ring.append((i0, g.snap()))
                for k, row in enumerate(res):
                    g.step(row)
                    if len(g.rows) % 10 == 0:
                        ring.append((len(g.rows), g.snap()))
                return True
        if fix is None:
            fix, best_fail = self._search(g, route, ring, D, why, ptarget, self.FAR, pfail, best_fail)
        if fix is not None:
            self._commit(g, route, ring, fix, D, why)
            return True
        if best_fail is not None and best_fail[0] >= pfail + 16:
            if self.verbose:
                log(f"   repair @{D} ({why} at world X {pfail}): nothing reaches X {ptarget}; taking {best_fail[3]} "
                    f"which gets to X {best_fail[0]}")
            self._commit(g, route, ring, (best_fail[1], best_fail[2], best_fail[3], None), D, why)
            return True
        return False

    def run(self, g: Game, route: Route, done, max_rows=20000, ring_every=10, ring_len=40):
        ring = [(len(g.rows), g.snap())]
        fails_here = {}
        ok = True
        self.done = done
        while not done(g):
            if len(g.rows) >= max_rows:
                ok = False
                break
            if self.mark:
                name = self.mark(g)
                if name and name not in self.marks:
                    self.marks[name] = (len(g.rows), g.snap())
            if self.engage is not None:
                self._decide(g, route)
            g.step(self.policy(g, route))
            if self.sight is not None:
                cur = set(self.sight(g))
                if self._seen is not None:
                    for key in cur - self._seen:
                        self.sightings.append((len(g.rows), key))
                self._seen = cur
            why = self.fail(g)
            if why:
                D = len(g.rows)
                fails_here[D // 40] = fails_here.get(D // 40, 0) + 1
                if fails_here[D // 40] > 6:
                    log(f"   giving up at row {D}: {why} ({g.r.summary()})")
                    ok = False
                    break
                if not self._handle(g, route, ring, D, why):
                    log(f"   no repair for {why} at row {D} ({g.r.summary()})")
                    ok = False
                    break
                continue
            if len(g.rows) % ring_every == 0:
                ring.append((len(g.rows), g.snap()))
                if len(ring) > ring_len:
                    g.free(ring.pop(0)[1])
        for (_, tok) in ring:
            g.free(tok)
        for name, (i, tok) in self.marks.items():
            g.free(tok)
        self.marks = {}
        return ok


# ------------------------------------------------------------------------------------------------ beam search
def beam(g: Game, actions, step_rows, score, done, width=8, max_steps=80, step=5, dedupe=None, fail=None,
         verbose=True, tag="beam", reserve_levels=8, lookahead=None, look_steps=4, max_seconds=None):
    """Beam search over fixed-length steps from g's current state.

    actions(g) -> [action names] available now; step_rows(g, action, k) -> buttons wanted on frame k of the step;
    score(g) -> tuple, smaller is better; done(g) -> True when the goal is reached; fail(g) -> truthy = drop.
    When every child of a level fails, the search falls back to the best nodes it had pruned (`reserve_levels`
    levels are kept). lookahead = [action sequences]: a child is kept only if at least one of these
    continuations survives look_steps steps (hazards that kill some frames after the decision).
    Returns (rows from the start state to the first node that is done, score) or None.
    The emulator is left in the winning state with g.rows / g.pad consistent.
    """
    t_start = time.time()
    root = g.snap()
    n_root = len(g.rows)
    nodes = [(None, root, ())]                # (score, snap, action history)
    reserve = []                              # pruned nodes of earlier levels, newest last
    winners = []
    beam.last_fail = None
    beam.last_hist = None

    def give_up():
        for lv in reserve:
            for (_, tok, _a) in lv:
                g.free(tok)
        for (_, tok, _h) in nodes:
            if tok is not root:
                g.free(tok)
        g.restore(root)
        g.free(root)
        return None

    for s in range(max_steps):
        if max_seconds is not None and time.time() - t_start > max_seconds:
            if verbose:
                log(f"   {tag}: out of time after {s} steps")
            return give_up()
        nxt = []
        seen = set()
        for (_, tok, hist) in nodes:
            g.restore(tok)
            acts = actions(g)
            for a in acts:
                g.restore(tok)
                dead = False
                fin = False
                for k in range(step):
                    g.step(step_rows(g, a, k))
                    if fail and fail(g):
                        dead = True
                        break
                    if done(g):
                        fin = True
                        break
                if dead:
                    continue
                if fin:
                    winners.append((len(g.rows), score(g), g.snap(), hist + (a,)))
                    continue
                key = dedupe(g) if dedupe else None
                if key is not None:
                    if key in seen:
                        continue
                    seen.add(key)
                nxt.append((score(g), g.snap(), hist + (a,)))
        if not nxt and not winners:
            beam.last_fail = [(sc, hist) for (sc, tok, hist) in nodes]
        for (_, tok, _h) in nodes:
            if tok is not root:
                g.free(tok)
        nodes = []
        if winners:
            for (_, tok, _a) in nxt:
                g.free(tok)
            break
        nxt.sort(key=lambda t: t[0])
        if nxt and lookahead:
            kept, rest = [], []
            for node in nxt:
                if len(kept) >= width:
                    rest.append(node)
                    continue
                alive = False
                for seq in lookahead:
                    g.restore(node[1])
                    okc = True
                    for j in range(look_steps):
                        a = seq[j % len(seq)]
                        if a not in actions(g):
                            a = seq[-1]
                        for k in range(step):
                            g.step(step_rows(g, a, k))
                            if fail(g):
                                okc = False
                                break
                            if done(g):
                                break
                        if not okc or done(g):
                            break
                    if okc:
                        alive = True
                        break
                if alive:
                    kept.append(node)
                else:
                    g.free(node[1])
            if not kept:
                for (_, tok, _a) in rest:
                    g.free(tok)
            nxt = kept + rest if kept else []
        if not nxt:
            while reserve and not reserve[-1]:
                reserve.pop()
            if not reserve:
                return give_up()
            nodes = reserve.pop()
            if verbose:
                log(f"   {tag} step {s}: dead end, falling back to {len(nodes)} pruned nodes (best {nodes[0][0]})")
            continue
        reserve.append(nxt[width:2 * width])
        for (_, tok, _a) in nxt[2 * width:]:
            g.free(tok)
        if len(reserve) > reserve_levels:
            for (_, tok, _a) in reserve.pop(0):
                g.free(tok)
        nodes = nxt[:width]
        if verbose and s % 4 == 0:
            log(f"   {tag} step {s}: best {nxt[0][0]} via {','.join(nxt[0][2][-6:])} ({len(nxt)} children)")
    if not winners:
        return give_up()
    for lv in reserve:
        for (_, tok, _a) in lv:
            g.free(tok)
    winners.sort(key=lambda t: (t[0], t[1]))
    n, sc, tok, beam.last_hist = winners[0]
    g.restore(tok)
    for (_, _, t, _h) in winners:
        g.free(t)
    g.free(root)
    return (list(g.rows[n_root:]), sc)


def pit_ahead(r: Ram, reach=64):
    """True when the player is falling and no floor, water or solid cell lies below him within `reach` px ahead."""
    if not r.air or r.yvel <= 0:
        return False
    x, y = r.x, r.y
    lim = min(reach, max(8, (232 - y) // 2))
    for dx in range(0, lim + 1, 8):
        xx = min(x + dx, 255)
        yy = (y + 16) & 0xF0
        while yy < 224:
            if r.coll(xx, yy + 8):
                return False
            yy += 16
    return True


def local_beam(policy, fail, width=6, step=6, look_steps=4, tag="local", max_seconds=240, shoot=None):
    """A fallback for Repair: beam search over `step`-frame choices on top of the run policy - R (as the policy
    says), J (jump now), NJ (skip a planned jump), P (duck and fire), S (stand and fire) - for the fewest frames
    to the goal. shoot(g, want) adds B to `want` for P and S (default: the fastest legal cadence; the rule v2
    policies pass their own version, which keeps the press plan's headroom)."""
    shoot = shoot or (lambda g, w: fire(g.pad, w))

    def run(g: Game, route: Route, until):
        def rows(g, a, k):
            if a == "P":
                return shoot(g, {"Down"})
            if a == "S":
                return shoot(g, set())
            w = policy(g, route)
            if a == "J" and k < 2:
                w.add("A")
            elif a == "NJ":
                w.discard("A")
            return w

        def acts(g):
            a = ["R"]
            if not g.r.air:
                a += ["J", "P", "S"]
                p = g.r.prog
                if any(p <= P <= p + step + 1 for P in route.jumps):
                    a.append("NJ")
            return a
        res = beam(g, acts, rows, lambda g: (-g.r.prog, g.r.y), until, width=width,
                   max_steps=90, step=step, fail=fail, verbose=False, tag=tag,
                   dedupe=lambda g: (g.r.prog, g.r.y, g.r.x, g.r.jumping, round(g.r.yvel, 1)),
                   lookahead=[("R",), ("J", "R"), ("P",), ("S",)], look_steps=look_steps, max_seconds=max_seconds)
        return None if res is None else res[0]
    return run
