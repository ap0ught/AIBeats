"""Trace rows from the 4-4 pre-control Mesen state (rows start at the control row 21,353).
    python work/l44p/tr.py <rows file | 'tas' | 'p2'> [n] [--poke 0xBF=v,0x62=v]"""
import sys
sys.path.insert(0, 'work/l44p')
from lib import *
from ng.solve import hitbox as H
a = sys.argv[1:]
pk = {}
if '--poke' in a:
    i = a.index('--poke'); pk = {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in a[i + 1].split(','))}; del a[i:i + 2]
src = a[0]; n = int(a[1]) if len(a) > 1 else 40
if src == 'tas':
    rows = [T(f) for f in range(21353, 21353 + n)]
elif src == 'p2':
    rows = [('Left',)] + [tuple(sorted(r)) for r in C.rows_of('logs/a34/4-4_p2.inputs.txt')]
else:
    rows = [tuple(sorted(r)) for r in C.rows_of(src)]
fc = core(PRE)
for k, v in pk.items(): fc.poke(k, v)
for i, r in enumerate(rows[:n]):
    fc.step([r]); m = fc.ram()
    ry = H.ryu(m); en = H.enemies(m)
    es = ' '.join(f"[{e['slot']}:t{e['type']} x{e['x']} y{e['y']} p{e.get('pose')} {'S' if H.spin_hits(m, e) else ''}{'H' if H.hurts(m, e) else ''}]" for e in en)
    print(f"{21353 + i} r{i + 1:3d} {P(r):14s} x{m[0x86]:3d} y{m[0x8A]:3d} f84 {m[0x84]:02x} act{m[0x80]:2d} hp{m[0x65]:2d} np{m[0x64]:2d} bhp{m[0x66]:2d} BF{m[0xBF]:3d} 62:{m[0x62]:2d} 63:{m[0x63]} {es}", flush=True)
fc.close()
