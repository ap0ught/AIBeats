"""Mesen trace of a rows file from the TAS 4-2 state with $BF poked at control: python work/l42p/mtrace.py <rows> <c> <out.txt>
writes 'frame X y hp pad' per frame."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
rows = C.rows_of(sys.argv[1]); c = int(sys.argv[2])
FL = {'x': 0x86, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'hp': 0x65, 'pad': 0x2A, 'np': 0x64}
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open('states/mesen/l42p_tas16682.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s'); fc.poke(0xBF, c); fc.save('p')
st = fc.run_batch('p', [rows[1:]], record='all')[0].states
with open(sys.argv[3], 'w') as f:
    for i, s in enumerate(st):
        f.write(f"{16683 + i} {s['sh']*256 + s['sl'] + s['x']} {s['y']} {s['hp']} {s['pad']} {s['np']}\n")
fc.close()
