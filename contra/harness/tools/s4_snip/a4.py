# cannon bullets: positions and velocities per frame (stage 4 and stage 2 boss rooms), Bill steered left out of the way
import numpy as np
from contra.emulator import State
BIT = bc.BIT
def cap(emu, job):
    stage, state = job
    emu.set_fields(bc.make_fields()); emu.trace(False)
    emu.load(state)
    out = []
    rows = [("Left",)] * 80 + [()] * 140
    for i, r in enumerate(rows):
        s = State.parse(emu.cmd("stepx %02x" % sum(BIT[b] for b in r)))
        m = emu.ram_all()
        for k in range(16):
            if m[0x4B8 + k] and m[0x528 + k] == 1:
                out.append((i + 1, k, m[0x33E + k], m[0x324 + k], m[0x508 + k], m[0x518 + k], m[0x4E8 + k], m[0x4F8 + k], m[0x4D8 + k], m[0x4C8 + k], m[0x598 + k], m[0x4B8 + k]))
        if i + 1 in (104, 105, 106, 219):
            print(stage, i + 1, "P", m[0x334], m[0x31A], "death", m[0xB4], "attack", m[0x8E], "state", m[0x90])
    return stage, out
for stage, out in bc.pmap(E[:2], cap, [(4, "s4/boss"), (2, "s2/boss")]):
    print("stage", stage)
    seen = {}
    for o in out:
        seen.setdefault(o[1], []).append(o)
    for k, v in seen.items():
        print(" slot", k, "first", v[0], "n", len(v), "last", v[-1])
        print("   xs", [o[2] for o in v][:40])
        print("   ys", [o[3] for o in v][:40])
