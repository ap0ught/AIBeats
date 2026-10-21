"""L12h walker finish from the saved hit-4 landings (logs/fix/L12h_w8_st4.json, made by l12h_w8a.py): for floor landings with the toad
to the RIGHT of the walker and the spring at/behind the toad: legal sprint ram Left (tap, gap, [run,] Left+B or a dash jump + Left+B).
When it kills, the toad flies on Left and may come down on the lower spring. Ranks by the frame the toad stands on the spring.
    python l12h_w8b.py [out=w8] [maxcand=120]"""
import json, sys
from l12h_lib import *
out = sys.argv[1] if len(sys.argv) > 1 else "w8"; MAXC = int(sys.argv[2]) if len(sys.argv) > 2 else 120
p = load_piece("s3c"); k0 = p["base_k"] + len(p["inputs"])
L4 = json.load(open(FIX / "L12h_w8_st4.json"))
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def hpw(s):
    f = foe(s); return f[0][2] if f else None
def spring(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
IDLE = (1, 2, 3, 4, 5, 6, 7, 8)
def onspring(s):
    sp = spring(s)
    return sp is not None and s["z"] == 0 and 4798 <= s["H"] <= 4812 and abs(dx(s["x"], sp)) <= 15
cands = [t for t in L4 if t["H"] <= 4770 and 6 <= dx(t["x"], t["wx"]) <= 70 and t["sp"] is not None and t["ready"] <= 6466]
seen = set(); uniq = []
for t in sorted(cands, key=lambda t: (t["ready"], t["x"])):
    key = (t["ready"], t["x"], t["wx"])
    if key in seen: continue
    seen.add(key); uniq.append(t)
print(len(cands), "candidates,", len(uniq), "distinct (ready, toad x, walker x):", [(t["ready"], t["x"], t["wx"], t["sp"]) for t in uniq[:40]], flush=True)
res = []
for t in uniq[:MAXC]:
    e.mload(root); run(e, t["seq"]); base = e.msave(); kb = k0 + len(t["seq"])
    for pre in (("Left", ""), ("Left", "", "Left"), ("Left", "", "Left", "Left"), ("Left", "", "Left", "Left", "Left"), ("", "Left", ""), ("Left", "", "Left", "Left", "Left", "Left", "Left")):
        for jump in (("Left+A", "Left+B"), ("Left+B",), ("Left+A", "Left+A", "Left+B"), ("Left+A+B",)):
            for hold in ("Left", ""):
                e.mload(base); k = kb; seq = list(pre) + list(jump); run(e, seq); k += len(seq)
                kill = None; board = None; s = rd(e)
                for i in range(70):
                    e.step(bt(hold), 1); k += 1; seq.append(hold); s = rd(e)
                    if not alive(s) or s["H"] < 4700: break
                    if kill is None and hpw(s) == 0: kill = k
                    if kill is None and i > 24: break
                    if kill and onspring(s) and s["an"] in IDLE: board = k; break
                    if kill and s["z"] == 0 and s["an"] in IDLE: break
                if kill:
                    res.append((board or 99999, kill, t["seq"] + seq, (t["ready"], t["x"], t["wx"], t["sp"]), (pre, jump, hold), s["x"], s["H"], spring(s)))
    e.mfree(base)
    b = min(res, key=lambda r: (r[0], r[1])) if res else None
    print("cand", (t["ready"], t["x"], t["wx"], t["sp"]), "-> kills so far", len(res), "best", (b[0], b[1], b[3], b[4]) if b else None, flush=True)
res.sort(key=lambda r: (r[0], r[1]))
for r in res[:12]: print("on the spring at", r[0], "kill", r[1], "from", r[3], r[4], "end", r[5], r[6], "spring", r[7], flush=True)
json.dump([dict(board=r[0], kill=r[1], seq=r[2]) for r in res[:40]], open(FIX / f"L12h_{out}_results.json", "w"))
if res and res[0][0] < 99999:
    b = res[0]
    save_piece(out, p["base"], p["base_k"], p["inputs"] + b[2], kill=b[1], board=b[0])
    e.load(p["base"]); run(e, p["inputs"] + b[2]); e.save("L12h_" + out); s = rd(e); print("saved", out, b[0], b[1], s["x"], s["H"], s["z"], s["an"], spring(s), "cam", s["cam"])
e.close()
