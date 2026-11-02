"""Mesen collision map around Ryu after stage rows[:n]: python work/l22f/tiles.py <rows|-> <n>"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows = [] if sys.argv[1]=='-' else C.rows_of(sys.argv[1])[:int(sys.argv[2])]
fc = core()
if rows: fc.step(rows, record='last')
r = fc.ram(); fc.close()
d = C.ROM.read_bytes(); b7 = 16 + 7 * 0x4000
def cell(x):
    t = d[b7 + 0xE7CC - 0xC000 + (x >> 4)] + r[0x5F]
    if t >= 0xC0: t -= 0xC0
    return t
rx, ry = r[0x86], r[0x8A]
print('ryu screen x', rx, 'y', ry, 'scroll', r[0x51], r[0x52], 'room', r[0x6E])
print('      ' + ''.join(f'{xx:<16d}'[:1] if False else str((xx//16)%10) for xx in range(0,256,16)))
for yy in range(64, 256, 16):
    line = ''
    for xx in range(0, 256, 16):
        c = cell(xx); band = (yy - 64) // 16
        b = r[0x300 + (c + band // 2) % 0xC0]
        k = (b >> 4) if band % 2 == 0 else (b & 15)
        ch = '.' if k == 0 else 'ABCDEFGHIJKLMNOP'[k - 1] if k > 9 else str(k)
        if xx <= rx < xx + 16 and yy <= ry < yy + 16: ch = '@'
        line += ch
    print(f'{yy:4d}  {line}')
