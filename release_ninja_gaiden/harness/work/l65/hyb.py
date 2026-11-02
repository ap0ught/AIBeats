"""Hybrid lines: podP1 (pod dead row 123) + walk Right to X 113 + wait + a56 r2d5's heart part (its rows 170-, which start with a
jump at X 113 twelve rows before r2d5's heart-down row 182). For each bf the jump row J = hd(bf) - 12 + d, d in DS (>= the walk end).
python work/l65/hyb.py <vals> [ds] -> work/l65/lines/hyb_j<J>.txt, results appended to work/l65/hyb.res.tsv"""
import sys, os
sys.path.insert(0, 'work/l65')
from lib65 import *
from ng.fastcore import free_ram_gb
VS = sys.argv[1]; DS = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '0,1,2,3,4,5,6,8,10,-1,-2').split(',')]
vals = []
for p in VS.split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    else: vals.append(int(p))
HD = {}
for l in open('work/l65/fb1.out'):
    p = l.split()
    if len(p) > 2 and p[1] == 'hd': HD[int(p[0])] = int(p[2])
P1 = rows_of('work/l65/podP1.txt'); r2 = rows_of('work/l63p/dm_r2d5_kill.txt'); H = r2[169:]
fc = core65()
fc.load('c0'); fc.poke(0xBF, 0); fc.step(P1); fc.save('p')
st = fc.run_batch('p', [[('Right',)] * 60], record='all')[0].states
nw = next(i + 1 for i, s in enumerate(st) if s['x86'] >= 113)
print('walk rows', nw, 'X', st[nw - 1]['x86'], flush=True)
J0 = len(P1) + nw + 1
fc.load('c0'); fc.poke(0xBF, 0); fc.step(P1[:120]); fc.save('p120')
out = open('work/l65/hyb.res.tsv', 'a', newline='\n')
os.makedirs('work/l65/lines', exist_ok=True)
for v in vals:
    if free_ram_gb() < 2.0: print('low RAM, stop at', v, flush=True); break
    got = None
    for d in DS:
        J = HD[v] - 12 + d
        if J < J0: continue
        rows = P1 + [('Right',)] * nw + [()] * (J - J0) + H
        fc.load('p120'); fc.poke(0xBF, (v + 120) % 256); fc.save('q')
        o = outcome(fc.run_batch('q', [rows[120:] + [()] * 20], record='last', stops=STOPS)[0])
        if o[0]:
            fn = f'work/l65/lines/hyb_j{J}.txt'
            if not os.path.exists(fn):
                with open(fn, 'w', newline='\n') as f:
                    f.write(f'# l65 hybrid: work/l65/podP1.txt + Right x{nw} (X 113) + {J - J0} blank + a56 r2d5 rows 170- (its heart part); jump on row {J} (row 1 = 6-5 control row)\n')
                    for r in rows: f.write(('+'.join(r) if r else '') + '\n')
            out.write(f'{v}\t{fn}\t{o[0] + 120}\t{o[1]}\n'); out.flush(); got = (J, o[0] + 120, o[1]); break
    print(v, 'hd', HD[v], 'got', got, flush=True)
fc.close()
