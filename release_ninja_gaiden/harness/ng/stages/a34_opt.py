"""Acts 3-4: optimise a short legal input sequence by mutation (hill climbing) against a rollout objective.
Used for boss fights (objective = the frame the boss HP $0497 reaches 0) and for short stage pieces
(objective = the frame a predicate first holds). Owned by the Acts 3-4 agent.

    python ng/stages/a34_opt.py boss <stage> [--start state] [--prefix name] [--hist name] [--n 150]
                                [--iters 1500] [--out name] [--seed 1] [--init name]

Every candidate is the full row list, made legal frame by frame (a34_core.greedy_legal with the history), so
every evaluated sequence is a legal one. Mutations: overwrite a random window (1-10 frames) with a primitive
move or with TAS rows (time-shifted), delete a frame, insert a frame. A candidate is accepted when its objective
is not worse (plateaus are walked).
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402

R = lambda *a: tuple(a)  # noqa: E731
PRIM = [R("Right"), R("Left"), (), R("A"), R("Right", "A"), R("Left", "A"), R("B"), R("Down", "B"), R("Right", "B"),
        R("Left", "B"), R("Up", "B"), R("Down"), R("Down", "Left"), R("Down", "Right"), R("Up")]


class BossObjective:
    def __init__(self, e, base_sid, stage, n):
        self.e, self.sid, self.stage, self.n = e, base_sid, stage, n

    def __call__(self, rows):
        """(kill frame index (1-based) or a big number, -damage score, -ryu hp). Smaller is better.
        damage score = sum over boss HP losses of (frames left in the window after the loss): early hits count more."""
        self.e.mload(self.sid)
        self.e.trace(True)
        self.e.run(rows)
        tr = self.e.last_trace
        self.e.trace(False)
        n = len(tr)
        dmg = 0
        prev = None
        for i, s in enumerate(tr):
            if (s["dead"] & 0x80) or s["hp"] == 0:
                return (10 ** 6, 0, 0)
            b = s["boss_real"] if s["stage"] == self.stage else 0
            if prev is not None and b < prev:
                dmg += (prev - b) * (n - i)
            prev = b
            if b == 0:
                return (i + 1, -dmg, -s["hp"])
        return (10 ** 5, -dmg, -tr[-1]["hp"])


def mutate(rows, rng, T, f0, kill):
    rows = list(rows)
    n = len(rows)
    hi = max(4, min(n - 1, kill + 3))
    p = rng.randrange(0, hi)
    l = rng.randint(1, 10)
    m = rng.random()
    if m < 0.45:
        prim = rng.choice(PRIM)
        for k in range(p, min(n, p + l)):
            rows[k] = prim
    elif m < 0.6:
        a, b = rng.choice(PRIM), rng.choice(PRIM)
        for k in range(p, min(n, p + l)):
            rows[k] = a if (k - p) % 2 == 0 else b
    elif m < 0.8:
        sh = rng.randint(-6, 6)
        for k in range(p, min(n, p + l)):
            j = f0 + k + sh
            rows[k] = tuple(x for x in T[j] if x not in ("Up", "Down") or not ("Up" in T[j] and "Down" in T[j]))
    elif m < 0.9:
        del rows[p]
        rows.append(rows[-1])
    else:
        rows.insert(p, rows[p])
        rows.pop()
    return rows


def optimise(e, base_sid, stage, hist, init_rows, iters, T, f0, seed=1, log=print, time_limit=1e9):
    rng = random.Random(seed)
    L = K.Legal(hist)
    cur = K.greedy_legal(init_rows, L)
    obj = BossObjective(e, base_sid, stage, len(cur))
    cv = obj(cur)
    best = (cv, cur)
    log(f"init: {cv}")
    t0 = time.time()
    for it in range(iters):
        if time.time() - t0 > time_limit:
            break
        kill = cv[0] if cv[0] < 10 ** 5 else len(cur)
        cand = mutate(cur, rng, T, f0, kill)
        cand = K.greedy_legal(cand, K.Legal(hist))
        v = obj(cand)
        if v <= cv:
            if v < cv:
                log(f"  it {it}: {v}  ({time.time() - t0:.0f}s)")
            cur, cv = cand, v
            if v < best[0]:
                best = (v, cand)
    return best


def main():
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            val = args[i + 1]
            del args[i:i + 2]
            return type(default)(val) if default is not None else val
        return default
    mode, name = args[0], args[1]
    st = K.BY_NAME[name]
    _, c0, c1, tstate = K.STAGES[st]
    start = opt("--start", tstate)
    prefix = opt("--prefix", "")
    hist_n = opt("--hist", "")
    n = opt("--n", 150)
    iters = opt("--iters", 1500)
    out = opt("--out", f"opt_{name}")
    seed = opt("--seed", 1)
    init = opt("--init", "")
    T = K.tas_rows()
    e = K.open_emu(f"a34_opt_{name}.log")
    try:
        s = e.load(start)
        f_start = s.frame
        pre = K.load_rows(prefix) if prefix else []
        if pre:
            e.run(pre)
        hist = (K.load_rows(hist_n) if hist_n else []) + pre
        f0 = f_start + len(pre)            # framecount where optimisation starts
        sid = e.msave()
        if init:
            init_rows = K.load_rows(init)[len(pre):len(pre) + n]
        else:
            init_rows = [tuple(b for b in T[f0 + k] if not (("Up" in T[f0 + k] and "Down" in T[f0 + k] and b in ("Up", "Down"))
                                                           or ("Left" in T[f0 + k] and "Right" in T[f0 + k] and b in ("Left", "Right"))))
                         for k in range(n)]
        best = optimise(e, sid, st, hist, init_rows, iters, T, f0, seed, log=lambda m: print(m, flush=True))
        (v, rows) = best
        kill = v[0] if v[0] < 10 ** 5 else len(rows)
        rows = pre + rows[:kill + 2]
        K.save_rows(out, rows, f"start={start} frame0={f_start} kill at +{len(pre) + kill} (frame {f_start + len(pre) + kill})")
        print(f"best: boss dead on frame {f_start + len(pre) + kill} (TAS boss0 13824/21376); saved {out}")
    finally:
        e.close()


if __name__ == "__main__":
    main()
