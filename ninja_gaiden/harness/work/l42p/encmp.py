"""Chain (Mesen) vs TAS: enemies + Ryu around a TAS frame window. python work/l42p/encmp.py <stage rows> <tas from> <tas to>"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
OFF = 316
R = [tuple(r) for r in C.rows_of(sys.argv[1])]; a, b = int(sys.argv[2]), int(sys.argv[3])
L = [tuple(r) for r in C.rows_of('work/l42p/lt18700.inputs.txt')]
while len(R) < b - 16682 + 1:
    r = set(L[len(R)]); 
    if 'Left' in r and 'Right' in r: r.discard('Left')
    R.append(tuple(sorted(r)))
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
fc = F.FastCore(boot_rows=None, ticks=True)
fc.put('s', open('states/mesen/l42p_lock16997.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
fc.step(R[:a - 16682], record='last')
def en(m):
    scr = m[0x52]*256 + m[0x51]
    return [(j, m[0x400+j], scr + m[0x460+j], m[0x480+j]) for j in range(8) if m[0x73] >> j & 1]
for f in range(a, b + 1):
    fc.step([R[f - 16682]], record='last'); m = fc.ram()
    t = d[(f - f0 - 1)*2048:(f - f0)*2048]
    print(f, 'row', '+'.join(R[f - 16682]) or '-', 'ours X', m[0x52]*256 + m[0x51] + m[0x86], m[0x8A], 'hp', m[0x65], en(m), '| TAS X', t[0x52]*256 + t[0x51] + t[0x86], t[0x8A], 'hp', t[0x65], en(t))
fc.close()
