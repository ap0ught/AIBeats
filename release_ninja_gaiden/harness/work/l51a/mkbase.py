"""Agent l51a (5-1 control -> X-1,504 wall). Base states on the locked chain logs/l44p_r1920_c2_poweron.inputs.txt.
Mesen: states/mesen/lock_51_pre.mst (after row 22,628) and lock_51_ctl.mst (after blank row 22,629)."""
import sys, time
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.solve import common as C
rows = C.rows_of('logs/l44p_r1920_c2_poweron.inputs.txt')
assert len(rows) == 22628, len(rows)
t = time.time()
boot = F.masks_of(list(rows))
with F.FastCore(boot_rows=boot, ticks=False) as fc:
    fc.save('a'); fc.save_file('a', F.STATES / 'lock_51_pre.mst', 22628)
    r = fc.ram()
    print('pre', 'x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'st', r[0x6D], 'rm', r[0x6E], 'bf', r[0xBF], '62', r[0x62], 'it', r[0xC9], flush=True)
    fc.step([()], record='last'); fc.save('b'); fc.save_file('b', F.STATES / 'lock_51_ctl.mst', 22629)
    r = fc.ram()
    print('ctl', 'x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'st', r[0x6D], 'rm', r[0x6E], 'bf', r[0xBF], '62', r[0x62], flush=True)
print('time', time.time() - t)
