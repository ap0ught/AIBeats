"""Face 2 from a given pump variant: grab the pole, hang until the lift (0x34, H 4488) is about to pass under the toad, drop
onto it, then jump to the wide platform (H 4574). Scans the drop moment and the jump; reports the wide-platform frame (old 6171)."""
import json, sys
from toads.emulator import BizHawk
import l12f2full as L
T=L.T
WAIT, PD = int(sys.argv[1]), sys.argv[2]
def tasbtn(j):
    p=T[j]["p"]
    if 'le' in p and 'ri' in p:
        p=p.replace('le','').replace('ri','')
        if PD and 'A' in p: p=PD+p
        elif PD and p=='': p=PD
        p='-' if p=='' else p
    return L.btn(p) if p!='-' else ()
e=BizHawk(log_name=f"l12f2lift_{WAIT}{PD}.log"); e.load("F2B_spring5346")
def rd():
    m=e.ram(0,0x800)
    lift=[m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x34 and (m[0x439+q]|m[0x42A+q]<<8)==4488]
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], lift=lift,
                face=any(m[0x3C1+q]==0x60 for q in range(2,15)), wind=any(m[0x3C1+q]==0x61 for q in range(2,15)))
f=5346; pre=[]; face=None
for i in range(WAIT): e.step((),1); f+=1; pre.append("")
j=74214
while j<74400:
    b=tasbtn(j); e.step(b,1); f+=1; j+=1; pre.append("+".join(b)); s=rd()
    if s["face"] and face is None: face=f
    if s["an"] in (94,95,96): break
print("pole", f, s["x"], "face", face, flush=True)
pole=e.msave(); fp=f; px=s["x"]
# when does the lift reach the pole?
e.mload(pole); arr=None; k=fp
for i in range(800):
    e.step((),1); k+=1; s=rd()
    if s["lift"] and abs(((s["lift"][0]-px)+256)%512-256) <= 4: arr=k; break
print("lift at the pole x at", arr, flush=True)
best=None
for d in range(-30, 6, 2):
    for jl in (0, 4, 8, 12, 16, 20):
        e.mload(pole); k=fp
        while k < arr+d: e.step((),1); k+=1
        for i in range(3): e.step(("Down",),1); k+=1
        on=None; wide=None
        for i in range(150):
            if on is None: b=()
            else: b=("Left","A") if k-on>=jl else ()
            e.step(b,1); k+=1; s=rd()
            if s["hp"]<47 or s["lives"]<4: break
            if on is None and s["z"]==0 and 4486<=s["H"]<=4500: on=k
            if s["z"]==0 and s["H"]>=4570: wide=k; break
        if wide and (best is None or wide<best[0]): best=(wide, d, jl, on); print("wide", wide, "drop", arr+d, "on lift", on, "jump after", jl, flush=True)
print("RESULT", WAIT, PD, "face", face, "pole", fp, px, "best", best, "(old wide 6171)")
e.close()
