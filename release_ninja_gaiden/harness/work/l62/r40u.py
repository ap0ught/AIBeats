import sys; sys.path.insert(0,'work/l62')
from lib62 import *
fc=base(33735,pokes={0xC9:133,0x64:20})
for pre in ([], [row('Right')]*3, [row('A+Right')]*2+[row('Right')]*10):
  for hold in ('Up','Up+Right'):
    rows=pre+[row(hold)]*120
    st=run(fc,rows)
    print(len(pre),hold,[(33736+i,RXY(s),s['anim']) for i,s in enumerate(st)][::10])
fc.close()
