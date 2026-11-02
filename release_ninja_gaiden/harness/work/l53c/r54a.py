"""l53c: 5-4 control row on our room-33 line (Right from 28867 -> trigger 29099) vs the TAS (trigger 29100)."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
base = [()] * 23 + [('Right',)] * (29099 - 28867 + 1)          # rows 28844..29099
fc.step(base, record='last'); fc.save('t'); fc._ka_slot = 't'   # after row 29099 (= our trigger frame)
r = fc.ram(); print('after 29099: 5C', r[0x5C], 'X', XY(r), 't62', r[0x62], 't63', r[0x63], 'BF', r[0xBF])
for c in range(29250, 29262):
    rows = [()] * (c - 29100) + [('Left',)] * 4
    st = fc.run_batch('t', [rows], record='all')[0].states
    xs = [RXY(s) for s in st[-6:]]
    print('Left from', c, 'last X:', xs, 'room', st[-1]['room6e'], 'st', st[-1]['st6d'], 'hp', st[-1]['hp65'], 'np', st[-1]['np64'], 'it', st[-1]['item'])
fc.close()
