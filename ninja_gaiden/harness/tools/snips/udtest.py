import sys; sys.path.insert(0,'.')
from ng.mode import TICKS
e.cmd("tick gm:%d" % 0xC088)
print('before reset', e.step((),1))
e.cmd("reset")
print('after raw reset (no re-tick)', e.step((),1))
e.load('intro_fastest_end')
for b in (('Up','Down'),('Left','Right'),('Up','Down','Left')):
    s=e.step(b,1); print(b, 'pad', s.pad, s)
