import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
e = C.open_emu('l62_chk65.log')
try:
    e.tick(TICKS)
    st = e.load('l63v1_39880'); f0 = st['frame']
    for d in (0, 6):
        S3 = 40462 + d
        e.load('l63v1_39880')
        _, rams = e.run_ram([()] * (S3 - f0 - 1) + [('Start',), ('Start',)] + [()] * 400)
        prev = None
        for i, m in enumerate(rams):
            f = f0 + 1 + i
            k = (m[0x6D], m[0x6E], m[0x5C], m[0x73] != 0)
            if k != prev: print(d, f, 'f-S', f - S3, '6D', m[0x6D], '6E', m[0x6E], '5C', m[0x5C], 'eact', m[0x73], 'BF', m[0xBF])
            prev = k
finally:
    e.close()
