"""l53c: room-31 arrival state from a power-on rows file + a Mesen state: python work/l53c/mkarr.py poweron.txt start.mst F_start F_end out.mst"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
from ng.inputs import read_inputs
rows = read_inputs(sys.argv[1]); mst = sys.argv[2]; f0 = int(sys.argv[3]); f1 = int(sys.argv[4]); out = sys.argv[5]
fc = core(mst)
seg = list(rows[f0:f1]); seg += [()] * (f1 - f0 - len(seg))
_, recs, _ = fc.step(seg, record="all")
r = fc.ram(); fc.save('s'); fc.save_file('s', out, f1)
print('after row', f1, 'room', r[0x6E], 'X,y', XY(r), 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], '$62', r[0x62], '$63', r[0x63])
ch = [f0 + 1 + i for i in range(1, len(recs)) if recs[i]['room6e'] != recs[i-1]['room6e']]
print('room changes', ch)
fc.close()
