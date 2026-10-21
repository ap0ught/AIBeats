"""From a TAS-synced bookmark: our own hit-beam kill of the enemy, then resync.py back onto the TAS at a landing in
[r0, r1] (jcheck = r1).   python tasfight2.py <bookmark> <ids hex> <r0> <r1> <out>
    -> knowledge/tasfight2_<out>.json {inputs from the bookmark, jend}, bookmark <out>_end"""
import json, sys
from toads.emulator import BizHawk, PROJECT
from fightbeam import foes, tot, toward, expand, LEADS, tx, th, Line
import resync
bm, ids, r0, r1, out = sys.argv[1], {int(v, 16) for v in sys.argv[2].split(",")}, int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
e = BizHawk(log_name=f"tasfight2_{out}.log"); e.load(bm); L = Line(e); m = e.ram(0, 0x800)
hp0, lives0, h0 = m[0x51A], m[0x11], th(m)
def safe(m): return m[0x51A] >= 40 and m[0x11] == lives0 and th(m) >= h0 - 80
WIDTH, WAIT, WAIT1 = 4, 60, 260
beam = [(0, e.msave(), [], None, bool(foes(m, ids)))]; done = []
while beam and not done:
    nxt = []
    for f, sid, ins, left, seen in beam:
        found = set(); e.mload(sid); L.ins = list(ins)
        for w in range(WAIT if seen else WAIT1):
            m = e.ram(0, 0x800)
            if not safe(m): break
            sn = seen or bool(foes(m, ids)); cur = tot(m, ids)
            if sn and left is not None and cur < left: left = cur
            if sn and cur == 0: nxt.append((len(L.ins), e.msave(), list(L.ins), 0, True, "(none)", w, tx(m))); break
            if sn:
                here = e.msave(); nh = len(L.ins); t = toward(m, ids)
                for lead in LEADS:
                    if lead in found: continue
                    e.mload(here); del L.ins[nh:]
                    for x in expand(lead, t): m = L.st(x)
                    got = None
                    for _ in range(40 if lead.endswith("!") else 26):
                        if not safe(m): break
                        c2 = tot(m, ids)
                        if c2 < cur: got = c2; break
                        m = L.st("")
                    if got is None: continue
                    for _ in range(70):
                        if m[0x475] == 0 or not safe(m): break
                        m = L.st("")
                    if m[0x475] != 0 or not safe(m): continue
                    found.add(lead); nxt.append((len(L.ins), e.msave(), list(L.ins), min(got, tot(m, ids)), True, lead, w, tx(m)))
                e.mload(here); e.mfree(here); del L.ins[nh:]
            m = L.st(""); seen = sn
            if left is None and sn: left = tot(m, ids)
    for n in beam: e.mfree(n[1])
    if not nxt: print("no next hit", flush=True); break
    nxt.sort(key=lambda n: (n[3], n[0])); keep, seenx = [], set()
    for n in nxt:
        kk = (n[7] // 8, n[3])
        if kk in seenx or len(keep) >= WIDTH: e.mfree(n[1]); continue
        seenx.add(kk); keep.append(n)
    print("hit ->", [(n[0], n[3], n[5], n[6], n[7]) for n in keep], flush=True)
    done = [n for n in keep if n[3] == 0]; beam = [n[:5] for n in keep]
if not done: e.close(); sys.exit(1)
best = None
for f, sid, ins, *_ in sorted(done, key=lambda n: n[0])[:2]:
    e.mload(sid); e.save(f"{out}_kill"); e.close()
    r = resync.run(f"{out}_kill", r0, r1 - 10, r1, "R", 40, idle=False, objcheck=(0x36, 0, 255), stop_first=True, extend=True)
    if not r: r = resync.run(f"{out}_kill", r0, r1 - 10, r1, "L", 40, idle=False, objcheck=(0x36, 0, 255), stop_first=True, extend=True)
    e = BizHawk(log_name=f"tasfight2_{out}.log")
    if r:
        tot_, j, rins, jend = r
        print(f"kill {f} + resync {len(rins)} (TAS {j + 1}..{jend}) = {f + len(rins)} frames", flush=True)
        if best is None or f + len(rins) < len(best[0]): best = (ins + rins, jend)
    else:
        print(f"kill {f}: no resync onto the TAS", flush=True)
if best:
    e.load(bm)
    for x in best[0]: e.step(tuple(v for v in x.split("+") if v), 1)
    e.save(f"{out}_end")
    json.dump({"bookmark": bm, "inputs": best[0], "jend": best[1]}, open(PROJECT / "knowledge" / f"tasfight2_{out}.json", "w"))
    print(f"saved knowledge/tasfight2_{out}.json: {len(best[0])} frames, ends on TAS {best[1]}", flush=True)
e.close()
