"""Save a Mesen state + power-on history after the first n 4-3 stage rows (stage rows start at the control row 19,297).
python work/r1920/mkst.py <stage rows> <n> <name>  -> states/mesen/<name>.mst (frame 19,296 + n), work/r1920/h_<name>.inputs.txt"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/r1920')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from gbeam import FL, X
import os
CHAIN = 'logs/l42_w_k932b_poweron.inputs.txt'; CTL = int(os.environ.get('CTL', '19296')); BASE = os.environ.get('BASE', 'states/mesen/l43_k932b19295.mst')
rows = [tuple(r) for r in C.rows_of(sys.argv[1])][:int(sys.argv[2])]
name = sys.argv[3]
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(BASE, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
fc.step(rows, record='last'); fc.save('z')
r = fc.ram()
f = CTL - 1 + len(rows)
fc.save_file('z', f'states/mesen/{name}.mst', frame=f)
hist = [tuple(x) for x in C.rows_of(CHAIN)][:CTL - 1] + rows
C.write_inputs(f'work/r1920/h_{name}.inputs.txt', hist, f'power-on rows 1..{f}: k932b 1..19296 + {sys.argv[1]}[:{len(rows)}]')
sh = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]
print(name, 'frame', f, 'room', r[0x6E], 'X', sh * 256 + r[0x51] + r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'BF', r[0xBF])
fc.close()
