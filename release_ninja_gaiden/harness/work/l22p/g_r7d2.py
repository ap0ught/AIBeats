from ng.solve import common as C
def cands():
    out=[]
    for j in range(16,36):
        for a in range(4,15):
            for b in range(8,17):
                w=[('Left',)]*j+[('A','Left')]*2+[('Left',)]*a+[('A','Right')]*2+[('Right',)]*b+[('A','Left')]*2
                w=(w+[('Left',)]*90)[:90]
                out.append(((j,a,b),w))
    return out
def goal(st,i): return st[i]['room']==7 and C.abs_x(st[i])<=782 and st[i]['y']<=128 and (st[i]['coll']&16)
