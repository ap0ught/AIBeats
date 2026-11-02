"""Chain (Mesen) vs TAS enemy-set divergence: print frames where the multiset of enemy types differs (first 40).
python work/l42p/endiv.py <stage rows> <from> <to>"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
R = [tuple(r) for r in C.rows_of(sys.argv[1])]; a, b = int(sys.argv[2]), int(sys.argv[3])
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
FL = {'x': 0x86, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'hp': 0x65, 'en': 0x73}
for j in range(8): FL[f't{j}'] = 0x400 + j; FL[f'ex{j}'] = 0x460 + j; FL[f'ey{j}'] = 0x480 + j
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open('states/mesen/l42p_lock16997.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s'); fc.save('p')
st = fc.run_batch('p', [R[:b - 16682 + 1]], record='all')[0].states
n = 0; last = None
for i, s in enumerate(st):
    f = 16998 + i - 316 + 0  # TAS axis: row 0 = 16,682
    f = 16682 + i
    if f < a: continue
    scr = s['sh']*256 + s['sl']
    ours = sorted((s[f't{j}'], scr + s[f'ex{j}'], s[f'ey{j}']) for j in range(8) if s['en'] >> j & 1)
    t = d[(f - f0 - 1)*2048:(f - f0)*2048]; ts = t[0x52]*256 + t[0x51]
    tas = sorted((t[0x400+j], ts + t[0x460+j], t[0x480+j]) for j in range(8) if t[0x73] >> j & 1)
    k = (tuple(x[0] for x in ours), tuple(x[0] for x in tas))
    if k[0] != k[1] and k != last:
        print(f, 'Ryu X', scr + s['x'], s['y'], 'ours', ours, '| TAS', tas); n += 1
        if n > 25: break
    last = k
fc.close()
