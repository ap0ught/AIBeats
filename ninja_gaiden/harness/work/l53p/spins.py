"""TAS 5-3 spins (ninpo -5) and what they hit: enemy slots that go inactive within 24 f while ON SCREEN (kills),
ninpo / item pickups after. Also every kill by any means (slot deactivates on screen)."""
import sys
sys.path.insert(0, 'work/l53p')
from lib0 import *
def scr(m): return (m[0x52] - 256 if m[0x52] >= 128 else m[0x52])*256 + m[0x51]
prev = TM(26608); kills = []
for f in range(26609, 29100):
    m = TM(f)
    for j in range(8):
        if prev[0x73] >> j & 1 and not (m[0x73] >> j & 1):
            sx = prev[0x460+j]; on = 8 <= sx <= 248 and prev[0x480+j] < 236
            kills.append((f, j, prev[0x400+j], scr(prev) + sx, prev[0x480+j], on, m[0x6E]))
    prev = m
spins = [f for f in range(26609, 29100) if TM(f)[0x64] == TM(f-1)[0x64] - 5]
print('spins', len(spins), spins)
for f, j, t, x, y, on, rm in kills:
    near = [s for s in spins if 0 <= f - s <= 30]
    print(f'{f} rm {rm} s{j} t{t:2d} at ({x},{y}) {"on " if on else "OFF"} {"spin "+str(near[-1]) if near else ""}')
