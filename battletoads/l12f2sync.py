"""From our landing on the spring (F2B_spring5346 == TAS 74214), replay TAS inputs 74214.. with Left+Right swapped for A/'',
walking Right n frames on the spring first; report the face spawn and the pole grab (TAS: face 74289, pole 74376)."""
import json, re
from toads.emulator import BizHawk
import l12f2full as L
T = L.T
def tasbtn(j, sub="A"):
    p = T[j]["p"]
    if 'le' in p and 'ri' in p:
        p = p.replace('le', '').replace('ri', '')
        p = '-' if p == '' else p
    return L.btn(p) if p != '-' else ()
e = BizHawk(log_name="l12f2sync.log"); e.load("F2B_spring5346")
def rd():
    m = e.ram(0, 0x800)
    sp=[m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x36]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                face=any(m[0x3C1+q]==0x60 for q in range(2,15)), sp=sp)
base = e.msave(); print("start", rd(), "TAS 74214", T[74214], flush=True)
res = []
for walk in range(0, 16, 2):
    for skip in range(-12, 13, 3):           # +: drop that many leading TAS frames (the 17-frame wait before the pump); -: wait longer
        e.mload(base); f = 5346; face = None; pole = None; land2 = None; hurt = False
        for i in range(walk): e.step(("Right",), 1); f += 1
        if skip < 0:
            for i in range(-skip): e.step((), 1); f += 1
        j = 74214 + max(0, skip)
        while j < 74390:
            e.step(tasbtn(j), 1); f += 1; j += 1; s = rd()
            if s["hp"] < 47 or s["lives"] < 4: hurt = True; break
            if s["face"] and face is None: face = f
            if j > 74300 and s["z"] == 0 and land2 is None: land2 = (f, j, s["x"], s["H"], s["sp"])
            if s["an"] in (94, 95, 96): pole = (f, s["x"]); break
        tag = f"walk {walk} skip {skip:+d}: face {face} land2 {land2} pole {pole} {'HURT' if hurt else ''} end {rd()['x']},{rd()['H']}"
        print(tag, flush=True)
        if pole: res.append((pole[0], face, walk, skip))
print("BEST", sorted(res)[:5], "(old face 5524 pole 5514; TAS-aligned face ~5416-5424)")
e.close()
