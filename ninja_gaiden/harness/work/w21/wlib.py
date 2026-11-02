"""wall-agent helpers: candidate evaluation on Mesen (<= 2 workers), spec parsing, legality."""
import sys, time
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F
MAP = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}
AB = {'Right': 'R', 'Left': 'L', 'Up': 'U', 'Down': 'D', 'A': 'A', 'B': 'B'}


def spec(s):
    out = []
    for tok in s.split():
        k, n = tok.split(':') if ':' in tok else (tok, '1')
        out += [tuple(sorted(MAP[c] for c in k if c != '-'))] * int(n)
    return out


def fmt(rows):
    out = []; prev = None; n = 0
    for r in rows:
        k = ''.join(AB[b] for b in r) or '-'
        if k == prev: n += 1
        else:
            if prev is not None: out.append(f'{prev}:{n}')
            prev, n = k, 1
    if prev is not None: out.append(f'{prev}:{n}')
    return ' '.join(out)


def legal(want, hist):
    en = L.Enforcer(list(hist)[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]


def pool(mst, n=2):
    P = F.FastPool(n, boot_rows=None, ticks=True)
    d = open(mst, 'rb').read()
    for w in P.workers: w.put('s', d)
    return P


def run(P, cands, stops=((0x65, '==', 0),), log=False):
    L0 = max(len(c) for c in cands)
    ch = max(2, 2 * (500 // max(1, L0)))
    return FS.run_chunked(P, 's', cands, chunk=ch, record='all', stops=list(stops),
                          log=(lambda s: print(s, flush=True)) if log else (lambda s: None))


def first(res, goal):
    """index of the first state satisfying goal (or None), stopping at death"""
    if res is None: return None
    for i, s in enumerate(res.states):
        if s['hp'] == 0 or (s['dead'] & 0x80): return None
        if goal(s): return i
    return None


def search(mst, hist, wants, goal, labels=None, top=10, n=2, minhp=0):
    """legalize every wanted list on hist, run, return sorted [(goal index, -hp, label, legal rows, state)]"""
    seen = {}; cands = []; labs = []
    for i, w in enumerate(wants):
        lg = tuple(legal(w, hist))
        if lg in seen: continue
        seen[lg] = 1; cands.append(list(lg)); labs.append(labels[i] if labels else i)
    t0 = time.time()
    P = pool(mst, n)
    try:
        res = run(P, cands)
    finally:
        P.close()
    out = []
    for c, lb, r in zip(cands, labs, res):
        k = first(r, goal)
        if k is None: continue
        s = r.states[k]
        if s['hp'] < minhp: continue
        out.append((k, -s['hp'], -s['ninpo'], lb, c[:k + 1], s))
    out.sort(key=lambda z: z[:3])
    print(f'search: {len(cands)} unique, {len(out)} reach, {time.time()-t0:.0f}s', flush=True)
    for z in out[:top]:
        s = z[5]
        print(f'  {z[0]+1} rows  {z[3]}  X {C.abs_x(s)} y {s["y"]} hp {s["hp"]} np {s["ninpo"]}', flush=True)
    return out
