from ng.solve import common as C
R=('Right',); L=('Left',); AL=('A','Left'); N=()
def cands():
    out=[]
    for r in range(8,26):
        for k in range(0,4):
            for m in range(20,40):
                w=[R]*r+[L]*k+[AL]*2+[L]*m+[AL]*2+[L]*60
                out.append(((r,k,m),w[:150]))
    return out
def goal(st,i): return st[i]['room']==8 and st[i]['y']==96 and (st[i]['coll']&16)
