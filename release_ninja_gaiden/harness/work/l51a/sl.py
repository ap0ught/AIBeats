"""Our slots per frame for a stage-rows file: python work/l51a/sl.py rows f1 f2 [step] [lag]"""
import sys; sys.path.insert(0, 'work/l51a')
from lib import *
rows = rows_file(sys.argv[1]); f1, f2 = int(sys.argv[2]), int(sys.argv[3]); st = int(sys.argv[4]) if len(sys.argv) > 4 else 1
LG = int(sys.argv[5]) if len(sys.argv) > 5 else 509
fc, _k = start_core(rows); fc.step(rows[_k:f1 - CTL], record='last')
def sl(m):
    scr = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52])*256 + m[0x51]
    return '; '.join(f's{j} t{m[0x400+j]} ({scr+m[0x460+j]},{m[0x480+j]})' for j in range(8) if m[0x73] >> j & 1)
for f in range(f1, f2 + 1):
    fc.step([rows[f - CTL]], record='last'); m = fc.ram()
    if (f - f1) % st: continue
    X, y = XY(m); t = TM(f - LG)
    print(f, f'X {X} y {y} scr {(m[0x52]-256 if m[0x52]>=128 else m[0x52])*256+m[0x51]} |', sl(m), '|| TAS', f - LG, XY(t), 'scr', (t[0x52]-256 if t[0x52]>=128 else t[0x52])*256+t[0x51], '|', sl(t), flush=True)
fc.close()
