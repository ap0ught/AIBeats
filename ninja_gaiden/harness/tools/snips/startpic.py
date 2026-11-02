import sys; sys.path.insert(0,'.')
from ng.inputs import read_inputs
from ng.mode import TICKS
rows=read_inputs('logs/intro_fastest.inputs.txt')
e.tick(TICKS)
e.run(rows[:165])
for f in range(14):
    r = ('Right',) if f >= 9 else ()
    s=e.step(r,1)
    oam=e.oam()
    spr=[(oam[i+3],oam[i],oam[i+1]) for i in range(4,256,4) if oam[i]<0xEF]
    shot(f'clock/start_{s.frame}')
    print(s.frame, '+'.join(r) or '.', 'gm',s.gm,'ctl',hex(s.ctl),'t',s.timer,s.subtimer,'x',s.x,'y',s.y,'oam visible',len(spr), spr[:4])
