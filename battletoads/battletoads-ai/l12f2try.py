"""Try lift-jump variants on the x-32 face-2 version and replay L12q3 from 6171; report Hornhead kill, walker-platform arrival and failure."""
import json
from toads.emulator import BizHawk
pre=json.load(open('knowledge/l12f2c_16ri_prefix.json'))['inputs']
q3=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12q3.json'))['inputs']]
e=BizHawk(log_name="l12f2try.log"); e.load("L11r_end0")
def rd():
    m=e.ram(0,0x800)
    hh=[m[0x51A+q] for q in range(2,15) if m[0x3C1+q]==0x5c]
    wk=[m[0x51A+q] for q in range(2,15) if m[0x3C1+q]==0x62]
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, z=m[0x475], hp=m[0x51A], lives=m[0x11], lvl=m[0x10], hh=hh, wk=wk, face=m[0x4A2]&0x40)
for b in pre[:5995]: e.step(tuple(v for v in b.split('+') if v),1)
for i in range(3): e.step(("Down",),1)
for i in range(18): e.step((),1)
base=e.msave(); f0=6016
for d in ("Left","Right"):
    for jl in range(10, 56, 2):
        e.mload(base); n=f0; seq=[]
        for i in range(jl): e.step((),1); n+=1
        land=None
        for i in range(60):
            e.step((d,"A"),1); n+=1; s=rd()
            if s["z"]==0 and s["H"]>=4570: land=(n,s["x"],s["face"]); break
        if not land: continue
        kill=None; walker=None; fail=None
        for k,b in enumerate(q3[6171:7200]):
            e.step(tuple(v for v in b.split('+') if v),1); n+=1; s=rd()
            if s["hp"]<47 or s["lives"]<4: fail=("hurt",6171+k); break
            if s["hh"] and s["hh"][0]==0 and kill is None: kill=6171+k
            if s["H"]>=4762 and s["z"]==0 and walker is None: walker=6171+k
        print(f"{d} jl {jl}: land {land} | q3 kill {kill} walker-platform {walker} fail {fail}", flush=True)
e.close()
