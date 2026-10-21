# open-loop test of an offline plan in the emulator: compare with the model every frame
import json, sys, importlib
from contra.emulator import State
import contra.stages.base_bsim as bs
importlib.reload(bs)
ROOT = ""
BIT = bc.BIT
st, state, plan = G.get("B1", (4, "s4/boss", "logs/s4/x_planAB_p0_plain.json"))
P = json.load(open(ROOT + plan))
rows = [tuple(r) for r in P["rows"]]
k0 = P["k0"]
e.set_fields(bc.make_fields()); e.trace(False)
e.load(state)
n = 0
while n < k0:
    s = State.parse(e.cmd("stepx 00")); n += 1
sim = bs.Sim.from_ram(e.ram_all())
bad = 0; lagn = 0
i = 0
log = []
while i < len(rows):
    r = rows[i]
    s = State.parse(e.cmd("stepx %02x" % sum(BIT[b] for b in r)))
    if s["lagged"]:
        lagn += 1
        continue
    m = e.ram_all()
    sim.step(m[0xF1] & 15, m[0xF5] & 0x80, m[0xF5] & 0x40)
    want = sum(BIT[b] for b in r)
    if m[0xF1] != want:
        log.append(f"row {i} (i={k0+i+1}): pad seen {m[0xF1]:02x} sent {want:02x}")
    ref = bs.Sim.from_ram(m)
    d = []
    if (sim.px, sim.py) != (ref.px, ref.py): d.append(f"P sim {sim.px},{sim.py} ram {ref.px},{ref.py}")
    if sim.br != ref.br: d.append(f"br sim {sim.br} ram {ref.br}")
    if sim.hp_left() != ref.hp_left(): d.append(f"hp sim {sim.hp_left()} ram {ref.hp_left()}")
    if m[0x90] != 1: d.append(f"player state {m[0x90]}")
    if d:
        bad += 1
        if bad < 12: log.append(f"row {i} (i={k0+i+1}): " + "; ".join(d))
        sim = ref
    i += 1
m = e.ram_all()
print("\n".join(log))
print("rows", len(rows), "lag", lagn, "mismatch frames", bad, "bossdef", m[0x3B], "player state", m[0x90], "x", m[0x334], "plates", m[0x87], "cores", m[0x86])
print(bc.fmt_enemies(e.state()))
