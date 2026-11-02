"""python work/l32b/xp.py <mst> "<rows spec>" [--every k]   spec: 'Right*20 A+Right*5 -*3' tokens ROW*n"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng import fastcore as F
a = sys.argv[1:]
ev = 1
if '--every' in a:
    i = a.index('--every'); ev = int(a[i+1]); del a[i:i+2]
def parse(spec):
    out = []
    for tok in spec.split():
        r, n = (tok.rsplit('*', 1) + ['1'])[:2] if '*' in tok else (tok, '1')
        row = () if r == '-' else tuple(sorted(r.split('+')))
        out += [row] * int(n)
    return out
FLD = dict(F._fields())
for j in range(8):
    FLD[f't{j}'] = 0x400 + j; FLD[f's{j}'] = 0x410 + j; FLD[f'x{j}'] = 0x460 + j; FLD[f'y{j}'] = 0x480 + j
FLD['eb'] = 0x73
def run(mst, rows):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD); fc.put('s', open(mst, 'rb').read()); fc.load('s')
    r = fc.run_batch('s', [rows], record='all')[0]; fc.close(); return r.states
if __name__ == '__main__':
    rows = parse(a[1])
    for i, s in enumerate(run(a[0], rows)):
        if i % ev and i != len(rows) - 1: continue
        scr = C.abs_x(s) - s['x']
        en = ' '.join(f"{j}:t{s[f't{j}']}s{s[f's{j}']}@{scr + s[f'x{j}']},{s[f'y{j}']}" for j in range(8) if s['eb'] >> j & 1)
        print(i + 1, '+'.join(rows[i]) or '-', 'X', C.abs_x(s), 'y', s['y'], 'vy', s['vy'], 'an', s['anim'], 'fl', hex(s['rflags']), 'coll', s['coll'], 'inv', s['inv'], 'hp', s['hp'], en)
