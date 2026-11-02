"""Acts 3-4 (stages $6D 5..11 = 3-1, 3-2, 3-3, 4-1, 4-2, 4-3, 4-4) shared helpers. Owned by the Acts 3-4 agent.

Import by path (ng/stages has no __init__.py on purpose, ng/stages.py is the module `ng.stages`):
    sys.path.insert(0, "<project>/ng/stages"); import a34_core as K

Frame numbering: TAS rows are bk2 rows; rows[k-1] is frame k. A state saved at framecount f is continued with
rows[f:] (frames f+1, ...). The TAS reference RAM (states/tmp/a34_ref/tas_ram.npy, built by a34_mkref) holds the
2 KB RAM after every frame 9830..22200 of the TAS replay from states/ref4751/05_3-1_control.
"""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

import numpy as np

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

from ng.inputs import read_inputs, write_inputs  # noqa: E402

BTNS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
OPP = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}
REF_DIR = PROJECT / "states" / "tmp" / "a34_ref"
OUT_DIR = PROJECT / "logs" / "a34"

# stage index -> (name, TAS control frame, TAS next-stage control frame, TAS start state)
STAGES = {
    5: ("3-1", 9829, 11434, "ref4751/05_3-1_control"),
    6: ("3-2", 11434, 13741, "ref4751/06_3-2_control"),
    7: ("3-3", 13741, 14569, "ref4751/07_3-3_control"),
    8: ("4-1", 14569, 16682, "ref4751/08_4-1_control"),
    9: ("4-2", 16682, 18960, "ref4751/09_4-2_control"),
    10: ("4-3", 18960, 21354, "ref4751/10_4-3_control"),
    11: ("4-4", 21354, 22125, "ref4751/11_4-4_control"),
}
BY_NAME = {v[0]: k for k, v in STAGES.items()}
# TAS next-stage load frame (first frame with the next $6D; logs/tas4751.events.json)
TAS_LOAD = {5: 11282, 6: 13589, 7: 14417, 8: 16530, 9: 18808, 10: 21202, 11: 21973}
# record stage times (control to next control, NES frames; record_notes.md section 6: seconds * 60.0988)
RECORD_STAGE_S = {"3-1": 26.67, "3-2": 38.73, "3-3": 15.17, "4-1": 36.47, "4-2": 38.33, "4-3": 42.55, "4-4": 13.07}
FPS = 60.0988

_ROWS = None
_REF = None


def tas_rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = read_inputs(PROJECT / "logs" / "tas4751.inputs.txt")
    return _ROWS


def ref_ram():
    """(first_frame, array[n, 2048]) of the TAS replay's RAM after each frame."""
    global _REF
    if _REF is None:
        _REF = (9830, np.load(REF_DIR / "tas_ram.npy", mmap_mode="r"))
    return _REF


def ref_at(frame):
    f0, a = ref_ram()
    return a[frame - f0]


# --- RAM comparison -------------------------------------------------------------------------------------------
# strict mask: everything except zero-page temporaries, the controller bytes, the stack page and the OAM buffer
STRICT = np.ones(2048, dtype=bool)
STRICT[0x00:0x20] = False
for _a in (0x21, 0x28, 0x29, 0x2A, 0x2E, 0xEA):
    STRICT[_a] = False
STRICT[0x100:0x300] = False
# loose: the bytes that decide the game (Ryu physics, HP, ninpo, scroll, room, timer, RNG, enemy slots)
LOOSE_ADDRS = [0x50, 0x51, 0x52, 0x62, 0x63, 0x64, 0x65, 0x66, 0x6D, 0x6E, 0x73, 0x84, 0x85, 0x86, 0x87, 0x89,
               0x8A, 0x8B, 0x95, 0xAC, 0xAD, 0xBF, 0xC9] + list(range(0x400, 0x4C0))
LOOSE = np.zeros(2048, dtype=bool)
LOOSE[LOOSE_ADDRS] = True


def ram_np(b: bytes):
    return np.frombuffer(b, dtype=np.uint8)


def diff(a, b, mask=STRICT):
    return np.nonzero((a != b) & mask)[0]


# --- the human input rules, incremental -----------------------------------------------------------------------
class Legal:
    """Mirror of check_inputs.py (period 5, hold 2, release 2, 600:109, 1800:246, no L+R, no U+D).
    ok(row) says whether appending row keeps the list legal so far (a 1-frame press is caught on its release)."""
    PERIOD, HOLD, RELEASE = 5, 2, 2
    WINDOWS = ((600, 109), (1800, 246))

    def __init__(self, history=()):
        self.t = 0
        self.held = dict.fromkeys(BTNS, False)
        self.run = dict.fromkeys(BTNS, 99)
        self.starts = {b: deque() for b in BTNS}
        for r in history:
            self.push(r)

    def copy(self):
        n = Legal.__new__(Legal)
        n.t, n.held, n.run = self.t, dict(self.held), dict(self.run)
        n.starts = {b: deque(q) for b, q in self.starts.items()}
        return n

    def why(self, row):
        """'' if legal, else the (first) reason."""
        w = self.reasons(row, first=True)
        return w[0] if w else ""

    def reasons(self, row, first=False):
        """every reason why appending row breaks a rule ([] = legal)."""
        out = []
        r = set(row)
        if "Left" in r and "Right" in r:
            out.append("L+R")
        if "Up" in r and "Down" in r:
            out.append("U+D")
        if out and first:
            return out
        nt = self.t + 1
        for b in BTNS:
            h = b in r
            if h and not self.held[b]:
                q = self.starts[b]
                if q and nt - q[-1] < self.PERIOD:
                    out.append(f"period {b}")
                elif q and self.run[b] < self.RELEASE:
                    out.append(f"release {b}")
                else:
                    for wf, wmax in self.WINDOWS:
                        c = 0
                        for s in reversed(q):
                            if nt - s < wf:
                                c += 1
                            else:
                                break
                        if c + 1 > wmax:
                            out.append(f"window{wf} {b}")
                            break
            elif not h and self.held[b] and self.run[b] < self.HOLD:
                out.append(f"hold {b}")
            if out and first:
                return out
        return out

    def ok(self, row):
        return self.why(row) == ""

    def push(self, row):
        r = set(row)
        self.t += 1
        for b in BTNS:
            h = b in r
            if h and not self.held[b]:
                q = self.starts[b]
                q.append(self.t)
                while q and self.t - q[0] >= 1800:
                    q.popleft()
                self.held[b] = True
                self.run[b] = 1
            elif h:
                self.run[b] += 1
            elif self.held[b]:
                self.held[b] = False
                self.run[b] = 1
            else:
                self.run[b] += 1

    def can_release(self, b):
        return (not self.held[b]) or self.run[b] >= self.HOLD

    def can_press(self, b):
        if self.held[b]:
            return True
        tmp = self.copy()
        return tmp.why((b,)) == "" or not tmp.why((b,)).endswith(" " + b)


def legal_list(rows, history=()):
    L = Legal(history)
    for i, r in enumerate(rows):
        w = L.why(r)
        if w:
            return i, w
        L.push(r)
    return None, ""


def greedy_legal(rows, L: Legal):
    """Nearest legal rows, frame by frame (commits into L): drop the second of an opposite pair, keep a press that
    cannot be released yet, drop a press that cannot start yet (it starts as soon as allowed while still wanted)."""
    out = []
    for r in rows:
        want = list(r)
        s = set(want)
        if "Left" in s and "Right" in s:
            s.discard("Left" if L.held["Right"] else "Right")
        if "Up" in s and "Down" in s:
            s.discard("Up" if L.held["Down"] else "Down")
        for b in BTNS:
            if L.held[b] and b not in s and not L.can_release(b):
                o = OPP.get(b)
                if o:
                    s.discard(o)
                s.add(b)
        for b in list(s):
            if not L.held[b]:
                tmp = L.copy()
                if tmp.why(tuple(x for x in s if x == b or L.held[x])):
                    if tmp.why((b,)).endswith(b):
                        s.discard(b)
        row = tuple(b for b in BTNS if b in s)
        w = L.why(row)
        if w:  # fall back: keep only what is held and must stay
            row = tuple(b for b in BTNS if L.held[b] and not L.can_release(b))
        L.push(row)
        out.append(row)
    return out


# --- emulator -------------------------------------------------------------------------------------------------
def open_emu(log_name):
    from ng.emulator import BizHawk
    e = BizHawk(log_name=log_name)
    try:
        e.cmd("invis on")
    except Exception:
        pass
    return e


def save_rows(name, rows, comment=""):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return write_inputs(OUT_DIR / f"{name}.inputs.txt", rows, comment)


def load_rows(name):
    return read_inputs(OUT_DIR / f"{name}.inputs.txt")


def wpos(s):
    """Ryu's world x in the room (scroll screen * 256 + scroll + screen x) for a State/dict."""
    scr = s.get("scroll_scr", 0)
    if scr >= 128:
        scr -= 256
    return scr * 256 + s.get("scroll", 0) + s.get("x", 0)


def ram_wpos(r):
    scr = int(r[0x52])
    if scr >= 128:
        scr -= 256
    return scr * 256 + int(r[0x51]) + int(r[0x86])
