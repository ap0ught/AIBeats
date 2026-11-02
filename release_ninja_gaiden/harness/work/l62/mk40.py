import sys; sys.path.insert(0,'work/l62')
from lib62 import *
src=sys.argv[1]; out=sys.argv[2]
r=rows_file(src)
fc=base(mst='states/mesen/l62_33589.mst')
st=run(fc,r+[()]*30); c40=next(33590+i for i,s in enumerate(st) if s['room6e']==40)
r=r[:c40-33589]; r+=[r[-1],r[-1]]; r+=[()]*(c40+23-33589-len(r))
st=run(fc,r); s=st[-1]; print('c40',c40,'rows to',33589+len(r), RXY(s), 'hp',s['hp65'],'np',s['np64'],'bf',s['bf'], legal_ok(r) or 'ok')
ent=rows_file('work/l62/r40_ent24.txt')
st=run(fc,r+ent+[row('A+Left')]*6+[row('Left')]*40)
print([ (33590+len(r)+i, RXY(x)) for i,x in enumerate(st[len(r):]) ][::6])
wrows(out, r+ent, f'rows from 33590 to room-40 change {c40} + 23, then entry cycle x4')
fc.close()
