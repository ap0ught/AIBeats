from ng.solve import common as C
def cands():
    out=[]
    for j in range(8,32):
        for a in range(2,26):
            for b in range(4,22,1):
                w=[('Left',)]*j+[('A','Left')]*2+[('Left',)]*a+[('A','Right')]*2+[('Right',)]*b+[('A','Left')]*2
                w=(w+[('Left',)]*100)[:100]
                out.append(((j,a,b),w))
    return out
def goal(st,i): return st[i]['room']==7 and C.abs_x(st[i])<=782 and st[i]['y']<=128 and (st[i]['coll']&16)
