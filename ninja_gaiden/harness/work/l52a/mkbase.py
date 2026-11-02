"""Mesen base state after row 24,997 from l51c_pb5_24481 + locked rows; NesHawk state l52a_c3d_24997; RAM diff."""
import sys; sys.path.insert(0, 'work/l52a')
from lib2 import *
from ng.mode import TICKS
rows = [tuple(sorted(r)) for r in C.rows_of(CHAIN)]
fc = core('states/mesen/l51c_pb5_24481.mst')
fc.step(rows[24481:24997], record='last'); ms = fc.ram()
fc.save('z'); fc.save_file('z', BASE52, 24997)
print('mesen', XY(ms), 'hp', ms[0x65], 'np', ms[0x64], 'it', ms[0xC9], 'BF', ms[0xBF], 'rm', ms[0x6E])
e = C.open_emu('l52a_mkbase.log')
try:
    e.tick(TICKS); st = e.load('l51a_c3d_24718'); print('nh load', st)
    _, rams = e.run_ram(rows[24718:24997]); nh = rams[-1]
    e.save('l52a_c3d_24997')
finally:
    e.close()
print('neshawk', XY(nh), 'hp', nh[0x65], 'np', nh[0x64], 'it', nh[0xC9], 'BF', nh[0xBF], 'rm', nh[0x6E])
d = [(hex(i), nh[i], ms[i]) for i in range(0x800) if nh[i] != ms[i] and not (0x100 <= i < 0x300)]
print('RAM diff (no stack/OAM)', len(d), d[:40])
d4 = [(hex(i), nh[i], ms[i]) for i in range(0x400, 0x500) if nh[i] != ms[i]]
print('$400-$4FF diff', d4)
fc.close()
