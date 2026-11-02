"""Mesen window brute force (wbrute on FastPool): every combination of segment lengths of a small grammar,
legalized by the Enforcer on the power-on history, earliest goal wins.
    python -u work/rep/mbrute.py <hist file> <mst> "<grammar>" "<goal>" <out tag> [--tail Right] [--horizon 160]
        [--minhp 0] [--npmin 0] [--item N] [--workers 2] [--top 10]
grammar: 'ROW:n1,n2|a-b;ROW:...' ROW = buttons joined by + or '-' for none.
goal: x:R:ge|le:GX[:ylo:yhi] | room:R | stage | land:R:ge:GX:Y (on ground y==Y at X>=GX)
Out: states/tmp/rep_<tag>.inputs.txt (legal rows to the goal frame, history excluded) + prints the top results."""
import itertools, sys, time
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
tail = opt('--tail', 'Right'); H = opt('--horizon', 160); minhp = opt('--minhp', 0); npmin = opt('--npmin', 0)
item = opt('--item', -1); NW = opt('--workers', 2); top = opt('--top', 10); chunk = opt('--chunk', 48)
hf, mst, gram, goal, tag = a[:5]
hist = C.rows_of(hf)
def row(s): return () if s in ('-', '') else tuple(s.split('+'))
segs = []
for sg in gram.split(';'):
    r, ls = sg.rsplit(':', 1)
    vals = []
    for p in ls.split(','):
        if '-' in p and not p.startswith('-'):
            x, y = p.split('-'); vals += list(range(int(x), int(y) + 1))
        else:
            vals.append(int(p))
    segs.append((row(r), vals))
g = goal.split(':')
def reached(s):
    if g[0] == 'stage': return s['stage'] != st0
    if g[0] == 'room': return s['room'] == int(g[1])
    if s['room'] != int(g[1]): return False
    x = C.abs_x(s)
    if g[0] == 'land':
        return x >= int(g[3]) and s['y'] == int(g[4]) and s['vy'] in (0, 1, 2, 3, 4, 5) and s['anim'] in (0, 1, 2, 3)
    ok = x <= int(g[3]) if g[2] == 'le' else x >= int(g[3])
    if ok and len(g) > 4: ok = int(g[4]) <= s['y'] <= int(g[5])
    return ok
base = L.Enforcer(hist[-1900:])
seen = set(); cands = []
for lens in itertools.product(*[v for _, v in segs]):
    w = []
    for (r, _), n in zip(segs, lens): w += [r] * n
    w = (w + [row(tail)] * H)[:H]
    en = base.copy(); lg = tuple(tuple(sorted(en.emit(x))) for x in w)
    if lg in seen: continue
    seen.add(lg); cands.append((lens, lg))
print(f"mbrute {tag}: {len(cands)} unique candidates, H {H}", flush=True)
P = F.FastPool(NW, boot_rows=None, ticks=True)
P.put_all('s', open(mst, 'rb').read())
for wk in P.workers: wk.load('s')
st0 = P.workers[0].ram()[0x6D]
stops = [(0x6D, 'changed', 0), (0x65, '==', 0)]
t0 = time.time()
res = FS.run_chunked(P, 's', [c[1] for c in cands], chunk=chunk, record='all', stops=stops,
                     log=lambda s: print(s, flush=True))
P.close()
scored = []
for (lens, lg), r in zip(cands, res):
    if r is None: continue
    mh = 99; hit = None
    for i, s in enumerate(r.states):
        mh = min(mh, s['hp'])
        if s['hp'] == 0 or (s['dead'] & 0x80): break
        if reached(s):
            if mh >= minhp and s['ninpo'] >= npmin and (item < 0 or s['item'] == item):
                hit = (i, s)
            break
    if hit:
        scored.append((hit[0], -hit[1]['hp'], -hit[1]['ninpo'], lens, lg, hit[1]))
scored.sort(key=lambda z: z[:3])
print(f"done {time.time()-t0:.0f}s, {len(scored)} reach the goal", flush=True)
for z in scored[:top]:
    s = z[5]
    print(f"  reach row {z[0]} lens {z[3]} X {C.abs_x(s)} y {s['y']} hp {s['hp']} np {s['ninpo']}")
if scored:
    z = scored[0]
    C.write_inputs(f'states/tmp/rep_{tag}.inputs.txt', list(z[4][:z[0] + 1]), f'mbrute {tag} {gram} goal {goal} lens {z[3]}')
