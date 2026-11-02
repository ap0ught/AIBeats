"""l53b beam (Mesen) from a .mst (after row F0) or a TAS frame. Rows written are from F0+1 (prefix + beam).
python -u work/l53b/bm.py <mst|tasF0> F0 <tag> [--hist file] [--prefix file] [--goal 'rm==29'] [--score 'X'] [--frames 300]
  [--width 150] [--cap 6] [--bx 3] [--by 8] [--alpha 'Right|A+Right|B+Right|-|Left|A+Left|A|B'] [--minhp 1] [--poke 65=3,64=35]
  [--npw 0.0] [--extra 4] [--goals 40]
--hist: rows before F0 (for the press-cap history; default: legalized TAS rows if F0 is a TAS frame).
env for goal/score: X y f hp np it rm s (s = field dict). Writes work/l53b/b_<tag>.txt and b_<tag>_h<hp>n<np>i<it>.txt."""
import sys, time
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
GOAL = opt('--goal', 'rm==29'); NFR = opt('--frames', 300); W = opt('--width', 150); CAP = opt('--cap', 6)
BX = opt('--bx', 3); BY = opt('--by', 8); ALPHA = opt('--alpha', 'Right|A+Right|B+Right|-|Left|A+Left|A|B'); MINHP = opt('--minhp', 1)
PREF = opt('--prefix', ''); EXTRA = opt('--extra', 4); DBG = opt('--dbg', 20); SCORE = opt('--score', 'X'); NGOALS = opt('--goals', 40)
FIX = set(int(x) for x in opt('--fix', '').split(',') if x); HIST = opt('--hist', ''); POKE = opt('--poke', ''); NPW = opt('--npw', 0.0); MINNP = opt('--minnp', 0)
src, F0, TAG = a[0], int(a[1]), a[2]
def rd(p): return [row(l.strip()) for l in open(p) if l.strip() and not l.startswith('#')]
if HIST: hist0 = rd(HIST)
else:
    hist0 = []
    for f in range(F0 - 150, F0 + 1):
        w = set(T(f))
        if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        hist0.append(tuple(sorted(w)))
pre = rd(PREF) if PREF else []
assert not legal_ok(pre, hist0), legal_ok(pre, hist0)
fc = core(src) if src.endswith('.mst') else core_at(int(src))
for p in [q for q in POKE.split(',') if q]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('s0'); fc._ka_slot = 's0'
if pre:
    fc.step(pre, record='last'); fc.save('s0')
r0 = fc.ram(); hp0 = r0[0x65]
FS = F0 + len(pre)
AL = [row(x) for x in ALPHA.split('|')]
en0 = A.Enforcer(list(hist0) + list(pre))
GC = compile(GOAL, 'goal', 'eval'); SC = compile(SCORE, 'sc', 'eval')
def env(s, f):
    X, y = RXY(s)
    return dict(X=X, y=y, f=f, hp=s['hp65'], np=s['np64'], it=s['item'], rm=s['room6e'], st=s['st6d'], s=s, hp0=hp0, abs=abs, min=min, max=max)
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
print(f'bm {TAG}: start frame {FS + 1} hp {hp0} np {r0[0x64]} BF {r0[0xBF]} X,y {XY(r0)} room {r0[0x6E]} | {" ".join(sys.argv[1:])}', flush=True)
for fr in range(NFR):
    f = FS + fr + 1
    out = []
    for ni, (slot, rows, en, s) in enumerate(nodes):
        kids = {}
        prevrow = rows[-1] if rows else (pre[-1] if pre else hist0[-1])
        for w in ([prevrow] if f in FIX else AL):
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if f in FIX and lg != tuple(sorted(prevrow)): continue
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
        if s['hp65'] < MINHP or s['np64'] < MINNP: continue
        if s['item'] != 133: continue
        e = env(s, f)
        if eval(GC, e):
            goals.append((f, s['hp65'], s['np64'], s['item'], n[1])); gf = gf or f
            continue
        scored.append((eval(SC, e) + NPW * s['np64'], n))
    scored.sort(key=lambda q: -q[0])
    nxt = []; seen = set(); cnt = {}; ovf = []
    for sc_, n in scored:
        s = n[3]; X, y = RXY(s)
        k = (X, s['xsub'], y, s['vy'], s['vy_sub'], s['coll'], s['anim'], s['rflags'], s['hp65'], s['np64'], s['inv95'], s['eact'],
             tuple(s[f'ex{j}'] for j in range(8)), tuple(s[f't{j}'] for j in range(8)), n[1][-1])
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
        print(f, 'best X', X, 'y', y, 'hp', b['hp65'], 'np', b['np64'], 'rm', b['room6e'], 'nodes', len(nodes), f'{time.time()-t0:.0f}s', flush=True)
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
    wr(f'work/l53b/b_{TAG}.txt', list(pre) + list(best[k][1]), f'bm {TAG} {k} goal {best[k][0]} (rows from frame {F0 + 1}; src {src})')
    for k2, (g2, rows2) in best.items():
        wr(f'work/l53b/b_{TAG}_h{k2[0]}n{k2[1]}i{k2[2]}.txt', list(pre) + list(rows2), f'bm {TAG} {k2} goal {g2} (rows from {F0 + 1}; src {src})')
elif nodes:
    wr(f'work/l53b/b_{TAG}_last.txt', list(pre) + list(nodes[0][1]), f'bm {TAG} last best (rows from {F0 + 1})')
fc.close()
