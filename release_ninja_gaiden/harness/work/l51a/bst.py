"""Wall-bird state (world X with fraction, x speed, y) vs Ryu: TAS dump frames or a rows file (our frames)."""
import sys; sys.path.insert(0, 'work/l51a')
from lib import *
def bird(m, ryX):
    scr = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51]
    out = []
    for j in range(8):
        if m[0x73] >> j & 1 and m[0x400 + j] == 11:
            x = scr + m[0x460 + j] + m[0x458 + j] / 256
            sp = m[0x450 + j]; sp = sp - 256 if sp >= 128 else sp; v = sp + m[0x448 + j] / 256
            out.append((j, round(x - ryX, 2), round(v, 3), m[0x480 + j]))
    return out
if sys.argv[1] == 'tas':
    for f in range(int(sys.argv[2]), int(sys.argv[3]) + 1, int(sys.argv[4])):
        m = TM(f); X, y = XY(m); print(f, 'Ryu', X, y, 'birds(rel x, v, y)', bird(m, X + m[0x85] / 256 if False else X))
else:
    rows = rows_file(sys.argv[1]); a, b, st = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    fc, _k = start_core(rows); fc.step(rows[_k:a - CTL], record='last')
    for f in range(a, b + 1):
        if f - CTL >= len(rows): break
        fc.step([rows[f - CTL]], record='last')
        if (f - a) % st == 0:
            m = fc.ram(); X, y = XY(m); print(f, 'Ryu', X, y, 'birds', bird(m, X))
    fc.close()
