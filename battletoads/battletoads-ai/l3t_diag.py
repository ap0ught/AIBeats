"""python l3t_diag.py [frames_back]: replay the current wall map, trace the last N frames before the crash, tile shots."""
import l3t, json, shutil, sys
from toads.emulator import BizHawk, SHOTS_DIR
from PIL import Image
import glob
back=int(sys.argv[1]) if len(sys.argv)>1 else 160
presses=sorted({tuple(e) for e in json.load(open("knowledge/l3_walls.json"))})
e=BizHawk(log_name="l3tdiag.log")
outcome,ins,info=l3t.attempt(e,1,presses); print(outcome,info)
out=SHOTS_DIR/"tunnel_diag"; out.mkdir(exist_ok=True)
for f in out.glob("*.png"): f.unlink()
e.load("L3_bike_go"); n=len(ins); k=0
for i,b in enumerate(ins):
    e.step(tuple(x for x in b.split("+") if x),1); r=e.ram_all(); q=l3t.rd(r)
    if i>=n-back:
        if i%10==0 or "A" in b:
            objs=[(sl,r[0x3c1+sl],r[0x3fd+sl]+256*((r[0x3ee+sl]+128)%256-128),r[0x41b+sl],r[0x439+sl]) for sl in range(2,12) if r[0x3c1+sl] and sl!=3]
            print(f"   f{i} {b:4s} x{q['x']} y{q['y']} z{q['z']} h{q['h']} spd{q['spd']} hp{q['hp']} objs{objs}")
        if i%16==0: shutil.copyfile(e.screenshot("_td"), out/f"{k:03d}.png"); k+=1
e.close()
files=sorted(glob.glob(str(out/"*.png"))); W,H=256,224; cols=5; r=(len(files)+cols-1)//cols
sheet=Image.new("RGB",(cols*W,r*H))
for i,f in enumerate(files): sheet.paste(Image.open(f).convert("RGB"),((i%cols)*W,(i//cols)*H))
sheet.resize((cols*W//2,r*H//2)).save("shots/tunnel_diag_sheet.png"); print(len(files),"shots")
