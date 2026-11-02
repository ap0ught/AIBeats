import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre0=rows_file('work/l62/b_r37a.txt')  # rows from 33590, goal at 34073
fc=base(mst='states/mesen/l62_33589.mst')
st0=run(fc,pre0)
for i in range(len(pre0)-6,len(pre0)): print(33590+i, RXY(st0[i]), st0[i]['hp65'])
for cut in range(len(pre0)-4,len(pre0)+1):
  for T1 in range(32995,33010):
    pre=pre0[:cut]; lag=33589+cut+1-T1
    tl=legalize_tas(T1,33175,pre[-150:]); rows=pre+tl
    if legal_ok(rows): continue
    st=run(fc,rows)
    rm=next((33590+k for k,s in enumerate(st) if s['room6e']==38),None)
    ev=[e for e in events(st,33590) if int(e.split()[0])>33590+cut and ('HIT' in e or 'np' in e)]
    print(cut,T1,'lag',lag,'room38',rm,ev[:4],flush=True)
fc.close()
