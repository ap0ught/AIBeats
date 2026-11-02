from ng.solve import common as C
def cands():
    out=[]
    for d in range(7,13):
        for r in range(68,84):
            w=[('Down',)]*d+[('Right',)]*r
            w=(w+[('Left',)]*220)[:230]
            out.append(((d,r),w))
    return out
def goal(st,i): return st[i]['room']==7 and st[i]['y']==192 and C.abs_x(st[i])<=828
