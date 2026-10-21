"""Shared helpers for the stage 6 (Energy Zone) and stage 7 (Hangar) solvers.

Nothing here writes RAM except the functions whose names start with dbg_ (mapping tools only, never a run).

    FIELDS            the RAM bytes reported with every traced frame (player, 16 enemy slots, bullets)
    Sim               one emulator: load a state, play rows with a per-frame trace, in-memory save states
    Fr                one traced frame with helpers (world x, enemies(), dead ...)
    Presser           press-rate bookkeeping (one new press per 5 frames, hold >= 2, release >= 2), per button
    legal(rows, hist) check a list of rows against the cap, given the rows that came before
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contra.emulator import BizHawk, State  # noqa: E402

PERIOD, HOLD, RELEASE = 5, 2, 2

BASE_FIELDS = {
    "fc": 0x1A, "rng": 0x34, "pause": 0x25, "delay": 0x2A, "lroutine": 0x2C, "elr": 0x2D, "wstr": 0x2F, "level": 0x30,
    "lives": 0x32, "bossdef": 0x3B, "stop": 0x58, "screen": 0x64, "scroll": 0x65, "fscroll": 0x68, "auto": 0x75,
    "sgr": 0x79, "sgt": 0x7A, "bossdone": 0x84, "atk": 0x8E, "pstate": 0x90, "ysub": 0x94, "xvel": 0x98,
    "jump": 0xA0, "fall": 0xA4, "weapon": 0xAA, "inv": 0xAE, "barrier": 0xB0, "death": 0xB4, "onen": 0xB6,
    "freeze": 0xB8, "hidden": 0xBA, "pseq": 0xBC, "aim": 0xC2, "yfr": 0xC4, "yvel": 0xC6, "boost": 0xD4,
    "psprite": 0xD6, "pad": 0xF1, "padnew": 0xF5, "hs": 0xFD, "ppuctrl": 0xFF, "x": 0x334, "y": 0x31A,
    "groutine": 0x18, "gameover": 0x38,
}
ENEMY_ARRAYS = {"er": 0x4B8, "et": 0x528, "eh": 0x578, "ex": 0x33E, "ey": 0x324, "es": 0x598, "ea": 0x5A8,
                "ed": 0x538, "ef": 0x568, "ev": 0x5B8, "esp": 0x30A}
BULLET_ARRAYS = {"bs": 0x388, "bx": 0x3C8, "by": 0x3B8, "br": 0x438}


def make_fields(enemies=True, bullets=True, extra=None):
    f = dict(BASE_FIELDS)
    if enemies:
        for k, a in ENEMY_ARRAYS.items():
            for i in range(16):
                f[f"{k}{i}"] = a + i
    if bullets:
        for k, a in BULLET_ARRAYS.items():
            for i in range(10):
                f[f"{k}{i}"] = a + i
    if extra:
        f.update(extra)
    return f


FIELDS = make_fields()
LEAN = make_fields(enemies=False, bullets=False)


class Fr(State):
    """One traced frame."""

    @property
    def wx(self):                       # world X of the player
        return self["screen"] * 256 + self["scroll"] + self["x"]

    @property
    def cam(self):                      # world X of the left screen edge
        return self["screen"] * 256 + self["scroll"]

    @property
    def dead(self):
        return bool(self["death"] & 1) or self["pstate"] == 2

    def enemies(self):
        out = []
        for i in range(16):
            if self.get(f"er{i}", 0):
                out.append({"slot": i, "type": self[f"et{i}"], "routine": self[f"er{i}"], "hp": self[f"eh{i}"],
                            "x": self[f"ex{i}"], "y": self[f"ey{i}"], "state": self[f"es{i}"], "attr": self[f"ea{i}"],
                            "delay": self[f"ed{i}"], "frame": self[f"ef{i}"], "var1": self[f"ev{i}"],
                            "sprite": self[f"esp{i}"]})
        return out

    def bullets(self):
        return [(i, self[f"bx{i}"], self[f"by{i}"], self[f"br{i}"]) for i in range(10) if self.get(f"bs{i}", 0)]

    def nbullets(self):
        return sum(1 for i in range(10) if self.get(f"bs{i}", 0))


def parse_trace(resp_states):
    return [Fr(s) for s in resp_states]


class Sim:
    """One emulator with a traced run primitive."""

    def __init__(self, name="s6", fields=None):
        self.fields = fields or FIELDS
        self.e = BizHawk(log_name=f"{name}.log", fields=self.fields)
        self.e.trace(True)
        self.pid = self.e.pid

    def set_fields(self, fields):
        self.fields = fields
        self.e.set_fields(fields)

    def close(self):
        self.e.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def load(self, name) -> Fr:
        return Fr(self.e.load(name))

    def save(self, name):
        return self.e.save(name)

    def msave(self):
        return self.e.msave()

    def mload(self, sid) -> Fr:
        return Fr(self.e.mload(sid))

    def mfree(self, sid):
        try:
            self.e.mfree(sid)
        except Exception:      # noqa: BLE001
            pass

    def state(self) -> Fr:
        return Fr(self.e.state())

    def run(self, rows):
        """Play rows, return one Fr per frame."""
        if not rows:
            return []
        self.e.run(rows)
        return [Fr(s) for s in self.e.last_trace]

    def ram(self, a, n=1):
        return self.e.ram(a, n)


# ------------------------------------------------------------------ press-rate rules

class Presser:
    """Tracks, per button, when the last press started and ended, so a controller can ask 'may I start a new
    press of B on this frame?'. Frames are a running index (any origin). Feed every row with feed()."""

    def __init__(self, history=()):
        self.t = 0
        self.start = {}          # button -> index of the start of its latest press
        self.end = {}            # button -> index of the last frame it was held
        self.held = set()
        for r in history:
            self.feed(r)

    def copy(self):
        p = Presser()
        p.t, p.start, p.end, p.held = self.t, dict(self.start), dict(self.end), set(self.held)
        return p

    def can_press(self, b):
        """May a NEW press of b start on the next frame fed?"""
        if b in self.held:
            return False
        if b in self.start and self.t - self.start[b] < PERIOD:
            return False
        if b in self.end and self.t - self.end[b] - 1 < RELEASE:
            return False
        return True

    def must_hold(self, b):
        """Is b held and has it been held for fewer than HOLD frames (so it must stay held)?"""
        return b in self.held and self.t - self.start[b] < HOLD

    def feed(self, row):
        row = set(row)
        for b in row:
            if b not in self.held:
                self.start[b] = self.t
            self.end[b] = self.t
        self.held = row
        self.t += 1


def violations(rows, history=(), buttons=("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")):
    """List of (index into rows, text) rule violations of rows given the rows played before them."""
    hist = [tuple(r) for r in history][-12:]
    allr = hist + [tuple(r) for r in rows]
    off = len(hist)
    out = []
    for i, r in enumerate(allr):
        if i >= off and (("Left" in r and "Right" in r) or ("Up" in r and "Down" in r)):
            out.append((i - off, "opposite directions"))
    for b in buttons:
        start = None
        prev_start = None
        prev_end = None
        for i, r in enumerate(allr + [()]):
            h = b in r
            if h and start is None:
                start = i
                if i >= off:
                    if prev_start is not None and i - prev_start < PERIOD:
                        out.append((i - off, f"{b} period {i - prev_start}"))
                    if prev_end is not None and i - prev_end - 1 < RELEASE:
                        out.append((i - off, f"{b} release {i - prev_end - 1}"))
            elif not h and start is not None:
                if i - start < HOLD and i < len(allr) and i - 1 >= off:
                    out.append((i - 1 - off, f"{b} hold {i - start}"))
                prev_start, prev_end = start, i - 1
                start = None
    return sorted(out)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    if path.exists():
        bak = path.with_name(path.name + ".backup")
        try:
            path.replace(bak)
        except OSError:
            pass
    tmp.replace(path)


# ------------------------------------------------------------------ background collision (read only)

def collision_columns(ram: bytes):
    """From a full RAM dump: {(world column, row): code} for the 16-px cells visible on screen.
    code 0 empty, 1 floor, 2 water, 3 solid. Rows are SCREEN rows (y = row * 16).
    A floor cell whose top is at y gives a standing Y of y - 12."""
    hs, ppu, screen, scroll = ram[0xFD], ram[0xFF], ram[0x64], ram[0x65]
    out = {}
    cam = screen * 256 + scroll
    for sx in range(0, 256, 16):
        v = hs + sx
        nt = (ppu & 1) ^ (v >> 8)
        col = (v & 0xFF) >> 4
        wc = (cam + sx) >> 4
        for row in range(15):
            v = row * 16 + ram[0xFC]            # the game adds VERTICAL_SCROLL to the screen Y
            if v >= 0xF0:
                v = (v + 16) & 0xFF
            r = (v >> 4) & 15
            b = ram[0x680 + nt * 0x40 + r * 4 + (col >> 2)]
            code = (b >> (6 - 2 * (col & 3))) & 3
            out[(wc, row)] = code
    return out
