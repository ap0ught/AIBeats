"""l53c: 5-4 control row on our room-33 line (Right from 28867, trigger 29099, Start at trigger+5)."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
L, R, S = ('Left',), ('Right',), ('Start',)
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
base = [()] * 23 + [R] * (29099 - 28867 + 1) + [()] * 4 + [S, S]          # rows 28844..29105
fc.step(base, record='last'); fc.save('r'); fc._ka_slot = 'r'                  # after 29105
st = fc.run_batch('r', [[L] * 200], record='all')[0].states
x0 = RXY(st[0])
for i, s in enumerate(st):
    if i and RXY(st[i-1])[0] == 176 and RXY(s)[0] != 176:
        print('first move with Left held from 29106: row', 29106 + i, RXY(st[i-1]), '->', RXY(s)); break
fc.close()
