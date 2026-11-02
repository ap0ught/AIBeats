import sys
sys.path.insert(0,'.'); sys.path.insert(0,'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
d=open('work/l42p/tas42_ram.bin','rb').read(); f0=int.from_bytes(d[:4],'little'); d=d[4:]
pads=bytes(d[i*2048+0x2A] for i in range(len(d)//2048))
R2D=C.rows_of('logs/a34/4-2_r2d.inputs.txt')
FL={'x':0x86,'sl':0x51,'sh':0x52,'y':0x8A,'hp':0x65,'anim':0x80,'en':0x73}
fc=F.FastCore(boot_rows=None,ticks=True,fields=FL)
fc.put('s',open('states/mesen/l42p_tas16682.mst','rb').read()); fc._ka_slot='s'; fc.load('s')
S=17030
fc.step(pads[:S-16682],record='last'); fc.save('s0'); fc._ka_slot='s0'
def show(tag, rows):
    st=fc.run_batch('s0',[rows],record='all')[0].states
    print(tag, [(S+1+i, s['sh']*256+s['sl']+s['x'], s['y'], s['anim']) for i,s in enumerate(st)][::2])
show('r2d', R2D[S-16682+1:S-16682+16])
show('pads', pads[S-16682:S-16682+15])
show('right', [('Right',)]*15)
show('B31', [('Right','B')]*2+[('Right',)]*13)
show('B32', [('Right',),('Right','B'),('Right','B')]+[('Right',)]*12)
fc.close()
