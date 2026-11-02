import sys; sys.path.insert(0,'work/l62')
from lib62 import *
cyc=[row(x) for x in 'Right A+Right A+Right A+Right A+Left Left'.split()]
np0=int(sys.argv[1]) if len(sys.argv)>1 else 10
fc=base(33290,pokes={0xC9:133,0x64:np0})
ent=cyc*5+[row('Right')]*80
lag=23
pre=ent[:61+lag]; tl=legalize_tas(33352,33712,pre[-150:]); rows0=pre+tl
res=[]
for t in range(33390,33442):
  for b in ('B',):
    rows=list(rows0); i=t-33291
    for j in (i,i+1): rows[j]=tuple(sorted(set(rows[j])|{b}))
    if legal_ok(rows): continue
    st=run(fc,rows)
    ev=[e for e in events(st,33291) if 'spawn' not in e and 'gone' not in e]
    div=next(((33291+k, RXY(s), tas_xy(33291+k-lag)) for k,s in enumerate(st) if k>=len(pre) and 33291+k-lag<=33712 and RXY(s)!=tas_xy(33291+k-lag)),None)
    rm=next((33291+k for k,s in enumerate(st) if s['room6e']==40),None)
    print(t,b,'div',div,'room40',rm,ev[:6],flush=True)
fc.close()
