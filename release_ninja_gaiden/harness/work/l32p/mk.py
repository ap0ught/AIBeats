import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
fc = core('states/mesen/l31_ctl.mst')
rows = C.rows_of('logs/l31_tas_c1b.inputs.txt'); print('stage rows', len(rows))
fc.step(rows, record='last'); r = fc.ram()
fc.save('s'); fc.save_file('s', MST, frame=9993 + len(rows)); fc.close()
X = r[0x52]*256 + r[0x51] + r[0x86]
print('frame', 9993 + len(rows), 'X', X, 'x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], '62', r[0x62], '63', r[0x63], 'stage', r[0x6D])
