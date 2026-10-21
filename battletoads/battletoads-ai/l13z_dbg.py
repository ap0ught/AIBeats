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
print("to_rise", S0 is not None, len(ins0), fS0.qe1, fS0.qe2, "toad", fS0.tx, fS0.thp, flush=True)
res, sims = zt.rise_search(e, S0, fS0, random.Random(1), budget=600)
print("res", [(p, n.e1, n.e2, n.f, len(n.ins)) for p, n in res], sims, flush=True)
for pred, node in res[:3]:
    e.mload(node.sid)
    ff = e.feat()
    print("top state: queen h", ff.qh, "e", ff.qe1, ff.qe2, "lvl", ff.lvl, "toad", ff.tx, ff.thp)
    r = zt.playout(e, node.sid, [])
    print("playout", None if r is None else r[1], flush=True)
    if r is None:
        e.mload(node.sid); n = 0; lv = 13
        while n < 1600:
            g = zt._step(e, ""); n += 1
            if g.lvl != lv: print("   level", lv, "->", g.lvl, "at", n); lv = g.lvl
            if n % 200 == 0: print("   ", n, "queen", hex(g.qid), g.qh, "e", g.qe1, g.qe2, "toad", g.tx, g.thp, "lvl", g.lvl)
e.close()
