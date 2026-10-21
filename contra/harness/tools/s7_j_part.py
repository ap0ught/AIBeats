"""Job: run part of the stage 7 route from a checkpoint with the current solver code.

Environment: S7_STATE (checkpoint), S7_ROW0 (its row), S7_TAG, S7_PARTS (letters of route_<x>, default "cdeB";
B = boss), S7_PARAMS ("k=v,k=v" integers)."""
import json
import os
import time
from pathlib import Path

from contra.stages import s7
from contra.stages.s6run import Mark

STATE = os.environ.get("S7_STATE", "s7/ph90_lower2")
ROW0 = int(os.environ.get("S7_ROW0", "1231"))
TAG = os.environ.get("S7_TAG", "part")
PARTS = os.environ.get("S7_PARTS", "cdeB")
params = {}
for kv in os.environ.get("S7_PARAMS", "").split(","):
    if "=" in kv:
        k, v = kv.split("=")
        params[k] = int(v)
t0 = time.time()
f0 = sim.load(STATE)
p = dict(s7.P)
p.update(params)
steps = []
for ch in PARTS:
    steps += s7.route_boss(p) if ch == "B" else getattr(s7, f"route_{ch}")(p)
r = s7.make_runner(sim, route=s7.tag_route(steps), name=TAG, params=params)
res = r.solve(max_deaths=80, back=110)
c = r.c
print("result", res, "rows", len(c.rows), "+", ROW0, "=", len(c.rows) + ROW0, "lag", sum(f["lagged"] for f in c.tr),
      "deaths", r.deaths, "trials", r.trials, "simulated", r.frames_simulated, "seconds", round(time.time() - t0),
      "params", params)
for m in r.marks:
    print("  mark", m[0], "row", m[1] + ROW0, "fc", m[2], "wx", m[3], "y", m[4])
print("remedies", [(repr(x), x.at + ROW0) for x in r.remedies])
print("local", r.local_fixes)
print("procs", {k: (v if k != "trio" else {kk: vv for kk, vv in v.items() if kk != "all"}) for k, v in r.user.items()
                if isinstance(v, dict)})
out = Path(r"logs\s7") / f"{TAG}.part.json"
out.write_text(json.dumps({"state": STATE, "row0": ROW0, "rows": [list(x) for x in c.rows]}), encoding="utf-8")
