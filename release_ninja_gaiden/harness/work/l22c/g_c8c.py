from ng.solve import common as C
R=('Right',); RU=('Right','Up'); ALU=('A','Left','Up'); AL=('A','Left'); L=('Left',); AR=('A','Right')
CYC=[R,RU,RU,ALU,AL]
def cands():
    out=[]
    for pre in [0,1,2,3]:
        for n in range(5,10):
            base=[()]*pre+[R]+CYC*n
            for k in range(0,4):
                w=base+[RU]*k+[ALU,AL,AL]+[R]*120
                out.append((('A',pre,n,k),w[:150]))
                w=base+[RU]*k+[ALU,AL]+[R]*120
                out.append((('A1',pre,n,k),w[:150]))
            for g in range(6,16):
                for h in [2,3]:
                    w=base[:-2]+[ALU,AL]+[L]*g+[AR]*h+[R]*120
                    out.append((('B',pre,n,g,h),w[:150]))
    return out
def goal(st,i): return st[i]['room']==8 and C.abs_x(st[i])>=1926
