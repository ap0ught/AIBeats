"""Closed-loop frame controller used by the stage 6 and stage 7 solvers.

Ctl plays one frame at a time on a Sim, keeps the rows really sent and the trace, and enforces the input rules
on every button while it plays (one new press per 5 frames, held >= 2, released >= 2, no opposite directions),
so whatever it produces passes check_inputs.py by construction (and is checked again at the end).
"""
from __future__ import annotations

from .s6lib import Fr, Presser, Sim, violations

ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")


class Dead(Exception):
    def __init__(self, ctl, why="death"):
        super().__init__(f"{why} at row {len(ctl.rows)} wx {ctl.f.wx} y {ctl.f['y']} fc {ctl.f['fc']}")
        self.n = len(ctl.rows)
        self.wx = ctl.f.wx
        self.y = ctl.f["y"]
        self.why = why


class Stuck(Exception):
    pass


class Ctl:
    def __init__(self, sim: Sim, history=(), f: Fr | None = None):
        self.sim = sim
        self.history = [tuple(r) for r in history][-12:]
        self.pr = Presser(self.history)
        self.rows: list[tuple] = []
        self.tr: list[Fr] = []
        self.f: Fr = f if f is not None else sim.state()
        self.fire = False            # press B whenever the cap allows
        self.aim: tuple = ()         # extra direction buttons added to every frame (e.g. ("Up",))
        self.blocked: set = set()
        self.lag = 0
        self.stop_on_death = True
        self.notes: list = []        # (row index, text)
        self.fire_gate = None        # optional callable(ctl) -> bool: may a new B press start now?

    # ---------------------------------------------------------------- snapshots
    def snap(self):
        # the rows and the trace are stored with the snapshot: a snapshot may be restored after the lists have
        # been rewritten by trials that branched off EARLIER than it (truncating would then keep trial rows)
        return {"sid": self.sim.msave(), "n": len(self.rows), "pr": self.pr.copy(), "f": self.f,
                "fire": self.fire, "aim": self.aim, "lag": self.lag, "notes": list(self.notes),
                "rows": list(self.rows), "tr": list(self.tr)}

    def restore(self, sn):
        self.sim.mload(sn["sid"])
        self.rows[:] = sn["rows"]
        self.tr[:] = sn["tr"]
        self.notes[:] = sn["notes"]
        self.pr = sn["pr"].copy()
        self.f = sn["f"]
        self.fire, self.aim, self.lag = sn["fire"], sn["aim"], sn["lag"]

    def free(self, sn):
        self.sim.mfree(sn["sid"])

    def note(self, text):
        self.notes.append((len(self.rows), text))

    # ---------------------------------------------------------------- one frame
    def can(self, b):
        return self.pr.can_press(b)

    def frame(self, want=()) -> Fr:
        want = set(want)
        want.update(self.aim)
        if self.fire and "B" not in want and self.pr.can_press("B") and (self.fire_gate is None or self.fire_gate(self)):
            want.add("B")
        blocked = set()
        for b in list(self.pr.held):
            if b not in want and self.pr.must_hold(b):
                want.add(b)                      # a press lasts at least 2 frames
        for b in list(want):
            if b not in self.pr.held and not self.pr.can_press(b):
                want.discard(b)                  # too soon for a new press of this button
                blocked.add(b)
        if "Left" in want and "Right" in want:
            want.discard("Left" if "Right" in self.pr.held else "Right")
        if "Up" in want and "Down" in want:
            want.discard("Up" if "Down" in self.pr.held else "Down")
        row = tuple(b for b in ORDER if b in want)
        self.blocked = blocked
        f = self.sim.run([row])[-1]
        self.pr.feed(row)
        self.rows.append(row)
        self.tr.append(f)
        self.f = f
        if f["lagged"]:
            self.lag += 1
        if self.stop_on_death and f.dead:
            raise Dead(self)
        return f

    def frames(self, want=(), n=1):
        for _ in range(n):
            self.frame(want)
        return self.f

    # ---------------------------------------------------------------- helpers
    @property
    def wx(self):
        return self.f.wx

    @property
    def grounded(self):
        f = self.f
        return (f["jump"] & 15) == 0 and f["fall"] == 0

    def until(self, cond, want=("Right",), limit=600):
        """Hold `want` until cond(ctl) is true (checked after each frame)."""
        n = 0
        while not cond(self):
            self.frame(want)
            n += 1
            if n > limit:
                raise Stuck(f"until: {limit} frames at wx {self.wx} y {self.f['y']}")
        return n

    def run_to(self, wx, want=("Right",), limit=900):
        return self.until(lambda c: c.f.wx >= wx, want, limit)

    def jump(self, want=("Right",), hold=2):
        """Start a jump now (A must be allowed and Bill on the ground)."""
        if not self.can("A"):
            raise Stuck("A not allowed yet")
        self.frame(tuple(want) + ("A",))
        for _ in range(hold - 1):
            self.frame(tuple(want) + ("A",))

    def land(self, want=("Right",), limit=200):
        """Hold `want` until back on the ground."""
        n = 0
        while not self.grounded or n == 0:
            self.frame(want)
            n += 1
            if n > limit:
                raise Stuck("land")
        return n

    def pause(self, n=5):
        """Pause for n frames (n >= 5 under the press cap): Start on the first frame, Start again n frames later.
        Game logic is frozen on exactly n frames; the buttons held on the un-pause frame act normally."""
        assert n >= 5
        if not self.can("Start"):
            raise Stuck("Start not allowed yet")
        held = tuple(b for b in self.pr.held if b in ("Left", "Right", "Up", "Down"))
        self.frame(held + ("Start",))
        self.frame(held + ("Start",))
        for _ in range(n - 2):
            self.frame(held)
        return held                      # the caller's next frame must include Start (un-pause)

    def check(self):
        return violations(self.rows, self.history)
