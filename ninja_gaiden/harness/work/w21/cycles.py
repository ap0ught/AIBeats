"""Enumerate legal repeating wall-climb cycles and measure them on Mesen.
    python -u work/w21/cycles.py <mst> "<preamble spec>" <side R|L> <frames> [--nmin 5 --nmax 9] [--top 25]
side = the wall's side (R: wall on Ryu's right). Cycle = direction pattern (runs >= 2, cyclic; toward/away/none)
x A pattern (A always held, or one A press of 2..n-2 frames per cycle) x phase. Score = height gained after <frames>
frames while staying near the wall."""
import sys, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'work/w21')
from ng.solve import common as C
from ng import fastcore as F
from try_ import spec_rows

def legal_seq(rows, pre=()):
    allr = list(pre) + list(rows)
    for b in ('A', 'Left', 'Right', 'Up', 'Down', 'B'):
        last = -99; held = False; run = 0
        for t, r in enumerate(allr):
            h = b in r
            if h and not held:
                if t - last < 5 or (run < 2 and last > -99): return False
                last = t; held = True; run = 1
            elif h: run += 1
            elif held:
                if run < 2: return False
                held = False; run = 1
            else: run += 1
        if 'Left' in r and 'Right' in r: pass
    for r in allr:
        if ('Left' in r and 'Right' in r) or ('Up' in r and 'Down' in r): return False
    return True

def dir_patterns(n):
    """cyclic sequences over {T(oward), W(away), N} with every run >= 2 (cyclically)"""
    out = set()
    for seq in itertools.product('TWN', repeat=n):
        if len(set(seq)) == 1: continue
        # runs cyclic
        s = ''.join(seq)
        # rotate so it starts at a run boundary
        k = next((i for i in range(n) if s[i] != s[i - 1]), None)
        if k is None: continue
        r = s[k:] + s[:k]
        runs = [len(list(g)) for _, g in itertools.groupby(r)]
        if min(runs) < 2: continue
        out.add(s)
    return sorted(out)

if __name__ == '__main__':
    a = sys.argv[1:]
    def opt(n, d):
        if n in a:
            i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
        return d
    UP = '--up' in a
    a = [x for x in a if x != '--up']
    nmin = opt('--nmin', 5); nmax = opt('--nmax', 9); top = opt('--top', 25)
    mst, pre, side, NF = a[0], a[1], a[2], int(a[3])
    T, W = ('Right', 'Left') if side == 'R' else ('Left', 'Right')
    prer = spec_rows(pre)
    cands = []; desc = []
    for n in range(nmin, nmax + 1):
        for dp in dir_patterns(n):
            apats = [('Aall', [True] * n)]
            for k in range(2, n - 1):
                for ph in range(n):
                    ap = [((i - ph) % n) < k for i in range(n)]
                    apats.append((f'A{k}@{ph}', ap))
            upats = [('', [False] * n)]
            if UP:
                for k in (2, 3):
                    for ph in range(n):
                        upats.append((f'U{k}@{ph}', [((i - ph) % n) < k for i in range(n)]))
            for (an, ap), (un, up) in itertools.product(apats, upats):
                an = an + un
                cyc = []
                for d, aon, uon in zip(dp, ap, up):
                    r = ['Up'] if uon else []
                    if d == 'T': r.append(T)
                    if d == 'W': r.append(W)
                    if aon: r.append('A')
                    cyc.append(tuple(sorted(r)))
                rows = (cyc * (NF // n + 2))[:NF]
                if not legal_seq(rows, prer): continue
                cands.append(prer + rows); desc.append((n, dp, an, cyc))
    print(len(cands), 'legal cycles', flush=True)
    P = F.FastPool(2, boot_rows=None, ticks=True)
    data = open(mst, 'rb').read()
    for w in P.workers: w.put('s', data)
    from ng.solve import fast as FS
    res = FS.run_chunked(P, 's', cands, chunk=12, record='all', log=lambda s: None)
    P.close()
    ab = {'Right': 'R', 'Left': 'L', 'A': 'A', 'Up': 'U'}
    sc = []
    y0 = None
    for d, r in zip(desc, res):
        if r is None: continue
        st = r.states
        if not st: continue
        if y0 is None: y0 = st[len(prer) - 1]['y'] if prer else st[0]['y']
        ys = [s['y'] for s in st[len(prer):]]
        last = st[-1]
        dead = any(s['hp'] == 0 or s['y'] >= 240 for s in st)
        if dead: continue
        sc.append((last['y'], min(ys), d, C.abs_x(last), last['coll'], last['room']))
    sc.sort(key=lambda z: (z[0], z[1]))
    for z in sc[:top]:
        n, dp, an, cyc = z[2]
        print(f"y_end {z[0]} y_min {z[1]} X {z[3]} coll {z[4]} room {z[5]} n {n} cycle {' '.join(''.join(ab[b] for b in r) or '-' for r in cyc)} ({an})")
