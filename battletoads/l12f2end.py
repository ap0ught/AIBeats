"""Face 2, second half: from the pole (wait-W pump variant), idle to frame X, then the TAS's inputs 74640.. (drop, jump to the
spring, pump, lift, wide platform) with Left+Right swapped to A/leA. Scan X; report lift landing and the wide platform (old 6171)."""
import json, os
from toads.emulator import BizHawk
import l12f2full as L
T = L.T; WAIT = int(os.environ.get("WAIT", 32))
def tasbtn(j, sub=("A",)):
    p = T[j]["p"]
    if 'le' in p and 'ri' in p:
        p = p.replace('ri', '') if j >= 74600 else p.replace('le', '').replace('ri', '')   # pump on the first spring: A only; at the end: keep Left
        p = '-' if p == '' else p
    return L.btn(p) if p != '-' else ()
e = BizHawk(log_name="l12f2end.log"); e.load("F2B_spring5346")
def rd():
    m = e.ram(0, 0x800)
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                face=any(m[0x3C1+q]==0x60 for q in range(2,15)), wind=sum(m[0x3C1+q]==0x61 for q in range(2,15)),
                lift=[m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x34 and (m[0x439+q]|m[0x42A+q]<<8)==4488])
f=5346; pre=[]
for i in range(WAIT): e.step((),1); f+=1; pre.append("")
j=74214
while True:
    b=tasbtn(j); e.step(b,1); f+=1; j+=1; pre.append("+".join(b)); s=rd()
    if s["an"] in (94,95,96): break
print("pole", f, s, flush=True); pole=e.msave(); fpole=f
# wind timeline from the pole (idle)
e.mload(pole); wl=[]
for i in range(500):
    e.step((),1); s=rd()
    wl.append((fpole+i+1, s["wind"], s["face"]))
wstart=next(f for f,w,fa in wl if w); wend=max(f for f,w,fa in wl if w); fgone=next(f for f,w,fa in wl if f>wend and not fa)
print("wind", wstart, "-", wend, "face gone", fgone, flush=True)
res=[]
for X in range(wend-90, wend+20, 3):
    e.mload(pole); k=fpole
    while k < X: e.step((),1); k+=1
    j=74640; ev={}
    while j < 74830:
        b=tasbtn(j); e.step(b,1); k+=1; j+=1; s=rd()
        if s["hp"]<47 or s["lives"]<4: ev["HURT"]=(k,s["x"],s["H"]); break
        if s["lift"]: ev.setdefault("liftspawn",(k,s["lift"][0],s["x"]))
        if s["z"]==0 and 4486<=s["H"]<=4500: ev.setdefault("onlift",(k,s["x"]))
        if s["z"]==0 and s["H"]>=4570: ev["wide"]=(k,s["x"]); break
    print("X", X, ev, flush=True)
    if "wide" in ev: res.append((ev["wide"][0], X))
print("BEST", sorted(res)[:3], "(old wide 6171)")
json.dump({"pre": pre, "fpole": fpole, "wind": [wstart, wend], "res": sorted(res)}, open(f"knowledge/l12f2end_{WAIT}.json","w"))
e.close()
