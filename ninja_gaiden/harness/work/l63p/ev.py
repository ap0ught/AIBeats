import sys
sys.path.insert(0, 'work/l63p'); sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from lib0 import *
import a56_common as A
TR = A.tas_rows()
F = {'st':0x6D,'rm':0x6E,'hp':0x65,'np':0x64,'item':0xC9,'boss':0x66,'t63':0x63,'e5c':0x5C,'bf':0xBF,'3e':0x3E}
prev = None
for f in range(34400, 39690):
    m = TM(f)
    cur = {k: m[a] for k, a in F.items() if k not in ('bf','3e','t63')}
    if prev is not None and cur != prev:
        ch = {k: (prev[k], cur[k]) for k in cur if cur[k] != prev[k]}
        inp = '+'.join(sorted(TR[f-1])) if f-1 < len(TR) else 'END'
        print(f, ch, 'XY', XY(m), 't63', m[0x63], 't62', m[0x62], 'bf', m[0xBF], '3e', m[0x3E], 'in', inp)
    prev = cur
