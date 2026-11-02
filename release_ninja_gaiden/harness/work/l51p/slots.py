"""print Ryu + active enemy slots on the TAS dump for frames: python work/l51p/slots.py f1 [f2 [step]]"""
import sys
sys.path.insert(0, 'work/l51p')
from lib0 import *
a = [int(x) for x in sys.argv[1:]]
f1 = a[0]; f2 = a[1] if len(a) > 1 else f1; st = a[2] if len(a) > 2 else 1
for f in range(f1, f2 + 1, st):
    m = TM(f); X, y = XY(m); scr = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52])*256 + m[0x51]
    s = []
    for j in range(8):
        if m[0x73] >> j & 1:
            s.append(f's{j} t{m[0x400+j]} ({scr+m[0x460+j]},{m[0x480+j]})')
    print(f, f'X {X} y {y} hp {m[0x65]} np {m[0x64]} it {m[0xC9]} BF {m[0xBF]} 62 {m[0x62]} 63 {m[0x63]} inv {m[0x95]} 84 {m[0x84]:02x} 5C {m[0x5C]} |', '; '.join(s))
