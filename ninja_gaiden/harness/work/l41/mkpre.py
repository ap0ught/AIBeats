"""NesHawk: states/lock_41_pre (frame 14,865) from l32_a_cB_end + p4t stage rows minus the last; history file."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
P = C.rows_of('logs/l33_p4t_poweron.inputs.txt')
print(len(P), P[-3:])
e = C.open_emu('l41_mk.log')
try:
    e.tick(TICKS)
    st = e.load('l32_a_cB_end'); f0 = st['frame']; print('f0', f0)
    e.run(P[f0:14865])
    s = e.state(); print(s)
    e.save('lock_41_pre')
    e.run([('Right',)])
    s = e.state(); print(s)
    e.save('lock_41_ctlR')
finally:
    e.close()
C.write_inputs(C.LOGS.parent / 'work/l41/h14865.inputs.txt', P[:14865], 'p4t power-on rows 1-14,865 (4-1 control row 14,866 excluded)')
