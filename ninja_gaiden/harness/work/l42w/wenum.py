"""4-2 exit wall: 2-stage enumeration (Mesen). Approach (Right held, 1-2 jumps, optional Right-release pause, optional
Down+B) until the first ladder contact, then ladder climbs (delay d, cycle A+L+U, A+L, R, R+U, R+U) to the trigger.
python -u work/l42w/wenum.py <mst> <start frame> [--hist rows] [--prefix rows] [--j1 0:40] [--h 75] [--top 60]
       [--npmin 10] [--tag t] [--pause 1] [--slash 0] [--j2 1] [--holds 2,12]
Writes work/l42w/we_<tag>.inputs.txt (prefix + best rows) and per-hp bests we_<tag>_h<hp>.inputs.txt."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/l42w')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from wlib import spec, short, LegState, FL, X, trig

a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d


HIST = opt('--hist', ''); PRE = opt('--prefix', ''); J1 = opt('--j1', '0:40'); H = opt('--h', 75); TOP = opt('--top', 60)
NPMIN = opt('--npmin', 10); TAG = opt('--tag', ''); PAUSE = opt('--pause', 1); SLASH = opt('--slash', 0)
J2 = opt('--j2', 1); CH = opt('--chunk', 40); HOLDS = [int(v) for v in opt('--holds', '2,12').split(',')]
PW = [int(v) for v in opt('--pw', '2,4,8').split(',')]; PSTEP = opt('--pstep', 3); PMAX = opt('--pmax', 0)
MST, F0 = a[0], int(a[1])
T00 = time.time()
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(MST, 'rb').read()); fc._ka_slot = 's'; fc.load('s')
hist = [tuple(r) for r in C.rows_of(HIST)][-400:] if HIST else [()] * 30
PR = [tuple(r) for r in C.rows_of(PRE)] if PRE else []
if PR: fc.step(PR, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); HP0 = r0[0x65]; S = F0 + len(PR)
L0 = LegState(hist + PR)
print('start', S, 'X', r0[0x52] * 256 + r0[0x51] + r0[0x86], 'y', r0[0x8A], 'hp', HP0, 'np', r0[0x64], 'BF', r0[0xBF],
      flush=True)
R = ('Right',)


def build(j1, h1, j2, h2, ps, pw, sl):
    rows = [R] * H
    for j, h in ((j1, h1), (j2, h2)):
        if j is None: continue
        for k in range(j, min(H, j + h)): rows[k] = ('A', 'Right')
    if ps is not None:
        for k in range(ps, min(H, ps + pw)): rows[k] = tuple(b for b in rows[k] if b != 'Right')
    if sl is not None:
        for k in range(sl, min(H, sl + 2)): rows[k] = tuple(sorted(set(rows[k]) | {'Down', 'B'}))
    return rows


ja, jb = map(int, J1.split(':'))
bases = [(None, 0)] + [(j1, h1) for j1 in range(ja, jb) for h1 in HOLDS]
bases = [b for b in bases if L0.check(build(b[0], b[1], None, 0, None, 0, None)) is None]
gr = {}
for i in range(0, len(bases), CH):
    res = fc.run_batch('s0', [build(b[0], b[1], None, 0, None, 0, None) for b in bases[i:i + CH]], record='all')
    for b, r in zip(bases[i:i + CH], res):
        gr[b] = [k for k, s in enumerate(r.states) if s['coll'] & 0x10]
print(len(bases), 'bases', f'{time.time() - T00:.0f}s', flush=True)
cands = set()
for (j1, h1), G in gr.items():
    j2s = [None] + ([k for k in G if j1 is None or k >= j1 + max(h1 + 2, 5)] if J2 else [])
    for j2 in j2s:
        cands.add((j1, h1, j2, 2, None, 0, None))
        if PAUSE:
            for ps in range(0, (PMAX or H - 10), PSTEP):
                for pw in PW:
                    cands.add((j1, h1, j2, 2, ps, pw, None))
        if SLASH:
            for sl in range((j1 or 0) + 2, min(H, (j1 or 0) + 50)):
                cands.add((j1, h1, j2, 2, None, 0, sl))
cands = sorted(cands, key=lambda c: tuple(-1 if v is None else v for v in c))
rowsets = []; params = []
for c in cands:
    rows = build(*c)
    if L0.check(rows) is not None: continue
    rowsets.append(rows); params.append(c)
print(len(rowsets), 'legal approach candidates', flush=True)
t0 = time.time()
contacts = {}
STOPA = [(0x8C, '==', 32), (0x80, '==', 12), (0x80, '==', 10), (0x5C, '==', 0)]
for i in range(0, len(rowsets), CH):
    res = fc.run_batch('s0', rowsets[i:i + CH], record='last', stops=STOPA)
    for rows, p, r in zip(rowsets[i:i + CH], params[i:i + CH], res):
        if not r.states: continue
        s = r.states[-1]; ci = r.rows_played - 1
        if not (s['coll'] == 32 or s['anim'] in (10, 12) or s['c5'] == 0): continue
        if s['c5'] == 0:
            k = ('T', ci, s['hp'])
            if k not in contacts: contacts[k] = (ci + 1, rows[:ci + 1], p, s, 0)
            continue
        if s['hp'] == 0 or s['it'] != 133 or s['np'] < NPMIN or s['st'] != 9: continue
        est = ci + 1 + max(0, s['y'] - 84) / 1.8
        k = (ci, s['y'], s['x'], s['vy'], s['anim'], s['coll'], s['hp'],
             tuple((s[f'ex{q}'], s[f'ey{q}']) for q in range(8)))
        if k not in contacts or contacts[k][4] > est:
            contacts[k] = (ci + 1, rows[:ci + 1], p, s, est)
print(len(contacts), 'distinct contacts', f'{time.time() - t0:.0f}s', flush=True)
direct = [v for k, v in contacts.items() if k[0] == 'T']
ranked = sorted((v for k, v in contacts.items() if k[0] != 'T'), key=lambda v: (v[4], -v[3]['hp']))[:TOP]
CYC = spec('ALU AL R RU RU')
climbs = []
for d in range(0, 7):
    for pre in ('RU', 'R'):
        for start in range(5):
            rows = spec(f'{pre}:{d}') if d else []
            rows += (CYC[start:] + CYC * 30)
            climbs.append(rows[:H])
climbs.append(spec('RU:%d' % H))
results = []
for v in direct:
    results.append((v[0], v[3]['hp'], v[1], v[2], 'direct'))
for n, (c, arows, p, s, est) in enumerate(ranked):
    r = fc.run_batch('s0', [arows], record='last', keep=True, prefix='ap')[0]
    L1 = L0.after(arows)
    ok = [cl for cl in climbs if L1.check(cl) is None]
    best = None
    for i in range(0, len(ok), CH):
        res = fc.run_batch(r.slot, ok[i:i + CH], record='last', stops=[(0x5C, '==', 0)])
        for cl, rr in zip(ok[i:i + CH], res):
            if not rr.states: continue
            s2 = rr.states[-1]; ti = rr.rows_played - 1
            if s2['c5'] != 0: continue
            if s2['np'] < NPMIN or s2['it'] != 133: continue
            tot = c + ti + 1
            if best is None or (tot, -s2['hp']) < (best[0], -best[1]):
                best = (tot, s2['hp'], arows + cl[:ti + 1], p, 'contact +%d y %d hp %d est %.1f' % (c, s['y'], s['hp'], est))
    fc.drop('ap1')
    if best: results.append(best)
results.sort(key=lambda z: (z[0], -z[1]))
print(f'{time.time() - t0:.0f}s; best triggers:')
for z in results[:15]:
    print(' trig', S + z[0], f'(+{z[0]})', 'hp', z[1], 'params', z[3], z[4], '|', ' '.join(short(r) for r in z[2][-14:]))
if TAG and results:
    import json
    with open(f'work/l42w/we_{TAG}_top.json', 'w') as fh:
        json.dump([{'trigger': S + z[0], 'hp': z[1], 'params': str(z[3]), 'rows': ['+'.join(r) for r in PR + z[2]]} for z in results[:40]], fh)
    C.write_inputs(f'work/l42w/we_{TAG}.inputs.txt', PR + results[0][2],
                   f'wenum {MST} {F0} trigger {S + results[0][0]} hp {results[0][1]}')
    byhp = {}
    for z in results:
        if z[1] not in byhp: byhp[z[1]] = z
    for hp, z in sorted(byhp.items()):
        C.write_inputs(f'work/l42w/we_{TAG}_h{hp}.inputs.txt', PR + z[2], f'wenum {MST} {F0} trigger {S + z[0]} hp {hp}')
        print(' best hp', hp, 'trigger', S + z[0], z[3], z[4])
fc.close()
