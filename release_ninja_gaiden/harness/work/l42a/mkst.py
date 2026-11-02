"""4-2 lock start states (agent l42a). NesHawk: lock_42_pre (16,997), lock_42_ctl (blank control row 16,998 = locked file),
lock_42_ctlR (Right on 16,998). Mesen: states/mesen/lock_42_pre.mst / lock_42_ctl.mst / lock_42_ctlR.mst
(from l41q_ctl.mst + r15_c stage rows), RAM compared with NesHawk."""
import sys, shutil
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
import fcka
from ng.solve import common as C
from ng import fastcore as F
from ng.mode import TICKS
P = C.rows_of('logs/l41_r15_c_poweron.inputs.txt'); S = C.rows_of('logs/l41_r15_c16844.inputs.txt')
assert len(P) == 16998 and list(P[14847:]) == list(S), (len(P), len(S))
C.write_inputs('work/l42a/h16997.inputs.txt', P[:16997], 'r15_c power-on rows 1-16,997 (4-2 control row 16,998 excluded)')
e = C.open_emu('l42a_mkst.log')
nh = {}
try:
    e.tick(TICKS); st = e.load('lock_41q_pre'); f0 = st['frame']; assert f0 == 14847
    e.run(S[:16997 - f0]); s = e.state(); print('pre', s); e.save('lock_42_pre')
    e.run([()]); s = e.state(); print('ctl', s); e.save('lock_42_ctl')
    e.load('lock_42_pre'); e.run([('Right',)]); s = e.state(); print('ctlR', s); e.save('lock_42_ctlR')
finally:
    e.close()
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41q_ctl.mst', 'rb').read()); fc.load('s')
fc.step(S[1:16997 - 14847], record='last'); fc.save('p'); fc.save_file('p', 'states/mesen/lock_42_pre.mst', frame=16997)
fc.step([()], record='last'); r = fc.ram(); fc.save('c'); fc.save_file('c', 'states/mesen/lock_42_ctl.mst', frame=16998)
print('mesen ctl x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'it', r[0xC9], 'BF', r[0xBF], '62', r[0x62], 'stage', r[0x6D], 'room', r[0x6E])
fc.load('p'); fc.step([('Right',)], record='last'); r = fc.ram(); fc.save('d'); fc.save_file('d', 'states/mesen/lock_42_ctlR.mst', frame=16998)
print('mesen ctlR x', r[0x86], r[0x85], 'y', r[0x8A], 'BF', r[0xBF], '62', r[0x62])
fc.close()
