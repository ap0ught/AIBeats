"""states/mesen/l41_pre.mst (14,865) and l41_ctl.mst (14,866, Right on the control row) from l33_cB_ctl.mst + p4t rows."""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
rows = C.rows_of('logs/l33_p4t.inputs.txt'); print(len(rows), rows[-2:])
fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD); fc.put('s', open('states/mesen/l33_cB_ctl.mst', 'rb').read()); fc.load('s')
fc.step(rows[:-1], record='last'); fc.save('p'); fc.save_file('p', 'states/mesen/l41_pre.mst', frame=14865)
fc.step([('Right',)], record='last'); r = fc.ram(); fc.save('c'); fc.save_file('c', MST, frame=14866); fc.close()
print('x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], '62', r[0x62], 'stage', r[0x6D], 'room', r[0x6E], '73', hex(r[0x73]))
