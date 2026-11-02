"""NesHawk segment check: load NesHawk state <state> (= after stage rows[:n0]), play rows[n0:n1], list DMC conflicts and
the first difference vs Mesen.  python work/l22f/nhseg.py <stage rows> <n0> <state> [--n1 N] [--save name]"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
from ng.emulator import BizHawk
from ng.mode import TICKS
a=sys.argv[1:]
def opt(n,d):
    if n in a:
        i=a.index(n); v=a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
n1=opt('--n1',-1); save=opt('--save','')
rows=C.rows_of(a[0]); n0=int(a[1]); stn=a[2]
if n1<0: n1=len(rows)
e=BizHawk(log_name='l22f_nhseg.log')
try:
    e.tick(TICKS)
    st=e.load(stn)
    assert st['frame']==F0+n0, (st['frame'],F0+n0)
    e.trace(True)
    e.run(rows[n0:n1])
    tr=e.last_trace
    if save: e.save(save); print('saved',save)
finally:
    e.close()
m=F.masks_of(rows[n0:n1])
conf=[F0+n0+i+1 for i,(t,mm) in enumerate(zip(tr,m)) if t['pad']!=mm]
print('conflicts',conf)
r=play(rows[:n1],stops=[])
first=None
for i in range(n0,n1):
    s=r.states[i]; t=tr[i-n0]
    if (ax(s),s['y'],s['hp'],s['ninpo'],s['room'])!=(C.abs_x(t),t['y'],t['hp'],t['ninpo'],t['room']):
        first=(F0+i+1,ax(s),s['y'],s['hp'],C.abs_x(t),t['y'],t['hp']); break
print('first diff',first)
t=tr[-1]; print('NesHawk end frame',t['frame'],'room',t['room'],'X',C.abs_x(t),'y',t['y'],'hp',t['hp'],'np',t['ninpo'])
