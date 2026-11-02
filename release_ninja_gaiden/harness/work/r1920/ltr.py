"""Trace with lanterns: python work/r1920/ltr.py <mst> <f0> "<spec>" [step]"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/l31t'); sys.path.insert(0,'work/r1920')
import fcka
from ng import fastcore as F
from gbeam import FL, X, row
fl=dict(FL); fl['c0']=0xC0
for i in range(4): fl[f'lx{i}']=0x4D9+i; fl[f'ly{i}']=0x4E1+i; fl[f'ls{i}']=0x4D1+i
def spec(sp):
    out=[]
    for tok in sp.split():
        k,n=tok.split(':') if ':' in tok else (tok,'1'); out+=[row(k)]*int(n)
    return out
rows=spec(sys.argv[3]); stp=int(sys.argv[4]) if len(sys.argv)>4 else 2
fc=F.FastCore(boot_rows=None,ticks=True,fields=fl); fc.put('s',open(sys.argv[1],'rb').read())
st=fc.run_batch('s',[rows],record='all')[0].states; fc.close()
for i,s in enumerate(st):
    if i%stp==0 or i==len(st)-1:
        sc=X(s)-s['x']
        print(int(sys.argv[2])+1+i,'+'.join(rows[i]) or '-','X',X(s),'y',s['y'],'an',s['anim'],'hp',s['hp'],'np',s['np'],'c5',s['c5'],'lan',[(s[f'lx{j}']+sc,s[f'ly{j}'],s[f'ls{j}']) for j in range(4) if (s['c0']>>j)&1], ' '.join(f"t{s['t%d'%j]}@{s['ex%d'%j]+sc}/{s['ey%d'%j]}" for j in range(8) if (s['en']>>j)&1))
