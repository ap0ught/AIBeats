"""l62: NesHawk kill state from l53c_30251 + the candidate's rows. python work/l62/mkkill.py [file] [state] [upto] [name]"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import read_inputs
a = sys.argv[1:]
F = a[0] if len(a) > 0 else 'work/l53c/v1c_cn1_poweron.inputs.txt'
ST = a[1] if len(a) > 1 else 'l53c_30251'
UP = int(a[2]) if len(a) > 2 else 30308
NM = a[3] if len(a) > 3 else 'l62_k30306'
R = [tuple(r) for r in read_inputs(F)]
e = C.open_emu('l62_mkkill.log')
try:
    e.tick(TICKS)
    st = e.load(ST); f0 = st['frame']; print('state frame', f0, st)
    sts, rams = e.run_ram(R[f0:UP])
    for i, m in enumerate(rams):
        f = f0 + 1 + i
        if f >= 30296 and f <= 30310 or f == UP: print(f, 'bh', m[0x66], '6D', m[0x6D], 'BF', m[0xBF], '3E', m[0x3E], '62', m[0x62], 'hp', m[0x65], 'np', m[0x64])
    e.save(NM); print('saved', NM, e.state())
finally:
    e.close()
