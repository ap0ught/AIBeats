"""Hornhead 7 our way (2026-10-03): from the exact TAS 2346 state (H6_j2346b) the TAS's inputs to its spawn (our camera
spawns it 3 frames later than the record's, so the record's fight inputs miss), then a kill beam over flying kicks /
boots (fightbeam's leads), then resync.py back onto the TAS at its 2557 platform landing (the record's 2534 Left+Right+A
dash jump is replaced by the generator's tap-release-jump).
    python l12f7.py -> knowledge/l12_f7.json {inputs from H6_j2346b to TAS 2557}, bookmark F7_j2557"""
import json, os, sys, resync
from toads.emulator import BizHawk
import fightbeam as fb
TAS = ["+".join(t) for t in resync.TAS]; rows = resync.rows
IDS = {0x5c}
WIDTH, WAIT = 4, 90
e = BizHawk(log_name="l12f7.log"); e.load("H6_j2346b")
L = fb.Line(e)
for j in range(2347, 2371): m = L.st(TAS[j])
print("prefix to the spawn: toad", fb.tx(m), fb.th(m), m[0x475], "foes", fb.foes(m, IDS), flush=True)
hp0, lives0 = m[0x51A], m[0x11]
def safe(m): return m[0x51A] >= hp0 and m[0x11] == lives0
sa = e.msave()
beam = [(len(L.ins), sa, list(L.ins), fb.tot(m, IDS))]
hitno = 0; done = []
while beam and not done:
    nxt = []
    for f, sid, ins, left in beam:
        found = set()
        for w in range(WAIT):
            e.mload(sid); L.ins = list(ins); L.st("", w); m = e.ram(0, 0x800)
            if not safe(m) or not fb.foes(m, IDS): break
            cur = fb.tot(m, IDS)
            if cur < left:                                      # a late hit of the previous blow
                nxt.append((len(L.ins), e.msave(), list(L.ins), cur, "(late)", w, fb.tx(m))); break
            here = e.msave(); nh = len(L.ins); t = fb.toward(m, IDS)
            for lead in fb.LEADS:
                if lead in found: continue
                e.mload(here); del L.ins[nh:]
                for x in fb.expand(lead, t): m = L.st(x)
                got = None
                for _ in range(40 if lead.endswith("!") else 26):
                    if not safe(m): break
                    c2 = fb.tot(m, IDS)
                    if c2 < cur: got = c2; break
                    m = L.st("")
                if got is None: continue
                for _ in range(70):
                    if m[0x475] == 0 or not safe(m): break
                    m = L.st("")
                if m[0x475] != 0 or not safe(m): continue
                found.add(lead)
                nxt.append((len(L.ins), e.msave(), list(L.ins), min(got, fb.tot(m, IDS)), lead, w, fb.tx(m)))
            e.mfree(here)
    for n in beam:
        if n[1] != sa: e.mfree(n[1])
    if not nxt: print("no next hit", flush=True); break
    hitno += 1
    nxt.sort(key=lambda n: (n[3], n[0]))
    keep, seenx = [], set()
    for n in nxt:
        k = (n[6], n[3])
        if k in seenx or len(keep) >= WIDTH: e.mfree(n[1]); continue
        seenx.add(k); keep.append(n)
    print(f"hit {hitno} ->", [(n[0], n[3], n[4], n[5], n[6]) for n in keep], flush=True)
    done = [n for n in keep if n[3] == 0]
    beam = [n[:4] for n in keep]
best = None
for i, (f, sid, ins, left, *_ ) in enumerate(sorted(done, key=lambda n: n[0])[:3]):
    e.mload(sid); e.save(f"F7_kill{i}")
    print(f"kill {i}: {f} frames (TAS 2347 -> kill 2492 = 145), toad {fb.tx(e.ram(0,0x800))}", flush=True)
    r = resync.run(f"F7_kill{i}", 2535, 2556, 2557, "L", 40, idle=False, objcheck=(0x35, 0, 255), stop_first=True, extend=False)
    if r:
        tot, jm, rins, jend = r
        total = ins + rins
        print(f"   -> resync {tot} frames via TAS {jm}; total {len(total)} frames from 2346 (TAS 2346 -> 2557 = 211)", flush=True)
        if best is None or len(total) < len(best): best = total
if best:
    e.load("H6_j2346b")
    for b in best: e.step(tuple(v for v in b.split("+") if v), 1)
    m = e.ram(0, 0x800); print("end", fb.tx(m), fb.th(m), m[0x475], m[0x3B5], "TAS 2557", rows[2557][1:5], flush=True)
    e.save("F7_j2557"); json.dump({"bookmark": "H6_j2346b", "jend": 2557, "inputs": best}, open("knowledge/l12_f7.json", "w"))
    print(f"SAVED {len(best)} frames", flush=True)
e.close()
