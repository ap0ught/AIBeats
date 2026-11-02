"""ng/legal.py - make TAS input legal under the project's human rules, and repair the result on the emulator.

OWNER: the Acts 1-2 agent. Other agents import this module READ-ONLY. The API below is kept backward compatible
(new keyword arguments only get defaults; nothing listed here is renamed or removed). Status and change log:
knowledge/legal_a12_notes.md (top of the file).

The rules (knowledge/project_rules.md, judged by check_inputs.py; RULES below are its defaults):
  * controller 1 only, never Left+Right, never Up+Down on one frame;
  * per button: a new press at most every `period` (5) frames (start to start), every press held >= `hold` (2)
    frames, released >= `release` (2) frames between two presses;
  * per button: <= 109 new presses in any 600 frames and <= 246 in any 1,800 frames (windows), counted across
    stage boundaries - so every function takes `history` = the legal rows played before (from power-on, or at
    least the last 1,800 frames).
A row is a tuple of button names ("Up","Down","Left","Right","Select","Start","B","A"), as ng/inputs.py.

API (stable)
------------
RULES                                   dict(period=5, hold=2, release=2, windows=((600, 109), (1800, 246)))
check(rows, history=(), **rules) -> dict      check_inputs.check() on history+rows; ["pass"] is the verdict
is_legal(rows, history=(), **rules) -> bool
class Legality(history=(), rules=RULES)       incremental judge, same semantics as check_inputs.py
    .can(row) -> bool                   may `row` be the next frame?
    .why(row) -> list[str]              the reasons it may not
    .fix(row) -> row                    nearest legal row: keep buttons that must stay held, drop presses that
                                        are not allowed yet, drop one of an opposing pair (keeps the held one)
    .push(row) / .copy() / .t           append a frame (does not check) / clone / frames seen
    .free_press(b) -> int               frames until a new press of b is allowed (0 = now)
resolve_opposing(rows, choose=None) -> rows
    every L+R / U+D frame resolved; choose(i, row, pair) -> the button to keep or None. Default: drop both.
enforce(rows, history=(), weights=None, max_delay=4, rules=RULES) -> rows
    press-rate repair with lookahead (dynamic programme per button over the desired presses: keep / delay by
    1..max_delay / merge with the previous press / drop, cost = weight of what is lost). weights: optional
    {(button, frame_index): weight} for press STARTS (frame_index into rows, 0-based; default 1.0, directions
    5.0). The result always passes is_legal(rows, history).
project(rows, history=(), choose=None, weights=None, max_delay=4) -> rows
    resolve_opposing + enforce (open loop, no emulator)
class TasRef(name="tas4751")            the TAS replay trace (logs/<name>.trace.csv, one row per frame)
    .rows                               the TAS input rows (row k = frame k, index 0 = frame 1)
    .at(frame) -> dict                  traced fields after that frame
    .control(stage) / .load(stage)      frames (load = first frame with the new $6D; control = load + 151)
    .stage_rows(stage) -> (first_frame, rows)  the TAS rows from control+1 up to and incl. the next stage's control
    .pos(frame) -> (stage, room, X, y)  X = scroll_scr*256 + scroll + x (absolute x in the room)
effects_resolve(emu, rows, first_frame, ...) -> (rows, info)   closed loop, ON the TAS trajectory: every
    opposing frame is resolved by RAM effect (the candidate whose RAM after the frame equals the TAS row's RAM,
    else the nearest by key fields), and every press start of A/B/Up/Down/Left/Right gets a weight = does
    removing it change RAM (10.0) or not (0.05). Needs the emulator positioned at frame first_frame-1 ON the
    TAS trajectory (a states/ref4751 state). info has the per-frame decisions.
play(emu, rows, chunk=..., stop=None) -> list[State]           traced play with an early stop predicate
score_progress(trace_state, ref, frame_hint, window=...) -> (k, dist)   nearest TAS frame k to our position
Repair(emu, ref, ...)                   closed-loop repair (see class doc): follow the TAS with legal rows; at a
    divergence search legal input windows (beam) and keep the variant with the best progress
Waypoints(rec_json, stage, tas=None)    (round 2) the record holder's route from the record video: .pts
    [(t, room, X, y)], .at(t) -> (room, X, y), .time_map() -> TAS frame per record time, .columns()
waypoint_ref(wp, f0) -> dict           a beam reference that follows the record in record time from our frame
    f0 (the `ref` format of ng/stages/a56_beam.StageBeam; driver ng/stages/a12r2_solve.py)
hybrid_ref(wp, f0, pad=30) -> dict      the TAS reference with the record's route spliced in around the TAS's
    banned moves (banned_tas_frames(tas, k0, k1)); lazy-followable where the TAS line is legal
KEYS                                    the trace fields compared for "in sync" (positions, room, stage, HP, ...)

Notes
-----
* Frame numbering: the reference trace and the states/ref4751 states use bk2 numbering (row k = frame k;
  a state named "..._control" was saved AFTER its frame f, so the next row to play is rows[f], 0-based).
* Nothing here pokes RAM. Everything that ends in a file is verified open-loop by the caller.
"""
from __future__ import annotations

import csv
import hashlib
import heapq
import math
from collections import deque
from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence

PROJECT = Path(__file__).resolve().parent.parent
LOGS = PROJECT / "logs"

BUTTONS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
OPPOSING = (("Left", "Right"), ("Up", "Down"))
DIRECTIONS = ("Up", "Down", "Left", "Right")
RULES = dict(period=5, hold=2, release=2, windows=((600, 109), (1800, 246)))

# trace fields that define "the same game state" for following the TAS (enemy RAM is not traced; HP/inv cover hits)
KEYS = ("stage", "room", "x", "xsub", "y", "vy", "vy_sub", "scroll", "scroll_scr", "hp", "inv", "lives", "dead",
        "anim", "rflags", "ninpo", "item", "bosshp", "boss_real", "timer", "subtimer")
POS_KEYS = ("stage", "room", "x", "xsub", "y", "scroll", "scroll_scr")


def norm(row: Iterable[str]) -> tuple:
    s = set(row)
    return tuple(b for b in BUTTONS if b in s)


def _rules(r):
    d = dict(RULES)
    if r:
        d.update(r)
    return d


# ------------------------------------------------------------------------------------------- judging
def check(rows, history=(), **rules) -> dict:
    """check_inputs.check() on history + rows (the project's judge)."""
    import sys
    sys.path.insert(0, str(PROJECT))
    import check_inputs as ci
    r = _rules(rules)
    allr = [norm(x) for x in list(history) + list(rows)]
    return ci.check(allr, r["period"], r["hold"], r["release"], ci.BUTTONS, (), tuple(tuple(w) for w in r["windows"]))


def is_legal(rows, history=(), **rules) -> bool:
    return check(rows, history, **rules)["pass"]


class _Btn:
    __slots__ = ("held", "run", "last_start", "last_end", "starts")

    def __init__(self):
        self.held = False
        self.run = 0
        self.last_start = -10 ** 9
        self.last_end = -10 ** 9
        self.starts = deque()

    def copy(self):
        c = _Btn()
        c.held, c.run, c.last_start, c.last_end = self.held, self.run, self.last_start, self.last_end
        c.starts = deque(self.starts)
        return c


class Legality:
    """Incremental judge with check_inputs.py's semantics. Frame index t = number of rows pushed so far."""

    def __init__(self, history: Sequence = (), rules: dict | None = None):
        self.r = _rules(rules)
        self.maxw = max([w for w, _ in self.r["windows"]] or [0])
        self.b = {k: _Btn() for k in BUTTONS}
        self.t = 0
        for row in history:
            self.push(row)

    def copy(self) -> "Legality":
        c = Legality.__new__(Legality)
        c.r, c.maxw, c.t = self.r, self.maxw, self.t
        c.b = {k: v.copy() for k, v in self.b.items()}
        return c

    def push(self, row) -> None:
        t = self.t
        s = set(row)
        for k, st in self.b.items():
            h = k in s
            if h and not st.held:
                st.held, st.run, st.last_start = True, 1, t
                st.starts.append(t)
                while st.starts and st.starts[0] <= t - self.maxw:
                    st.starts.popleft()
            elif h:
                st.run += 1
            elif st.held:
                st.held, st.last_end, st.run = False, t, 0
        self.t = t + 1

    def _press_ok(self, st: _Btn, t: int) -> bool:
        if t - st.last_end < self.r["release"] or t - st.last_start < self.r["period"]:
            return False
        for wf, wmax in self.r["windows"]:
            n = sum(1 for x in st.starts if x > t - wf)
            if n + 1 > wmax:
                return False
        return True

    def free_press(self, b: str) -> int:
        st = self.b[b]
        if st.held:
            return 10 ** 6
        for d in range(0, 2000):
            if self._press_ok(st, self.t + d):
                return d
        return 10 ** 6

    def why(self, row) -> list:
        s = set(row)
        out = []
        for a, c in OPPOSING:
            if a in s and c in s:
                out.append(f"{a}+{c}")
        for k, st in self.b.items():
            h = k in s
            if st.held and not h and st.run < self.r["hold"]:
                out.append(f"{k} must stay held ({st.run} < {self.r['hold']})")
            if h and not st.held and not self._press_ok(st, self.t):
                out.append(f"{k} press not allowed yet")
        return out

    def can(self, row) -> bool:
        s = set(row)
        for a, c in OPPOSING:
            if a in s and c in s:
                return False
        for k, st in self.b.items():
            h = k in s
            if st.held:
                if not h and st.run < self.r["hold"]:
                    return False
            elif h and not self._press_ok(st, self.t):
                return False
        return True

    def must_hold(self) -> set:
        return {k for k, st in self.b.items() if st.held and st.run < self.r["hold"]}

    def fix(self, row) -> tuple:
        s = set(row) | self.must_hold()
        for k in list(s):
            st = self.b[k]
            if not st.held and not self._press_ok(st, self.t):
                s.discard(k)
        for a, c in OPPOSING:
            if a in s and c in s:
                # keep the one already held (it may be forced); else keep neither
                if self.b[a].held and not self.b[c].held:
                    s.discard(c)
                elif self.b[c].held and not self.b[a].held:
                    s.discard(a)
                else:
                    mh = self.must_hold()
                    if a in mh:
                        s.discard(c)
                    elif c in mh:
                        s.discard(a)
                    else:
                        s.discard(a)
                        s.discard(c)
        return norm(s)


# ------------------------------------------------------------------------------------------- open-loop projection
def resolve_opposing(rows, choose: Optional[Callable] = None) -> list:
    out = []
    for i, r in enumerate(rows):
        s = set(r)
        for pair in OPPOSING:
            a, c = pair
            if a in s and c in s:
                keep = choose(i, norm(r), pair) if choose else None
                s.discard(a)
                s.discard(c)
                if keep:
                    s.add(keep)
        out.append(norm(s))
    return out


def _runs(rows, b):
    out, st = [], None
    for i, r in enumerate(rows):
        h = b in r
        if h and st is None:
            st = i
        elif not h and st is not None:
            out.append([st, i])
            st = None
    if st is not None:
        out.append([st, len(rows)])
    return out


def _enforce_button(runs, n, b, ls0, le0, fixed, rules, weights, max_delay, forbidden):
    """DP over the desired runs of one button. Returns the output runs [[s, e]] (0-based, e exclusive).
    ls0/le0: start / end of the button's last press before these runs, relative to frame 0 of rows (le0 <= 0 is
    in the past and cannot change). fixed: an output run that must be kept as is at the front ([0, e] when the
    press is held over from the history) or None; then ls0/le0 describe it. forbidden: frames where the opposite
    direction is held."""
    P, H, R = rules["period"], rules["hold"], rules["release"]

    def wt(i):
        dflt = 5.0 if b in DIRECTIONS else 1.0
        return weights.get((b, runs[i][0]), dflt) if weights else dflt

    def ok_hold(s, e):
        return all(f not in forbidden for f in range(s, e))

    states = {(ls0, le0): (0.0, None)}
    trail = []
    for i, (s, e) in enumerate(runs):
        new = {}
        w = wt(i)

        def put(k2, c2, bp):
            if k2 not in new or new[k2][0] > c2:
                new[k2] = (c2, bp)
        for key, (cost, _) in states.items():
            ls, le = key
            put(key, cost + w, (key, "drop", None))
            gap = s - le
            if le > 0 and 0 <= gap <= R and ok_hold(le, e):
                put((ls, max(le, e)), cost + 0.3 * w + 0.01 * gap, (key, "merge", (ls, max(le, e))))
            for d in range(0, max_delay + 1):
                s2 = s + d
                if s2 >= n:
                    break
                if s2 - ls < P:
                    continue
                pe = min(le, s2 - R)
                if pe < le and (le <= 0 or pe < ls + H):
                    continue
                e2 = min(max(e, s2 + H), n)
                if not ok_hold(s2, e2):
                    e2 = min(s2 + H, n)
                    if not ok_hold(s2, e2):
                        continue
                put((s2, e2), cost + w * 0.15 * d + 0.02 * d, (key, "keep", (s2, e2)))
        if len(new) > 64:
            new = dict(heapq.nsmallest(64, new.items(), key=lambda kv: kv[1][0]))
        trail.append(new)
        states = new
    out = []
    if runs:
        key = min(states.items(), key=lambda kv: kv[1][0])[0]
        for i in range(len(runs) - 1, -1, -1):
            _, bp = trail[i][key]
            pkey, act, val = bp
            if act in ("keep", "merge"):
                out.append([act, val[0], val[1]])
            key = pkey
        out.reverse()
    final = [list(fixed)] if fixed else []
    for act, s, e in out:
        if act == "merge" and final and final[-1][0] == s:
            final[-1][1] = max(final[-1][1], e)
        elif act == "merge" and not final:
            pass                       # cannot happen (merge needs le > 0, i.e. an output run)
        else:
            final.append([s, e])
    for j in range(len(final) - 1):
        if final[j + 1][0] - final[j][1] < R:
            final[j][1] = final[j + 1][0] - R
    return final


def enforce(rows, history=(), weights: Optional[dict] = None, max_delay: int = 4, rules: Optional[dict] = None) -> list:
    """Press-rate repair (opposing pairs in rows are resolved first with the default policy). Always legal."""
    r = _rules(rules)
    rows = [norm(x) for x in resolve_opposing(rows)]
    n = len(rows)
    leg = Legality(history, r)
    off = leg.t
    held = {b: set() for b in BUTTONS}
    order = sorted(BUTTONS, key=lambda b: -sum(1 for x in rows if b in x))
    order = [b for b in order if b in DIRECTIONS] + [b for b in order if b not in DIRECTIONS]
    for b in order:
        runs = _runs(rows, b)
        st = leg.b[b]
        ls0 = st.last_start - off
        opp = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}.get(b)
        forbidden = set(held[opp]) if opp else set()
        fixed = None
        if st.held:
            need = max(0, r["hold"] - st.run)
            if runs and runs[0][0] == 0:
                fixed = [0, max(runs[0][1], need)]
                runs = runs[1:]
            elif need > 0:
                fixed = [0, need]
            if fixed:
                le0 = fixed[1]
            else:
                le0 = 0
        else:
            le0 = st.last_end - off
        if not runs and not fixed:
            continue
        final = _enforce_button(runs, n, b, ls0, le0, fixed, r, weights or {}, max_delay, forbidden)
        for s, e in final:
            for f in range(max(0, s), min(n, e)):
                held[b].add(f)
    out = [norm([b for b in BUTTONS if i in held[b]]) for i in range(n)]
    return _final_fix(out, history, r)


def _final_fix(rows, history, r) -> list:
    """Safety net: walk the rows with the incremental judge and fix anything still illegal (windows, edge cases)."""
    leg = Legality(history, r)
    out = []
    for row in rows:
        if not leg.can(row):
            row = leg.fix(row)
        leg.push(row)
        out.append(row)
    return out


def project(rows, history=(), choose=None, weights=None, max_delay: int = 4, rules=None) -> list:
    return enforce(resolve_opposing(rows, choose), history, weights, max_delay, rules)


# ------------------------------------------------------------------------------------------- the TAS reference
class TasRef:
    def __init__(self, name: str = "tas4751"):
        self.name = name
        self.tr = []
        with open(LOGS / f"{name}.trace.csv", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                d = {k: (int(v) if v not in ("",) and k != "input" else v) for k, v in r.items()}
                self.tr.append(d)
        self.rows = [tuple(x for x in d["input"].split("+") if x) for d in self.tr]
        self._loads = {}
        prev = None
        for d in self.tr:
            st = d["stage"]
            if st <= 21 and st != prev:
                self._loads.setdefault(st, d["frame"])
            prev = st
        self._ctl = {}
        for st, f in self._loads.items():
            for d in self.tr[f - 1:f + 400]:
                if d["stage"] == st and d.get("gm"):
                    self._ctl[st] = d["frame"]
                    break

    def at(self, frame: int) -> dict:
        return self.tr[frame - 1]

    def load(self, stage: int) -> Optional[int]:
        return None if stage == 0 else self._loads.get(stage)

    def control(self, stage: int) -> int:
        return self._ctl[stage]

    def stage_rows(self, stage: int):
        a = self.control(stage)
        b = self.control(stage + 1) if stage + 1 in self._ctl else len(self.rows)
        return a + 1, self.rows[a:b]

    def pos(self, frame: int):
        d = self.at(frame)
        return pos_of(d)


def pos_of(d) -> tuple:
    return (d["stage"], d["room"], d["scroll_scr"] * 256 + d["scroll"] + d["x"] + d["xsub"] / 256.0, d["y"])


def score_progress(s, ref: TasRef, frame_hint: int, window: int = 240) -> tuple:
    """(k, dist): the TAS frame k within +-window of frame_hint whose position is nearest to ours (dist in px).
    Same stage required; another room counts as far (rooms only change forward)."""
    st, rm, X, y = pos_of(s)
    best = (frame_hint - window, 1e9)
    lo = max(1, frame_hint - window)
    hi = min(len(ref.tr), frame_hint + window)
    for k in range(lo, hi + 1):
        d = ref.tr[k - 1]
        if d["stage"] != st:
            continue
        if d["room"] != rm:
            continue
        dist = abs(pos_of(d)[2] - X) + abs(d["y"] - y)
        if dist < best[1] or (dist == best[1] and k > best[0]):
            best = (k, dist)
    return best


# ------------------------------------------------------------------------------------------- emulator helpers
def play(emu, rows, chunk: int = 600, stop: Optional[Callable] = None) -> list:
    """Traced play of rows from the emulator's current state. stop(state) -> True ends early (that frame included)."""
    emu.trace(True)
    out = []
    rows = [tuple(r) for r in rows]
    for i in range(0, len(rows), chunk):
        emu.run(rows[i:i + chunk], chunk=chunk)
        for s in emu.last_trace:
            out.append(s)
            if stop and stop(s):
                return out
    return out


def same(a, b, keys=KEYS) -> bool:
    return all(a.get(k) == b.get(k) for k in keys if k in a and k in b)


def ram_digest(emu) -> bytes:
    return emu.ram_all()


def _ram_dist(a: bytes, b: bytes) -> int:
    # weight the player bytes ($80-$95) and the enemy slots ($0400-$04FF) higher
    d = 0
    for i in range(0x30, len(a)):          # $00-$2F: temporaries, PPU shadows, the pad bytes ($28-$2A)
        if a[i] != b[i]:
            if 0x80 <= i <= 0x95 or 0x400 <= i < 0x500 or i in (0x50, 0x51, 0x52, 0x6D, 0x6E):
                d += 10
            elif 0x100 <= i < 0x200 or 0x200 <= i < 0x300 or 0x700 <= i:
                d += 0          # stack, OAM buffer, PPU buffer: cosmetic
            else:
                d += 1
    return d


def effects_resolve(emu, rows, first_frame: int, presses=("A", "B", "Up", "Down", "Left", "Right"),
                    log: Optional[Callable] = None):
    """Walk the TAS rows ON the TAS trajectory (emulator at frame first_frame-1, positioned by the caller).
    For each opposing frame: try the legal candidates from the frame's state and keep the one whose RAM after the
    frame equals the TAS row's RAM (else the nearest). For each press start of `presses`: weight = 10.0 if
    removing that one frame of the button changes RAM after the frame, else 0.05.
    Returns (resolved rows (press rate NOT enforced yet), info) with info = {"weights": {(b, i): w},
    "opposing": [(i, row, chosen, exact)]}."""
    rows = [norm(r) for r in rows]
    out = list(rows)
    weights = {}
    opp = []
    emu.trace(False)
    prev = ()
    for i, r in enumerate(rows):
        s = set(r)
        is_opp = any(a in s and c in s for a, c in OPPOSING)
        new = [b for b in presses if b in s and b not in prev]
        if is_opp or new:
            sid = emu.msave()
            emu.run([r])
            ref_ram = emu.ram_all()
            if is_opp:
                cands = []
                base = set(s)
                pairs = [p for p in OPPOSING if p[0] in s and p[1] in s]
                for p in pairs:
                    base -= set(p)
                opts = [[]]
                for p in pairs:
                    opts = [o + [x] for o in opts for x in (None, p[0], p[1])]
                for o in opts:
                    c = norm(base | {x for x in o if x})
                    emu.mload(sid)
                    emu.run([c])
                    cands.append((_ram_dist(emu.ram_all(), ref_ram), len(c), c))
                cands.sort()
                chosen = cands[0][2]
                out[i] = chosen
                opp.append((i, r, chosen, cands[0][0] == 0))
            for b in new:
                if b in DIRECTIONS and is_opp:
                    continue
                c = norm(set(out[i]) - {b})
                emu.mload(sid)
                emu.run([c])
                weights[(b, i)] = 10.0 if _ram_dist(emu.ram_all(), ref_ram) > 0 else 0.05
            emu.mload(sid)
            emu.mfree(sid)
            emu.run([r])                     # stay ON the TAS trajectory
        else:
            emu.run([r])
        prev = s
        if log and i % 500 == 0:
            log(f"effects_resolve {i}/{len(rows)}")
    return out, {"weights": weights, "opposing": opp}


# ------------------------------------------------------------------------------------------- closed-loop repair
# "anim" is left out: U+D+Right (TAS) and Right (legal) run identically but show different animation numbers
SYNC_KEYS = ("stage", "room", "x", "xsub", "y", "vy", "vy_sub", "scroll", "scroll_scr", "hp", "lives", "dead",
             "rflags", "ninpo", "item", "boss_real")
BOSS_STAGES = (1, 4, 7, 11, 15, 19, 20, 21)


def _sig(s, keys=SYNC_KEYS):
    return tuple(s.get(k) for k in keys)


class Segment:
    """A reference to follow: traced states ref[i] after desired row rows[i] (i = 0 is the first frame played from
    the start state). Build from the TAS (Segment.from_tas) or from an earlier legal solution's trace."""

    def __init__(self, ref_states: Sequence, rows: Sequence, keys=SYNC_KEYS, raw: Optional[Sequence] = None):
        self.ref = list(ref_states)
        self.rows = [norm(r) for r in rows]
        self.raw = [tuple(r) for r in (raw if raw is not None else rows)]   # original rows (may hold L+R / U+D)
        self.keys = keys
        self.index = {}
        for i, s in enumerate(self.ref):
            self.index.setdefault(_sig(s, keys), []).append(i)
        self.stage = self.ref[0]["stage"] if self.ref else None
        self.boss = self.stage in BOSS_STAGES

    @classmethod
    def from_tas(cls, ref: "TasRef", first_frame: int, last_frame: int, keys=SYNC_KEYS):
        return cls(ref.tr[first_frame - 1:last_frame], ref.rows[first_frame - 1:last_frame], keys)

    tol_x = 0.0      # loose sync: |X - X_ref| <= tol_x px and |y - y_ref| <= tol_y (0 = exact on the keys)
    tol_y = 0
    loose_window = 8   # a loose match must lie within +-8 reference frames of the expected index

    def same(self, s, r) -> bool:
        if not self.tol_x and not self.tol_y:
            return same(s, r, self.keys)
        for k in ("stage", "room", "rflags", "item", "boss_real"):   # HP differences are scored, not a desync
            if s.get(k) != r.get(k):
                return False
        if (s.get("dead", 0) & 0x80) != (r.get("dead", 0) & 0x80):
            return False
        if abs(pos_of(s)[2] - pos_of(r)[2]) > self.tol_x or abs(s["y"] - r["y"]) > self.tol_y:
            return False
        if s.get("vy") != r.get("vy") and abs(s["y"] - r["y"]) > 0:
            return False
        return True

    def match(self, s, lo: int, hi: int) -> Optional[int]:
        """An index j in [lo, hi] whose reference state equals s (exact keys, else loosely), nearest to the
        middle of the window first; None if there is none."""
        for j in self.index.get(_sig(s, self.keys), ()):
            if lo <= j <= hi:
                return j
        if not self.tol_x and not self.tol_y:
            return None
        mid = (lo + hi) // 2
        best = None
        lo, hi = max(lo, mid - self.loose_window), min(hi, mid + self.loose_window)
        for j in range(max(0, lo), min(len(self.ref) - 1, hi) + 1):
            if self.same(s, self.ref[j]):
                if best is None or abs(j - mid) < abs(best - mid):
                    best = j
        return best

    height_w = 0.0             # axis mode: frames per px of being lower (+) / higher (-) than the reference
    progress_mode = "nearest"  # "axis": along the room's main direction of travel; "nearest": nearest TAS point

    def progress(self, s, hint: int, back: int = 150, ahead: int = 15) -> tuple:
        if self.progress_mode == "axis" and not self.boss:
            return self.progress_axis(s, hint, back, ahead)
        return self.progress_nearest(s, hint, back, ahead)

    def progress_axis(self, s, hint: int, back: int = 150, ahead: int = 40) -> tuple:
        """(j, 0): the last reference index j around hint the reference had not yet gone past our position
        along the main axis of travel (X, or y in a climb), judged over the reference frames around j."""
        st, rm, X, y = pos_of(s)
        lo, hi = max(0, hint - back), min(len(self.ref) - 1, hint + ahead)
        best = None
        for j in range(lo, hi + 1):
            d = self.ref[j]
            if d["stage"] != st or d["room"] != rm:
                continue
            a, b = max(0, j - 30), min(len(self.ref) - 1, j + 30)
            pa, pb = pos_of(self.ref[a]), pos_of(self.ref[b])
            if pa[1] != rm or pb[1] != rm:
                pa = pos_of(self.ref[max(a, j - 5)]) if pos_of(self.ref[max(a, j - 5)])[1] == rm else pos_of(d)
                pb = pos_of(self.ref[min(b, j + 5)]) if pos_of(self.ref[min(b, j + 5)])[1] == rm else pos_of(d)
            dx, dy = pb[2] - pa[2], pb[3] - pa[3]
            p = pos_of(d)
            if abs(dx) / 1.5 >= abs(dy) / 2.0:
                reached = (X >= p[2] - 0.5) if dx >= 0 else (X <= p[2] + 0.5)
            else:
                reached = (y <= p[3]) if dy <= 0 else (y >= p[3])
            if reached:
                best = j
        if best is not None and self.height_w:
            return best, self.height_w * 1.5 * (y - self.ref[best]["y"])
        if best is None:
            rooms = [d["room"] for d in self.ref[lo:hi + 1]]
            if rooms and s["stage"] == self.stage and rm > max(rooms):
                return hi, 0.0
            if rooms and rm in rooms:
                return lo + rooms.index(rm), 30.0
            return lo, 999.0
        return best, 0.0

    def progress_nearest(self, s, hint: int, back: int = 150, ahead: int = 15) -> tuple:
        """(j, dist): the reference index j around hint that maximises j - dist/1.5, dist = |dX| + 0.75*|dy| px
        (a frame-equivalent: running 1.5 px/f, climbing ~2 px/f); in a boss stage boss HP counts too."""
        st, rm, X, y = pos_of(s)
        lo, hi = max(0, hint - back), min(len(self.ref) - 1, hint + ahead)
        best_j, best_d, best_v = None, 1e9, -1e18
        for j in range(lo, hi + 1):
            d = self.ref[j]
            if d["stage"] != st or d["room"] != rm:
                continue
            p = pos_of(d)
            dist = abs(p[2] - X) + 0.75 * abs(p[3] - y)
            if self.boss:
                dist += 12.0 * max(0, s.get("boss_real", 0) - d.get("boss_real", 0))
            if dist < best_d or (dist == best_d and j > best_j):
                best_j, best_d = j, dist
        if best_j is None:
            rooms = [d["room"] for d in self.ref[lo:hi + 1]]
            if rooms and s["stage"] == self.stage and rm > max(rooms):
                return hi, 0.0
            return lo, 999.0
        return best_j, best_d


class Node:
    __slots__ = ("sid", "leg", "rows", "last", "score", "lag", "synced", "j", "done", "hp")

    def __init__(self, sid, leg, rows, last):
        self.sid, self.leg, self.rows, self.last = sid, leg, rows, last
        self.score, self.lag, self.synced, self.j, self.done, self.hp = 0.0, 0.0, None, 0, None, 0


class Repair:
    """Closed loop: follow `seg` (desired rows + reference states) with legal rows from the emulator's current
    state; at a divergence, beam-search legal input windows and keep the best by progress against the reference.

        rep = Repair(emu, seg, history=legal_rows_before, weights=w, log=print)
        rows, info = rep.solve(done=lambda s: ...)       # the emulator must be at the segment's start state

    done(prev_state, state) -> True when the segment is complete (e.g. the next stage's control frame); that frame's row is
    the last one returned. Parameters: step (frames per beam step), width (beam width), horizon (max beam steps
    per divergence before committing), back (frames rewound before a divergence), hp_cost (frames per HP point
    below the reference). weights: {(button, reference index): w} press importance (effects_resolve)."""

    def __init__(self, emu, seg: Segment, history=(), weights=None, log=print, step: int = 4, width: int = 10,
                 horizon: int = 12, back: int = 8, hp_cost: float = 4.0, max_frames: int = 20000, rules=None,
                 extra_dirs: bool = True, sync_window: int = 40, beam_back: int = 16,
                 edit_depth: int = 1, verbose: bool = False,
                 tol_x: float = 1.5, tol_y: int = 2, esc_lag: float = 6.0, esc_back: int = 120,
                 esc_width: int = 10, esc_horizon: int = 36, item_cost: float = 40.0,
                 ninpo_cost: float = 3.0, ninpo_floor: int = 0):
        self.emu, self.seg, self.log = emu, seg, log
        self.r = _rules(rules)
        self.history = [norm(x) for x in history]
        self.weights = weights or {}
        self.step, self.width, self.horizon, self.back = step, width, horizon, back
        self.hp_cost, self.max_frames, self.extra_dirs = hp_cost, max_frames, extra_dirs
        self.sync_window = sync_window
        self.beam_back = beam_back
        self.edit_depth = edit_depth
        self.verbose = verbose
        seg.tol_x, seg.tol_y = tol_x, tol_y
        self.esc_lag, self.esc_back, self.esc_width, self.esc_horizon = esc_lag, esc_back, esc_width, esc_horizon
        self.item_cost = item_cost
        self.ninpo_cost = ninpo_cost
        self.ninpo_floor = ninpo_floor
        self.stats = {"beam_calls": 0, "beam_frames": 0, "follow_frames": 0, "resyncs": 0}

    def _penalty(self, s, rs) -> float:
        """frames-equivalent cost of being worse off than the reference: HP below it (hp_cost per point), the
        reference's sub-weapon missing (item_cost), ninpo below it (ninpo_cost per point)"""
        pen = self.hp_cost * max(0, rs.get("hp", 0) - s.get("hp", 0))
        if rs.get("item") and s.get("item") != rs.get("item"):
            pen += self.item_cost
        pen += self.ninpo_cost * max(0, rs.get("ninpo", 0) - s.get("ninpo", 0))
        pen += 30.0 * max(0, self.ninpo_floor - s.get("ninpo", 0))   # absolute floor (e.g. 10 for the next boss)
        return pen

    def _desired(self, j0: int, n: int) -> list:
        """legal projection of the reference rows from reference index j0 (n rows), after the committed rows"""
        src = list(self.seg.rows[max(0, j0):max(0, j0) + n])
        if j0 < 0:
            src = [self.seg.rows[0]] * min(n, -j0) + src
        src = src[:n]
        if len(src) < n:
            src = src + [src[-1] if src else ()] * (n - len(src))
        w = {(b, i - j0): v for (b, i), v in self.weights.items() if j0 <= i < j0 + n}
        return enforce(src, self._all[-1900:], w, rules=self.r)

    # ---------------------------------------------------------------- main loop
    def _commit(self, rows, every: int = 16):
        """play rows from the emulator's state, append them, keep a checkpoint every `every` frames"""
        emu = self.emu
        i = 0
        while i < len(rows):
            idx = len(self.out)
            nxt = (idx // every + 1) * every
            part = rows[i:i + (nxt - idx)]
            self._last = play(emu, part, chunk=max(1, len(part)))[-1]
            for r in part:
                self.leg.push(r)
            self.out += part
            self._all += part
            i += len(part)
            if len(self.out) % every == 0:
                self._ck[len(self.out)] = (emu.msave(), self._last)
        for k in [k for k in self._ck if k < len(self.out) - 480]:
            emu.mfree(self._ck.pop(k)[0])

    def _truncate(self, n: int):
        """drop committed rows after index n (a checkpoint index); the emulator is put at that checkpoint"""
        emu = self.emu
        sid, last = self._ck[n]
        cut = len(self.out) - n
        if cut:
            self.out = self.out[:n]
            self._all = self._all[:len(self._all) - cut]
        self.leg = Legality(self._all, self.r)
        for k in [k for k in self._ck if k > n]:
            emu.mfree(self._ck.pop(k)[0])
        emu.mload(sid)
        self._last = last

    def solve(self, done: Callable, start_index: int = 0, prefix=(), dump: Optional[str] = None):
        """prefix: rows to commit first without checks (resume a dumped partial solution; start_index is then
        re-estimated). dump: path of an inputs file rewritten with the committed rows after every repair."""
        self._dump = dump
        self._prefix = [norm(r) for r in prefix]
        return self._solve(done, start_index)

    def _solve(self, done: Callable, start_index: int = 0):
        emu = self.emu
        from .mode import TICKS
        emu.tick(TICKS)
        emu.trace(False)
        self._all = list(self.history)
        self.out = []
        self.leg = Legality(self.history, self.r)
        self._last = emu.state()
        self._ck = {0: (emu.msave(), self._last)}
        self.delta = start_index   # reference index = our index + delta  (our index = len(self.out))
        n_ref = len(self.seg.ref)
        if self._prefix:
            self._commit(self._prefix)
            hint = len(self.out) - 1 + self.delta
            m = self.seg.match(self._last, hint - 40, hint + 40)
            if m is None:
                j, dist = self.seg.progress_nearest(self._last, hint, back=60, ahead=60)
                m = j if dist < 30 else hint
            self.delta = m + 1 - len(self.out)
            self.log(f"  prefix: {len(self._prefix)} rows committed, delta {self.delta}")
        try:
            while True:
                i = len(self.out)
                if i > self.max_frames:
                    raise RuntimeError("Repair: max_frames exceeded")
                j0 = i + self.delta
                chunk = 120
                want = self._desired(j0, chunk)
                sid = emu.msave()
                tr = play(emu, want, chunk=chunk)
                k, fin = len(tr), False
                prev = self._last
                for q, s in enumerate(tr):
                    if done(prev, s):
                        k, fin = q, True
                        break
                    prev = s
                    j = j0 + q
                    if j >= n_ref or not self.seg.same(s, self.seg.ref[j]):
                        k = q
                        break
                emu.mload(sid)
                emu.mfree(sid)
                if fin:
                    self._commit(want[:k + 1])
                    self.stats["follow_frames"] += k + 1
                    return self.out, {"stats": self.stats, "delta_end": self.delta}
                keep = k if k == len(tr) else max(0, k - self.back)
                if keep:
                    self._commit(want[:keep])
                    self.stats["follow_frames"] += keep
                if k == len(tr):
                    continue
                if self._repair(k - keep, done):
                    return self.out, {"stats": self.stats, "delta_end": self.delta}
        finally:
            for sid, _ in self._ck.values():
                try:
                    emu.mfree(sid)
                except Exception:
                    pass
            self._ck = {}

    def _repair(self, d0: int, done: Callable) -> bool:
        """divergence d0 frames after the current point. Tries near edits, then the step beam from a checkpoint
        up to beam_back frames back, then (if the beam still loses > esc_lag frames) a wider, longer beam from
        up to esc_back frames back. Commits the best (done > stable sync with the least lag > best progress)."""
        emu = self.emu
        i_r = len(self.out)
        delta = self.delta
        cur_lag = -delta
        sid_r = emu.msave()
        last_r = self._last
        hist_r = self._all[-1900:]
        orig = list(self.out)
        T = i_r                                   # the committed rows are cut back to T (emulator lost above it)
        options = []
        base = self._desired(i_r + delta, d0 + 48)
        res = self._edit_search(sid_r, base, i_r, delta, d0, done, last_r, hist_r, lo=d0 - 14, hi=d0 + 8,
                                depth=self.edit_depth)
        options.append(("near", i_r, res))

        def good(r):
            return r.get("done") or (r.get("stable") and r["lag"] <= cur_lag)

        def rank(o):
            r = o[2]
            if r.get("done"):
                return (-1e9, 0)
            if r.get("stable"):
                return (r["lag"] + r.get("pen", 0.0), 0)
            return (r.get("score", 1e9) + 1.0, 1)

        def run_beam(back, width, horizon, min_idx, tag):
            nonlocal T
            cks = [c for c in self._ck if max(i_r - back, getattr(self, "_floor", 0)) <= c <= T]
            c = min(cks) if cks else T
            if c < T:
                self._truncate(c)
                T = c
            elif T == i_r:
                emu.mload(sid_r)
            else:
                self._truncate(T)
            rows_b, info = self._beam(self.leg.copy(), c, delta, done, width=width, horizon=horizon,
                                      min_idx=min_idx)
            r = {"rows": rows_b, "done": info["done"], "synced": info["synced"], "j": info["j"],
                 "lag": info["lag"], "stable": info["synced"] is not None, "score": info["score"],
                 "pen": max(0.0, info["score"] - info["lag"] + 0.5) if info["synced"] is not None else 0.0,
                 "edits": [tag]}
            options.append((tag, c, r))
            return r
        if not good(res):
            r1 = run_beam(self.beam_back, self.width, self.horizon, i_r + d0, "beam")
            best_now = min(options, key=rank)[2]
            lag_now = best_now["lag"] if best_now.get("stable") else best_now.get("score", 1e9)
            if not best_now.get("done") and lag_now - cur_lag > self.esc_lag:
                run_beam(self.esc_back, self.esc_width, self.esc_horizon, i_r + d0 + 5, "beam2")
        kind, at, best = min(options, key=rank)
        if T < i_r:
            self._truncate(T)
        else:
            emu.mload(sid_r)
        emu.mfree(sid_r)
        rows = orig[T:at] + best["rows"]
        self._commit(rows)
        if not best.get("done") and len(self.out) <= i_r + d0 + 2:
            # no progress past the divergence: walk on with the beam from here (no rewind)
            self._no_progress = getattr(self, "_no_progress", 0) + 1
            rows_w, info_w = self._beam(self.leg.copy(), len(self.out), self.delta if best.get("synced") is None
                                        else best["synced"] + 1 - len(self.out), done,
                                        min_idx=len(self.out) + 4 * self.step)
            if not rows_w and self._no_progress > 3:
                raise RuntimeError(f"Repair stuck at row {len(self.out)}: every continuation dies or stalls")
            self._commit(rows_w)
            rows = rows + rows_w
            best = {"done": info_w["done"], "synced": info_w["synced"], "j": info_w["j"],
                    "lag": info_w["lag"], "stable": info_w["synced"] is not None, "score": info_w["score"],
                    "edits": (best.get("edits") or []) + ["walk"]}
            kind = kind + "+walk"
        self._floor = len(self.out)          # later repairs never rewind past this point (no loops)
        if best.get("done"):
            self.log(f"  repair {kind}@{at}: done, edits {best.get('edits')}")
            return True
        n_now = len(self.out)
        if best.get("synced") is not None:
            self.delta = best["synced"] + 1 - n_now
            self.stats["resyncs"] += 1
        else:
            self.delta = best["j"] + 1 - n_now
        self.stats[kind] = self.stats.get(kind, 0) + 1
        if self._dump:
            from .inputs import write_inputs
            write_inputs(self._dump, self.out, "partial Repair solution (rows from the start state)")
        self.log(f"  repair {kind}@{at} (diverged @{i_r + d0}): +{len(rows)} rows, stable={bool(best.get('stable'))} "
                 f"lag {cur_lag} -> {-self.delta}, edits {best.get('edits')}; options "
                 + ", ".join(f"{k}@{a}:{'done' if r.get('done') else (r['lag'] if r.get('stable') else round(r.get('score', 0), 1))}"
                             for k, a, r in options))
        return False

    # ---------------------------------------------------------------- edit search
    def _edits(self, base, d, i_r, delta, lo, hi):
        """single edits of the window rows `base` (base[0] = our index i_r) around the divergence d"""
        out = []
        n = len(base)
        lo, hi = max(0, lo), min(n - 1, hi)
        for b in ("A", "B", "Left", "Right", "Up", "Down"):
            for s, e in _runs(base, b):
                if e < lo or s > hi:
                    continue
                for sh in (-3, -2, -1, 1, 2, 3):
                    out.append(("shift", b, s, e, sh))
                out.append(("drop", b, s, e, 0))
                if e - s >= 3:
                    out.append(("trim", b, s, e, 0))
                for x in (1, 2):
                    out.append(("ext", b, s, e, x))
        for f in range(max(lo, d - 8), min(n - 2, d + 6)):
            for b in ("A", "B"):
                if b not in base[f]:
                    out.append(("add", b, f, f + 2, 0))
        for p in range(max(lo, d - 8), min(n, d + 4), 2):
            for sh in (1, 2, 3, -1):
                out.append(("time", None, p, n, sh))
        for f in range(max(lo, d - 10), min(n - 1, d + 6)):
            j = i_r + delta + f
            if 0 <= j < len(self.seg.raw):
                r = set(self.seg.raw[j])
                for a, c in OPPOSING:
                    if a in r and c in r:
                        for keep in (a, c, None):
                            out.append(("dir", keep, f, min(n, f + 2), (a, c)))
        return out

    def _apply(self, base, ed, i_r, delta):
        kind, b, s, e, x = ed
        rows = [set(r) for r in base]
        n = len(rows)
        if kind == "shift":
            for f in range(s, e):
                rows[f].discard(b)
            for f in range(max(0, s + x), min(n, e + x)):
                rows[f].add(b)
        elif kind == "drop":
            for f in range(s, e):
                rows[f].discard(b)
        elif kind == "trim":
            rows[e - 1].discard(b)
        elif kind == "ext":
            for f in range(e, min(n, e + x)):
                rows[f].add(b)
        elif kind == "add":
            for f in range(s, min(n, e)):
                rows[f].add(b)
        elif kind == "time":
            tail = self._desired_raw(i_r + delta + s - x, n - s)
            rows = rows[:s] + [set(r) for r in tail]
        elif kind == "dir":
            a, c = x
            for f in range(s, e):
                rows[f].discard(a)
                rows[f].discard(c)
                if b:
                    rows[f].add(b)
        return [norm(r) for r in rows]

    def _desired_raw(self, j0, n):
        src = list(self.seg.rows[max(0, j0):max(0, j0) + n])
        if j0 < 0:
            src = [self.seg.rows[0]] * min(n, -j0) + src
        src = src[:n]
        if len(src) < n:
            src = src + [src[-1] if src else ()] * (n - len(src))
        return src

    def _follow_ok(self, m: int, hist, n: int = 24) -> bool:
        """from the emulator's state (synced to reference index m): does the projected reference stay in sync?"""
        src = list(self.seg.rows[m + 1:m + 1 + n + 6])
        if len(src) < n:
            return True
        want = enforce(src, hist[-1900:], rules=self.r)[:n]
        tr = play(self.emu, want, chunk=n)
        for q, s in enumerate(tr):
            if m + 1 + q >= len(self.seg.ref):
                return True
            if not self.seg.same(s, self.seg.ref[m + 1 + q]):
                return False
        return True

    def _eval(self, sid, rows, i_r, delta, d, done, last0, hist):
        """play rows from sid; -> dict. key: smaller = better ((0,..) done, (1, lag) stable sync, (2, score))"""
        emu = self.emu
        emu.mload(sid)
        rows = _final_fix(rows, hist, self.r)
        tr = play(emu, rows, chunk=len(rows))
        prev = last0
        lives0 = last0.get("lives", 0)
        n_ref = len(self.seg.ref)
        for t, s in enumerate(tr):
            if (s.get("dead", 0) & 0x80) or s.get("dw") or s.get("lives", 0) < lives0:
                return {"key": (3, 0, 0), "rows": rows, "why": "death", "score": 1e9}
            if done(prev, s):
                return {"key": (0, t, 0), "rows": rows[:t + 1], "done": True, "synced": None, "t": t, "score": -1e9}
            prev = s
            if t >= d - 1 and t + 2 < len(tr):
                hint = i_r + delta + t
                m = self.seg.match(s, hint - 40, hint + 40)
                if m is not None and m + 2 < n_ref and self.seg.same(tr[t + 1], self.seg.ref[m + 1]):
                    lag = (i_r + t) - m
                    emu.mload(sid)
                    play(emu, rows[:t + 1], chunk=t + 1)
                    stable = self._follow_ok(m, list(hist) + rows[:t + 1])
                    if stable:
                        pen = self._penalty(s, self.seg.ref[m])
                        return {"key": (1, lag + pen, t), "rows": rows[:t + 1], "synced": m, "t": t, "lag": lag,
                                "stable": True, "score": float(lag + pen), "pen": pen}
                    break
        s = tr[-1]
        hint = i_r + delta + len(tr) - 1
        j, dist = self.seg.progress(s, hint)
        rs = self.seg.ref[min(j, n_ref - 1)]
        lag = (i_r + len(tr) - 1) - j
        sc = lag + dist / 1.5 + self._penalty(s, rs)
        return {"key": (2, sc, 0), "rows": rows, "synced": None, "j": j, "lag": lag, "score": sc}

    def _edit_search(self, sid, base, i_r, delta, d, done, last0, hist, lo, hi, depth=2, width=4):
        cur_lag = -delta
        best = self._eval(sid, base, i_r, delta, d, done, last0, hist)
        best["edits"] = []
        frontier = [(best, base, [])]
        evals = 1
        for lvl in range(depth):
            cand = []
            for res0, rows0, eds0 in frontier:
                for ed in self._edits(rows0, d, i_r, delta, lo, hi):
                    rows = self._apply(rows0, ed, i_r, delta)
                    res = self._eval(sid, rows, i_r, delta, d, done, last0, hist)
                    evals += 1
                    res["edits"] = eds0 + [ed]
                    cand.append((res, rows, eds0 + [ed]))
                    if res["key"] < best["key"]:
                        best = res
                    if res["key"][0] == 0 or (res["key"][0] == 1 and res["key"][1] <= cur_lag):
                        self.stats["edit_evals"] = self.stats.get("edit_evals", 0) + evals
                        return res
            cand.sort(key=lambda c: c[0]["key"])
            frontier = [c for c in cand if c[0]["key"][0] < 3][:width]
        self.stats["edit_evals"] = self.stats.get("edit_evals", 0) + evals
        return best

    def _cands(self, node: Node, j_hint: int) -> list:
        """legal macro candidates (lists of `step` rows) from node"""
        leg = node.leg
        n = self.step
        cands = []
        hist = (self._all + node.rows)[-1900:]
        for off in (1, 2):
            a = max(0, j_hint + off)
            src = list(self.seg.rows[a:a + n + 6])
            if len(src) < n + 6:
                src = src + [()] * (n + 6 - len(src))
            cands.append(src[:n])
            cands.append(enforce(src, hist, rules=self.r)[:n])
        near = self.seg.rows[max(0, j_hint - 30):j_hint + 30]
        h = 2
        pats = ["R" * n, "L" * n, "-" * n, "L" * h + "R" * (n - h), "R" * h + "L" * (n - h),
                "-" * h + "R" * (n - h), "-" * h + "L" * (n - h)]
        if self.extra_dirs:
            if any("Up" in r for r in near):
                pats.append("U" * n)
            if any("Down" in r for r in near):
                pats.append("D" * n)
        use_b = any("B" in r for r in near)
        amap = {"R": "Right", "L": "Left", "U": "Up", "D": "Down"}
        specs = [(p, a, None) for p in pats for a in (None, 0)]
        if use_b:
            specs += [(p, None, 0) for p in ("R" * n, "L" * n, "-" * n)]
        for pat, a, b in specs:
            rows = []
            for f in range(n):
                row = set()
                if pat[f] in amap:
                    row.add(amap[pat[f]])
                if a is not None and a <= f < a + 2:
                    row.add("A")
                if b is not None and b <= f < b + 2:
                    row.add("B")
                rows.append(tuple(row))
            cands.append(rows)
        # wall climb cycles (cling, hold exactly A+away to jump off, come back at drift speed)
        cands.append([("Left", "A"), ("Left", "A")] + [("Right",)] * (n - 2))
        cands.append([("Right", "A"), ("Right", "A")] + [("Left",)] * (n - 2))
        # corner / pole jump-off: step away and back into it with A held (the TAS's "L+A, R+A")
        cands.append([("Left", "A"), ("Left", "A")] + [("Right", "A")] * (n - 3) + [("Right",)])
        cands.append([("Right", "A"), ("Right", "A")] + [("Left", "A")] * (n - 3) + [("Left",)])
        cands.append([("Left",), ("Left",)] + [("Right", "A")] * (n - 3) + [("Right",)])
        cands.append([("Right",), ("Right",)] + [("Left", "A")] * (n - 3) + [("Left",)])
        seen = set()
        out = []
        for c in cands:
            lg = leg.copy()
            fixed = []
            for row in c:
                row = resolve_opposing([row])[0]
                if not lg.can(row):
                    row = lg.fix(row)
                lg.push(row)
                fixed.append(row)
            key = tuple(fixed)
            if key not in seen:
                seen.add(key)
                out.append((fixed, lg))
        return out

    def _stable(self, node: Node, n: int = 24) -> bool:
        """does following the reference from this synced node stay in sync for n frames?"""
        emu = self.emu
        emu.mload(node.sid)
        j = node.synced
        src = list(self.seg.rows[j + 1:j + 1 + n + 6])
        if len(src) < n:
            return True
        want = enforce(src, (self._all + node.rows)[-1900:], rules=self.r)[:n]
        tr = play(emu, want, chunk=n)
        for q, s in enumerate(tr):
            if j + 1 + q >= len(self.seg.ref):
                return True
            if not self.seg.same(s, self.seg.ref[j + 1 + q]):
                return False
        return True

    def _beam(self, leg: Legality, i0: int, delta: int, done: Callable, width: Optional[int] = None,
              horizon: Optional[int] = None, min_idx: int = 0):
        """Beam search from the emulator's current state (our index i0). Returns (rows, info); the emulator is
        left at the end of the returned rows."""
        emu = self.emu
        root = Node(emu.msave(), leg.copy(), [], emu.state())
        root.j = i0 + delta - 1          # reference index of the CURRENT state
        beam = [root]
        best_done = None
        all_sids = [root.sid]
        n_ref = len(self.seg.ref)
        lives0 = root.last.get("lives", 0)
        width = width or self.width
        horizon = horizon or self.horizon
        for depth in range(horizon):
            children = []
            seen = {}
            for node in beam:
                for rows, lg in self._cands(node, node.j):
                    emu.mload(node.sid)
                    tr = play(emu, rows, chunk=len(rows))
                    self.stats["beam_frames"] += len(rows)
                    if any((s.get("dead", 0) & 0x80) or s.get("dw") for s in tr) or tr[-1].get("lives", 0) < lives0:
                        continue
                    ch = Node(None, lg, node.rows + rows, tr[-1])
                    fin_at = next((q for q, s in enumerate(tr) if done(tr[q - 1] if q else node.last, s)), None)
                    if fin_at is not None:
                        ch.rows = node.rows + rows[:fin_at + 1]
                        ch.done = i0 + len(ch.rows)
                        ch.lag, ch.score, ch.j = 0.0, float(ch.done - i0), n_ref - 1
                        if best_done is None or ch.done < best_done.done:
                            best_done = ch
                        continue
                    idx = i0 + len(ch.rows) - 1          # our index of the state after these rows
                    hint = node.j + len(rows)
                    m = self.seg.match(tr[-1], hint - self.sync_window, hint + self.sync_window)
                    if m is not None:
                        ch.synced, ch.j, dist = m, m, 0.0
                    else:
                        ch.j, dist = self.seg.progress(tr[-1], hint)
                    rs = self.seg.ref[min(ch.j, n_ref - 1)]
                    ch.hp = tr[-1].get("hp", 0)
                    ch.lag = idx - ch.j
                    ch.score = ch.lag + dist / 1.5 + self._penalty(tr[-1], rs) - (0.5 if ch.synced is not None else 0.0)
                    sg = _sig(tr[-1]) + (tr[-1].get("anim"), tr[-1].get("vx"), tr[-1].get("vx_sub"))
                    if sg in seen and seen[sg].score <= ch.score:
                        continue
                    ch.sid = emu.msave()
                    all_sids.append(ch.sid)
                    seen[sg] = ch
                    children.append(ch)
            if not children:
                break
            children.sort(key=lambda c: c.score)
            beam = children[:width]
            if self.verbose:
                self.log(f"    beam depth {depth}: {len(children)} children, best score {beam[0].score:.1f} "
                         f"lag {beam[0].lag} j {beam[0].j} y {beam[0].last.get('y')} X "
                         f"{beam[0].last.get('scroll_scr', 0) * 256 + beam[0].last.get('scroll', 0)} rows "
                         f"{'|'.join('+'.join(r) for r in beam[0].rows[-self.step:])}")
            if best_done is not None:
                # finishing beats any open node that cannot finish earlier (an open node needs >= 1 more frame)
                if all(i0 + len(c.rows) + 1 >= best_done.done for c in beam):
                    break
            if beam[0].synced is not None and depth >= 1 and i0 + len(beam[0].rows) >= min_idx:
                if self._stable(beam[0]):
                    break
                for c in beam:
                    if c.synced is not None and c is not beam[0]:
                        continue
                beam[0].synced = None
                beam[0].score += 1.0
        pick = best_done if best_done is not None else min(beam, key=lambda c: c.score)
        emu.mload(root.sid)
        if pick.rows:
            pick.last = play(emu, pick.rows)[-1]
        for sid in all_sids:
            try:
                emu.mfree(sid)
            except Exception:
                pass
        last = pick.last if pick.rows else root.last
        info = {"done": pick.done is not None, "synced": pick.synced, "j": pick.j, "lag": pick.lag,
                "score": pick.score, "hp": pick.hp, "last": last}
        return pick.rows, info


# ------------------------------------------------------------------------------------------- record waypoints
# (round 2, 2026-10-19) The record holder's route as a reference: per-frame (room, X, y) of Ryu taken from the record
# video (work/a12r2/rtrace.py -> work/a12r2/rec/rNN.json, method of agent a56: room = black screens, X = background
# scroll since the room start + Ryu's screen x, y = Ryu's screen y). Coordinates are RAM coordinates after
# calibration (X: the TAS's scroll at the room's first play frame + the record's cumulative scroll + screen x + xoff;
# y: screen y + yoff; xoff/yoff fitted on the first frames of the stage where both stand on the ground).
# waypoint_ref() turns it into a beam reference (frame k = start frame + NES frames after the record's control):
# positions from the record, rows / hp / ninpo / item from the TAS at a time-warped TAS frame (the TAS frame whose
# position best matches the record's at that point, monotone), so where the two routes agree the legalized TAS rows
# are still offered as candidates. Used by ng/stages/a12r2_solve.py with the a56 StageBeam (progress = the largest
# k - 0.75 |dX| - 0.5 |dy| near the node's pointer, i.e. "lag vs the record").

def _signed(v):
    return v - 256 if v >= 128 else v


def _absx(d) -> int:
    return _signed(d.get("scroll_scr", 0)) * 256 + d.get("scroll", 0) + d.get("x", 0)


class Waypoints:
    """The record's route in one stage. pts = [(t, room, X, y)] (t = NES frames after the record's control)."""

    def __init__(self, rec_json, stage: int, tas: Optional["TasRef"] = None, xoff=None, yoff=None, min_n: int = 12,
                 room_ids=None, left_shift: int = 7):
        import json as _json
        rec = _json.loads(Path(rec_json).read_text())["rows"]
        self.stage = stage
        self.tas = tas or TasRef()
        T = self.tas
        c = T.control(stage)
        nxt = T.load(stage + 1) or len(T.tr)
        self.tas_c, self.tas_end = c, nxt
        # TAS rooms of this stage in order, with the scroll at the room's first play frame
        rooms, starts = [], {}
        prev = None
        for k in range(c, nxt):
            d = T.at(k)
            if d["room"] != prev:
                rooms.append(d["room"])
                starts[d["room"]] = k if k == c else k + 23
                prev = d["room"]
        self.rooms = room_ids or rooms
        self.s0 = {r: _signed(T.at(starts[r])["scroll_scr"]) * 256 + T.at(starts[r])["scroll"] for r in rooms}
        # camera rule: while the background scrolls the camera keeps Ryu near the screen centre, so a detection
        # far from it (a scrolling sign or an enemy; Ryu himself can be off the top of the screen, e.g. 1-1's roof
        # jumps) is replaced by the centre (x 129) with y interpolated from the neighbours.
        rec = [dict(r) for r in rec if r["t"] >= 0 and r["room"] < len(self.rooms)]
        for i, r in enumerate(rec):
            pr = rec[i - 1] if i else None
            moving = pr is not None and pr["room"] == r["room"] and abs(r["scroll"] - pr["scroll"]) >= 2
            good = r.get("sx") is not None and r["n"] >= min_n
            if moving and not (good and 112 <= r["sx"] <= 150):
                r["sx"], r["sy"], r["n"] = 129, None, min_n
        for i, r in enumerate(rec):
            if r.get("sx") is not None and r.get("sy") is None:
                a = next((q for q in reversed(rec[:i]) if q["room"] == r["room"] and q.get("sy") is not None
                          and q["n"] >= min_n), None)
                b = next((q for q in rec[i + 1:] if q["room"] == r["room"] and q.get("sy") is not None
                          and q["n"] >= min_n), None)
                if a and b:
                    u = (r["t"] - a["t"]) / max(1e-6, b["t"] - a["t"])
                    r["sy"] = round(a["sy"] + u * (b["sy"] - a["sy"]))
                else:
                    r["sy"] = (a or b or {"sy": 150})["sy"]
        raw = [r for r in rec if r.get("sx") is not None and r["n"] >= min_n]
        # calibration on the first 60 frames (both on the ground: TAS y and record y nearly constant)
        if xoff is None or yoff is None:
            dx, dy = [], []
            for r in raw:
                if r["t"] > 60 or r["room"] != 0:
                    continue
                d = T.at(c + int(round(r["t"])))
                dx.append(_absx(d) - (self.s0[self.rooms[0]] + r["scroll"] + r["sx"]))
                dy.append(d["y"] - r["sy"])
            def _mode(v, dflt):                 # the most common offset (+-1): ground frames, not jumps
                if not v:
                    return dflt
                return max(set(v), key=lambda a: sum(1 for b in v if abs(b - a) <= 1))
            xoff = _mode(dx, 0) if xoff is None else xoff
            yoff = _mode(dy, 9) if yoff is None else yoff
        self.xoff, self.yoff = xoff, yoff
        # Ryu's sprite is not symmetric: the tracked centre sits ~7 px further left (relative to RAM x) when he
        # faces left (1-1/2-1 start, facing right: -1..0; 2-2 start, facing left: -8). Facing = sign of the
        # tracked motion over +-3 images (kept while standing still); xoff applies to the calibration's facing.
        raw_x = [self.s0[self.rooms[r["room"]]] + r["scroll"] + r["sx"] for r in raw]
        face, faces = 1, []
        for i, r in enumerate(raw):
            j0, j1 = max(0, i - 3), min(len(raw) - 1, i + 3)
            if raw[j0]["room"] == raw[j1]["room"] == r["room"]:
                v = raw_x[j1] - raw_x[j0]
                if v >= 3:
                    face = 1
                elif v <= -3:
                    face = -1
            faces.append(face)
        f_cal = next((f for r, f in zip(raw, faces) if r["room"] == 0 and r["t"] > 3), 1)
        self.left_shift = left_shift
        def _fx(f):
            return 0 if f == f_cal else (left_shift if f == 1 else -left_shift)
        pts = [(r["t"], self.rooms[r["room"]], rx + xoff + _fx(f), r["sy"] + yoff)
               for r, rx, f in zip(raw, raw_x, faces)]
        clean = pts[:1]
        for p in pts[1:]:                       # drop tracking outliers (> 12 px per frame from the last point)
            q = clean[-1]
            if p[1] == q[1] and abs(p[2] - q[2]) + abs(p[3] - q[3]) > 12 * max(1.0, p[0] - q[0]):
                continue
            clean.append(p)
        # the record stands still at a room's exit while the screen fades (e.g. 2-1 room 4, t 1984-2016): drop
        # those trailing points so the reference does not reward waiting there
        keep = []
        for i, p in enumerate(clean):
            nxt_room = next((q[1] for q in clean[i + 1:] if q[1] != p[1]), None)
            last_in_room = [q for q in clean[i:] if q[1] == p[1]]
            if nxt_room is not None and len(last_in_room) > 1 and all(
                    abs(q[2] - p[2]) + abs(q[3] - p[3]) <= 2 for q in last_in_room):
                if keep and keep[-1][1] == p[1] and abs(keep[-1][2] - p[2]) + abs(keep[-1][3] - p[3]) <= 2:
                    continue
            keep.append(p)
        clean = keep
        self.pts = clean
        self.tend = int(clean[-1][0]) if clean else 0

    def at(self, t: float) -> tuple:
        """(room, X, y) at record time t (linear between tracked images of the same room)."""
        P = self.pts
        lo, hi = 0, len(P) - 1
        while lo < hi:
            m = (lo + hi + 1) // 2
            if P[m][0] <= t:
                lo = m
            else:
                hi = m - 1
        p = P[lo]
        q = P[lo + 1] if lo + 1 < len(P) else p
        if q[1] == p[1] and q[0] > p[0] and t >= p[0]:
            u = (t - p[0]) / (q[0] - p[0])
            return p[1], round(p[2] + u * (q[2] - p[2])), round(p[3] + u * (q[3] - p[3]))
        return p[1], p[2], p[3]

    def time_map(self, max_adv: int = 3) -> list:
        """tmap[t] = TAS frame matched to record time t: dynamic time warping (TAS frame advances 0..max_adv per
        record frame), cost |dX| + 0.5 |dy| (+1000 in another room)."""
        import numpy as np
        T = self.tas
        ks = list(range(self.tas_c, self.tas_end))
        K = len(ks)
        troom = np.array([T.at(k)["room"] for k in ks])
        tx = np.array([_absx(T.at(k)) for k in ks], dtype=float)
        ty = np.array([T.at(k)["y"] for k in ks], dtype=float)
        n = self.tend + 1
        D = np.full(K, 1e18)
        D[0] = 0.0
        back = np.zeros((n, K), dtype=np.int8)
        for t in range(n):
            room, X, y = self.at(t)
            cost = np.abs(tx - X) + 0.5 * np.abs(ty - y) + 1000.0 * (troom != room)
            if t == 0:
                D = np.full(K, 1e18)
                D[0] = cost[0]
                continue
            best = D.copy()
            arg = np.zeros(K, dtype=np.int8)
            for a in range(1, max_adv + 1):
                sh = np.full(K, 1e18)
                sh[a:] = D[:-a]
                m = sh < best
                best[m] = sh[m]
                arg[m] = a
            D = best + cost
            back[t] = arg
        k = int(np.argmin(D))
        out = [0] * n
        for t in range(n - 1, -1, -1):
            out[t] = ks[k]
            k -= int(back[t][k])
        return out

    def columns(self, step: int = 64) -> dict:
        """{(room, X // step): first record time} (progress table, same buckets as work/a56r2/cmp_route.py)."""
        out = {}
        for t, room, X, y in self.pts:
            out.setdefault((room, int(X) // step), t)
        return out


def waypoint_ref(wp: Waypoints, f0: int, name: str = "record", hp_from_tas: bool = True) -> dict:
    """A StageBeam reference (ng/stages/a56_beam.py format: rows / trace indexed by absolute frame, control, load_next)
    that follows the record's route in record time, starting at our start frame f0 (= the record's control)."""
    tm = wp.time_map()
    T = wp.tas
    rows = [()] * f0
    trace = [None] * f0
    for t in range(wp.tend + 1):
        room, X, y = wp.at(t)
        d = T.at(tm[t])
        rows.append(T.rows[tm[t]] if tm[t] < len(T.rows) else ())     # the row that leads from tm[t] to tm[t]+1
        trace.append({"frame": f0 + t, "stage": wp.stage, "room": room, "x": 0, "xsub": 0, "y": y,
                      "scroll": X % 256, "scroll_scr": (X // 256) % 256, "hp": d["hp"] if hp_from_tas else 0,
                      "ninpo": d["ninpo"], "item": d["item"], "bosshp": d.get("bosshp", 16),
                      "boss_real": d.get("boss_real", 16), "timer": d.get("timer", 0), "subtimer": d.get("subtimer", 0),
                      "tas_frame": tm[t]})
    trace[f0]["frame"] = f0
    return {"name": name, "rows": rows, "trace": trace, "control": f0, "load_next": f0 + wp.tend + 1, "tmap": tm}


def banned_tas_frames(tas: "TasRef", k0: int, k1: int, ud: bool = False) -> list:
    """TAS frames in [k0, k1) whose row moves Ryu in a way a legal row cannot copy: L+R anywhere, U+D with a
    direction while airborne (only with ud=True: measured harmless in 2-1 room 2, where the legalized rows
    replay in sync; U+D(+dir) on the ground = plain dir)."""
    out = []
    for k in range(k0, k1):
        r = set(tas.rows[k - 1]) if k - 1 < len(tas.rows) else set()
        if "Left" in r and "Right" in r:
            out.append(k)
        elif ud and "Up" in r and "Down" in r and ("Left" in r or "Right" in r):
            ys = [tas.at(j)["y"] for j in range(k, min(k + 3, len(tas.tr)))]
            if len(set(ys)) > 1:
                out.append(k)
    return out


def hybrid_ref(wp: "Waypoints", f0: int, pad: int = 30, name: str = "hybrid", min_gap: int = 60, ud: bool = False) -> dict:
    """A StageBeam reference that is the TAS (positions, rows, hp/ninpo/item: lazy-followable) except around the
    TAS's banned moves, where the record's route is spliced in (record positions, in record time; rows = the TAS
    rows of the DTW-matched frames). Banned frames (banned_tas_frames) are padded by `pad` and merged when closer
    than `min_gap`. Returns the ref dict plus "segments": [(tas_k_from, tas_k_to, rec_t_from, rec_t_to)]."""
    T = wp.tas
    tm = wp.time_map()
    bad = banned_tas_frames(T, wp.tas_c, wp.tas_end, ud=ud)   # ud=True: also U+D+dir in the air (a12r3)
    segs = []
    for k in bad:
        a, b = max(wp.tas_c, k - pad), min(wp.tas_end - 1, k + pad)
        if segs and a <= segs[-1][1] + min_gap:
            segs[-1][1] = max(segs[-1][1], b)
        else:
            segs.append([a, b])

    def tinv(k):
        for t, kk in enumerate(tm):
            if kk >= k:
                return t
        return len(tm) - 1

    rows = [()] * f0
    trace = [None] * f0
    seginfo = []
    k = wp.tas_c
    si = 0
    while k < wp.tas_end:
        if si < len(segs) and k >= segs[si][0]:
            a, b = segs[si]
            ta, tb = tinv(a), tinv(b + 1)
            seginfo.append((a, b, ta, tb))
            for t in range(ta, max(ta + 1, tb)):
                room, X, y = wp.at(t)
                d = T.at(tm[t])
                rows.append(T.rows[tm[t]] if tm[t] < len(T.rows) else ())
                trace.append({"frame": len(trace), "stage": wp.stage, "room": room, "x": 0, "xsub": 0, "y": y,
                              "scroll": X % 256, "scroll_scr": (X // 256) % 256, "hp": d["hp"], "ninpo": d["ninpo"],
                              "item": d["item"], "bosshp": d.get("bosshp", 16), "boss_real": d.get("boss_real", 16),
                              "timer": d.get("timer", 0), "subtimer": d.get("subtimer", 0), "src": "rec", "rt": t})
            k = b + 1
            si += 1
            continue
        d = dict(T.at(k))
        d["frame"] = len(trace)
        d["src"] = "tas"
        rows.append(T.rows[k] if k < len(T.rows) else ())
        trace.append(d)
        k += 1
    return {"name": name, "rows": rows, "trace": trace, "control": f0, "load_next": len(trace), "segments": seginfo}
