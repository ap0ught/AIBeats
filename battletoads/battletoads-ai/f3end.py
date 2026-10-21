"""From the face-3 pole (x 32, via F3P_6980 + TAS inputs to j0 + Right+A), scan: drop time t, drop steer, pump frames p after
landing on the lower spring, launch direction; report the face-4 spawn (face gone then face again) and a face-4 pole grab.
Current route: face 4 at 7713 (L12q3)."""
import json
from toads.emulator import BizHawk
import f3tas as F
e=BizHawk(log_name="f3end.log"); e.load("F3P_6980")
f=6980
for j in range(75340, 75362): e.step(F.btn(j),1); f+=1
while True:
    e.step(("Right","A"),1); f+=1
    if F.rd(e)["an"] in (94,95,96): break
pole=e.msave(); fp=f; print("pole at", fp, flush=True)
def lowsp(e):
    m=e.ram(0,0x800); return [m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x36 and (m[0x439+q]|m[0x42A+q]<<8)==4800]
res=[]
for t in range(7380, 7490, 4):
    for dd in (("Down",), ("Down","Right"), ("Down","Left")):
        for steer in ("", "Right", "Left"):
            e.mload(pole); k=fp
            while k<t: e.step((),1); k+=1
            for i in range(3): e.step(dd,1); k+=1
            on=None
            for i in range(90):
                e.step((steer,) if steer else (),1); k+=1; s=F.rd(e)
                if s["hp"]<47 or s["lives"]<4: break
                if s["z"]==0:
                    if 4800<=s["H"]<=4810 and lowsp(e): on=k
                    break
            if not on: continue
            base=e.msave()
            for w in (0, 6, 12, 20, 30):
                for p in (20, 26, 32):
                    for fl in ("Left+A", "Right+A", "A"):
                        e.mload(base); k2=on; gone=None; f4=None; pole4=None
                        for i in range(w): e.step((),1); k2+=1
                        for i in range(p): e.step(("A",),1); k2+=1
                        for i in range(150):
                            e.step(tuple(fl.split('+')),1); k2+=1; s=F.rd(e)
                            if s["hp"]<47 or s["lives"]<4: break
                            if not s["faces"] and gone is None: gone=k2
                            if gone and s["faces"] and f4 is None: f4=(k2, s["cam"])
                            if f4 and s["an"] in (94,95,96): pole4=(k2, s["x"], s["H"]); break
                            if s["z"]==0 and s["H"]<4790: break
                        if f4: res.append((f4[0], pole4, t, dd, steer, w, p, fl)); print("F4", f4, "pole", pole4, "drop", t, dd, steer, "w", w, "p", p, fl, flush=True)
            e.mfree(base)
res.sort(key=lambda r:(r[0], r[1][0] if r[1] else 99999)); print("BEST", res[:5])
json.dump([list(map(str,r)) for r in res[:20]], open("knowledge/f3end.json","w"))
e.close()
