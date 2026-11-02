"""5-3 legal beam (Mesen) from a TAS state F0 (l53p_tas<F0>.mst), prefix = legalized TAS rows F0+1..P (or --prefix file),
then a beam until the goal. python -u work/l53p/b52.py F0 P <tag> [--goal 'rm==24'] [--score '-X'] [--frames 300] [--width 150]
  [--cap 6] [--bx 3] [--by 8] [--alpha 'Left|A+Left|B+Left|-|Right|A+Right|A|Up|Down'] [--minhp 1] [--bf v] [--ov ...]
Writes work/l53p/b_<tag>.txt (rows from F0+1). env: X y f hp np it rm s."""
import sys, time
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
GOAL = opt('--goal', 'rm==24'); NFR = opt('--frames', 300); W = opt('--width', 150); CAP = opt('--cap', 6)
BX = opt('--bx', 3); BY = opt('--by', 8); ALPHA = opt('--alpha', 'Left|A+Left|B+Left|-|Right|A+Right|A|B'); MINHP = opt('--minhp', 1)
PREF = opt('--prefix', ''); EXTRA = opt('--extra', 4); DBG = opt('--dbg', 20); SCORE = opt('--score', '-X'); NGOALS = opt('--goals', 40)
BF = opt('--bf', -1); OV = opt('--ov', ''); LR = opt('--lr', 'R'); KEEPIT = opt('--item', -1)
F0, PEND, TAG = int(a[0]), int(a[1]), a[2]
ov = {}
for part in [p for p in OV.split(';') if p]:
    k, v = part.split('=')
    x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
    for f in range(x, y + 1): ov[f] = set(row(v))
def want(f):
    if f in ov: return ov[f]
    w = set(T(f))
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= ({'Left'} if LR == 'R' else {'Right'})
    return w
hist0 = [tuple(sorted(want(f))) for f in range(F0 - 150, F0 + 1)]
if PREF:
    pre = [row(l.strip()) for l in open(PREF) if l.strip() and not l.startswith('#')]
else:
    en = A.Enforcer(hist0); pre = [tuple(sorted(en.emit(tuple(sorted(want(f)))))) for f in range(F0 + 1, PEND + 1)]
assert not legal_ok(pre, hist0), legal_ok(pre, hist0)
fc = core_at(F0)
if BF >= 0: fc.poke(0xBF, BF)
fc.step(pre, record='last'); fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); hp0 = r0[0x65]
FS = F0 + len(pre)
AL = [row(x) for x in ALPHA.split('|')]
en0 = A.Enforcer(hist0 + list(pre))
GC = compile(GOAL, 'goal', 'eval'); SC = compile(SCORE, 'sc', 'eval')
def env(s, f):
    X, y = RXY(s)
    return dict(X=X, y=y, f=f, hp=s['hp65'], np=s['np64'], it=s['item'], rm=s['room6e'], st=s['st6d'], s=s, hp0=hp0, abs=abs, min=min, max=max)
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
print(f'b53 {TAG}: start frame {FS + 1} hp {hp0} BF {r0[0xBF]} X,y {XY(r0)} room {r0[0x6E]}', flush=True)
for fr in range(NFR):
    f = FS + fr + 1
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
        if s['hp65'] < MINHP: continue
        if KEEPIT >= 0 and s['item'] != KEEPIT and s['room6e'] >= 0: pass
        if s['y8a'] >= 240 and s['5c' if False else 'e5c'] == 2: continue
        e = env(s, f)
        if eval(GC, e):
            goals.append((f, s['hp65'], s['np64'], s['item'], n[1])); gf = gf or f
            continue
        scored.append((eval(SC, e), n))
    scored.sort(key=lambda q: -q[0])
    nxt = []; seen = set(); cnt = {}; ovf = []
    for sc_, n in scored:
        s = n[3]; X, y = RXY(s)
        k = (X, s['xsub'], y, s['vy'], s['vy_sub'], s['coll'], s['anim'], s['rflags'], s['hp65'], s['np64'], s['inv95'], s['eact'], s['item'],
             tuple(s[f'ex{j}'] for j in range(8)), n[1][-1])
        if k in seen: continue
        seen.add(k)
        b = (X // BX, y // BY, s['hp65'])
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
for gfr, hp, np_, it, rows in goals:
    k = (hp, np_, it)
    if k not in best or gfr < best[k][0]: best[k] = (gfr, rows)
print(f'RESULT {TAG} goal(hp,np,item)->frame:', sorted(((k, v[0]) for k, v in best.items()), key=lambda q: q[1]), f'{time.time()-t0:.0f}s', flush=True)
def wr(path, rows, hdr):
    with open(path, 'w') as fo:
        fo.write('# ' + hdr + '\n')
        for r_ in rows: fo.write(('+'.join(sorted(r_)) or '-') + '\n')
if best:
    k = min(best, key=lambda q: best[q][0])
    wr(f'work/l53p/b_{TAG}.txt', list(pre) + list(best[k][1]), f'b53 {TAG} {k} goal {best[k][0]} (rows from TAS frame {F0 + 1})')
    for k2, (g2, rows2) in best.items():
        wr(f'work/l53p/b_{TAG}_h{k2[0]}n{k2[1]}i{k2[2]}.txt', list(pre) + list(rows2), f'b53 {TAG} {k2} goal {g2}')
elif nodes:
    wr(f'work/l53p/b_{TAG}_last.txt', list(pre) + list(nodes[0][1]), f'b53 {TAG} last best')
fc.close()
