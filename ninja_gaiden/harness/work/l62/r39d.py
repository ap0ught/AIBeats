import sys; sys.path.insert(0,'work/l62')
from lib62 import *
cyc=[row(x) for x in 'Right A+Right A+Right A+Right A+Left Left'.split()]
fc=base(33290,pokes={0xC9:133,0x64:10})
ent=cyc*5+[row('Right')]*80
lag=23
pre=ent[:61+lag]; tl=legalize_tas(33352,33712,pre[-150:]); rows=pre+tl
st=run(fc,rows)
for e in events(st,33291): print(e)
for f in range(33425,33442,2):
    s=st[f-33291]; scr=s['scr_hi']*256+s['scr_lo']
    m=TM(f-lag); tscr=m[0x52]*256+m[0x51]
    print(f, RXY(s), [(j,s[f't{j}'],scr+s[f'ex{j}'],s[f'ey{j}']) for j in range(8) if s['eact']>>j&1], '| TAS', XY(m), [(j,m[0x400+j],tscr+m[0x460+j],m[0x480+j]) for j in range(8) if m[0x73]>>j&1])
fc.close()
