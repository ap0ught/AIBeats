"""Faces 3/4 on L12f, staged scan with limits (2026-10-07). -> bookmark L12G_f4pole, knowledge/l12g.json (inputs from power-on)."""
import json
from toads.emulator import BizHawk, LOGS_DIR
import f3tas as F
L12f=[x.replace(',','+') for x in json.load(open(LOGS_DIR/"pbeam_L12f.json"))['inputs']]
e=BizHawk(log_name="l12g.log"); e.load("L11r_end0")
for b in L12f[:6782]: e.step(tuple(v for v in b.split('+') if v),1)
root=e.msave()
def lowsp():
    m=e.ram(0,0x800); return [m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x36 and (m[0x439+q]|m[0x42A+q]<<8)==4800]
def run(seq):
    for b in seq: e.step(tuple(v for v in b.split('+') if v),1)
# stage 1: ride r frames, TAS pump (22), Right+A to a pole
best1=None
for r in range(90, 170, 2):
    for d in ("", "Left", "Right"):
        e.mload(root); seq=[(d if (d and i<6) else "") for i in range(r)]
        run(seq)
        if F.rd(e)["z"]!=0: continue
        seq2=["+".join(F.btn(j)) for j in range(75340,75362)]; run(seq2)
        k=6782+r+22; face=None; pole=None; fl=[]
        for i in range(140):
            e.step(("Right","A"),1); k+=1; fl.append("Right+A"); s=F.rd(e)
            if s["hp"]<47 or s["lives"]<4: break
            if s["faces"] and face is None: face=k; spx=(lowsp() or [-1])[0]
            if s["an"] in (94,95,96): pole=(k,s["x"]); break
        if pole and face and pole[1]==32 and 380<=spx<=460 and (best1 is None or pole[0]<best1[0]): best1=(pole[0], face, pole[1], seq+seq2+fl); print("stage1", pole, "face3", face, "spring", spx, "ride", r, d, flush=True)
if not best1: raise SystemExit("stage 1 failed")
pk, f3, px, s1 = best1
e.mload(root); run(s1); p1=e.msave()
# stage 2-3: drop at t, land on lower spring, pump 22, Left+A to the upper landing
best3=None
for t in range(pk+300, pk+460):
    e.mload(p1); k=pk; seq=[]
    while k<t: e.step((),1); k+=1; seq.append("")
    for i in range(3): e.step(("Down",),1); k+=1; seq.append("Down")
    ok=False
    for i in range(80):
        e.step((),1); k+=1; seq.append(""); s=F.rd(e)
        if s["hp"]<47: break
        if s["z"]==0: ok = 4800<=s["H"]<=4810 and bool(lowsp()); break
    if not ok: continue
    for p in (18, 22, 26):
        e2=e.msave(); k2=k; sq=list(seq)
        for i in range(p): e.step(("A",),1); k2+=1; sq.append("A")
        air=False; land=None
        for i in range(140):
            e.step(("Left","A"),1); k2+=1; sq.append("Left+A"); s=F.rd(e)
            if s["hp"]<47 or s["lives"]<4: break
            if s["z"]==8: air=True
            if air and s["z"]==0: land=(k2, s["x"], s["H"]); break
        if land and land[2]>=4855 and (best3 is None or land[0]<best3[0]): best3=(land[0], land, sq); print("stage3 drop", t, "pump", p, "->", land, flush=True)
        e.mload(e2); e.mfree(e2)
if not best3: raise SystemExit("stage 3 failed")
e.mload(p1); run(best3[2]); p3=e.msave(); k3=best3[0]
# stage 4: upper spring pump to the face-4 pole
best4=None
for w in range(0, 30, 2):
    for p in (16, 20, 24):
        for fl in ("Left+A", "Right+A", "A"):
            e.mload(p3); k=k3; sq=[""]*w+["A"]*p; run(sq); k+=len(sq); f4=None; pole=None
            for i in range(140):
                e.step(tuple(fl.split('+')),1); k+=1; sq.append(fl); s=F.rd(e)
                if s["hp"]<47 or s["lives"]<4: break
                if s["faces"] and f4 is None: f4=k
                if s["an"] in (94,95,96) and s["H"]>=4940: pole=(k,s["x"]); break
                if s["z"]==0 and i>15: break
            if pole and (best4 is None or pole[0]<best4[0]): best4=(pole[0], f4, pole[1], sq); print("stage4", pole, "face4", f4, flush=True)
if not best4: raise SystemExit("stage 4 failed")
e.mload(p3); run(best4[3]); e.save("L12G_f4pole")
ins=L12f[:6782]+s1+best3[2]+best4[3]
print("RESULT face3", f3, "face4", best4[1], "pole4", best4[0], best4[2], "(L12f face4 = 7633)", flush=True)
json.dump({"bookmark":"L11r_end0","inputs":ins,"face4":best4[1],"pole4":best4[0],"polex":best4[2]}, open("knowledge/l12g.json","w"))
e.close()
