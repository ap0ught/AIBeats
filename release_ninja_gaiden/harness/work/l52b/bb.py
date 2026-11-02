"""5-2 rooms 24-26 legal beam (agent l52b; from work/l52p/b52.py).
python -u work/l52b/bb.py F0 <tag> [--state file.mst] [--hist rowsfile] [--pre 'Row*n,...' | --prefile f]
   [--goal 'rm==25'] [--score '-X'] [--frames 300] [--width 150] [--cap 6] [--bx 3] [--by 8]
   [--alpha 'Left|A+Left|-|Right|A+Right|A'] [--minhp 1] [--poke 'a=v;a=v'] [--keepit 133]
F0 = frame of the start state (TAS state l52p_tas<F0>.mst unless --state). History for legality: --hist (rows file whose
LAST rows end at F0) else the legalized TAS rows. Writes work/l52b/b_<tag>.txt (rows from F0+1). env: X y f hp np it rm s."""
import sys, time
sys.path.insert(0, 'work/l52p')
from lib import *
if os.environ.get('MINGB'):
    import fcka as _fk; d = list(_fk._init.__defaults__); d[-1] = float(os.environ['MINGB']); _fk._init.__defaults__ = tuple(d)
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
GOAL = opt('--goal', 'rm==25'); NFR = opt('--frames', 300); W = opt('--width', 150); CAP = opt('--cap', 6)
BX = opt('--bx', 3); BY = opt('--by', 8); ALPHA = opt('--alpha', 'Left|A+Left|-|Right|A+Right|A'); MINHP = opt('--minhp', 1)
PRE = opt('--pre', ''); PREF = opt('--prefile', ''); EXTRA = opt('--extra', 4); DBG = opt('--dbg', 20); SCORE = opt('--score', '-X')
NGOALS = opt('--goals', 40); POKE = opt('--poke', ''); KEEPIT = opt('--keepit', -1); STATE = opt('--state', ''); HIST = opt('--hist', '')
OUTD = opt('--outd', 'work/l52b'); KEEP = opt('--keep', '')
F0, TAG = int(a[0]), a[1]
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
def load_rows(p):
    return [row(l.strip()) for l in open(p) if l.strip() and not l.startswith('#')]
if HIST:
    hist0 = load_rows(HIST)[-1900:]
else:
    def want(f):
        w = set(T(f))
        if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        return tuple(sorted(w))
    hist0 = [want(f) for f in range(F0 - 300, F0 + 1)]
pre = load_rows(PREF) if PREF else rr(PRE)
assert not legal_ok(pre, hist0), legal_ok(pre, hist0)
fc = core(STATE) if STATE else core_at(F0)
for part in [p for p in POKE.split(';') if p]:
    k, v = part.split('='); fc.poke(int(k, 0), int(v, 0))
fc.step(pre, record='last'); fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); hp0 = r0[0x65]
FS = F0 + len(pre)
AL = [row(x) for x in ALPHA.split('|')]
en0 = A.Enforcer(hist0 + list(pre))
GC = compile(GOAL, 'goal', 'eval'); KC = compile(KEEP, 'keep', 'eval') if KEEP else None; SC = compile(SCORE, 'sc', 'eval')
def env(s, f):
    X, y = RXY(s)
    return dict(X=X, y=y, f=f, hp=s['hp65'], np=s['np64'], it=s['item'], rm=s['room6e'], st=s['st6d'], s=s, hp0=hp0, abs=abs, min=min, max=max)
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
print(f'bb {TAG}: start frame {FS + 1} hp {hp0} np {r0[0x64]} it {r0[0xC9]} BF {r0[0xBF]} X,y {XY(r0)} room {r0[0x6E]}', flush=True)
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
        rr_ = fc.run_batch(slot, [[lg] for lg, _ in kl], record='last', keep=True, prefix=f'g{fr}n{ni}_')
        for (lg, e2), r in zip(kl, rr_):
            if not r.states: continue
            out.append((r.slot, rows + (lg,), e2, r.states[-1]))
    if fr: fc.drop_prefix(f'g{fr-1}n')
    scored = []
    for n in out:
        s = n[3]
        if s['hp65'] < MINHP: continue
        if KEEPIT >= 0 and s['item'] != KEEPIT: continue
        if s['y8a'] >= 240 and s['e5c'] == 2: continue
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
             tuple(s[f'ex{j}'] for j in range(8)), tuple(s[f'ey{j}'] for j in range(8)), n[1][-1])
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
    with open(path + '.tmp', 'w') as fo:
        fo.write('# ' + hdr + '\n')
        for r_ in rows: fo.write(('+'.join(sorted(r_)) or '-') + '\n')
    os.replace(path + '.tmp', path)
if best:
    k = min(best, key=lambda q: best[q][0])
    wr(f'{OUTD}/b_{TAG}.txt', list(pre) + list(best[k][1]), f'bb {TAG} {k} goal {best[k][0]} (rows from frame {F0 + 1})')
    for k2, (g2, rows2) in best.items():
        wr(f'{OUTD}/b_{TAG}_h{k2[0]}n{k2[1]}i{k2[2]}.txt', list(pre) + list(rows2), f'bb {TAG} {k2} goal {g2} (rows from frame {F0 + 1})')
elif nodes:
    wr(f'{OUTD}/b_{TAG}_last.txt', list(pre) + list(nodes[0][1]), f'bb {TAG} last best (rows from frame {F0 + 1})')
fc.close()
