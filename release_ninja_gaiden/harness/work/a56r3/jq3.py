"""Round 3 Jaquio planner (agent a56). Jaquio is deterministic (bank07 $D357: y 96 fixed, x paces 48..208 at
1.5 px/f, two homing fireballs every 120 f), so hits depend only on WHEN Ryu jumps from a pedestal top and which way
he faces. Beam over jump steps:

  step = pre-move pd for w frames (or nothing), jump (A 2 f) with direction f held for k frames (k >= 2 turns Ryu
  toward Jaquio; k large = drift), then nothing; the legal cancel cycle `Down|Down+B|B|-|-` from offset o
  (relative to the jump press). The step ends on landing (>= 8 air frames), on the kill or after 90 frames.

Candidates for a pedestal node are ranked by a geometric model (Jaquio x extrapolated from RAM with the pacing
rule, Ryu's measured straight-jump y profile, hit band |dx| in [B0,B1], Ryu y <= YMAX, facing toward him) and
only the best `--verify` per node are emulated. Floor nodes (approach) are emulated on a coarse grid.
Rows go through the a56 Enforcer (legal by construction).

    python work/a56r3/jq3.py [--width 4] [--verify 10] [--tag t] [--hours 2] [--b0 18 --b1 54 --ymax 124]
Output: states/tmp/a56r3_jaq_<tag>.inputs.txt (rows from tmp/a56r2_64b_control up to the kill frame).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402

START = "tmp/a56r2_64b_control"
HIST = "logs/a56_6-4a_b11.inputs.txt"
AIR = (5, 6, 0x0B)
CYC = [("Down",), ("Down", "B"), ("B",), (), ()]
HOPW = (0,)
OPTS = {"b0": 18.0, "b1": 54.0, "ymax": 124.0, "hpw": 10.0}


def opt(a, n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v)
    return d


def step_rows(pd, w, f, k, o, n=90):
    rows = []
    for _ in range(w):
        rows.append((pd,) if pd else ())
    for i in range(n):
        r = set()
        if i < 2:
            r.add("A")
        if f and i < k:
            r.add(f)
        if i >= o:
            r |= set(CYC[(i - o) % 5])
        rows.append(tuple(sorted(r)))
    return rows


def jaq_path(x, d, n):
    """Jaquio x for the next n frames from x (moving d = +1/-1), pacing rule of $D394 (approximate)."""
    out = []
    for _ in range(n):
        x += 1.5 * d
        if x >= 208 or x < 48:
            d = -d
        out.append(x)
    return out


class Node:
    __slots__ = ("sid", "rows", "frame", "thp", "hp", "x", "y", "en", "score", "jx", "jd", "face", "hits", "anim")


class Planner:
    def __init__(self, tag, width, verify, hours):
        self.tag, self.width, self.verify = tag, width, verify
        self.deadline = time.time() + hours * 3600
        self.e = C.open_emu(f"a56r3_jaq_{tag}.log")
        self.logf = open(P / "logs" / f"a56r3_jaq_{tag}.out", "a")
        self.prof = None          # Ryu y offsets per air frame of a straight pedestal jump
        self.best = None
        self.evals = 0
        self.t0 = time.time()

    def log(self, *a):
        print(*a, flush=True)
        print(*a, file=self.logf, flush=True)

    def setup(self):
        from ng.mode import TICKS
        e = self.e
        e.tick(TICKS)
        F = dict(e.fields)
        F.update(jx=0x467, jy=0x487)
        e.set_fields(F)
        s0 = e.load(START)
        self.f0 = s0["frame"]
        hist = list(read_inputs(P / HIST))[-1700:] + [()] * 151
        r = Node()
        r.en = C.Enforcer(hist)
        r.rows = []
        r.sid = e.msave()
        r.frame, r.thp, r.hp, r.x, r.y = s0["frame"], s0["bosshp"] or 16, s0["hp"], s0["x"], s0["y"]
        tr = C.play_trace(e, [()] * 2)
        r.jx, r.jd = s0["jx"], (1 if tr[-1]["jx"] >= s0["jx"] else -1)
        r.face, r.hits, r.anim = 0, 0, s0["anim"]
        r.score = r.thp * OPTS["hpw"]
        e.mload(r.sid)
        self.log("start", self.f0, "x", r.x, "y", r.y, "hp", r.hp, "boss", r.thp, "J", r.jx, r.jd)
        return r

    def play(self, node, desired):
        """emulate desired rows from node; cut at landing / kill / death. -> child Node or None"""
        e = self.e
        e.mload(node.sid)
        en = node.en.copy()
        rows = [en.emit(w, retry=0) for w in desired]
        tr = C.play_trace(e, rows)
        self.evals += 1
        cut, started, airn = None, False, 0
        for i, s in enumerate(tr):
            if s["hp"] == 0 or (s.get("dead", 0) & 0x80):
                return None, tr
            if s["bosshp"] == 0:
                cut = i
                break
            if s["anim"] in AIR:
                started = True
                airn += 1
            elif started:
                if airn < 8:
                    return None, tr
                cut = i
                break
        if cut is None:
            if not started:
                return None, tr
            cut = len(tr) - 1
        en = node.en.copy()
        rows = [en.emit(w, retry=0) for w in desired[:cut + 1]]
        if cut < len(tr) - 1:
            e.mload(node.sid)
            e.run(rows)
        s = tr[cut]
        n = Node()
        n.rows = node.rows + rows
        n.en = en
        n.frame, n.thp, n.hp, n.x, n.y = s["frame"], s["bosshp"], s["hp"], s["x"], s["y"]
        n.jx = s["jx"]
        n.anim = s["anim"]
        n.jd = 1 if (cut == 0 or tr[cut]["jx"] >= tr[cut - 1]["jx"]) else -1
        n.hits = node.thp - n.thp
        n.sid = None
        return n, tr[:cut + 1]

    def predict(self, node, w, f, o):
        """model: hits and end frame of a straight pedestal jump after waiting w frames, facing f."""
        if self.prof is None:
            return 0, w + 46
        jp = jaq_path(node.jx, node.jd, w + len(self.prof) + 2)
        hits = 0
        face = 1 if f == "Right" else -1
        if face == -1 and OPTS.get("rightonly", 1):
            return 0, w + len(self.prof)   # round-3 calibration: no hit ever measured with Jaquio on Ryu's left
        for i, dy in enumerate(self.prof):
            if i < o or (i - o) % 5 != 1:
                continue
            jx = jp[w + i]
            ry = node.y + dy
            dx = (jx - node.x) * face
            if OPTS["b0"] <= dx <= OPTS["b1"] and ry <= OPTS["ymax"]:
                hits += 1
        return hits, w + len(self.prof)

    def children(self, node):
        kids = []
        on_ped = node.y == 160 and node.anim != 10
        if on_ped and self.prof is not None:
            cands = []
            for w in range(0, 52):
                for f in ("Left", "Right"):
                    for o in range(5):
                        h, L = self.predict(node, w, f, o)
                        if h:
                            cands.append((-(min(h, node.thp) * OPTS["hpw"]) + L, w, f, o, h))
            cands.sort()
            seen = set()
            pick = []
            for c in cands:
                if (c[1], c[2]) in seen:
                    continue
                seen.add((c[1], c[2]))
                pick.append(c)
                if len(pick) >= self.verify:
                    break
            for _, w, f, o, h in pick:
                kids.append(((None, w, f, 2, o), h))
            # also: plain jumps to measure / reposition
            for w in (0, 6):
                for f in ("Left", "Right"):
                    kids.append(((None, w, f, 2, 1), -1))
            # hop to a neighbour pedestal
            for f in ("Left", "Right"):
                for k in (12, 20, 28, 36):
                    for w in HOPW:
                        kids.append(((None, w, f, k, 1 + (w // 4) % 3), -1))
        else:
            for pd in ("Right", "Left", None):
                for w in ((0, 6, 12, 18, 24, 30, 36, 44, 52) if pd else (4, 10)):
                    for k in (2, 10, 16, 22, 28, 34, 90):
                        kids.append(((pd, w, pd or "Right", k, 1), -1))
        return kids

    def run(self):
        root = self.setup()
        beam = [root]
        visited = {}
        for depth in range(40):
            cands = []
            for node in beam:
                for (pd, w, f, k, o), h in self.children(node):
                    if time.time() > self.deadline:
                        break
                    n, tr = self.play(node, step_rows(pd, w, f, k, o))
                    if n is None:
                        continue
                    if pd is None and k == 2 and node.y == 160 and node.anim != 10 and self.prof is None and n.y == 160 and abs(n.x - node.x) <= 6:
                        j0 = next(i for i, s in enumerate(tr) if s["anim"] in AIR) - 1 if any(
                            s["anim"] in AIR for s in tr) else 0
                        self.prof = [s["y"] - node.y for s in tr[w:]]
                        self.log("profile", self.prof)
                    if n.thp == 0:
                        if self.best is None or n.frame < self.best.frame:
                            self.best = n
                            self.log("DONE", n.frame, "t", n.frame - self.f0, "hp", n.hp, "rows", len(n.rows))
                            C.save_rows(P / "states" / "tmp" / f"a56r3_jaq_{self.tag}.inputs.txt", n.rows,
                                        f"a56r3 jaquio kill at {n.frame} (start {self.f0}) hp {n.hp}")
                        continue
                    if self.best and n.frame + n.thp * 5 >= self.best.frame:
                        continue
                    n.score = n.frame - self.f0 + n.thp * OPTS["hpw"] + (25 if n.y != 160 or n.anim == 10 else 0) + \
                        max(0, 16 - n.hp) * 2
                    cell = (n.x // 4, n.y // 8, n.thp, n.frame // 4)
                    if cell in visited:
                        continue
                    visited[cell] = 1
                    n.sid = self.e.msave()
                    cands.append(n)
                    if h >= 0:
                        self.log(f"  d{depth} w{w} {f} o{o} pred {h} got {n.hits} -> t {n.frame - self.f0} "
                                 f"boss {n.thp} x {n.x} y {n.y} hp {n.hp}")
            front, bf = [], 1 << 30
            for n in sorted(cands, key=lambda n: (n.thp, n.frame)):
                if n.frame < bf:
                    front.append(n)
                    bf = n.frame
            nb = sorted(front, key=lambda n: n.score)[:max(1, self.width // 2)]
            for n in sorted(cands, key=lambda n: n.score):
                if len(nb) >= self.width:
                    break
                if n not in nb:
                    nb.append(n)
            for n in cands:
                if n not in nb:
                    self.e.mfree(n.sid)
            beam = nb
            self.log(f"depth {depth} cands {len(cands)} evals {self.evals} {time.time() - self.t0:.0f}s best",
                     [(n.frame - self.f0, n.thp, n.hp, n.x, n.y) for n in beam])
            if beam:
                C.save_rows(P / "states" / "tmp" / f"a56r3_jaq_{self.tag}_partial.inputs.txt", beam[0].rows,
                            f"partial t {beam[0].frame - self.f0} boss {beam[0].thp}")
            if not beam or time.time() > self.deadline:
                break
        return self.best


if __name__ == "__main__":
    a = sys.argv[1:]
    width = opt(a, "--width", 4)
    ver = opt(a, "--verify", 10)
    tag = opt(a, "--tag", "t")
    hours = opt(a, "--hours", 2.0)
    HOPW = tuple(int(v) for v in opt(a, "--hopw", "0").split(","))
    for k in list(OPTS):
        OPTS[k] = opt(a, "--" + k, OPTS[k])
    pl = Planner(tag, width, ver, hours)
    try:
        b = pl.run()
        print("RESULT", None if b is None else (b.frame, b.frame - pl.f0, b.hp))
    finally:
        pl.e.close()
        pl.logf.close()
