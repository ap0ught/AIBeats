"""Shared helpers for the stage 3 (Waterfall) and stage 8 (Alien's Lair) solvers.

Nothing here writes RAM. Everything is built on contra.emulator.BizHawk (frozen) and the bridge's plain commands.

    Pad        per-button press history: tells whether a new press of a button is legal on the next frame under the
               project's input rules (new press of the same button at most once every 5 frames, held >= 2, released
               >= 2) and builds legal rows. The history is carried across segments (Pad.from_rows).
               Rule v2 (2026-10-12): the Pad is also the PRESS BUDGET. It keeps the start rows of every button's
               presses of the last 1,800 rows and refuses, as a hard constraint, a press that would put more than
               109 starts of that button into any 600 rows or more than 246 into any 1,800 (WINDOWS; a parameter).
               A refused press is simply "cannot be pressed now": can_press() is False, fix() drops it,
               wait_press() says when it fits. On top of that a soft plan (`reserve`) keeps presses back for a
               fight that is still ahead.
    Game       one emulator + the rows sent so far in this segment; step(buttons) advances one frame and returns the
               whole 2 KB of RAM (a `R` object with named accessors), with lost-press handling (see step()).
"""
from __future__ import annotations

import bisect
import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from contra.emulator import BizHawk, LOGS_DIR, STATES_DIR  # noqa: E402
from contra.inputs import BUTTONS, to_mask, from_mask, write_inputs, read_inputs  # noqa: E402

PERIOD, HOLD, RELEASE = 5, 2, 2
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


class Pad:
    """Press-rate bookkeeping for the 8 buttons. Frame index t counts the rows of the whole run so far (any origin:
    only differences matter). For each button: start of its last press, whether it is down now, when it went up."""

    def __init__(self, windows=None):
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

    def can_release(self, b: str) -> bool:
        """May button b be up on the next row?"""
        if not self.down[b]:
            return True
        return self.t - self.start[b] >= HOLD

    def must_hold(self, b: str) -> bool:
        return self.down[b] and self.t - self.start[b] < HOLD

    def wait_press(self, b: str) -> int:
        """Rows to wait before a new press of b may start (0 = may start on the next row), assuming b is released
        from now on (or as soon as its hold allows)."""
        if self.down[b]:
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

    def legal(self, row) -> bool:
        row = set(row)
        if "Left" in row and "Right" in row:
            return False
        if "Up" in row and "Down" in row:
            return False
        for b in BUTTONS:
            if b in row:
                if not self.can_press(b):
                    return False
            elif not self.can_release(b):
                return False
        return True

    def fix(self, want) -> tuple:
        """The closest legal row to `want`: buttons that must stay held are added, presses that may not start are
        dropped. Left/Right and Up/Down conflicts: the one that must be held wins, else the wanted one."""
        want = set(want)
        out = set()
        for b in BUTTONS:
            if b in want:
                if self.can_press(b):
                    out.add(b)
            elif self.must_hold(b):
                out.add(b)
        for a, c in (("Left", "Right"), ("Up", "Down")):
            if a in out and c in out:
                if self.must_hold(a) and not self.must_hold(c):
                    out.discard(c)
                elif self.must_hold(c) and not self.must_hold(a):
                    out.discard(a)
                else:
                    out.discard(a if c in want else c)
        return tuple(b for b in BUTTONS if b in out)

    def push(self, row) -> None:
        row = set(row)
        for b in BUTTONS:
            if b in row:
                if not self.down[b]:
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
            elif self.down[b]:
                self.down[b] = False
                self.up[b] = self.t
        self.t += 1


class R:
    """One frame's RAM (2 KB) with the names the solvers use."""
    __slots__ = ("m", "frame", "lagged")

    def __init__(self, m: bytes, frame: int = 0, lagged: int = 0):
        self.m = m
        self.frame = frame
        self.lagged = lagged

    def __getitem__(self, a):
        return self.m[a]

    # level / engine
    @property
    def lroutine(self): return self.m[0x2C]
    @property
    def level(self): return self.m[0x30]
    @property
    def fc(self): return self.m[0x1A]
    @property
    def rng(self): return self.m[0x34]
    @property
    def screen(self): return self.m[0x64]
    @property
    def scroll(self): return self.m[0x65]
    @property
    def pos(self): return self.m[0x64] * 256 + self.m[0x65]
    @property
    def vscroll(self): return self.m[0xFC]
    @property
    def bossdef(self): return self.m[0x3B]
    @property
    def autoscroll(self): return self.m[0x75]
    @property
    def autoscroll1(self): return self.m[0x76]
    @property
    def autodone(self): return self.m[0x84]
    # player
    @property
    def x(self): return self.m[0x334]
    @property
    def y(self): return self.m[0x31A]
    @property
    def sub(self): return self.m[0x94]
    @property
    def vy(self):
        v = self.m[0xC6] * 256 + self.m[0xC4]
        return v - 65536 if v >= 32768 else v
    @property
    def jump(self): return self.m[0xA0]
    @property
    def edge(self): return self.m[0xA4]
    @property
    def pstate(self): return self.m[0x90]
    @property
    def dead(self): return self.m[0xB4] & 1
    @property
    def weapon(self): return self.m[0xAA]
    @property
    def pad(self): return self.m[0xF1]
    @property
    def inv(self): return self.m[0xAE]
    @property
    def barrier(self): return self.m[0xB0]
    @property
    def on_enemy(self): return self.m[0xB6]
    @property
    def hidden(self): return self.m[0xBA]
    @property
    def lives(self): return self.m[0x32]
    @property
    def airborne(self): return bool(self.m[0xA0] or self.m[0xA4])

    def enemies(self):
        """[(slot, type, routine, hp, x, y, state, attr)] for live slots."""
        m = self.m
        return [(s, m[0x528 + s], m[0x4B8 + s], m[0x578 + s], m[0x33E + s], m[0x324 + s], m[0x598 + s], m[0x5A8 + s])
                for s in range(16) if m[0x4B8 + s]]

    def bullets(self):
        m = self.m
        return [(s, m[0x3C8 + s], m[0x3B8 + s], m[0x438 + s]) for s in range(16) if m[0x388 + s]]

    def nbul(self):
        m = self.m
        return sum(1 for s in range(10) if m[0x388 + s])

    def desc(self) -> str:
        m = self.m
        return (f"f{self.frame} scr {m[0x64]}.{m[0x65]:3d} x={m[0x334]:3d} y={m[0x31A]:3d} sub={m[0x94]:02x} vy={self.vy:5d} "
                f"jump={m[0xA0]:02x} edge={m[0xA4]:02x} st={m[0x90]} lr={m[0x2C]} fc={m[0x1A]:3d} rng={m[0x34]:3d} w={m[0xAA]:02x}")

    def edesc(self) -> str:
        return " ".join(f"[{s}:t{t:02x} r{r} hp{hp} {x},{y} s{st:02x} a{at:02x}]" for s, t, r, hp, x, y, st, at in self.enemies())


class Game:
    """One emulator, driven a frame at a time, recording the rows really sent since the last load()/reset_rows().

    Lost presses: NesHawk makes the game ignore the pad on some frames (it then reuses the previous frame's byte).
    step() compares $F1 with what was sent. The row list always holds exactly what was sent, so a replay is
    identical; callers that need a press to have happened check `self.seen` (the pad byte the game saw)."""

    def __init__(self, emu: BizHawk | None = None, log_name: str = "s38.log"):
        self.e = emu or BizHawk(log_name=log_name, fields={})
        self.own = emu is None
        self.rows: list[tuple] = []
        self.pad = Pad()
        self.r: R | None = None
        self.ignored = 0            # frames on which the game's pad byte differed from what was sent
        self.lag = 0
        self.frame = 0

    def close(self):
        if self.own:
            self.e.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def read(self) -> R:
        st = self.e.state()
        self.frame = st["frame"]
        self.r = R(self.e.ram_all(), st["frame"], st["lagged"])
        return self.r

    def load(self, name: str, pad: Pad | None = None) -> R:
        self.e.load(name)
        self.rows = []
        self.pad = pad.copy() if pad else Pad()
        self.ignored = 0
        self.lag = 0
        return self.read()

    def step(self, want=(), strict: bool = False) -> R:
        """Advance one frame with the legal row closest to `want` (strict=True: raise if `want` itself is illegal)."""
        if isinstance(want, str):
            want = tuple(b for b in want.replace(",", "+").split("+") if b)
        row = self.pad.fix(want)
        if strict and set(row) != set(want):
            raise ValueError(f"illegal row {want} at t={self.pad.t} (fixed to {row})")
        resp = self.e.cmd("stepx " + f"{to_mask(row):02x}")
        self.pad.push(row)
        self.rows.append(row)
        f = dict(tok.split("=") for tok in resp.split())
        self.frame = int(f["frame"])
        lagged = int(f["lagged"])
        self.r = R(self.e.ram_all(), self.frame, lagged)
        if lagged:
            self.lag += 1
        elif self.r.pad != to_mask(row) and self.r.lroutine in (4, 8):
            self.ignored += 1
        return self.r

    def run(self, rows) -> R:
        """Replay rows open-loop (no fixing), fast."""
        rows = [tuple(r) for r in rows]
        if not rows:
            return self.r
        st = self.e.run(rows)
        for r in rows:
            self.pad.push(r)
        self.rows.extend(rows)
        return self.read()

    # in-memory snapshots that also keep rows / pad
    def snap(self):
        return (self.e.msave(), list(self.rows), self.pad.copy(), self.ignored, self.lag)

    def restore(self, sn) -> R:
        sid, rows, pad, ign, lag = sn
        self.e.mload(sid)
        self.rows = list(rows)
        self.pad = pad.copy()
        self.ignored, self.lag = ign, lag
        return self.read()

    def free(self, sn):
        try:
            self.e.mfree(sn[0])
        except Exception:
            pass


def save_segment(name: str, rows, meta: dict) -> Path:
    """logs/<name>.inputs.txt (harness format) + logs/<name>.seg.json (rows + meta, for assemble.py)."""
    p = LOGS_DIR / f"{name}.inputs.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    write_inputs(p, rows, " ".join(f"{k}={v}" for k, v in meta.items() if isinstance(v, (int, str)) and " " not in str(v)))
    j = dict(meta)
    j["frames"] = len(rows)
    j["done"] = True
    j["rows"] = ["+".join(r) for r in rows]
    segp = LOGS_DIR / f"{name}.seg.json"
    tmp = segp.with_name(segp.name + ".tmp")
    tmp.write_text(json.dumps(j, indent=0), encoding="utf-8")
    if segp.exists():
        try:
            os.replace(segp, segp.with_name(segp.name + ".backup"))
        except OSError:
            pass
    os.replace(tmp, segp)
    return p


def history_tail(rows, keep: int | None = None, slack: int = 900) -> list:
    """The end of the real press history that the budget needs: at least the longest window (1,800 rows), cut
    on a row before which nothing is held, so that no press is split by the cut (a split press would look like
    a new, short one). Give the result to Pad.from_rows / a solver's prior_rows."""
    rows = [tuple(r) for r in rows]
    if keep is None:
        keep = max((w for w, _ in WINDOWS), default=0) + 10
    cut = max(0, len(rows) - max(keep, 12))
    lo = max(0, cut - slack)
    while cut > lo and rows[cut - 1]:
        cut -= 1
    return rows[cut:]


def check_rows(rows, prior=(), windows=None) -> list:
    """Violations of the input rules in rows (given the rows that came before), the sustained limits of rule v2
    included (windows: default WINDOWS). [] = legal."""
    p = Pad.from_rows(prior, windows)
    bad = []
    for i, r in enumerate(rows):
        if not p.legal(r):
            bad.append((i, r))
        p.push(r)
    return bad
