import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
R = ('Right',)
cands = {
 'Rall': [()] * 23 + [R] * (29099 - 28867 + 1),
 'Rto29097': [()] * 23 + [R] * (29097 - 28867 + 1),
 'Rto29096': [()] * 23 + [R] * (29096 - 28867 + 1),
 'Rto29097,-,R': [()] * 23 + [R] * (29097 - 28867 + 1) + [(), R],
 'Rto29096,-,-,R': [()] * 23 + [R] * (29096 - 28867 + 1) + [(), (), R],
 'tas': [TM(g)[0x2A] for g in range(28844, 29100)],
}
for name, rows in cands.items():
    rows = rows + [()] * (29500 - 28843 - len(rows))
    st = fc.run_batch('b', [rows], record='all')[0].states
    trig = ch = None
    for i, s in enumerate(st):
        f = 28844 + i
        if trig is None and s['e5c'] == 4: trig = f; xt = RXY(s)
        if ch is None and s['room6e'] == 34: ch = f
    print(f'{name:16s} trigger {trig} X {xt} room34 {ch}')
fc.close()
