import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pa=rows_file('work/l62/b_r40d.txt')
plat=rows_file('work/l61p/r40_plat_33863.txt')
fc=base(33735,pokes={0xC9:133,0x64:20})
st=run(fc,pa)
for i in range(len(pa)-8,len(pa)): print(33736+i, RXY(st[i]), P(pa[i]), st[i]['vy'])
res=[]
for cut in range(len(pa)-6,len(pa)+3):
  for w in range(0,8):
    for wr in ('Left','-','Right'):
      rows=pa[:cut]+[row(wr)]*w+plat+[row('Right')]*40
      if legal_ok(rows): continue
      st=run(fc,rows)
      g=next((33736+i for i,s in enumerate(st) if RXY(s)[1]<=96 and RXY(s)[0]>=123),None)
      if g: res.append((g,cut,w,wr,st[g-33736]['hp65']))
res.sort(); print(res[:10])
fc.close()
