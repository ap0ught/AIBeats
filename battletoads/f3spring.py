"""Face 3: drop at DROP onto the lower spring, wait w, pump (A, with direction d1), fly with d2 (+A); report the face-4 spawn
and the face-4 pole grab. Current route: face 4 at 7713."""
import json, sys
from toads.emulator import BizHawk
DROP=int(sys.argv[1]) if len(sys.argv)>1 else 7412
ins=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12q3.json'))['inputs']]
e=BizHawk(log_name=f"f3spring_{DROP}.log"); e.load("L12q_f7000")
for b in ins[7000:DROP]: e.step(tuple(v for v in b.split('+') if v),1)
def rd():
    m=e.ram(0,0x800)
    faces=[q for q in range(2,15) if m[0x3C1+q]==0x60]
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], cam=m[0x89]|m[0x8A]<<8, face=bool(faces))
for i in range(3): e.step(("Down",),1)
k=DROP+3
while True:
    e.step((),1); k+=1
    if rd()["z"]==0: break
land=k; print("on the spring at", land, rd(), flush=True); base=e.msave(); res=[]
for w in range(0, 40, 3):
    for d1 in ("", "Left", "Right"):
        for d2 in ("Left", "Right"):
            for pa in (14, 20, 26, 32):
                e.mload(base); k=land; facegone=False; f4=None; pole=None; top=0
                for i in range(w): e.step((),1); k+=1
                for i in range(pa): e.step(((d1,"A") if d1 else ("A",)),1); k+=1
                for i in range(150):
                    e.step((d2,"A"),1); k+=1; s=rd(); top=max(top,s["H"])
                    if s["hp"]<47 or s["lives"]<4: break
                    if not s["face"]: facegone=True
                    if facegone and s["face"] and f4 is None: f4=k
                    if s["an"] in (94,95,96): pole=(k, s["x"], s["H"]); break
                    if s["z"]==0 and s["H"]<4790: break
                if f4 or pole: print(f"w {w} d1 {d1 or '-'} pa {pa} d2 {d2}: face4 {f4} pole {pole} top {top}", flush=True); res.append((f4 or 99999, pole, w, d1, pa, d2))
res.sort(key=lambda r:(r[0], r[1][0] if r[1] else 99999)); print("BEST", res[:5])
e.close()
