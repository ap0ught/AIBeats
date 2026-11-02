"""Go-explore a short route segment with legal rows: earliest arrival in a goal box (room, X >= gx, y in [ylo, yhi]).

    python ng/stages/a12r2_goex.py <start state> --history <legal inputs from power-on to the start>
        [--prefix <inputs> --prefix-frames N] --goal room,gx,ylo,yhi [--iters 6000] [--tag t] [--seed 1]

Archive: cells (X/8, y/8, hp) -> the earliest node; pick cells with weight exp((X - 1.5 (f - f0) - best)/24) /
sqrt(1 + times chosen); expand one random macro (a56_beam MACROS8 + DIRS_MACRO + wall-jump cycles, 4-8 frames).
Every row goes through the legal Enforcer. Output: logs/a12r2_goex_<tag>.inputs.txt = prefix + found rows
(rows from the frame after the start state), the goal frame in the header.
"""
from __future__ import annotations

import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import a56_common as C  # noqa: E402
from a56_beam import MACROS8, DIRS_MACRO, macro_rows  # noqa: E402

from ng import legal  # noqa: E402
from ng.inputs import read_inputs, write_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

EXTRA = [("^", "Right", "Left", 2), ("^", "Left", "Right", 2), ("Up", "B"), ("Right", "Up", "B"), ("Down",),
         ("Right", "Down")]


def opt(a, n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v) if d is not None else v
    return d


def main():
    a = sys.argv[1:]
    histf = opt(a, "--history", None)
    pre = opt(a, "--prefix", None)
    pre_n = opt(a, "--prefix-frames", 0)
    goal = [int(v) for v in opt(a, "--goal", "0,0,0,255").split(",")]
    iters = opt(a, "--iters", 6000)
    tag = opt(a, "--tag", "t")
    seed = opt(a, "--seed", 1)
    hp_min = opt(a, "--hp-min", 1)
    TEMP = opt(a, "--temp", 24.0)
    start = a[0]
    rnd = random.Random(seed)
    history = [tuple(r) for r in read_inputs(histf)] if histf else []
    prefix = [tuple(r) for r in read_inputs(pre)[:pre_n]] if pre else []
    macros = list(MACROS8) + list(DIRS_MACRO) + EXTRA
    e = C.open_emu(f"a12r2_goex_{tag}.log")
    out = ROOT / "logs" / f"a12r2_goex_{tag}.inputs.txt"
    try:
        e.tick(TICKS)
        e.load(start)
        st = e.run(prefix) if prefix else e.state()
        f0 = st["frame"]
        en = C.Enforcer((history + prefix)[-1900:])
        room0, gx, ylo, yhi = goal
        arch = {}
        chosen = {}

        def cell(s):
            return (s["room"], C.abs_x(s) // 8, s["y"] // 8, s["hp"])

        recj = opt(a, "--rec", None)
        if recj:
            # value = minus the lag behind the record's route: max over record points (t, X, y) of
            # (f_rec0 + t) - 0.75 |dX| - 0.5 |dy| - frame, f_rec0 = the stage's control frame (--rec-f0)
            wp = legal.Waypoints(recj, opt(a, "--stage", 0))
            rf0 = opt(a, "--rec-f0", 174)
            P = [(rf0 + t, rm, X, y) for t, rm, X, y in wp.pts]

            def val(s):
                ax, y, rm = C.abs_x(s), s["y"], s["room"]
                return max(k - 0.75 * abs(ax - X) - 0.5 * abs(y - yy) for k, r2, X, yy in P
                           if r2 == rm and abs(ax - X) < 80) - s["frame"] if any(
                    r2 == rm and abs(ax - X) < 80 for k, r2, X, yy in P) else -1e9
        else:
            def val(s):
                return C.abs_x(s) - 1.5 * (s["frame"] - f0)

        root = (e.msave(), en, [], st, val(st))
        arch[cell(st)] = root
        best = None
        t0 = time.time()
        for it in range(iters):
            cells = list(arch)
            bv = max(arch[c][4] for c in cells)
            w = [math.exp((arch[c][4] - bv) / TEMP) / math.sqrt(1 + chosen.get(c, 0)) for c in cells]
            c = rnd.choices(cells, weights=w)[0]
            chosen[c] = chosen.get(c, 0) + 1
            sid, en0, rows0, s0, _v = arch[c]
            if best is not None and s0["frame"] >= best[0]:
                continue
            m = rnd.choice(macros)
            n = rnd.randint(4, 8)
            en1 = en0.copy()
            rows = [en1.emit(r) for r in macro_rows(m, n)]
            e.mload(sid)
            e.trace(True)
            e.run(rows)
            tr = e.last_trace
            if any(s.get("dw") or s.get("hp", 1) < hp_min or s.get("dead", 0) & 0x80 for s in tr):
                continue
            hit = next((i for i, s in enumerate(tr) if s["room"] == room0 and C.abs_x(s) >= gx and ylo <= s["y"] <= yhi),
                       None)
            if hit is not None:
                fr = tr[hit]["frame"]
                if best is None or fr < best[0]:
                    best = (fr, rows0 + rows[:hit + 1], tr[hit])
                    print(f"{time.strftime('%H:%M:%S')} it {it} GOAL at frame {fr} (+{fr - f0}) X {C.abs_x(tr[hit])} "
                          f"y {tr[hit]['y']} hp {tr[hit]['hp']}", flush=True)
                    write_inputs(out, prefix + best[1], f"a12r2 goex {tag}: goal {goal} reached on frame {fr}; "
                                                       f"start {start} + prefix {len(prefix)}")
                continue
            last = tr[-1]
            ck = cell(last)
            if ck not in arch or last["frame"] < arch[ck][3]["frame"]:
                if ck in arch:
                    e.mfree(arch[ck][0])
                arch[ck] = (e.msave(), en1, rows0 + rows, last, val(last))
            if it % 250 == 0:
                bq = max(arch.values(), key=lambda q: q[4]); bc = bq[3]
                write_inputs(ROOT / 'logs' / f'a12r2_goex_{tag}.best.inputs.txt', prefix + bq[2], f'best-progress cell, frame {bc["frame"]}')
                print(f"{time.strftime('%H:%M:%S')} it {it} cells {len(arch)} best-progress X {C.abs_x(bc)} y {bc['y']} "
                      f"f {bc['frame']} lag {-bq[4]:.0f} goal {best[0] if best else None} {time.time() - t0:.0f}s", flush=True)
        print("BEST", best[0] if best else None, flush=True)
    finally:
        e.close()


if __name__ == "__main__":
    main()
