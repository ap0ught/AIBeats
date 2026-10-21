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
rng = random.Random(1)
# manual: root expansion 200 samples
kids = {}
for i in range(200):
    e.mload(S0)
    p = [0.0, 0.08, 0.25, 0.5][i % 4]
    ff = None
    for _ in range(fS0.qe2):
        ff = zt._step(e, "Select" if rng.random() < p else "")
    kids.setdefault((ff.qe1, ff.qe2), e.msave())
print("root children:", len(kids), sorted(k for k in kids if 143 <= 77 + k[1] <= 147))
for (e1, e2), sidc in sorted(kids.items()):
    if not (143 <= 77 + e2 <= 147): continue
    out = {}
    for i in range(32):
        e.mload(sidc)
        p = [0.0, 0.08, 0.25, 0.5][i % 4]
        ff = None
        for _ in range(e2):
            ff = zt._step(e, "Select" if rng.random() < p else "")
        k = (ff.qe1, ff.qe2)
        if k not in out:
            # follow on for 8 frames to see what comes
            seq = []
            for _ in range(8):
                g = zt._step(e, ""); seq.append((g.qe1, g.qe2))
            out[k] = seq
    print(f"child ({e1},{e2}) reload at {77+e2}: outcomes", out)
e.close()
