"""Face 3 the TAS's way from F3P_6980 (== TAS 75340): replay TAS 75340..END; banned Left+Right -> Left when the TAS toad is
airborne, nothing when it stands. Reports f3 spawn, pole, drop, landing, f3 gone, f4 spawn."""
import json, re, sys
from toads.emulator import BizHawk
import l12f2full as L
END = int(sys.argv[1]) if len(sys.argv) > 1 else 75960
rows={}; trow={}
for l in open('tas/watch_1p_l12.txt'):
    if ' x=' not in l: continue
    f=int(l.split()[0][1:])
    if 75330<=f<=76000:
        rows[f]=re.search(r'p1=(\S+)',l).group(1)
        m=re.search(r' x=(-?\d+) h=(-?\d+) z=(\d+)', l); trow[f]=(int(m.group(1)),int(m.group(2)),int(m.group(3)))
def btn(j):
    p=rows[j]
    if 'le' in p and 'ri' in p:
        p = p.replace('ri','') if trow[j][2]==8 else (p.replace('le','').replace('ri','') or '-')
    return L.btn(p) if p!='-' else ()
def rd(e):
    m=e.ram(0,0x800)
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, h=m[0x439], z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], cam=m[0x89]|m[0x8A]<<8,
                faces=sum(m[0x3C1+q]==0x60 for q in range(2,15)))
if __name__=="__main__":
    e=BizHawk(log_name="f3tas.log"); e.load("F3P_6980")
    f=6980; ev={}; dev=None
    for j in range(75340, END):
        e.step(btn(j),1); f+=1; s=rd(e)
        if dev is None and (abs(s["x"]-trow[j][0])%512 > 8 and abs(s["x"]-trow[j][0])%512 < 504 or abs(s["h"]-trow[j][1])>8): dev=(j,f,(s["x"],s["h"],s["z"]),trow[j])
        if s["hp"]<47 or s["lives"]<4: ev["HURT"]=(f,s["x"],s["H"]); break
        if s["faces"] and "f3" not in ev: ev["f3"]=f
        if s["an"] in (94,95,96) and "pole" not in ev: ev["pole"]=(f,s["x"])
        if "pole" in ev and s["an"] not in (94,95,96) and "drop" not in ev: ev["drop"]=f
        if "drop" in ev and s["z"]==0 and "land" not in ev: ev["land"]=(f,s["x"],s["H"])
        if "f3" in ev and not s["faces"] and "f3gone" not in ev: ev["f3gone"]=f
        if "f3gone" in ev and s["faces"] and "f4" not in ev: ev["f4"]=(f, s["cam"])
    print(ev); print("first deviation >8px:", dev)
    e.save("F3T_end"); e.close()
