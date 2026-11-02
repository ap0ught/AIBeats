"""5-1 legal beam (Mesen) from the TAS state 22,124 with $BF after the control row = c, prefix = D-variant legalized TAS rows
(blank control row, Right from row 2; = the TAS positions) up to frame START, then a beam to the goal.
python -u work/l51p/b51.py <c> <tag> [--start 22281] [--goal 'X>=600'] [--frames 400] [--width 120] [--cap 6] [--bx 3] [--by 8]
   [--alpha 'Right|A+Right|B+Right|-|Left|A+Left|A|Down+B+Right'] [--hpw 4] [--yw 0] [--minhp 1] [--prefix rowsfile] [--extra 6]
Score (higher better): X + yw*(208-y)/10 - hpw*(hp loss); goal frames reported per hp. Writes work/l51p/b_<tag>.txt
(stage rows from the control row 22,125) and prints the goal table."""
import sys, time
sys.path.insert(0, 'work/l51p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
START = opt('--start', 22281); GOAL = opt('--goal', 'X>=600'); NFR = opt('--frames', 400); W = opt('--width', 120)
CAP = opt('--cap', 6); BX = opt('--bx', 3); BY = opt('--by', 8); HPW = opt('--hpw', 4.0); YW = opt('--yw', 0.0)
ALPHA = opt('--alpha', 'Right|A+Right|B+Right|-|Left|A+Left|A|Down+B+Right'); MINHP = opt('--minhp', 1)
PREF = opt('--prefix', ''); EXTRA = opt('--extra', 6); DBG = opt('--dbg', 20); SCORE = opt('--score', '')
NGOALS = opt('--goals', 30)
TAS = opt('--tas', 0); TPRE = opt('--tpre', 0); NPRE = opt('--npre', 0)
c = int(a[0]); TAG = a[1]
if TAS:
    want = []
    for f in range(TAS + 1, TPRE + 1):
        w = set(T(f))
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        if f in (22793, 22794): w = {'Left'}
        want.append(tuple(sorted(w)))
    hist0 = [tuple(sorted(set(T(f)) - ({'Left'} if {'Left', 'Right'} <= set(T(f)) else set()))) for f in range(TAS - 120, TAS + 1)]
    en = A.Enforcer(hist0); pre = [tuple(sorted(en.emit(w))) for w in want]
elif PREF:
    pre = [tuple(sorted(r)) for r in C.rows_of(PREF)]
    if NPRE: pre = pre[:NPRE]
else:
    want = []
    for f in range(22125, START):
        w = set(T(f))
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        if f in (22289, 22793): w = {'Right'}
        if f == 22126: w = {'Right'}
        if f == 22125: w = set()
        want.append(tuple(sorted(w)))
    en = A.Enforcer([()] * 60); pre = [tuple(sorted(en.emit(w))) for w in want]
if TAS:
    fc = core(tas_mst(TAS)); fc.poke(0xBF, (c + TAS - 22125) % 256)
else:
    assert not legal_ok(pre, [()] * 60)
    fc = core(tas_mst(22124)); fc.poke(0xBF, (c - 1) % 256)
fc.step(pre, record='last'); fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); hp0 = r0[0x65]
F0 = (TAS if TAS else 22124) + len(pre)
AL = [row(x) for x in ALPHA.split('|')]
en0 = A.Enforcer((hist0 if TAS else [()] * 60) + list(pre))
GC = compile(GOAL, 'goal', 'eval'); SC = compile(SCORE, 'sc', 'eval') if SCORE else None
def env(s, f):
    X, y = RXY(s)
    return dict(X=X, y=y, f=f, hp=s['hp65'], np=s['np64'], it=s['item'], s=s, hp0=hp0, abs=abs, min=min, max=max)
def score(s, f):
    e = env(s, f)
    if SC: return eval(SC, e)
    return e['X'] + YW * (208 - e['y']) / 10 - HPW * (hp0 - e['hp'])
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
print(f'b51 {TAG}: c {c} start frame {F0 + 1} hp {hp0} BF {r0[0xBF]} X,y {XY(r0)}', flush=True)
for fr in range(NFR):
    f = F0 + fr + 1
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
        if s['hp65'] < MINHP or s['st6d'] != 12: continue
        if s['y8a'] >= 232: continue
        e = env(s, f)
        if eval(GC, e):
            goals.append((f, s['hp65'], s['np64'], s['item'], n[1])); gf = gf or f
            continue
        scored.append((score(s, f), n))
    scored.sort(key=lambda q: -q[0])
    nxt = []; seen = set(); cnt = {}; ovf = []
    for sc_, n in scored:
        s = n[3]; X, y = RXY(s)
        k = (X, s['xsub'], y, s['vy'], s['vy_sub'], s['coll'], s['anim'], s['rflags'], s['hp65'], s['np64'], s['inv95'], s['eact'],
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
        print(f, 'best X', X, 'y', y, 'hp', b['hp65'], 'np', b['np64'], 'nodes', len(nodes), f'{time.time()-t0:.0f}s', flush=True)
    if gf and (f > gf + EXTRA or len(goals) >= NGOALS): break
    if not nodes: break
fc.drop_prefix(f'g{fr}n')
best = {}
for gfr, hp, np_, it, rows in goals:
    k = (hp, np_)
    if k not in best or gfr < best[k][0]: best[k] = (gfr, rows)
print(f'RESULT {TAG} c {c} goal(hp,np)->frame:', sorted(((k, v[0]) for k, v in best.items()), key=lambda q: q[1]), f'{time.time()-t0:.0f}s', flush=True)
def wr(path, rows, hdr):
    with open(path, 'w') as fo:
        fo.write('# ' + hdr + '\n')
        for r_ in rows: fo.write('+'.join(sorted(r_)) + '\n')
if best:
    k = min(best, key=lambda q: (best[q][0] + 3 * (16 - q[0]), ))
    wr(f'work/l51p/b_{TAG}.txt', list(pre) + list(best[k][1]), f'b51 {TAG} c {c} {k} goal {best[k][0]} (rows from the 5-1 control row 22,125)')
    for k2, (g2, rows2) in best.items():
        wr(f'work/l51p/b_{TAG}_h{k2[0]}n{k2[1]}.txt', list(pre) + list(rows2), f'b51 {TAG} c {c} {k2} goal {g2}')
elif nodes:
    wr(f'work/l51p/b_{TAG}_last.txt', list(pre) + list(nodes[0][1]), f'b51 {TAG} last best')
fc.close()
