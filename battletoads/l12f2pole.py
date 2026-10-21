"""From our landing on the spring after the TAS-style kill (frame 5346), pump/launch/re-land/pump to the face-2 pole.
Scan: a1 = A start after landing, r1 = in-air frames before holding Right, a2 = frames after re-landing before the 2nd pump,
L = frames into the 2nd launch before Left. Success: hanging (an 94) on the pole at x 480. Reports face spawn and pole frames."""
import json
from toads.emulator import BizHawk
import l12f2full as L
e = BizHawk(log_name="l12f2pole.log"); e.load("L12p_f5000")
for f in range(5000, 5225): e.step(tuple(v for v in L.ins[f].split('+') if v), 1)
seq = L.build({})
f = 5225
for b in seq:
    e.step(b, 1); f += 1
    if f == 5346: break
def rd():
    m = e.ram(0, 0x800)
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                face=any(m[0x3C1+q]==0x60 for q in range(2,15)))
print("start", f, rd(), flush=True)
base = e.msave(); res = []
for a1 in range(0, 26, 2):
    for r1 in (0, 8, 16, 24):
        e.mload(base); k = 5346; face = None
        for i in range(a1): e.step((), 1); k += 1
        launched = False; landed = None
        for i in range(160):
            air = rd()["z"] == 8
            if not launched: b = ("A",)
            else: b = (("Right", "A") if i >= r1 else ("A",))
            e.step(b, 1); k += 1; s = rd()
            if s["face"] and face is None: face = k
            if s["z"] == 8 and s["H"] > 4440: launched = True
            if launched and s["z"] == 0: landed = (k, s["x"], s["H"]); break
            if s["hp"] < 47: break
        if not landed: continue
        mid = e.msave()
        for a2 in range(0, 20, 2):
            for Lt in (0, 4, 8, 12):
                e.mload(mid); k2 = landed[0]; f2 = face; pole = None
                for i in range(a2): e.step((), 1); k2 += 1
                up = False
                for i in range(120):
                    if not up: b = ("A",)
                    else: b = (("Left", "A") if i >= Lt else ("A",))
                    e.step(b, 1); k2 += 1; s = rd()
                    if s["face"] and f2 is None: f2 = k2
                    if s["z"] == 8 and s["H"] > landed[2] + 20: up = True
                    if s["an"] in (94, 95, 96): pole = (k2, s["x"]); break
                    if s["hp"] < 47 or s["lives"] < 4: break
                if pole:
                    res.append((pole[0], f2, a1, r1, a2, Lt, landed))
                    print("POLE", pole, "face", f2, "a1", a1, "r1", r1, "land", landed, "a2", a2, "Lt", Lt, flush=True)
            e.mfree(mid) if False else None
res.sort(); print("BEST", res[:5], "(old: face 5524, pole 5514)")
json.dump(res, open("knowledge/l12f2pole.json", "w"))
e.close()
