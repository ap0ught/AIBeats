import json, sys, time, random
import l13z_beam as zb, l13z_tail as zt
from toads.emulator import LOGS_DIR
seg = sys.argv[1]
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
kill = j["kill_at"]
e = zb.Emu(log_name="l13z_tail7.log")
e.load(j["bookmark"])
for b in j["inputs"][:kill]:
    e.step(tuple(v for v in b.split("+") if v), 1)
f = e.feat(); sid = e.msave()
S0, ins0, fS0 = zt.to_rise(e, sid, f)
print("to_rise:", S0, len(ins0), "queen", hex(fS0.qid), fS0.qh, "ctr", fS0.ctr, "e", fS0.qe1, fS0.qe2, "toad", fS0.tx, flush=True)
res, sims = zt.rise_search(e, S0, fS0, random.Random(1), budget=300)
print(sims, [(p, n.e1, n.e2, n.f) for p, n in res][:10])
e.close()
