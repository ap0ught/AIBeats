"""ng.solve.verify - finish a stage, verify it open-loop, judge it, record it; power-on chain assembly.

    python -m ng.solve.verify finish <stage> <start state> <history file> <rows file> [N] <out name> [--note ..]
        play rows[:N] from the start state, then blank rows (+ the earliest legal Start skip of a cutscene) until the
        next stage's control; replay the whole stage open-loop from the start state; judge history + rows; save
        states/<out>_end.State, logs/<out>.inputs.txt, logs/<out>.json and append logs/results.json.
    python -m ng.solve.verify stage <stage> <start state> <history file> <stage file>
        open-loop replay + judge only (prints the report).
    python -m ng.solve.verify chain <route name> <file> [<file> ...]
        concatenate power-on segments -> logs/<route>.inputs.txt, check_inputs (judge), then assemble.py --serial
        (two independent power-on replays, RAM + trace SHA-1 must MATCH; logs/<route>.report.json).

Library: finish(...), verify_stage(e, stage, start, rows, history), to_control(e, stage, hist_rows), chain(...).
"""
from __future__ import annotations

import json
import subprocess
import sys

from . import common as C
from . import legality as L
from . import results as R

import a12r2_solve as _S  # noqa: E402  (to_control / verify of the Acts 1-2 agent; any stage 0..20)
from ng.mode import TICKS  # noqa: E402

to_control = _S.to_control
verify_stage = _S.verify


def finish(stage, start, history_file, rows, out, note="", tool="ng.solve.verify.finish", e=None) -> dict:
    stage = C.stage_index(stage)
    history = C.rows_of(history_file)
    own = e is None
    if own:
        e = C.open_emu(f"tk_{out}_emu.log")
    try:
        e.tick(TICKS)
        st = e.load(start)
        f0 = st["frame"]
        assert len(history) == f0, f"history has {len(history)} rows but the state is at frame {f0}"
        e.run(rows)
        tail = to_control(e, stage, history + list(rows))
        rows = list(rows) + tail
        rep = verify_stage(e, stage, start, rows, history)
        # the load frame: first frame with the next $6D in the replay
        e.save(f"{out}_end")
        C.write_inputs(C.LOGS / f"{out}.inputs.txt", rows,
                       f"stage {C.NAMES[stage]} from {start} (frame {f0}) to the next control {rep['control_frame']}; "
                       f"legal={rep['legal']}")
        rep.update({"stage": C.NAMES[stage], "start": start, "end_state": f"{out}_end",
                    "vs_tas": rep["frames"] - C.tas_split(stage),
                    "vs_record": round(rep["frames"] - C.record_split(stage), 1)})
        (C.LOGS / f"{out}.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
        R.record(stage, f"logs/{out}.inputs.txt", f"states/{start}.State", f0, history_file, rep["control_frame"],
                 hp=rep["hp"], ninpo=rep["ninpo"], item=rep["item"], legal=rep["legal"],
                 verified=bool(rep["control_ok"]) and rep["deaths"] == 0, end_state=f"states/{out}_end.State",
                 tool=tool, note=note)
        return rep
    finally:
        if own:
            e.close()


def chain(route, files) -> int:
    rows = []
    for f in files:
        rows += C.rows_of(f)
    out = C.LOGS / f"{route}.inputs.txt"
    C.write_inputs(out, rows, f"power-on chain {route}: " + " + ".join(str(f) for f in files))
    chk = L.check(rows)
    print("judge:", "PASS" if chk.get("pass") else f"FAIL {str(chk)[:300]}", flush=True)
    r = subprocess.run([sys.executable, "-u", "assemble.py", route, str(out), "--serial"], cwd=str(C.PROJECT))
    return r.returncode


def _main(a):
    note = ""
    if "--note" in a:
        i = a.index("--note")
        note = a[i + 1]
        del a[i:i + 2]
    cmd = a[0]
    if cmd == "finish":
        stage, start, hist, rf = a[1], a[2], a[3], a[4]
        if len(a) == 7:
            n, out = int(a[5]), a[6]
        else:
            n, out = None, a[5]
        rows = C.rows_of(rf)
        rows = rows[:n] if n is not None else rows
        print("RESULT", json.dumps(finish(stage, start, hist, rows, out, note=note)), flush=True)
    elif cmd == "stage":
        stage, start, hist, rf = C.stage_index(a[1]), a[2], a[3], a[4]
        e = C.open_emu("tk_verify_emu.log")
        try:
            e.tick(TICKS)
            print(json.dumps(verify_stage(e, stage, start, C.rows_of(rf), C.rows_of(hist))))
        finally:
            e.close()
    elif cmd == "chain":
        sys.exit(chain(a[1], a[2:]))


if __name__ == "__main__":
    _main(sys.argv[1:])
