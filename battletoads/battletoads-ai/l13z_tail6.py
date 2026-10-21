"""DEBUG PROBE ON A SNAPSHOT (memory write, never part of a run): the last scene's length as a function of the queen's
leftover timer ($4ED+slot) and state byte ($4DE+slot) at the tower top. Poke them at input <n0> (she waits at the top), play out."""
import json, sys
import l13z_beam as zb
from toads.emulator import LOGS_DIR
seg, n0 = sys.argv[1], int(sys.argv[2])
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
e = zb.Emu(log_name="l13z_tail6.log")
e.load(j["bookmark"])
for b in j["inputs"][:n0]:
    e.step(tuple(v for v in b.split("+") if v), 1)
S = e.msave()
f = e.feat()
print("at", n0, "queen h", f.qh, "e1/e2", f.qe1, f.qe2, "slot", f.slot, flush=True)
def play(e1, e2):
    e.mload(S)
    if e1 is not None: e.poke(0x4DE + f.slot, e1)
    if e2 is not None: e.poke(0x4ED + f.slot, e2)
    n = n0; phase = 0; k = 0; ev = {}
    while n < n0 + 1800:
        b = ("A" if k % 2 == 0 else "-") if phase == 1 else "-"
        f3 = e.xp(None, [(b,)])[0][1]; n += 1; k += 1
        if phase == 0 and f3.lvl != 13: phase = 1; k = 0; ev["cut1"] = n
        elif phase == 1 and f3.lvl == 13: phase = 2; k = 0; ev["tower"] = n
        elif phase == 2 and f3.lvl == 254: ev["tbird"] = n; break
    return ev.get("tbird", 0) - ev.get("tower", 0), ev
print("unpoked:", play(None, None))
for e1 in (254, 2):
    row = []
    for e2 in list(range(0, 256, 6)) + [172, 174, 176, 177, 178, 179, 180, 181, 182, 183, 184, 186, 188, 255]:
        sc, ev = play(e1, e2)
        row.append((e2, sc))
    print("e1", e1, sorted(set(row)), flush=True)
for e1 in (0, 1, 3, 4, 252, 253, 255, 128):
    row = []
    for e2 in (1, 20, 60, 120, 170, 178, 180, 182, 184, 190, 200, 230, 250):
        sc, ev = play(e1, e2)
        row.append((e2, sc))
    print("e1", e1, row, flush=True)
e.close()
