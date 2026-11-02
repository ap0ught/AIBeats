"""Kill row / hp / T of a 6-5 line for every bf (Mesen, TAS control-1 state with $BF poked).
python work/l65/cover.py <line.txt> [--vals 0-255] [--out tsv]  -> prints 'bf kill hp T' (kill = row number, control row = 1; '-' = none)"""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
VS = opt('--vals', '0-255'); OUT = opt('--out', '')
vals = []
for p in VS.split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    else: vals.append(int(p))
rows = rows_of(a[0]) + [()] * 20
fc = core65()
res = test_bfs(fc, rows, vals)
fc.close()
lines = []
for v in vals:
    k, hp, T = res[v]
    lines.append(f'{v}\t{k if k else "-"}\t{hp}\t{T}')
ok = [v for v in vals if res[v][0]]
print(f'# {a[0]}: kills {len(ok)}/{len(vals)}')
print('\n'.join(lines))
if OUT: open(OUT, 'w', newline='\n').write(f'# {a[0]}\n' + '\n'.join(lines) + '\n')
