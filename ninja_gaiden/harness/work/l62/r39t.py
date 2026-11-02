import sys; sys.path.insert(0,'work/l62')
from lib62 import *
cyc=[row(x) for x in 'Right A+Right A+Right A+Right A+Left Left'.split()]
np0=int(sys.argv[1]) if len(sys.argv)>1 else 10
fc=base(33290,pokes={0xC9:133,0x64:np0})
ent=cyc*5+[row('Right')]*(33375-33290-30)
for lag in (21,22,23,24,25):
    pre=(ent+[row('Right')]*40)[:61+lag]
    T1=33352
    tl=legalize_tas(T1,33712,pre[-150:])
    rows=pre+tl
    st=run(fc,rows)
    ev=events(st,33291)
    div=next(((33291+i, XY_:=RXY(s), tas_xy(33291+i-lag)) for i,s in enumerate(st) if i>=len(pre) and 33291+i-lag<=33712 and RXY(s)!=tas_xy(33291+i-lag)),None)
    print('lag',lag,'T1',T1,legal_ok(rows) or 'ok','div',div, [e for e in ev if 'spawn' not in e and 'gone' not in e][:12], flush=True)
fc.close()
