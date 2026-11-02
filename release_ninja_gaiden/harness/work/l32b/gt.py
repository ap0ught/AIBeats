"""ground truth: our handover + legal TAS rows (lag 194, no B) with stops inserted, Ryu kept invulnerable by poking $95.
python work/l32b/gt.py <n> [stops 'frameoffset:k,...'] -> prints per frame"""
import sys
sys.path.insert(0, 'work/l32b'); sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
import xp, a56_common as A
from ng.solve import common as C, legality as L
from ng import fastcore as F
TR = A.tas_rows()
H = C.rows_of('work/l32a/h_h1252.inputs.txt'); f0 = len(H); lag = 194
n = int(sys.argv[1]); stops = {}
if len(sys.argv) > 2 and sys.argv[2]:
    for q in sys.argv[2].split(','):
        o, k = q.split(':'); stops[int(o)] = int(k)
want = []; k = 0
while len(want) < n:
    if len(want) in stops:
        want += [()] * stops[len(want)]
    want.append(tuple(x for x in TR[f0 - lag + k] if x != 'B')); k += 1
en = L.Enforcer(H[-1900:]); rows = [tuple(sorted(en.emit(w))) for w in want[:n]]
fc = F.FastCore(boot_rows=None, ticks=True, fields=xp.FLD); fc.put('s', open('states/mesen/l32a_h1252.mst', 'rb').read()); fc.load('s')
for j in range(8): pass
out = []
for i in range(n):
    m0 = fc.ram(); fc.poke(0x84, m0[0x84] | 2)
    _, rec, _ = fc.step([rows[i]], record='last'); s = rec[-1]
    m = fc.ram()
    X = C.abs_x(s); scr = X - s['x']
    b = None
    for j in range(8):
        if m[0x73] >> j & 1 and m[0x400 + j] == 11:
            sp = m[0x450 + j]; sp = sp - 256 if sp >= 128 else sp
            b = (j, m[0x460 + j], m[0x458 + j], sp * 256 + m[0x448 + j], m[0x480 + j])
    print(f0 + i + 1, '+'.join(rows[i]) or '-', X, s['x'], s['xsub'], s['y'], m[0x50], scr, b, m[0xA3], m[0xA2])
fc.close()
