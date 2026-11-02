"""Exhaustive structured ladder/wall climb from a state near the exit wall (Mesen).
Climb = first wait (0..W frames, each R / RU / - / U) + segments; segment = jump-off (A held ha frames with L or L+U,
ha in 2..3) + return (n frames of R or R+U, n in 1..5). Every legal sequence up to the trigger is run (stop at $5C=0).
python -u work/l42w/wclimb.py <mst> <frame> [--prefix rows] [--hist rows] [--w 4] [--nseg 4] [--tag t]"""
import sys, time, itertools
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


PRE = opt('--prefix', ''); HIST = opt('--hist', ''); W = opt('--w', 4); NSEG = opt('--nseg', 4); TAG = opt('--tag', '')
CH = opt('--chunk', 40); MAXF = opt('--maxf', 40)
MST, F0 = a[0], int(a[1])
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(MST, 'rb').read()); fc._ka_slot = 's'; fc.load('s')
hist = [tuple(r) for r in C.rows_of(HIST)][-400:] if HIST else [()] * 30
PR = [tuple(r) for r in C.rows_of(PRE)] if PRE else []
if PR: fc.step(PR, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); S = F0 + len(PR)
L0 = LegState(hist + PR)
print('start', S, 'X', r0[0x52] * 256 + r0[0x51] + r0[0x86], 'y', r0[0x8A], 'anim', r0[0x80], 'hp', r0[0x65], flush=True)
R, RU, N, U = ('Right',), ('Right', 'Up'), (), ('Up',)
AL, ALU = ('A', 'Left'), ('A', 'Left', 'Up')
waits = [()]
for w in range(1, W + 1):
    waits += list(itertools.product((R, RU, N, U), repeat=w))
jumps = []
for ha in (2, 3):
    for ups in itertools.product((False, True), repeat=ha):
        jumps.append(tuple(ALU if u else AL for u in ups))
rets = []
for n in range(1, 6):
    for k in range(n + 1):  # first k frames R, rest RU
        rets.append(tuple([R] * k + [RU] * (n - k)))
cands = set()
def grow(seq, nseg):
    if len(seq) >= MAXF or nseg == 0:
        cands.add(tuple(seq[:MAXF])); return
    for j in jumps:
        for r in rets:
            grow(seq + list(j) + list(r), nseg - 1)
for w in waits:
    for j in jumps:
        for r in rets:
            s = list(w) + list(j) + list(r)
            cands.add(tuple((s + [RU] * MAXF)[:MAXF]))
print('1-seg', len(cands), flush=True)
# deeper: greedy expansion of the best prefixes (beam over segment count)
def run(cs):
    out = []
    cs = [c for c in cs if L0.check(c) is None]
    for i in range(0, len(cs), CH):
        res = fc.run_batch('s0', [list(c) for c in cs[i:i + CH]], record='all', stops=[(0x5C, '==', 0)])
        for c, r in zip(cs[i:i + CH], res):
            out.append((c, r.states, r.rows_played))
    return out
t0 = time.time()
best = None; pool = sorted(cands)
for depth in range(NSEG):
    res = run(pool)
    scored = []
    for c, st, n in res:
        if st and st[-1]['c5'] == 0:
            if best is None or n < best[0]: best = (n, c[:n], st[-1]['hp'])
            continue
        # progress: min y reached while at the wall, per frame index
        ys = [s['y'] for s in st]
        scored.append((min(ys[:len(ys)]), c, st))
    print('depth', depth, 'ran', len(res), 'best', None if best is None else (S + best[0], best[2]), f'{time.time() - t0:.0f}s', flush=True)
    # extend: keep the 60 prefixes with the lowest y at a cut point, cut at each jump-off start after the 1st segment
    nxt = set()
    for cut in range(6, MAXF - 8, 1):
        bykey = {}
        for c, st, n in res:
            if len(st) <= cut: continue
            s = st[cut - 1]
            if s['c5'] == 0: continue
            k = (s['x'], s['y'], s['vy'], s['anim'], s['coll'], LegState(hist + PR + list(c[:cut])).st.__repr__())
            if k not in bykey: bykey[k] = c[:cut]
        for pre in list(bykey.values())[:400]:
            for j in jumps:
                for r in rets:
                    nxt.add(tuple((list(pre) + list(j) + list(r) + [RU] * MAXF)[:MAXF]))
    if depth + 1 < NSEG:
        pool = sorted(nxt - set(c for c, _, _ in res))
        if len(pool) > 20000: pool = pool[:20000]
print('BEST', None if best is None else ('trigger', S + best[0], 'hp', best[2], ' '.join(short(r) for r in best[1])))
if TAG and best:
    C.write_inputs(f'work/l42w/wc_{TAG}.inputs.txt', PR + list(best[1]), f'wclimb {MST} {F0} trigger {S + best[0]}')
fc.close()
