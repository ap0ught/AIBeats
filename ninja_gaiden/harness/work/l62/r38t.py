import sys; sys.path.insert(0,'work/l62')
from lib62 import *
cyc=[row(x) for x in 'Left A+Left A A+Right A+Right Right'.split()]
fc=base(33190)
for s0 in range(33190,33196):
  for k in (28,29,30,31):
    for tail in ('Left','-','Right'):
        rows=[()]*(s0-33190)+cyc*k+[row(tail)]*60
        lg=legal_ok(rows)
        st=run(fc,rows)
        ch=next((33191+i for i,s in enumerate(st) if s['room6e']==39),None)
        if ch: print(s0+1,k,tail,lg or 'ok',ch, flush=True)
fc.close()
