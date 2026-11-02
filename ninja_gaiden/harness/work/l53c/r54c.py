import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
base = [()] * 23 + [('Right',)] * (29099 - 28867 + 1)
fc.step(base, record='last')
for k in range(12):
    fc.step([()], record='last'); r = fc.ram(); t = TM(29100 + k)
    d = [(hex(i), r[i], t[i]) for i in range(0x800) if r[i] != t[i] and not (0x100 <= i < 0x200)]
    print(29100 + k, 'BF', r[0xBF], len(d), d[:40])
fc.close()
