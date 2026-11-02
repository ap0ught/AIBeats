"""ng.solve.record - the record holder's run as a reference (splits + route).

  splits()                       {stage: (record control on our frame axis, record split, TAS split)}
  route_json(stage)              path of the traced record route (work/a12r2/rec, work/a34r2/rec, work/a56r2/rec)
  waypoints(stage)               ng.legal.Waypoints over that json (RAM coordinates, record time; .at(t), .columns())
  python -m ng.solve.record      print the split table

Making a new route json from the video (agent a56's tracker, unchanged):
  1. cut the stage's frames: see states/tmp/a12r2_vid/extract.sh (ffmpeg, game area 1200x900 at (600,140) -> 256x240)
  2. python work/a56r2/record_trace.py <dir> <video control frame> <video end frame> <out.json>
     (control video frames: knowledge/record_events.json "control_est_f"; HUD mask y 72 there, 60 in work/a12r2/rtrace.py)
"""
from __future__ import annotations

from pathlib import Path

from . import common as C

DIRS = [C.PROJECT / "work" / d / "rec" for d in ("a12r2", "a34r2", "a56r2")]


def route_json(stage) -> Path | None:
    nm = C.NAMES[C.stage_index(stage)].replace("-", "").replace("a", "a").replace("b", "b")
    for d in DIRS:
        p = d / f"r{nm}.json"
        if p.exists():
            return p
    return None


def waypoints(stage):
    from ng import legal
    p = route_json(stage)
    return legal.Waypoints(str(p), C.stage_index(stage)) if p else None


def splits() -> dict:
    out = {}
    for i, n in enumerate(C.NAMES):
        out[n] = (round(C.record_control_frame(i), 1), C.record_split(i), C.tas_split(i))
    return out


if __name__ == "__main__":
    print("| stage | record control (our axis) | record split | TAS split | record - TAS |")
    print("|---|---|---|---|---|")
    for n, (c, r, t) in splits().items():
        print(f"| {n} | {c} | {r} | {t} | {r - t:+.1f} |")
