"""6-1 control on the chain (rows file from 28418 on the TAS state 28417 + pokes): first row where Left/Right moves Ryu after the 6-1
load, and whether Start presses after the load shorten it."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
rows = [row(l.strip()) for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
fc = core_at(28417); fc.poke(0x64, 20); fc.poke(0x65, 3)
fc.step(rows, record='last'); r = fc.ram(); F = 28417 + len(rows)
print('after row', F, 'stage', r[0x6D], 'room', r[0x6E], XY(r), 'BF', r[0xBF]); fc.save('e'); fc._ka_slot = 'e'
for d in ('Left', 'Right'):
    st = fc.run_batch('e', [[(d,)] * 260], record='all')[0].states
    for i in range(1, len(st)):
        if st[i]['st6d'] == 16 and RXY(st[i]) != RXY(st[i-1]) and abs(RXY(st[i])[0] - RXY(st[i-1])[0]) < 3:
            print(d, 'held: first move on row', F + 1 + i, RXY(st[i-1]), '->', RXY(st[i])); break
for s in range(F + 1, F + 150, 10):
    rr = [()] * (s - F - 1) + [('Start',)] * 2 + [()] * 2 + [('Left',)] * (260 - (s - F + 3))
    st = fc.run_batch('e', [rr], record='all')[0].states
    mv = next((F + 1 + i for i in range(1, len(st)) if RXY(st[i]) != RXY(st[i-1]) and abs(RXY(st[i])[0] - RXY(st[i-1])[0]) < 3), None)
    print('Start at', s, '-> first Left move', mv, 'pause?', st[-1]['st6d'])
fc.close()
