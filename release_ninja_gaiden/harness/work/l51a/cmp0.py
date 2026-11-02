import sys; sys.path.insert(0, 'work/l51a')
from lib import *
fc = core('states/mesen/lock_51_ctl.mst'); r = fc.ram(); fc.close()
fc = core('states/mesen/l51p_tas22125.mst'); t = fc.ram(); fc.close()
d = [(hex(a), r[a], t[a]) for a in range(0x800) if r[a] != t[a] and not (0x100 <= a < 0x200)]
print(len(d)); print(d[:80])
