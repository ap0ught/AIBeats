"""NesHawk: load an end state, print Ryu/HUD/enemy slots; compare with the TAS RAM at 3-3 control (13,741)."""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
d = open('work/l32p/tas32_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
i = 13741 - f0 - 1; t = d[i*2048:(i+1)*2048]
e = C.open_emu('l32a_nhend.log')
try:
    e.tick(TICKS); st = e.load(sys.argv[1]); m = e.ram_all()
    if m is None:
        _, rams = e.run_ram([()]); m = rams[0]; print('(after one blank frame)')
    for nm, r in (('ours', m), ('TAS', t)):
        print(nm, 'x', r[0x86], 'xsub', r[0x85], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'it', r[0xC9], 'bf', r[0xBF], '62', r[0x62], '63', r[0x63], '73', hex(r[0x73]), 'slots', [r[0x400+k] for k in range(8)], 'stage', r[0x6D], 'anim', r[0x80])
    print('frame', st['frame'])
finally:
    e.close()
