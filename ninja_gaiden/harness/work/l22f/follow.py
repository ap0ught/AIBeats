"""play prefix rows (stage rows from 2-1 control) then legalized TAS rows from TAS row k0, report divergence.
python work/l22f/follow.py <prefix file|-> <k0> <n> [--out f] [--keep m] [--every 25]"""
import sys
sys.path.insert(0, 'work/l22f'); sys.path.insert(0, '.')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
out = opt('--out', ''); keep = opt('--keep', -1); every = opt('--every', 25)
pre = [] if a[0] == '-' else C.rows_of(a[0])
k0 = int(a[1]); n = int(a[2])
tail = legal_after(pre, TR[k0:k0+n])
rows = list(pre) + tail
r = play(rows)
f0 = F0 + len(pre)
div = None
for i, s in enumerate(r.states[len(pre):]):
    t = T[k0 + i + 1]
    dx = ax(s) - ax(t); dy = s['y'] - t['y']
    bad = abs(dx) > 2 or abs(dy) > 2 or s['room'] != t['room'] or s['hp'] < t['hp']
    if div is None and bad: div = i
    if i % every == 0 or i == div or s['stage'] != 3:
        print(f"i {i} f {f0+i+1} r{s['room']} X {ax(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} | TAS {k0+i+1} r{t['room']} X {ax(t)} y {t['y']} hp {t['hp']} np {t['ninpo']}" + ('  <== div' if i == div else ''))
    if s['stage'] != 3: break
print('lag', f0 - k0, 'div row', div, 'played', len(r.states))
if out:
    m = keep if keep >= 0 else (div if div is not None else len(tail))
    C.write_inputs(out, rows[:len(pre) + m], f'2-2 stage rows: prefix + legal TAS {k0}..{k0+m}')
    print('wrote', out, len(pre) + m)
