"""Play rows from a state and print the trace. python work/l52b/play.py F0 <spec or @file> [--state f.mst] [--every k] [--poke a=v;..]
spec: 'Row*n,Row*n'  (Row like A+Left, '-' = blank). Prints frame, row, X, y, hp, np, item, room, $5C, enemies near."""
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
ST = opt('--state', ''); SAVEST = opt('--savest', ''); EV = opt('--every', 1); POKE = opt('--poke', ''); EN = opt('--en', 0)
F0 = int(a[0]); spec = a[1]
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
rows = [row(l.strip()) for l in open(spec[1:]) if l.strip() and not l.startswith('#')] if spec.startswith('@') else rr(spec)
fc = core(ST) if ST else core_at(F0)
for part in [p for p in POKE.split(';') if p]:
    k, v = part.split('='); fc.poke(int(k, 0), int(v, 0))
_, st, _ = fc.step(rows, record='all')
if SAVEST:
    fc.save('z'); fc.save_file('z', SAVEST, frame=F0 + len(rows)); print('saved', SAVEST, F0 + len(rows))
fc.close()
prev = None
for i, s in enumerate(st):
    f = F0 + 1 + i; X, y = RXY(s)
    ch = prev is None or any(s[k] != prev[k] for k in ('hp65', 'np64', 'item', 'room6e', 'e5c'))
    if ch or i % EV == 0 or i == len(st) - 1:
        en = ''
        if EN:
            en = ' '.join(f"t{s[f't{j}']}@{s[f'ex{j}']},{s[f'ey{j}']}" for j in range(8) if s[f't{j}'])
        print(f, P(rows[i]), f"X {X}.{s['xsub']:03d} y {y} vy {s['vy']} coll {s['coll']} anim {s['anim']} rf {s['rflags']} hp {s['hp65']} np {s['np64']} it {s['item']} rm {s['room6e']} 5c {s['e5c']}", en)
    prev = s
