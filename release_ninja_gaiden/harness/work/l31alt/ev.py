"""Mesen: play 3-1 stage rows (file, rows after 3-1 control) then blank rows until the stage changes; print events
(lantern breaks/pickups, ninpo, item, hp changes, throws) and the stage-change frame.
    python work/l31alt/ev.py <rows file> [N rows to use] [--quiet]"""
import sys
sys.path.insert(0, 'work/l31alt')
from lib import *
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
if len(sys.argv) > 2 and sys.argv[2].isdigit(): rows = rows[:int(sys.argv[2])]
quiet = '--quiet' in sys.argv
fc = core()
prev = None
f = F0
for i in range(len(rows) + 600):
    r = rows[i] if i < len(rows) else ()
    fc.step([r], record='last'); m = fc.ram(); f += 1
    k = (m[0x64], m[0xC9], m[0x65], m[0xC8], m[0xC0], m[0x73])
    if not quiet and prev is not None and k != prev:
        print(f, 'X', X(m), 'y', m[0x8A], 'in', '+'.join(r) or '-', 'np', m[0x64], 'it', m[0xC9], 'hp', m[0x65], 'thrown', m[0xC8],
              'lant', [(X(m) - m[0x86] + h['x'], h['y'], h['item'], h['state']) for h in H.lanterns(m)], 'en', enemies(m))
    prev = k
    if m[0x6D] != 5:
        print('STAGE CHANGE at frame', f, 'row', i + 1, 'of', len(rows), 'hp', m[0x65], 'np', m[0x64], 'item', m[0xC9], '$62', m[0x62], 'timer', m[0x63])
        break
fc.close()
