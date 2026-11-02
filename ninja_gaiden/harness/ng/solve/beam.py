"""ng.solve.beam - one legal stage with the TAS-guided beam (a56_beam.StageBeam), any stage, three reference modes.

    python -m ng.solve.beam <stage> <start state> --history <power-on rows to the start> [--ref tas|record|hybrid]
        [--rec <record json>] [--ud] [--prefix <rows> --prefix-frames N] [--width 8] [--chunk 8] [--explore 4000]
        [--hours 2] [--tag t] [--no-climb] [--boss | --no-boss] [--hpw 2.0 (frames per Ryu HP lost)] [--note ..]

Reference modes:
  tas     follow the TAS 4751M (lazy: TAS rows replayed while in sync; scoring = largest TAS frame k reached)
  record  follow the record holder's route from the video (ng.legal.Waypoints; work/*/rec/r<act><stage>.json)
  hybrid  the TAS where its line is legal, the record's route spliced in around the TAS's banned moves (+ --ud: also
          around the TAS's U+D+direction air moves)
Boss stages (1-2, 2-3, 3-3, 4-4, 5-4, 6-4a, 6-4b, 6-5) use StageBeam(boss=True) (boss HP in the score, slash macros)
unless --no-boss. Every row is made legal by the a56 Enforcer (legal by construction; the result is judged again).
Output: logs/tk_<stage>_<tag>.inputs.txt / .json, states/tk_<stage>_<tag>_end.State (the next control), an entry in
logs/results.json; partial rows: states/tmp/tk_<stage>_<tag>.partial.inputs.txt (resume with --prefix).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from . import common as C
from . import results as R

import a56_common as A  # noqa: E402
from a56_beam import StageBeam  # noqa: E402
from ng import legal  # noqa: E402
from ng.mode import TICKS  # noqa: E402
from . import verify as V  # noqa: E402

BOSS_STAGES = {1, 4, 7, 11, 15, 19, 20, 21}
REC = {"1-1": "work/a12r2/rec/r11.json", "1-2": "work/a12r2/rec/r12.json", "2-1": "work/a12r2/rec/r21.json",
       "2-2": "work/a12r2/rec/r22.json", "2-3": "work/a12r2/rec/r23.json", "3-1": "work/a34r2/rec/r31.json",
       "3-2": "work/a34r2/rec/r32.json", "4-1": "work/a34r2/rec/r41.json", "4-2": "work/a34r2/rec/r42.json",
       "4-3": "work/a34r2/rec/r43.json"}


def make_ref(mode, stage, f0, rec=None, ud=False, hpad=30):
    if mode == "tas":
        return None
    rec = rec or REC.get(C.NAMES[stage])
    if not rec or not (C.PROJECT / rec).exists():
        raise SystemExit(f"no record route json for {C.NAMES[stage]} (pass --rec)")
    wp = legal.Waypoints(str(C.PROJECT / rec), stage)
    if mode == "hybrid":
        return legal.hybrid_ref(wp, f0, pad=hpad, name="hybrid_" + Path(rec).stem, ud=ud)
    return legal.waypoint_ref(wp, f0, name=Path(rec).stem)


def main(a):
    def opt(n, d):
        if n in a:
            i = a.index(n)
            v = a[i + 1]
            del a[i:i + 2]
            return type(d)(v) if d is not None else v
        return d

    def flag(n):
        if n in a:
            a.remove(n)
            return True
        return False
    mode = opt("--ref", "tas")
    rec = opt("--rec", None)
    histf = opt("--history", None)
    pre = opt("--prefix", None)
    pre_n = opt("--prefix-frames", 0)
    width = opt("--width", 8)
    chunk = opt("--chunk", 8)
    hours = opt("--hours", 2.0)
    tag = opt("--tag", "t")
    explore_n = opt("--explore", 0)
    note = opt("--note", "")
    hpw = opt("--hpw", 2.0)
    ud, noclimb, fboss, nboss = flag("--ud"), flag("--no-climb"), flag("--boss"), flag("--no-boss")
    stage, start = C.stage_index(a[0]), a[1]
    nm = C.NAMES[stage]
    out = f"tk_{nm}_{tag}"
    logf = open(C.LOGS / f"{out}.solve.log", "a", encoding="utf-8")

    def log(*x):
        s = time.strftime("%H:%M:%S ") + " ".join(str(y) for y in x)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    history = C.rows_of(histf) if histf else []
    prefix = C.rows_of(pre)[:pre_n] if pre else []
    e = C.open_emu(f"{out}_emu.log")
    try:
        e.tick(TICKS)
        st = e.load(start)
        f0 = st["frame"]
        assert not history or len(history) == f0, f"history {len(history)} rows, state frame {f0}"
        log(f"{out}: stage {nm} from {start} (frame {f0}), prefix {len(prefix)}, ref {mode} {rec or ''}, "
            f"width {width} chunk {chunk} hours {hours}")
        hist = history + prefix
        if prefix:
            assert legal.is_legal(prefix, history), "prefix not legal"
            bstart = e.run(prefix)
        else:
            bstart = st
        ref = make_ref(mode, stage, f0, rec, ud)
        boss = (stage in BOSS_STAGES or fboss) and not nboss
        b = StageBeam(e, stage, bstart, history=hist[-1900:], width=width, chunk=chunk, ref=ref, log=log, boss=boss, hp_weight=hpw)
        b.dump = C.STATES / "tmp" / f"{out}.partial.inputs.txt"
        if explore_n and not b.boss:
            b.explore_budget = explore_n
        if not b.boss and not noclimb:
            for away, back in (("Left", "Right"), ("Right", "Left")):
                for cyc in ([(away, "A"), (away, "A")] + [(back,)] * 5, [(away, "A"), (away, "A")] + [(back,)] * 6):
                    for ph in range(len(cyc)):
                        b.macros = list(b.macros) + [("R",) + tuple((cyc * 4)[ph:ph + chunk])]
        node = b.run(deadline=time.time() + hours * 3600)
        if node is None:
            log("FAILED")
            sys.exit(2)
        rows = prefix + node.rows[:node.done - bstart["frame"]]
        histfile = histf
        logf.close()
        e.load(start)
        rep = V.finish(stage, start, histfile, rows, out, note=note or f"beam ref={mode} tag={tag}",
                       tool="ng.solve.beam", e=e)
        rep["load"] = node.done
        print("RESULT", json.dumps(rep), flush=True)
    finally:
        e.close()


if __name__ == "__main__":
    main(sys.argv[1:])
