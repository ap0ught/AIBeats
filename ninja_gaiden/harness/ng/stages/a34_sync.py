"""Acts 3-4: follow the TAS frame by frame with legal input, repairing each illegal spot by a small local search
that must bring the game back to the TAS's own RAM (zero-loss repair). Owned by the Acts 3-4 agent.

    python ng/stages/a34_sync.py <stage name> [--start <state>] [--frame0 F] [--hist <inputs>] [--out name]
                                 [--until F] [--B 4] [--F 4] [--H 30]

Algorithm (in sync = our masked RAM equals the TAS's RAM at the same frame):
  1. play the TAS rows while they stay legal given our own history;
  2. at the first illegal row v, back up B frames (ring of in-memory states) and try variants of the window
     [v-B, v+F]: per-button edits of the TAS's bit timelines (extend/shift/delete/merge presses, drop one side
     of L+R / U+D), only legal ones, cheapest first; each is followed by up to H legal TAS rows and compared with
     the TAS's RAM at the end; the first exact match wins;
  3. if nothing matches exactly, the best "loose" match (Ryu, scroll, timer, RNG, enemy slots equal) is taken and
     the strict-only differences are tolerated until they converge; if nothing matches loosely either, stop and
     report the spot (a real desync: those are solved by hand in the stage modules).
"""
from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402

T = None


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


def edits(bits, max_out=40):
    """variants of one button's bit list (cheapest first): (cost, tuple)."""
    n = len(bits)
    res = {tuple(bits): 0}

    def add(v, c):
        v = tuple(v)
        if v not in res or res[v] > c:
            res[v] = c
    rs = runs(bits)
    for (i, j) in rs:
        for d in (1, 2, 3):
            if j + d < n:
                v = list(bits); v[j + 1:j + d + 1] = [1] * d; add(v, d)
            if i - d >= 0:
                v = list(bits); v[i - d:i] = [1] * d; add(v, d)
        for d in (1, 2, -1, -2):
            v = [0] * n
            ok = True
            for k in range(i, j + 1):
                if 0 <= k + d < n:
                    v[k + d] = 1
            for k in range(n):
                if k < i or k > j:
                    v[k] = max(v[k], bits[k])
            add(v, abs(d) + 1)
        v = list(bits); v[i:j + 1] = [0] * (j - i + 1); add(v, 3)
        # make it exactly 2 long
        if j == i:
            if j + 1 < n:
                v = list(bits); v[j + 1] = 1; add(v, 1)
    for a, b in zip(rs, rs[1:]):
        v = list(bits); v[a[1] + 1:b[0]] = [1] * (b[0] - a[1] - 1); add(v, b[0] - a[1])
    # second-order: extend + extend of different runs
    base = sorted(res.items(), key=lambda kv: kv[1])
    if len(rs) >= 2:
        for (v1, c1) in base[:12]:
            for (i, j) in runs(list(v1)):
                for d in (1, 2):
                    if j + d < n:
                        v = list(v1); v[j + 1:j + d + 1] = [1] * d; add(v, c1 + d)
    out = sorted(res.items(), key=lambda kv: kv[1])
    return out[:max_out]


class Follower:
    def __init__(self, e, stage, frame0, hist=(), B=4, F=4, H=30, log=print):
        global T
        T = K.tas_rows()
        self.e, self.stage, self.B, self.F, self.H, self.log = e, stage, B, F, H, log
        self.t = frame0                    # frames emulated (framecount)
        self.L = K.Legal(hist)
        self.out = []                      # our rows for frames frame0+1 ...
        self.frame0 = frame0
        self.ring = {}                     # frame -> (msave id, Legal copy, len(out))
        self.tol = np.zeros(2048, dtype=bool)   # tolerated strict differences (after a loose repair)
        self.repairs = []
        self.snap()

    # ring of states
    def snap(self):
        if self.t in self.ring:
            self.e.mfree(self.ring[self.t][0])
        sid = self.e.msave()
        self.ring[self.t] = (sid, self.L.copy(), len(self.out))
        for f in [f for f in self.ring if f < self.t - 40]:
            self.e.mfree(self.ring[f][0])
            del self.ring[f]

    def ring_at(self, f):
        ks = [k for k in self.ring if k <= f]
        return max(ks) if ks else min(self.ring)

    def restore(self, f):
        sid, L, n = self.ring[f]
        self.e.mload(sid)
        self.t, self.L = f, L.copy()
        del self.out[n:]
        for g in [g for g in self.ring if g > f]:
            self.e.mfree(self.ring[g][0])
            del self.ring[g]

    def push(self, rows, snap_each=False):
        if snap_each:
            for r in rows:
                self.L.push(r)
                self.e.step(r) if r else self.e.step((), 1)
                self.t += 1
                self.out.append(tuple(r))
                self.snap()
        else:
            for r in rows:
                self.L.push(r)
            if rows:
                self.e.run(rows)
            self.t += len(rows)
            self.out.extend(tuple(r) for r in rows)

    def mask(self):
        return K.STRICT & ~self.tol

    def compare(self, f):
        r = K.ram_np(self.e.ram_all())
        ref = K.ref_at(f)
        d_strict = K.diff(r, ref, self.mask())
        d_loose = K.diff(r, ref, K.LOOSE)
        return d_strict, d_loose, r

    def legal_prefix(self, start, L, limit):
        """how many TAS rows from frame start+1 are legal as they are, given tracker L (not modified)."""
        L2 = L.copy()
        k = 0
        while k < limit and L2.ok(T[start + k]):
            L2.push(T[start + k])
            k += 1
        return k

    def step_to(self, end):
        """advance in sync to `end` (framecount) or to the frame before the first illegal TAS row.
        Returns the frame of the illegal row (1-based frame number) or None."""
        k = self.legal_prefix(self.t, self.L, end - self.t)
        n_fast = max(0, k - self.B - 1)
        self.push(T[self.t:self.t + n_fast])
        self.snap()
        rest = k - n_fast
        self.push(T[self.t:self.t + rest], snap_each=True)
        if self.t >= end:
            return None
        return self.t + 1

    def window_variants(self, a, b, L):
        """candidate row lists for frames a+1..b (0-based T[a:b]); cheapest first."""
        rows = [set(r) for r in T[a:b]]
        n = b - a
        # involved buttons: those that a greedy scan finds in a violation
        inv = set()
        L2 = L.copy()
        for r in T[a:b + 2]:
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
        inv = sorted(inv)
        per = {}
        for bt in inv:
            bits = [1 if bt in r else 0 for r in rows]
            opts = edits(bits)
            o = OPPB.get(bt)
            if o:
                conf = [1 if (bt in r and o in r) else 0 for r in rows]
                if any(conf):
                    nb = [x & (1 - c) for x, c in zip(bits, conf)]
                    for v, c in edits(nb):
                        opts.append((v, c + 1))
                    opts.append((tuple([0] * n), 4))
            # dedupe, keep min cost
            m = {}
            for v, c in opts:
                if v not in m or m[v] > c:
                    m[v] = c
            per[bt] = sorted(m.items(), key=lambda kv: kv[1])[:30]
        combos = []
        for choice in itertools.product(*[per[bt] for bt in inv]):
            cost = sum(c for _, c in choice)
            new = [set(r) - set(inv) for r in rows]
            for bt, (v, _) in zip(inv, choice):
                for k in range(n):
                    if v[k]:
                        new[k].add(bt)
            cand = [tuple(x for x in K.BTNS if x in s) for s in new]
            combos.append((cost, cand))
        combos.sort(key=lambda x: x[0])
        return inv, combos

    def repair(self, v, max_eval=400):
        """v = 1-based frame number of the first illegal TAS row; we are at framecount v-1."""
        a = self.ring_at(v - 1 - self.B)
        b = v - 1 + self.F + 1
        best_loose = None
        tries = 0
        t0 = time.time()
        for widen in range(3):
            self.restore(a)
            L0 = self.L.copy()
            inv, combos = self.window_variants(a, b, L0)
            for cost, cand in combos:
                L2 = L0.copy()
                ok = True
                for r in cand:
                    if not L2.ok(r):
                        ok = False
                        break
                    L2.push(r)
                if not ok:
                    continue
                k = self.legal_prefix(b, L2, self.H)
                tail = T[b:b + k]
                tries += 1
                self.e.mload(self.ring[a][0])
                self.e.run(list(cand) + list(tail))
                f = b + k
                ds, dl, _ = self.compare(f)
                if len(ds) == 0:
                    self.restore(a)
                    self.push(cand, snap_each=True)
                    self.repairs.append({"frame": v, "window": [a + 1, b], "kind": "exact", "cost": cost,
                                         "tries": tries, "buttons": inv})
                    self.tol[:] = False
                    return True
                if len(dl) == 0 and (best_loose is None or len(ds) < best_loose[0]):
                    best_loose = (len(ds), cost, cand, ds)
                if tries >= max_eval:
                    break
            if best_loose or tries >= max_eval:
                break
            # widen the window
            a = self.ring_at(a - 3)
            b = b + 3
        if best_loose:
            nds, cost, cand, ds = best_loose
            self.restore(a)
            self.push(cand, snap_each=True)
            self.tol[ds] = True
            self.repairs.append({"frame": v, "window": [a + 1, b], "kind": "loose", "strict_diff": [hex(x) for x in ds],
                                 "cost": cost, "tries": tries, "buttons": inv})
            return True
        self.restore(a)
        self.repairs.append({"frame": v, "window": [a + 1, b], "kind": "FAILED", "tries": tries})
        return False

    def follow(self, end):
        while self.t < end:
            v = self.step_to(end)
            if v is None:
                break
            ok = self.repair(v)
            r = self.repairs[-1]
            self.log(f"  repair at {v}: {r['kind']} tries={r['tries']} window={r['window']} {r.get('buttons', '')}"
                     + (f" tol={r.get('strict_diff')}" if r['kind'] == 'loose' else ""))
            if not ok:
                return False
        return True


OPPB = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}


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
    until = opt("--until", c1 + 0)
    out = opt("--out", f"sync_{name}")
    B, F, H = opt("--B", 4), opt("--F", 4), opt("--H", 30)
    e = K.open_emu(f"a34_sync_{name}.log")
    try:
        s = e.load(state)
        print("start", s.frame, "stage", s.stage, "x", s.x, "y", s.y, flush=True)
        fo = Follower(e, st, s.frame, (), B, F, H, log=lambda m: print(m, flush=True))
        t = time.time()
        ok = fo.follow(until)
        print("followed to", fo.t, "ok", ok, "repairs", len(fo.repairs), "secs", round(time.time() - t))
        K.save_rows(out, fo.out, f"from {state} frame {fo.frame0} to {fo.t} ok={ok}")
        import json
        (K.OUT_DIR / f"{out}.repairs.json").write_text(json.dumps(fo.repairs, indent=1))
    finally:
        e.close()


if __name__ == "__main__":
    main()
