import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l61p/r37_top_32763.txt')
tl=legalize_tas(32704,33170,pre[-150:])
fc=base(32595,pokes={0xC9:133,0x64:20})
st=run(fc,pre+tl)
for e in events(st,32596): print(e)
for f in range(32815,32830):
    s=st[f-32596]
    print(f, RXY(s), 'hp',s['hp65'], 'act', bin(s['eact']), [(j,s[f't{j}'],s[f'ex{j}'],s[f'ey{j}']) for j in range(8) if s['eact']>>j&1], s['anim'], s['rflags'])
fc.close()
