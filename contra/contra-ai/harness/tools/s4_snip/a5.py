# captures with Bill dying to cannon bullets (hazard model validation): full RAM per frame
import json, numpy as np
from contra.emulator import State
ROOT = ""
BIT = bc.BIT
def cap(emu, job):
    name, state, spec, n = job
    rows = bc.rows_from_spec(n, spec)
    emu.set_fields(bc.make_fields()); emu.trace(False)
    emu.load(state)
    out = [np.frombuffer(emu.ram_all(), dtype=np.uint8)]
    lag = [0]
    for r in rows:
        s = State.parse(emu.cmd("stepx %02x" % sum(BIT[b] for b in r)))
        out.append(np.frombuffer(emu.ram_all(), dtype=np.uint8))
        lag.append(int(s["lagged"]))
    st = name[1]
    np.save(ROOT + f"logs/s{st}/x_cap_{name}.npy", np.array(out))
    json.dump({"rows": rows, "lag": lag}, open(ROOT + f"logs/s{st}/x_cap_{name}.json", "w"))
    d = [i for i in range(1, len(out)) if out[i][0x90] == 2 and out[i - 1][0x90] != 2]
    return name, d
jobs = [("s4hzA", "s4/boss", [(8, 87, "Left")], 230),                       # stand at x 51
        ("s4hzB", "s4/boss", [(8, 20, "Left"), (150, 151, "A")], 230),       # stand near the middle, jump late
        ("s4hzC", "s4/boss", [(8, 40, "Right"), (120, 121, "A"), (122, 160, "Left")], 230),
        ("s2hzA", "s2/boss", [(8, 87, "Left")], 230),
        ("s2hzB", "s2/boss", [(8, 60, "Right"), (130, 131, "A")], 230),
        ("s2hzC", "s2/boss", [(8, 30, "Left"), (125, 126, "A"), (127, 150, "Right")], 230)]
for r in bc.pmap(E, cap, jobs):
    print(r)
