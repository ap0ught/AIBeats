"""3-3 event-genome GA on Mesen (legal by Enforcer).  python -u work/l33/ga.py <tag> <out tag> [--mins 40] [--H 175]
    [--seed f1,f2] (event files from earlier runs, json) [--rseed 1] [--lam 48] [--mu 12]
Genome = sorted events (t, kind, arg): d = held direction from t (arg Left/Right/None), a = jump (A 2 f + dir),
b = slash (B 2 f + dir), w = Fire Wheel (Up+B 2 f, dir released), k = Down+B slash.
Fitness = M = kill row + 3*(timer + ninpo) if killed, else 1000 + 40*boss hp + last hit row / 10.
Out: work/l33/ga_<out>.json (best genome + legal rows) and work/l33/ga_<out>.inputs.txt (legal rows to the kill)."""
import sys, json, random, time
sys.path.insert(0, 'work/l33')
from sw import Ctx, C
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
MINS = opt('--mins', 40.0); H = opt('--H', 175); SEEDS = opt('--seed', ''); RS = opt('--rseed', 1)
LAM = opt('--lam', 48); MU = opt('--mu', 12); TMAX = opt('--tmax', 0); TMIN = opt('--tmin', 0)
tag, out = a[:2]
random.seed(RS)
DIRS = ['Left', 'Right', None]


def decode(g):
    rows = [()] * H
    ev = sorted(g, key=lambda e: (e[0], e[1] != 'd'))
    d = 'Right'   # control: Ryu moving right
    dirs = [None] * H
    di = 0
    evd = [e for e in ev if e[1] == 'd']
    for t in range(H):
        while di < len(evd) and evd[di][0] <= t:
            d = evd[di][2]; di += 1
        dirs[t] = d
    rows = [set([dirs[t]]) if dirs[t] else set() for t in range(H)]
    for t, k, arg in ev:
        if k == 'd' or t >= H: continue
        for j in (t, t + 1):
            if j >= H: continue
            if k == 'a': rows[j] |= {'A'}
            elif k == 'b': rows[j] |= {'B'}
            elif k == 'k': rows[j] |= {'B', 'Down'}
            elif k == 'w': rows[j] = {'Up', 'B'} | (rows[j] & {'A'})
    return [tuple(sorted(r)) for r in rows]


def mutate(g):
    fixed = [e for e in g if e[0] < TMIN]
    g = [e for e in g if e[0] >= TMIN]
    g2 = _mutate(g)
    return sorted(set(fixed + [e for e in g2 if e[0] >= TMIN]), key=lambda e: (e[0], e[1], str(e[2])))


def _mutate(g):
    g = list(g)
    for _ in range(random.choice([1, 1, 1, 2, 2, 3])):
        op = random.random()
        if op < 0.30 and g:
            i = random.randrange(len(g)); t, k, x = g[i]
            g[i] = (max(0, min(H - 2, t + random.choice([-3, -2, -1, -1, 1, 1, 2, 3, 5, -5]))), k, x)
        elif op < 0.42 and g:
            i = random.randrange(len(g)); t, k, x = g[i]
            if k == 'd': g[i] = (t, k, random.choice(DIRS))
            else: g[i] = (t, random.choice('abwk'), x)
        elif op < 0.54 and g:
            del g[random.randrange(len(g))]
        elif op < 0.78:
            t = random.randrange(TMIN, TMAX or H - 2)
            k = random.choice('ddabbwwk')
            g.append((t, k, random.choice(DIRS) if k == 'd' else None))
        else:                                    # time warp after t
            t0 = random.randrange(TMIN, H - 2); dt = random.choice([-3, -2, -1, 1, 2, 3])
            g = [(max(0, min(H - 2, t + dt)) if t >= t0 else t, k, x) for t, k, x in g]
    return sorted(set(g), key=lambda e: (e[0], e[1], str(e[2])))


def fit(r):
    if r['M'] is not None:
        return r['M']
    last = r['hits'][-1][0] if r['hits'] else H
    return 1000 + 40 * r['boss'] + last / 10.0 + (0 if r['hp'] > 0 else 500)


def from_rows(rows):
    """rows (wanted) -> events (presses where a button starts; direction changes)."""
    g = []
    prev = set(); pd = 'Right'
    for t, r in enumerate(rows):
        r = set(r)
        d = 'Left' if 'Left' in r else ('Right' if 'Right' in r else None)
        if 'Up' in r and 'B' in r:
            if 'B' not in prev: g.append((t, 'w', None))
        else:
            if d != pd: g.append((t, 'd', d)); pd = d
            if 'B' in r and 'B' not in prev: g.append((t, 'k' if 'Down' in r else 'b', None))
        if 'A' in r and 'A' not in prev: g.append((t, 'a', None))
        prev = r
    return g


X = Ctx(tag)
pop = []
seeds = []
for f in [s for s in SEEDS.split(',') if s]:
    if f.endswith('.json'):
        seeds.append([tuple(e) for e in json.load(open(f))['genome']])
    else:
        seeds.append(from_rows(C.rows_of(f)))
if not seeds:
    seeds = [[]]
res = X.run([decode(g) for g in seeds])
pop = sorted([(fit(r), g, r) for g, r in zip(seeds, res)], key=lambda p: p[0])
print('seeds', [round(p[0], 1) for p in pop], flush=True)
best = pop[0]
t0 = time.time(); gen = 0
def save(b):
    json.dump(dict(fit=b[0], genome=b[1], rows=['+'.join(x) for x in b[2]['rows']], kill=b[2]['kill'], M=b[2]['M'],
                   boss=b[2]['boss'], hits=b[2]['hits'], np=b[2]['np'], hp=b[2]['hp']), open(f'work/l33/ga_{out}.json', 'w'))
    if b[2]['kill']:
        C.write_inputs(f'work/l33/ga_{out}.inputs.txt', b[2]['rows'], f'ga {tag} kill row {b[2]["kill"]} M {b[2]["M"]}')
save(best)
while time.time() - t0 < MINS * 60:
    gen += 1
    kids = []
    for _ in range(LAM):
        p = min(random.sample(pop, min(3, len(pop))), key=lambda q: q[0])
        kids.append(mutate(p[1]))
    res = X.run([decode(g) for g in kids])
    allp = pop + [(fit(r), g, r) for g, r in zip(kids, res)]
    allp.sort(key=lambda q: q[0])
    nxt, seen = [], set()
    for q in allp:
        key = tuple(q[2]['rows'])
        if key in seen: continue
        seen.add(key); nxt.append(q)
        if len(nxt) >= MU: break
    pop = nxt
    if pop[0][0] < best[0]:
        best = pop[0]; save(best)
        print(f'{time.time()-t0:5.0f}s gen {gen} NEW fit {best[0]:.1f} kill {best[2]["kill"]} boss {best[2]["boss"]} np {best[2]["np"]} hp {best[2]["hp"]} hits {best[2]["hits"][-3:]}', flush=True)
    elif gen % 10 == 0:
        print(f'{time.time()-t0:5.0f}s gen {gen} best {best[0]:.1f} pop {[round(q[0]) for q in pop[:6]]}', flush=True)
X.close()
print('DONE best', best[0], 'kill', best[2]['kill'])
