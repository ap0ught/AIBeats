def cands():
    out=[]
    for d in range(8,12):
        for r in range(70,92):
            for k in ['none','kick']:
                for g in ([0] if k=='none' else [0,1,2,3,4,6]):
                    w=[('Down',)]*d+[('Right',)]*r
                    if k=='kick': w+=[('Right',)]*g+[('A','Left')]*2
                    w=(w+[('Left',)]*220)[:260]
                    out.append(((d,r,k,g),w))
    return out
def goal(st,i): return st[i]['room']==7 and st[i]['y']==192 and st[i]['x']+st[i].get('scroll',0)*0==st[i]['x'] and __import__('ng.solve.common',fromlist=['abs_x']).abs_x(st[i])<=820
