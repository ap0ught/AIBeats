"""Shortest-path search for the Waterfall climb on the exact model (contra/stages/s3_model.py).

Directions in the air obey the project's input rules: runs of one direction are at least 2 frames, and two starts
of the same direction are at least 5 frames apart (a new Right press at most every 5 frames, held >= 2, released
>= 2; the same for Left; the direction stays latched when nothing is held). Direction state `ds`:
    0            nothing latched yet (no L/R since the jump began)
    1 + 6*L + 2*(a-1) + (lp-2)   direction (0 right, 1 left), a = length of the current run capped at 3,
                                 lp = length of the previous run of the other direction capped at 3 (3 = none)
A switch needs a >= 2 and a + lp >= 5.

rise table  B[k][sub, ds, dx+30] = bit mask over c: "from frame k to the last rising frame (29), all of them
scroll frames, with $94 = sub before frame k and direction state ds, exactly c counted carries and a net X
displacement dx are achievable". Scroll gained = sum of the frames' whole-pixel rises - c.

search(): layered beam over floor rows, bottom to top. A node is an exact standing state (X, Y, $94, A) with the
frame count since the start; its children are found by expand_raw(): walk 0.. frames, then a jump whose rise is
taken from the table (chosen number of carries and X displacement) and whose fall is simulated exactly.
"""
from __future__ import annotations

import random
from functools import lru_cache

import numpy as np

from .s3_model import Map, V0, G, XMAX, XMIN, TRIG

NDS = 13
KR = 29                                   # last rising frame of a jump
FR = [0] + [((V0 + G * k) & 0xFF) for k in range(1, 80)]          # velocity low byte after gravity, frame k
FH = [0] + [((V0 + G * k) >> 8) & 0xFF for k in range(1, 80)]     # velocity high byte
RISE = [0] + [(256 - FH[k]) if FH[k] >= 0x80 else 0 for k in range(1, 80)]
DXO = 30
SUMR = [0] * (KR + 3)
for _k in range(KR, 0, -1):
    SUMR[_k] = SUMR[_k + 1] + RISE[_k]
TAIR = {64: 36, 48: 39, 32: 47, 16: 53}


def ds_dir(ds):
    return 0 if ds == 0 else (1 if (ds - 1) < 6 else -1)


def ds_parts(ds):
    z = ds - 1
    return (1 if z < 6 else -1), (z % 6) // 2 + 1, (z % 2) + 2


def ds_make(d, a, lp):
    return 1 + (0 if d > 0 else 6) + (min(a, 3) - 1) * 2 + (min(lp, 3) - 2)


def ds_next(ds):
    """[(new ds, d)] legal actions for one frame."""
    if ds == 0:
        return [(0, 0), (ds_make(1, 1, 3), 1), (ds_make(-1, 1, 3), -1)]
    d, a, lp = ds_parts(ds)
    out = [(ds_make(d, a + 1, lp), d)]
    if a >= 2 and a + lp >= 5:
        out.append((ds_make(-d, 1, a), -d))
    return out


DSN = [ds_next(i) for i in range(NDS)]


def build_table():
    B = np.zeros((KR + 2, 256, NDS, 61), dtype=np.uint32)
    B[KR + 1, :, :, DXO] = 1
    subs = np.arange(256)
    for k in range(KR, 0, -1):
        fr = FR[k]
        s1 = (subs + fr) & 255
        c1 = (subs + fr) >> 8
        s2 = (s1 + fr) & 255
        c2 = (s1 + fr) >> 8
        nxt = B[k + 1]
        for ds in range(NDS):
            acc = np.zeros((256, 61), dtype=np.uint32)
            for nds, d in DSN[ds]:
                if d > 0:
                    src = nxt[s2, nds, :]
                    car = c2
                else:
                    src = nxt[s1, nds, :]
                    car = c1
                sh = np.zeros_like(src)
                if d > 0:
                    sh[:, 1:] = src[:, :-1]
                elif d < 0:
                    sh[:, :-1] = src[:, 1:]
                else:
                    sh = src
                acc |= np.where(car[:, None] == 1, sh << 1, sh)
            B[k, :, ds, :] = acc
    return B


_B = None


def table():
    global _B
    if _B is None:
        _B = build_table()
    return _B


@lru_cache(maxsize=400000)
def reconstruct(k0, sub, ds, dx, c, variant=0):
    """Directions for frames k0..29 realising (dx, c) from (sub, ds). Returns (dirs tuple, sub_end, ds_end) or None.
    variant 0 prefers keeping the direction, 1 prefers switching, >= 2 is a seeded random choice."""
    B = table()
    if not (0 <= dx + DXO < 61) or not (int(B[k0, sub, ds, dx + DXO]) >> c) & 1:
        return None
    rng = random.Random(variant * 7919 + k0 * 31 + sub) if variant >= 2 else None
    dirs = []
    for k in range(k0, KR + 1):
        fr = FR[k]
        acts = list(DSN[ds])
        if rng is not None:
            rng.shuffle(acts)
        elif variant == 1:
            acts.reverse()
        for nds, d in acts:
            s1 = sub + fr
            if d > 0:
                s2 = (s1 & 255) + fr
                car, ns = s2 >> 8, s2 & 255
            else:
                car, ns = s1 >> 8, s1 & 255
            ndx, nc = dx - d, c - car
            if nc < 0 or not (0 <= ndx + DXO < 61):
                continue
            if (int(B[k + 1, ns, nds, ndx + DXO]) >> nc) & 1:
                dirs.append(d)
                sub, ds, dx, c = ns, nds, ndx, nc
                break
        else:
            return None
    return tuple(dirs), sub, ds


def run_air(X, Y, sub, A, dirs, rows, k0=1, v=None, stop_at=None, maxk=110):
    """Fast exact simulation of airborne frames k0.. with directions dirs (the last repeats). `rows` = Map.rows.
    Returns (k_landed or None, X, Y, sub, A, v, trig_k): k counts frames after the A-press frame (frame 0).
    stop_at: return after that frame even if still airborne."""
    if v is None:
        v = (V0 + G * (k0 - 1)) & 0xFFFF
    nd = len(dirs)
    auto = 0
    trig = None
    k = k0
    i = 0
    d = 0
    while k <= maxk:
        if i < nd:
            d = dirs[i]
        i += 1
        fast = v >> 8
        if fast < 0x80 and fast >= 1 and (fast >= 4 or ((Y - A) & 15) < 8) and Y + 16 < 0xE0 \
                and (rows.get((Y + 16 - A) >> 4, 0) >> (X >> 4)) & 1:
            Y = Y - ((Y - A) & 15) + 4
            if d > 0:
                if X < XMAX:
                    X += 1
            elif d < 0:
                if X >= XMIN:
                    X -= 1
            if auto:
                A += 1
                Y += 1
            return k, X, Y, sub, A, 0, trig
        v = (v + G) & 0xFFFF
        fast = v >> 8
        fr = v & 0xFF
        scroll = 0
        if fast >= 0x80 and Y < 0x50 and not auto:
            if A >= TRIG:
                auto = 0x40
                trig = k
                t = sub + fr
                sub = t & 0xFF
                Y = (Y + fast + (t >> 8)) & 0xFF
            else:
                t = sub + fr
                sub = t & 0xFF
                scroll = 256 - fast - (t >> 8)
        else:
            t = sub + fr
            sub = t & 0xFF
            Y = (Y + fast + (t >> 8)) & 0xFF
        if d > 0:
            if X < XMAX:
                if fast >= 0x80 and Y < 0x50 and not auto:
                    if A >= TRIG:
                        auto = 0x40
                        trig = k
                    else:
                        t = sub + fr
                        sub = t & 0xFF
                        scroll = 256 - fast - (t >> 8)
                X += 1
        elif d < 0:
            if X >= XMIN:
                X -= 1
        if auto:
            auto -= 1
            A += 1
            Y += 1
        else:
            A += scroll
        if Y >= 0xE8:
            return None, X, Y, sub, A, v, trig
        if stop_at is not None and k >= stop_at:
            return None, X, Y, sub, A, v, trig
        k += 1
    return None, X, Y, sub, A, v, trig


@lru_cache(maxsize=20000)
def pre_scroll(Y0, sub0, ds0):
    """Frames before the scroll phase (Y >= $50 at the start of the frame). Returns groups
    {(k_s, sub_s, bonus, Ypin): [(ds_s, dx_s, dirs)]}: the scroll phase starts on frame k_s with $94 = sub_s."""
    if Y0 < 0x50:
        return {(1, sub0, 0, Y0): [(ds0, 0, ())]}
    out = {}
    front = {(ds0, 0): (Y0, sub0, ())}
    k = 1
    while front and k <= KR:
        fr, fh = FR[k], FH[k]
        nf = {}
        for (ds, dx), (Y, sub, dirs) in front.items():
            t = sub + fr
            ns = t & 255
            nY = Y + fh - 256 + (t >> 8)
            for nds, d in DSN[ds]:
                if nY < 0x50:
                    if d > 0:
                        t2 = ns + fr
                        key = (k + 1, t2 & 255, RISE[k] - (t2 >> 8), nY)
                    else:
                        key = (k + 1, ns, 0, nY)
                    g = out.setdefault(key, {})
                    g.setdefault((nds, dx + d), dirs + (d,))
                else:
                    nf.setdefault((nds, dx + d), (nY, ns, dirs + (d,)))
        front = nf
        k += 1
    res = {key: [(ds, dx, dirs) for (ds, dx), dirs in g.items()] for key, g in out.items()}
    if front:                                            # never reached the scroll line
        (Y, sub, _d) = next(iter(front.values()))
        res[(KR + 1, sub, 0, Y)] = [(ds, dx, dirs) for (ds, dx), (_y, _s, dirs) in front.items()]
    return res


class Planner:
    def __init__(self, mp: Map | None = None, seed: int = 1):
        self.mp = mp or Map()
        self.rows = self.mp.rows
        self.rng = random.Random(seed)
        self.B = table()

    # ------------------------------------------------------------------ one jump
    def jumps(self, X0, Y0, sub0, A0, ds0, targets, nvar=2, nT=4, extra=0):
        """Candidate jumps from a standing state. targets = [(q, x0, x1)] floor segments above.
        ds0: direction state before the first airborne frame (0 = nothing held on the A frame).
        Returns [(frames, X, Y, sub, A, q, dirs)] (frames = A-press frame + airborne frames incl. the landing)."""
        q0 = (Y0 + 16 - A0) >> 4
        B = self.B
        res = {}
        groups = pre_scroll(Y0, sub0, ds0)
        for (ks, sub_s, bonus, Yp), entries in groups.items():
            pre_rise = Y0 - Yp
            dsa = np.array([e[0] for e in entries])
            dxa = np.array([e[1] for e in entries])
            if ks <= KR:
                M = B[ks, sub_s][dsa]                       # (E, 61) masks over c
                allc = int(np.bitwise_or.reduce(M, axis=None))
            else:
                M = None
                allc = 1
            base_rise = pre_rise + bonus + SUMR[ks]
            for (tq, xa, xb) in targets:
                h = (q0 - tq) * 16
                # measured on the model: a landing h px up needs a total rise of at least h + 3
                cs = [c for c in range(30) if (allc >> c) & 1 and h + 3 + extra <= base_rise - c]
                if not cs:
                    continue
                cs.sort(reverse=True)                       # most carries first = lowest peak = earliest landing
                if len(cs) > 5:                             # lowest three, the middle one, the highest
                    cs = cs[:3] + [cs[(len(cs) + 2) // 2], cs[-1]]
                for c in cs:
                    if M is None:
                        tot = {int(dx): (i, 0) for i, dx in enumerate(dxa)}
                    else:
                        ei, di = np.nonzero((M >> c) & 1)
                        tot = {}
                        for i, d in zip(ei.tolist(), di.tolist()):
                            T = int(dxa[i]) + d - DXO
                            if T not in tot:
                                tot[T] = (i, d - DXO)
                    F = TAIR.get(h, 40) - KR + 4
                    lo, hi = xa - X0 - F, xb - X0 + F
                    Ts = sorted(T for T in tot if lo <= T <= hi and XMIN - 1 <= X0 + T <= XMAX)
                    if not Ts:
                        continue
                    mid = (xa + xb) // 2 - X0
                    pick = {Ts[0], Ts[-1], min(Ts, key=lambda T: abs(T - mid)), min(Ts, key=abs)}
                    if len(Ts) > 4:
                        pick.add(Ts[len(Ts) // 3])
                        pick.add(Ts[2 * len(Ts) // 3])
                    for T in sorted(pick)[:nT + 2]:
                        i, dxs = tot[T]
                        ds_s, dx_s, pdirs = entries[i]
                        for var in range(nvar):
                            if M is None:
                                rdirs, sub_e, ds_e = (), sub_s, ds_s
                                if var:
                                    break
                            else:
                                rec = reconstruct(ks, sub_s, ds_s, dxs, c, var)
                                if rec is None:
                                    continue
                                rdirs, sub_e, ds_e = rec
                            dirs = pdirs + rdirs
                            self._falls(X0, Y0, sub0, A0, dirs, ds_e, q0 + (1 if tq == q0 else 0), res)
        return list(res.values())

    def _falls(self, X0, Y0, sub0, A0, dirs, ds_e, q0, res):
        """Simulate the rise exactly, then a few direction plans for the fall. Keeps landings on any row above
        the take-off row. No new direction press in the last 5 frames before landing."""
        rows = self.rows
        n = len(dirs)
        k, X, Y, sub, A, v, trig = run_air(X0, Y0, sub0, A0, dirs, rows, stop_at=n)
        if k is not None:
            return
        plans = [((ds_dir(ds_e),), None)]
        if ds_e == 0:
            for j in (0, 5, 10):
                plans.append(((0,) * j + (1,), n + 1 + j))
                plans.append(((0,) * j + (-1,), n + 1 + j))
        else:
            d, a, lp = ds_parts(ds_e)
            j0 = 0
            while not (a + j0 >= 2 and a + j0 + lp >= 5):
                j0 += 1
            for j in (j0, j0 + 3, j0 + 6, j0 + 10, j0 + 15):
                plans.append(((d,) * j + (-d,), n + 1 + j))
        for fd, sw in plans:
            kl, X2, Y2, sub2, A2, v2, tr2 = run_air(X, Y, sub, A, fd, rows, k0=n + 1, v=v)
            if kl is None:
                continue
            if sw is not None and sw > kl - 5:
                continue
            q = (Y2 + 16 - A2) >> 4
            if q >= q0:
                continue
            key = (X2, Y2, sub2, A2)
            if key in res and res[key][0] <= kl + 1:
                continue
            full = dirs + (fd + (fd[-1],) * (kl - n - len(fd)))[:kl - n]
            res[key] = (kl + 1, X2, Y2, sub2, A2, q, full)


# ---------------------------------------------------------------------------------------------- beam over ledges
class Node:
    __slots__ = ("t", "X", "Y", "sub", "A", "q", "parent", "walk", "ds0", "dirs", "tag")

    def __init__(self, t, X, Y, sub, A, parent=None, walk=0, ds0=0, dirs=None, tag=None):
        self.t, self.X, self.Y, self.sub, self.A = t, X, Y, sub, A
        self.q = (Y + 16 - A) >> 4
        self.parent, self.walk, self.ds0, self.dirs, self.tag = parent, walk, ds0, dirs, tag

    def __repr__(self):
        return f"Node(t={self.t} q={self.q} X={self.X} Y={self.Y} sub={self.sub:02x} A={self.A})"

    def path(self):
        out = []
        n = self
        while n is not None:
            out.append(n)
            n = n.parent
        return out[::-1]


def seg_of(mp: Map, q, x):
    for (a, b) in mp.segs(q):
        if a <= x <= b:
            return (a, b)
    return None


def prune(nodes, keep=30, per_bucket=2):
    """Keep the fastest nodes of one floor segment with some spread over $94 and X."""
    nodes = sorted(nodes, key=lambda n: n.t)
    out, seen, cnt = [], set(), {}
    for n in nodes:
        k = (n.X, n.Y, n.sub)
        if k in seen:
            continue
        b = (n.sub >> 4, n.X >> 4, 0 if n.Y < 80 else (1 if n.Y <= 100 else 2))
        if cnt.get(b, 0) >= per_bucket:
            continue
        cnt[b] = cnt.get(b, 0) + 1
        seen.add(k)
        out.append(n)
        if len(out) >= keep:
            break
    return out


def expand_raw(pl: Planner, t, X, Y, sub, A, targets, tlimit=None, extra=0):
    """Children of a standing state as tuples (t, X, Y, sub, A, walk, ds0, dirs). targets: [(q, xa, xb)];
    tlimit: {target: latest useful arrival} to skip take-offs that cannot matter."""
    mp = pl.mp
    q0 = (Y + 16 - A) >> 4
    seg = seg_of(mp, q0, X)
    if seg is None:
        return []
    takeoffs = {}
    for tg in targets:
        tq, xa, xb = tg
        h = (q0 - tq) * 16
        T = TAIR.get(h, 40)
        gap_r = xa - X                 # > 0: target lies to the right
        gap_l = X - xb                 # > 0: target lies to the left
        ws = set()
        if gap_r > T:
            ws.update((1, gap_r - T + e) for e in (-3, -2, -1, 0, 1, 2, 3, 4, 6, 8, 12, 16))
        elif gap_l > T:
            ws.update((-1, gap_l - T + e) for e in (-3, -2, -1, 0, 1, 2, 3, 4, 6, 8, 12, 16))
        else:
            ws.add((1, 0))
            for e in (1, 2, 3, 4, 6, 8, 11, 14, 18, 23, 28):
                ws.add((1, e))
                ws.add((-1, e))
        for wd, w in ws:
            if w < 0:
                continue
            if w == 0:
                wd = 1
            X0 = X + wd * w
            if X0 < seg[0] or X0 > seg[1] or X0 < XMIN - 1 or X0 > XMAX:
                continue
            if tlimit is not None and t + w + T - 3 > tlimit.get(tg, 10 ** 9):
                continue
            takeoffs.setdefault((wd, w), []).append(tg)
    out = []
    for (wd, w), tgs in takeoffs.items():
        X0 = X + wd * w
        ds0 = 0 if w == 0 else ds_make(wd, min(3, w + 1), 3)
        for (fr, X2, Y2, sub2, A2, q, dirs) in pl.jumps(X0, Y, sub, A, ds0, tgs, extra=extra):
            out.append((t + w + fr, X2, Y2, sub2, A2, wd * w, ds0, dirs))
    return out


_PL = None


def _winit():
    global _PL
    _PL = Planner()


def _wexp(job):
    return expand_raw(_PL, *job)


def search(pl: Planner, starts, q_end, keep=30, log=None, blocked=None, slack=30, up=4, pool=None):
    """Layered search by row from the start nodes up to row q_end (inclusive). Returns {(q, xa, xb): [nodes]}.
    pool: a multiprocessing.Pool created with initializer=_winit (optional)."""
    mp = pl.mp
    pools = {}
    best_t = {}

    def add(n):
        seg = seg_of(mp, n.q, n.X)
        if seg is None:
            return
        key = (n.q, seg[0], seg[1])
        pools.setdefault(key, []).append(n)
        if n.t < best_t.get(key, 10 ** 9):
            best_t[key] = n.t
    for n in starts:
        add(n)
    q = max(k[0] for k in pools)
    while q > q_end:
        for key in sorted(k for k in pools if k[0] == q):
            nodes = [n for n in prune(pools[key], keep) if n.t <= best_t[key] + slack]
            pools[key] = nodes
            targets = []
            for dq in range(1, up + 1):
                if q - dq < q_end:
                    break
                for (xa, xb) in mp.segs(q - dq):
                    if blocked and blocked(q - dq, xa, xb):
                        continue
                    targets.append((q - dq, xa, xb))
            if not targets:
                continue
            tl = {tg: best_t.get(tg, 10 ** 9) + slack for tg in targets}
            jobs = [(n.t, n.X, n.Y, n.sub, n.A, targets, tl) for n in nodes]
            if pool is not None and len(jobs) > 1:
                results = pool.map(_wexp, jobs)
            else:
                results = [expand_raw(pl, *j) for j in jobs]
            cnt = 0
            for n, chs in zip(nodes, results):
                for (t2, X2, Y2, sub2, A2, walk, ds0, dirs) in chs:
                    add(Node(t2, X2, Y2, sub2, A2, n, walk, ds0, dirs))
                    cnt += 1
            if log:
                log(f"row {q} seg {key[1]}-{key[2]}: {len(nodes)} nodes, best t {best_t[key]}, {cnt} children")
        q -= 1
    for key in list(pools):
        pools[key] = prune(pools[key], keep)
    return pools


def node_rows(n: Node):
    """Button rows (direction buttons and A only) for the step parent -> n: walking frames, the A frame, air
    frames. Each run of a direction holds its button on the run's first two frames, then the latch carries it."""
    rows = []
    wd = "Right" if n.walk > 0 else "Left"
    for _ in range(abs(n.walk)):
        rows.append((wd,))
    if n.ds0 == 0:
        rows.append(("A",))
        prev = 0
        run = 0
    else:
        d0 = ds_dir(n.ds0)
        rows.append((("Right" if d0 > 0 else "Left"), "A"))
        prev = d0
        run = 0
    for d in n.dirs:
        if d == 0:
            rows.append(())
            continue
        if d != prev:
            prev, run = d, 0
        run += 1
        rows.append((("Right",) if d > 0 else ("Left",)) if run <= 2 else ())
    return rows
