import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l61p/r37_top_32763.txt')
tl0=legalize_tas(32704,33170,pre[-150:])
fc=base(32595,pokes={0xC9:133,0x64:20})
for d in range(-2,8):
  for v in ['B+Left','B']:
    t=list(tl0); t[50]=row('Left'); t[51]=row('Left'); t[50+d]=row(v); t[51+d]=row(v)
    st=run(fc,pre+t)
    ev=[e for e in events(st,32596) if int(e.split()[0])>=32800][:7]
    print(d, v, legal_ok(pre+t) or 'ok', ev, flush=True)
fc.close()
