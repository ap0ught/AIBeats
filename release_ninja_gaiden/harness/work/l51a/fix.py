"""Greedy hit repair on legalized TAS rows (lag LG) after a prefix.
python -u work/l51a/fix.py <prefix> <N> <LG> <TAS END> <tag> [--npw px_per_5np] [--ov t:row,...] [--allow-hit tasframe]
Edits near the first unwanted hit: shift A/B presses, add B+Right / A+Right / blank x2 / Left x2. Score = no hit/death, then
X at END + npw * np/5. Writes work/l51a/fx_<tag>.txt (full stage rows) + prints the edit set."""
import sys, time; sys.path.insert(0, 'work/l51a')
from rep import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
NPW = opt('--npw', 4.5); OVS = opt('--ov', ''); ALLOWH = opt('--allow-hit', 0); WIN = opt('--win', 40); MAXIT = opt('--it', 12)
base = {int(k): set(row(v)) for k, v in (x.split(':') for x in OVS.split(','))} if OVS else {}
R = Rep(a[0], int(a[1]), int(a[2]), int(a[3]), base); TAG = a[4]
LG = R.LG
def ev(ov):
    r = R.run(ov)
    h = r['hit']
    if h and ALLOWH and h[0] - LG >= ALLOWH: h = None
    dead = r['dead'] is not None
    hf = h[0] if h else 10**6
    X = r['last'][1] if not dead else -1
    np_ = r['last'][4]
    return (not dead, hf, X + NPW * np_ / 5), r
def presses(ov, t0, t1):
    """TAS frames in [t0,t1] where A or B starts in the current wanted rows."""
    o = dict(base); o.update(ov); out = []
    prev = set()
    for t in range(t0 - 1, t1 + 1):
        w = set(o.get(t, T(t)))
        for b in ('A', 'B'):
            if b in w and b not in prev and t >= t0: out.append((t, b))
        prev = w
    return out
ov = {}
sc, r = ev(ov); t0 = time.time()
print('start', sc, r, flush=True)
for it in range(MAXIT):
    h = r['hit'] if r['hit'] and not (ALLOWH and r['hit'][0] - LG >= ALLOWH) else None
    d = r['dead']
    if not h and not d: break
    tf = (h or d)[0] - LG
    cands = []
    for (t, b) in presses(ov, tf - WIN, tf):
        for dd in (-4, -3, -2, -1, 1, 2, 3, 4, None):
            o = dict(ov); o[t] = set(o.get(t, T(t))) - {b}; o[t + 1] = set(o.get(t + 1, T(t + 1))) - {b}
            if dd is not None:
                o[t + dd] = set(o.get(t + dd, T(t + dd))) | {b}
            cands.append(o)
    for t in range(tf - WIN, tf + 1):
        for add in ({'B', 'Right'}, {'A', 'Right'}):
            o = dict(ov); o[t] = add; cands.append(o)
        for add in (set(), {'Left'}, {'B'}, {'B', 'Left'}):
            o = dict(ov); o[t] = set(add); o[t + 1] = set(add); cands.append(o)
    best = None
    for o in cands:
        s2, r2 = ev(o)
        if best is None or s2 > best[0]: best = (s2, o, r2)
    print(f'it {it}: first {"hit" if h else "dead"} TAS {tf} -> best {best[0]} {best[2]} ({len(cands)} cands, {time.time()-t0:.0f}s)', flush=True)
    if best[0] <= sc: print('no improvement'); break
    sc, ov, r = best
print('FINAL', sc, r, flush=True)
print('edits', {t: P(tuple(sorted(w))) for t, w in sorted(ov.items())}, flush=True)
rr = R.run(ov, keep=True)
print('legal', legal_ok(rr['rows']) or 'ok')
wr(f'work/l51a/fx_{TAG}.txt', rr['rows'], f'fix {sys.argv[1:]} edits {sorted((t, P(tuple(sorted(w)))) for t, w in ov.items())}')
