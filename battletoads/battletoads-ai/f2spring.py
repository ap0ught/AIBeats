"""Face 2: drop off the pole and ride the spring (0x36) to the wide platform (H 4574) sooner than the old lift (6171).
Beam over 2-frame macros from L12r frame ROOT (hanging); goal z 0 and H >= 4570. -> knowledge/f2spring.json, bookmark F2S_goal"""
import json, os, sys
from toads.emulator import BizHawk
ROOT = int(os.environ.get("ROOT", 5926)); W = int(os.environ.get("W", 500))
ins=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12r.json'))['inputs']]
e = BizHawk(log_name=f"f2spring_{ROOT}.log"); e.load("L12p_f5500")
for f in range(5500, ROOT): e.step(tuple(v for v in ins[f].split('+') if v), 1)
SEQ = {"RunR": [("Right",), ()], "RunL": [("Left",), ()]}
ACTS = [(), ("Down",), ("Right",), ("Left",), ("A",), ("Right","A"), ("Left","A"), ("Down","Right"), ("Down","Left"), "RunR", "RunL"]
def rd():
    m = e.ram(0, 0x800)
    sp=[(m[0x3FD+q] | m[0x3EE+q] << 8, m[0x439+q]|m[0x42A+q]<<8) for q in range(2,15) if m[0x3C1+q]==0x36]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], spd=m[0x565], sp=sp)
frontier=[(e.msave(), [])]; seen=set(); goal=None
for step in range(130):
    nxt=[]
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid)
            fr = SEQ[a] if isinstance(a, str) else [a, a]
            for b in fr: e.step(b, 1)
            s=rd()
            if s["hp"]<47 or s["lives"]<4: continue
            p2 = path + ["+".join(b) for b in fr]
            if s["z"]==0 and s["H"]>=4570: goal=(e.msave(), p2, s); break
            k=(step, s["x"], s["H"], s["z"], s["an"]//4, s["spd"]//32)
            if k in seen: continue
            seen.add(k)
            spx = s["sp"][0][0] if s["sp"] else s["x"]
            dx = min((spx - s["x"]) % 512, (s["x"] - spx) % 512)
            score = -s["H"]*3 + (dx if s["H"] < 4420 else 0)
            nxt.append((score, e.msave(), p2))
        if goal: break
    for sid,_ in frontier: e.mfree(sid)
    if goal: break
    nxt.sort(key=lambda n:n[0])
    for n in nxt[W:]: e.mfree(n[1])
    frontier=[(n[1], n[2]) for n in nxt[:W]]
    if step%10==0: print("step", step, "frame", ROOT+2*(step+1), "states", len(nxt), flush=True)
    if not frontier: print("died out", flush=True); break
if goal:
    sid, p2, s = goal
    print("GOAL: wide platform at frame", ROOT+len(p2), "(old 6171)", s, flush=True)
    e.mload(sid); e.save(f"F2S_goal_{ROOT}")
    json.dump({"a": ROOT, "inputs": p2, "land": ROOT+len(p2), "state": {k:v for k,v in s.items() if k!='sp'}}, open(f"knowledge/f2spring_{ROOT}.json","w"))
e.close()
