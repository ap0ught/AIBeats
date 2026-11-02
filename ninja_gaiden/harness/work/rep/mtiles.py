"""Mesen: collision map + enemies around Ryu after power-on row F. python work/rep/mtiles.py hist rows F"""
import sys
sys.path.insert(0,'.')
from ng.solve import common as C, hitbox as H
from ng import fastcore as F
hist=C.rows_of(sys.argv[1]); rows=C.rows_of(sys.argv[2]); fr=int(sys.argv[3])
fc=F.FastCore(boot_rows=hist)
fc.step(rows[:fr-len(hist)],record='last'); r=fc.ram(); fc.close()
d = C.ROM.read_bytes(); b7 = 16 + 7 * 0x4000
def cell(x):
    t = d[b7 + 0xE7CC - 0xC000 + (x >> 4)] + r[0x5F]
    if t >= 0xC0: t -= 0xC0
    return t
rx, ry = r[0x86], r[0x8A]
scr = r[0x52]*256 + r[0x51] if r[0x52] < 128 else 0
print('frame', fr, 'ryu scr x', rx, 'y', ry, 'scroll', r[0x51], r[0x52], 'absx', scr + rx, 'BF', r[0xBF])
print('    ' + ''.join(f'{(scr+xx)%1000:<16d}'[:4] if xx % 64 == 0 else '' for xx in range(0,256,16)))
for yy in range(64, 256, 16):
    line = ''
    for xx in range(0, 256, 16):
        c = cell(xx); band = (yy - 64) // 16
        b = r[0x300 + (c + band // 2) % 0xC0]
        k = (b >> 4) if band % 2 == 0 else (b & 15)
        ch = '.' if k == 0 else 'ABCDEFGHIJKLMNOP'[k - 1] if k > 9 else str(k)
        if xx <= rx < xx + 16 and yy <= ry < yy + 16: ch = '@'
        line += ch
    print(f'{yy:3d} {line}')
for e in H.enemies(r):
    print('enemy', e)
