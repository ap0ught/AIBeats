"""L12h stage 1: new pre-face-2 fight (kill 5323, toad 14 px ahead on the spring like the TAS) + the TAS's double pump:
launch as the boot recovery ends (face 2 spawns), come down on the spring (A released, pressed again 3 frames before the landing),
second launch Left to the x-480 pole.  -> logs/fix/L12h_s1.json (inputs from L12h_g_f5000), bookmark L12h_s1 (on the pole)."""
import json, sys
from l12h_lib import *
G = seg("L12g")
R = json.load(open(FIX / "L12h_s0b.json"))
cands = [r for r in R if r["K"] <= 5323 and r["off"] >= 12]
print(len(cands), "fight candidates")
e = BizHawk(log_name="fix_l12h_s1d.log")
best = None
for c in cands[:6]:
    e.load("L12h_g_f5000"); run(e, G[5000:5140]); run(e, c["seq"]); kb = 5140 + len(c["seq"]); base = e.msave()
    s = rd(e); print("fight", {k: v for k, v in c.items() if k != "seq"}, "at", kb, s["x"], s["H"], flush=True)
    for a0 in range(kb + 12, kb + 26):
        for r0 in (0, 4, 8, 12):
            def go(Lhint):
                e.mload(base); k = kb; seq = []; ev = {}
                def st(b):
                    nonlocal k
                    e.step(bt(b), 1); k += 1; seq.append(b); return rd(e)
                while k < a0: st("")
                for i in range(60):
                    s = st("A")
                    if s["z"] == 8: ev["launch"] = k; break
                if "launch" not in ev: return ev, seq, None
                for i in range(r0): s = st("A")
                for i in range(160):
                    if Lhint and k >= Lhint - 3: b = "A"
                    elif k < ev["launch"] + 62: b = "Right+A"
                    else: b = "Right"
                    s = st(b)
                    if s["faces"] and "face" not in ev: ev["face"] = k
                    if not alive(s): ev["dead"] = k; return ev, seq, None
                    if s["z"] == 0: ev["land"] = (k, s["x"], s["H"], ob(s, 0x36, 4407, 40)); break
                if "land" not in ev or s["H"] < 4400: return ev, seq, None
                if not Lhint: return ev, seq, ev["land"][0]
                for i in range(40):
                    s = st("A")
                    if s["z"] == 8: ev["launch2"] = k; break
                if "launch2" not in ev: return ev, seq, None
                top = 0
                for i in range(100):
                    s = st("Left+A"); top = max(top, s["H"])
                    if not alive(s): ev["dead"] = k; break
                    if s["an"] in (94, 95, 96): ev["pole"] = (k, s["x"], s["H"]); break
                    if s["z"] == 0: ev["land2"] = (k, s["x"], s["H"]); break
                ev["apex2"] = top
                return ev, seq, None
            ev, seq, L = go(None)
            if L is None: print("  a0", a0, "r0", r0, ev, flush=True); continue
            ev, seq, _ = go(L)
            print("  a0", a0, "r0", r0, ev, flush=True)
            if "pole" in ev and "face" in ev and ev["pole"][1] == 480:
                key = (ev["face"], ev["pole"][0])
                if best is None or key < best[0]: best = (key, c, a0, r0, list(G[5000:5140]) + c["seq"] + seq, ev)
    e.mfree(base)
if best:
    print("BEST", best[0], {k: v for k, v in best[1].items() if k != "seq"}, best[2], best[3], best[5])
    save_piece("s1", "L12h_g_f5000", 5000, best[4], face=best[0][0], pole=best[0][1])
    e.load("L12h_g_f5000"); run(e, best[4]); e.save("L12h_s1"); print("saved L12h_s1 at", 5000 + len(best[4]), rd(e)["an"])
e.close()
