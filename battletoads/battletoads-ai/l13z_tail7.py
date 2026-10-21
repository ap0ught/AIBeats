"""Test the tail optimiser on a finished segment's kill state:  python l13z_tail7.py <segment> [budget] [seed]"""
import json, sys, time
import l13z_beam as zb, l13z_tail as zt
from toads.emulator import LOGS_DIR
seg = sys.argv[1]; budget = int(sys.argv[2]) if len(sys.argv) > 2 else 900; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
kill = j["kill_at"]
e = zb.Emu(log_name="l13z_tail7.log")
e.load(j["bookmark"])
for b in j["inputs"][:kill]:
    e.step(tuple(v for v in b.split("+") if v), 1)
f = e.feat(); sid = e.msave()
print(seg, "kill state at", kill, "queen id", hex(f.qid), "h", f.qh, "e1/e2", f.qe1, f.qe2, "toad x", f.tx, flush=True)
t0 = time.time()
r = zt.optimise(e, sid, f, budget=budget, seed=seed, tops=4)
print({k: v for k, v in r.items() if k != "inputs"}, f"{time.time()-t0:.0f}s")
print("T. Bird at", kill + r["total"], "(segment as stored:", j["tbird_at"], ")")
e.close()
