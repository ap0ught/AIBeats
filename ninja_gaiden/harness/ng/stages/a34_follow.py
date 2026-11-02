"""Acts 3-4: follow the TAS with legal input, frame by frame, with TIME-SHIFTED sync. Owned by the Acts 3-4 agent.

    python ng/stages/a34_follow.py <stage> [--start <state>] [--prefix <our inputs from the state>] [--d D]
                                   [--out name] [--until F] [--maxextra 3] [--hist <inputs>]

In sync with offset d = our RAM after our frame f equals the TAS's RAM after TAS frame f-d, except the bytes that
only count time ($BF RNG, $62/$63 timer, $3E HUD phase) when d > 0, and except "tolerated" bytes after a loose
repair. Our row for frame f is the TAS row of frame f-d whenever that is legal. At an illegal row the window
around it is searched: first edits that keep d (zero loss), then the same with 1, 2, ... frames inserted (each
inserted frame = one frame lost). The cheapest variant that comes back into sync (checked against the TAS RAM at
the end of a horizon of legal TAS rows) wins.
"""
from __future__ import annotations

import heapq
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402

T = None
SHIFTX = np.zeros(2048, dtype=bool)
SHIFTX[[0x3E, 0x62, 0x63, 0xBF]] = True


def runs(bits):
    out, i, n = [], 0, len(bits)
    while i < n:
        if bits[i]:
            j = i
            while j + 1 < n and bits[j + 1]:
                j += 1
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def edits(bits, max_out=24):
    """variants of one button's bit list, cheapest first: [(tuple, cost)]."""
    n = len(bits)
    res = {tuple(bits): 0}

    def add(v, c):
        v = tuple(v)
        if v not in res or res[v] > c:
            res[v] = c
    rs = runs(bits)
    for (i, j) in rs:
        for d in (1, 2):
            if j + d < n:
                v = list(bits); v[j + 1:j + d + 1] = [1] * d; add(v, d)
            if i - d >= 0:
                v = list(bits); v[i - d:i] = [1] * d; add(v, d)
            if j - i + 1 > d:
                v = list(bits); v[j - d + 1:j + 1] = [0] * d; add(v, d + 1)     # shorten end
                v = list(bits); v[i:i + d] = [0] * d; add(v, d + 1)             # start later
        for d in (1, -1, 2, -2):
            v = list(bits)
            for k in range(i, j + 1):
                v[k] = 0
            for k in range(i, j + 1):
                if 0 <= k + d < n:
                    v[k + d] = 1
            add(v, abs(d) + 1)
        v = list(bits); v[i:j + 1] = [0] * (j - i + 1); add(v, 4)
    for a, b in zip(rs, rs[1:]):
        v = list(bits); v[a[1] + 1:b[0]] = [1] * (b[0] - a[1] - 1); add(v, b[0] - a[1])
    base = sorted(res.items(), key=lambda kv: kv[1])
    if len(rs) >= 2 or True:
        for (v1, c1) in base[:10]:
            for (i, j) in runs(list(v1)):
                for d in (1, 2):
                    if j + d < n:
                        v = list(v1); v[j + 1:j + d + 1] = [1] * d; add(v, c1 + d)
                    if i - d >= 0:
                        v = list(v1); v[i - d:i] = [1] * d; add(v, c1 + d)
    return sorted(res.items(), key=lambda kv: kv[1])[:max_out]


def cheapest_products(lists, limit):
    """lazily yield (cost, choice tuple) over the product of lists of (item, cost), cheapest first."""
    if not lists:
        yield 0, ()
        return
    start = tuple([0] * len(lists))
    seen = {start}
    h = [(sum(l[0][1] for l in lists), start)]
    n = 0
    while h and n < limit:
        c, idx = heapq.heappop(h)
        yield c, tuple(lists[k][i][0] for k, i in enumerate(idx))
        n += 1
        for k in range(len(lists)):
            if idx[k] + 1 < len(lists[k]):
                nidx = idx[:k] + (idx[k] + 1,) + idx[k + 1:]
                if nidx not in seen:
                    seen.add(nidx)
                    heapq.heappush(h, (sum(lists[q][i][1] for q, i in enumerate(nidx)), nidx))


class Follower:
    def __init__(self, e, frame0, d=0, hist=(), B=4, F=4, H=30, maxextra=3, log=print, max_eval=(160, 160, 120, 80)):
        global T
        T = K.tas_rows()
        self.e, self.B, self.F, self.H, self.log = e, B, F, H, log
        self.maxextra, self.max_eval = maxextra, max_eval
        self.t, self.d = frame0, d
        self.L = K.Legal(hist)
        self.out = []
        self.frame0 = frame0
        self.ring = {}
        self.tol = np.zeros(2048, dtype=bool)
        self.repairs = []
        self.snap()

    # --- TAS mapping ---
    def trow(self, f, d=None):
        """TAS row for our 1-based frame f under offset d."""
        d = self.d if d is None else d
        return T[f - 1 - d]

    def mask(self, d=None):
        d = self.d if d is None else d
        m = K.STRICT & ~self.tol
        if d:
            m = m & ~SHIFTX
        return m

    # --- states ---
    def snap(self):
        if self.t in self.ring:
            self.e.mfree(self.ring[self.t][0])
        sid = self.e.msave()
        self.ring[self.t] = (sid, self.L.copy(), len(self.out), self.d, self.tol.copy())
        for f in [f for f in self.ring if f < self.t - 60]:
            self.e.mfree(self.ring[f][0])
            del self.ring[f]

    def ring_at(self, f):
        ks = [k for k in self.ring if k <= f]
        return max(ks) if ks else min(self.ring)

    def restore(self, f):
        sid, L, n, d, tol = self.ring[f]
        self.e.mload(sid)
        self.t, self.L, self.d, self.tol = f, L.copy(), d, tol.copy()
        del self.out[n:]
        for g in [g for g in self.ring if g > f]:
            self.e.mfree(self.ring[g][0])
            del self.ring[g]

    def push(self, rows, snap_each=False):
        rows = [tuple(r) for r in rows]
        if snap_each:
            for r in rows:
                self.L.push(r)
                self.e.step(r) if r else self.e.step((), 1)
                self.t += 1
                self.out.append(r)
                self.snap()
        else:
            for r in rows:
                self.L.push(r)
            if rows:
                self.e.run(rows)
            self.t += len(rows)
            self.out.extend(rows)

    def compare(self, f, d=None):
        d = self.d if d is None else d
        r = K.ram_np(self.e.ram_all())
        ref = K.ref_at(f - d)
        return K.diff(r, ref, self.mask(d)), K.diff(r, ref, K.LOOSE & ~(SHIFTX if d else False)), r

    def legal_prefix(self, f_next, L, limit, d=None):
        """number of TAS rows (offset d) from our frame f_next on that are legal as they are given tracker L."""
        L2 = L.copy()
        k = 0
        while k < limit and L2.ok(self.trow(f_next + k, d)):
            L2.push(self.trow(f_next + k, d))
            k += 1
        return k

    def step_to(self, end):
        k = self.legal_prefix(self.t + 1, self.L, end - self.t)
        n_fast = max(0, k - self.B - 1)
        if n_fast:
            self.push([self.trow(self.t + 1 + i) for i in range(n_fast)])
            ds, dl, _ = self.compare(self.t)
            if len(ds):
                self.log(f"  ! silent divergence by frame {self.t} (d={self.d}): {[hex(x) for x in ds[:12]]}")
                self.tol[ds] = True
        self.snap()
        rest = k - n_fast
        self.push([self.trow(self.t + 1 + i) for i in range(rest)], snap_each=True)
        if self.t >= end:
            return None
        return self.t + 1

    # --- candidates ---
    def involved(self, rows, L):
        inv = set()
        L2 = L.copy()
        for r in rows:
            for w in L2.reasons(r):
                if w == "L+R":
                    inv |= {"Left", "Right"}
                elif w == "U+D":
                    inv |= {"Up", "Down"}
                else:
                    inv.add(w.split()[-1])
            L2.push(r)
        for p, q in (("Left", "Right"), ("Up", "Down")):
            if p in inv or q in inv:
                inv |= {p, q}
        return sorted(inv)

    def variants(self, base, inv, limit):
        """edits of base rows on the involved buttons, cheapest first: yields (cost, rows)."""
        n = len(base)
        sets = [set(r) for r in base]
        per = []
        for bt in inv:
            bits = [1 if bt in s else 0 for s in sets]
            opts = edits(bits)
            o = K.OPP.get(bt)
            if o:
                conf = [1 if (bt in s and o in s) else 0 for s in sets]
                if any(conf):
                    nb = [x & (1 - c) for x, c in zip(bits, conf)]
                    opts += [(v, c + 1) for v, c in edits(nb)]
                    opts.append((tuple([0] * n), 5))
            m = {}
            for v, c in opts:
                if v not in m or m[v] > c:
                    m[v] = c
            per.append(sorted(m.items(), key=lambda kv: kv[1])[:24])
        for cost, choice in cheapest_products(per, limit):
            new = [s - set(inv) for s in sets]
            for bt, v in zip(inv, choice):
                for k in range(n):
                    if v[k]:
                        new[k].add(bt)
            yield cost, [tuple(x for x in K.BTNS if x in s) for s in new]

    def try_cand(self, a, cand, d_new, L0):
        """play cand from ring state a, then legal TAS rows (offset d_new); return (strict diff, loose diff, f)."""
        L2 = L0.copy()
        for r in cand:
            if not L2.ok(r):
                return None
            L2.push(r)
        f_next = a + len(cand) + 1
        k = self.legal_prefix(f_next, L2, self.H, d_new)
        tail = [self.trow(f_next + i, d_new) for i in range(k)]
        if k < 6:
            # too short to judge: continue with the nearest legal rows
            L3 = L2.copy()
            for r in tail:
                L3.push(r)
            tail += K.greedy_legal([self.trow(f_next + k + i, d_new) for i in range(self.H - k)], L3)
        self.e.mload(self.ring[a][0])
        self.e.run(list(cand) + tail)
        f = a + len(cand) + len(tail)
        ds, dl, _ = self.compare(f, d_new)
        return ds, dl, f

    def repair(self, v):
        a = self.ring_at(v - 1 - self.B)
        b = v - 1 + self.F + 1
        best_loose = None
        tries = 0
        t0 = time.time()
        self.restore(a)
        L0 = self.L.copy()
        d0 = self.d
        for extra in range(0, self.maxextra + 1):
            n_ev = 0
            dn = d0 + extra
            # base rows: TAS rows of our frames a+1..b under the current offset
            base = [self.trow(f, d0) for f in range(a + 1, b + 1)]
            inv = self.involved(base, L0)
            bases = []
            if extra == 0:
                bases.append((0, base))
            else:
                n = len(base)
                for p in range(n + 1):
                    prev = base[p - 1] if p > 0 else (self.out[-1] if self.out else ())
                    nodir = tuple(x for x in prev if x not in ("Left", "Right"))
                    for kind, ins in ((0, prev), (1, ()), (1, nodir)):
                        bases.append((kind + abs(p - (v - 1 - a)) * 0.1, base[:p] + [ins] * extra + base[p:]))
                bases.sort(key=lambda x: x[0])
            per_base = max(4, self.max_eval[min(extra, len(self.max_eval) - 1)] // max(1, len(bases)) * 3)
            seen = set()
            cands = []
            for bc, bb in bases:
                inv2 = self.involved(bb, L0) or inv
                for c, cand in self.variants(bb, inv2, per_base):
                    key = tuple(cand)
                    if key in seen:
                        continue
                    seen.add(key)
                    cands.append((c + bc, cand))
            cands.sort(key=lambda x: x[0])
            for c, cand in cands:
                if n_ev >= self.max_eval[min(extra, len(self.max_eval) - 1)]:
                    break
                res = self.try_cand(a, cand, dn, L0)
                if res is None:
                    continue
                n_ev += 1
                tries += 1
                ds, dl, f = res
                if len(ds) == 0:
                    self.restore(a)
                    self.d = dn
                    self.push(cand, snap_each=True)
                    self.tol[:] = False
                    self.repairs.append({"frame": v, "window": [a + 1, a + len(cand)], "kind": "exact", "extra": extra,
                                         "d": dn, "cost": c, "tries": tries, "buttons": inv,
                                         "secs": round(time.time() - t0, 1)})
                    return True
                if len(dl) == 0 and (best_loose is None or len(ds) < best_loose[0]):
                    best_loose = (len(ds), c, cand, ds, dn, extra)
            if best_loose:
                break
        if best_loose:
            nds, c, cand, ds, dn, extra = best_loose
            self.restore(a)
            self.d = dn
            self.push(cand, snap_each=True)
            self.tol[ds] = True
            self.repairs.append({"frame": v, "window": [a + 1, a + len(cand)], "kind": "loose", "extra": extra, "d": dn,
                                 "strict_diff": [hex(x) for x in ds], "cost": c, "tries": tries, "buttons": inv,
                                 "secs": round(time.time() - t0, 1)})
            return True
        self.restore(a)
        self.repairs.append({"frame": v, "window": [a + 1, b], "kind": "FAILED", "tries": tries, "d": d0,
                             "secs": round(time.time() - t0, 1)})
        return False

    def follow(self, end):
        """end: our framecount to reach (TAS frame end - d at the time... we simply stop at our frame `end`)."""
        while self.t < end:
            v = self.step_to(end)
            if v is None:
                break
            ok = self.repair(v)
            r = self.repairs[-1]
            self.log(f"  repair at {v}: {r['kind']} d={r['d']} tries={r['tries']} window={r['window']} "
                     f"{r.get('buttons', '')} {r['secs']}s" + (f" tol={r.get('strict_diff')}" if r['kind'] == 'loose' else ""))
            if not ok:
                return False
        return True


def main():
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            val = args[i + 1]
            del args[i:i + 2]
            return type(default)(val) if default is not None else val
        return default
    name = args[0]
    st = K.BY_NAME[name]
    _, c0, c1, state = K.STAGES[st]
    state = opt("--start", state)
    prefix = opt("--prefix", "")
    d = opt("--d", 0)
    until = opt("--until", c1 + 40)
    out = opt("--out", f"follow_{name}")
    maxextra = opt("--maxextra", 3)
    e = K.open_emu(f"a34_follow_{name}.log")
    try:
        s = e.load(state)
        print("start", s.frame, "stage", s.stage, "x", s.x, "y", s.y, flush=True)
        pre = K.load_rows(prefix) if prefix else []
        if pre:
            e.run(pre)
        fo = Follower(e, s.frame + len(pre), d, pre, maxextra=maxextra, log=lambda m: print(m, flush=True))
        fo.out = list(pre)
        fo.ring.clear()
        fo.snap()
        t = time.time()
        ok = fo.follow(until)
        print("followed to", fo.t, "d", fo.d, "ok", ok, "repairs", len(fo.repairs), "secs", round(time.time() - t))
        K.save_rows(out, fo.out, f"from {state} frame {s.frame} to {fo.t} d={fo.d} ok={ok}")
        (K.OUT_DIR / f"{out}.repairs.json").write_text(json.dumps(fo.repairs, indent=1))
    finally:
        e.close()


if __name__ == "__main__":
    main()
