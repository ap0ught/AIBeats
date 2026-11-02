from ng.solve import common as C
R=('Right',); L=('Left',); D=('Down',); AL=('A','Left'); AR=('A','Right'); DR=('Down','Right')
def cands():
    out=[]
    pres={'R1D10':[R]+[D]*10,'D11':[D]*11,'DR1D10':[DR]+[D]*10,'R1D9':[R]+[D]*9,'R2D9':[R]*2+[D]*9}
    for pn,p in pres.items():
        for r in range(60,95):
            w=p+[R]*r+[L]*160
            out.append(((pn,'run',r),w[:240]))
            for k in (2,3):
                w=p+[R]*r+[AL]*k+[L]*160
                out.append(((pn,'kick',r,k),w[:240]))
            for j in range(40,r-4,3):
                w=p+[R]*j+[AR]*2+[R]*(r-j-2)+[L]*160
                out.append(((pn,'jump',r,j),w[:240]))
    return out
def goal(st,i): return st[i]['room']==7 and C.abs_x(st[i])<=828 and st[i]['y']>=185
