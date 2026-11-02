"""Extend sync with the TAS by editing B presses (free air slashes) in the legalized TAS rows.
python -u work/l31t/sync.py <prefix stage rows | -> <k0> <N> "<edit spec>" [--pairs] [--top 10] [--out f] [--tol 0]
  prefix = our stage rows from 3-1 control (legal, played first); then TAS rows TR[k0:k0+N] (TR[k] = input of TAS frame k+1).
  edit spec: 'B:a-b' = add B on rows j, j+1 (row index in the TAS part) for j in a..b; 'xB:a-b' = also allow removing
  the TAS's own B rows in a..b+1 (variants); 'U:a-b' adds Up+B (throw) on row j only (Right released j-1..j by the
  legalizer is NOT automatic: the row is replaced by Up+B and row j+1 by '-'), 'J:a-b' shifts... (not yet).
  Score: rows in sync (X exact, y exact, hp >= TAS hp), then ninpo.
Out (--out): prefix + the best candidate cut at its last synced row."""
import sys, itertools
sys.path.insert(0, 'work/l31t'); sys.path.insert(0, '.')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
def flag(n):
    if n in a: a.remove(n); return True
    return False
top = opt('--top', 10); out = opt('--out', ''); tol = opt('--tol', 0); pairs = flag('--pairs'); npw = opt('--npw', 0)
pre = [] if a[0] == '-' else C.rows_of(a[0])
k0, N, spec = int(a[1]), int(a[2]), a[3]
base = [tuple(r) for r in TR[k0:k0 + N]]
edits = []  # list of functions row-list -> row-list
for tok in spec.split():
    kind, rng = tok.split(':'); lo, hi = map(int, rng.split('-'))
    for j in range(lo, hi + 1):
        if kind == 'B':
            edits.append(('B', j))
        elif kind == 'U':
            edits.append(('U', j))
        elif kind == 'xB':
            edits.append(('xB', j))
def apply(rows, ed):
    rows = list(rows)
    for kind, j in ed:
        if kind == 'B':
            for q in (j, j + 1):
                if q < len(rows): rows[q] = tuple(sorted(set(rows[q]) | {'B'}))
        elif kind == 'xB':
            if j < len(rows): rows[j] = tuple(x for x in rows[j] if x != 'B')
        elif kind == 'U':
            if j < len(rows): rows[j] = ('B', 'Up')
            if j + 1 < len(rows): rows[j + 1] = ()
            if j - 1 >= 0: rows[j - 1] = tuple(x for x in rows[j - 1] if x not in ('Right', 'Left'))
    return rows
cands_ed = [()] + [(e,) for e in edits]
if pairs:
    cands_ed += [(e1, e2) for e1, e2 in itertools.combinations(edits, 2) if abs(e1[1] - e2[1]) >= 2]
wanted = [apply(base, ed) for ed in cands_ed]
rows_c = [legal_after(pre, w) for w in wanted]
P = F.FastPool(2, boot_rows=None, ticks=True)
P.put_all('s', open(MST, 'rb').read())
for wk in P.workers: wk.load('s')
if pre:
    for wk in P.workers:
        wk.load('s'); wk.step(list(pre), record='last'); wk.save('p')
    slot = 'p'
else:
    slot = 's'
sys.path.insert(0, 'work/l11r')
from ng.solve import fast as FS
L0 = N
ch = max(2, 2 * (600 // max(1, L0)))
res = FS.run_chunked(P, slot, rows_c, chunk=ch, log=lambda s: None, record='all', stops=[(0x6D, 'changed', 0)])
P.close()
kb = k0  # TAS frame of state before row 0 of this part = k0 ; row i -> TAS frame k0+i+1
scored = []
for ci, r in enumerate(res):
    n = 0
    for i, s in enumerate(r.states):
        t = T[kb + i + 1]
        if abs(ax(s) - ax(t)) <= tol and s['y'] == t['y'] and s['hp'] >= t['hp'] and s['item'] in (0, 128, 129):
            n = i + 1
        else:
            break
    last = r.states[n - 1] if n else None
    scored.append((n, last['ninpo'] if last else 0, ci))
scored.sort(key=lambda q: (-(q[0] + npw * q[1]), q[2]))
for n, np_, ci in scored[:top]:
    s = res[ci].states[min(n, len(res[ci].states) - 1)]
    print(f"sync {n} np {np_} edits {cands_ed[ci]}  next: X {ax(s)} y {s['y']} hp {s['hp']} vs TAS X {ax(T[kb+n+1])} y {T[kb+n+1]['y']}")
if out:
    n, np_, ci = scored[0]
    C.write_inputs(out, list(pre) + rows_c[ci][:n], f'3-1 stage rows: prefix + legal TAS {k0}.. edits {cands_ed[ci]} sync {n}')
    print('wrote', out, len(pre) + n)
