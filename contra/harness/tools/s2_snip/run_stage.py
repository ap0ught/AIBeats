# run stage solvers on the daemon's emulators, one job per emulator
# G["JOBS"] = [dict(stage=2, state="ref_s2", tag="p0", pause=0, beam=12000, boss_width=12, boss_hold=4, rooms_only=False,
#                   save_states=None), ...]
import json
import time
import io
import contextlib
import contra.stages.s2 as s2
import contra.stages.s4 as s4
from contra.inputs import write_inputs

jobs = G["JOBS"]


def job(emu, j):
    mod = s2 if j["stage"] == 2 else s4
    name = f"s{j['stage']}"
    t = time.time()
    buf = io.StringIO()
    out = mod.solve(emu, j["state"], verbose=False, beam=j.get("beam", 12000), boss_width=j.get("boss_width", 12),
                    boss_hold=j.get("boss_hold", 4), rooms_only=j.get("rooms_only", False), pause=j.get("pause", 0),
                    save_states=j.get("save_states"))
    out["secs"] = round(time.time() - t)
    out["job"] = j
    rows = out.pop("rows", [])
    base = f"logs/{name}/{j['tag']}"
    json.dump(rows, open(base + "_rows.json", "w"))
    json.dump(out, open(base + "_report.json", "w"), indent=1)
    if out.get("ok"):
        write_inputs(base + ".inputs.txt", rows, f"stage {j['stage']} segment from state {j['state']} pause={j.get('pause', 0)}")
    if j.get("rooms_only"):
        json.dump(rows, open(base + "_rows_to_boss.json", "w"))
    return out


res = bc.pmap(E[:len(jobs)], job, jobs)
for o in res:
    if "error" in o:
        print("JOB ERROR", o["error"][-600:])
        continue
    j = o["job"]
    print(f"stage {j['stage']} tag {j['tag']} pause {j.get('pause', 0)}: ok={o.get('ok')} frames={o.get('frames')} "
          f"boss={o.get('boss')} secs={o['secs']} weapon={o.get('weapon')}")
    print("   rooms:", [(r["room"], r["frames"], r["last_hit_T"], r["lag"], r["replans"], r["reason"]) for r in o["rooms"]],
          "boss_load", o.get("boss_load"))
