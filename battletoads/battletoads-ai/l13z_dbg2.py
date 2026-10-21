import json, sys, random
import l13z_beam as zb, l13z_tail as zt
from toads.emulator import LOGS_DIR
seg = sys.argv[1]
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
kill = j["kill_at"]
e = zb.Emu(log_name="l13z_dbg.log")
e.load(j["bookmark"])
for b in j["inputs"][:kill]:
    e.step(tuple(v for v in b.split("+") if v), 1)
f = e.feat(); sid = e.msave()
S0, ins0, fS0 = zt.to_rise(e, sid, f)
e.mload(S0)
row = []
for k in range(1, 300):
    g = zt._step(e, "")
    if k < 6 or 74 <= k <= 82 or 165 <= k <= 176 or k % 40 == 0:
        row.append((k, g.qh, g.qe1, g.qe2, g.ctr, g.tx, g.thp, g.lvl))
print(row)
e.close()
