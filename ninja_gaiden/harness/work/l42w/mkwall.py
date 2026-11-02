"""Mesen states on the TAS 4-2 line near the exit wall (research only) + the collision map there.
python -u work/l42w/mkwall.py"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True)
fc.put('s', open('states/mesen/l42p_tas16682.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
ROM = C.ROM.read_bytes(); b7 = 16 + 7 * 0x4000
def cmap(r):
    def cell(x):
        t = ROM[b7 + 0xE7CC - 0xC000 + (x >> 4)] + r[0x5F]
        if t >= 0xC0: t -= 0xC0
        return t
    rx, ry = r[0x86], r[0x8A]; scr = r[0x52]*256 + r[0x51]
    print('ryu x', rx, 'y', ry, 'scroll', scr, 'X', scr + rx)
    print('     ' + ''.join(f'{(scr + xx)//16 % 10}' for xx in range(0, 256, 16)) + '   (world X/16 mod 10; col 0 = X %d)' % scr)
    for yy in range(64, 256, 16):
        line = ''
        for xx in range(0, 256, 16):
            c = cell(xx); band = (yy - 64) // 16
            b = r[0x300 + (c + band // 2) % 0xC0]
            k = (b >> 4) if band % 2 == 0 else (b & 15)
            ch = '.' if k == 0 else ('ABCDEFGHIJKLMNOP'[k - 1] if k > 9 else str(k))
            if xx <= rx < xx + 16 and yy <= ry < yy + 16: ch = '@'
            line += ch
        print(f'{yy:3d}  {line}')
for tf in (18596, 18620, 18642):
    fc.load('s'); fc.step(pads[:tf - 16682], record='last'); r = fc.ram()
    fc.save('t'); fc.save_file('t', f'states/mesen/l42w_tas{tf}.mst', frame=tf)
    m = d[(tf - f0 - 1)*2048:(tf - f0)*2048]
    print('TAS', tf, 'mesen X', r[0x52]*256 + r[0x51] + r[0x86], 'y', r[0x8A], 'BF', r[0xBF], '| neshawk X', m[0x52]*256 + m[0x51] + m[0x86], 'y', m[0x8A], 'BF', m[0xBF])
    diff = [hex(a) for a in range(0x800) if r[a] != m[a] and not (0x100 <= a < 0x200)]
    print(' diffs', diff[:20])
    if tf == 18642: cmap(r)
fc.close()
