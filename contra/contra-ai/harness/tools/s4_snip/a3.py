# capture full RAM per frame for the two existing boss fights (model validation data)
import json, numpy as np
from contra.emulator import State
ROOT = ""
BIT = bc.BIT
def cap(emu, job):
    stage, tag, state, n_extra = job
    rep = json.load(open(ROOT + f"logs/s{stage}/{tag}_report.json"))
    rows = [tuple(r) for r in json.load(open(ROOT + f"logs/s{stage}/{tag}_rows.json"))]
    b0, b1 = rep["boss_load"], rep["boss_dead"]
    emu.set_fields(bc.make_fields())
    emu.trace(False)
    emu.load(state)
    out = [np.frombuffer(emu.ram_all(), dtype=np.uint8)]
    lag = [0]
    seg = rows[b0:b1 + n_extra]
    for r in seg:
        s = State.parse(emu.cmd("stepx %02x" % sum(BIT[b] for b in r)))
        out.append(np.frombuffer(emu.ram_all(), dtype=np.uint8))
        lag.append(int(s["lagged"]))
    np.save(ROOT + f"logs/s{stage}/x_cap_{tag}.npy", np.array(out))
    json.dump({"rows": seg, "lag": lag}, open(ROOT + f"logs/s{stage}/x_cap_{tag}.json", "w"))
    return (stage, tag, len(seg), sum(lag))
print(bc.pmap(E[:2], cap, [(4, "p0", "s4/boss", 40), (2, "f0", "s2/boss", 40)]))
