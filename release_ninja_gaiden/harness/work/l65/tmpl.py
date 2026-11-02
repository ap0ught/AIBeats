"""Template heart lines on podP1: P1 (pod dead row 123) + Right x33 (X 110, row 156) + wait + N jump cycles, each cycle = 44 rows:
A on rows 0-1, Right on rows r0..kR-1, slash cycle Down|Down+B|B|-|- from row o, Left from row kL (lands at X ~110 on row 43; 6 heart
hits per jump from X 110). First jump row J = max(157, hd(bf) + a); g blank rows between cycles.
python work/l65/tmpl.py <vals> [--as -8,-6,..] [--gs 0] [--spec 7,10,38,0] [--res work/l65/tmpl.res.tsv] [--tag t1]"""
import sys, os
sys.path.insert(0, 'work/l65')
from lib65 import *
from ng.fastcore import free_ram_gb
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
AS = [int(x) for x in opt('--as', '-8,-6,-4,-2,0,2,4,6,8').split(',')]
GS = [int(x) for x in opt('--gs', '0').split(',')]
r0, kR, kL, o = [int(x) for x in opt('--spec', '7,10,38,0').split(',')]
RES = opt('--res', 'work/l65/tmpl.res.tsv'); TAG = opt('--tag', 't1'); NCY = int(opt('--ncy', '4'))
vals = []
for p in a[0].split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    else: vals.append(int(p))
HD = {}
for l in open('work/l65/fb1.out'):
    p = l.split()
    if len(p) > 2 and p[1] == 'hd': HD[int(p[0])] = int(p[2])
def cycle():
    rr = []
    for t in range(44):
        r = set()
        if t < 2: r.add('A')
        if t >= kL: r.add('Left')
        else:
            if r0 <= t < kR: r.add('Right')
            k = t - o
            if k >= 0:
                ph = k % 5
                if ph == 0: r.add('Down')
                elif ph == 1: r |= {'Down', 'B'}
                elif ph == 2: r.add('B')
        rr.append(tuple(sorted(r)))
    return rr
CY = cycle()
P1 = rows_of('work/l65/podP1.txt'); PRE = P1 + [('Right',)] * 33
HIST = [()] * 150
fc = core65()
fc.load('c0'); fc.poke(0xBF, 0); fc.step(P1[:120]); fc.save('p120')
os.makedirs('work/l65/lines', exist_ok=True)
out = open(RES, 'a', newline='\n')
for v in vals:
    if free_ram_gb() < 1.5: print('low RAM, stop at', v, flush=True); break
    best = None
    for aa in AS:
        J = max(len(PRE) + 1, HD[v] + aa)
        for g in GS:
            rows = PRE + [()] * (J - len(PRE) - 1)
            for c in range(NCY): rows += CY + [()] * g
            fc.load('p120'); fc.poke(0xBF, (v + 120) % 256); fc.save('q')
            oc = outcome(fc.run_batch('q', [rows[120:] + [()] * 20], record='last', stops=STOPS)[0])
            if oc[0] and (best is None or oc[0] + 120 < best[0]):
                best = (oc[0] + 120, oc[1], J, g, rows[:oc[0] + 120])
    if best:
        k, hp, J, g, rows = best
        L = K.Legal(HIST); ok = all(not L.why(r) and (L.push(r) or True) for r in rows)
        fn = f'work/l65/lines/{TAG}_j{J}_g{g}.txt'
        if not os.path.exists(fn):
            with open(fn, 'w', newline='\n') as f:
                f.write(f'# l65 template {TAG}: podP1 + Right x33 (X 110) + wait, jump cycles (44 rows: A 0-1, Right {r0}-{kR - 1}, slash from {o}, Left from {kL}) from row {J}, gap {g} (row 1 = 6-5 control row)\n')
                for r in rows: f.write(('+'.join(r) if r else '') + '\n')
        if ok: out.write(f'{v}\t{fn}\t{k}\t{hp}\n'); out.flush()
        print(v, 'hd', HD[v], 'kill', k, 'hp', hp, 'J', J, 'g', g, 'legal', ok, flush=True)
    else:
        print(v, 'hd', HD[v], 'none', flush=True)
fc.close()
