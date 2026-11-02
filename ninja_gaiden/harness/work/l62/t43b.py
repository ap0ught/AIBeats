import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l62/pre43_37090.txt')
fc=base(mst='states/mesen/l63_35798.mst')
st=run(fc,pre+[row('Left')]*50)
for i in range(len(pre)-10,len(st),3):
    s=st[i]; scr=s['scr_hi']*256+s['scr_lo']
    print(35799+i, RXY(s), s['hp65'], [(j,s[f't{j}'],scr+s[f'ex{j}'],s[f'ey{j}']) for j in range(8) if s['eact']>>j&1])
fc.close()
