# final checks: open-loop replays of every delivered segment on a second emulator; save the best run's states
import json
import os
from contra.inputs import write_inputs

ROOT = ""
runs = G.get("FIN", [("s2", "best", "ref_s2", True), ("s2", "p0", "ref_s2", False), ("s2", "p5", "ref_s2", False),
                     ("s2", "p37", "ref_s2", False), ("s4", "best", "s4/dbg_L", False), ("s4", "p6", "s4/dbg_L", False),
                     ("s4", "p37", "s4/dbg_L", False)])


def job(emu, run):
    name, tag, state, save = run
    p = ROOT + f"logs/{name}/{tag}_rows.json"
    if not os.path.exists(p):
        return (run, "no rows file")
    rows = [tuple(r) for r in json.load(open(p))]
    emu.set_fields(bc.make_fields())
    s0 = emu.load(state)
    emu.trace(True)
    emu.run(rows)
    tr = emu.last_trace
    emu.trace(False)
    ev, lag, prev = [], 0, s0
    marks = {}
    for i, s in enumerate(tr):
        lag += s["lagged"]
        if s["screen"] != prev["screen"] and s["level"] == s0["level"]:
            ev.append(f"room{s['screen'] + 1}@{i + 1}")
        if s["bossdef"] and not prev["bossdef"]:
            ev.append(f"bossdef@{i + 1}")
            marks["boss_dead"] = i + 1
        if s["death"] & 1 and not prev["death"] & 1:
            ev.append(f"DEATH@{i + 1}")
        prev = s
    first4 = next((i + 1 for i, s in enumerate(tr) if s["level"] != s0["level"] and s["lroutine"] == 4), None)
    s = tr[-1]
    res = (run, f"{len(rows)} rows, next stage's first frame at row {first4}, end level {s['level']} lroutine {s['lroutine']} "
                f"weapon ${s['weapon']:02X} lives {s['lives']} lag {lag} | " + " ".join(ev))
    if save and first4 == len(rows):
        for nm, n in (("boss_dead", marks.get("boss_dead")), ("next_stage", len(rows))):
            if n:
                emu.load(state)
                emu.run(rows[:n])
                emu.save(f"{name}/{nm}")
    return res


for r in bc.pmap(E, job, runs):
    print(r)
