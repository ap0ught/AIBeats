"""l53b: NesHawk pad-read conflicts: frames where $2A != the row's mask. python work/l53b/nhconf.py stage.txt [nhstate l52b_e4_27360] [F 27360]"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
from ng.mode import TICKS
rows = [row(l.strip()) for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
nhs = sys.argv[2] if len(sys.argv) > 2 else 'l52b_e4_27360'
F = int(sys.argv[3]) if len(sys.argv) > 3 else 27360
BIT = {'A': 0x80, 'B': 0x40, 'Select': 0x20, 'Start': 0x10, 'Up': 0x08, 'Down': 0x04, 'Left': 0x02, 'Right': 0x01}
e = C.open_emu('l53b_nhconf.log')
try:
    e.tick(TICKS); e.load(nhs); _, rams = e.run_ram(rows[1:])
finally:
    e.close()
bad = []
for i, m in enumerate(rams):
    r = rows[i + 1]; want = sum(BIT[b] for b in r)
    if m[0x2A] != want: bad.append((F + 1 + i, P(r), m[0x2A], want, P(rows[i])))
print('conflicts', len(bad))
for b in bad: print(b)
