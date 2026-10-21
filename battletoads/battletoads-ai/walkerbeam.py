"""Walker (0x62, 79 hp) from F2W_pre: beam over hits (leads x waits, incl. jump-kicks and Select re-rolls), then BFS to stand
on the lower spring (0x36 at H 4800). Score = frame of standing on the spring. -> knowledge/walkerbeam.json, bookmark WB_spring"""
import json, os
from toads.emulator import BizHawk
W = int(os.environ.get("W", 4)); WAIT1 = int(os.environ.get("WAIT1", 60)); WAIT = int(os.environ.get("WAIT", 40))
e = BizHawk(log_name="walkerbeam.log"); e.load("F2W_pre")
F0 = 6456
def rd():
    m = e.ram(0, 0x800)
    wk = [(m[0x3FD+q] | m[0x3EE+q] << 8, m[0x439+q] | m[0x42A+q] << 8, m[0x51A+q]) for q in range(2, 15) if m[0x3C1+q] == 0x62]
    sp = [m[0x3FD+q] | m[0x3EE+q] << 8 for q in range(2, 15) if m[0x3C1+q] == 0x36 and (m[0x439+q] | m[0x42A+q] << 8) == 4800]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], hp=m[0x51A], lives=m[0x11], an=m[0x3B5], wk=wk, sp=sp)
def tow(s):
    if not s["wk"]: return "Left"
    d = (s["wk"][0][0] - s["x"] + 256) % 512 - 256; return "Right" if d >= 0 else "Left"
LEADS = [[], ["T"], ["T"]*4, ["J"]*4, ["J"]*8, ["J"]*12, ["T+J"]*4, ["T+J"]*8, ["T+J"]*12, ["T+J"]*16, ["W+J"]*6, ["J"]*16, ["SE"], ["SE","","SE"]]
def play(lead, t):
    w = "Left" if t == "Right" else "Right"; seq = []
    for tok in lead:
        b = "+".join({"T": t, "W": w, "J": "A", "SE": "Select"}[p] for p in tok.split("+") if p) if tok else ""
        e.step(tuple(v for v in b.split("+") if v), 1); seq.append(b)
    return seq
beam = [(e.msave(), [], None)]
for hitno in range(8):
    nxt = []
    for sid, path, hpl in beam:
        e.mload(sid); base_seen = False
        for w in range(WAIT1 if hpl is None else WAIT):
            s = rd()
            if s["hp"] < 47 or s["lives"] < 4: break
            if not s["wk"]: 
                e.step((), 1); path = path + [""]; continue
            hp0 = s["wk"][0][2]
            if hp0 == 0: break
            here = e.msave(); t = tow(s)
            for lead in LEADS:
                e.mload(here)
                seq = play(lead, t) + ["B"]
                e.step(("B",) if "J" not in "".join(lead) else (t, "B"), 1)
                got = None
                for i in range(30):
                    s2 = rd()
                    if s2["hp"] < 47 or s2["lives"] < 4: break
                    if s2["wk"] and s2["wk"][0][2] < hp0: got = s2["wk"][0][2]; break
                    if not s2["wk"]: break
                    e.step((), 1); seq.append("")
                if got is not None:
                    nxt.append((len(path) + w + len(seq), e.msave(), path + [""] * 0 + seq, got))
            e.mload(here); e.mfree(here)
            e.step((), 1); path = path + [""]
    if not nxt: print("no next hit", flush=True); break
    nxt.sort(key=lambda n: (n[3], n[0]))
    keep = []; seenhp = {}
    for n in nxt:
        if len(keep) < W: keep.append(n)
        else: e.mfree(n[1])
    for sid, _, _ in beam: e.mfree(sid)
    beam = [(n[1], n[2], n[3]) for n in keep]
    print("hit", hitno + 1, [(F0 + len(n[2]), n[3]) for n in keep], flush=True)
    if all(n[3] == 0 for n in keep): break
best = None
for sid, path, hpl in beam:
    if hpl != 0: continue
    e.mload(sid)
    # BFS to stand on the lower spring
    layer = [(e.msave(), [])]; seen = set(); goal = None
    for d in range(120):
        nl = []
        for s2, p2 in layer:
            for b in ("", "Left", "Right", "Left+A", "Right+A", "A"):
                e.mload(s2); e.step(tuple(v for v in b.split("+") if v), 1); s = rd()
                if s["hp"] < 47 or s["lives"] < 4: continue
                if s["z"] == 0 and 4800 <= s["H"] <= 4810 and s["sp"]: goal = (e.msave(), p2 + [b]); break
                k = (s["x"], s["H"], s["z"], s["an"] // 4)
                if k in seen: continue
                seen.add(k); nl.append((e.msave(), p2 + [b]))
            if goal: break
        for s2, _ in layer: e.mfree(s2)
        if goal or not nl: break
        layer = sorted(nl, key=lambda n: 0)[:400]
        for n in nl[400:]: e.mfree(n[0])
    if goal:
        f = F0 + len(path) + len(goal[1])
        print("ON SPRING at", f, "(kill path", F0 + len(path), ")", flush=True)
        if best is None or f < best[0]:
            best = (f, path + goal[1]); e.mload(goal[0]); e.save("WB_spring")
if best:
    json.dump({"bookmark": "F2W_pre", "f0": F0, "inputs": best[1], "on_spring": best[0]}, open("knowledge/walkerbeam.json", "w"))
    print("BEST on spring at", best[0], flush=True)
e.close()
