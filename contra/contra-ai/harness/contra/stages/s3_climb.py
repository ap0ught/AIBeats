"""Waterfall climb: the ledge search of s3_plan.py with every node validated in the emulator.

The model proposes jumps (walk, direction pattern) between floor rows; each proposal is played from its parent's
savestate and kept only if Bill really ends up standing on a higher row, alive, with his weapon. A kept node has
the true number of rows (lag frames, waits, lost presses included), its own savestate and the rows from the stage
state, so the result is a real, legal input list. Enemies, the bridge flames and the floating rocks are handled
by the emulator: proposals that die are dropped, waits and firing modes are tried when nothing survives, and the
rocks are "virtual rows" of the model map that only count when the game says Bill is standing on an enemy.
"""
from __future__ import annotations

import threading
import time
from multiprocessing import Pool

from .s3s8_lib import Game, Pad, R
from .s3_model import Map
from .s3_plan import Planner, Node, expand_raw, seg_of, _winit, run_air, TAIR
from .s3_exec import play_node, wait_frames, A_of, MODES

# rocks: (virtual row, first column, last column, A at which the rock exists)
ROCKS = {-54: (6, 12, 849), -84: (6, 12, 1321)}
FLAME_ROW = -37


def make_map() -> Map:
    mp = Map()
    for q, (c0, c1, _a) in ROCKS.items():
        m = 0
        for c in range(c0, c1 + 1):
            m |= 1 << c
        mp.rows[q] = mp.rows.get(q, 0) | m
    return mp


_PLV = None


def _winit_v():
    global _PLV
    _PLV = Planner(make_map())


def _wexp_v(job):
    return expand_raw(_PLV, *job)


class EN:
    """A node that exists in the emulator."""
    __slots__ = ("t", "X", "Y", "sub", "A", "q", "state", "rows", "pad", "parent", "how", "rock", "lag", "ign")

    def __init__(self, t, r: R, state, rows, pad, parent=None, how=None, lag=0, ign=0):
        self.t = t
        self.X, self.Y, self.sub, self.A = r.x, r.y, r.sub, A_of(r)
        self.q = (self.Y + 16 - self.A) >> 4
        self.rock = bool(r.on_enemy)
        self.state, self.rows, self.pad, self.parent, self.how = state, rows, pad, parent, how
        self.lag, self.ign = lag, ign

    def __repr__(self):
        return (f"EN(t={self.t} q={self.q} X={self.X} Y={self.Y} sub={self.sub:02x} A={self.A}"
                f"{' ROCK' if self.rock else ''} lag={self.lag})")


class Climber:
    def __init__(self, games, tag="s3", procs=6, log=print, weapon=0x13):
        self.games = games
        self.tag = tag
        self.log = log
        self.weapon = weapon
        self.mp = make_map()
        self.pl = Planner(self.mp)
        self.pool = Pool(procs, initializer=_winit_v) if procs > 1 else None
        self.nid = 0
        self.lock = threading.Lock()
        self.tests = 0

    def close(self):
        if self.pool is not None:
            self.pool.terminate()
            self.pool = None

    # ------------------------------------------------------------------ emulator trials
    def _name(self):
        with self.lock:
            self.nid += 1
            return f"{self.tag}/tmp/n{self.nid}"

    def trial(self, g: Game, parent: EN, cand, wait=0, mode=0, hop=False):
        """cand = (pred_t, X, Y, sub, A, walk, ds0, dirs). Returns an EN or None."""
        self.tests += 1
        g.load(parent.state, parent.pad)
        st = "ok"
        if wait:
            st, r = wait_frames(g, wait, MODES[mode], self.weapon)
            if st != "ok":
                return None
        nd = Node(0, cand[1], cand[2], cand[3], cand[4], None, cand[5], cand[6], cand[7])
        st, r = play_node(g, nd, MODES[mode], check=False, weapon=self.weapon)
        if st != "ok":
            return None
        k = 0
        while r.airborne and k < 40:
            r = g.step(())
            k += 1
            if r.dead or r.pstate != 1 or r.weapon != self.weapon:
                return None
        if r.airborne or r.dead or r.pstate != 1:
            return None
        q = (r.y + 16 - A_of(r)) >> 4
        if q > parent.q or (q == parent.q and not hop):
            return None
        # eight more frames on the spot: a shell or a soldier arriving with us is not a landing
        snap_rows = len(g.rows)
        name = self._name()
        g.e.save(name)
        ok = True
        rr = r
        for _ in range(8):
            rr = g.step(())
            if rr.dead or rr.pstate != 1:
                ok = False
                break
        if not ok:
            return None
        rows = parent.rows + g.rows[:snap_rows]
        pad = parent.pad.copy()
        for row in g.rows[:snap_rows]:
            pad.push(row)
        return EN(len(rows), r, name, rows, pad, parent, (wait, mode, cand[5], cand[6], cand[7]),
                  parent.lag + g.lag, parent.ign + g.ignored)

    def trials(self, jobs):
        """jobs: [(parent, cand, wait, mode, hop)] -> results in order, run on all emulators."""
        out = [None] * len(jobs)
        idx = [0]
        lock = threading.Lock()

        def work(g):
            while True:
                with lock:
                    i = idx[0]
                    idx[0] += 1
                if i >= len(jobs):
                    return
                p, c, w, m, hop = jobs[i]
                try:
                    out[i] = self.trial(g, p, c, w, m, hop)
                except Exception as ex:  # noqa: BLE001
                    out[i] = ex
        th = [threading.Thread(target=work, args=(g,)) for g in self.games]
        for t in th:
            t.start()
        for t in th:
            t.join()
        for o in out:
            if isinstance(o, Exception):
                raise o
        return out

    # ------------------------------------------------------------------ the validated beam
    def expand(self, nodes, targets, tlimit):
        jobs = [(n.t, n.X, n.Y, n.sub, n.A, targets, tlimit, 8 if (n.rock and n.q == -84) else 0) for n in nodes]
        if self.pool is not None and len(jobs) > 1:
            return self.pool.map(_wexp_v, jobs)
        return [expand_raw(self.pl, *j) for j in jobs]

    def climb(self, start: EN, q_end: int, keep=6, tests=18, slack=24, up=4, extra_starts=()):
        """From a standing node up to row q_end. Returns {(q, xa, xb): [validated EN sorted by t]}."""
        mp = self.mp
        cands = {}                     # target key -> [(pred_t, parent, cand)]
        valid = {}
        best = {}
        seg = seg_of(mp, start.q, start.X)
        key0 = (start.q, seg[0], seg[1]) if seg else (start.q, 0, 255)
        valid[key0] = sorted([start] + list(extra_starts), key=lambda e: e.t)
        best[key0] = valid[key0][0].t
        q = start.q
        failed = {}
        while q >= q_end:
            if q > q_end and not any(k[0] <= q and k not in valid for k in cands) \
                    and not any(k[0] == q and valid.get(k) for k in valid):
                # dead end: nothing is proposed for this row or above. Go back to the segments that were given up
                # with a small budget and try them properly (waits, firing), highest first.
                redo = sorted((k for k, v in failed.items() if v), key=lambda k: k[0])
                got = None
                for k in redo:
                    failed[k] = False
                    self.log(f"dead end at row {q}: retrying row {k[0]} seg {k[1]}-{k[2]} with the full budget")
                    v = self.validate(k, cands.get(k, []), keep, tests * 3, slack, late_scale=1.0)
                    if v:
                        valid[k] = v
                        best[k] = v[0].t
                        got = k
                        break
                if got is None:
                    break
                q = got[0]
            keys = sorted(set(k for k in list(cands) + list(valid) if k[0] == q))
            for key in keys:
                if key not in valid:
                    # later rounds (waits, firing) only where nothing else leads upward
                    others = any(k2[0] == q and valid.get(k2) for k2 in keys if k2 != key) or                         any(k2[0] < q and cands.get(k2) for k2 in cands)
                    forced = key[0] in ROCKS or key[0] == FLAME_ROW
                    near_bridge = FLAME_ROW - 4 <= key[0] < FLAME_ROW
                    valid[key] = self.validate(key, cands.get(key, []), keep * (2 if near_bridge else 1),
                                               tests * (4 if near_bridge else 1), slack,
                                               late_scale=1.0 if (forced or not others) else 0.34)
                    if not valid[key] and not (forced or not others):
                        failed[key] = True
                    if key[0] == FLAME_ROW:
                        valid[key] = self.bridge_extra(key, cands.get(key, []), valid[key])
                    if key[0] in ROCKS and valid[key]:
                        valid[key] = self.ride_extra(valid[key])
                    if valid[key]:
                        best[key] = valid[key][0].t
                        v = valid[key][0]
                        self.log(f"row {q} seg {key[1]}-{key[2]}: {len(valid[key])} valid, best {v} "
                                 f"(tests so far {self.tests})")
                    else:
                        self.log(f"row {q} seg {key[1]}-{key[2]}: nothing valid of {len(cands.get(key, []))} proposals")
                nodes = valid[key]
                if not nodes or q == q_end:
                    continue
                targets = []
                for dq in range(1, up + 1):
                    if q - dq < q_end:
                        break
                    for (xa, xb) in mp.segs(q - dq):
                        targets.append((q - dq, xa, xb))
                if q == FLAME_ROW:
                    targets.append(key)                         # hops along the bridge
                if not targets:
                    continue
                tl = {tg: best.get(tg, 10 ** 9) + slack for tg in targets}
                res = self.expand(nodes, targets, tl)
                for n, chs in zip(nodes, res):
                    for c in chs:
                        cq = (c[2] + 16 - c[4]) >> 4
                        s2 = seg_of(mp, cq, c[1])
                        if s2 is None:
                            continue
                        cands.setdefault((cq, s2[0], s2[1]), []).append((c[0], n, c))
                if q == FLAME_ROW:
                    # hops along the bridge (over a flame): validate them now and expand the survivors too
                    hv = self.bridge_hops(key, [pr for pr in cands.get(key, []) if pr[1].q == q])
                    if hv:
                        valid[key] = sorted(valid[key] + hv, key=lambda e: e.t)
                        tg2 = [tg for tg in targets if tg != key]
                        res2 = self.expand(hv, tg2, tl)
                        for n, chs in zip(hv, res2):
                            for c in chs:
                                cq = (c[2] + 16 - c[4]) >> 4
                                s2 = seg_of(mp, cq, c[1])
                                if s2 is None or cq >= q:
                                    continue
                                cands.setdefault((cq, s2[0], s2[1]), []).append((c[0], n, c))
            q -= 1
        return valid

    ROUNDS = (([0], 0, 1.0), ([4, 8, 16, 24, 32], 0, 1.0), ([48, 64, 80, 96, 112, 128, 160, 192], 0, 1.5),
              ([0, 8, 24], 1, 1.0), ([0, 8, 24], 2, 1.0), ([0, 8, 24], 4, 1.0))

    def bridge_extra(self, key, props, have):
        """The bridge has two flames sweeping X $48..$B8. More arrivals: the right-most landings, each delayed
        by 0..112 frames on the floor below, so that some node stands right of the left-going flame."""
        props = sorted(props, key=lambda z: -z[2][1])
        seen, pick = set(), []
        for pt, parent, c in props:
            sig = (parent.state, c[5])
            if sig in seen:
                continue
            seen.add(sig)
            pick.append((parent, c))
            if len(pick) >= 4:
                break
        jobs = [(p_, c, w, 0, False) for (p_, c) in pick for w in range(0, 132, 6)]
        res = self.trials(jobs)
        out = list(have)
        b = {}
        for en, job in zip(res, jobs):
            if en is None or en.q != key[0]:
                continue
            k = (en.X >> 3, job[2])
            if k in b:
                continue
            b[k] = 1
            out.append(en)
        # second pass: the waits above step by 6 frames; around the first waits that survive, try every frame
        ok = sorted(((en.t, job) for en, job in zip(res, jobs) if en is not None and en.q == key[0] and job[2] > 0
                     and en.X >= 64), key=lambda z: z[0])
        fine, seenf = [], set()
        for _t, job in ok[:3]:
            for d in (1, 2, 3, 4, 5):
                sig = (job[0].state, job[1][5], job[2] - d)
                if job[2] - d > 0 and sig not in seenf:
                    seenf.add(sig)
                    fine.append((job[0], job[1], job[2] - d, 0, False))
        if fine:
            n0 = len(out)
            for en in self.trials(fine):
                if en is not None and en.q == key[0]:
                    out.append(en)
            self.log(f"   bridge: {len(out) - n0} of {len(fine)} finer waits alive")
        out.sort(key=lambda e: e.t)
        self.log(f"   bridge: {len(out) - len(have)} extra arrivals: " + ", ".join(f"X{e.X}@{e.t}" for e in out))
        return out

    def ride(self, g: Game, parent: EN, wait: int):
        """Stand on the rock for `wait` frames. Returns an EN (still on the rock) or None."""
        self.tests += 1
        g.load(parent.state, parent.pad)
        st, r = wait_frames(g, wait, MODES[0], self.weapon)
        if st != "ok" or r.airborne or not r.on_enemy:
            return None
        name = self._name()
        g.e.save(name)
        pad = parent.pad.copy()
        for row in g.rows:
            pad.push(row)
        return EN(parent.t + len(g.rows), r, name, parent.rows + list(g.rows), pad, parent, (wait, 0, 0, 0, ()),
                  parent.lag + g.lag, parent.ign + g.ignored)

    def ride_extra(self, nodes):
        """A rock carries Bill sideways: more nodes = the same landing after riding 6..126 more frames."""
        jobs = [(n, w) for n in nodes[:2] for w in range(6, 132, 6)]
        out = [None] * len(jobs)
        idx = [0]
        lock = threading.Lock()

        def work(g):
            while True:
                with lock:
                    i = idx[0]
                    idx[0] += 1
                if i >= len(jobs):
                    return
                out[i] = self.ride(g, jobs[i][0], jobs[i][1])
        th = [threading.Thread(target=work, args=(g,)) for g in self.games]
        for t in th:
            t.start()
        for t in th:
            t.join()
        extra = [e for e in out if e is not None]
        self.log(f"   rock: {len(extra)} riding nodes, X " + ", ".join(f"{e.X}@{e.t}" for e in extra[:14]))
        return sorted(list(nodes) + extra, key=lambda e: e.t)

    def bridge_hops(self, key, props):
        """Jumps from the bridge that land on the bridge further right (clearing a flame in the air)."""
        props = [pr for pr in props if pr[2][1] >= pr[1].X + 24]
        if not props:
            return []
        groups = {}
        for pr in sorted(props, key=lambda z: (-z[2][1], z[0])):
            g_ = groups.setdefault(pr[1].state, [])
            if len(g_) < 3 and all(abs(pr[2][1] - z[2][1]) >= 8 for z in g_):
                g_.append(pr)
        jobs = [(pr[1], pr[2], w, 0, True) for g_ in groups.values() for pr in g_ for w in (0, 6, 12, 20)]
        res = self.trials(jobs)
        out, b = [], {}
        for en in res:
            if en is None or en.q != key[0]:
                continue
            k = (en.X >> 3, en.t >> 3)
            if k in b:
                continue
            b[k] = 1
            out.append(en)
        out.sort(key=lambda e: e.t)
        self.log(f"   bridge hops: {len(out)} of {len(jobs)} trials alive: " + ", ".join(f"X{e.X}@{e.t}" for e in out[:12]))
        return out[:10]

    def rock_traj(self, g: Game, parent: EN, n: int = 260):
        """X of the floating rock above Bill for the next n frames while he stands still (it moves by itself)."""
        self.tests += 1
        r = g.load(parent.state, parent.pad)
        out = []
        for _ in range(n):
            r = g.step(())
            xs = [(y, x) for (sl, t, ro, hp, x, y, st, at) in r.enemies() if t == 0x10 and y < parent.Y]
            out.append(max(xs)[1] if xs else None)
        return out

    def validate_rock(self, key, props, keep, tests):
        """Landings on a floating rock: the rock's X is recorded for 260 frames per parent, and every proposal
        is given the shortest wait that puts the rock under its landing spot."""
        groups = {}
        for pr in sorted(props, key=lambda z: z[0]):
            groups.setdefault(pr[1].state, []).append(pr)
        jobs = []
        for st, g_ in groups.items():
            parent = g_[0][1]
            traj = self.rock_traj(self.games[0], parent)
            seen = set()
            for pt, par, c in g_:
                sig = (c[5], c[1])
                if sig in seen:
                    continue
                seen.add(sig)
                k = pt - par.t
                for w in range(0, len(traj) - k - 3):
                    x = traj[w + k]
                    if x is not None and abs(x - c[1]) <= 8:
                        jobs.append((w + pt, par, c, w))
                        break
        jobs.sort(key=lambda z: z[0])
        out, b = [], {}
        i = 0
        nb = len(self.games) * 2
        while i < len(jobs) and i < tests * 6 and len(out) < keep * 2:
            batch = jobs[i:i + nb]
            i += nb
            res = self.trials([(par, c, w, 0, False) for (_t, par, c, w) in batch])
            for en in res:
                if en is None or not en.rock or en.q != key[0]:
                    continue
                k2 = (en.X >> 3, en.t >> 3)
                if k2 in b:
                    continue
                b[k2] = 1
                out.append(en)
        out.sort(key=lambda e: e.t)
        self.log(f"   rock row {key[0]}: {len(out)} landings from {min(i, len(jobs))} timed trials "
                 f"({len(jobs)} proposals had a rock under them within 260 frames)")
        return out[:keep * 2]

    def validate(self, key, props, keep, tests, slack, rounds=None, late_scale=1.0):
        """Test proposals for one floor segment in order of predicted arrival; keep the best few real ones.
        Rounds: as proposed; with waits (flames, rocks, bullets); with firing modes. A later round is only
        used when the earlier ones left nothing alive."""
        if not props:
            return []
        if key[0] in ROCKS:
            v = self.validate_rock(key, props, keep, tests)
            if v:
                return v
        # fair order: the best proposal of every parent first, then the second best of every parent, ...
        groups = {}
        for pr in sorted(props, key=lambda z: z[0]):
            groups.setdefault(pr[1].state, []).append(pr)
        gl = sorted(groups.values(), key=lambda g_: g_[0][0])
        props = []
        for rank in range(max(len(g_) for g_ in gl)):
            for g_ in gl:
                if rank < len(g_):
                    props.append(g_[rank])
        hop = key[0] == FLAME_ROW
        out = []
        nb = len(self.games) * 2
        for rnd, (waits, mode, mult) in enumerate(self.ROUNDS[:rounds] if rounds else self.ROUNDS):
            seen = set()
            per = {}
            buckets = {}
            tested = 0
            best_t = None
            i = 0
            limit = int(tests * mult) if rnd == 0 else max(6, int(tests * mult * late_scale))
            while i < len(props) and tested < limit:
                batch = []
                while i < len(props) and len(batch) < nb:
                    pt, parent, c = props[i]
                    i += 1
                    if best_t is not None and pt > best_t + slack:
                        continue
                    sig = (parent.state, c[5], c[6], c[7])
                    s2 = (parent.state, c[5])
                    if sig in seen or per.get(s2, 0) >= 2:
                        continue
                    seen.add(sig)
                    per[s2] = per.get(s2, 0) + 1
                    for w in waits:
                        batch.append((parent, c, w, mode, hop and parent.q == key[0]))
                if not batch:
                    break
                res = self.trials(batch)
                tested += len(batch) if rnd == 0 else max(1, len(batch) // len(waits))
                for en in res:
                    if en is None or en.q != key[0]:
                        continue
                    if (key[0] in ROCKS) != en.rock:
                        continue
                    b = (en.sub >> 4, 0 if en.Y < 80 else (1 if en.Y <= 100 else 2))
                    if buckets.get(b, 0) >= 2:
                        continue
                    buckets[b] = buckets.get(b, 0) + 1
                    out.append(en)
                    if best_t is None or en.t < best_t:
                        best_t = en.t
                if len(out) >= keep and tested >= limit // 2:
                    break
            if out:
                if rnd:
                    self.log(f"   (row {key[0]}: needed round {rnd}: waits {waits}, mode {mode})")
                break
        out.sort(key=lambda e: e.t)
        out = out[:keep]
        return self.refine_waits(key, out)

    def refine_waits(self, key, nodes):
        """Second pass: the wait rounds step by 4..32 frames, so a node found with a wait may be several frames
        later than it needs to be. Try the same jump with the wait shortened by 1..15 frames and keep the
        earliest that still stands there (one frame saved in the climb can be worth 8 at the dragon)."""
        jobs = []
        for en in nodes[:3]:
            how = en.how
            if not how or how[0] in ("drop",) or len(how) < 5 or not how[0] or how[1] != 0 or en.parent is None:
                continue
            w = how[0]
            cand = (0, en.X, en.Y, en.sub, en.A, how[2], how[3], how[4])
            for d in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15):
                if w - d >= 0:
                    jobs.append((en.parent, cand, w - d, 0, key[0] == FLAME_ROW and en.parent.q == key[0]))
        if not jobs:
            return nodes
        res = self.trials(jobs)
        extra = [en for en in res if en is not None and en.q == key[0] and ((key[0] in ROCKS) == en.rock)]
        if extra:
            best_old = nodes[0].t
            nodes = sorted(list(nodes) + extra, key=lambda e: e.t)
            if nodes[0].t < best_old:
                self.log(f"   row {key[0]}: shorter waits: best {best_old} -> {nodes[0].t} ({len(extra)} of {len(jobs)} alive)")
        return nodes
