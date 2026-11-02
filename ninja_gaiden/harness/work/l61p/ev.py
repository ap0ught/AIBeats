"""TAS Act-6 events (5-4 control -> 6-3 control): stage/room changes, hp/ninpo/item, $5C, timer, enemy spawns."""
import sys
sys.path.insert(0, 'work/l61p')
from lib0 import *
N = int(sys.argv[1]) if len(sys.argv) > 1 else 0
f1 = int(sys.argv[2]) if len(sys.argv) > 2 else TF0 + 1
f2 = int(sys.argv[3]) if len(sys.argv) > 3 else TF0 + NF
prev = TM(f1)
for f in range(f1 + 1, f2 + 1):
    m = TM(f); X, y = XY(m); ev = []
    for a, nm in ((0x6E, 'room'), (0x6D, 'stage'), (0x65, 'hp'), (0x64, 'np'), (0xC9, 'item'), (0x5C, '5C'), (0x66, 'bossHP'), (0x63, 'timer')):
        if m[a] != prev[a]: ev.append(f'{nm} {prev[a]}->{m[a]}')
    scr = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52])*256 + m[0x51]
    for j in range(8):
        on, on0 = m[0x73] >> j & 1, prev[0x73] >> j & 1
        if on and (not on0 or m[0x400+j] != prev[0x400+j]): ev.append(f'spawn s{j} t{m[0x400+j]} ({scr+m[0x460+j]},{m[0x480+j]})')
        if on0 and not on: ev.append(f'gone s{j} t{prev[0x400+j]}')
    if ev or (N and f % N == 0):
        print(f, f'X {X} y {y} hp {m[0x65]} np {m[0x64]} it {m[0xC9]} BF {m[0xBF]} 62 {m[0x62]} rm {m[0x6E]} |', ', '.join(ev))
    prev = m
