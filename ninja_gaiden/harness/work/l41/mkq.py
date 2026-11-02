"""q4 start states: NesHawk lock_41q_pre (14,847) + lock_41q_ctlR (Right on 14,848); history work/l41/hq14847.inputs.txt;
Mesen states/mesen/l41q_pre.mst / l41q_ctl.mst (from l33_cB_ctl.mst + q4 stage rows)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng import fastcore as F
from ng.mode import TICKS
P = C.rows_of('logs/l33_q4_poweron.inputs.txt'); S = C.rows_of('logs/l33_q4.inputs.txt')
print(len(P), P[-2:], len(S))
C.write_inputs('work/l41/hq14847.inputs.txt', P[:14847], 'q4 power-on rows 1-14,847 (4-1 control row 14,848 excluded)')
e = C.open_emu('l41_mkq.log')
try:
    e.tick(TICKS); st = e.load('l32_a_cB_end'); f0 = st['frame']
    e.run(P[f0:14847]); print(e.state()); e.save('lock_41q_pre')
    e.run([('Right',)]); s = e.state(); print(s); e.save('lock_41q_ctlR')
finally:
    e.close()
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l33_cB_ctl.mst', 'rb').read()); fc.load('s')
fc.step(S[:-1], record='last'); fc.save('p'); fc.save_file('p', 'states/mesen/l41q_pre.mst', frame=14847)
fc.step([('Right',)], record='last'); r = fc.ram(); fc.save('c'); fc.save_file('c', 'states/mesen/l41q_ctl.mst', frame=14848); fc.close()
print('mesen x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'BF', r[0xBF], '62', r[0x62], 'stage', r[0x6D], 'room', r[0x6E])
