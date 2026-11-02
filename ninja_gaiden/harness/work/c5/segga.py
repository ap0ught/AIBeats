"""Segment optimizer on Mesen: mutation search over wanted rows, legal by construction (Enforcer on the power-on
history), goal = earliest row reaching a room / a position / the next stage.
    python -u work/c5/segga.py <hist file> <mesen state .mst> <seed rows> <goal> <out tag> [opts]
goal: room:R | x:R:le|ge:GX[:ylo:yhi] | stage
opts: --mins 30 --workers 2 --batch 48 --pop 16 --minhp 1 --item 133 --npb 0 (frames bonus per ninpo) --npcap 10
      --npmin 0 (hard minimum ninpo at the goal) --noub (no Up+B added) --extra 30 (rows past the seed) --rseed 1
      --focus a-b (mutate only rows a..b) --cut N (only the first N seed rows)
Out: states/tmp/c5_<tag>.inputs.txt (legal rows to the goal, history excluded), states/mesen/c5_<tag>.mst (+.frame),
     states/tmp/c5_<tag>.json. Mesen numbers are CANDIDATES: verify on NesHawk."""
import json
import os
import random
import sys
import time

sys.path.insert(0, '.')
from ng.solve import common as C, legality as L, fast as FS  # noqa: E402
from ng import fastcore as F  # noqa: E402

a = sys.argv[1:]


def opt(n, d, flag=False):
    if n in a:
        i = a.index(n)
        if flag:
            del a[i]
            return True
        v = a[i + 1]
        del a[i:i + 2]
        return v
    return d


MINS = float(opt('--mins', 30))
NW = int(opt('--workers', 2))
NB = int(opt('--batch', 48))
POP = int(opt('--pop', 16))
MINHP = int(opt('--minhp', 1))
ITEM = opt('--item', None)
NPB = float(opt('--npb', 0))
NPCAP = int(opt('--npcap', 10))
NPMIN = int(opt('--npmin', 0))
NOUB = opt('--noub', False, True)
EXTRA = int(opt('--extra', 30))
RS = int(opt('--rseed', 1))
FOCUS = opt('--focus', None)
PDIR = opt('--pdir', 'le')
CUT = opt('--cut', None)
hf, mst, seedf, goal, tag = a[:5]
random.seed(RS)
hist = C.rows_of(hf)
seed = C.rows_of(seedf)
if CUT:
    seed = seed[:int(CUT)]
H = len(seed) + EXTRA
fa, fb = (0, H) if not FOCUS else tuple(int(x) for x in FOCUS.split('-'))
g = goal.split(':')
stops = [(0x6D, 'changed', 0), (0x65, '==', 0)]
if g[0] == 'room':
    stops.append((0x6E, '==', int(g[1])))


def reached(s):
    if g[0] == 'room':
        return s['room'] == int(g[1])
    R, cmp_, gx = int(g[1]), g[2], int(g[3])
    if s['room'] != R:
        return False
    x = C.abs_x(s)
    ok = x <= gx if cmp_ == 'le' else x >= gx
    if ok and len(g) > 4:
        ok = int(g[4]) <= s['y'] <= int(g[5])
    return ok


def evaluate(r, st0):
    sts = r.states
    minhp = 99
    for i, s in enumerate(sts):
        minhp = min(minhp, s['hp'])
        if s['hp'] == 0 or (s['dead'] & 0x80):
            return (9, 0, 0), None
        if g[0] == 'stage':
            hit = s['stage'] != st0
        else:
            if s['stage'] != st0:
                return (9, 0, 0), None
            hit = reached(s)
        if hit:
            if minhp < MINHP or (ITEM and s['item'] != int(ITEM)) or s['ninpo'] < NPMIN:
                return (5, i, 0), None
            return (0, i - NPB * min(s['ninpo'], NPCAP), -minhp), i
    s = sts[-1] if sts else None
    prog = 0
    if s and g[0] == 'x' and s['room'] == int(g[1]):
        x = C.abs_x(s)
        prog = (int(g[3]) - x) if g[2] == 'ge' else (x - int(g[3]))
    elif s and g[0] in ('room', 'stage'):
        x = C.abs_x(s)
        prog = (x if PDIR == 'le' else -x) + 4000 * (1 if s['stage'] == st0 and s['room'] != R0 + 0 else 0) * 0
        if g[0] == 'room' and s['room'] == int(g[1]):
            prog = -9999
    return (1, prog, -minhp), None


def dir_of(r):
    return tuple(b for b in r if b in ('Left', 'Right'))


def norm(rows):
    rows = [tuple(sorted(set(r))) for r in rows][:H]
    return rows + [rows[-1] if rows else ()] * (H - len(rows))


def mutate(w):
    w = list(w)
    for _ in range(random.choice([1, 1, 1, 2, 3])):
        op = random.random()
        k = random.randrange(fa, max(fa + 1, min(fb, H - 2)))
        if op < 0.30:
            if random.random() < 0.6:
                del w[k]
                w.append(w[-1])
            else:
                w.insert(k, w[k])
                w.pop()
        elif op < 0.50:
            kinds = ['B', 'DB', 'A', 'A', 'X'] + ([] if NOUB else ['UB'])
            kind = random.choice(kinds)
            d = dir_of(w[k])
            if kind == 'X':
                btn = random.choice(['A', 'B'])
                for j in range(k, min(H, k + random.randint(1, 3))):
                    w[j] = tuple(b for b in w[j] if b != btn)
                continue
            add = {'B': ('B',) + d, 'DB': ('Down', 'B') + d, 'UB': ('Up', 'B'), 'A': ('A',) + d}[kind]
            for j in (k, k + 1):
                w[j] = tuple(sorted(set(add) | (set() if kind == 'UB' else set(w[j]) - {'Up', 'Down'})))
        elif op < 0.62:
            for j in range(k, min(H, k + random.randint(1, 4))):
                w[j] = dir_of(w[j])
        elif op < 0.80:
            Ln = random.randint(1, 12)
            d = random.choice([('Left',), ('Right',), ()])
            for j in range(k, min(H, k + Ln)):
                keep = tuple(b for b in w[j] if b not in ('Left', 'Right'))
                if 'Up' in keep and 'B' in keep:
                    continue
                w[j] = tuple(sorted(set(keep) | set(d)))
        elif op < 0.90:
            j = k
            if 'A' in w[j]:
                if random.random() < 0.5 and j + 1 < H:
                    w[j + 1] = tuple(sorted(set(w[j + 1]) | {'A'}))
                else:
                    while j + 1 < H and 'A' in w[j + 1]:
                        j += 1
                    w[j] = tuple(b for b in w[j] if b != 'A')
        else:
            s = random.choice([-3, -2, -1, 1, 2, 3])
            j = min(H - 1, max(0, k + s))
            w[k], w[j] = w[j], w[k]
    return norm(w)


base = L.Enforcer(hist[-1900:])
def boot():
    P = F.FastPool(NW, boot_rows=None, ticks=True)
    data = open(mst, 'rb').read()
    P.put_all('s', data)
    for wk in P.workers:
        wk.load('s')
    return P


P = boot()
ram0 = P.workers[0].ram()
st0 = ram0[0x6D]
R0 = ram0[0x6E]
f0 = int(open(mst + '.frame').read()) if os.path.exists(mst + '.frame') else None
assert f0 is None or f0 == len(hist), (f0, len(hist))
print(f"segga {tag}: start frame {f0} stage {st0} room {ram0[0x6E]} goal {goal} H {H} seed {len(seed)}", flush=True)


def legal(w):
    en = base.copy()
    out = []
    for x in w:
        if NOUB and 'Up' in x and 'B' in x:
            x = tuple(b for b in x if b != 'Up')
        out.append(en.emit(x))
    return out


pop, seen, best = [], set(), None
t0 = time.time()
cands = [norm(seed)]
while len(cands) < NB:
    cands.append(mutate(norm(seed)))
gen = 0
while time.time() - t0 < MINS * 60:
    cands = [c for c in cands if tuple(c) not in seen]
    for c in cands:
        seen.add(tuple(c))
    legs = [legal(c) for c in cands]
    res = FS.run_chunked(P, 's', legs, chunk=24, log=lambda s: None, record='all', stops=stops, reboot=boot)
    P = FS.run_chunked.pool
    for w, lg, r in zip(cands, legs, res):
        k, i = evaluate(r, st0)
        pop.append((k, w, lg, i))
    pop.sort(key=lambda p: p[0])
    newpop, ks = [], {}
    for p in pop:
        if ks.get(p[0], 0) < 2:
            newpop.append(p)
            ks[p[0]] = ks.get(p[0], 0) + 1
        if len(newpop) >= POP:
            break
    pop = newpop
    if best is None or pop[0][0] < best[0]:
        best = pop[0]
        k, w, lg, i = best
        if i is not None:
            C.write_inputs(f'states/tmp/c5_{tag}.inputs.txt', lg[:i + 1], f'segga {tag} goal {goal} key {k} (Mesen; verify)')
            C.write_inputs(f'states/tmp/c5_{tag}.want.txt', w[:i + 1], f'segga {tag} wanted rows')
        print(f"{time.time()-t0:6.0f}s gen {gen} BEST {k} reach {i}", flush=True)
    gen += 1
    if gen % 10 == 0:
        print(f"{time.time()-t0:6.0f}s gen {gen} seen {len(seen)} top {[p[0] for p in pop[:3]]}", flush=True)
    cands = []
    while len(cands) < NB:
        j = min(int(random.expovariate(0.4)), len(pop) - 1)
        cands.append(mutate(pop[j][1]))
k, w, lg, i = best
if i is not None:
    wk = P.workers[0]
    wk.load('s')
    _, recs, _ = wk.step(lg[:i + 1], record='last')
    wk.save('end')
    fr = (f0 + i + 1) if f0 is not None else None
    wk.save_file('end', f'states/mesen/c5_{tag}.mst', fr)
    s = recs[-1]
    info = dict(tag=tag, goal=goal, key=list(k), rows=i + 1, end_frame=fr, hp=s['hp'], ninpo=s['ninpo'], item=s['item'],
                room=s['room'], x=C.abs_x(s), y=s['y'])
    json.dump(info, open(f'states/tmp/c5_{tag}.json', 'w'))
    print('END', json.dumps(info), flush=True)
P.close()
