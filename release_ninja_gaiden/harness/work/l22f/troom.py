"""python work/l22f/troom.py <stage rows> <n> "<grammar>" room [show a b] : first frame of room"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of(sys.argv[1])[:int(sys.argv[2])]; w=[]
for sg in sys.argv[3].split(';'):
    r,k=sg.rsplit('*',1); w+=[row(r)]*int(k)
new=list(rows)+legal_after(rows,w); R=int(sys.argv[4])
r=play(new, stops=[(0x6D,'changed',0)])
for i,s in enumerate(r.states):
    if s['room']==R: print('room',R,'at frame',F0+i+1,'row',i+1,'X',ax(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo']); break
else: s=r.states[-1]; print('not reached; end X',ax(s),'y',s['y'])
if len(sys.argv)>6:
    for f in range(int(sys.argv[5]),int(sys.argv[6])):
        s=r.states[f-F0-1]; print(f,ax(s),s['y'],s['coll'],s['anim'],'+'.join(new[f-F0-1]))
