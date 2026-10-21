"""A Hornhead fight our way + resync onto the record (2026-10-04), generalised from l12f7.py.
    python l12fight.py <bookmark> <TAS index of that state> <pre_to (replay TAS inputs up to this index first)> <jlo-jhi> <jcheck> <out> [ids hex, default 5c]
      -> knowledge/l12_<out>.json {inputs from the bookmark}, bookmark F_<out>_j<jend>"""
import json, os, sys, resync
from toads.emulator import BizHawk
import fightbeam as fb
TAS = ["+".join(t) for t in resync.TAS]; rows = resync.rows
bm, j0, pre_to, win, jcheck, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6]
IDS = {int(v, 16) for v in (sys.argv[7] if len(sys.argv) > 7 else "5c").split(",")}
jlo, jhi = (int(v) for v in win.split("-"))
WIDTH, WAIT = int(os.environ.get("FB_WIDTH", 4)), int(os.environ.get("FB_WAIT", 90))
e = BizHawk(log_name=f"l12fight_{out}.log"); e.load(bm); L = fb.Line(e); m = e.ram(0, 0x800)
for j in range(j0 + 1, pre_to + 1): m = L.st(TAS[j])
print("start: toad", fb.tx(m), fb.th(m), m[0x475], "foes", fb.foes(m, IDS), "hp", m[0x51A], flush=True)
hp0, lives0 = m[0x51A], m[0x11]
def safe(m): return m[0x51A] >= hp0 and m[0x11] == lives0
sa = e.msave(); beam = [(len(L.ins), sa, list(L.ins), fb.tot(m, IDS))]; hitno = 0; done = []
while beam and not done:
    nxt = []
    for f, sid, ins, left in beam:
        found = set()
        for w in range(WAIT):
            e.mload(sid); L.ins = list(ins); L.st("", w); m = e.ram(0, 0x800)
            if not safe(m) or not fb.foes(m, IDS): break
            cur = fb.tot(m, IDS)
            if cur < left: nxt.append((len(L.ins), e.msave(), list(L.ins), cur, "(late)", w, fb.tx(m))); break
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
                found.add(lead); nxt.append((len(L.ins), e.msave(), list(L.ins), min(got, fb.tot(m, IDS)), lead, w, fb.tx(m)))
            e.mfree(here)
    for n in beam:
        if n[1] != sa: e.mfree(n[1])
    if not nxt: print("no next hit", flush=True); break
    hitno += 1; nxt.sort(key=lambda n: (n[3], n[0])); keep, seenx = [], set()
    for n in nxt:
        k = (n[6], n[3])
        if k in seenx or len(keep) >= WIDTH: e.mfree(n[1]); continue
        seenx.add(k); keep.append(n)
    print(f"hit {hitno} ->", [(n[0], n[3], n[4], n[5], n[6]) for n in keep], flush=True)
    done = [n for n in keep if n[3] == 0]; beam = [n[:4] for n in keep]
best = None
for i, (f, sid, ins, left, *_ ) in enumerate(sorted(done, key=lambda n: n[0])[:3]):
    e.mload(sid); e.save(f"F_{out}_kill{i}"); json.dump({"bookmark": bm, "inputs": ins}, open(f"knowledge/l12_{out}_kill{i}.json", "w")); print(f"kill {i}: {f} frames, toad {fb.tx(e.ram(0,0x800))}", flush=True)
    if os.environ.get("FIGHT_NORESYNC"): continue
    for dirc in ("L", "R"):
        r = resync.run(f"F_{out}_kill{i}", jlo, jhi, jcheck, dirc, 40, idle=False, objcheck=None, stop_first=True, extend=True)
        if r:
            tot, jm, rins, jend = r; total = ins + rins
            print(f"   -> resync {tot} via TAS {jm} to {jend}; total {len(total)} frames", flush=True)
            if best is None or len(total) - jend < len(best[0]) - best[1]: best = (total, jend)
            break
if best:
    e.load(bm)
    for b in best[0]: e.step(tuple(v for v in b.split("+") if v), 1)
    m = e.ram(0, 0x800); print("end", fb.tx(m), fb.th(m), m[0x475], m[0x3B5], "TAS", best[1], rows[best[1]][1:5], flush=True)
    e.save(f"F_{out}_j{best[1]}"); json.dump({"bookmark": bm, "jend": best[1], "inputs": best[0]}, open(f"knowledge/l12_{out}.json", "w")); print("SAVED", len(best[0]), flush=True)
e.close()
