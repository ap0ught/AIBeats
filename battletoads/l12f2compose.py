"""Compose: old L12r[:5225] + TAS-style kill (l12f2full build up to 5346) + pump variant to the pole + lift ride + jump to the wide
platform; then compare the landing with the old run's (6171: x 458) and replay L12q3's inputs from 6171 on, reporting where it ends.
    python l12f2compose.py <wait> <pumpdir> <drop offset d> <jump-after jl>"""
import json, sys
from toads.emulator import BizHawk
import l12f2full as L
T=L.T
WAIT, PD, D, JL = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
q3 = [x.replace(',','+') for x in json.load(open('logs/pbeam_L12q3.json'))['inputs']]
def tasbtn(j):
    p=T[j]["p"]
    if 'le' in p and 'ri' in p:
        p=p.replace('le','').replace('ri','')
        if PD and 'A' in p: p=PD+p
        elif PD and p=='': p=PD
        p='-' if p=='' else p
    return L.btn(p) if p!='-' else ()
e=BizHawk(log_name=f"l12f2compose_{WAIT}{PD}.log"); e.load("L11r_end0")
ins=[]
def st(b): e.step(tuple(v for v in b.split('+') if v),1); ins.append(b)
for b in q3[:5225]: st(b)
for b in L.build({})[:5346-5225]: st("+".join(b))
def rd():
    m=e.ram(0,0x800)
    lift=[m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x34 and (m[0x439+q]|m[0x42A+q]<<8)==4488]
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], lift=lift, lvl=m[0x10], spd=m[0x565], face=m[0x4A2]&0x40)
for i in range(WAIT): st("")
j=74214
while True:
    st("+".join(tasbtn(j))); j+=1
    if rd()["an"] in (94,95,96): break
fp=len(ins); px=rd()["x"]; print("pole", fp, px, flush=True)
pole=e.msave(); arr=None
for i in range(800):
    e.step((),1); s=rd()
    if s["lift"] and abs(((s["lift"][0]-px)+256)%512-256)<=4: arr=fp+i+1; break
e.mload(pole)
while len(ins) < arr+D: st("")
for i in range(3): st("Down")
on=None
while True:
    k=len(ins); s=rd()
    if on is None and s["z"]==0 and 4486<=s["H"]<=4500: on=k
    if s["z"]==0 and s["H"]>=4570: break
    st("Left+A" if (on is not None and k-on>=JL) else "")
s=rd(); wide=len(ins); print("wide platform at", wide, s, "(old 6171: x 458 H 4574)", flush=True)
e.save(f"F2C_wide_{WAIT}{PD}")
json.dump({"bookmark": "L11r_end0", "inputs": ins}, open(f"knowledge/l12f2c_{WAIT}{PD}_prefix.json","w"))
# replay L12q3 from 6171 and watch
for k, b in enumerate(q3[6171:]):
    st(b); s=rd()
    if s["hp"]<47 or s["lives"]<4: print("HURT/died at q3 index", 6171+k, s, flush=True); break
    if s["lvl"]!=5: print("level changed at q3 index", 6171+k, "lvl", s["lvl"], "total", len(ins), flush=True); break
    if k % 400 == 0: print("q3", 6171+k, "ours", len(ins), s, flush=True)
e.close()
