"""How the short state's timer (n) at its start depends on the toad's x: from a reload landing on step 143..146 of the rise,
walk the toad to different x during the preceding wander state and read the timer at the reload."""
import json, sys, random, collections
import l13z_beam as zb, l13z_tail as zt
from toads.emulator import LOGS_DIR
seg = sys.argv[1]
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
kill = j["kill_at"]
e = zb.Emu(log_name="l13z_tail9.log")
e.load(j["bookmark"])
for b in j["inputs"][:kill]:
    e.step(tuple(v for v in b.split("+") if v), 1)
f = e.feat(); sid = e.msave()
S0, ins0, fS0 = zt.to_rise(e, sid, f)
rng = random.Random(11)
kids = {}
for i in range(300):
    e.mload(S0)
    p = [0.08, 0.25, 0.5, 0.15][i % 4]
    ff = None
    for _ in range(fS0.qe2):
        ff = zt._step(e, "Select" if rng.random() < p else "")
    if 143 <= fS0.qe2 + ff.qe2 <= 146 and (ff.qe1, ff.qe2) not in kids:
        kids[(ff.qe1, ff.qe2)] = e.msave()
print("window children:", sorted(kids), "toad x", fS0.tx, flush=True)
for (e1, R), sidc in sorted(kids.items()):
    row = []
    for tx in (22, 40, 60, 80, 96, 160, 176, 196, 210, 224, 238):
        e.mload(sidc)
        g = None
        for _ in range(R):
            cur = e.feat() if g is None else g
            b = "Right" if cur.tx < tx - 1 else ("Left" if cur.tx > tx + 1 else "")
            g = zt._step(e, b)
        row.append((g.tx, g.qe1, g.qe2, g.thp))
    print(f"wander state ({e1},{R}) -> reload at step {fS0.qe2 + R}: (toad x, new state, timer n, hp):", row, flush=True)
e.close()
