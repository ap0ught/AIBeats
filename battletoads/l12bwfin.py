"""Fallback finish of the big walker (2026-10-03): from the plain replay's end (walker left with 15 hp), one more
blow by fightbeam's leads, then resync onto the TAS's next landing (3217 (496,180) or 3237 (44,254)).
    python l12bwfin.py <bookmark at TAS 3172> -> knowledge/l12_bwfin.json, bookmark BWF_j<jend>"""
import json, sys, resync
from toads.emulator import BizHawk
import fightbeam as fb
TAS = ["+".join(t) for t in resync.TAS]; rows = resync.rows
IDS = {0x62}
bm = sys.argv[1]
e = BizHawk(log_name="bwfin.log"); e.load(bm); L = fb.Line(e); m = e.ram(0, 0x800)
hp0, lives0 = m[0x51A], m[0x11]
def safe(m): return m[0x51A] >= hp0 and m[0x11] == lives0
def live(m): return [f for f in fb.foes(m, IDS) if f[3] > 0 and f[3] < 100]
print("start: toad", fb.tx(m), fb.th(m), "foes", fb.foes(m, IDS), flush=True)
sa = e.msave(); cands = []
for w in range(0, 160):
    e.mload(sa); L.ins = []; L.st("", w); m = e.ram(0, 0x800)
    if not safe(m) or not live(m): continue
    cur = sum(f[3] for f in live(m)); here = e.msave(); t = fb.toward(m, {0x62})
    for lead in fb.LEADS:
        e.mload(here); L.ins = [""] * w
        for x in fb.expand(lead, t): m = L.st(x)
        got = None
        for _ in range(40 if lead.endswith("!") else 26):
            if not safe(m): break
            c2 = sum(f[3] for f in live(m))
            if c2 < cur: got = c2; break
            m = L.st("")
        if got is None: continue
        for _ in range(70):
            if m[0x475] == 0 or not safe(m): break
            m = L.st("")
        if m[0x475] != 0 or not safe(m): continue
        cands.append((len(L.ins), got, list(L.ins), lead, w)); print("blow:", len(L.ins), "frames, left", got, lead, "wait", w, flush=True)
        if got == 0: break
    e.mfree(here)
    if any(c[1] == 0 for c in cands): break
kills = sorted([c for c in cands if c[1] == 0], key=lambda c: c[0])[:3]
best = None
for i, (f, got, ins, lead, w) in enumerate(kills):
    e.mload(sa)
    for b in ins: e.step(tuple(v for v in b.split("+") if v), 1)
    e.save(f"BWF_kill{i}")
    for jc in (3217, 3237):
        r = resync.run(f"BWF_kill{i}", jc - 40, jc - 1, jc, "R", 40, idle=False, objcheck=None, stop_first=True, extend=True)
        if r:
            tot, jm, rins, jend = r; total = ins + rins
            print(f"kill {i} ({f}) + resync {tot} via TAS {jm} -> {jend}: total {len(total)} (TAS 3172->{jend} = {jend - 3172})", flush=True)
            if best is None or len(total) - jend < len(best[0]) - best[1]: best = (total, jend)
            break
if best:
    e.mload(sa)
    for b in best[0]: e.step(tuple(v for v in b.split("+") if v), 1)
    e.save(f"BWF_j{best[1]}"); json.dump({"bookmark": bm, "jend": best[1], "inputs": best[0]}, open("knowledge/l12_bwfin.json", "w")); print("SAVED", len(best[0]), "frames to TAS", best[1], flush=True)
e.close()
