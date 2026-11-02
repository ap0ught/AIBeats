import sys; sys.path.insert(0,'.')
from ng.mode import TICKS
e.tick(TICKS); e.trace(True)
e.run([()]*2400); tr=e.last_trace
for s in tr:
    if s.title or s.act1 or s.csdone or s.csskip: print(s.frame, s.title, s.act1, s.csdone, s.csskip, s.cs)
print('cs frames', sum(1 for s in tr if s.cs))
