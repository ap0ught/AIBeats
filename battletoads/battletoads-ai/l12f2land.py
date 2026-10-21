"""Face 2 (pump variant): scan the lift drop and the jump to the wide platform for a landing equal to the old run's (6171:
x 458, H 4574, an 6, same facing/speed); then replay L12q3 from 6171 and report how far it holds."""
import json, sys
from toads.emulator import BizHawk
import l12f2full as L
T=L.T
WAIT, PD = int(sys.argv[1]), sys.argv[2]
q3=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12q3.json'))['inputs']]
pre=json.load(open(f'knowledge/l12f2c_{WAIT}{PD}_prefix.json'))['inputs']
e=BizHawk(log_name=f"l12f2land_{WAIT}{PD}.log"); e.load("L11r_end0")
def rd():
    m=e.ram(0,0x800)
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], spd=m[0x565], face=m[0x4A2]&0x40, sub=m[0x448], lvl=m[0x10])
# old reference state at 6171
e.load("L12p_f6000")
oldins=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12r.json'))['inputs']]
for b in oldins[6000:6171]: e.step(tuple(v for v in b.split('+') if v),1)
ref=rd(); print("old 6171", ref, flush=True)
e.load("L11r_end0")
# replay our prefix to the pole (find the pole index: first an 94 after 5346)
k=0
for b in pre:
    e.step(tuple(v for v in b.split('+') if v),1); k+=1
    if k>5400 and rd()["an"] in (94,95,96): break
pole=e.msave(); fp=k; print("pole at", fp, flush=True)
res=[]
for drop in range(fp+300, fp+700, 2):
    e.mload(pole); n=fp
    while n<drop: e.step((),1); n+=1
    for i in range(3): e.step(("Down",),1); n+=1
    on=None; s=rd()
    for i in range(80):
        s=rd()
        if s["z"]==0 and 4486<=s["H"]<=4500: on=n; break
        if s["hp"]<47: break
        e.step((),1); n+=1
    if on is None: continue
    base=e.msave()
    for jl in range(0, 40, 2):
        for d in ("Left","Right"):
            e.mload(base); k2=on
            for i in range(jl): e.step((),1); k2+=1
            land=None
            for i in range(60):
                e.step((d,"A"),1); k2+=1; s=rd()
                if s["hp"]<47: break
                if s["z"]==0 and s["H"]>=4570: land=(k2,s); break
            if land and abs(land[1]["x"]-ref["x"])<=2:
                res.append((land[0], drop, jl, d, land[1]["x"])); print("LAND", land[0], "x", land[1]["x"], "drop", drop, "jl", jl, d, flush=True)
    e.mfree(base)
res.sort(); print("best", res[:5])
json.dump(res, open(f"knowledge/l12f2land_{WAIT}{PD}.json","w"))
e.close()
