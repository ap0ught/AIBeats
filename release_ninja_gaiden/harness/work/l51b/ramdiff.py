"""RAM diff NesHawk state vs Mesen state: python work/l51b/ramdiff.py <neshawk state name> <mesen mst>"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
from ng.mode import TICKS
e = C.open_emu('l51b_ramdiff.log')
try:
    e.tick(TICKS); e.load(sys.argv[1]); nh = e.ram_all()
finally:
    e.close()
fc = core(sys.argv[2]); ms = fc.ram(); fc.close()
d = [(hex(i), nh[i], ms[i]) for i in range(0x800) if nh[i] != ms[i] and not (0x200 <= i < 0x300)]
print(len(d), d)
open('work/l51b/nh_' + sys.argv[1].replace('/', '_') + '.ram', 'wb').write(nh)
