"""Acts 3-4: TAS-guided beam search with legal input. Owned by the Acts 3-4 agent.

    python ng/stages/a34_beam.py <stage> [--start state] [--prefix name] [--W 10] [--K 2] [--out name]
                                 [--until-room R] [--hist name] [--max-steps N]

Each node is an emulator state reached with legal rows (a34_core.Legal). Every step expands each node by a set of
K-frame actions: "follow the TAS" (the TAS's rows from the TAS frame that matches the node's position), and
primitive moves (run, jump, slash, throw, turn, wait), all made legal frame by frame (greedy_legal). A node's
position (room, world x, y) is matched to the TAS trajectory: g = matching TAS frame, lateness = t - g + dist/1.5.
The beam keeps the W nodes with the lowest lateness (+ a small HP penalty), deduplicated by game state.
The search stops when a node reaches the next stage ($6D changes): the first one is the answer.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402

R = lambda *a: tuple(a)  # noqa: E731
import os  # noqa: E402
NOTHROW = os.environ.get("A34_NOTHROW", "") == "1"   # round 2: never throw a sub-weapon (save ninpo for 3-3)
# round 3: drop the TAS's throws only inside these TAS frame ranges ("10320-10350,10480-10510")
NOTHROW_RANGES = [tuple(int(v) for v in x.split("-")) for x in os.environ.get("A34_NOTHROW_FRAMES", "").split(",") if x]


def _no_throw_at(f):
    return NOTHROW or any(lo <= f <= hi for lo, hi in NOTHROW_RANGES)


class TasPath:
    """TAS trajectory of one stage: per TAS frame (room, wpos, y)."""

    def __init__(self, f_lo, f_hi):
        self.f_lo, self.f_hi = f_lo, f_hi
        rows = []
        for f in range(f_lo, f_hi + 1):
            r = K.ref_at(f)
            rows.append((int(r[0x6E]), K.ram_wpos(r), int(r[0x8A]), int(r[0x6D])))
        a = np.array(rows, dtype=np.int32)
        self.room, self.wpos, self.y, self.stage = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
        self.item = np.array([int(K.ref_at(f)[0xC9]) for f in range(f_lo, f_hi + 1)])
        self.ninpo = np.array([int(K.ref_at(f)[0x64]) for f in range(f_lo, f_hi + 1)])
        self.hp = np.array([int(K.ref_at(f)[0x65]) for f in range(f_lo, f_hi + 1)])

    def hp_def(self, g, hp):
        i = min(max(g, self.f_lo), self.f_hi) - self.f_lo
        return max(0, int(self.hp[i]) - hp)

    def res_pen(self, g, item, ninpo, w_item=40.0, w_ninpo=1.0):
        i = min(max(g, self.f_lo), self.f_hi) - self.f_lo
        if NOTHROW or NOTHROW_RANGES:      # round 2: keep ninpo (only a shortfall vs the TAS costs); the weapon must still match
            want = int(self.ninpo[i])
            if NOTHROW_RANGES:     # round 3: the ninpo saved by the dropped throws must be kept too
                for lo, hi in NOTHROW_RANGES:
                    for f in range(max(lo, self.f_lo + 1), min(hi, g, self.f_hi) + 1):
                        dn = int(self.ninpo[f - 1 - self.f_lo]) - int(self.ninpo[f - self.f_lo])
                        if dn > 0:
                            want += dn
            item_ok = item == self.item[i] or (self.item[i] == 0x81 and item in (0, 0x81))
            return (0.0 if item_ok else w_item) + 2.0 * max(0, want - ninpo)
        return (w_item if item != self.item[i] else 0.0) + w_ninpo * abs(ninpo - int(self.ninpo[i]))

    def match(self, room, wpos, y, hint, span=90):
        hint = min(max(hint, self.f_lo), self.f_hi)
        i0 = max(0, hint - span - self.f_lo)
        i1 = min(len(self.room), hint + span - self.f_lo + 1)
        idx = np.arange(i0, i1)
        idx = idx[self.room[idx] == room]
        if len(idx) == 0:
            idx = np.nonzero(self.room == room)[0]
            if len(idx) == 0:
                return hint, 999
        dist = np.abs(self.wpos[idx] - wpos) + np.abs(self.y[idx] - y) * 0.75
        fr = idx + self.f_lo
        cost = dist + 0.05 * np.abs(fr - hint)
        k = int(np.argmin(cost))
        return int(fr[k]), float(dist[k])


class Node:
    __slots__ = ("sid", "L", "t", "g", "dist", "late", "hp", "parent", "rows", "tag", "s", "key")

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def node_rows(n):
    out = []
    while n is not None:
        out.append(n.rows)
        n = n.parent
    res = []
    for r in reversed(out):
        res.extend(r)
    return res


PRIMS = {
    "R": [R("Right")],
    "RA": [R("Right", "A")],
    "RB": [R("Right", "B")],
    "UB": [R("Up", "B")],
    "L": [R("Left")],
    "LA": [R("Left", "A")],
    "LB": [R("Left", "B")],
    "N": [()],
    "A": [R("A")],
    "B": [R("B")],
    "DB": [R("Down", "B")],
    "RD": [R("Right", "Down")],
    # legal wall climb cycles (a12 notes: "R+A, R+A, L, L, -" climbs 2 px/f), both orientations
    "WR": [R("Right", "A"), R("Right", "A"), R("Left"), R("Left"), ()],
    "WL": [R("Left", "A"), R("Left", "A"), R("Right"), R("Right"), ()],
    "WR0": [R("Right", "A"), R("Right", "A"), (), (), ()],
    "WL0": [R("Left", "A"), R("Left", "A"), (), (), ()],
    "WRR": [R("Right", "A"), R("Right", "A"), R("Right"), R("Right"), ()],
    "WLL": [R("Left", "A"), R("Left", "A"), R("Left"), R("Left"), ()],
    # alternating wall-jump climbs that work legally (p33: 4-1b shaft exits +35 f, 4-3a exits +13 f vs the TAS)
    "Z1": [R("Left", "A"), R("Left", "A"), (), (), (), R("Right", "A"), R("Right", "A"), R("Right"), R("Right"), R("Right")],
    "Z2": [R("Left", "A"), R("Left", "A"), (), (), (), (), R("Right", "A"), R("Right", "A"), R("Right"), R("Right")],
    "Z1m": [R("Right", "A"), R("Right", "A"), (), (), (), R("Left", "A"), R("Left", "A"), R("Left"), R("Left"), R("Left")],
    "Z2m": [R("Right", "A"), R("Right", "A"), (), (), (), (), R("Left", "A"), R("Left", "A"), R("Left"), R("Left")],
    # round 2: legal SINGLE-wall climb found by sweep at 4-1c (1.54 px/f, = the record's period-8 climb)
    "C8": [R("Left", "A"), R("Left", "A")] + [R("Right")] * 6,     # wall on Ryu's right
    "C8m": [R("Right", "A"), R("Right", "A")] + [R("Left")] * 6,   # wall on Ryu's left
}
MACROS = {"WR", "WL", "WR0", "WL0", "WRR", "WLL", "Z1", "Z2", "Z1m", "Z2m", "C8", "C8m"}


class Beam:
    def __init__(self, e, stage, frame0, hist, path: TasPath, W=10, K_=2, prims=None, hp_pen=2.0, log=print,
                 tas_shifts=(0, 1, -1)):
        self.e, self.stage, self.path, self.W, self.K, self.log = e, stage, path, W, K_, log
        self.T = K.tas_rows()
        self.prims = prims or list(PRIMS)
        self.hp_pen = hp_pen
        self.tas_shifts = tas_shifts
        s = e.state()
        sid = e.msave()
        g, dist = path.match(s.room, K.wpos(s), s.y, frame0)
        self.beam = [Node(sid=sid, L=K.Legal(hist), t=frame0, g=g, dist=dist, late=frame0 - g + dist / 1.5,
                          hp=s.hp, parent=None, rows=[], tag="start", s=s, key=None)]
        self.done = []
        self.steps = 0
        self.goal = None
        self.goal_step = 0
        self.reached = False
        self.auto_goal = True
        self.stuck = 6.0
        self.goal_ahead = 45

    def actions(self, n):
        acts = []
        for sh in self.tas_shifts:
            g = n.g + sh
            rows = [self.T[g + i] for i in range(self.K)]   # TAS frames g+1..g+K
            if NOTHROW or NOTHROW_RANGES:
                rows = [tuple(b for b in r if b not in ("Up", "B")) if ("Up" in r and "B" in r and _no_throw_at(g + i + 1))
                        else r for i, r in enumerate(rows)]
            acts.append((f"T{sh:+d}", rows))
        for p in self.prims:
            if NOTHROW and p == "UB":
                continue
            acts.append((p, list(PRIMS[p]) if len(PRIMS[p]) > 1 else PRIMS[p] * self.K))
        return acts

    def expand(self):
        children = {}
        for n in self.beam:
            for tag, rows in self.actions(n):
                L = n.L.copy()
                legal = K.greedy_legal(rows, L)
                self.e.mload(n.sid)
                s = self.e.run(legal)
                t = n.t + len(legal)
                if s.stage != self.stage:
                    self.done.append((t, n, legal, tag, s))
                    continue
                if (s.dead & 0x80) or s.lives < n.s.lives or s.y >= 0xF8:
                    continue
                rb = self.e.ram(0x400, 0xC0)
                key = (s.x, s.xsub, s.y, s.vy, s.vy_sub, s.scroll, s.scroll_sub, s.scroll_scr, s.room, s.anim, s.hp,
                       s.rflags, s.ninpo, rb, L.held["A"], L.held["B"])
                g, dist = self.path.match(s.room, K.wpos(s), s.y, n.g + len(legal))
                late = t - g + dist / 1.5 + self.hp_pen * self.path.hp_def(g, s.hp) + self.path.res_pen(g, s.item, s.ninpo)
                if self.goal is not None:
                    gr, gx, gy, gf = self.goal
                    gd = abs(K.wpos(s) - gx) + abs(s.y - gy) if s.room == gr else (0 if s.room > gr else 999)
                    if (gd <= 2 and not (s.rflags & 4)) or s.room > gr:
                        g = gf
                        late = t - gf + self.hp_pen * self.path.hp_def(g, s.hp) + self.path.res_pen(g, s.item, s.ninpo)
                        self.reached = True
                    else:
                        # goal mode: time to the goal position (+ resources)
                        late = t + gd / 1.5 - gf + 1000 + self.hp_pen * self.path.hp_def(g, s.hp)                             + self.path.res_pen(g, s.item, s.ninpo)
                old = children.get(key)
                if old is None or late < old.late:
                    if old is not None:
                        self.e.mfree(old.sid)
                    sid = self.e.msave()
                    children[key] = Node(sid=sid, L=L, t=t, g=g, dist=dist, late=late, hp=s.hp, parent=n, rows=legal,
                                         tag=tag, s=s, key=key)
        return list(children.values())

    def step(self):
        kids = self.expand()
        self.steps += 1
        old = self.beam
        if self.done:
            return True
        kids.sort(key=lambda c: (c.late, -c.hp))
        keep = kids[:self.W]
        drop = kids[self.W:]
        for c in drop:
            self.e.mfree(c.sid)
        keepids = {id(c.parent) for c in keep}
        for n in old:
            # parents are no longer needed as states (rows stay reachable through the parent links)
            self.e.mfree(n.sid)
            n.sid = None
        self.beam = keep
        return False

    def run(self, max_steps=100000, report_every=25):
        t0 = time.time()
        hist = []
        while self.steps < max_steps:
            if not self.beam:
                self.log("beam empty")
                return None
            self.reached = False
            fin = self.step()
            if fin:
                break
            if not self.beam:
                self.log("beam empty")
                return None
            b = self.beam[0]
            self.best_partial = b
            if self.goal is not None:
                if self.reached or self.steps - self.goal_step > 400:
                    self.log(f"  goal {self.goal} {'reached' if self.reached else 'abandoned'} at t={b.t} late={b.late:.1f}")
                    self.goal = None
                    hist = []
                    # re-score the beam in normal mode on the next expansion (late values are recomputed)
            elif self.auto_goal:
                hist.append(b.late)
                if len(hist) > 12 and b.late - min(hist[-12:]) >= self.stuck:
                    gf = min(b.g + self.goal_ahead, self.path.f_hi)
                    i = gf - self.path.f_lo
                    j = b.g - self.path.f_lo
                    if int(self.path.room[i]) != int(self.path.room[j]):
                        # stay in the current room: aim at the TAS's last position in it (the exit)
                        while i > j and int(self.path.room[i]) != int(self.path.room[j]):
                            i -= 1
                        gf = i + self.path.f_lo
                    self.goal = (int(self.path.room[i]), int(self.path.wpos[i]), int(self.path.y[i]), gf)
                    self.goal_step = self.steps
                    self.log(f"  stuck at t={b.t} g={b.g} late={b.late:.1f}: goal mode -> TAS position of frame {gf}")
            if self.steps % report_every == 0:
                b = self.beam[0]
                self.log(f"  step {self.steps} t={b.t} g={b.g} late={b.late:.1f} hp={b.hp} room={b.s.room} "
                         f"x={b.s.x} y={b.s.y} tag={b.tag} {time.time() - t0:.0f}s")
        if not self.done:
            return None
        self.done.sort(key=lambda d: d[0])
        t, n, legal, tag, s = self.done[0]
        rows = node_rows(n) + legal
        return t, rows


def stage_from_args(args):
    def opt(name, default):
        if name in args:
            i = args.index(name)
            val = args[i + 1]
            del args[i:i + 2]
            return type(default)(val) if default is not None else val
        return default
    return opt


def main():
    args = sys.argv[1:]
    opt = stage_from_args(args)
    name = args[0]
    st = K.BY_NAME[name]
    _, c0, c1, state = K.STAGES[st]
    state = opt("--start", state)
    prefix = opt("--prefix", "")
    W = opt("--W", 10)
    K_ = opt("--K", 2)
    out = opt("--out", f"beam_{name}")
    hist = opt("--hist", "")
    max_steps = opt("--max-steps", 100000)
    e = K.open_emu(f"a34_beam_{name}.log")
    try:
        s = e.load(state)
        f0 = s.frame
        pre = K.load_rows(prefix) if prefix else []
        h = (K.load_rows(hist) if hist else []) + pre
        if pre:
            s = e.run(pre)
        path = TasPath(c0, c1)
        print("start", s.frame, "stage", s.stage, "room", s.room, "x", s.x, "y", s.y, flush=True)
        bm = Beam(e, st, s.frame, h, path, W=W, K_=K_, log=lambda m: print(m, flush=True))
        t = time.time()
        res = bm.run(max_steps)
        if res is None:
            print("no result")
            return
        tend, rows = res
        rows = pre + rows
        # stage time: load frame of the next stage (first frame with the new $6D)
        print(f"next stage load at frame {tend} (TAS {c1 - 151}); {tend - (c1 - 151):+d} frames; {time.time() - t:.0f}s")
        K.save_rows(out, rows, f"from {state} frame {f0}; next-stage load at {tend}")
        (K.OUT_DIR / f"{out}.json").write_text(json.dumps({"start": state, "frame0": f0, "load": tend,
                                                          "tas_load": c1 - 151, "rows": len(rows)}))
    finally:
        e.close()




class BossBeam(Beam):
    """Boss fights: score = t + c * boss HP ($0497, slot 7) + Ryu HP penalty; the TAS is followed by time (g = TAS
    frame t - d). Stops at the first node with boss HP 0 (the kill frame)."""

    def __init__(self, *a, c=6.0, prims=None, wdist=0.3, wcost=5, rollout=0, c2=0.0, proj_ids=(), **kw):
        prims = prims or ["R", "RA", "RB", "UB", "L", "LA", "LB", "N", "A", "B", "DB"]
        super().__init__(*a, prims=prims, **kw)
        self.c = c
        self.auto_goal = False
        self.wdist = wdist
        self.wcost = wcost
        self.rollout, self.c2, self.proj_ids = rollout, c2, set(proj_ids)
        n = self.beam[0]
        n.g = n.t
        n.late = n.t + self.c * self.e.byte(0x497)

    def expand(self):
        children = {}
        for n in self.beam:
            for tag, rows in self.actions(n):
                L = n.L.copy()
                legal = K.greedy_legal(rows, L)
                self.e.mload(n.sid)
                s = self.e.run(legal)
                t = n.t + len(legal)
                if (s.dead & 0x80) or s.lives < n.s.lives or s.hp == 0 or s.y >= 0xF8:
                    continue
                bhp = s.boss_real
                if bhp == 0 or s.bosshp == 0 or s.stage != self.stage:
                    # find the exact kill frame inside the step
                    self.done.append((t, n, legal, tag, s))
                    continue
                rb = self.e.ram(0x400, 0xC0)
                key = (s.x, s.xsub, s.y, s.vy, s.vy_sub, s.anim, s.hp, s.rflags, s.ninpo, rb, L.held["A"], L.held["B"],
                       L.held["Down"], L.held["Up"])
                sh = int(tag[1:]) if tag.startswith("T") else 0
                g = n.g + len(legal) + (sh if tag.startswith("T") else 0)
                bx, by = rb[0x67], rb[0x87]          # boss slot 7: x $0467, y $0487
                dist = abs(int(bx) - s.x) + abs(int(by) - s.y) * 0.5
                sid = self.e.msave()
                bhp_eff = bhp
                if self.rollout and (not self.proj_ids or any(rb[i] in self.proj_ids for i in range(7))):
                    s2 = self.e.run([()] * self.rollout)
                    bhp_eff = s2.boss_real if s2.stage == self.stage else 0
                late = (t + self.c * bhp + self.c2 * bhp_eff + self.hp_pen * max(0, 16 - s.hp) * 0.25
                        + (self.wdist if s.ninpo < self.wcost else 0.0) * dist / 1.5)
                old = children.get(key)
                if old is None or late < old.late:
                    if old is not None:
                        self.e.mfree(old.sid)
                    children[key] = Node(sid=sid, L=L, t=t, g=g, dist=0, late=late, hp=s.hp, parent=n, rows=legal,
                                         tag=tag, s=s, key=key)
                else:
                    self.e.mfree(sid)
        return list(children.values())


class GoalBeam(Beam):
    """Reach a fixed goal position (room, world x, y) as fast as possible: late = t + dist/1.5 (dist = |dx| +
    ky*|dy|). Done when dist <= tol and Ryu is on the ground (rflags bit 2 clear) or when the room changes to
    goal_room+1."""

    def __init__(self, *a, goal=None, ky=1.0, tol=2, room_done=False, **kw):
        super().__init__(*a, **kw)
        self.goal_pos = goal      # (room, wpos, y)
        self.auto_goal = False
        self.ky, self.tol = ky, tol
        self.room_done = room_done
        self.reached = []

    def expand(self):
        children = {}
        gr, gx, gy = self.goal_pos
        for n in self.beam:
            for tag, rows in self.actions(n):
                L = n.L.copy()
                legal = K.greedy_legal(rows, L)
                self.e.mload(n.sid)
                s = self.e.run(legal)
                t = n.t + len(legal)
                if s.stage != self.stage:
                    self.done.append((t, n, legal, tag, s))
                    continue
                if (s.dead & 0x80) or s.lives < n.s.lives or s.y >= 0xF8:
                    continue
                if s.room != gr and self.room_done:
                    self.done.append((t, n, legal, tag, s))
                    continue
                dist = abs(K.wpos(s) - gx) + self.ky * abs(s.y - gy) if s.room == gr else 999
                if dist <= self.tol and not (s.rflags & 4):
                    self.done.append((t, n, legal, tag, s))
                    continue
                rb = self.e.ram(0x400, 0xC0)
                key = (s.x, s.xsub, s.y, s.vy, s.vy_sub, s.scroll, s.scroll_sub, s.scroll_scr, s.room, s.anim, s.hp,
                       s.rflags, s.ninpo, rb, L.held["A"], L.held["B"])
                g, _ = self.path.match(s.room, K.wpos(s), s.y, n.g + len(legal))
                late = t + dist / 1.5 + self.hp_pen * self.path.hp_def(g, s.hp)
                old = children.get(key)
                if old is None or late < old.late:
                    if old is not None:
                        self.e.mfree(old.sid)
                    sid = self.e.msave()
                    children[key] = Node(sid=sid, L=L, t=t, g=g, dist=dist, late=late, hp=s.hp, parent=n, rows=legal,
                                         tag=tag, s=s, key=key)
        return list(children.values())


def goal_main():
    """python ng/stages/a34_beam.py goal <stage> <prefix rows> <goal TAS frame> <out> [W]"""
    _, _, name, prefix, gf, out = sys.argv[:6]
    W = int(sys.argv[6]) if len(sys.argv) > 6 else 12
    st = K.BY_NAME[name]
    _, c0, c1, state = K.STAGES[st]
    if gf.startswith("room:"):            # room:<room>:<wpos>:<y>:<ky>  -> leave the room, heading for that point
        _, rm, gx, gy, ky = gf.split(":")
        goal = (int(rm), int(gx), int(gy))
        gf, kyv, rd = 0, float(ky), True
    else:
        gf = int(gf)
        r = K.ref_at(gf)
        goal = (int(r[0x6E]), K.ram_wpos(r), int(r[0x8A]))
        kyv, rd = 1.0, False
    e = K.open_emu(f"a34_goal_{name}.log")
    try:
        e.load(state)
        pre = K.load_rows(prefix)
        s = e.run(pre)
        path = TasPath(c0, c1)
        bm = GoalBeam(e, st, s.frame, pre, path, W=W, goal=goal, ky=kyv, room_done=rd, log=lambda m: print(m, flush=True))
        res = bm.run(4000, report_every=10)
        if res is None:
            print("no result")
            return
        tend, rows = res
        print(f"goal {goal} (TAS frame {gf}) reached at {tend}: {tend - gf:+d}")
        K.save_rows(out, pre + rows, f"{prefix} + goal beam to TAS pos of {gf}, reached {tend}")
    finally:
        e.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "goal":
        goal_main()
    else:
        main()
