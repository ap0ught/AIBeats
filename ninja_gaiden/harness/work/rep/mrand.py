"""Random window search on Mesen: prefix (grammar with fixed lengths) + K random rows from an alphabet + tail.
    python -u work/rep/mrand.py <hist> <mst> "<prefix ROW*n;..>" "<alphabet R|L|A+R|...>" K N "<goal>" tag
       [--horizon 90] [--tail Right] [--minhp 0] [--npmin 0] [--seed 1] [--runs 1-4 (row repeat lengths)]
goal like mbrute. Prints the best, writes states/tmp/rep_<tag>.inputs.txt"""
import random, sys, time
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
H = opt('--horizon', 90); tail = opt('--tail', 'Right'); minhp = opt('--minhp', 0); npmin = opt('--npmin', 0)
random.seed(opt('--seed', 1)); runs = opt('--runs', '1-4')
r0, r1 = map(int, runs.split('-'))
hf, mst, pre, alph, K, N, goal, tag = a[:8]; K = int(K); N = int(N)
hist = C.rows_of(hf)
def row(s): return () if s in ('-', '') else tuple(s.split('+'))
P0 = []
for sg in pre.split(';'):
    if sg:
        r, n = sg.rsplit('*', 1); P0 += [row(r)] * int(n)
AL = [row(x) for x in alph.split('|')]
g = goal.split(':')
def reached(s):
    if g[0] == 'stage': return s['stage'] != 0
    if g[0] == 'room': return s['room'] == int(g[1])
    if s['room'] != int(g[1]): return False
    x = C.abs_x(s)
    if g[0] == 'land':
        return x >= int(g[3]) and s['y'] == int(g[4]) and s['anim'] in (0, 1, 2, 3)
    ok = x <= int(g[3]) if g[2] == 'le' else x >= int(g[3])
    if ok and len(g) > 4: ok = int(g[4]) <= s['y'] <= int(g[5])
    return ok
base = L.Enforcer(hist[-1900:])
seen = set(); cands = []
tries = 0
while len(cands) < N and tries < N * 20:
    tries += 1
    w = list(P0)
    while len(w) < len(P0) + K:
        w += [random.choice(AL)] * random.randint(r0, r1)
    w = (w[:len(P0) + K] + [row(tail)] * H)[:H]
    en = base.copy(); lg = tuple(tuple(sorted(en.emit(x))) for x in w)
    if lg in seen: continue
    seen.add(lg); cands.append(lg)
print(f"mrand {tag}: {len(cands)} candidates", flush=True)
P = F.FastPool(2, boot_rows=None, ticks=True)
P.put_all('s', open(mst, 'rb').read())
for wk in P.workers: wk.load('s')
res = FS.run_chunked(P, 's', cands, chunk=48, record='all', stops=[(0x6D, 'changed', 0), (0x65, '==', 0)],
                     log=lambda s: None)
P.close()
sc = []
for lg, r in zip(cands, res):
    if r is None: continue
    mh = 99
    for i, s in enumerate(r.states):
        mh = min(mh, s['hp'])
        if s['hp'] == 0: break
        if reached(s):
            if mh >= minhp and s['ninpo'] >= npmin: sc.append((i, -s['hp'], lg, s))
            break
sc.sort(key=lambda z: z[:2])
print(f"{len(sc)} reach", flush=True)
for z in sc[:8]:
    print(' row', z[0], 'X', C.abs_x(z[3]), 'y', z[3]['y'], 'hp', z[3]['hp'], 'np', z[3]['ninpo'], ' '.join('+'.join(x) or '-' for x in z[2][len(P0):len(P0) + K]))
if sc:
    C.write_inputs(f'states/tmp/rep_{tag}.inputs.txt', list(sc[0][2][:sc[0][0] + 1]), f'mrand {tag}')
