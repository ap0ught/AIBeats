"""Acts 5-6 (stages $6D 12..21) shared helpers: TAS data, a legal input enforcer, emulator runs, TAS comparison.

Owned by the Acts 5-6 agent. Import by path (ng/stages has no __init__.py on purpose: ng/stages.py must stay the
module `ng.stages`):
    sys.path.insert(0, "<project>/ng/stages"); import a56_common as C

Frame numbering: TAS rows are bk2 rows; rows[k-1] is frame k. A TAS state saved "at" frame f (framecount f) is
continued with rows[f:] (= frames f+1, f+2, ...).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import deque
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

from ng.inputs import read_inputs, write_inputs  # noqa: E402

NAMES = ["1-1", "1-2", "2-1", "2-2", "2-3", "3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "4-4",
         "5-1", "5-2", "5-3", "5-4", "6-1", "6-2", "6-3", "6-4a", "6-4b", "6-5"]
MY_STAGES = list(range(12, 22))
BOSS_STAGES = {15, 19, 20, 21}
OPP = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}
BTNS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")

_TAS_ROWS = None
_TAS_TRACE = None
_TAS_EVENTS = None


def tas_rows():
    global _TAS_ROWS
    if _TAS_ROWS is None:
        _TAS_ROWS = read_inputs(PROJECT / "logs" / "tas4751.inputs.txt")
    return _TAS_ROWS


INT_FIELDS = ("frame", "gm", "dw", "bk", "se", "nx", "cs", "csskip", "pad", "padnew", "subtimer", "timer", "ninpo",
              "hp", "bosshp", "stage", "room", "lives", "x", "xsub", "y", "vx", "vy", "scroll", "scroll_scr",
              "scroll_sub", "inv", "boss_real", "rng", "item", "dead", "rflags", "anim", "coll", "hudphase")


def tas_trace():
    """list indexed by frame (index 0 unused): dict of int fields of the TAS replay trace."""
    global _TAS_TRACE
    if _TAS_TRACE is None:
        out = [None]
        with open(PROJECT / "logs" / "tas4751.trace.csv", newline="") as f:
            for r in csv.DictReader(f):
                out.append({k: int(r[k]) for k in INT_FIELDS if k in r})
        _TAS_TRACE = out
    return _TAS_TRACE


def tas_events():
    global _TAS_EVENTS
    if _TAS_EVENTS is None:
        _TAS_EVENTS = json.loads((PROJECT / "logs" / "tas4751.events.json").read_text())
    return _TAS_EVENTS


def tas_stage(stage: int) -> dict:
    return tas_events()["stages"][stage]


def tas_ref(stage: int) -> dict:
    """Reference for the beam: rows[k] = the row that advances reference state k to k+1; trace[k] = fields after k."""
    return {"name": "tas4751", "rows": tas_rows(), "trace": tas_trace(), "control": tas_stage(stage)["control"],
            "load_next": tas_stage(stage + 1)["load"] if stage < 21 else 39084}


def legal_ref(path_json) -> dict:
    """Reference from one of our own solved stages (logs/a56_<name>_<tag>.json + .ref.json written by a56_solve)."""
    j = json.loads(Path(path_json).read_text())
    rj = json.loads(Path(str(path_json).replace(".json", ".ref.json")).read_text())
    f0 = j["start_frame"]
    rows = [()] * f0 + [tuple(r) for r in read_inputs(j["inputs"])]
    trace = {int(k): v for k, v in rj["trace"].items()}
    tr = [None] * (max(trace) + 1)
    for k, v in trace.items():
        tr[k] = v
    tr[f0] = rj["start"]
    return {"name": Path(path_json).stem, "rows": rows, "trace": tr, "control": f0, "load_next": j["load"]}


def abs_x(s) -> int:
    """Ryu's position in the room: scroll screen*256 + scroll + x (screen x)."""
    scr = s.get("scroll_scr", 0)
    if scr >= 128:
        scr -= 256
    return scr * 256 + s.get("scroll", 0) + s.get("x", 0)


# ---------------------------------------------------------------------------------------------------------------
# Legal input enforcer (project rules: per button new press >= 5 frames after the previous press start, held >= 2,
# released >= 2; <= 109 presses / 600 f and <= 246 / 1800 f; no L+R; no U+D). Every row it emits is legal given the
# history it was fed; check_inputs.py is still the judge.
# ---------------------------------------------------------------------------------------------------------------
class Enforcer:
    PERIOD, HOLD, RELEASE = 5, 2, 2
    WINDOWS = ((600, 109), (1800, 246))

    def __init__(self, history=()):
        self.t = 0                                   # frames emitted so far (1-based index of the last one)
        self.held = {b: False for b in BTNS}
        self.run = {b: 0 for b in BTNS}              # frames held (if held) or released (if not)
        self.starts = {b: deque() for b in BTNS}     # press start frames within the last 1800
        self.pending = {b: 0 for b in BTNS}          # a wanted press that was blocked: frames left to retry
        for r in history:
            self._commit(set(r))

    def copy(self):
        n = Enforcer.__new__(Enforcer)
        n.t = self.t
        n.held = dict(self.held)
        n.run = dict(self.run)
        n.starts = {b: deque(q) for b, q in self.starts.items()}
        n.pending = dict(self.pending)
        return n

    def can_press(self, b) -> bool:
        if self.held[b]:
            return False
        q = self.starts[b]
        nt = self.t + 1
        if q and nt - q[-1] < self.PERIOD:
            return False
        if self.run[b] < self.RELEASE and self.t > 0 and q:
            return False
        for wf, wmax in self.WINDOWS:
            c = sum(1 for s in q if nt - s < wf)
            if c + 1 > wmax:
                return False
        o = OPP.get(b)
        if o and self.held[o] and self.run[o] < self.HOLD:
            return False
        return True

    def can_release(self, b) -> bool:
        return (not self.held[b]) or self.run[b] >= self.HOLD

    def _commit(self, rowset):
        self.t += 1
        for b in BTNS:
            h = b in rowset
            if h and not self.held[b]:
                self.starts[b].append(self.t)
                self.held[b] = True
                self.run[b] = 1
            elif h:
                self.run[b] += 1
            elif self.held[b]:
                self.held[b] = False
                self.run[b] = 1
            else:
                self.run[b] += 1
            q = self.starts[b]
            while q and self.t - q[0] >= 1800:
                q.popleft()

    def emit(self, want, retry=3, prefer=None) -> tuple:
        """Turn a wanted row into the nearest legal row and commit it. retry: frames a blocked new press is kept
        pending (pressed as soon as allowed). prefer: for L+R / U+D conflicts, the direction to keep."""
        want = set(want)
        for a, b in (("Left", "Right"), ("Up", "Down")):
            if a in want and b in want:
                keep = prefer if prefer in (a, b) else (a if self.held[a] else b if self.held[b] else a)
                want.discard(b if keep == a else a)
        out = set()
        # first the directions/buttons already held or forced
        for b in BTNS:
            if self.held[b]:
                if b in want or not self.can_release(b):
                    out.add(b)
        for b in BTNS:
            if b in out:
                continue
            w = b in want or self.pending[b] > 0
            if not w:
                continue
            if b in want and self.held[b]:
                continue
            o = OPP.get(b)
            if o and o in out:
                if b in want and not self.held[b]:
                    self.pending[b] = max(self.pending[b], retry)
                continue
            if self.can_press(b):
                out.add(b)
                self.pending[b] = 0
            elif b in want:
                self.pending[b] = max(self.pending[b], retry) if self.pending[b] == 0 else self.pending[b]
        for b in BTNS:
            if b not in out and self.pending[b] > 0 and b not in want:
                self.pending[b] -= 1
            elif b in out and self.held[b] is False:
                self.pending[b] = 0
        # a pending press that started gets the minimum hold automatically via can_release
        row = tuple(b for b in BTNS if b in out)
        self._commit(out)
        return row


def legalize(rows, history=(), retry=3):
    en = Enforcer(history)
    return [en.emit(r, retry) for r in rows]


# ---------------------------------------------------------------------------------------------------------------
# Emulator helpers
# ---------------------------------------------------------------------------------------------------------------
def open_emu(log_name):
    from ng.emulator import BizHawk
    e = BizHawk(log_name=log_name)
    try:
        e.cmd("invis on")
    except Exception:
        pass
    return e


def play_trace(e, rows):
    """Play rows with trace on; return list of State per frame."""
    e.trace(True)
    try:
        e.run(rows)
        return list(e.last_trace)
    finally:
        e.trace(False)


def stage_done(s, stage) -> bool:
    return s.get("stage", stage) != stage


def save_rows(path, rows, comment=""):
    return write_inputs(path, rows, comment)
