import sys; sys.path.insert(0,'.'); sys.path.insert(0,'ng/stages')
from ng.solve import common as C
import a56_common as A
T=A.tas_trace()
p=None
for f in range(6090,9100):
    t=T[f]; k=(t['stage'],t['room'])
    if k!=p: print(f,k,'X',C.abs_x(t),'y',t['y'],'np',t['ninpo']); p=k
