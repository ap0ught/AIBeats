"""l62: FORECAST state for the np-15 line (5-4 control 14 f earlier): l53c_30251 with $BF -14, $62 +14, $3E +14 mod 6 (poked),
then the candidate's 5-4 rows to 30,308; saved as l62_np15fc_30308 (frame labels = ours; real = label - 14)."""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import read_inputs
R = [tuple(r) for r in read_inputs('work/l53c/v1c_cn1_poweron.inputs.txt')]
e = C.open_emu('l62_mkfc.log')
try:
    e.tick(TICKS)
    st = e.load('l53c_30251'); m = e.ram_all()
    print('before', 'BF', m[0xBF], '62', m[0x62], '3E', m[0x3E])
    e.poke(0xBF, (m[0xBF] - 14) % 256); e.poke(0x62, m[0x62] + 14); e.poke(0x3E, (m[0x3E] + 14) % 6)
    m = e.ram_all(); print('after', 'BF', m[0xBF], '62', m[0x62], '3E', m[0x3E])
    _, rams = e.run_ram(R[30251:30308])
    kill = next(30252 + i for i, r in enumerate(rams) if r[0x66] == 0)
    print('kill label', kill, 'real', kill - 14, 'BF', rams[-1][0xBF], '3E', rams[-1][0x3E], '62', rams[-1][0x62])
    e.save('l62_np15fc_30308')
finally:
    e.close()
