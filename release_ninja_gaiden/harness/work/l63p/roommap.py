"""whole-room collision map from the TAS dump (merge of the visible columns over frames f1..f2), with the TAS path.
python work/l63p/roommap.py f1 f2   (kind digits as dmap.py; '*' = TAS Ryu path (X,y))"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'work/l63p')
from ng.solve import common as C
from lib0 import *
f1, f2 = int(sys.argv[1]), int(sys.argv[2])
d = C.ROM.read_bytes(); b7 = 16 + 7*0x4000
cols = {}; path = {}
for f in range(f1, f2 + 1):
    r = TM(f)
    s52 = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]; scroll = s52*256 + r[0x51]
    fine = scroll % 16
    for sx in range(16):
        ax = scroll - fine + sx*16
        if ax < scroll: continue
        t = (d[b7 + 0xE7CC - 0xC000 + sx] + r[0x5F]) % 0xC0
        col = []
        for band in range(12):
            b = r[0x300 + (t + band//2) % 0xC0]; k = (b >> 4) if band % 2 == 0 else (b & 15)
            col.append(k)
        cols[ax] = col
    X, y = XY(r); path.setdefault((X // 16 * 16, y // 16), f)
xs = sorted(cols)
print('cols', xs[0], '..', xs[-1])
for i in range(0, len(xs), 48):
    part = xs[i:i+48]
    print('     ' + ''.join(f'{x//16%100:<2d}'[:1] if x % 160 == 0 else ' ' for x in part))
    print('  X  ' + ''.join(str(x // 160 % 10) if x % 160 == 0 else '.' for x in part), part[0])
    for band in range(12):
        yy = 64 + 16*band; line = ''
        for x in part:
            k = cols[x][band]; ch = '.' if k == 0 else ('ABCDEFGHIJKLMNOP'[k-1] if k > 9 else str(k))
            if (x, yy // 16) in path: ch = '*' if ch == '.' else ch.lower() if ch.isalpha() else '#'
            line += ch
        print(f'{yy:3d}  {line}')
