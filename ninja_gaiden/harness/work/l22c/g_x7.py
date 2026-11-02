L=('Left',); R=('Right',); U=('Up',); RU=('Right','Up'); AL=('A','Left'); ALU=('A','Left','Up')
AV={'A':('A',),'AR':('A','Right'),'AU':('A','Up'),'ARU':('A','Right','Up')}
def cands():
    out=[]
    for a in range(2,5):
        for b in range(16,22):
            for kk in ('AL',):
                K=[AL,AL] if kk=='AL' else [ALU,AL]
                for c in range(0,4):
                    for d in range(0,4):
                        for dv in ('U','RU'):
                            for av in AV:
                                w=[L]*a+[AL]*2+[L]*b+K+[R]*c+[U if dv=='U' else RU]*d+[AV[av]]*2+[R]*12
                                out.append(((a,b,kk,c,d,dv,av),w[:48]))
    return out
def goal(st,i): return st[i]['room']==8
