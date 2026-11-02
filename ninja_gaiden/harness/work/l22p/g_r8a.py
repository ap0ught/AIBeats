R=('Right',); RU=('Right','Up'); ALU=('A','Left','Up'); AL=('A','Left'); L=('Left',); AR=('A','Right')
CYC=[R,RU,RU,ALU,AL]
def cands():
    out=[]
    for pre in [0,1,2]:
        for n in range(4,10):
            base=[()]*pre+[R]+CYC*n
            # A: last grab kick + drift right
            for k in range(0,4):
                w=base+[RU]*k+[ALU,AL,AL]+[R]*120
                out.append((('A',pre,n,k),w[:160]))
            # B: kick to left wall, A+R kick at contact
            for g in range(6,20):
                for h in [2,3]:
                    w=base[:-2]+[ALU,AL]+[L]*g+[AR]*h+[R]*120
                    out.append((('B',pre,n,g,h),w[:160]))
    return out
def goal(st,i): return st[i]['room']==8 and st[i]['x']>=127
