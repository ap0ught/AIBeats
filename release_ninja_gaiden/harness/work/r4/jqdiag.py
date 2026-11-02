import sys, numpy as np
sys.path.insert(0, 'G:/AI World Record/Ninja Gaiden/work/r4')
import jqplan as M, jqplan2 as Q
steps=[('jump', 26, 68.0, 1, ('F', 1, 43)), ('jump', 74, 119.0, -1, ('O', 1, 13)), ('jump', 118, 124.5, -1, ('F', 28, 43))]
# build Ryu path rows 20..161 and fb state
x=59.0; t=20; last=-99; fb=Q.fb_init()[None]
for (_,T,X,F,hold) in steps:
    h=M.HOLDS.index(hold)
    sw,hs,xi,V=Q.sim_jump(T,X,F,h,last,0)
    n=T-t
    pre=np.full(n,x); j=round((X-x)/1.5)
    for k in range(abs(j)): pre[n-abs(j)+k]=x+1.5*np.sign(j)*(k+1)
    RX=np.floor(np.concatenate([pre,xi[:M.NI]]))[None].astype(np.int64)
    RY=np.concatenate([np.full(n,160),M.PJ[:M.NI]]).astype(np.int64)
    SW=np.zeros((1,len(RY)),bool)
    for s in sw: SW[0,s-t]=True
    fb,hurt=Q.sim_rows(fb,t,RX,RY,SW,F)
    print('jump',T,'hits',hs,'hurt',hurt,'land x',xi[M.NI])
    x=float(xi[M.NI]); t=T+M.NI; last=sw[-1] if sw else last
print('node t',t,'x',x,'fb',fb[0][:2])
# now: stand still facing right and see fireball tracks
for wait in (0,):
    RX=np.full((1,90),int(x)); RY=np.full(90,160)
    f=fb.copy()
    for k in range(90):
        f,h=Q.sim_rows(f,t+k,RX[:, :1],RY[:1],np.zeros((1,1),bool),1)
        if k%3==0: print(t+k,'fbR',f[0][0][[0,1,4]],'fbL',f[0][1][[0,1,4]],'hurt' if h[0] else '')
