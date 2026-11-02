"""NesHawk state on the TAS 4-2 line at TAS frame F (research): python work/l42w/nhtas.py 18596 -> states/l42w_tas18596"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows(); F = int(sys.argv[1])
e = C.open_emu('l42w_nhtas.log')
try:
    e.tick(TICKS); st = e.load('ref4751/09_4-2_control'); f0 = st['frame']
    e.run(TR[f0:F]); s = e.state(); print('frame', s['frame'], 'x', s['x'], 'y', s['y'], 'hp', s['hp'])
    e.save(f'l42w_tas{F}')
finally:
    e.close()
