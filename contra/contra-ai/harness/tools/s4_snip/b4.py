# which frames does the game not read the pad on? probe with Select toggled every frame on top of different inputs
import json, importlib, pickle
from contra.emulator import State
import contra.stages.base_bplan as bp
ROOT = ""
BIT = bc.BIT
D = pickle.load(open(ROOT + "logs/s4/x_dbg_b3.pkl", "rb"))
plan_rows = [bp.act_row(a) for a in D["acts"]]
def probe(emu, job):
    name, state, rows = job
    emu.set_fields(bc.make_fields()); emu.trace(False)
    emu.load(state)
    drops = []; lag = []
    prev_sent = 0
    for i in range(420):
        r = rows[i] if i < len(rows) else ()
        mask = sum(BIT[b] for b in r) | (0x20 if i & 1 else 0)
        s = State.parse(emu.cmd("stepx %02x" % mask))
        if s["lagged"]:
            lag.append(i + 1)
            continue
        m = emu.ram_all()
        if m[0xF1] != mask:
            drops.append((i + 1, "%02x" % m[0xF1], "%02x" % mask))
        if m[0x90] != 1:
            drops.append((i + 1, "DEAD"))
            break
    return name, lag, drops
jobs = [("plan", "s4/boss", [()] * 9 + plan_rows),
        ("passive-left", "s4/boss", [()] * 9 + [("Left",)] * 70),
        ("passive-right", "s4/boss", [()] * 9 + [("Right",)] * 70)]
for name, lag, drops in bc.pmap(E, probe, jobs):
    print(name, "lag", lag[:3], "..", len(lag))
    print("   drops", drops)
