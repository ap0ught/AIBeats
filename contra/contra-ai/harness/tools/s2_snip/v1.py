# open-loop replay of a saved row list on another emulator instance + write the inputs file
import json, sys
from contra.inputs import write_inputs
name = G.get("VNAME", "s2/v0")
state = G.get("VSTATE", "ref_s2")
rows = [tuple(r) for r in json.load(open(f"logs/{name}_rows.json"))]
write_inputs(f"logs/{name}.inputs.txt", rows, f"segment from state {state}")
em = E[1]
em.set_fields(bc.make_fields())
s0 = em.load(state)
em.trace(True)
em.run(rows)
tr = em.last_trace
em.trace(False)
ev = []
prev = s0
lag = 0
for i, s in enumerate(tr):
    if s["lagged"]: lag += 1
    if s["screen"] != prev["screen"] and s["level"] == s0["level"]: ev.append(f"room{s['screen']+1}@{i+1}")
    if s["bossdef"] and not prev["bossdef"]: ev.append(f"bossdef@{i+1}")
    if s["death"] & 1 and not prev["death"] & 1: ev.append(f"DEATH@{i+1}")
    if s["level"] != prev["level"]: ev.append(f"level->{s['level']}@{i+1}")
    prev = s
s = tr[-1]
print("replay:", len(rows), "rows; end", {k: s[k] for k in ("frame", "level", "lroutine", "weapon", "lives", "death")}, "lag", lag)
print(" ".join(ev))
first4 = next((i + 1 for i, s in enumerate(tr) if s["level"] != s0["level"] and s["lroutine"] == 4), None)
print("next stage first $2C==4 at row", first4, "=> segment frames", first4)
