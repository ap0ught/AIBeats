import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l62/pre_r40_35300.txt')
fc=base(mst='states/mesen/l62_33589.mst')
fc.load('b'); fc.step(pre, record='last'); fc.save('p'); fc._ka_slot='p'
s0=fc.ram(); print('at 35300', XY(s0))
res=[]
for w in range(0,12,1):
  for hold in (2,4,8,16,30):
    for d in ('Right','-'):
      rows=[row('Right')]*w+[row('A+Right' if d=='Right' else 'A')]*hold+[row(d)]*60
      st=fc.run_batch('p',[rows],record='all')[0].states
      ys=[RXY(s)[1] for s in st[w:w+50]]
      i=ys.index(min(ys))
      res.append((min(ys), 35301+w, hold, d, RXY(st[w]), 35301+w+i, st[w+i]['hp65']))
res.sort()
for r in res[:12]: print(r)
print('worst', res[-1])
fc.close()
