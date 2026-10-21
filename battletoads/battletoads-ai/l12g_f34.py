"""Transplant the face-3/face-4 sequence onto L12f (2026-10-07):
L12f inputs up to its spring boarding (q3 6862 - 80) -> ride until the lower spring is at x 16 -> TAS 75340..75361 ->
Right+A to the x-32 pole -> hang; drop 416 frames after face 3 spawns (Down x3) -> land on the lower spring -> A x22 ->
Left+A to the upper spring -> idle 2, A x16, Left+A to the x-352 pole. Saves bookmark L12G_f4pole and knowledge/l12g_f34.json."""
import json
from toads.emulator import BizHawk, LOGS_DIR
import f3tas as F
L12f=[x.replace(',','+') for x in json.load(open(LOGS_DIR/"pbeam_L12f.json"))['inputs']]
e=BizHawk(log_name="l12g_f34.log"); e.load("L11r_end0")
ins=[]
def st(b): e.step(tuple(v for v in b.split('+') if v),1); ins.append(b)
def lowsp():
    m=e.ram(0,0x800); return [m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x36 and (m[0x439+q]|m[0x42A+q]<<8)==4800]
for b in L12f[:6782]: st(b)
s=F.rd(e); print("at 6782", s, lowsp(), flush=True)
while True:
    sp=lowsp()
    if sp and sp[0]==16: break
    st("")
    if len(ins)>7100: raise SystemExit("spring never at 16")
print("spring at 16 at", len(ins), F.rd(e), flush=True)
for j in range(75340, 75362): st("+".join(F.btn(j)))
while F.rd(e)["an"] not in (94,95,96): st("Right+A")
print("pole x32 at", len(ins), F.rd(e)["x"], flush=True)
f3=None
# face 3 spawn frame: find by replaying? track while hanging
k0=len(ins)
# we need the frame face 3 spawned: re-derive by checking faces now (already spawned) -> search back is costly; use relative 7450-7051=399 frames after the pole grab
while len(ins) < k0 + 399: st("")
for i in range(3): st("Down")
while F.rd(e)["z"]!=0: st("")
s=F.rd(e); print("landed after drop", len(ins), s["x"], s["H"], lowsp(), flush=True)
for i in range(22): st("A")
air=False
while True:
    st("Left+A"); s=F.rd(e)
    if s["z"]==8: air=True
    if air and s["z"]==0: break
print("upper landing", len(ins), s["x"], s["H"], flush=True)
st(""); st("")
for i in range(16): st("A")
f4=None
while True:
    st("Left+A"); s=F.rd(e)
    if s["faces"] and f4 is None: f4=len(ins)
    if s["an"] in (94,95,96): break
    if s["hp"]<47 or len(ins)>8200: raise SystemExit("no F4 pole")
print("F4 face", f4, "F4 pole", len(ins), s["x"], s["H"], "(L12f old F4: q3 7713-80 = 7633)", flush=True)
e.save("L12G_f4pole")
json.dump({"bookmark":"L11r_end0","inputs":ins,"f4":f4}, open("knowledge/l12g_f34.json","w"))
e.close()
