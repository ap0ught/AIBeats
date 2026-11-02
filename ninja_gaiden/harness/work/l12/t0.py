import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/l12')
from lib import *
rows = C.rows_of('logs/tk_1-2_s11.inputs.txt')[:100]
P = pool(1)
r = run(P, [rows])[0]
print(kill(r))
for i,s in enumerate(r.states[:95]):
    if i>=66: print(i+1, s['x'], s['y'], s['anim'], s['bosshp'])
P.close()
