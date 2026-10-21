"""L12h walker finish from the floor state after hit 4 (piece w7r4: frame 6454, toad 25 on the floor, walker 17 at 15 hp, lower spring 34
and arriving): a short jump (any direction) and an AIR kick so that the hit registers while the toad is airborne above the spring level,
then it comes down on the spring. Brute force; ranks by the frame the toad stands on the spring with the walker dead.
    python l12h_w10.py [piece=w7r4] [out=w10]"""
import json, sys, itertools
from l12h_lib import *
pn = sys.argv[1] if len(sys.argv) > 1 else "w7r4"; out = sys.argv[2] if len(sys.argv) > 2 else "w10"
p = load_piece(pn); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def hpw(s):
    f = foe(s); return f[0][2] if f else None
def spring(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
IDLE = (1, 2, 3, 4, 5, 6, 7, 8)
def onspring(s):
    sp = spring(s)
    return sp is not None and s["z"] == 0 and 4798 <= s["H"] <= 4812 and abs(dx(s["x"], sp)) <= 14
s0 = rd(e); print("root", k0, s0["x"], s0["H"], s0["z"], s0["an"], "walker", foe(s0), "spring", spring(s0), flush=True)
res = []; n = 0
for pre in ((), ("Left",), ("Left", ""), ("",), ("", ""), ("Right",), ("Left", "Left"), ("Left", "", "Left")):
    for jd in ("Left", "", "Right"):
        for ja in (1, 2, 3, 4, 6, 9):
            for bd in range(1, 11):
                for bdir in ("Right", "Left", ""):
                    for mid in ("", jd):                         # direction held between the jump frame and B
                        for hold in ("", "Left", "Right"):
                            seq = list(pre) + [(jd + "+A").strip("+")]
                            for i in range(1, bd): seq.append("+".join(x for x in (mid, "A" if i < ja else "") if x))
                            seq.append("+".join(x for x in (bdir, "B", "A" if bd < ja else "") if x))
                            e.mload(root); run(e, seq); k = k0 + len(seq); kill = None; board = None; air = None; s = rd(e); n += 1
                            for i in range(50):
                                b = "+".join(x for x in (hold, "A" if bd + 1 + i < ja else "") if x)
                                e.step(bt(b), 1); k += 1; seq.append(b); s = rd(e)
                                if not alive(s) or s["H"] < 4700: break
                                if kill is None and hpw(s) == 0: kill = k; air = s["z"]
                                if kill is None and i > 20: break
                                if kill and onspring(s) and s["an"] in IDLE:
                                    for j in range(4): e.step((), 1); k += 1; seq.append("")
                                    s = rd(e)
                                    if onspring(s): board = k - 4
                                    break
                                if kill and s["z"] == 0 and s["an"] in IDLE: break
                            if kill: res.append((board or 99999, kill, seq, (pre, jd, ja, bd, bdir, mid, hold), s["x"], s["H"], spring(s), air))
    print("pre", pre, "trials", n, "kills", len(res), "best", min(((r[0], r[1], r[3]) for r in res), default=None), flush=True)
res.sort(key=lambda r: (r[0], r[1]))
for r in res[:14]: print("on the spring at", r[0], "kill", r[1], "airborne at the kill:", r[7], r[3], "end", r[4], r[5], "spring", r[6], flush=True)
json.dump([dict(board=r[0], kill=r[1], seq=r[2]) for r in res[:40]], open(FIX / f"L12h_{out}_results.json", "w"))
if res and res[0][0] < 99999:
    b = res[0]
    save_piece(out, p["base"], p["base_k"], p["inputs"] + b[2], kill=b[1], board=b[0])
    e.load(p["base"]); run(e, p["inputs"] + b[2]); e.save("L12h_" + out); s = rd(e); print("saved", out, b[0], b[1], s["x"], s["H"], s["z"], s["an"], spring(s), "cam", s["cam"])
e.close()
