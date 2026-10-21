import json, sys, random, collections
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
rng = random.Random(5)
kids = collections.Counter()
for i in range(400):
    e.mload(S0)
    p = [0.0, 0.08, 0.25, 0.5][i % 4]
    ff = None
    for _ in range(fS0.qe2):
        ff = zt._step(e, "Select" if rng.random() < p else "")
    kids[(ff.qe1, ff.qe2)] += 1
print("root", fS0.qe1, fS0.qe2, "distinct children", len(kids))
print("e2 histogram:", sorted(collections.Counter(k[1] for k in kids.elements()).items()))
print("e1 histogram:", sorted(collections.Counter(k[0] for k in kids.elements()).items()))
print("in window (reload step 143..150):", sorted((k, v) for k, v in kids.items() if 143 <= fS0.qe2 + k[1] <= 150))
e.close()
