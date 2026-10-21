"""Open-loop candidate evaluation with savestates, for the stage 3 / stage 8 solvers.

    Engine(n, tag)                n emulators (n <= 3), file checkpoints under states/<tag>/tmp
    eng.root(state, prior_rows)   start a segment at a savestate (one frame before the stage's first frame)
    eng.sim(ck, rows)             play rows from checkpoint ck on a free emulator, return the per-frame trace
    eng.sims(ck, list_of_rows)    the same for many row lists, in parallel
    eng.commit(ck, rows)          play rows from ck and make a new checkpoint at the end

    gen(pad, i0, n, ov, ...)      rows from a policy "base buttons + B cadence" with overrides (jumps, aims, ...)

A checkpoint (Ck) knows its row index in the segment, the rows of the whole segment up to it, and the press
history (Pad), so everything generated after it obeys the input rules across the cut.
"""
from __future__ import annotations

import copy
import queue
import threading
from dataclasses import dataclass, field
from pathlib import Path

from .s3s8_lib import Pad, PROJECT, BizHawk, STATES_DIR
from contra.inputs import to_hex

TR = {"fc": 0x1A, "lroutine": 0x2C, "elr": 0x2D, "level": 0x30, "rng": 0x34, "bossdef": 0x3B, "screen": 0x64,
      "scroll": 0x65, "auto0": 0x75, "auto1": 0x76, "autodone": 0x84, "pstate": 0x90, "sub": 0x94, "jump": 0xA0,
      "edge": 0xA4, "weapon": 0xAA, "inv": 0xAE, "barrier": 0xB0, "death": 0xB4, "onenemy": 0xB6, "pseq": 0xBC,
      "aim": 0xC2, "vyf": 0xC4, "vy": 0xC6, "pad": 0xF1, "vscroll": 0xFC, "x": 0x334, "y": 0x31A, "delay": 0x2A,
      "lives": 0x32, "groutine": 0x18, "nbossdead": 0x85}
for _s in range(16):
    TR[f"t{_s}"] = 0x528 + _s
    TR[f"h{_s}"] = 0x578 + _s
    TR[f"r{_s}"] = 0x4B8 + _s
    TR[f"ex{_s}"] = 0x33E + _s
    TR[f"ey{_s}"] = 0x324 + _s
    TR[f"es{_s}"] = 0x598 + _s
for _s in range(10):
    TR[f"b{_s}"] = 0x388 + _s
    TR[f"br{_s}"] = 0x438 + _s          # bullet routine: 1 = flying, >= 2 = hit (rule v2: pellets a press created)


def pellets_born(prev, cur) -> int:
    """Pellets created between two consecutive trace states (a slot that became active, or was reused)."""
    n = 0
    for s in range(10):
        if cur[f"b{s}"] and (not prev[f"b{s}"] or (prev[f"br{s}"] >= 2 and cur[f"br{s}"] < 2)):
            n += 1
    return n


def b_starts(rows, prev_down: bool = False) -> int:
    """New B presses in a list of rows."""
    n = 0
    for r in rows:
        d = "B" in r
        if d and not prev_down:
            n += 1
        prev_down = d
    return n


@dataclass
class Ck:
    name: str               # savestate name (under states/)
    i: int                  # rows of the segment played before this state
    rows: list              # those rows
    pad: Pad


def new_ov() -> dict:
    return {"jumps": [], "aims": [], "nofire": [], "stops": [], "lefts": [], "holds": [], "fires": []}


def ov_add(ov: dict, **kw) -> dict:
    o = {k: list(v) for k, v in ov.items()}
    for k, v in kw.items():
        o[k].append(v)
    return o


def _in(iv, i):
    """The LAST interval containing i wins (later overrides are added on top of earlier ones)."""
    out = None
    for a, b, *rest in iv:
        if a <= i < b:
            out = rest[0] if rest else True
    return out


def gen(pad: Pad, i0: int, n: int, ov: dict, base=("Right",), fire=True):
    """n rows for segment indices i0..i0+n-1. Policy: `base` held, B pressed as often as the rules allow (2 frames
    down), plus overrides. fire: True = B at the legal cadence everywhere (the first run's metronome), False =
    never, "demand" (rule v2) = B only inside the `fires` intervals. In every mode a press the Pad refuses (5-frame
    rule, press budget, reserve) is not made.
        fires   [(a, b[, gap])] "demand" mode: B presses may start on rows a..b-1, at least `gap` rows apart
        jumps   [i]            A at rows i, i+1
        aims    [(a, b, btn)]  btn ("Up" / "Down") held on rows a..b-1
        nofire  [(a, b)]       no new B press on rows a..b-1
        stops   [(a, b)]       the base direction released on rows a..b-1
        lefts   [(a, b)]       Left instead of Right on rows a..b-1
        holds   [(a, b, btn)]  any extra button held on rows a..b-1
    Returns (rows, pad after)."""
    p = pad.copy()
    rows = []
    jset = set()
    for j in ov["jumps"]:
        jset.add(j)
        jset.add(j + 1)
    for i in range(i0, i0 + n):
        want = set(base)
        if _in(ov["stops"], i):
            want.discard("Right")
            want.discard("Left")
        if _in(ov["lefts"], i):
            want.discard("Right")
            want.add("Left")
        a = _in(ov["aims"], i)
        if a:
            want.discard("Up")
            want.discard("Down")
            if a != "Flat":
                want.add(a)
        h = None
        for (a0, b0, btn) in ov["holds"]:
            if a0 <= i < b0:
                want.add(btn)
        if i in jset:
            want.add("A")
        if fire:
            if p.down["B"]:
                if p.t - p.start["B"] < 2:
                    want.add("B")
            elif not _in(ov["nofire"], i):
                if fire == "demand":
                    f = _in(ov.get("fires", ()), i)
                    if f and (f is True or p.t - p.start["B"] >= f) and p.can_press("B"):
                        want.add("B")
                elif p.can_press("B"):
                    want.add("B")
        row = p.fix(want)
        p.push(row)
        rows.append(row)
    return rows, p


class Engine:
    def __init__(self, n: int = 3, tag: str = "s8", fields: dict | None = None):
        self.tag = tag
        self.fields = dict(fields or TR)
        self.emus = []
        errs = []

        def boot(k):
            try:
                e = BizHawk(log_name=f"{tag}_eng{k}.log", fields=self.fields)
                e.trace(True)
                self.emus.append(e)
            except Exception as ex:  # noqa: BLE001
                errs.append(ex)
        th = [threading.Thread(target=boot, args=(k,)) for k in range(n)]
        for t in th:
            t.start()
        for t in th:
            t.join()
        if errs:
            self.close()
            raise errs[0]
        self.q = queue.Queue()
        for e in self.emus:
            self.q.put(e)
        self.nck = 0
        (STATES_DIR / tag / "tmp").mkdir(parents=True, exist_ok=True)
        self.frames = 0

    def close(self):
        for e in self.emus:
            try:
                e.close()
            except Exception:  # noqa: BLE001
                pass
        self.emus = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def root(self, state: str, prior_rows=()) -> Ck:
        return Ck(state, 0, [], Pad.from_rows(prior_rows))

    def _run(self, e, ck: Ck, rows):
        e.load(ck.name)
        if not rows:
            return []
        e.run(rows)
        self.frames += len(rows)
        return e.last_trace

    def sim(self, ck: Ck, rows):
        e = self.q.get()
        try:
            return self._run(e, ck, rows)
        finally:
            self.q.put(e)

    def sims(self, ck: Ck, rows_list):
        out = [None] * len(rows_list)
        errs = []

        def work(k):
            try:
                out[k] = self.sim(ck, rows_list[k])
            except Exception as ex:  # noqa: BLE001
                errs.append(ex)
        # at most len(emus) run at once (the queue blocks the rest)
        th = [threading.Thread(target=work, args=(k,)) for k in range(len(rows_list))]
        for t in th:
            t.start()
        for t in th:
            t.join()
        if errs:
            raise errs[0]
        return out

    def commit(self, ck: Ck, rows, keep: str | None = None) -> tuple[Ck, list]:
        """Play rows from ck, save a checkpoint after them. Returns (new ck, trace)."""
        rows = [tuple(r) for r in rows]
        e = self.q.get()
        try:
            tr = self._run(e, ck, rows)
            self.nck += 1
            name = keep or f"{self.tag}/tmp/ck{self.nck}_{id(self) & 0xFFFF:04x}"
            e.save(name)
        finally:
            self.q.put(e)
        p = ck.pad.copy()
        for r in rows:
            p.push(r)
        return Ck(name, ck.i + len(rows), ck.rows + rows, p), tr

    def ram(self, ck: Ck, rows=()) -> bytes:
        e = self.q.get()
        try:
            self._run(e, ck, [tuple(r) for r in rows])
            return e.ram_all()
        finally:
            self.q.put(e)


def hpos(s) -> int:
    return s["screen"] * 256 + s["scroll"] + s["x"]


def find_slot(s, typ: int):
    for k in range(16):
        if s[f"r{k}"] and s[f"t{k}"] == typ:
            return k
    return None


def first(tr, pred):
    for k, s in enumerate(tr):
        if pred(s):
            return k
    return None
