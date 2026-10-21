"""Reload-rule statistics: random Select patterns through the rise; every reload logged as (step, e1 before -> e1, e2 after)
with exact reload detection (step = f + e2)."""
import json, random, sys, collections
import l13z_beam as zb, l13z_tail as zt
from toads.emulator import LOGS_DIR
seg, NS = sys.argv[1], int(sys.argv[2])
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
kill = j["kill_at"]
e = zb.Emu(log_name="l13z_tail8.log")
e.load(j["bookmark"])
for b in j["inputs"][:kill]:
    e.step(tuple(v for v in b.split("+") if v), 1)
f = e.feat(); sid = e.msave()
S0, ins0, fS0 = zt.to_rise(e, sid, f)
random.seed(3)
trans = collections.defaultdict(list)
chains = collections.Counter()
for s in range(NS):
    e.mload(S0)
    p = random.choice([0.05, 0.15, 0.4, 0.7])
    step = 0; e1, e2 = fS0.qe1, fS0.qe2; chain = []
    while step + e2 <= zt.RISE:
        ff = None
        for _ in range(e2):
            ff = zt._step(e, "Select" if random.random() < p else "")
        step += e2
        r = e.ram_all()
        qh = ff.qh
        trans[e1].append((step, ff.qe1, ff.qe2, qh, r[0x3FD], r[0x439]))
        chain.append((step, ff.qe1, ff.qe2))
        e1, e2 = ff.qe1, ff.qe2
        if e2 == 0: break
    chains[(tuple(c[1] for c in chain), e2 - (zt.RISE - step))] += 1
for k in sorted(trans):
    v = trans[k]
    nxt = collections.Counter((a[1]) for a in v)
    print(f"from e1={k}: {len(v)} reloads; next e1 counts {sorted(nxt.items())}")
    for ne in sorted(nxt):
        vals = sorted((a[0], a[2]) for a in v if a[1] == ne)
        print(f"    -> e1={ne}: (step, e2) {vals[:60]}")
print("chains with timer_at_top >= 100:", sorted((c for c in chains if c[1] >= 100), key=lambda c: c[1])[:40])
e.close()
