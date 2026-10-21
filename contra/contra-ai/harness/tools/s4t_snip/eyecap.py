"""Capture RAM at the frame the fourth plating's wreck is drawn (start of the Eye phase) in the verified second-pass
stage 2 runs, plus the frame before the boss room's logic starts; for offline work on the Eye planner."""
import json, pickle
from contra.stages.base_common import BIT
from contra.emulator import State

em = E[1]
out = {}
for tag, state in (("L2", "s1/s2_start_legal_v2"), ("L0", "s1/s2_start_legal"), ("g0", "ref_s2"), ("g37", "ref_s2")):
    rep = json.load(open(f"logs/s2/{tag}_report.json"))
    rows = [tuple(r) for r in json.load(open(f"logs/s2/{tag}_rows.json"))]
    b0 = rep["boss_load"]
    pd = rep["boss"]["plates_done"]
    em.load(state)
    n = b0 + pd
    for r in rows[:n]:
        em.cmd("stepx %02x" % sum(BIT[b] for b in r))
    m = em.ram_all()
    out[tag] = {"ram": bytes(m), "rows": rows[n - 14:n], "row": n, "boss_load": b0, "plates_done": pd,
                "flag": rep["boss"]["frames"], "rest": rows[n:b0 + rep["boss"]["frames"]]}
    print(tag, "row", n, "plates", m[0x87], "x", m[0x334], "y", m[0x31A], "jump", m[0xA0], "flag at boss row", rep["boss"]["frames"])
pickle.dump(out, open("logs/s2t/eye_caps.pkl", "wb"))
print("saved")
