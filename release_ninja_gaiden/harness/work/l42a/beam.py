"""4-2 local legal beam on our chain (Mesen, from lock_42_pre + prefix rows), TAS-distance score at a lag.
python -u work/l42a/beam.py <prefix rows> N <goalX> <tag> [--lag 316] [--width 40] [--frames 300] [--hpw 6]
   [--alpha 'Right|A+Right|B+Right|Down+B+Right|-'] [--ylo 0 --yhi 999] [--npmin 0] [--extra 12] [--dbg 0]
Item must stay J&S (133). Goal: X >= goalX (ylo<=y<=yhi), hp>0. Reports per (hp,np) the best lag (goal frame - TAS
frame at goalX - lag). Writes work/l42a/bm_<tag>.txt = prefix[:N] + beam rows (best: min lag, then max hp, max np)."""
import sys, time
sys.path.insert(0, 'work/l42a')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
W = opt('--width', 40); NF = opt('--frames', 300); HPW = opt('--hpw', 6.0); LAG = opt('--lag', LAG0); DBG = opt('--dbg', 0)
ALPHA = opt('--alpha', 'Right|A+Right|B+Right|Down+B+Right|-'); YLO = opt('--ylo', 0); YHI = opt('--yhi', 999)
NPMIN = opt('--npmin', 0); EXTRA = opt('--extra', 12); YW = opt('--yw', 0.3); NPW = opt('--npw', 0.0)
pre = [tuple(r) for r in C.rows_of(a[0])] if a[0] != '-' else []; N = int(a[1]); XG = int(a[2]); TAG = a[3]
pre = pre[:N]
def tX(f): return C.abs_x(TT[f])
TG = next(f for f in range(TAS_CTL, TAS_CTL + 2400) if tX(f) >= XG)
fc = core()
if pre: fc.step(pre, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); HP0 = r0[0x65]
AL = [row(x) for x in ALPHA.split('|')]
en0 = L.Enforcer((HIST + pre)[-1900:])
def score(s, f):
    t = TT[f - LAG]
    return abs(C.abs_x(s) + s['xsub'] / 256 - tX(f - LAG)) + YW * abs(s['y'] - t['y']) + HPW * (HP0 - s['hp']) - NPW * s['ninpo']
nodes = [('s0', (), en0, None)]
goals = []; t0 = time.time()
for fr in range(NF):
    f = F0 + N + fr + 1
    out = []
    for ni, (slot, rows, en, s) in enumerate(nodes):
        kids = {}
        for w in AL:
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if lg not in kids: kids[lg] = e2
        kl = list(kids.items())
        rr = fc.run_batch(slot, [[lg] for lg, _ in kl], record='last', keep=True, prefix=f'g{fr}n{ni}_')
        for (lg, e2), r in zip(kl, rr):
            if not r.states: continue
            out.append((r.slot, rows + (lg,), e2, r.states[-1]))
    if fr: fc.drop_prefix(f'g{fr-1}n')
    nxt = []; seen = set()
    for n in sorted(out, key=lambda n: score(n[3], f)):
        s = n[3]
        if s['hp'] == 0 or s['stage'] != 9 or s['item'] != 133: continue
        if C.abs_x(s) >= XG and YLO <= s['y'] <= YHI and s['ninpo'] >= NPMIN:
            goals.append((f - TG - LAG, s['hp'], s['ninpo'], n[1])); continue
        k = (C.abs_x(s), s['xsub'], s['y'], s['vy'], s.get('vy_sub', 0), s['coll'], s['anim'], s['hp'], s['ninpo'], s.get('eact', 0), n[1][-1])
        if k in seen: continue
        seen.add(k); nxt.append(n)
        if len(nxt) >= W: break
    nodes = nxt
    if DBG and fr % 10 == 0 and nodes:
        b = nodes[0][3]; print(f, 'best X', C.abs_x(b), 'y', b['y'], 'hp', b['hp'], 'np', b['ninpo'], 'tasX', tX(f - LAG), 'sc', round(score(b, f), 1), flush=True)
    if goals and f - TG - LAG > min(g[0] for g in goals) + EXTRA: break
    if not nodes: break
best = {}
for lag, hp, np_, rows in goals:
    k = (hp, np_)
    if k not in best or lag < best[k][0]: best[k] = (lag, rows)
print(f'beam {TAG} N {N} goalX {XG} TAS {TG} lag {LAG} results (hp,np)->extra lag:',
      sorted(((k, v[0]) for k, v in best.items()), key=lambda q: q[1]), f'{time.time()-t0:.0f}s', flush=True)
if best:
    k = min(best, key=lambda q: (best[q][0], -q[0], -q[1]))
    C.write_inputs(f'work/l42a/bm_{TAG}.txt', list(pre) + list(best[k][1]), f'beam {TAG} from N {N} best {k} lag +{best[k][0]}')
    for k2, (lg2, rows2) in best.items():
        C.write_inputs(f'work/l42a/bm_{TAG}_h{k2[0]}n{k2[1]}.txt', list(pre) + list(rows2), f'beam {TAG} {k2} lag +{lg2}')
fc.close()
