"""The queen's leftover timer $4ED,X during her rise: it reloads at 0; the value left at the top sets the last scene's length
(T. Bird = tower + 438 + e2). Sample random Select patterns during the rise and list the reloads and the final value."""
import json, random, sys, collections
import l13z_beam as zb
from toads.emulator import LOGS_DIR
seg, n0, NS = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = j["inputs"]
e = zb.Emu(log_name="l13z_tail4.log")
e.load(j["bookmark"])
for b in ins[:n0]:
    e.step(tuple(v for v in b.split("+") if v), 1)
# run idle to the rise start (ctr reaches 0)
n = n0
f = e.feat()
while not (f.qid == zb.QUEEN and f.ctr == 0 and f.qh > 200):
    f = e.xp(None, [("-",)])[0][1]; n += 1
print("rise starts after input", n, "e1/e2", f.qe1, f.qe2, "toad x", f.tx, flush=True)
S0 = e.msave()
random.seed(1)
res = collections.Counter(); reloads = collections.Counter(); best = []
for s in range(NS):
    e.mload(S0)
    p = random.choice([0.0, 0.05, 0.15, 0.4]) if s else 0.0
    pat = []; prev = f.qe2; rl = []; k = 0; ph = None; f2 = f
    while k < 260:
        b = "Select" if random.random() < p else "-"
        f2 = e.xp(None, [(b,)])[0][1]; pat.append(b); k += 1
        if f2.qe2 > prev: rl.append((k, f2.qe1, f2.qe2))
        prev = f2.qe2
        if f2.qh == 156 and ph == 156: break
        ph = f2.qh
    res[f2.qe2] += 1
    for r in rl: reloads[(r[1], r[2])] += 1
    best.append((f2.qe2, k, rl))
    if s < 12: print(s, "p", p, "top after", k, "reloads", rl, "final e2", f2.qe2, flush=True)
print("final e2 distribution:", sorted(res.items()))
print("reload values (e1,e2):", sorted(reloads.items()))
print("first-reload frames:", collections.Counter(b[2][0][0] for b in best if b[2]))
e.close()
