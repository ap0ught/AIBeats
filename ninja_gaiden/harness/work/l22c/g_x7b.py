import sys; sys.path.insert(0,'work/w21')
from wlib import spec
PRE=spec("LU:2 L:1 AL:2 LU:1 BLU:2 L:1 AL:2 L:1 LU:2 L:3 LU:1")   # rows 1327-1344 of v3
S1=["","U:1","U:1 RU:1","RU:2","-:1 U:1 RU:2","U:1 RU:2"]
S2=["","R:1","R:2","-:1 R:2","-:1 R:1 RU:1","R:1 RU:1"]
S3=["R:1 RU:1 ARU:1 AR:1","R:1 ARU:1 AR:1","L:1 R:1 RU:1 ARU:1 AR:1","RU:1 ARU:1 AR:1","ARU:1 AR:1"]
def cands():
    out=[]
    for w in range(0,6):
        for lw in ('L','LU'):
            for i1,s1 in enumerate(S1):
                for i2,s2 in enumerate(S2):
                    for i3,s3 in enumerate(S3):
                        t=f"{lw}:{w} " if w else ""
                        w_=PRE+spec((t+s1+" ALU:1 AL:1 "+s2+" ALU:2 "+s3+" R:8").replace("  "," ").strip())
                        out.append(((w,lw,i1,i2,i3),w_[:50]))
    return out
def goal(st,i): return st[i]['room']==8
