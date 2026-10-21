"""Last-scene length vs the timer value left at the top: sample Select patterns in the rise, then play each distinct final value
out to the T. Bird cut (A mash through the speech) and print scene length = tbird - tower."""
import json, random, sys, collections
import l13z_beam as zb
from toads.emulator import LOGS_DIR
seg, n0, NS = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = j["inputs"]
e = zb.Emu(log_name="l13z_tail5.log")
e.load(j["bookmark"])
for b in ins[:n0]:
    e.step(tuple(v for v in b.split("+") if v), 1)
n = n0
f = e.feat()
while not (f.qid == zb.QUEEN and f.ctr == 0 and f.qh > 200):
    f = e.xp(None, [("-",)])[0][1]; n += 1
S0 = e.msave(); nS0 = n
random.seed(int(sys.argv[4]) if len(sys.argv) > 4 else 7)
seen = {}
for s in range(NS):
    e.mload(S0)
    p = random.choice([0.0, 0.05, 0.15, 0.4, 0.7]) if s else 0.0
    prev = f.qe2; k = 0; ph = None; f2 = f; rl = []
    while k < 260:
        b = "Select" if random.random() < p else "-"
        f2 = e.xp(None, [(b,)])[0][1]; k += 1
        if f2.qe2 > prev: rl.append((k, f2.qe1, f2.qe2))
        prev = f2.qe2
        if f2.qh == 156 and ph == 156: break
        ph = f2.qh
    v = f2.qe2
    if v in seen and not (v > 100 and len(seen[v]) < 3):
        continue
    # play out: idle to cut1, A mash, idle to tbird
    n2 = nS0 + k; phase = 0; kk = 0; ev = {}
    while n2 < nS0 + 1600:
        b = ("A" if kk % 2 == 0 else "-") if phase == 1 else "-"
        f3 = e.xp(None, [(b,)])[0][1]; n2 += 1; kk += 1
        if phase == 0 and f3.lvl != 13: phase = 1; kk = 0; ev["cut1"] = n2
        elif phase == 1 and f3.lvl == 13: phase = 2; kk = 0; ev["tower"] = n2
        elif phase == 2 and f3.lvl == 254: ev["tbird"] = n2; break
    sc = ev.get("tbird", 0) - ev.get("tower", 0)
    seen.setdefault(v, []).append(sc)
    print(f"e2 at top {v:3d} (e1 {f2.qe1}) reloads {rl}: cut1 {ev.get('cut1')} tower +{ev.get('tower',0)-ev.get('cut1',0)} last scene {sc} -> tbird {ev.get('tbird')}", flush=True)
print(sorted((v, s) for v, s in seen.items()))
e.close()
