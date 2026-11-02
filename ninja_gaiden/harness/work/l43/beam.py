"""4-3 beam (Mesen). Start = base state (pre-control 19,297) + the first N stage rows of <prefix>.
python -u work/l43/beam.py <prefix stage rows|-> N <tag> [--score EXPR] [--goal EXPR] [--width 150] [--frames 300]
   [--alpha 'Right|A+Right|..'] [--cap 10] [--bx 4] [--by 8] [--extra 8] [--minhp 1] [--hpw 3] [--nospin 0]
   [--keepnp 0] [--rooms 18,19] [--ekey 0] [--dbg 10] [--goals 40]
EXPR variables: X y f hp np rm vy inv (ours), tx(f) ty(f) trm(f) (TAS trace), LAG (TAS lag), hp0 np0, s (Row).
Default score = TAS distance at LAG: |X - tx(f-LAG)| + 0.3|y - ty(f-LAG)| + hpw*(hp0-hp) (lower is better).
Writes work/l43/b_<tag>.txt (stage rows from the control row: prefix[:N] + best) and b_<tag>_h<hp>n<np>.txt."""
import sys, time
sys.path.insert(0, 'work/l43')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
W = opt('--width', 150); NF = opt('--frames', 300); CAP = opt('--cap', 10); BX = opt('--bx', 4); BY = opt('--by', 8)
ALPHA = opt('--alpha', 'Right|A+Right|B+Right|-|Left|A+Left|A')
SCORE = opt('--score', ''); GOAL = opt('--goal', 'False'); EXTRA = opt('--extra', 8); MINHP = opt('--minhp', 1)
HPW = opt('--hpw', 3.0); NOSPIN = opt('--nospin', 0); KEEPNP = opt('--keepnp', -1); ROOMS = opt('--rooms', '')
EKEY = opt('--ekey', 0); DBG = opt('--dbg', 10); NGOALS = opt('--goals', 40); LAGO = opt('--lag', LAG)
NPEQ = opt('--npeq', -1); REQ = opt('--req', 'True')
ROOMS = set(int(q) for q in ROOMS.split(',') if q)
MST = opt('--mst', ''); MF0 = opt('--f0', 0)
pre = rows_file(a[0])[:int(a[1])] if a[0] != '-' else []; N = len(pre); TAG = a[2]
F0 = MF0 if MST else CTL - 1                     # frame of the base state
def tx(f): return TX.get(f, 0)
def ty(f): return TY.get(f, 0)
def trm(f): return TRM.get(f, 0)
_TPC = {}
def tp(X_, y_, t1, t2, wy=0.5):
    """TAS-path progress: the TAS frame t in [t1, t2] nearest to (X_, y_) (same room as TAS frame t1) and the distance."""
    key = (t1, t2)
    if key not in _TPC: _TPC[key] = [(t, TX[t], TY[t]) for t in range(t1, t2 + 1) if TRM[t] == TRM[t1]]
    bt, bd = t1, 1e9
    for t, x_, yy in _TPC[key]:
        d = abs(X_ - x_) + wy * abs(y_ - yy)
        if d < bd: bd, bt = d, t
    return bt, bd
fc = core(MST) if MST else core()
if pre: fc.step(pre, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); hp0 = r0[0x65]; np0 = r0[0x64]
AL = [row(x) for x in ALPHA.split('|')]
en0 = A.Enforcer([()] * 40 + list(pre)) if MST else enforcer(pre)
SC = compile(SCORE, 'score', 'eval') if SCORE else None
GC = compile(GOAL, 'goal', 'eval'); RC = compile(REQ, 'req', 'eval')
def env(s, f):
    return dict(X=C.abs_x(s), y=s['y'], f=f, hp=s['hp'], np=s['ninpo'], rm=s['room'], vy=s['vy'], inv=s['inv'],
                tx=tx, ty=ty, trm=trm, tp=tp, en=enemies_s, any=any, LAG=LAGO, hp0=hp0, np0=np0, s=s, abs=abs, min=min, max=max)
def score(s, f):
    e = env(s, f)
    if SC: return eval(SC, e)
    t = f - LAGO
    v = abs(e['X'] - tx(t)) + 0.3 * abs(e['y'] - ty(t)) + HPW * (hp0 - e['hp'])
    if trm(t) != e['rm']: v += 1000
    return v
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
print(f'beam {TAG}: N {N} start frame {F0 + N} hp {hp0} np {np0}', flush=True)
for fr in range(NF):
    f = F0 + N + fr + 1
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
            st_ = r.states[-1]
            if NOSPIN and s is not None and st_['ninpo'] < s['ninpo']: continue
            out.append((r.slot, rows + (lg,), e2, st_))
    if fr: fc.drop_prefix(f'g{fr-1}n')
    scored = []
    for n in out:
        s = n[3]
        if s['hp'] < MINHP or s['item'] != 133 or s['stage'] != 10: continue
        if ROOMS and s['room'] not in ROOMS: continue
        if KEEPNP >= 0 and s['ninpo'] < KEEPNP: continue
        if not eval(RC, env(s, f)): continue
        if eval(GC, env(s, f)):
            if NPEQ < 0 or s['ninpo'] == NPEQ:
                goals.append((f, s['hp'], s['ninpo'], n[1])); gf = gf or f
            continue
        scored.append((score(s, f), n))
    scored.sort(key=lambda q: q[0])
    nxt = []; seen = set(); cnt = {}; ovf = []
    for sc_, n in scored:
        s = n[3]
        k = (C.abs_x(s), s['xsub'], s['y'], s['vy'], s['vy_sub'], s['coll'], s['anim'], s['rflags'], s['hp'], s['ninpo'],
             s['inv'], s['eact'], n[1][-1])
        if EKEY: k = k + tuple(s[f'ex{j}'] for j in range(8)) + tuple(s[f'ey{j}'] for j in range(8))
        if k in seen: continue
        seen.add(k)
        b = (s['room'], C.abs_x(s) // BX, s['y'] // BY, s['hp'], s['ninpo'])
        if cnt.get(b, 0) >= CAP:
            ovf.append(n); continue
        cnt[b] = cnt.get(b, 0) + 1
        nxt.append(n)
        if len(nxt) >= W: break
    if len(nxt) < W: nxt += ovf[:W - len(nxt)]
    nodes = nxt
    if DBG and fr % DBG == 0 and nodes:
        b = nodes[0][3]
        print(f, 'best rm', b['room'], 'X', C.abs_x(b), 'y', b['y'], 'hp', b['hp'], 'np', b['ninpo'], 'sc', round(scored[0][0], 1),
              '| TAS', tx(f - LAGO), ty(f - LAGO), 'nodes', len(nodes), f'{time.time()-t0:.0f}s', flush=True)
    if gf and (f > gf + EXTRA or len(goals) >= NGOALS): break
    if not nodes: break
fc.drop_prefix(f'g{fr}n')
best = {}
for gfr, hp, np_, rows in goals:
    k = (hp, np_)
    if k not in best or gfr < best[k][0]: best[k] = (gfr, rows)
print(f'beam {TAG} N {N} results (hp,np)->goal frame:', sorted(((k, v[0]) for k, v in best.items()), key=lambda q: q[1]),
      f'{time.time()-t0:.0f}s', flush=True)
if nodes:
    write_rows(f'work/l43/b_{TAG}_last.txt', list(pre) + list(nodes[0][1]), f'beam {TAG} best node of the last generation (frame {f})')
if best:
    k = min(best, key=lambda q: (best[q][0], -q[0], -q[1]))
    write_rows(f'work/l43/b_{TAG}.txt', list(pre) + list(best[k][1]), f'beam {TAG} from N {N} best {k} goal frame {best[k][0]}')
    for k2, (g2, rows2) in best.items():
        write_rows(f'work/l43/b_{TAG}_h{k2[0]}n{k2[1]}.txt', list(pre) + list(rows2), f'beam {TAG} {k2} goal frame {g2}')
fc.close()
