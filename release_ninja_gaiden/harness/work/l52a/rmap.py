"""room kinds map (no path) X range, from the TAS dump frames f1..f2"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'work/l52p')
from ng.solve import common as C
from lib0 import *
f1, f2 = int(sys.argv[1]), int(sys.argv[2])
d = C.ROM.read_bytes(); b7 = 16 + 7*0x4000
cols = {}
for f in range(f1, f2 + 1):
    r = TM(f)
    s52 = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]; scroll = s52*256 + r[0x51]
    fine = scroll % 16
    for sx in range(16):
        ax = scroll - fine + sx*16
        if ax < scroll: continue
        t = (d[b7 + 0xE7CC - 0xC000 + sx] + r[0x5F]) % 0xC0
        cols[ax] = [((r[0x300 + (t + band//2) % 0xC0] >> 4) if band % 2 == 0 else (r[0x300 + (t + band//2) % 0xC0] & 15)) for band in range(12)]
xs = sorted(cols)
print('      ' + ''.join(f'{x:<4d}'[:4] if (x//16) % 4 == 0 else '' for x in xs))
for band in range(12):
    print(f'{64+16*band:3d}   ' + ''.join(('.' if cols[x][band] == 0 else 'ABCDEFGHIJKLMNOP'[cols[x][band]-1] if cols[x][band] > 9 else str(cols[x][band])) for x in xs))
