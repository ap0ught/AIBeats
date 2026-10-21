"""One-off patch (rule v2): press budget in contra/stages/s3s8_lib.py. utf-8, temp file then rename.
The file before the patch is contra/stages/s3s8_lib.py.backup_v2."""
import os
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s3s8_lib.py"
s = p.read_text(encoding="utf-8")


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


rep('''    Pad        per-button press history: tells whether a new press of a button is legal on the next frame under the
               project's input rules (new press of the same button at most once every 5 frames, held >= 2, released
               >= 2) and builds legal rows. The history is carried across segments (Pad.from_rows).
''', '''    Pad        per-button press history: tells whether a new press of a button is legal on the next frame under the
               project's input rules (new press of the same button at most once every 5 frames, held >= 2, released
               >= 2) and builds legal rows. The history is carried across segments (Pad.from_rows).
               Rule v2 (2026-10-12): the Pad is also the PRESS BUDGET. It keeps the start rows of every button's
               presses of the last 1,800 rows and refuses, as a hard constraint, a press that would put more than
               109 starts of that button into any 600 rows or more than 246 into any 1,800 (WINDOWS; a parameter).
               A refused press is simply "cannot be pressed now": can_press() is False, fix() drops it,
               wait_press() says when it fits. On top of that a soft plan (`reserve`) keeps presses back for a
               fight that is still ahead.
''')
rep('''PERIOD, HOLD, RELEASE = 5, 2, 2
''', '''PERIOD, HOLD, RELEASE = 5, 2, 2
WINDOWS = ((600, 109), (1800, 246))          # rule v2: (rows, most new presses of one button in any such span)
NEVER = 10 ** 6


def parse_windows(spec: str) -> tuple:
    """'600:109,1800:246' -> ((600, 109), (1800, 246)); '' or 'none' -> () (no sustained limits)."""
    if not spec or spec.lower() == "none":
        return ()
    return tuple((int(a), int(c)) for a, c in (x.split(":") for x in spec.split(",") if x))


def set_windows(windows) -> tuple:
    """Change the default sustained limits of every Pad made from now on (the solvers' --windows option)."""
    global WINDOWS
    WINDOWS = tuple((int(w), int(n)) for w, n in windows)
    return WINDOWS


if os.environ.get("CONTRA_WINDOWS") is not None:
    set_windows(parse_windows(os.environ["CONTRA_WINDOWS"]))
''')
rep('''    def __init__(self):
        self.t = 0
        self.down = {b: False for b in BUTTONS}
        self.start = {b: -10 ** 6 for b in BUTTONS}      # row index of the last press start
        self.up = {b: -10 ** 6 for b in BUTTONS}         # row index of the first released row after the last press

    def copy(self) -> "Pad":
        p = Pad()
        p.t = self.t
        p.down = dict(self.down)
        p.start = dict(self.start)
        p.up = dict(self.up)
        return p

    @classmethod
    def from_rows(cls, rows) -> "Pad":
        p = cls()
        for r in rows:
            p.push(r)
        return p

    # -- queries about the NEXT row (index self.t)
    def can_press(self, b: str) -> bool:
        """May button b be down on the next row? (continuing a hold is always fine)"""
        if self.down[b]:
            return True
        return self.t - self.start[b] >= PERIOD and self.t - self.up[b] >= RELEASE
''', '''    def __init__(self, windows=None):
        self.t = 0
        self.down = {b: False for b in BUTTONS}
        self.start = {b: -10 ** 6 for b in BUTTONS}      # row index of the last press start
        self.up = {b: -10 ** 6 for b in BUTTONS}         # row index of the first released row after the last press
        # rule v2: sustained limits. hist[b] = start rows of b's presses, oldest first, the last `keep` rows only
        self.windows = WINDOWS if windows is None else tuple((int(w), int(n)) for w, n in windows)
        self.keep = max((w for w, _ in self.windows), default=0)
        self.hist = {b: [] for b in BUTTONS}
        # soft plan: ((t0, t1, n, button), ...) = "n presses of button will be wanted between rows t0 and t1";
        # a press BEFORE t0 is refused when it would leave less than that inside a window that reaches the fight
        self.reserve = ()

    def copy(self) -> "Pad":
        p = Pad.__new__(Pad)
        p.t = self.t
        p.down = dict(self.down)
        p.start = dict(self.start)
        p.up = dict(self.up)
        p.windows = self.windows
        p.keep = self.keep
        p.hist = {b: list(v) for b, v in self.hist.items()}
        p.reserve = self.reserve
        return p

    @classmethod
    def from_rows(cls, rows, windows=None) -> "Pad":
        p = cls(windows)
        for r in rows:
            p.push(r)
        return p

    # -- the press budget (rule v2)
    def count(self, b: str, w: int, t: int | None = None) -> int:
        """Press starts of b in the w rows ending at row t (default: the next row), i.e. rows t-w+1 .. t."""
        t = self.t if t is None else t
        h = self.hist[b]
        return len(h) - bisect.bisect_right(h, t - w)

    def room(self, b: str) -> tuple:
        """Presses of b that still fit each window if they were all made now: (limit - count) per window."""
        return tuple(n - self.count(b, w) for w, n in self.windows)

    def budget_wait(self, b: str) -> int:
        """Rows until a new press of b fits every window (0 = it fits on the next row). Hard limit."""
        h = self.hist[b]
        w = 0
        for W, N in self.windows:
            if N <= 0:
                return NEVER
            if len(h) >= N:
                w = max(w, h[-N] + W - self.t)          # the N-th last start has to leave the window first
        return w

    def reserve_ok(self, b: str, t: int | None = None) -> bool:
        """Would a press of b on row t still leave the planned fights their presses? (soft plan, see reserve)"""
        if not self.reserve:
            return True
        t = self.t if t is None else t
        h = self.hist[b]
        for (t0, t1, n, rb) in self.reserve:
            if rb != b or t >= t0 or n <= 0:
                continue
            span = max(1, t1 - t0 + 1)
            for W, N in self.windows:
                hi = min(t1, t + W - 1)                 # the last window end that still holds row t
                if hi < t0:
                    continue
                us = list(range(t0, hi + 1, 16))
                if us[-1] != hi:
                    us.append(hi)
                for u in us:
                    need = -(-n * (u - t0 + 1) // span)  # presses the fight wants up to row u (ceil)
                    have = len(h) - bisect.bisect_right(h, u - W)
                    if have + 1 + need > N:
                        return False
        return True

    # -- queries about the NEXT row (index self.t)
    def can_press(self, b: str) -> bool:
        """May button b be down on the next row? (continuing a hold is always fine)"""
        if self.down[b]:
            return True
        if not (self.t - self.start[b] >= PERIOD and self.t - self.up[b] >= RELEASE):
            return False
        return self.budget_wait(b) <= 0 and self.reserve_ok(b)
''')
rep('''        if self.down[b]:
            rel = max(self.t, self.start[b] + HOLD)             # first row it can be up
            return max(rel + RELEASE, self.start[b] + PERIOD) - self.t
        return max(0, self.start[b] + PERIOD - self.t, self.up[b] + RELEASE - self.t)
''', '''        if self.down[b]:
            rel = max(self.t, self.start[b] + HOLD)             # first row it can be up
            w = max(rel + RELEASE, self.start[b] + PERIOD) - self.t
        else:
            w = max(0, self.start[b] + PERIOD - self.t, self.up[b] + RELEASE - self.t)
        w = max(w, self.budget_wait(b))
        if w < NEVER and self.reserve and not self.reserve_ok(b, self.t + w):
            for k in range(1, 65):
                if self.reserve_ok(b, self.t + w + k):
                    return w + k
            return NEVER
        return w
''')
rep('''                if not self.down[b]:
                    self.down[b] = True
                    self.start[b] = self.t
''', '''                if not self.down[b]:
                    self.down[b] = True
                    self.start[b] = self.t
                    h = self.hist[b]
                    h.append(self.t)
                    if h[0] <= self.t - self.keep:
                        lo = self.t - self.keep
                        k = 0
                        while k < len(h) and h[k] <= lo:
                            k += 1
                        del h[:k]
''')
rep('''import json
import os
''', '''import bisect
import json
import os
''')
rep('''def check_rows(rows, prior=()) -> list:
    """Violations of the input rules in rows (given the rows that came before). [] = legal."""
    p = Pad.from_rows(prior)
''', '''def check_rows(rows, prior=(), windows=None) -> list:
    """Violations of the input rules in rows (given the rows that came before), the sustained limits of rule v2
    included (windows: default WINDOWS). [] = legal."""
    p = Pad.from_rows(prior, windows)
''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(tmp, p)
print("patched", p)
