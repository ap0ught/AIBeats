"""prefix rows (from 3-2 control) + legalized TAS rows from TAS frame k0. python work/l32p/follow.py <prefix|-> <k0> <n> [--mst m] [--out f] [--every 25] [--lag L]"""
import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
out = opt('--out', ''); every = opt('--every', 25); mst = opt('--mst', MST); lag = opt('--lag', F0 - TAS_CTL)
pre = [] if a[0] == '-' else C.rows_of(a[0])
k0 = int(a[1]); n = int(a[2])
tail = legal_after(pre, TR[k0:k0+n])
rows = list(pre) + tail
fc = core(mst)
r = fc.run_batch('s', [rows], record='all', stops=[(0x6D, 'changed', 0)])[0]; fc.close()
div = None
for i, s in enumerate(r.states):
    f = F0 + i + 1
    t = T[f - lag]
    dx = ax(s) - ax(t); dy = s['y'] - t['y']
    bad = abs(dx) > 2 or abs(dy) > 2 or s['hp'] < t['hp']
    if div is None and bad and i >= len(pre): div = i
    if i % every == 0 or i == div:
        print(f"i {i} f {f} X {ax(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} BF {s['rng']} in {'+'.join(rows[i]) or '-'} | TAS {f-lag} X {ax(t)} y {t['y']} hp {t['hp']} np {t['ninpo']}" + ('  <== div' if i == div else ''))
print('div row', div, 'played', len(r.states))
if out:
    m = div if div is not None else len(rows)
    C.write_inputs(out, rows[:m], f'3-2 rows from control: prefix + legal TAS {k0}..')
    print('wrote', out, m)
