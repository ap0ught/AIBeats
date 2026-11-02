"""python work/l22a/ramdiff.py <rows A> <rows B> <editsB|-> <n>: RAM diff after n rows"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
def load(f,ed=None):
    rows=[tuple(r) for r in C.rows_of(f)]
    if ed and ed!='-':
        for e in ed.split(','):
            k,v=e.split('='); a,b=(k.split('-')+[k])[:2]
            for i in range(int(a),int(b)+1): rows[i-1]=row(v)
    return rows
n=int(sys.argv[4])
A=load(sys.argv[1])[:n]; B=load(sys.argv[2],sys.argv[3])[:n]
fc=core(); r1=fc.run_batch('s',[A],record='last',record_ram=True); r2=fc.run_batch('s',[B],record='last',record_ram=True); fc.close()
a,b=r1[0].ram,r2[0].ram
d=[(i,a[i],b[i]) for i in range(len(a)) if a[i]!=b[i] and not 0x200<=i<0x300 and not 0x100<=i<0x200]
print(len(d),'diffs:',' '.join(f'{i:03X}:{x}/{y}' for i,x,y in d[:80]))
