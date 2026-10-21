"""Shared machinery of the stage 1 and stage 5 solvers (contra/stages/s1.py, s5.py).

    Ram      one frame's 2 KB of RAM with named accessors (player, scroll, enemies, bullets, background collision)
    Pad      the input-rule tracker: turns "buttons I want" into the nearest row that check_inputs.py accepts
             (one new press of a button per 5 frames, hold >= 2, release >= 2, never L+R / U+D)
             and, since rule v2 (2026-10-12), the PRESS BUDGET: it knows the start row of every press of each
             button over the longest window and refuses a new press that would put more than 109 into any 600
             rows or more than 246 into any 1,800 (WINDOWS; a parameter of Pad). A refused press is simply
             missing from the row legal() returns: for every search it is "cannot fire now"
    Fights   the press plan: which fights are still ahead and what they need, so the run policy keeps headroom
    Game     one emulator driven a frame at a time through a Pad, with in-memory save states that carry the
             Pad and the rows played so far
    Farm     up to 3 emulators evaluating candidate continuations of one saved state in parallel

Nothing here writes RAM. Frame numbers are emulator frame numbers (emu.framecount()).
"""
from __future__ import annotations

import json
import queue
from bisect import bisect_right
import threading
import time
from pathlib import Path

from ..emulator import BizHawk, LOGS_DIR, STATES_DIR
from ..inputs import to_hex, write_inputs

PERIOD, HOLD, RELEASE = 5, 2, 2
WINDOWS = ((600, 109), (1800, 246))      # rule v2: (rows, most new presses of one button in any span of that many rows)
HISTORY_ROWS = 2000                      # rows of real press history a solver hands to Pad.from_rows (>= the longest window)
BTN = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
OPP = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}


# ------------------------------------------------------------------------------------------------ RAM
class Ram:
    __slots__ = ("m", "frame", "lagc", "lagged")

    def __init__(self, m: bytes, frame: int = 0, lagc: int = 0, lagged: int = 0):
        self.m, self.frame, self.lagc, self.lagged = m, frame, lagc, lagged

    # --- globals
    @property
    def fc(self): return self.m[0x1A]
    @property
    def rng(self): return self.m[0x34]
    @property
    def groutine(self): return self.m[0x18]
    @property
    def lr(self): return self.m[0x2C]
    @property
    def level(self): return self.m[0x30]
    @property
    def lives(self): return self.m[0x32]
    @property
    def screen(self): return self.m[0x64]
    @property
    def scroll(self): return self.m[0x65]
    @property
    def scr(self): return self.m[0x64] * 256 + self.m[0x65]
    @property
    def auto(self): return self.m[0x75]
    @property
    def auto_done(self): return self.m[0x84]
    @property
    def tank_scroll(self): return self.m[0x77]
    @property
    def bossdef(self): return self.m[0x3B]
    @property
    def delay(self): return self.m[0x2A]
    @property
    def attack(self): return self.m[0x8E]
    @property
    def paused(self): return self.m[0x25]
    # --- player
    @property
    def x(self): return self.m[0x334]
    @property
    def y(self): return self.m[0x31A]
    @property
    def prog(self): return self.m[0x64] * 256 + self.m[0x65] + self.m[0x334]
    @property
    def pstate(self): return self.m[0x90]
    @property
    def jumping(self): return self.m[0xA0] & 15
    @property
    def falling(self): return self.m[0xA4]
    @property
    def air(self): return (self.m[0xA0] & 15) or self.m[0xA4]
    @property
    def weapon(self): return self.m[0xAA]
    @property
    def dead(self): return (self.m[0xB4] & 1) or self.m[0x90] == 2
    @property
    def inv(self): return self.m[0xAE]
    @property
    def pad(self): return self.m[0xF1]
    @property
    def padnew(self): return self.m[0xF5]
    @property
    def water(self): return self.m[0xB2]
    @property
    def yvel(self):
        v = self.m[0xC6] * 256 + self.m[0xC4]
        return (v - 65536 if v >= 32768 else v) / 256.0
    @property
    def aim(self): return self.m[0xC2]

    def enemies(self):
        """[(slot, type, routine, hp, x, y, state, sprite, attr)] for every live slot."""
        m = self.m
        return [(s, m[0x528 + s], m[0x4B8 + s], m[0x578 + s], m[0x33E + s], m[0x324 + s], m[0x598 + s],
                 m[0x30A + s], m[0x5A8 + s]) for s in range(16) if m[0x4B8 + s]]

    def enemy(self, s):
        m = self.m
        if not m[0x4B8 + s]:
            return None
        return (s, m[0x528 + s], m[0x4B8 + s], m[0x578 + s], m[0x33E + s], m[0x324 + s], m[0x598 + s],
                m[0x30A + s], m[0x5A8 + s])

    def find(self, etype):
        return [e for e in self.enemies() if e[1] == etype]

    def bullets(self):
        """[(slot, x, y, routine)] of live player bullets."""
        m = self.m
        return [(s, m[0x3C8 + s], m[0x3B8 + s], m[0x438 + s]) for s in range(16) if m[0x388 + s]]

    def nbullets(self):
        m = self.m
        return sum(1 for s in range(10) if m[0x388 + s])

    def coll(self, x, y):
        """Background collision code at screen point (x, y): 0 empty, 1 floor, 2 water, 3 solid."""
        m = self.m
        if y >= 0xE0 or y < 0:
            return 0
        yy = y + m[0xFC]
        if yy >= 0x100:
            yy = ((yy & 0xFF) + 0x10) & 0xFF
        elif yy >= 0xF0:
            yy = (yy + 0x10) & 0xFF
        xx = x + m[0xFD]
        nt = m[0xFF] & 1
        if xx >= 256:
            nt ^= 1
            xx -= 256
        off = ((yy >> 2) & 0x3C) | (xx >> 6) | (0x40 if nt else 0)
        b = m[0x680 + off]
        return (b >> (6 - 2 * ((xx >> 4) & 3))) & 3

    def summary(self):
        return (f"f={self.frame} scr {self.screen}.{self.scroll} x={self.x} y={self.y} lr={self.lr} w=${self.weapon:02x} "
                f"fc={self.fc} rng={self.rng} lives={self.lives}")


# ------------------------------------------------------------------------------------------------ input rules
class Pad:
    """Tracks every button's press history and returns the nearest legal row for a wanted set of buttons.

    Press budget (rule v2): `starts[b]` holds the row numbers (= self.t when the press began) of the new presses
    of b over the last `span` rows; `windows` = ((rows, limit), ...). The budget is a hard constraint of
    can_press() / legal(), counted across whatever history was pushed (stage boundaries included).
    `refused` counts the wanted presses that legal() dropped because of a window (not because of the 5-frame
    rule) on the path that led to this Pad."""
    __slots__ = ("held", "run", "since", "t", "starts", "windows", "span", "refused")

    def __init__(self, windows=WINDOWS):
        self.held = {b: False for b in BTN}
        self.run = {b: 99 for b in BTN}        # frames the button has been in its current state
        self.since = {b: 99 for b in BTN}      # frames played after the first frame of its last press
        self.t = 0                             # rows pushed so far
        self.starts = {b: () for b in BTN}     # start rows of the presses in the last `span` rows (tuples: shared by copies)
        self.windows = tuple((int(a), int(c)) for a, c in windows)
        self.span = max([a for a, _ in self.windows], default=0)
        self.refused = 0

    def copy(self):
        p = Pad.__new__(Pad)
        p.held, p.run, p.since = dict(self.held), dict(self.run), dict(self.since)
        p.t, p.starts, p.windows, p.span, p.refused = self.t, dict(self.starts), self.windows, self.span, self.refused
        return p

    @classmethod
    def from_rows(cls, rows, windows=WINDOWS):
        p = cls(windows)
        for r in rows:
            p.push(tuple(r))
        return p

    def rate_ok(self, b):
        """The burst rule alone: released for RELEASE frames and PERIOD frames after the last press began."""
        return (not self.held[b]) and self.run[b] >= RELEASE and self.since[b] + 1 >= PERIOD

    def count(self, b, rows, at=0):
        """New presses of b whose start lies inside the span of `rows` rows that ends on the row played `at` rows
        from now (at = 0: the row about to be played)."""
        st = self.starts[b]
        return len(st) - bisect_right(st, self.t + at - rows) if st else 0

    def budget_ok(self, b, extra=0, at=0):
        """Would a new press of b on the row about to be played keep every window within its limit?
        Planning form: with `extra` more presses to come by the row `at` rows from now, would the windows that
        end there still be within their limits (this press is counted only where it is still inside)."""
        st = self.starts[b]
        for wf, wmax in self.windows:
            n = (len(st) - bisect_right(st, self.t + at - wf)) if st else 0
            if n + (1 if at < wf else 0) + extra > wmax:
                return False
        return True

    def room(self, b, at=0):
        """How many more presses of b fit before the tightest window that ends `at` rows from now is full."""
        return min([wmax - self.count(b, wf, at) for wf, wmax in self.windows], default=10 ** 6)

    def can_press(self, b):
        return self.rate_ok(b) and self.budget_ok(b)

    def can_release(self, b):
        return self.held[b] and self.run[b] >= HOLD

    def legal(self, want):
        """The row to send: `want`, with presses that are not allowed yet dropped and releases that are not
        allowed yet delayed."""
        out = []
        for b in BTN:
            w = b in want
            if w and not self.held[b]:
                if self.rate_ok(b):
                    if self.budget_ok(b):
                        out.append(b)
                    else:
                        self.refused += 1
            elif w and self.held[b]:
                out.append(b)
            elif not w and self.held[b]:
                if not self.can_release(b):
                    out.append(b)
        for a, b in (("Left", "Right"), ("Up", "Down")):
            if a in out and b in out:
                # one of them is a forced hold (cannot be released yet): drop the one that is a new press
                if not self.held[a]:
                    out.remove(a)
                elif not self.held[b]:
                    out.remove(b)
                else:                       # cannot happen: both were held on the previous frame
                    out.remove(b)
        return tuple(out)

    def push(self, row):
        for b in BTN:
            h = b in row
            self.since[b] += 1
            if h == self.held[b]:
                self.run[b] += 1
            else:
                self.held[b] = h
                self.run[b] = 1
                if h:
                    self.since[b] = 0
                    st = self.starts[b]
                    lo = self.t - self.span
                    if st and st[0] <= lo:
                        st = st[bisect_right(st, lo):]
                    self.starts[b] = st + (self.t,)
        self.t += 1

    def b_ready_in(self, b="B"):
        """Frames until a new press of b is allowed by the burst rule (0 = now), assuming it is released as soon
        as possible. The window budget is not looked at here."""
        if self.held[b]:
            rel = max(0, HOLD - self.run[b])           # frames it must still be held
            return max(rel + RELEASE, PERIOD - 1 - self.since[b])
        return max(RELEASE - self.run[b], PERIOD - 1 - self.since[b], 0)


def press_starts(rows, b="B"):
    """Row indices on which a new press of b begins."""
    out, prev = [], False
    for i, r in enumerate(rows):
        h = b in r
        if h and not prev:
            out.append(i)
        prev = h
    return out


def press_report(rows, history=(), b="B", windows=WINDOWS):
    """{'presses': new presses of b in rows, 'most_<wf>': the highest count in any window of wf rows that ends
    inside rows, with the history before them counted} - the same count as check_inputs.py --windows."""
    h = [tuple(r) for r in history][-(max([w for w, _ in windows], default=0) + 5):]
    st = press_starts(list(h) + [tuple(r) for r in rows], b)
    n0 = len(h)
    rep = {"presses": sum(1 for x in st if x >= n0)}
    for wf, _ in windows:
        j = best = 0
        for i in range(len(st)):
            while st[i] - st[j] >= wf:
                j += 1
            if st[i] >= n0:
                best = max(best, i - j + 1)
        rep[f"most_{wf}"] = best
    return rep


class Fights:
    """The press plan of a stage: the fights still ahead and the presses each needs, so that the run policy
    keeps headroom for them. fights = [(world X at which the fight begins, presses it needs), ...] in order.

    room(pad, prog, b) is True when one more press of b now leaves every window with room for every fight not
    yet reached: for fight f, expected `eta` = (its world X - prog) rows from now (Bill moves 1 px a frame at
    best, so this is the earliest it can start: the window that ends there holds the most of what was pressed
    so far), the presses already inside the window that ends there + this one + the needs of f and of the
    earlier fights that would still be inside that window must not exceed the limit."""

    def __init__(self, fights=()):
        self.fights = sorted((int(x), int(n)) for x, n in fights)

    def room(self, pad: Pad, prog: int, b: str = "B"):
        ahead = [(x - prog, n) for x, n in self.fights if x > prog]
        for k, (eta, need) in enumerate(ahead):
            for wf, wmax in pad.windows:
                extra = need + sum(n for e, n in ahead[:k] if e > eta - wf)
                if pad.count(b, wf, eta) + (1 if eta < wf else 0) + extra > wmax:
                    return False
        return True


def fire(pad: Pad, want: set, on: bool = True):
    """Add the B button to `want` at the fastest legal cadence (press 2 frames, release 3)."""
    if not on:
        return want
    if pad.held["B"]:
        if pad.run["B"] < HOLD:
            want.add("B")
    elif pad.can_press("B"):
        want.add("B")
    return want


# ------------------------------------------------------------------------------------------------ emulator
class Game:
    def __init__(self, emu: BizHawk | None = None, name: str = "s1", pad: Pad | None = None):
        self.e = emu or BizHawk(log_name=f"{name}.log", fields={})
        self.e.set_fields({})
        self.pad = pad or Pad()
        self.rows: list[tuple] = []
        self.r: Ram | None = None
        self.stall = 0                      # consecutive frames with Right held, on the ground, and no progress
        self.sync()

    def sync(self):
        st = self.e.cmd("state")
        self.r = self._ram(st)
        return self.r

    def _ram(self, line):
        d = dict(t.split("=") for t in line.split())
        return Ram(self.e.ram(0, 0x800), int(d["frame"]), int(d["lag"]), int(d["lagged"]))

    def step(self, want=()) -> Ram:
        row = self.pad.legal(want)
        st = self.e.cmd("stepx " + to_hex([row]))
        self.pad.push(row)
        self.rows.append(row)
        p0, r0 = self.r.prog, self.r
        self.r = self._ram(st)
        if ("Right" in row and "A" not in row and "Down" not in row and self.r.prog <= p0 and not self.r.air
                and self.r.fc != r0.fc and not self.r.paused):
            self.stall += 1
        else:
            self.stall = 0
        return self.r

    def step_raw(self, row) -> Ram:
        """Send a row exactly as given (replays)."""
        row = tuple(row)
        st = self.e.cmd("stepx " + to_hex([row]))
        self.pad.push(row)
        self.rows.append(row)
        self.r = self._ram(st)
        return self.r

    def run_raw(self, rows) -> Ram:
        rows = [tuple(r) for r in rows]
        if not rows:
            return self.r
        for i in range(0, len(rows), 2000):
            st = self.e.cmd("stepx " + to_hex(rows[i:i + 2000]))
        for r in rows:
            self.pad.push(r)
        self.rows.extend(rows)
        self.r = self._ram(st)
        return self.r

    # in-memory states that carry the pad tracker and the row count
    def snap(self):
        sid = self.e.cmd("msave")
        return (sid, self.pad.copy(), tuple(self.rows), self.r, self.stall)

    def restore(self, tok):
        sid, pad, rows, r, stall = tok
        self.e.cmd(f"mload {sid}")
        self.pad = pad.copy()
        self.rows = list(rows)
        self.r = r
        self.stall = stall
        return r

    def free(self, tok):
        try:
            self.e.cmd(f"mfree {tok[0]}")
        except Exception:
            pass

    # file states (shared between emulators)
    def save_file(self, name):
        p = STATES_DIR / f"{name}.State"
        p.parent.mkdir(parents=True, exist_ok=True)
        self.e.cmd(f"save {p}")
        return name

    def load_file(self, name, pad: Pad | None = None, rows=None):
        p = STATES_DIR / f"{name}.State"
        if self.e.cmd(f"load {p}") != "ok":
            raise RuntimeError(f"load failed: {p}")
        self.pad = pad.copy() if pad is not None else Pad()
        self.rows = list(rows) if rows is not None else []
        self.stall = 0
        return self.sync()

    def close(self):
        self.e.close()


class Farm:
    """n Games on n threads. map(fn, jobs) -> [fn(game, job)] in job order."""

    def __init__(self, n=3, name="farm"):
        self.games = []
        errs = []

        def boot(i):
            try:
                self.games.append(Game(name=f"{name}_{i}"))
            except Exception as ex:      # noqa: BLE001
                errs.append(ex)
        th = [threading.Thread(target=boot, args=(i,)) for i in range(n)]
        [t.start() for t in th]
        [t.join() for t in th]
        if errs:
            self.close()
            raise errs[0]

    @property
    def g0(self):
        return self.games[0]

    def map(self, fn, jobs):
        jobs = list(jobs)
        q = queue.Queue()
        for i, j in enumerate(jobs):
            q.put((i, j))
        out = [None] * len(jobs)
        errs = []

        def work(g):
            while True:
                try:
                    i, j = q.get_nowait()
                except queue.Empty:
                    return
                try:
                    out[i] = fn(g, j)
                except Exception as ex:      # noqa: BLE001
                    import traceback
                    traceback.print_exc()
                    errs.append(ex)
                    return
        th = [threading.Thread(target=work, args=(g,)) for g in self.games]
        [t.start() for t in th]
        [t.join() for t in th]
        if errs:
            raise errs[0]
        return out

    def close(self):
        for g in self.games:
            try:
                g.close()
            except Exception:                 # noqa: BLE001
                pass
        self.games = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def rows_to_str(rows):
    return ["+".join(r) for r in rows]


def save_seg(path, rows, meta=None):
    """logs/<path>.seg.json in the format assemble.py reads ({"rows": [...]}); temp file then rename."""
    p = LOGS_DIR / f"{path}.seg.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    j = dict(meta or {})
    j.update({"done": True, "frames": len(rows), "rows": rows_to_str(rows)})
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(j, indent=0), encoding="utf-8")
    if p.exists():
        bak = p.with_name(p.name + ".backup")
        try:
            bak.unlink(missing_ok=True)
            p.replace(bak)
        except OSError:
            pass
    tmp.replace(p)
    return p


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)
