"""absolute-X collision map: python work/l11r/amap.py <rows file|-> t1,t2..  (ring col = (X//16)%32)"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l11r')
from lib import *
rows = BASE if sys.argv[1] == '-' else C.rows_of(sys.argv[1])
fc = F.FastCore(boot_rows=INTRO)
done = 0
for t in [int(v) for v in sys.argv[2].split(',')]:
    fc.step(rows[done:t]); done = t
    r = fc.ram()
    s52 = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]
    scroll = s52 * 256 + r[0x51]
    X, y = scroll + r[0x86], r[0x8A]
    print(f't {t} Ryu X {X} y {y} scroll {scroll} hp {r[0x65]} rng {r[0xBF]} $5F {r[0x5F]} (check {6*((scroll//16)%32)})')
    c0, c1 = scroll // 16 - 2, scroll // 16 + 18
    print('     ' + ''.join(str((c * 16 // 100) % 10) for c in range(c0, c1)) + '   (X/100 digit; col X = 16*col)')
    print('     ' + ''.join(str((c * 16 // 10) % 10) for c in range(c0, c1)))
    for band in range(12):
        yy = 64 + 16 * band
        line = ''
        for c in range(c0, c1):
            b = r[0x300 + 6 * (c % 32) + band // 2]
            k = (b >> 4) if band % 2 == 0 else (b & 15)
            ch = '.' if k == 0 else ('ABCDEFGHIJKLMNOP'[k - 1] if k > 9 else str(k))
            if c * 16 <= X < c * 16 + 16 and yy <= y < yy + 16: ch = '@'
            line += ch
        print(f'{yy:3d}  {line}')
    for e in H.enemies(r):
        print('   enemy', e['slot'], 'type', e['type'], 'pose', e['pose'], 'X', scroll + e['x'], 'y', e['y'], 'xr', e['xr'], 'yr', e['yr'], 'hp', e['hp'])
fc.close()
