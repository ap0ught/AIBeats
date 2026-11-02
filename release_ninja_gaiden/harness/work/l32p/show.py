"""play rows from a mst (poke BF at start optional) and print per-frame Ryu + enemies.
python work/l32p/show.py <mst> <hist file> <rows spec: file or py-expr> [--bf v] [--every k] [--f0 frame]"""
import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
bf = opt('--bf', -1); every = opt('--every', 1); f0 = opt('--f0', 0)
mst, hf, spec = a[:3]
H = C.rows_of(hf)
f0 = f0 or len(H)
if spec.endswith('.txt'): want = C.rows_of(spec)
else: want = eval(spec, {'TR': TR})
rows = legal_after([], want, H)
fld = dict(F._fields())
for j in range(8):
    fld[f't{j}'] = 0x400 + j; fld[f's{j}'] = 0x410 + j; fld[f'T{j}'] = 0x408 + j; fld[f'x{j}'] = 0x460 + j; fld[f'y{j}'] = 0x480 + j
fld['eb'] = 0x73
fc = F.FastCore(boot_rows=None, ticks=True, fields=fld); fc.put('s', open(mst, 'rb').read()); fc.load('s')
if bf >= 0: fc.poke(0xBF, bf); fc.save('s')
r = fc.run_batch('s', [rows], record='all')[0]; fc.close()
for i, s in enumerate(r.states):
    if i % every and i != len(r.states) - 1: continue
    scr = C.abs_x(s) - s['x']
    en = ' '.join(f"{j}:t{s[f't{j}']}s{s[f's{j}']}T{s[f'T{j}']}@{scr + s[f'x{j}']},{s[f'y{j}']}" for j in range(8) if s['eb'] >> j & 1)
    print(f0 + i + 1, '+'.join(rows[i]) or '-', 'X', ax(s), 'y', s['y'], 'hp', s['hp'], 'BF', s['rng'], 'anim', s['anim'], en)
