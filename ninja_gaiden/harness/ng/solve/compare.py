"""ng.solve.compare - where does a run lose time? Replays rows from a state and prints, per room and 32-px column,
the first frame we reach it vs the TAS (and the record's route when a record json exists), with hp / ninpo / item
changes and lantern breaks. Measures first-reach times (the beam's printed "lag" is not reliable after explores).

    python -m ng.solve.compare <start state> <rows file> [--n N] [--col 32] [--rec <json>]
"""
from __future__ import annotations

import sys

from . import common as C
from ng.mode import TICKS  # noqa: E402
import a56_common as A  # noqa: E402


def first_reach(trace, col=32):
    """{(room, col index): first frame} with the stage's direction ignored (every column touched)."""
    out = {}
    for s in trace:
        if s is None:
            continue
        k = (s["room"], C.abs_x(s) // col)
        if k not in out:
            out[k] = s["frame"]
    return out


def main(a):
    def opt(n, d):
        if n in a:
            i = a.index(n)
            v = a[i + 1]
            del a[i:i + 2]
            return type(d)(v) if d is not None else v
        return d
    n = opt("--n", 0)
    col = opt("--col", 32)
    start, rf = a[0], a[1]
    rows = C.rows_of(rf)
    rows = rows[:n] if n else rows
    e = C.open_emu("tk_compare_emu.log")
    try:
        e.tick(TICKS)
        st = e.load(start)
        tr = A.play_trace(e, rows)
    finally:
        e.close()
    f0 = st["frame"]
    stage = st["stage"]
    T = A.tas_trace()
    tc = C.tas_control(stage)
    tn = C.tas_control(stage + 1) if stage < 21 else len(T) - 1
    tas = first_reach([dict(T[k], frame=k) for k in range(tc, min(tn, len(T)))], col)
    ours = first_reach(tr, col)
    print(f"start {start} frame {f0} stage {C.NAMES[stage]}; TAS control {tc}; offset = (our f - f0) - (TAS f - tc)")
    rows_out = []
    for k, f in sorted(ours.items(), key=lambda kv: kv[1]):
        tf = tas.get(k)
        d = None if tf is None else (f - f0) - (tf - tc)
        rows_out.append((f, k, tf, d))
    prev = None
    for f, k, tf, d in rows_out:
        if prev is not None and d == prev:
            continue
        print(f"  room {k[0]:2d} X {k[1] * col:5d}: ours t {f - f0:5d}  TAS t {'-' if tf is None else tf - tc:>5}  "
              f"diff {'' if d is None else f'{d:+d}'}")
        prev = d
    p = None
    for s in tr:
        key = (s["hp"], s["ninpo"], s.get("item"), s["room"])
        if key != p:
            print(f"  f {s['frame']} t {s['frame'] - f0}: room {s['room']} X {C.abs_x(s)} y {s['y']} hp {s['hp']} "
                  f"np {s['ninpo']} item {s.get('item')}")
            p = key


if __name__ == "__main__":
    main(sys.argv[1:])
