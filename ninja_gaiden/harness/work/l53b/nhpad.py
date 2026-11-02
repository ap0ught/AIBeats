"""l53b: NesHawk vs Mesen pad byte $2A and Ryu per frame over a window. python work/l53b/nhpad.py stage.txt f1 f2"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
from ng.mode import TICKS
rows = [row(l.strip()) for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
f1, f2 = int(sys.argv[2]), int(sys.argv[3])
seg = rows[1:f2 - 27360 + 1]
fc = core('states/mesen/l53a_e4_27359.mst'); _, rec, _ = fc.step(rows[:f2 - 27359], record='all'); fc.close()
e = C.open_emu('l53b_nhpad.log')
try:
    e.tick(TICKS); e.load('l52b_e4_27360'); _, rams = e.run_ram(seg)
finally:
    e.close()
for f in range(f1, f2 + 1):
    m = rams[f - 27361]; s = rec[f - 27360]
    print(f, P(rows[f - 27360]), 'NH pad', m[0x2A], XY(m), '| Mesen', RXY(s))
