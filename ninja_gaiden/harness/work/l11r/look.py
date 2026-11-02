"""Mesen: intro + rows[:t] for each t, print the $300 collision map + Ryu + enemies (screen x).
python work/l11r/look.py <rows file> t1,t2,..."""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C, hitbox as H
from ng import fastcore as F
intro = C.rows_of('logs/a12_intro.inputs.txt')
rows = C.rows_of(sys.argv[1])
ts = [int(x) for x in sys.argv[2].split(',')]
fc = F.FastCore(boot_rows=intro)
d = C.ROM.read_bytes(); b7 = 16 + 7 * 0x4000
done = 0
for t in ts:
    _, rr, _ = fc.step(rows[done:t], record='last'); done = t
    r = fc.ram()
    def cell(x):
        c = d[b7 + 0xE7CC - 0xC000 + (x >> 4)] + r[0x5F]
        return c - 0xC0 if c >= 0xC0 else c
    rx, ry = r[0x86], r[0x8A]
    scr = C.abs_x(rr[-1]) - rr[-1]['x']
    print(f't {t} ryu sx {rx} X {scr+rx} y {ry} scroll {scr} hp {r[0x65]} rng {r[0xBF]}')
    print('    ' + ''.join(str(((scr + xx) // 16) % 10) for xx in range(0, 256, 16)))
    for yy in range(64, 256, 16):
        line = ''
        for xx in range(0, 256, 16):
            c = cell(xx)
            band = (yy - 64) // 16
            b = r[0x300 + (c + band // 2) % 0xC0]
            k = (b >> 4) if band % 2 == 0 else (b & 15)
            ch = '.' if k == 0 else ('ABCDEFGHIJKLMNOP'[k - 1] if k > 9 else str(k))
            if xx <= rx < xx + 16 and yy <= ry < yy + 16: ch = '@'
            line += ch
        print(f'{yy:3d} {line}')
    for e in H.enemies(r):
        print('   enemy', e['slot'], 'type', e['type'], 'pose', e['pose'], 'sx', e['x'], 'X', scr + e['x'], 'y', e['y'], 'box', e['box'])
fc.close()
