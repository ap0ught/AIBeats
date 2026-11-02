"""collision map from the TAS dump at frame f (same decoding as work/l32p/amap.py). python work/l51p/dmap.py f"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'work/l51p')
from ng.solve import common as C
from lib0 import *
r = TM(int(sys.argv[1]))
s52 = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]; scroll = s52*256 + r[0x51]
print(f'Ryu X {scroll + r[0x86]} y {r[0x8A]} scroll {scroll}')
d = C.ROM.read_bytes(); b7 = 16 + 7*0x4000; fine = scroll % 16
print('abs X:     ' + ' '.join(f'{scroll - fine + sx*16:4d}' for sx in range(17)))
for band in range(12):
    yy = 64 + 16*band; line = ''
    for sx in range(16):
        t = (d[b7 + 0xE7CC - 0xC000 + sx] + r[0x5F]) % 0xC0
        b = r[0x300 + (t + band//2) % 0xC0]; k = (b >> 4) if band % 2 == 0 else (b & 15)
        line += '    ' + ('.' if k == 0 else ('ABCDEFGHIJKLMNOP'[k-1] if k > 9 else str(k)))
    print(f'{yy:3d}       {line}')
