"""3-3 Basaquer: mutation search over wanted rows on Mesen (FastPool), legal by construction (Enforcer).
    python -u work/c5/b33ga.py <hist file> <mesen state> <out rows file> [--seed rows,rows2] [--H 140] [--mins 60]
Score: kill row (lower) / then boss HP left, hit times; min Ryu HP as tie-break; deaths discarded.
Writes the best LEGAL rows (Enforcer output) to <out> whenever it improves."""
import sys, random, time, json
sys.path.insert(0, '.'); sys.path.insert(0, 'work/c5')
from b33lib import Ctx
from ng.solve import common as C

a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return v
    return d
H = int(opt('--H', 140)); MINS = float(opt('--mins', 60)); seeds = opt('--seed', ''); POP = int(opt('--pop', 16))
NB = int(opt('--batch', 48)); NW = int(opt('--workers', 2)); minhp_req = int(opt('--minhp', 1)); rs = int(opt('--rseed', 1))
hf, mst, out = a[0], a[1], a[2]
random.seed(rs)
DIRS = [('Left',), ('Right',), ()]


def norm(rows):
    rows = [tuple(sorted(set(r))) for r in rows][:H]
    return rows + [()] * (H - len(rows))


def dir_of(r):
    return tuple(b for b in r if b in ('Left', 'Right'))


def mutate(w):
    w = list(w)
    for _ in range(random.choice([1, 1, 1, 2, 3])):
        op = random.random()
        k = random.randrange(0, H - 2)
        if op < 0.18:                       # time shift: delete or duplicate a row
            if random.random() < 0.5:
                del w[k]; w.append(())
            else:
                w.insert(k, w[k]); w.pop()
        elif op < 0.45:                     # add a 2-frame press
            kind = random.choice(['B', 'DB', 'UB', 'A', 'A'])
            d = dir_of(w[k])
            if kind == 'B':
                add = ('B',) + d
            elif kind == 'DB':
                add = ('Down', 'B') + d
            elif kind == 'UB':
                add = ('Up', 'B')
            else:
                add = ('A',) + d
            for j in (k, k + 1):
                w[j] = tuple(sorted(set(add) | (set() if kind == 'UB' else set(w[j]) - {'Up', 'Down'})))
        elif op < 0.6:                      # remove presses around k
            for j in range(k, min(H, k + random.randint(1, 4))):
                w[j] = dir_of(w[j])
        elif op < 0.85:                     # direction window
            L = random.randint(1, 20)
            d = random.choice(DIRS)
            for j in range(k, min(H, k + L)):
                keep = tuple(b for b in w[j] if b not in ('Left', 'Right'))
                if 'Up' in keep and 'B' in keep:
                    continue
                w[j] = tuple(sorted(set(keep) | set(d)))
        else:                               # move one press by +-1..4 (swap rows k and k+s)
            s = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            j = min(H - 1, max(0, k + s))
            w[k], w[j] = w[j], w[k]
    return norm(w)


def key(s):
    if s['dead'] or s['minhp'] < minhp_req:
        return (3, 0, 0, 0)
    if s['kill'] is not None:
        return (0, s['kill'], -s['minhp'], 0)
    return (1, s['left'], sum(i for i, _ in s['hits']) / max(1, len(s['hits'])), -s['minhp'])


ctx = Ctx(hf, mst, n=NW)
pop = []
seen = set()
init = [norm(C.rows_of(f)) for f in seeds.split(',') if f]
if not init:
    init = [norm([('Right',)] * 10)]
cands = list(init)
while len(cands) < NB:
    cands.append(mutate(random.choice(init)))
best = None
t0 = time.time()
gen = 0
while time.time() - t0 < MINS * 60:
    cands = [c for c in cands if tuple(c) not in seen]
    for c in cands:
        seen.add(tuple(c))
    res = ctx.run(cands)
    for w, (legal, s) in zip(cands, res):
        pop.append((key(s), w, legal, s))
    pop.sort(key=lambda p: p[0])
    # keep distinct keys mostly
    newpop, ks = [], {}
    for p in pop:
        if ks.get(p[0], 0) < 3:
            newpop.append(p); ks[p[0]] = ks.get(p[0], 0) + 1
        if len(newpop) >= POP:
            break
    pop = newpop
    if best is None or pop[0][0] < best[0]:
        best = pop[0]
        k, w, legal, s = best
        n = (s['kill'] + 1) if s['kill'] is not None else len(legal)
        C.write_inputs(out, legal[:n], f"b33ga best key {k} {json.dumps(s)[:300]}")
        print(f"{time.time()-t0:6.0f}s gen {gen} BEST {k} hits {s['hits']} minhp {s['minhp']}", flush=True)
    gen += 1
    if gen % 10 == 0:
        print(f"{time.time()-t0:6.0f}s gen {gen} seen {len(seen)} top {[p[0] for p in pop[:4]]}", flush=True)
    cands = []
    while len(cands) < NB:
        i = min(int(random.expovariate(0.35)), len(pop) - 1)
        cands.append(mutate(pop[i][1]))
ctx.close()
print("done", best[0])
