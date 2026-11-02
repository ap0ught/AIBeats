"""make the room-32 start .mst (TAS state after row 28652 = room-32 control - 1) and the legal history file."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core_at(28652); fc.save('s'); fc.save_file('s', 'states/mesen/l53c_tas28652.mst', 28652)
r = fc.ram(); print('X,y', XY(r), 'room', r[0x6E], 'BF', r[0xBF])
h = legalize_tas(28652 - 300, 28652)
open('work/l53c/hist_tas28652.txt', 'w').write('\n'.join(P(x) for x in h) + '\n')
fc.close()
