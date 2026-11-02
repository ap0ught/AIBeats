import itertools
def cands():
    out=[]
    for u in [1,2,3]:
        for k in range(0,16):
            for bl in [('B','Left'),('B',)]:
                for k2 in [0,5,10]:
                    w=[('Up',)]*u+[('A','Left')]*2+[('Left',)]*k+[bl]*2+[('Left',)]*k2+[('B','Left')]*2
                    w=(w+[('Left',)]*120)[:120]
                    out.append(((u,k,bl,k2),w))
    return out
from ng.solve import common as C
def goal(st,i): return st[i]['room']==7 and C.abs_x(st[i])<=800
