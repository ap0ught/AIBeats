import sys; sys.path.insert(0,'.')
from ng.solve import common as C, legality as L
from ng import fastcore as F
H=C.rows_of('logs/l21f_fol_v4_poweron.inputs.txt')
p=C.rows_of('work/l22f/p1.txt')
c=F.FastCore(boot_rows=None); c.put('s',open('states/mesen/l22p_ctl.mst','rb').read()); c.load('s')
res=[]
for k in range(584,594):
  for tail in ['-','Right']:
    for j in [0,2,4]:
      want=p[:k]+[('Left',)]*j+[(() if tail=='-' else ('Right',))]*60
      en=L.Enforcer(H[-1900:]); rows=[tuple(sorted(en.emit(w))) for w in want]
      c.load('s'); n,recs,_=c.step(rows,record='all')
      ch=next((i for i,s in enumerate(recs) if s['room']==7),None)
      s=recs[-1]; r=c.ram()
      res.append((ch,k,j,tail,s['room'],r[0x64],r[0xC9],C.abs_x(s),s['y']))
for z in sorted(res,key=lambda z:(z[0] is None, z[0] or 0)): print(z)
c.close()
