import sys; sys.path.insert(0,'work/l62')
from lib62 import *
cyc=[row(x) for x in 'Left A+Left A A+Right Right Right'.split()]
plat=rows_file('work/l61p/r40_plat_33863.txt')
fc=base(33735,pokes={0xC9:133,0x64:20})
for nA in range(1,12):
  for mid in ('tas','left'):
    ent=cyc*4+[row('A+Left')]*nA
    rows=list(ent)
    st=run(fc,rows+[row('Left')]*60)
    # find first frame X<=128 y<=185
    g=next((33736+i for i,s in enumerate(st) if RXY(s)[0]<=128 and RXY(s)[1]<=185),None)
    print('nA',nA,mid,'goal',g, [ (33736+i,RXY(s)) for i,s in enumerate(st)][len(ent)-1:len(ent)+50:6], flush=True)
    break
fc.close()
