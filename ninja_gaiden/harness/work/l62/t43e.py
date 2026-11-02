import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l62/pre43_37090.txt')
fc=base(mst='states/mesen/l63_35798.mst')
fc.load('b'); fc.step(pre, record='last'); fc.save('p'); fc._ka_slot='p'
for mid2 in ('Left','-'):
  rows=[row('A+Left')]*2+[row('-')]*16+[row(mid2)]*80
  st=fc.run_batch('p',[rows],record='all')[0].states
  print(mid2, [(37091+i,RXY(s),s['hp65']) for i,s in enumerate(st)][::3])
fc.close()
