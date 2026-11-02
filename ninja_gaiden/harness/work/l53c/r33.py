"""l53c: room 33 + trigger. From TAS 28843 (room 32 -> 33 change at 28844): blank until row S, then Right; report the
first Right row that moves Ryu, the trigger frame ($5C 2->4), hp refill, room-34 load, and $62/$63 at the trigger."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
for S in (28862, 28864, 28866, 28867, 28868):
    rows = [()] * (S - 28844) + [('Right',)] * (29110 - S + 1)
    st = fc.run_batch('b', [rows], record='all')[0].states
    mv = trig = None
    for i, s in enumerate(st):
        f = 28844 + i
        if mv is None and i and RXY(s)[0] != RXY(st[i-1])[0]: mv = f
        if trig is None and i and s['e5c'] == 4 and st[i-1]['e5c'] != 4: trig = f; tr_s = s
    print('Right from', S, 'first move', mv, 'trigger', trig, 'X', RXY(tr_s), 't62', tr_s['t62'], 't63', tr_s['t63'], 'TAS trigger 29100')
fc.close()
