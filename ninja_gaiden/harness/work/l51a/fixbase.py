"""Make a Mesen base at 23,100 that is RAM-equal to NesHawk (the tosser-1 transient leaves $47D etc. different).
Writes states/mesen/l51a_p23100N.mst. Then checks w2a rows to 23,588 (full RAM, no stack) on both."""
import sys; sys.path.insert(0, 'work/l51a')
from lib import *
from ng.mode import TICKS
p = rows_file('work/l51a/p23100.txt'); w = rows_file('work/l51a/hc_w2a.txt')
e = C.open_emu('l51a_fixbase.log')
try:
    e.tick(TICKS); e.load('lock_51_pre'); e.run(p); n1 = e.ram_all()
    e.run(w[len(p):]); n2 = e.ram_all()
finally:
    e.close()
fc = core(); fc.step(p, record='last'); m1 = fc.ram()
d = [a for a in range(0x800) if m1[a] != n1[a] and not (0x100 <= a < 0x200)]
print('diff @23100', [(hex(a), m1[a], n1[a]) for a in d])
for a in d: fc.poke(a, n1[a])
fc.save('n'); fc.save_file('n', F.STATES / 'l51a_p23100N.mst', 23100)
fc.step(w[len(p):], record='last'); m2 = fc.ram(); fc.close()
d2 = [(hex(a), m2[a], n2[a]) for a in range(0x800) if m2[a] != n2[a] and not (0x100 <= a < 0x200)]
print('diff @23588 after patch', d2)
