"""Wait-for-the-enemy search (Mesen): Right held, one stop (no Right) of w frames starting at frame a, then the jump
off the post on any frame Ryu stands on it (y 176), Right to the ladder contact, then the standard ladder climbs.
Finds whether waiting lets a trailing enemy (bird / type 13) boost Ryu up the wall for a net gain.
python -u work/l42w/wpause.py <mst> <frame> --hist h [--a 0:44:2] [--w 2:42:2] [--h 110] [--tag t]"""
import sys, time, json
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


HIST = opt('--hist', ''); AR = opt('--a', '0:44:2'); WR = opt('--w', '2:42:2'); H = opt('--h', 110); TAG = opt('--tag', '')
CH = opt('--chunk', 40); POSTY = opt('--posty', 176)
MST, F0 = a[0], int(a[1])
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s0', open(MST, 'rb').read()); fc._ka_slot = 's0'
hist = [tuple(r) for r in C.rows_of(HIST)][-400:] if HIST else [()] * 30
L0 = LegState(hist)
R = ('Right',)
t0 = time.time()
base = []
for aa in range(*map(int, AR.split(':'))):
    for w in [0] + list(range(*map(int, WR.split(':')))):
        if w == 0 and aa: continue
        rows = [R] * aa + [()] * w + [R] * (H - aa - w)
        base.append((aa, w, rows))
cands = []
for i in range(0, len(base), CH):
    res = fc.run_batch('s0', [b[2] for b in base[i:i + CH]], record='all')
    for (aa, w, rows), r in zip(base[i:i + CH], res):
        post = [k for k, s in enumerate(r.states) if s['y'] == POSTY and s['coll'] & 0x10]
        for j in post:
            if j < aa + w and j >= aa: continue  # jump during the stop: keep (A only) as well
            v = list(rows)
            for k in (j, j + 1):
                if k < H: v[k] = ('A', 'Right')
            if L0.check(v) is None: cands.append((aa, w, j, v))
        for j in post:
            if aa <= j < aa + w:
                v = list(rows)
                for k in (j, j + 1):
                    if k < H: v[k] = ('A',) if k < aa + w else ('A', 'Right')
                if L0.check(v) is None: cands.append((aa, w, j, v))
print(len(base), 'stop variants,', len(cands), 'jump candidates', f'{time.time() - t0:.0f}s', flush=True)
STOPA = [(0x8C, '==', 32), (0x80, '==', 12), (0x80, '==', 10), (0x5C, '==', 0)]
contacts = {}
for i in range(0, len(cands), CH):
    res = fc.run_batch('s0', [c[3] for c in cands[i:i + CH]], record='last', stops=STOPA)
    for c, r in zip(cands[i:i + CH], res):
        if not r.states: continue
        s = r.states[-1]; ci = r.rows_played - 1
        if not (s['coll'] == 32 or s['anim'] in (10, 12) or s['c5'] == 0): continue
        if s['hp'] == 0 or s['np'] < 10 or s['it'] != 133: continue
        est = ci + 1 + max(0, s['y'] - 84) / 1.8
        k = (ci, s['y'], s['x'], s['anim'], s['hp'])
        if k not in contacts or contacts[k][0] > est: contacts[k] = (est, ci + 1, c, s)
print(len(contacts), 'contacts', f'{time.time() - t0:.0f}s', flush=True)
CYC = spec('ALU AL R RU RU')
climbs = []
for d in range(0, 5):
    for pre in ('RU', 'R'):
        for st in range(5):
            climbs.append(((spec(f'{pre}:{d}') if d else []) + CYC[st:] + CYC * 15)[:60])
climbs += [spec('AL:2 -:1 R:3 AL:2 R:30'), spec('AL:2 R:3 AL:2 R:30'), spec('AL:2 -:1 R:3 AL:2 -:1 R:3 AL:2 R:30')]
results = []
for est, n, c, s in sorted(contacts.values(), key=lambda v: v[0])[:60]:
    arows = c[3][:n]
    r = fc.run_batch('s0', [arows], record='last', keep=True, prefix='ap')[0]
    L1 = L0.after(arows)
    ok = [cl for cl in climbs if L1.check(cl) is None]
    res = fc.run_batch(r.slot, ok, record='last', stops=[(0x5C, '==', 0)])
    best = None
    for cl, rr in zip(ok, res):
        if rr.states and rr.states[-1]['c5'] == 0:
            t = n + rr.rows_played
            if best is None or t < best[0]: best = (t, rr.states[-1]['hp'], arows + cl[:rr.rows_played])
    fc.drop('ap1')
    if best: results.append((F0 + best[0], best[1], c[0], c[1], c[2], n, s['y'], s['hp'], best[2]))
results.sort(key=lambda z: (z[0], -z[1]))
print(f'{time.time() - t0:.0f}s best: (trigger, hp, stop at, stop len, jump at, contact+, contact y, hp at contact)')
for z in results[:20]: print(' ', z[:8])
if TAG and results:
    json.dump([{'trigger': z[0], 'hp': z[1], 'params': str(z[2:8]), 'rows': ['+'.join(r) for r in z[8]]} for z in results[:40]],
              open(f'work/l42w/wp_{TAG}_top.json', 'w'))
fc.close()
