def cands():
    out=[]
    for a in range(12,18):
        for mode in ['-','R','B','LB','RB']:
            for b in range(0,12,2):
                for c in range(2,8,2):
                    w=[('Left',)]*a
                    if mode=='-': w+=[()]*b
                    elif mode=='R': w+=[('Right',)]*b
                    elif mode=='B': w+=[()]*b+[('B',)]*2
                    elif mode=='LB': w+=[('Left',)]*b+[('B','Left')]*2
                    elif mode=='RB': w+=[('Right',)]*b+[('B','Right')]*2
                    w+=[()]*c+[('Right',)]*0
                    w=(w+[()]*100)[:100]
                    out.append(((a,mode,b,c),w))
    return out
def goal(st,i): return st[i]['room']==7
def ok(st,i):
    j=min(len(st)-1,i+26); return st[j]['item']!=0 and st[j]['lives']==st[0]['lives'] and len(st)>i+26
