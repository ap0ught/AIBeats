"""4-2 progress beam (Mesen, from lock_42_pre + prefix rows[:N]); score = -X + hpw*hp lost (+ npw bonus); diversity cap
per (y band, hp) bucket. Item must stay J&S (133).
python -u work/l42a/beam2.py <prefix rows> N <goalX> <tag> [--width 120] [--frames 300] [--hpw 4] [--cap 12] [--yb 16]
   [--alpha ..] [--ylo 0 --yhi 999] [--npmin 0] [--npw 0] [--extra 10] [--minhp 1] [--dbg 1]
Writes work/l42a/b2_<tag>.txt (best: earliest goal frame, then hp, then np) and b2_<tag>_h<hp>n<np>.txt per class."""
import sys, time
sys.path.insert(0, 'work/l42a')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
W = opt('--width', 120); NF = opt('--frames', 300); HPW = opt('--hpw', 4.0); CAP = opt('--cap', 12); YB = opt('--yb', 16)
DBG = opt('--dbg', 1); ALPHA = opt('--alpha', 'Right|A+Right|B+Right|A+B+Right|-|Left|A+Left|B+Left|Down+B+Right')
YLO = opt('--ylo', 0); YHI = opt('--yhi', 999); NPMIN = opt('--npmin', 0); NPW = opt('--npw', 0.0); EXTRA = opt('--extra', 10)
MINHP = opt('--minhp', 1); TLAG = opt('--tas', 0); NOSPIN = opt('--nospin', 0); KEEP = [tuple(map(int, q.split(':'))) for q in opt('--keep', '').split(',') if q]; FRW = opt('--frw', 0.0); NOBX = opt('--nobx', 99999)
pre = [tuple(r) for r in C.rows_of(a[0])][:int(a[1])] if a[0] != '-' else []; N = len(pre); XG = int(a[2]); TAG = a[3]
fc = core()
if pre: fc.step(pre, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); HP0 = r0[0x65]
AL = [row(x) for x in ALPHA.split('|')]
en0 = L.Enforcer((HIST + pre)[-1900:])
def score(s):
    v = -(C.abs_x(s) + s['xsub'] / 256) + HPW * (HP0 - s['hp']) - NPW * s['ninpo']
    if TLAG:
        t = TT[s['frame'] - TLAG]; v = abs(C.abs_x(s) + s['xsub'] / 256 - C.abs_x(t)) + 0.3 * abs(s['y'] - t['y']) + HPW * (HP0 - s['hp']) - NPW * s['ninpo']
    return v
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time(); gf = None
for fr in range(NF):
    f = F0 + N + fr + 1
    out = []
    for ni, (slot, rows, en, s) in enumerate(nodes):
        kids = {}
        for w in AL:
            if s is not None and C.abs_x(s) >= NOBX and 'B' in w and 'Down' not in w and s['y'] < 190: continue
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if lg not in kids: kids[lg] = e2
        kl = list(kids.items())
        rr = fc.run_batch(slot, [[lg] for lg, _ in kl], record='last', keep=True, prefix=f'g{fr}n{ni}_')
        for (lg, e2), r in zip(kl, rr):
            if not r.states: continue
            st_ = r.states[-1]; st_['frame'] = f
            if NOSPIN and s is not None and st_['ninpo'] < s['ninpo']: continue
            out.append((r.slot, rows + (lg,), e2, st_))
    if fr: fc.drop_prefix(f'g{fr-1}n')
    nxt = []; seen = set(); cnt = {}; ovf = []
    for n in sorted(out, key=lambda n: score(n[3])):
        s = n[3]
        if s['hp'] < MINHP or s['stage'] != 9 or s['item'] != 133 or s['y'] > 200: continue
        if any(not ((s['eact'] >> sl) & 1 and s[f't{sl}'] == ty) for sl, ty in KEEP): continue
        if C.abs_x(s) >= XG and YLO <= s['y'] <= YHI and s['ninpo'] >= NPMIN:
            goals.append((f, s['hp'], s['ninpo'], n[1])); gf = gf or f; continue
        k = (C.abs_x(s), s['xsub'], s['y'], s['vy'], s.get('vy_sub', 0), s['coll'], s['anim'], s['hp'], s['ninpo'], s.get('eact', 0), n[1][-1])
        if k in seen: continue
        seen.add(k)
        b = (s['y'] // YB, s['hp'], s['ninpo'])
        if cnt.get(b, 0) >= CAP:
            ovf.append(n); continue
        cnt[b] = cnt.get(b, 0) + 1
        nxt.append(n)
        if len(nxt) >= W: break
    if len(nxt) < W: nxt += ovf[:W - len(nxt)]
    nodes = nxt
    if DBG and fr % 10 == 0 and nodes:
        b = nodes[0][3]; print(f, 'best X', C.abs_x(b), 'y', b['y'], 'hp', b['hp'], 'np', b['ninpo'], 'nodes', len(nodes), f'{time.time()-t0:.0f}s', flush=True)
    if gf and f > gf + EXTRA: break
    if not nodes: break
best = {}
for gfr, hp, np_, rows in goals:
    k = (hp, np_)
    if k not in best or gfr < best[k][0]: best[k] = (gfr, rows)
print(f'beam2 {TAG} N {N} goalX {XG} results (hp,np)->goal frame:', sorted(((k, v[0]) for k, v in best.items()), key=lambda q: q[1]), f'{time.time()-t0:.0f}s', flush=True)
if best:
    k = min(best, key=lambda q: (best[q][0], -q[0], -q[1]))
    C.write_inputs(f'work/l42a/b2_{TAG}.txt', list(pre) + list(best[k][1]), f'beam2 {TAG} from N {N} best {k} goal frame {best[k][0]}')
    for k2, (g2, rows2) in best.items():
        C.write_inputs(f'work/l42a/b2_{TAG}_h{k2[0]}n{k2[1]}.txt', list(pre) + list(rows2), f'beam2 {TAG} {k2} goal frame {g2}')
fc.close()
