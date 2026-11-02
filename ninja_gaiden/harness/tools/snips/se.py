import sys; sys.path.insert(0,'.')
from ng.mode import TICKS, mode
e.tick(TICKS); e.trace(True)
e.poke(0xBE, 0x80)
e.run([()]*1500); tr=e.last_trace
prev=None
for s in tr:
    m=mode(s)
    if m!=prev: print(s.frame, m, 'stage',s.stage,'room',s.room, s.lagged, {k:s[k] for k in TICKS}); prev=m
    if s.frame%30==0: shot(f'se/{s.frame:05d}')
