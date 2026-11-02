"""room-41 wait grid (Mesen, real 6-3 arrival): Right on 35,799 (control row), then w rows of filler, then pre63 rows 2.. ; room 43 frame, hp."""
import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l63p/pre63_35212.txt')
fc=base(mst='states/mesen/l63_35798.mst')
for fill in ('-','Left'):
  out=[]
  for w in range(0,61):
    rows=pre[:2]+[row(fill)]*w+pre[2:]+[()]*30
    if legal_ok(rows): out.append((w,'illegal')); continue
    st=run(fc,rows)
    c42=next((35799+i for i,s in enumerate(st) if s['room6e']==42),None)
    c43=next((35799+i for i,s in enumerate(st) if s['room6e']==43),None)
    hp=[s['hp65'] for s in st]
    out.append((w,c42,c43,min(hp[:len(pre)+w])))
  print(fill, out, flush=True)
fc.close()
