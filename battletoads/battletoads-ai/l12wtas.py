"""Walker fight by the TAS's inputs (75155..END) from our F2W timeline (walker spawn 6479 == TAS 75155), with an x-nudge
prefix (k frames of Left/Right/idle replacing the first k TAS frames). Reports walker hp track, spring landing, hurt."""
import json, re, sys
from toads.emulator import BizHawk
import l12f2full as L
rows={}
for l in open('tas/watch_1p_l12.txt'):
    if ' x=' not in l: continue
    f=int(l.split()[0][1:])
    if 75100<=f<=75400: rows[f]=re.search(r'p1=(\S+)',l).group(1)
def btn(p):
    if 'le' in p and 'ri' in p: p=p.replace('le','').replace('ri','') or '-'
    return L.btn(p) if p!='-' else ()
q3=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12q3.json'))['inputs']]
e=BizHawk(log_name="l12wtas.log"); e.load("F2W_pre")
for b in q3[6540:6540+(6479-6456)-6]: e.step(tuple(v for v in b.split('+') if v),1)
base=e.msave(); F=6479-6
def rd():
    m=e.ram(0,0x800)
    wk=[m[0x51A+q] for q in range(2,15) if m[0x3C1+q]==0x62]
    sp=[m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x36 and (m[0x439+q]|m[0x42A+q]<<8)==4800]
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, z=m[0x475], hp=m[0x51A], lives=m[0x11], wk=wk, sp=sp)
for nudge in ("", "Left", "Right"):
    for k in (0, 2, 4, 6):
        e.mload(base); f=F
        seq=[(nudge,) if nudge else ()]*k + [btn(rows[j]) for j in range(75149+k, 75345)]
        hits=[]; prev=79; out=None
        for b in seq:
            e.step(b,1); f+=1; s=rd()
            if s["hp"]<47 or s["lives"]<4: out=("HURT",f,s["x"],s["H"]); break
            if s["wk"] and s["wk"][0]<prev: hits.append((f,s["wk"][0])); prev=s["wk"][0]
        print(nudge or '-', k, "hits", hits, out or ("end", f, rd()["x"], rd()["H"], rd()["z"], rd()["sp"]), flush=True)
e.close()
