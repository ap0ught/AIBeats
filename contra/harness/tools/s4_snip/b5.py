# replay a saved fight (x_fight_*.json) from the boss state: full RAM capture + exit timeline
import json, numpy as np
from contra.emulator import State
ROOT = ""
BIT = bc.BIT
stage, state, name = G.get("B5", (4, "s4/boss", "x_fight_p0"))
F = json.load(open(ROOT + f"logs/s{stage}/{name}.json"))
rows = [tuple(r) for r in F["rows"]][F["boss_load"]:]
e.set_fields(bc.make_fields()); e.trace(False)
e.load(state)
out = [np.frombuffer(e.ram_all(), dtype=np.uint8)]
lag = [0]
prev = None
for i, r in enumerate(rows):
    s = State.parse(e.cmd("stepx %02x" % sum(BIT[b] for b in r)))
    m = e.ram_all()
    out.append(np.frombuffer(m, dtype=np.uint8))
    lag.append(int(s["lagged"]))
    if i + 1 >= F["boss_rows"] - 2:
        cur = (m[0x2C], m[0x3B], m[0x90], m[0xA0] != 0, m[0x30])
        if cur != prev or (i + 1 - F["boss_rows"]) % 40 == 0:
            print(f"boss row {i+1} (+{i + 1 - F['boss_rows']}) lroutine {m[0x2C]} bossdef {m[0x3B]:02x} pstate {m[0x90]} jump {m[0xA0]:02x} P({m[0x334]},{m[0x31A]}) in={'+'.join(r)} delay {m[0x2A]:02x} lag {s['lagged']} level {m[0x30]}")
        prev = cur
np.save(ROOT + f"logs/s{stage}/x_cap_{name}.npy", np.array(out))
json.dump({"rows": rows, "lag": lag}, open(ROOT + f"logs/s{stage}/x_cap_{name}.json", "w"))
print("saved", len(out), "lag total", sum(lag))
