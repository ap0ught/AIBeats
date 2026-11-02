"""Room-23 legal beam (Mesen) from our chain. python -u work/l52a/b23.py <rows file (from row 24,998)> <start frame S> <tag>
  [--goal 'rm==24'] [--score '-X'] [--frames 300] [--width 200] [--cap 6] [--bx 3] [--by 8] [--alpha 'Left|A+Left|...'] [--minhp 1]
The first S-24,997 rows of the file are the fixed prefix (state after row S); the beam emits rows S+1, S+2, ...
Writes work/l52a/b_<tag>.txt (all rows from 24,998) for the best goal; env: X y f hp np it rm act tch fl vy s."""
import sys, time
sys.path.insert(0, 'work/l52a')
from lib2 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
GOAL = opt('--goal', 'rm==24'); NFR = opt('--frames', 300); W = opt('--width', 200); CAP = opt('--cap', 6)
BX = opt('--bx', 3); BY = opt('--by', 8); ALPHA = opt('--alpha', 'Left|A+Left|B+Left|-|Right|A+Right|A|Up'); MINHP = opt('--minhp', 1)
EXTRA = opt('--extra', 3); DBG = opt('--dbg', 10); SCORE = opt('--score', '-X'); NGOALS = opt('--goals', 30); MST = opt('--mst', '')
KEEP = opt('--keep', '')
SRC, S, TAG = a[0], int(a[1]), a[2]
FLD.update(dict(act=0x80, tch=0x8C, fl=0x84, vy=0x89))
allrows = rows_file(SRC)
pre = allrows[:S - CTL52 + 1]
H = chain_hist()
assert not legal_ok(pre, H), legal_ok(pre, H)
if MST:
    fc = core(MST)
else:
    fc = core(BASE52); fc.step(pre, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); hp0 = r0[0x65]
print(f'b23 {TAG}: state after {S}: X,y {XY(r0)} hp {hp0} np {r0[0x64]} it {r0[0xC9]} BF {r0[0xBF]}', flush=True)
AL = [row(x) for x in ALPHA.split('|')]
en0 = A.Enforcer(H + list(pre))
GC = compile(GOAL, 'goal', 'eval'); SC = compile(SCORE, 'sc', 'eval'); KC = compile(KEEP, 'keep', 'eval') if KEEP else None
def env(s, f):
    X, y = RXY(s)
    return dict(X=X, y=y, f=f, hp=s['hp65'], np=s['np64'], it=s['item'], rm=s['room6e'], act=s['act'], tch=s['tch'], fl=s['fl'],
                vy=s['vy'], s=s, hp0=hp0, abs=abs, min=min, max=max)
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
for fr in range(NFR):
    f = S + fr + 1
    out = []
    for ni, (slot, rows, en, s) in enumerate(nodes):
        kids = {}
        for w in AL:
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if ('Left' in lg and 'Right' in lg) or ('Up' in lg and 'Down' in lg): continue
            if lg not in kids: kids[lg] = e2
        kl = list(kids.items())
        rr = fc.run_batch(slot, [[lg] for lg, _ in kl], record='last', keep=True, prefix=f'g{fr}n{ni}_')
        for (lg, e2), r in zip(kl, rr):
            if not r.states: continue
            out.append((r.slot, rows + (lg,), e2, r.states[-1]))
    if fr: fc.drop_prefix(f'g{fr-1}n')
    scored = []
    for n in out:
        s = n[3]
        if s['hp65'] < MINHP or s['y8a'] >= 240: continue
        e = env(s, f)
        if eval(GC, e):
            goals.append((f, s['hp65'], s['np64'], s['item'], n[1], RXY(s))); gf = gf or f
            continue
        if KC is not None and not eval(KC, e): continue
        scored.append((eval(SC, e), n))
    scored.sort(key=lambda q: -q[0])
    nxt = []; seen = set(); cnt = {}; ovf = []
    for sc_, n in scored:
        s = n[3]; X, y = RXY(s)
        k = (X, s['xsub'], y, s['vy'], s['vy_sub'], s['act'], s['tch'], s['fl'], s['anim'], s['hp65'], s['np64'], s['inv95'], s['eact'], s['item'],
             tuple(s[f'ex{j}'] for j in range(8)), tuple(s[f'ey{j}'] for j in range(8)), n[1][-1])
        if k in seen: continue
        seen.add(k)
        b = (X // BX, y // BY, s['hp65'], s['item'])
        if cnt.get(b, 0) >= CAP:
            ovf.append(n); continue
        cnt[b] = cnt.get(b, 0) + 1
        nxt.append(n)
        if len(nxt) >= W: break
    if len(nxt) < W: nxt += ovf[:W - len(nxt)]
    nodes = nxt
    if DBG and fr % DBG == 0 and nodes:
        b = nodes[0][3]; X, y = RXY(b)
        print(f, 'best X', X, 'y', y, 'hp', b['hp65'], 'np', b['np64'], 'it', b['item'], 'rm', b['room6e'], 'nodes', len(nodes), f'{time.time()-t0:.0f}s', flush=True)
    if gf and (f > gf + EXTRA or len(goals) >= NGOALS): break
    if not nodes: break
fc.drop_prefix(f'g{fr}n')
best = {}
for gfr, hp, np_, it, rows, xy in goals:
    k = (hp, np_, it)
    if k not in best or gfr < best[k][0]: best[k] = (gfr, rows, xy)
print(f'RESULT {TAG} goal(hp,np,item)->frame:', sorted(((k, v[0], v[2]) for k, v in best.items()), key=lambda q: q[1]), f'{time.time()-t0:.0f}s', flush=True)
if best:
    k = min(best, key=lambda q: (best[q][0], -q[0]))
    wr(f'work/l52a/b_{TAG}.txt', list(pre) + list(best[k][1]), f'b23 {TAG} {k} goal {best[k][0]} (rows from 24,998)')
    for k2, (g2, rows2, xy2) in best.items():
        wr(f'work/l52a/b_{TAG}_h{k2[0]}n{k2[1]}i{k2[2]}.txt', list(pre) + list(rows2), f'b23 {TAG} {k2} goal {g2}')
elif nodes:
    wr(f'work/l52a/b_{TAG}_last.txt', list(pre) + list(nodes[0][1]), f'b23 {TAG} last best')
fc.close()
