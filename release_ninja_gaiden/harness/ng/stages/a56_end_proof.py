"""Acts 5-6: prove the END clock event on our own 6-5 solution with tools/clock_evidence.py.

    python ng/stages/a56_end_proof.py <start state> <6-5 inputs file> <tag>

Plays the rows from the start state up to the first frame with the boss HP display $66 == 0, saves
states/tmp/a56_6-5_<tag>_boss0.State, runs `tools/clock_evidence.py end tmp/a56_6-5_<tag>_boss0` (which writes
knowledge/clock_evidence.json and shots/clock/end_*.png), copies its "end" result to
knowledge/a56_clock_end_<tag>.json and puts the harness's own clock_evidence.json back as it was.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a56_common as C  # noqa: E402

from ng import clock  # noqa: E402
from ng.mode import TICKS  # noqa: E402

if __name__ == "__main__":
    start, inputs, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    rows = C.read_inputs(inputs)
    e = C.open_emu(f"a56_endproof_{tag}.log")
    try:
        e.tick(TICKS)
        e.load(start)
        tr = C.play_trace(e, rows)
        k = next(i for i, s in enumerate(tr) if s["stage"] == 21 and s["bosshp"] == 0 and s["frame"] > tr[0]["frame"] + 160)
        e.load(start)
        e.run(rows[:k + 1])
        boss0 = e.state()["frame"]
        e.save(f"tmp/a56_6-5_{tag}_boss0")
        tr2 = tr + C.play_trace(e, [()] * 12) if False else tr
    finally:
        e.close()
    ours = clock.end_frame(tr + [])
    ev = C.PROJECT / "knowledge" / "clock_evidence.json"
    bak = C.PROJECT / "states" / "tmp" / "a56_clock_evidence.backup.json"
    shutil.copyfile(ev, bak)
    try:
        r = subprocess.run([sys.executable, str(C.PROJECT / "tools" / "clock_evidence.py"), "end",
                            f"tmp/a56_6-5_{tag}_boss0"], capture_output=True, text=True, cwd=str(C.PROJECT))
        j = json.loads(ev.read_text(encoding="utf-8"))
        out = {"start_state": start, "inputs": inputs, "boss0_frame": boss0, "clock_py_end_from_trace": ours,
               "clock_evidence_end": j.get("end"), "stdout_tail": r.stdout.strip().splitlines()[-14:]}
        (C.PROJECT / "knowledge" / f"a56_clock_end_{tag}.json").write_text(json.dumps(out, indent=1))
        print(json.dumps({k: v for k, v in out.items() if k != "clock_evidence_end"}, indent=1))
        print("P (first $63 == 0):", (j.get("end") or {}).get("P_first_timer0"))
    finally:
        shutil.copyfile(bak, ev)
