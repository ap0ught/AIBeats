"""python work/l22a/strip.py <rows> "a-b,c-d" ...: strip B from row ranges, compare with base (pos diff, end np/hp)"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
base=[tuple(r) for r in C.rows_of(sys.argv[1])]
rb=play(base,stops=[]).states
for spec in sys.argv[2:]:
    rows=list(base)
    for rg in spec.split(','):
        a,b=(rg.split('-')+[rg])[:2]
        for i in range(int(a),int(b)+1): rows[i-1]=tuple(x for x in rows[i-1] if x!='B')
    rs=play(rows,stops=[]).states
    fd=None
    for i in range(min(len(rs),len(rb))):
        if (rs[i]['room'],ax(rs[i]),rs[i]['y'],rs[i]['hp'])!=(rb[i]['room'],ax(rb[i]),rb[i]['y'],rb[i]['hp']): fd=i+1; break
    s=rs[-1]
    ev=[(i+1,rs[i]['ninpo']) for i in range(1,len(rs)) if rs[i]['ninpo']!=rs[i-1]['ninpo']]
    print(spec,'firstdiff',fd, (fd and (ax(rb[fd-1]),rb[fd-1]['y'],rb[fd-1]['hp'],'->',ax(rs[fd-1]),rs[fd-1]['y'],rs[fd-1]['hp'])),'end room',s['room'],'X',ax(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo'],'item',s['item'],'np events',ev[-8:])
