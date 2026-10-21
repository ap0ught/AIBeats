"""Route runner with death-driven save-state search, shared by the stage 6 and stage 7 solvers.

A route is a list of steps. Each step is a small object with tick(runner) -> buttons wanted this frame, or None when
the step is finished (the next step is then asked on the same frame). The Runner plays the route one frame at a
time through a Ctl (which enforces the input rules), keeps rolling in-memory save states, and when Bill dies it
rewinds and tries "remedies" (a jump, a short stop, ducking, a pause over a hazard's trigger frame ...) in order
of the frames they cost, keeping the cheapest one that gets Bill past the place he died.

Nothing here knows about a particular stage; s6.py / s7.py supply the route, the fire policy and extra remedies.
"""
from __future__ import annotations

import copy
import math
import time

from .s6ctl import Ctl, Dead, Stuck

DIRS = ("Left", "Right", "Up", "Down")


# ----------------------------------------------------------------------------- steps
class Step:
    name = "step"

    def tick(self, r):          # -> iterable of buttons, or None when finished
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.name} {self.__dict__}>"


class Run(Step):
    """Hold `want` until world x >= wx (and, if ground is set, standing on the ground)."""
    name = "run"

    def __init__(self, wx, want=("Right",), ground=False, y=None):
        self.wx, self.want, self.ground, self.y = wx, tuple(want), ground, y

    def tick(self, r):
        f = r.c.f
        if f.wx >= self.wx and (not self.ground or r.c.grounded) and (self.y is None or f["y"] == self.y):
            return None
        if self.y is not None and f.wx >= self.wx + 24 and r.c.grounded and f["y"] != self.y:
            raise Stuck(f"at wx {f.wx} on level y {f['y']}, expected {self.y}")
        return self.want


class Jump(Step):
    """Run (hold `want`) to world x >= wx on the ground, then jump: A for two frames with `air`."""
    name = "jump"

    def __init__(self, wx, want=("Right",), air=None, skip_y=None):
        self.wx, self.want, self.air = wx, tuple(want), tuple(air if air is not None else want)
        self.k = 0
        self.skip_y = skip_y          # already standing on the level this jump is for (a dodge jump got there)

    def tick(self, r):
        if self.k == 0:
            if (self.skip_y is not None and r.c.grounded and r.c.f["y"] == self.skip_y
                    and r.c.f.wx >= self.wx - 56):
                return None
            if r.c.f.wx >= self.wx and r.c.grounded and r.c.can("A"):
                self.k = 1
                return self.air + ("A",)
            return self.want
        if self.k == 1:
            self.k = 2
            return self.air + ("A",)
        if self.k == 2 and r.c.grounded and r.c.f["yvel"] == 0:
            self.k = 0                      # the game did not start the jump (A was eaten): try again
            return self.want
        return None


class JumpSteer(Step):
    """Run to world x >= wx on the ground, jump holding Right, hold Left instead on air frames
    [left_from, left_from + left_n), and finish on landing (y = expected standing Y, else Stuck)."""
    name = "jumpsteer"

    def __init__(self, wx, left_from, left_n, y=None):
        self.wx, self.left_from, self.left_n, self.y = wx, left_from, left_n, y
        self.k = 0
        self.air = 0

    def tick(self, r):
        c = r.c
        if self.k == 0:
            if c.f.wx >= self.wx and c.grounded and c.can("A"):
                self.k = 1
                return ("Right", "A")
            return ("Right",)
        if self.k == 1:
            self.k = 2
            return ("Right", "A")
        self.air += 1
        if self.air > 5 and c.grounded:
            if self.y is not None and c.f["y"] != self.y:
                raise Stuck(f"steered jump landed at y {c.f['y']}, expected {self.y}")
            return None
        if self.left_from <= self.air + 2 < self.left_from + self.left_n:
            return ("Left",)
        return ("Right",)


class Land(Step):
    """Hold `want` until Bill is on the ground again (at least one frame is played)."""
    name = "land"

    def __init__(self, want=("Right",), y=None, max_wx=None, min_wx=None):
        self.want, self.y, self.k = tuple(want), y, 0
        self.max_wx, self.min_wx = max_wx, min_wx

    def tick(self, r):
        self.k += 1
        if self.k > 1 and r.c.grounded:
            if self.y is None or r.c.f["y"] == self.y:
                return None
            self.bad = getattr(self, "bad", 0) + 1
            if self.bad > 2:
                raise Stuck(f"landed at y {r.c.f['y']}, expected {self.y}")
        w = self.want
        if self.max_wx is not None and r.c.f.wx >= self.max_wx:
            w = tuple(b for b in w if b != "Right")
        if self.min_wx is not None and r.c.f.wx <= self.min_wx:
            w = tuple(b for b in w if b != "Left")
        return w


class Hold(Step):
    """Hold `want` for n frames."""
    name = "hold"

    def __init__(self, n, want=()):
        self.n, self.want = n, tuple(want)

    def tick(self, r):
        if self.n <= 0:
            return None
        self.n -= 1
        return self.want


class Drop(Step):
    """Down+A drop through the platform Bill stands on (Down alone, A for two frames), then fall until grounded.
    y = the standing Y expected after the drop (a different level raises Stuck)."""
    name = "drop"

    def __init__(self, after=("Right",), y=None):
        self.k, self.after, self.y, self.y0 = 0, tuple(after), y, None

    def tick(self, r):
        c = r.c
        self.k += 1
        if self.k == 1:
            if not (c.grounded and c.can("A")):
                self.k = 0
                return ()
            self.y0 = c.f["y"]
            return ("Down", "A")
        if self.k == 2:
            return ("Down", "A")
        if self.k == 4 and c.grounded and c.f["y"] == self.y0:
            self.k = 0                      # nothing happened (the press was eaten): press again
            return ()
        if self.k > 4 and c.grounded:
            if self.y is not None and c.f["y"] != self.y:
                raise Stuck(f"drop landed at y {c.f['y']}, expected {self.y}")
            return None
        return self.after


class Until(Step):
    """Hold `want` until cond(runner) is true."""
    name = "until"

    def __init__(self, cond, want=("Right",), label=""):
        self.cond, self.want, self.label = cond, tuple(want), label

    def tick(self, r):
        if self.cond(r):
            return None
        return self.want

    def __repr__(self):
        return f"<until {self.label}>"


class Set(Step):
    """Set attributes on the runner (fire mode, aim ...) and finish at once."""
    name = "set"

    def __init__(self, **kw):
        self.kw = kw

    def tick(self, r):
        for k, v in self.kw.items():
            setattr(r, k, v)
        return None


class Mark(Step):
    """Record a named checkpoint (row count when reached) and finish at once."""
    name = "mark"

    def __init__(self, label, save=None):
        self.label, self.save = label, save

    def tick(self, r):
        r.marks.append((self.label, len(r.c.rows), r.c.f["fc"], r.c.f.wx, r.c.f["y"]))
        if self.save and r.save_states:
            r.c.sim.save(self.save)
            r.saved.append((self.save, len(r.c.rows)))
        return None


class Call(Step):
    """A step implemented by a function fn(runner, state_dict) -> buttons or None."""
    name = "call"

    def __init__(self, fn, label="", **st):
        self.fn, self.label, self.st = fn, label, dict(st)

    def tick(self, r):
        return self.fn(r, self.st)

    def __repr__(self):
        return f"<call {self.label} {self.st}>"


# ----------------------------------------------------------------------------- remedies
class Remedy:
    """An override that starts at absolute row `at` (index into the runner's rows)."""

    def __init__(self, at, kind, n=0, extra=None):
        self.at, self.kind, self.n, self.extra = at, kind, n, extra
        self.left = None

    @property
    def cost(self):
        return {"jump": 1, "wait": self.n, "duck": self.n, "pause": self.n, "left": 2 * self.n,
                "nofire": 0, "aim": 0, "fire": 0, "shift": 0}.get(self.kind, self.n)

    def key(self):
        return (self.at, self.kind, self.n, str(self.extra))

    def __repr__(self):
        return f"{self.kind}{self.n if self.n else ''}@{self.at}" + (f"[{self.extra}]" if self.extra else "")


class Done(Exception):
    pass


class Runner:
    def __init__(self, sim, route, history=(), fire_policy=None, name="run", log=print):
        self.c = Ctl(sim, history)
        self.route = route
        self.pristine = copy.deepcopy(route)
        self.i = 0
        self.fire_policy = fire_policy       # callable(runner, want:set) -> set (may add B and aim buttons)
        self.remedies: list[Remedy] = []
        self.applied: list[Remedy] = []
        self.active: list[Remedy] = []
        self.marks: list = []
        self.saved: list = []
        self.save_states = False
        self.unpause = False
        self.fire_on = True
        self.aim_mode = None                 # stage-specific hint for the fire policy
        self.log = log
        self.name = name
        self.snaps: list = []                # rolling snapshots (row, snap dict)
        self.snap_every = 12
        self.keep_snaps = 40
        self.deaths = 0
        self.trials = 0
        self.frames_simulated = 0
        self.user: dict = {}                 # stage-specific state that must be saved with snapshots
        self.dirty = 0                       # highest route index ever ticked
        self.shifts: dict = {}               # route step index -> new wx (committed "retime this jump" remedies)
        self.committed: list = []
        self._sn_i = 0
        self._seen: dict = {}
        self.max_combo = 4                   # remedies per set in the repair search
        self.greedy = False                  # accept a remedy that gets clearly past the death even if Bill dies later
        self.use_local = False               # fall back to a local beam search when remedies fail or cost a lot
        self.local_over = 6
        self.local_ahead = 70
        self.local_steps = 60
        self.local_kinds = ("R", "J", "S", "D")
        self.local_fixes: list = []
        self.floor_row = 0                   # end row of the last accepted local beam
        self.pass_margin = 30
        self.expand_width = 16

    # ------------------------------------------------------------ snapshots
    def snap(self):
        return {"c": self.c.snap(), "i": self.i, "steps": copy.deepcopy(self.route[self.i:self.i + 2]),
                "active": copy.deepcopy(self.active), "marks": list(self.marks), "unpause": self.unpause,
                "fire_on": self.fire_on, "aim_mode": self.aim_mode, "user": copy.deepcopy(self.user),
                "applied": list(self.applied), "saved": list(self.saved)}

    def restore(self, sn):
        self.c.restore(sn["c"])
        self.i = sn["i"]
        steps = copy.deepcopy(sn["steps"])
        for k, st in enumerate(steps):
            self.route[self.i + k] = st
        for j in range(self.i + len(steps), min(len(self.route), self.dirty + 1)):
            self.route[j] = copy.deepcopy(self.pristine[j])     # steps touched after the snapshot was taken
        for j, wx in self.shifts.items():
            if j >= self.i and getattr(self.route[j], "k", 0) == 0:
                self.route[j].wx = wx
        self.active = copy.deepcopy(sn["active"])
        self.marks[:] = sn["marks"]
        self.applied[:] = sn["applied"]
        self.saved[:] = sn["saved"]
        self.unpause = sn["unpause"]
        self.fire_on, self.aim_mode = sn["fire_on"], sn["aim_mode"]
        self.user = copy.deepcopy(sn["user"])

    def free(self, sn):
        self.c.free(sn["c"])

    def _roll(self):
        n = len(self.c.rows)
        if not self.snaps or n - self.snaps[-1][0] >= self.snap_every:
            self.snaps.append((n, self.snap()))
            while len(self.snaps) > self.keep_snaps:
                _, old = self.snaps.pop(0)
                self.free(old)

    def drop_snaps_after(self, n):
        while self.snaps and self.snaps[-1][0] > n:
            _, old = self.snaps.pop()
            self.free(old)

    # ------------------------------------------------------------ one frame
    def progress(self):
        return (self.i, self.c.f.wx)

    def tick(self):
        c = self.c
        n = len(c.rows)
        # 1. remedies starting now
        for rm in self.remedies:
            if rm.at == n and rm.left is None:
                rm2 = copy.deepcopy(rm)
                rm2.left = {"jump": 2}.get(rm.kind, rm.n)
                rm2.k = 0
                self.active.append(rm2)
                self.applied.append(rm)
        # 2. a pause in progress: extra frames on which the game does nothing (the route is not asked)
        pz = next((x for x in self.active if x.kind == "pause"), None)
        if pz is not None:
            held = set(b for b in c.pr.held if b in DIRS)
            if pz.k == 0 and not c.can("Start"):
                self.active.remove(pz)                          # cannot pause here: the remedy is void
            else:
                row = set(held)
                if pz.k < 2:
                    row.add("Start")
                c.frame(row)
                self.frames_simulated += 1
                pz.k += 1
                pz.left -= 1
                if pz.k == 2 and not c.f["pause"]:
                    self.active.remove(pz)                      # the game did not see the press
                elif pz.left <= 0:
                    self.active.remove(pz)
                    self.unpause = True
                return
        # 3. what does the route want?
        while True:
            if self.i >= len(self.route):
                raise Done()
            if self.i > self.dirty:
                self.dirty = self.i
            w = self.route[self.i].tick(self)
            if w is None:
                self.i += 1
                continue
            break
        want = set(w)
        nofire = False
        aim_over = False
        still = []
        for rm in self.active:
            if rm.kind == "jump":
                if rm.left == 2 and not (c.grounded and c.can("A")):
                    continue                                    # cannot jump here: the remedy is void
                want.add("A")
            elif rm.kind == "wait":
                want.discard("Left"); want.discard("Right"); want.discard("A")
            elif rm.kind == "duck":
                want.discard("Left"); want.discard("Right"); want.discard("Up"); want.discard("A")
                want.add("Down")
            elif rm.kind == "left":
                want.discard("Right"); want.add("Left")
            elif rm.kind == "nofire":
                nofire = True
            elif rm.kind == "aim":
                want.discard("Up"); want.discard("Down")
                want.update(rm.extra or ())
                aim_over = True
            rm.left -= 1
            if rm.left > 0:
                still.append(rm)
        self.active = still
        # 4. fire policy
        if self.fire_policy and self.fire_on and not nofire:
            want = self.fire_policy(self, want, aim_over)
        if self.unpause:
            want.add("Start")
        c.frame(want)
        self.frames_simulated += 1
        if self.unpause and not c.f["pause"]:
            self.unpause = False
        g = getattr(self, "guard_fn", None)
        if g is not None and not g(self):
            raise Dead(c, "guard")

    # ------------------------------------------------------------ plain run (no search)
    def play(self, max_rows=20000, until_progress=None, until_row=None):
        """Play until Done / death / a limit. Returns "done" | "dead" | "limit" | "progress" | "stuck"."""
        try:
            stall = 0
            last = None
            while len(self.c.rows) < max_rows:
                if until_progress is not None and self.progress() >= until_progress:
                    return "progress"
                if until_row is not None and len(self.c.rows) >= until_row:
                    return "limit"
                self.tick()
                key = (self.i, self.c.f.wx, self.c.f["y"])
                stall = stall + 1 if key == last else 0
                last = key
                if stall > 400:
                    return "stuck"
            return "limit"
        except Done:
            return "done"
        except Dead:
            return "dead"
        except Stuck:
            return "stuck"

    # ------------------------------------------------------------ death-driven search
    def candidates(self, D, s_lo, killer):
        """Remedy candidates for a death at row D (rows s_lo..D-1 can be changed), cheapest first.
        Stage solvers may replace this (self.candidates_fn)."""
        out = []
        # retime the route's own most recent jump(s) (free)
        for j in range(self.i, max(-1, self.i - 4), -1):
            st = self.route[j] if j < len(self.route) else None
            if isinstance(st, Jump) and j >= self._sn_i and st.wx > 0:
                base = self.shifts.get(j, self.pristine[j].wx)
                for d in (-2, 2, -4, 4, -6, 6, -8, 8, -11, 11, -14, 14, -18, 18, -22, 22, -27, 27):
                    out.append([Remedy(j, "shift", base + d)])
                break
        for back in (4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56):
            s = D - back
            if s > s_lo:
                out.append([Remedy(s, "jump")])
        # duck under a shot: the prone box is 24 px wide, so the duck has to last while the shot crosses it
        for back, n in ((3, 6), (4, 8), (5, 10), (6, 12), (8, 12), (8, 16), (10, 14), (12, 18)):
            s = D - back
            if s > s_lo:
                out.append([Remedy(s, "duck", n)])
        for n in (2, 3, 4, 6, 8, 11, 14, 18, 23, 28, 34, 42, 50, 64):
            for back in (3, 6, 10, 16, 24, 36, 50, 70):
                s = D - back - (n if back > 10 else 0)
                if s > s_lo:
                    out.append([Remedy(s, "wait", n)])
        return out

    def solve(self, max_rows=20000, horizon=70, back=90, max_deaths=200, log_every=1):
        """Play the route to the end, repairing every death. Returns "done" or a failure word."""
        t0 = time.time()
        fails_here = 0
        last_D = -1
        while True:
            try:
                while True:
                    self._roll()
                    self.tick()
                    if len(self.c.rows) >= max_rows:
                        return "limit"
            except Done:
                return "done"
            except Stuck as ex:
                self.log(f"[{self.name}] stuck: {ex}")
                if not self.use_local or not self.snaps:
                    return "stuck"
                D = len(self.c.rows)
                wxD = self.c.f.wx
                self._stucks = getattr(self, "_stucks", 0) + 1
                if self._stucks > 12:
                    return "stuck"
                older = [(n, sn) for n, sn in self.snaps if n <= D - 80]
                nL, snL = older[-1] if older else self.snaps[0]
                self.restore(snL)
                if self.aim_mode == "off":
                    self.aim_mode = None
                rows = local_beam(self, max(wxD, self.c.f.wx) + self.local_ahead, max_steps=self.local_steps + 20,
                                  kinds=self.local_kinds)
                if rows is None:
                    self.log(f"[{self.name}] local beam after the stuck step found nothing")
                    return "stuck"
                self.log(f"[{self.name}] local beam after the stuck step: {len(rows)} rows from row {nL} to wx "
                         f"{self.c.f.wx} y {self.c.f['y']}")
                self.drop_snaps_after(nL)
                self.remedies = [rm for rm in self.remedies if rm.at < nL]
                self.active = []
                self.unpause = False
                self.skip_passed_steps()
                self.local_fixes.append((D, nL, len(rows), None))
                self.floor_row = len(self.c.rows)
                self.snaps.append((len(self.c.rows), self.snap()))
                continue
            except Dead as ex:
                D = ex.n
                self.deaths += 1
                if self.deaths > max_deaths:
                    return "too many deaths"
                killer = self.killer()
                fails_here = fails_here + 1 if abs(D - last_D) < 30 else 0
                last_D = D
                key = self.progress()
                self._seen[key] = self._seen.get(key, 0) + 1
                if self._seen[key] > 4:
                    self.log(f"[{self.name}] giving up: died {self._seen[key]} times at progress {key}")
                    return "dead"
                bk = back * (1 + fails_here)
                ok = self.repair(D, bk, horizon, killer)
                if not ok:
                    self.log(f"[{self.name}] UNSOLVED death at row {D} wx {ex.wx} y {ex.y} killer {killer} "
                             f"(t+{time.time() - t0:.0f}s)")
                    return "dead"

    def killer(self):
        """The enemy closest to Bill on the last frame (a guess at what killed him)."""
        f = self.c.f
        best = None
        for e in f.enemies():
            d = abs(e["x"] - f["x"]) + abs(e["y"] - f["y"])
            if best is None or d < best[0]:
                best = (d, e["type"], e["slot"], e["x"], e["y"], e["attr"])
        return best

    def trial(self, sn, rems, R):
        """From snapshot sn play with the extra remedies until row R. Returns (alive at R, progress, result)."""
        saved = self.remedies
        saved_shifts = dict(self.shifts)
        for rm in rems:
            if rm.kind == "shift":
                self.shifts[rm.at] = rm.n
        self.restore(sn)
        self.remedies = saved + [rm for rm in rems if rm.kind != "shift"]
        self.trials += 1
        self._in_trial = True                 # a memoised Proc (stage 7) ends the trial instead of searching
        try:
            res = self.play(until_row=R)
        finally:
            self._in_trial = False
            self.remedies = saved
            self.shifts = saved_shifts
        return (res in ("limit", "done")), self.progress(), res

    def repair(self, D, back, horizon, killer, depth=0):
        """Best-first search over sets of remedies for the death at row D. A set that dies later than the death
        it was made for is expanded with remedies for that later death, so combinations (two pauses, a pause and
        a short stop ...) are found; sets are tried in order of the frames they cost."""
        import heapq
        f = self.c.f
        prog_D = self.progress()
        cands_sn = [(n, sn) for n, sn in self.snaps if n <= D - 4]
        if not cands_sn:
            return False
        bf = getattr(self, "back_fn", None)
        if bf:
            back = bf(self, killer, D, back)
        # Remedy trials replay the ROUTE from a snapshot, so they must not start before the end of the last
        # accepted local beam (the rows of a beam are not something the route would play again).
        trial_sn = [(n, sn) for n, sn in cands_sn if n >= self.floor_row]
        older = [(n, sn) for n, sn in trial_sn if n <= D - back]
        if trial_sn:
            n0, sn0 = older[-1] if older else trial_sn[0]
        else:
            n0, sn0 = cands_sn[-1]
        self._sn_i = sn0["i"]
        fn = getattr(self, "candidates_fn", None) or (lambda r, D_, lo, k: r.candidates(D_, lo, k))
        hz = getattr(self, "horizon_fn", None)
        if hz:
            horizon = hz(self, killer, horizon)
        R = D + horizon
        heap = []
        order = 0
        for rems in (fn(self, D, n0, killer) if trial_sn else []):
            heapq.heappush(heap, (sum(r.cost for r in rems), order, D, rems))
            order += 1
        best = None
        tried = 0
        partial = []
        seen = set()
        budget = getattr(self, "repair_budget", 140)
        while heap and tried < budget:
            cost, _, d_for, rems = heapq.heappop(heap)
            if best is not None:
                # a remedy after which Bill still dies a little later is only kept if nothing up to 8 frames
                # dearer keeps him alive to the horizon
                slack = 8 if best[3][1] == 1 else 0
                if cost > best[0] + slack or (cost == best[0] and cost > 0 and best[3][1] == 0):
                    break
            key = tuple(sorted(r.key() for r in rems))
            if key in seen:
                continue
            seen.add(key)
            ok, prog, res = self.trial(sn0, rems, R + min(cost, 60))
            tried += 1
            n = len(self.c.rows)
            # passed: alive at the horizon, or (greedy mode) died later at a place clearly further along
            later = (self.greedy and res == "dead" and n >= D + 14 + cost
                     and (prog[0] > prog_D[0] or prog[1] >= prog_D[1] + self.pass_margin))
            if (ok and prog >= prog_D) or later:
                eff = cost
                if getattr(self, "progress_check", False):
                    # frames really lost against 1 px per row since the death row, beyond the nominal cost
                    lost = (prog_D[1] + (n - D)) - prog[1] - cost
                    if lost > 6:
                        eff = cost + lost
                k = (eff, 1 if later else 0, tuple(-x for x in prog))
                if best is None:
                    best = (eff, prog, rems, k)
                elif best[3][1] == 1 and not later and eff <= best[0] + 8:
                    best = (eff, prog, rems, k)             # alive beats "dies later" (within the slack)
                elif best[3][1] == (1 if later else 0) and k < best[3]:
                    best = (eff, prog, rems, k)
                elif eff + 8 < best[0]:
                    best = (eff, prog, rems, k)
            elif res == "dead" and n > d_for + 8:
                partial.append((n, rems))
                if len(rems) < self.max_combo:
                    k2 = self.killer()
                    for extra in fn(self, n, n0, k2)[:self.expand_width]:
                        if any(e.kind == "shift" for e in extra):
                            continue
                        heapq.heappush(heap, (cost + sum(r.cost for r in extra), order, n, rems + extra))
                        order += 1
        if self.use_local and (best is None or best[0] > self.local_over):
            wxD = prog_D[1]
            got = None
            tried_roots = set()
            for bk in (70, 130, 230):
                nL, snL = min(cands_sn, key=lambda t: abs(t[0] - (D - bk)))     # the snapshot nearest to D - bk
                if nL in tried_roots:
                    continue
                tried_roots.add(nL)
                self.restore(snL)
                if self.aim_mode == "off":
                    self.aim_mode = None        # the beam may shoot (a scripted no-fire stretch does not bind it)
                rows_before = len(self.c.rows)
                t_b = time.time()
                rows = local_beam(self, wxD + self.local_ahead, max_steps=self.local_steps, kinds=self.local_kinds)
                if rows is not None:
                    lost = len(rows) - (self.c.f.wx - snL["c"]["f"].wx)
                    if best is None or lost < best[0] + (self.c.f.wx - wxD - self.local_ahead) * 0:
                        got = (nL, snL, rows, lost)
                    self.log(f"[{self.name}] death at row {D} wx {f.wx} y {f['y']} killer {killer}: local beam from "
                             f"row {nL}: {len(rows)} rows to wx {self.c.f.wx} y {self.c.f['y']}, {lost} frames "
                             f"lost, {time.time() - t_b:.0f} s (best remedy cost {best[0] if best else None})")
                    break
            if got is not None and (best is None or got[3] < best[0]):
                nL, snL, rows, lost = got
                # the beam left the emulator at its end: keep it, drop newer snapshots, skip finished route steps
                self.drop_snaps_after(nL)
                self.remedies = [rm for rm in self.remedies if rm.at < nL]
                self.active = []
                self.unpause = False
                self.skip_passed_steps()
                self.local_fixes.append((D, nL, len(rows), lost))
                self.floor_row = len(self.c.rows)
                self.snaps.append((len(self.c.rows), self.snap()))
                return True
        if best is None:
            self.log(f"[{self.name}] death at row {D} wx {f.wx} y {f['y']} fc {f['fc']} killer {killer}: "
                     f"none of {tried} remedy sets passed (longest {sorted((n, str(r)) for n, r in partial)[-2:]})")
            if partial and depth < 2:
                n, rems = max(partial, key=lambda t: t[0])
                self.commit(sn0, n0, rems)
                return True
            return False
        cost, prog, rems, k = best
        self.log(f"[{self.name}] death at row {D} wx {f.wx} y {f['y']} fc {f['fc']} killer {killer}: "
                 f"{rems} (cost {cost}, {tried} trials{', dies later' if k[1] else ''})")
        self.commit(sn0, n0, rems)
        return True

    def skip_passed_steps(self):
        """After a local beam: route steps whose place is already behind Bill are skipped (marks in between are
        still recorded)."""
        wx = self.c.f.wx
        while self.i < len(self.route):
            j = self.i
            while j < len(self.route) and getattr(self.route[j], "end_wx", None) is None \
                    and isinstance(self.route[j], (Mark, Set)):
                j += 1
            if j >= len(self.route):
                break
            e = getattr(self.route[j], "end_wx", None)
            if e is None or e > wx:
                break
            for k in range(self.i, j):
                self.route[k].tick(self)           # marks / settings on the way
            self.i = j + 1
        # a step interrupted in the middle starts afresh
        if self.i < len(self.route):
            self.route[self.i] = copy.deepcopy(self.pristine[self.i])
            for j, sw in self.shifts.items():
                if j == self.i:
                    self.route[j].wx = sw
        if self.i > self.dirty:
            self.dirty = self.i

    def commit(self, sn0, n0, rems):
        for rm in rems:
            if rm.kind == "shift":
                self.shifts[rm.at] = rm.n
        self.restore(sn0)
        self.drop_snaps_after(n0)
        self.remedies = self.remedies + [rm for rm in rems if rm.kind != "shift"]
        self.committed.append((n0, rems))

    def target_after(self, prog, horizon):
        fn = getattr(self, "target_fn", None)
        if fn:
            return fn(self, prog, horizon)
        return (prog[0], prog[1] + horizon)


# ----------------------------------------------------------------------------- generic spread auto-aim
SPREAD_SPEED = 3.48
PELLET_DEG = 11.25


def aim_options(grounded, moving_right=True):
    """(buttons to add, angle in degrees (0 = right, 90 = up), muzzle dx, dy)."""
    if grounded:
        return [((), 0.0, 16, -5), (("Up",), 45.0, 13, -16), (("Down",), -45.0, 13, 6)]
    return [((), 0.0, 16, 0), (("Up",), 45.0, 15, -15), (("Down",), -45.0, 15, 15)]


def predicted_hits(px, py, ang, mdx, mdy, targets, scroll, tmax=70):
    """Rough count of spread pellets that will pass through a target box. targets: (x, y, hw, hh, vx, vy, hp)."""
    hits = 0
    for (tx, ty, hw, hh, vx, vy, hp) in targets:
        got = 0
        for k in (-2, -1, 0, 1, 2):
            a = math.radians(ang + k * PELLET_DEG)
            bvx, bvy = SPREAD_SPEED * math.cos(a) - scroll, -SPREAD_SPEED * math.sin(a)
            bx, by = px + mdx, py + mdy
            ex, ey = tx, ty
            for t in range(tmax):
                if abs(bx - ex) <= hw and abs(by - ey) <= hh:
                    got += 1
                    break
                bx += bvx; by += bvy
                ex += vx; ey += vy
                if bx > 251 or bx < 5 or by < 5 or by > 232:
                    break
        hits += min(got, hp)
    return hits


# ----------------------------------------------------------------------------- beam search (boss fights)
class Proc(Step):
    """A step that plays many frames by itself: fn(runner) is called once and must leave the emulator, the rows
    and the trace consistent (use runner.c.frame). It handles its own deaths (raise Stuck if it cannot)."""
    name = "proc"

    def __init__(self, fn, label=""):
        self.fn, self.label = fn, label

    def tick(self, r):
        self.fn(r)
        return None

    def __repr__(self):
        return f"<proc {self.label}>"


class Member:
    __slots__ = ("sid", "rows", "pr", "f", "score", "done", "key", "prev")

    def __init__(self, sid, rows, pr, f, score=0.0, done=False, key=None, prev=None):
        self.sid, self.rows, self.pr, self.f, self.score, self.done, self.key, self.prev = \
            sid, rows, pr, f, score, done, key, prev


def beam_search(r, actions, score_fn, done_fn, key_fn=None, step=5, width=8, max_steps=90, log=None, label="beam",
                keep_back=17, max_recover=5):
    """Beam search from the runner's current state. actions(member) -> list of (name, fn) where fn(k, ctl) gives
    the buttons wanted on frame k of the step (Ctl enforces the press rules; B etc. are the action's business).
    score_fn(frame, trace of the step, parent member) -> number (bigger is better); done_fn(frame) -> True ends
    the search. Leaves the emulator at the end of the best line with r.c.rows / r.c.tr extended.

    Wipe-out recovery (integrator's chain1 fix, 2026-10-12, ported to the live file): a wipe-out (every child of the beam dies) no longer ends the search. The beams of the
    last `keep_back` depths keep their save states; on a wipe-out the search goes back 8, then `keep_back` depths and
    continues from that beam with the width doubled (at most 64), up to `max_recover` times."""
    c = r.c
    n0 = len(c.rows)
    sod = c.stop_on_death
    c.stop_on_death = False
    root = Member(c.sim.msave(), [], c.pr.copy(), c.f, 0.0)
    root_sid = root.sid
    beam = [root]
    best_done = None
    hist = []                       # beams of earlier depths, oldest first (their states are still held)
    w = width
    recoveries = 0
    depth = 0
    steps_done = 0

    def free_beam(bm):
        for m in bm:
            if m.sid != root_sid:
                c.sim.mfree(m.sid)

    try:
        while depth < max_steps and steps_done < 3 * max_steps:
            steps_done += 1
            children = []
            seen = set()
            died = []
            for m in beam:
                for name, fn in actions(m):
                    c.sim.mload(m.sid)
                    c.pr = m.pr.copy()
                    c.f = m.f
                    del c.rows[n0:]
                    del c.tr[n0:]
                    dead = done = False
                    for k in range(step):
                        f = c.frame(fn(k, c))
                        r.frames_simulated += 1
                        if f.dead:
                            dead = True
                            break
                        if done_fn(f):
                            done = True
                            break
                    if dead:
                        if len(died) < 400:
                            died.append((name, k, c.f))
                        continue
                    key = key_fn(c.f) if key_fn else None
                    if key is not None and not done:
                        if key in seen:
                            continue
                        seen.add(key)
                    sc = score_fn(c.f, c.tr[n0:], m)
                    children.append(Member(c.sim.msave(), m.rows + list(c.rows[n0:]), c.pr.copy(), c.f, sc, done, key))
            if not children:
                if log:
                    try:
                        ex = []
                        for name, k, f in died[:6]:
                            near = sorted(f.enemies(), key=lambda e: abs(e["x"] - f["x"]) + abs(e["y"] - f["y"]))[:2]
                            ex.append(f"{name}@{k}: Bill ({f['x']},{f['y']}) jump {f['jump']} | " + "; ".join(
                                f"type ${e['type']:02x} ({e['x']},{e['y']}) r{e['routine']} hp{e['hp']}" for e in near))
                        log(f"[{label}] WIPE-OUT at depth {depth} (width {w}, {len(beam)} lines, {len(died)} deaths): "
                            + " || ".join(ex))
                    except Exception as e2:  # noqa: BLE001
                        log(f"[{label}] WIPE-OUT at depth {depth} (diagnostic failed: {e2})")
                if recoveries >= max_recover or not hist:
                    raise Stuck(f"{label}: every line died at depth {depth}")
                recoveries += 1
                back = min(len(hist), 8 if recoveries == 1 else keep_back)     # a doomed jump is 12 steps long
                free_beam(beam)
                for _ in range(back - 1):
                    free_beam(hist.pop())
                beam = hist.pop()
                depth -= back
                w = min(max(w * 2, width * 2), 64)
                if log:
                    log(f"[{label}] recovery {recoveries}: back {back} depths to depth {depth}, width now {w}")
                continue
            dones = [m for m in children if m.done]
            if dones:
                best_done = min(dones, key=lambda m: (len(m.rows), -m.score))
                for m in children:
                    if m is not best_done:
                        c.sim.mfree(m.sid)
                free_beam(beam)
                break
            children.sort(key=lambda m: -m.score)
            for m in children[w:]:
                c.sim.mfree(m.sid)
            hist.append(beam)
            while len(hist) > keep_back:
                free_beam(hist.pop(0))
            beam = children[:w]
            if log and depth % 6 == 0:
                log(f"[{label}] depth {depth} rows {len(beam[0].rows)} best {beam[0].score:.1f} "
                    f"worst kept {beam[-1].score:.1f} children {len(children)}")
            depth += 1
        if best_done is None:
            best_done = beam[0]
            for m in beam[1:]:
                c.sim.mfree(m.sid)
    finally:
        c.stop_on_death = sod
        for bm in hist:
            free_beam(bm)
    # replay the chosen line from the root so rows / trace / presser are the real ones
    best = best_done
    c.sim.mload(root_sid)
    c.pr = root.pr.copy()
    c.f = root.f
    del c.rows[n0:]
    del c.tr[n0:]
    for row in best.rows:
        c.frame(row)
        r.frames_simulated += 1
    c.sim.mfree(root_sid)
    if best.sid != root_sid:
        c.sim.mfree(best.sid)
    return best


# ----------------------------------------------------------------------------- generic Spread fire policy
def enemy_boxes(r, f, types):
    """(x, y, half width, half height, vx, vy, hp) for every live enemy whose type is in `types` (a dict
    type -> (hw, hh) or a callable(enemy) -> (hw, hh) | None)."""
    prev = r.c.tr[-2] if len(r.c.tr) >= 2 else None
    out = []
    two = callable(types) and getattr(types, "wants_runner", False)
    for e in f.enemies():
        box = (types(e, r) if two else types(e)) if callable(types) else types.get(e["type"])
        if box is None:
            continue
        vx = vy = 0.0
        s = e["slot"]
        if prev is not None and prev.get(f"er{s}", 0) and prev[f"et{s}"] == e["type"]:
            vx = e["x"] - prev[f"ex{s}"]
            vy = e["y"] - prev[f"ey{s}"]
            if abs(vx) > 8 or abs(vy) > 8:
                vx = vy = 0.0
        dy = box[2] if len(box) > 2 else 0
        out.append((e["x"], e["y"] + dy, box[0], box[1], vx, vy, e["hp"] if 0 < e["hp"] < 0xF0 else 1))
    return out


def make_fire_policy(target_types, avoid_types=None, min_hits=1):
    """Spread auto-aim: a new B press only when some pellet is predicted to hit a target, with the aim (forward,
    up-forward, down-forward) that hits most; never when a pellet is predicted to hit something in avoid_types.
    r.aim_mode == "always" fires forward at every opportunity; "off" never fires."""

    def policy(r, want, aim_over):
        c = r.c
        f = c.f
        if "B" in c.pr.held or not c.can("B") or r.aim_mode == "off":
            return want
        rng_px = getattr(r, "fire_range", 200)
        tg = [t for t in enemy_boxes(r, f, target_types) if -24 <= t[0] - f["x"] <= rng_px]
        av = enemy_boxes(r, f, avoid_types) if avoid_types else []
        mode = r.aim_mode
        if not tg and mode != "always":
            return want
        grounded = c.grounded and "A" not in want
        left = "Left" in want
        moving = ("Right" in want) or left
        scroll = float(f["fscroll"]) if ("Right" in want and f["x"] >= 0x80 and f["stop"] != 0xFF) else 0.0
        best = None
        for btn, ang, mdx, mdy in aim_options(grounded):
            if left:
                continue
            if aim_over and not set(btn) <= want:
                continue
            if btn and not moving and grounded:
                continue        # Up / Down alone on the ground = straight up / prone: the route's business
            ok = True
            for b in btn:
                if b not in c.pr.held and not c.can(b):
                    ok = False
                if b == "Up" and "Down" in c.pr.held:
                    ok = False
                if b == "Down" and "Up" in c.pr.held:
                    ok = False
            if not ok:
                continue
            if (("Up" in want) or ("Down" in want)) and set(btn) != (want & {"Up", "Down"}):
                continue        # the route already holds a vertical direction
            if av and predicted_hits(f["x"], f["y"], ang, mdx, mdy, av, scroll) > 0:
                continue
            h = predicted_hits(f["x"], f["y"], ang, mdx, mdy, tg, scroll)
            key = (h, -len(btn))
            if best is None or key > best[0]:
                best = (key, btn)
        if best is None:
            return want
        if best[0][0] < min_hits and mode != "always":
            return want
        want = set(want)
        want.add("B")
        want.update(best[1])
        return want

    return policy


# ----------------------------------------------------------------------------- local beam search (obstacle clusters)
def _local_act(kind):
    def fn(k, c, r):
        w = set()
        if kind in ("R", "J", "U"):
            w.add("Right")
        if kind == "J" and k < 2:
            w.add("A")
        if kind == "JS" and k < 2:
            w.add("A")
        if kind == "D":
            w.add("Down")
        if kind == "L":
            w.add("Left")
        if r.fire_policy and r.fire_on and kind != "D":
            w = r.fire_policy(r, w, False)
        elif kind == "D" and c.can("B") and "B" not in c.pr.held:
            w.add("B")
        return w
    return fn


LOCAL_ACTIONS = {k: _local_act(k) for k in ("R", "J", "S", "D", "JS", "L")}


def local_beam(r, target_wx, max_steps=60, step=6, per_bucket=2, width=14, extra_fail=None, log=None,
               kinds=("R", "J", "S", "D")):
    """Beam search over 6-frame choices - R run right, J run and jump, S stand, D duck (all with the fire
    policy) - from the runner's current state until Bill stands at world x >= target_wx. Lines are kept per
    8-px bucket of world x, so a line that waits is not thrown away for being behind. The route is not ticked.
    Returns the rows played (the emulator, rows and trace are left at the end of the best line) or None."""
    c = r.c
    n0 = len(c.rows)
    sod = c.stop_on_death
    c.stop_on_death = False
    root_sid = c.sim.msave()
    root = Member(root_sid, [], c.pr.copy(), c.f, 0.0)
    beam = [root]
    best = None
    g = getattr(r, "guard_fn", None)
    try:
        for depth in range(max_steps):
            children = []
            seen = set()
            for m in beam:
                grounded = (m.f["jump"] & 15) == 0 and m.f["fall"] == 0
                for kind in kinds:
                    if kind in ("J", "D", "JS") and not grounded:
                        continue
                    if kind == "S" and not grounded:
                        continue
                    fn = LOCAL_ACTIONS[kind]
                    c.sim.mload(m.sid)
                    c.pr = m.pr.copy()
                    c.f = m.f
                    del c.rows[n0:]
                    del c.tr[n0:]
                    bad = False
                    for k in range(step):
                        f = c.frame(fn(k, c, r))
                        r.frames_simulated += 1
                        if f.dead or (g is not None and not g(r)) or (extra_fail and extra_fail(r)):
                            bad = True
                            break
                    if bad:
                        continue
                    f = c.f
                    gr = (f["jump"] & 15) == 0 and f["fall"] == 0
                    key = (f.wx, f["y"], f["jump"], f["fall"], f["yvel"], f["rng"] & 3)
                    if key in seen:
                        continue
                    seen.add(key)
                    done = f.wx >= target_wx and gr
                    children.append(Member(c.sim.msave(), m.rows + list(c.rows[n0:]), c.pr.copy(), f,
                                           float(f.wx) + (0.5 if gr else 0.0), done, key))
            for m in beam:
                if m.sid != root_sid:
                    c.sim.mfree(m.sid)
            if not children:
                break
            dones = [m for m in children if m.done]
            if dones:
                best = max(dones, key=lambda m: m.score)
                for m in children:
                    if m is not best:
                        c.sim.mfree(m.sid)
                break
            children.sort(key=lambda m: -m.score)
            kept, per = [], {}
            for m in children:
                b = int(m.f.wx) // 8
                if per.get(b, 0) < per_bucket and len(kept) < width:
                    per[b] = per.get(b, 0) + 1
                    kept.append(m)
                else:
                    c.sim.mfree(m.sid)
            beam = kept
        else:
            for m in beam:
                if m.sid != root_sid:
                    c.sim.mfree(m.sid)
    finally:
        c.stop_on_death = sod
    c.sim.mload(root_sid)
    c.pr = root.pr.copy()
    c.f = root.f
    del c.rows[n0:]
    del c.tr[n0:]
    if best is None:
        c.sim.mfree(root_sid)
        return None
    for row in best.rows:
        c.frame(row)
        r.frames_simulated += 1
    c.sim.mfree(root_sid)
    c.sim.mfree(best.sid)
    return best.rows
