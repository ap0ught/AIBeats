from ng.solve import common as C
R=('Right',); L=('Left',); D=('Down',); AL=('A','Left'); AR=('A','Right'); DR=('Down','Right')
def cands():
    out=[]
    p=[R,DR]+[D]*9
    for r in range(70,79):
        for j in range(20,47):
            if j>r-6: continue
            for h in (2,3):
                for tail in ('L','AL'):
                    t=[L]*160 if tail=='L' else [AL]*2+[L]*160
                    w=p+[R]*j+[AR]*h+[R]*(r-j-h)+t
                    out.append((('j',r,j,h,tail),w[:198]))
    return out
def goal(st,i): return st[i]['room']==7 and C.abs_x(st[i])<=828 and st[i]['y']>=185
