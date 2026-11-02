import sys
sys.path.insert(0,'work/l21f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of('work/l21f/v3_rows.txt')
base=play(rows,stops=[])
def summ(r):
    st=r.states
    out={}
    for f in (4402,4480,5096,5221):
        s=st[f-F0-1]; out[f]=(ax(s),s['y'],s['hp'],s['ninpo'],s['room'])
    gm=[F0+i+1 for i,s in enumerate(st) if s['gm']==0 and s['room']==5 and i>2400]
    return out, (gm[0] if gm else None)
print('base',summ(base))
for i in range(int(sys.argv[1]),int(sys.argv[2])):
    for w in (('B','Right','Up'),('B','Up')):
        want=list(rows); want[i]=w; want[i+1]=tuple(sorted(set(w)|{'Right'})) if len(sys.argv)>3 else want[i+1]
        new=list(rows[:i])+legal_after(rows[:i],want[i:])
        if new[i]!=tuple(sorted(w)): continue
        r=play(new,stops=[])
        o,g=summ(r)
        print(i,F0+i+1,'+'.join(w),o[4402],o[4480],o[5221],'gm0',g, flush=True)
