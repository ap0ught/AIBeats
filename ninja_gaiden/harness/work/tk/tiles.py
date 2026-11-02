"""Print the $300 collision map (hitbox.tile_kinds) around Ryu at a row of an input file. Row = 16-px band of y
(band k = y 64+16k .. ), using the Lua GetCell formula for Ryu's column.
    python work/tk/tiles.py <state> <rows> <i>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, hitbox as H
from ng.mode import TICKS
rows = C.rows_of(sys.argv[2])[:int(sys.argv[3])]
e = C.open_emu('tk_tiles.log')
try:
    e.tick(TICKS); e.load(sys.argv[1]); e.run(rows); r = e.ram_all()
    d = C.ROM.read_bytes(); b7 = 16 + 7 * 0x4000
    def cell(x, y):
        t = d[b7 + 0xE7CC - 0xC000 + (x >> 4)] + r[0x5F]
        if t >= 0xC0: t -= 0xC0
        return t
    rx, ry = r[0x86], r[0x8A]
    print('ryu', rx, ry, 'scroll', r[0x51], r[0x52])
    for yy in range(64, 256, 16):
        line = ''
        for xx in range(0, 256, 16):
            c = cell(xx, yy); col = c
            v = r[0x300 + ((c + ((yy - 64) >> 5) * 0) % 0xC0)]
            # the ring is 6 bytes per column, each byte = two 16-px bands
            band = (yy - 64) // 16
            b = r[0x300 + (c - c % 6 + band // 2) % 0xC0] if False else r[0x300 + (c + band // 2) % 0xC0]
            k = (b >> 4) if band % 2 == 0 else (b & 15)
            ch = '.' if k == 0 else 'ABCDEFGHIJKLMNOP'[k - 1] if k > 9 else str(k)
            if xx <= rx < xx + 16 and yy <= ry < yy + 16: ch = '@'
            line += ch
        print(f'{yy:3d} {line}')
finally:
    e.close()
