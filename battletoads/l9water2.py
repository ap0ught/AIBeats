"""Terra Tubes: from L9c 7852 (813,6502) land on the ledge at H 6406 (x 884-904) fast, without being carried (2026-10-07).
Then probe: walk off its right end into the water below and swim right.  -> bookmark L9_ledgeB, knowledge/l9_water2.json"""
import json
from toads.emulator import BizHawk
e = BizHawk(log_name="l9water2.log"); e.load("L9_at7800")
l9 = [x.replace(",", "+") for x in json.load(open("logs/pbeam_L9c.json"))["inputs"]]
for b in l9[7800:7852]: e.step(tuple(v for v in b.split("+") if v), 1)
def rd():
    m = e.ram(0, 0x800); return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], camx=m[0x87] | m[0x88] << 8)
ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("Down",), ("Down", "Right"), ("Up", "A"), ("B",)]
root = e.msave(); print("root", rd(), flush=True)
frontier = [(root, [])]; seen = set(); goal = None
for step in range(130):
    nxt = []
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid); e.step(a, 2); s = rd()
            if s["hp"] < 47 or s["lives"] < 4 or s["an"] in (36, 37): continue
            if s["an"] in (98, 99) and s["x"] >= 860 and s["H"] <= 6420: goal = (e.msave(), path + [a], s); break
            k = (s["x"], s["H"], s["z"], s["an"] // 4)
            if k in seen: continue
            seen.add(k); nxt.append((abs(s["x"] - 905) + abs(s["H"] - 6380) * 2, e.msave(), path + [a]))
        if goal: break
    for sid, _ in frontier:
        if sid != root: e.mfree(sid)
    if goal: break
    nxt.sort(key=lambda n: n[0]); frontier = [(sid, p) for _, sid, p in nxt[:1000]]
    for _, sid, _ in nxt[1000:]: e.mfree(sid)
    if step % 10 == 0: print("step", step, "best", nxt[0][0] if nxt else None, flush=True)
    if not frontier: print("died out", flush=True); break
if not goal: print("no water found", flush=True); e.close(); raise SystemExit
sid, path, s = goal; print("WATER after", len(path) * 2, "frames:", s, flush=True)
e.mload(sid); e.save("L9_waterC"); base = e.msave()
json.dump({"from": "L9c 7852", "inputs": [b for a in path for b in ["+".join(a)] * 2]}, open("knowledge/l9_water2.json", "w"))
for name, seq in [("Right 150", [("Right",)] * 150), ("Right+A 14, Right", [("Right", "A")] * 14 + [("Right",)] * 140), ("Right 10, Down 30, Right", [("Right",)] * 10 + [("Down",)] * 30 + [("Right",)] * 120), ("B, Right", [("B",)] + [()] * 15 + [("Right",)] * 140), ("idle 30, Right", [()] * 30 + [("Right",)] * 140)]:
    e.mload(base); out = []
    for i, b in enumerate(seq):
        e.step(b, 1); q = rd()
        if i % 20 == 19 or (q["an"] in (98, 99) and (not out or out[-1][-1] not in (98, 99))): out.append((i + 1, q["x"], q["H"], q["z"], q["camx"], q["an"]))
        if q["hp"] < 47 or q["lives"] < 4: out.append(("HURT", i + 1, q["x"], q["H"], q["an"])); break
    print(name, out[:9], flush=True)
e.close()
