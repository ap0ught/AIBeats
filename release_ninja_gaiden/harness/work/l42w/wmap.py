"""Bird-boost map (research, Mesen): from a state, poke the bird slot's x / y (screen) on a grid, play fixed approach
rows (until ladder contact), and for every config where the bird hits Ryu, finish with the best standard ladder climb.
python -u work/l42w/wmap.py <mst> <frame> <approach rows> --slot 5 [--xs 16:240:8] [--ys 64:200:8] [--out f.tsv]
Prints per config: hit frame, Ryu X/y at the hit, contact frame/y, trigger frame."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/l42w')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from wlib import spec, short, LegState, FL, X

a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d


SL = opt('--slot', 5); XS = opt('--xs', '16:241:8'); YS = opt('--ys', '64:201:8'); OUT = opt('--out', '')
CH = opt('--chunk', 40); SPD = opt('--spd', '')
MST, F0, AP = a[0], int(a[1]), a[2]
rows = [tuple(r) for r in C.rows_of(AP)]
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(MST, 'rb').read()); fc._ka_slot = 's'
CYC = spec('ALU AL R RU RU')
climbs = []
for d in range(0, 5):
    for start in range(5):
        climbs.append((spec(f'RU:{d}') if d else []) + (CYC[start:] + CYC * 12)[:50])
L0 = LegState([()] * 30)
xa, xb, xs = map(int, XS.split(':')); ya, yb, ys = map(int, YS.split(':'))
spds = [None] if not SPD else [tuple(map(int, v.split('/'))) for v in SPD.split(',')]
res_all = []
t0 = time.time()
for sp in spds:
    for bx in range(xa, xb, xs):
        for by in range(ya, yb, ys):
            fc.load('s')
            fc.poke(0x460 + SL, bx); fc.poke(0x480 + SL, by)
            if sp: fc.poke(0x455 + SL, sp[0]); fc.poke(0x44D + SL, sp[1]); fc.poke(0x445 + SL, sp[2])
            fc.save('p'); fc._ka_slot = 'p'
            r = fc.run_batch('p', [rows], record='all', stops=[(0x8C, '==', 32), (0x80, '==', 12), (0x80, '==', 10), (0x5C, '==', 0)])[0]
            st = r.states
            hit = next((i for i in range(1, len(st)) if st[i]['hp'] < st[i - 1]['hp']), None)
            if hit is None and st and st[0]['hp'] < 16: hit = 0
            if hit is None:
                res_all.append((sp, bx, by, None)); continue
            ci = len(st) - 1; s = st[ci]
            if not (s['coll'] == 32 or s['anim'] in (10, 12) or s['c5'] == 0):
                res_all.append((sp, bx, by, (F0 + 1 + hit, X(st[hit]), st[hit]['y'], st[hit]['hp'], None, None, None))); continue
            if s['c5'] == 0:
                trig = F0 + 1 + ci
            else:
                rr = fc.run_batch('p', [rows[:ci + 1]], record='last', keep=True, prefix='cc')[0]
                L1 = L0.after(rows[:ci + 1])
                ok = [c for c in climbs if L1.check(c) is None]
                out = fc.run_batch(rr.slot, ok, record='last', stops=[(0x5C, '==', 0)])
                tr = [o.rows_played for o in out if o.states and o.states[-1]['c5'] == 0]
                trig = F0 + 1 + ci + min(tr) if tr else None
                fc.drop('cc1')
            res_all.append((sp, bx, by, (F0 + 1 + hit, X(st[hit]), st[hit]['y'], s['hp'], F0 + 1 + ci, s['y'], trig)))
    print('spd', sp, 'done', f'{time.time() - t0:.0f}s', flush=True)
fc.close()
lines = ['spd\tbird_x\tbird_y\thit_frame\thit_X\thit_y\thp\tcontact\tcontact_y\ttrigger']
for sp, bx, by, h in res_all:
    lines.append('\t'.join(str(v) for v in ([sp, bx, by] + (list(h) if h else ['-'] * 7))))
if OUT: open(OUT, 'w').write('\n'.join(lines) + '\n')
hits = [z for z in res_all if z[3] and z[3][6]]
hits.sort(key=lambda z: z[3][6])
print(len(res_all), 'configs', len([z for z in res_all if z[3]]), 'hits', len(hits), 'with trigger')
for z in hits[:25]: print(z)
