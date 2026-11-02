import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l63p')
import a56_common as A
from lib0 import *
TR = A.tas_rows()
f0, f1 = int(sys.argv[1]), int(sys.argv[2]); st = int(sys.argv[3]) if len(sys.argv) > 3 else 1
for f in range(f0, f1 + 1, st):
    m = TM(f); r = '+'.join(sorted(TR[f-1])) if f - 1 < len(TR) else ''
    en = ' '.join(f'{m[0x400+j]}@{m[0x460+j]},{m[0x480+j]}' for j in range(8) if m[0x400+j])
    print(f, f'{r:16s}', XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'f84', m[0x84], 'scr', m[0x51] + 256*m[0x52], '|', en)
