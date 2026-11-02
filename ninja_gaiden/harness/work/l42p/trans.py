"""4-2 -> 4-3 transition: Start tests (Mesen, TAS line). Trigger 18680 (X 3035 y 84), load 18808, 4-3 control 18959."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
FL = {'x': 0x86, 'y': 0x8A, 'st': 0x6D, 'rm': 0x6E, 'BE': 0xBE, 'pad': 0x2A, 'c0': 0xC0, 'c1': 0xC1, 'hp': 0x65}
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open('states/mesen/l42p_tas16682.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
P = 18670
fc.step(pads[:P - 16682], record='last'); fc.save('p')
from ng.fastcore import masks_of
START = masks_of([('Start',)])[0]; LEFT = masks_of([('Left',)])[0]
def test(sf, n=2, extra=None):
    rows = bytearray(pads[P - 16682:18680 - 16682]) + bytearray(400)
    for k in range(n):
        if 0 <= sf + k - P - 1 < len(rows): rows[sf + k - P - 1] = START
    # hold Left from 18900 on to detect control (x changes)
    for f in range(18900, P + len(rows) + 1):
        if f - P - 1 < len(rows) and rows[f - P - 1] == 0: rows[f - P - 1] = LEFT
    st = fc.run_batch('p', [bytes(rows)], record='all')[0].states
    load = next((P + 1 + i for i, s in enumerate(st) if s['st'] == 10), None)
    ctl = next((P + 1 + i for i, s in enumerate(st) if P + 1 + i > 18900 and s['st'] == 10 and s['x'] != st[i-1]['x']), None)
    return load, ctl
print('no Start', test(0, 0), flush=True)
for sf in [18680, 18681, 18700, 18750, 18800, 18806, 18808, 18810, 18850, 18900, 18930, 18950, 18955]:
    print('Start on', sf, sf + 1, '->', test(sf), flush=True)
fc.close()
