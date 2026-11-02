import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
for name, base in (('ours', [()] * 23 + [('Right',)] * (29099 - 28867 + 1) + [()] * 30),
                   ('tas', [TM(g)[0x2A] for g in range(28844, 29130)]),
                   ('ours+R', [()] * 23 + [('Right',)] * (29130 - 28867 + 1))):
    st = fc.run_batch('b', [base], record='all')[0].states
    for i, s in enumerate(st):
        f = 28844 + i
        if 29096 <= f <= 29112 or f == 28844 + len(st) - 1:
            print(name, f, '5C', s['e5c'], 'rm', s['room6e'], 'st', s['st6d'], 'hp', s['hp65'], 'X', RXY(s), 't62', s['t62'])
fc.close()
