"""l53c beam (Mesen), from a TAS state or a .mst. Rows are on the TAS axis when started from a TAS state.
python -u work/l53c/bm.py <F0|path.mst F0> <tag> [--prefix 'spec' | --pfile file] [--goal 'rm==32'] [--score expr]
   [--frames 300] [--width 150] [--cap 6] [--bx 3] [--by 8] [--alpha 'Left|A+Left|...'] [--minhp 3] [--poke 'BF=v,64=v']
   [--hist file] [--extra 4] [--goals 40] [--dbg 20] [--keep 'expr' (prune nodes where expr is false)]
spec = 'Left*20,A+Left*2,...'. env for exprs: X y f hp np it rm s (row dict), vy.
Writes work/l53c/b_<tag>.txt (prefix + beam rows, rows from F0+1) and b_<tag>_h<hp>n<np>.txt per (hp,np)."""
import sys, time
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
GOAL = opt('--goal', 'rm==32'); NFR = opt('--frames', 300); W = opt('--width', 150); CAP = opt('--cap', 6)
BX = opt('--bx', 3); BY = opt('--by', 8); ALPHA = opt('--alpha', 'Left|A+Left|B+Left|-|Right|A+Right|Up|Down+B|A')
MINHP = opt('--minhp', 3); PSPEC = opt('--prefix', ''); PFILE = opt('--pfile', ''); EXTRA = opt('--extra', 4); DBG = opt('--dbg', 20)
SCORE = opt('--score', '-X'); NGOALS = opt('--goals', 40); POKE = opt('--poke', ''); HIST = opt('--hist', ''); KEEP = opt('--keep', '')
def spec_rows(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, k = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(k)
    return out
if a[0].endswith('.mst'):
    fc = core(a[0]); F0 = int(a[1]); TAG = a[2]
else:
    F0 = int(a[0]); TAG = a[1]; fc = core_at(F0)
for p in [p for p in POKE.split(',') if p]:
    k, v = p.split('='); fc.poke(0xBF if k == 'BF' else int(k, 16), int(v))
if HIST:
    hist0 = [row(l.strip()) for l in open(HIST) if l.strip() and not l.startswith('#')]
else:
    hist0 = legalize_tas(F0 - 150, F0)
pre = spec_rows(PSPEC) if PSPEC else ([row(l.strip()) for l in open(PFILE) if l.strip() and not l.startswith('#')] if PFILE else [])
lg = legal_ok(pre, hist0)
assert not lg, lg
fc.save('s00'); fc._ka_slot = 's00'
if pre:
    fc.step(pre, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); hp0 = r0[0x65]
FS = F0 + len(pre)
AL = [row(x) for x in ALPHA.split('|')]
en0 = A.Enforcer(list(hist0) + list(pre))
GC = compile(GOAL, 'goal', 'eval'); SC = compile(SCORE, 'sc', 'eval'); KC = compile(KEEP, 'keep', 'eval') if KEEP else None
def env(s, f):
    X, y = RXY(s)
    return dict(X=X, y=y, f=f, hp=s['hp65'], np=s['np64'], it=s['item'], rm=s['room6e'], st=s['st6d'], s=s, vy=s['vy'], hp0=hp0,
                abs=abs, min=min, max=max)
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
print(f'bm {TAG}: start frame {FS + 1} hp {hp0} np {r0[0x64]} BF {r0[0xBF]} X,y {XY(r0)} room {r0[0x6E]}', flush=True)
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
        if s['hp65'] < MINHP or s['hp65'] > 200: continue
        e = env(s, f)
        if KC is not None and not eval(KC, e): continue
        if eval(GC, e):
            goals.append((f, s['hp65'], s['np64'], s['item'], n[1])); gf = gf or f
            continue
        scored.append((eval(SC, e), n))
    scored.sort(key=lambda q: -q[0])
    nxt = []; seen = set(); cnt = {}; ovf = []
    for sc_, n in scored:
        s = n[3]; X, y = RXY(s)
        k = (X, s['xsub'], y, s['vy'], s['vy_sub'], s['coll'], s['anim'], s['rflags'], s['hp65'], s['np64'], s['inv95'], s['eact'], s['item'],
             tuple(s[f'ex{j}'] for j in range(8)), tuple(s[f't{j}'] for j in range(8)), n[1][-1])
        if k in seen: continue
        seen.add(k)
        b = (X // BX, y // BY, s['hp65'], s['np64'])
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
    wr(f'work/l53c/b_{TAG}.txt', list(pre) + list(best[k][1]), f'bm {TAG} {k} goal {best[k][0]} (rows from frame {F0 + 1})')
    for k2, (g2, rows2) in best.items():
        wr(f'work/l53c/b_{TAG}_h{k2[0]}n{k2[1]}.txt', list(pre) + list(rows2), f'bm {TAG} {k2} goal {g2} (rows from frame {F0 + 1})')
elif nodes:
    wr(f'work/l53c/b_{TAG}_last.txt', list(pre) + list(nodes[0][1]), f'bm {TAG} last best (rows from frame {F0 + 1})')
fc.close()
