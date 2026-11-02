"""ng.solve.results - the standard per-stage result record, logs/results.json (a list; one entry per solved stage
attempt, newest last). Every solver in ng/solve writes one through record(); old results of the act agents can be
imported with record(...) by hand.

Entry fields:
  stage        "2-2"
  file         stage input file (rows from the frame after the start state up to and incl. the next control)
  start_state  states/<name>.State (the stage's control frame)
  start_frame  power-on frame number of that state
  history      the power-on input file that leads to start_state (legal; its rows are the frames 1..start_frame)
  load_frame   first frame with the next $6D (stage load)       control_frame  next stage's control frame
  frames       control -> next control
  vs_tas       frames - TAS 4751M split            vs_record   frames - record split (record_events.json)
  vs_record_cum  our next control frame - the record's next control on our axis (174 + its cum NES frames)
  hp / ninpo / item at the next control
  legal        check_inputs verdict on history + file         verified  open-loop replay reached the same control
  end_state    states/<name>.State at the next control         tool / note / time
"""
from __future__ import annotations

import json
import os
import time

from . import common as C

RESULTS = C.LOGS / "results.json"


def load() -> list:
    if RESULTS.exists():
        return json.loads(RESULTS.read_text(encoding="utf-8"))
    return []


def _save(lst):
    tmp = RESULTS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(lst, indent=1), encoding="utf-8")
    if RESULTS.exists():
        try:
            (C.LOGS / "results.json.backup").write_text(RESULTS.read_text(encoding="utf-8"), encoding="utf-8")
        except OSError:
            pass
    os.replace(tmp, RESULTS)


def record(stage, file, start_state, start_frame, history, control_frame, load_frame=None, hp=None, ninpo=None,
           item=None, legal=None, verified=None, end_state=None, tool="", note="") -> dict:
    i = C.stage_index(stage)
    frames = control_frame - start_frame
    e = {"stage": C.NAMES[i], "file": str(file), "start_state": str(start_state), "start_frame": start_frame,
         "history": str(history), "load_frame": load_frame, "control_frame": control_frame, "frames": frames,
         "vs_tas": frames - C.tas_split(i), "vs_record": round(frames - C.record_split(i), 1),
         "vs_record_cum": round(control_frame - C.record_control_frame(i + 1), 1) if i < 21 else None,
         "hp": hp, "ninpo": ninpo, "item": item, "legal": legal, "verified": verified, "end_state": end_state,
         "tool": tool, "note": note, "time": time.strftime("%Y-%m-%d %H:%M")}
    lst = load()
    lst.append(e)
    _save(lst)
    return e


def best(stage, verified_only=True) -> dict | None:
    c = [r for r in load() if r["stage"] == C.NAMES[C.stage_index(stage)] and (r.get("verified") or not verified_only)]
    return min(c, key=lambda r: r["control_frame"]) if c else None


def table(rows=None) -> str:
    rows = rows if rows is not None else load()
    out = ["| stage | file | start f | next control | frames | vs TAS | vs record | vs record cum | hp/np | legal | verified |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['stage']} | {r['file']} | {r['start_frame']} | {r['control_frame']} | {r['frames']} | "
                   f"{r['vs_tas']:+d} | {r['vs_record']:+.1f} | {r['vs_record_cum']} | {r['hp']}/{r['ninpo']} | "
                   f"{r['legal']} | {r['verified']} |")
    return "\n".join(out)


if __name__ == "__main__":
    print(table())
