"""python -u work/w21/try.py <mst> "<spec>" [--every 1] [--raw]   spec tokens 'RA:3 -:4 L:2'; legalized on a blank history unless --raw"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C, legality as L
from ng import fastcore as F
MAP={'R':'Right','L':'Left','U':'Up','D':'Down','A':'A','B':'B'}
ab={'Right':'R','Left':'L','Up':'U','Down':'D','A':'A','B':'B'}
def spec_rows(spec):
    out=[]
    for tok in spec.split():
        k,n=tok.split(':') if ':' in tok else (tok,'1')
        out+=[tuple(sorted(MAP[c] for c in k if c!='-'))]*int(n)
    return out
def legal(rows,hist=None):
    en=L.Enforcer(list(hist or [()]*60)[-1900:]); return [tuple(sorted(en.emit(w))) for w in rows]
if __name__=='__main__':
    a=sys.argv[1:]; raw='--raw' in a
    a=[x for x in a if x!='--raw']
    rows=spec_rows(a[1]); rows=rows if raw else legal(rows)
    fc=F.FastCore(boot_rows=None); fc.put('s',open(a[0],'rb').read()); fc.load('s')
    _,recs,_=fc.step(rows,record='all'); fc.close()
    for i,(s,r) in enumerate(zip(recs,rows)):
        print(i+1,''.join(ab[b] for b in r) or '-','r%d'%s['room'],'X',C.abs_x(s),'x',s['x'],s['xsub'],'y',s['y'],'vy',s['vy'],'coll',s['coll'],'anim',s['anim'],'rf',s['rflags'],'hp',s['hp'])
