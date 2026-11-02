from ng.solve import common as C
R=('Right',); RU=('Right','Up'); ALU=('A','Left','Up'); AL=('A','Left'); L=('Left',); AR=('A','Right'); U=('Up',)
CYC=[R,RU,RU,ALU,AL]
def chims():
    base=lambda n:[R]+CYC*n
    return {'A073':(base(7)+[RU]*3+[ALU,AL,AL],63),
            'B06122':(base(6)[:-2]+[ALU,AL]+[L]*12+[AR]*2,61),
            'A1080':(base(8)+[ALU,RU],62),
            'A081':(base(8)+[RU,U,AL,AL],60),
            'A173':([()]+base(7)+[RU]*3+[ALU,AL,AL],63)}
def cands():
    out=[]
    for nm,(ch,r0) in chims().items():
        for r in range(r0-2,r0+4):
            for k in range(0,3):
                for m in range(29,37):
                    w=ch+[R]*r+[L]*k+[AL]*2+[L]*m+[AL]*2+[L]*60
                    out.append(((nm,r,k,m),w[:215]))
    return out
def goal(st,i): return st[i]['room']==8 and st[i]['y']==96 and (st[i]['coll']&16)
