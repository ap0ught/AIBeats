"""Print Ryu and every enemy (world X) per frame for a row spec from a state. python work/l52b/birds.py F0 spec --state f.mst [--every k]"""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
if os.environ.get('MINGB'):
    import fcka as _fk; d = list(_fk._init.__defaults__); d[-1] = float(os.environ['MINGB']); _fk._init.__defaults__ = tuple(d)
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
ST = opt('--state', ''); EV = opt('--every', 1)
F0 = int(a[0]); spec = a[1]
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
rows = [row(l.strip()) for l in open(spec[1:]) if l.strip() and not l.startswith('#')] if spec.startswith('@') else rr(spec)
fc = core(ST) if ST else core_at(F0)
for i, r in enumerate(rows):
    fc.step([r]); m = fc.ram()
    if i % EV and i != len(rows) - 1: continue
    X, y = XY(m); sc = X - m[0x86]
    en = ' '.join(f't{m[0x400+j]}@{m[0x460+j]+sc},{m[0x480+j]}' for j in range(8) if m[0x400+j])
    print(F0 + 1 + i, P(r), f'X {X} y {y} hp {m[0x65]} np {m[0x64]} inv {m[0x95]} |', en)
fc.close()
