"""Shared pieces for the two base stages (stage 2 = Base 1, stage 4 = Base 2).

RAM fields for base rooms, a thin emulator session with in-memory save states, input-rule bookkeeping
(the 5-frame press cap carried across segments), and decoders for bullets / enemies.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from contra.emulator import BizHawk, State  # noqa: E402

NB = 10        # P1 Spread bullet slots 0..9
NE = 16        # enemy slots

CORE = {"frame_fc": 0x1A, "rng": 0x34, "groutine": 0x18, "lroutine": 0x2C, "level": 0x30, "lives": 0x32,
        "screen": 0x64, "scroll": 0x65, "cleared": 0x37, "cores": 0x86, "plates": 0x87, "atkcount": 0x88,
        "loc": 0x40, "pstate": 0x90, "death": 0xB4, "elec": 0xC8, "adv": 0xD0, "iscroll": 0x73, "trans": 0x61,
        "x": 0x334, "y": 0x31A, "jump": 0xA0, "pseq": 0xBC, "pad": 0xF1, "padnew": 0xF5, "weapon": 0xAA,
        "inv": 0xAE, "bossdef": 0x3B, "delay": 0x2A, "attack": 0x8E, "elr": 0x2D, "hud": 0x6A, "jflag": 0xCA,
        "gbuf": 0x21, "pause": 0x25, "aim": 0xC2}


def make_fields(bullets: bool = True, enemies: bool = True, extra: dict | None = None) -> dict:
    f = dict(CORE)
    if bullets:
        for i in range(NB):
            f[f"bs{i}"] = 0x388 + i      # slot (0 = free)
            f[f"bt{i}"] = 0x418 + i      # depth timer
            f[f"br{i}"] = 0x438 + i      # routine
            f[f"bx{i}"] = 0x3C8 + i
            f[f"by{i}"] = 0x3B8 + i
            f[f"bvx{i}"] = 0x408 + i     # X velocity whole px (signed)
            f[f"bfx{i}"] = 0x3E8 + i     # X velocity fraction
            f[f"bvy{i}"] = 0x3F8 + i
            f[f"bfy{i}"] = 0x3D8 + i
    if enemies:
        for i in range(NE):
            f[f"er{i}"] = 0x4B8 + i      # routine (0 = empty)
            f[f"et{i}"] = 0x528 + i      # type
            f[f"eh{i}"] = 0x578 + i      # HP
            f[f"ex{i}"] = 0x33E + i
            f[f"ey{i}"] = 0x324 + i
            f[f"es{i}"] = 0x598 + i      # state/width (bit 7 = bullets pass)
            f[f"ed{i}"] = 0x538 + i      # animation delay
            f[f"ea{i}"] = 0x5A8 + i      # attributes
            f[f"e1{i}"] = 0x5B8 + i      # var 1
            f[f"e4{i}"] = 0x5E8 + i      # var 4
            f[f"ec{i}"] = 0x588 + i      # score / collision code
            f[f"ep{i}"] = 0x30A + i      # sprite code (0 = cannot be hit)
            f[f"evx{i}"] = 0x508 + i     # X velocity whole px (signed)
            f[f"efx{i}"] = 0x518 + i     # X velocity fraction
    if extra:
        f.update(extra)
    return f


def bullets(s) -> list:
    """[(slot index, slot byte, timer, routine, x, y)] for live bullets."""
    out = []
    for i in range(NB):
        if s.get(f"bs{i}", 0):
            out.append((i, s[f"bs{i}"], s[f"bt{i}"], s[f"br{i}"], s[f"bx{i}"], s[f"by{i}"]))
    return out


def enemies(s) -> list:
    """[(slot, routine, type, hp, x, y, state, delay, attr, var1, var4)] for used enemy slots."""
    out = []
    for i in range(NE):
        if s.get(f"er{i}", 0):
            out.append((i, s[f"er{i}"], s[f"et{i}"], s[f"eh{i}"], s[f"ex{i}"], s[f"ey{i}"], s[f"es{i}"],
                        s[f"ed{i}"], s[f"ea{i}"], s[f"e1{i}"], s[f"e4{i}"]))
    return out


def fmt_enemies(s) -> str:
    return " ".join(f"[{i}:t{t:02x} r{r} hp{hp} ({x},{y}) s{st:02x} d{d} a{a:02x} v{v1}/{v4}]"
                    for i, r, t, hp, x, y, st, d, a, v1, v4 in enemies(s))


def fmt_bullets(s) -> str:
    return " ".join(f"{i}:{t}{'*' if r != 1 else ''}@{x},{y}" for i, sl, t, r, x, y in bullets(s))


def row(*btn) -> tuple:
    return tuple(b for b in btn if b)


def pmap(emus, fn, jobs):
    """Run fn(emu, job) for every job on the given emulators (one thread each); results in job order."""
    import queue
    import threading
    q = queue.Queue()
    for i, j in enumerate(jobs):
        q.put((i, j))
    out = [None] * len(jobs)
    err = []

    def work(emu):
        while True:
            try:
                i, j = q.get_nowait()
            except queue.Empty:
                return
            try:
                out[i] = fn(emu, j)
            except Exception as ex:  # noqa: BLE001
                import traceback
                out[i] = {"error": traceback.format_exc()}
                err.append(out[i]["error"])
    th = [threading.Thread(target=work, args=(e,)) for e in emus]
    for t in th:
        t.start()
    for t in th:
        t.join()
    if err and all(isinstance(o, dict) and "error" in o for o in out):
        raise RuntimeError(err[0])
    return out


def rows_from_spec(n, spec):
    """spec: [(first, last, 'A+B'), ...] frame offsets inclusive -> list of n button tuples."""
    r = [set() for _ in range(n)]
    for a, b, btn in spec:
        for i in range(max(0, a), min(n - 1, b) + 1):
            r[i] |= set(x for x in btn.split("+") if x)
    order = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
    return [tuple(b for b in order if b in x) for x in r]


# ---------------------------------------------------------------------------------------------------------------
# input rules (check_inputs.py defaults): per button, new press at most once per 5 frames, hold >= 2, release >= 2
PERIOD, HOLD, RELEASE = 5, 2, 2
ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")


class Pad:
    """Tracks the press history of every button so a driver can ask what is legal on the next frame."""

    def __init__(self, hist=()):
        self.t = 0
        self.start = {b: -99 for b in ORDER}      # frame index of the last press start
        self.len = {b: 0 for b in ORDER}          # current hold length (0 = released)
        self.rel = {b: 99 for b in ORDER}         # frames since release (while released)
        for r in hist:
            self.push(r, check=False)

    def copy(self):
        p = Pad.__new__(Pad)
        p.t, p.start, p.len, p.rel = self.t, dict(self.start), dict(self.len), dict(self.rel)
        return p

    def can_press(self, b, at=0):
        """May a new press of b start `at` frames from now (assuming it stays released until then)?"""
        if self.len[b]:
            return False
        return (self.t + at) - self.start[b] >= PERIOD and self.rel[b] + at >= RELEASE

    def can_release(self, b):
        return self.len[b] == 0 or self.len[b] >= HOLD

    def must_hold(self, b):
        return 0 < self.len[b] < HOLD

    def ok(self, row):
        for b in ORDER:
            h = b in row
            if h and not self.len[b] and not self.can_press(b):
                return False
            if not h and self.len[b] and not self.can_release(b):
                return False
        if ("Left" in row and "Right" in row) or ("Up" in row and "Down" in row):
            return False
        return True

    def fix(self, row):
        """Smallest change that makes the row legal: keep buttons that must still be held, drop illegal new presses."""
        out = []
        for b in ORDER:
            h = b in row
            if h and not self.len[b] and not self.can_press(b):
                h = False
            if not h and self.must_hold(b):
                h = True
            if h:
                out.append(b)
        if "Left" in out and "Right" in out:
            out.remove("Left" if self.len["Right"] else "Right")
        if "Up" in out and "Down" in out:
            out.remove("Up" if self.len["Down"] else "Down")
        return tuple(out)

    def push(self, row, check=True):
        if check and not self.ok(row):
            raise ValueError(f"illegal row {row} at t={self.t}: start={self.start} len={self.len} rel={self.rel}")
        for b in ORDER:
            if b in row:
                if not self.len[b]:
                    self.start[b] = self.t
                self.len[b] += 1
                self.rel[b] = 0
            else:
                if self.len[b]:
                    self.len[b] = 0
                    self.rel[b] = 1
                else:
                    self.rel[b] += 1
        self.t += 1


class Sess:
    """One emulator, closed loop: every frame goes through step(); rows and the pad history are kept so that
    snapshot()/restore() rewind the emulator, the row log and the press history together."""

    def __init__(self, emu, hist=(), fields=None):
        self.e = emu
        emu.set_fields(fields or make_fields())
        emu.trace(False)
        self.rows = []
        self.pad = Pad(hist)
        self.s = None
        self.snaps = []

    def load(self, name):
        self.s = self.e.load(name)
        self.rows = []
        return self.s

    def step(self, row=(), strict=True):
        row = tuple(b for b in ORDER if b in row)
        if not self.pad.ok(row):
            if strict:
                raise ValueError(f"illegal row {row} at t={self.pad.t}")
            row = self.pad.fix(row)
        self.pad.push(row)
        self.rows.append(row)
        self.s = State.parse(self.e.cmd("stepx %02x" % sum(BIT[b] for b in row)))
        return self.s

    def snapshot(self):
        sid = self.e.msave()
        self.snaps.append(sid)
        return (sid, list(self.rows), self.pad.copy(), self.s)

    def restore(self, snap):
        sid, rows, pad, s = snap
        self.e.cmd(f"mload {sid}")
        self.rows = list(rows)
        self.pad = pad.copy()
        self.s = s
        return s

    def free(self, snap=None):
        if snap is None:
            for sid in self.snaps:
                try:
                    self.e.mfree(sid)
                except Exception:
                    pass
            self.snaps = []
        else:
            try:
                self.e.mfree(snap[0])
                self.snaps.remove(snap[0])
            except Exception:
                pass


BIT = {"A": 0x80, "B": 0x40, "Select": 0x20, "Start": 0x10, "Up": 0x08, "Down": 0x04, "Left": 0x02, "Right": 0x01}
PROJECT = Path(__file__).resolve().parent.parent.parent
