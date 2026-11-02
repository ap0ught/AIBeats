import sys; sys.path.insert(0,'ng/stages'); sys.path.insert(0,'.')
import a56_common as C
from ng.inputs import read_inputs
from ng.mode import TICKS
start, f, name = sys.argv[1], sys.argv[2], sys.argv[3]
extra = [tuple(x.split('+')) if x else () for x in (sys.argv[4].split(',') if len(sys.argv)>4 else [])]
rows=[tuple(r) for r in read_inputs(f)]
e=C.open_emu('a12r2_shot.log')
try:
    e.tick(TICKS); e.load(start); st=e.run(rows); print('end',st['frame'],C.abs_x(st),st['x'],st['y'])
    e.screenshot(name+'_0')
    for i,r in enumerate(extra):
        st=e.step(r,8); print(i,r,st['frame'],C.abs_x(st),st['y'])
        e.screenshot(f'{name}_{i+1}')
finally: e.close()
