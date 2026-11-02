"""Print the TAS line per frame from tas43_ram.bin: frame, row, X, y, vy, anim $80, coll $8C, rf $84, hp, np, room, enemies.
python work/r1920/tasdump.py f1 f2 [step] [--en]"""
import sys; sys.path.insert(0, 'work/l43p')
from lib import TM, XY, T, P
from ng.solve.hitbox import BIT
a = sys.argv[1:]; en = '--en' in a; a = [x for x in a if x != '--en']
f1, f2 = int(a[0]), int(a[1]); st = int(a[2]) if len(a) > 2 else 1
for f in range(f1, f2 + 1, st):
    m = TM(f); X, y = XY(m)
    s = f'{f} {P(T(f)):6s} rm {m[0x6E]} X {X:5d} y {y:3d} vy {m[0x89]:3d} an {m[0x80]:2d} co {m[0x8C]:3d} rf {m[0x84]:3x} hp {m[0x65]} np {m[0x64]} inv {m[0x95]} bf {m[0xBF]}'
    if en:
        sc = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51]
        s += ' |' + ' '.join(f'{j}:t{m[0x400+j]}@{m[0x460+j]+sc}/{m[0x480+j]}' for j in range(8) if m[0x73] & BIT[j])
    print(s)
