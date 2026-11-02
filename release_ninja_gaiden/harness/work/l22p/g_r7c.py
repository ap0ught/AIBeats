from ng.solve import common as C
P=[('Down',)]*8+[('Right',)]*74+[('Left',)]*120
def cands():
    out=[]
    for j in range(0,30,1):
        for a in range(4,16,1):
            for b in range(2,14,2):
                for c in [0,4,8]:
                    w=P+[('Left',)]*j+[('A','Left')]*2+[('Left',)]*a+[('A','Right')]*2+[('Right',)]*b+[('A','Left')]*2+[('Left',)]*c+[('A','Right')]*2+[('Right',)]*b+[('A','Left')]*2
                    w=(w+[('Left',)]*120)[:len(P)+120]
                    out.append(((j,a,b,c),w))
    return out
def goal(st,i): return st[i]['room']==7 and C.abs_x(st[i])<=782 and st[i]['y']<=128 and (st[i]['coll']&16)
