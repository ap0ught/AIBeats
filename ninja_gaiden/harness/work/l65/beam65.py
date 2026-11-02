"""l65 beam for the 6-5 Demon (Mesen). Synchronous beam over 5-row legal macro blocks from the TAS 6-5 control-1 state
with $BF poked (one or several bf values: a candidate is scored over all of them = a robust line).

python work/l65/beam65.py --bf 243[,v,..] --phase pod|heart|kill [--prefix rows.txt] [--width 60] [--blocks 40]
       [--out work/l65/x.txt] [--hpmin 1] [--offsets 0,1,2,3,4] [--dmgw 6]

phase pod  : goal = the pod dead (slot 6 explosion) -> score frames; stops when every node is past the best goal + 10.
phase kill : goal = $66 == 0 (the heart dead) in stage 21; the whole fight (pod first).
Rows written = prefix + found rows, row 1 = the 6-5 control row. Every row passes K.Legal (period 5, hold 2, release 2,
600:109, 1800:246, no L+R / U+D) with 150 blank rows of history.
"""
import sys, time
sys.path.insert(0, 'work/l65')
from lib65 import *
FLD['pst6'] = 0x42E; FLD['pf6'] = 0x416
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
BFS = [int(v) for v in opt('--bf', '243').split(',')]
PH = opt('--phase', 'kill'); PREF = opt('--prefix', ''); W = int(opt('--width', '60')); NB = int(opt('--blocks', '40'))
OUT = opt('--out', ''); HPMIN = int(opt('--hpmin', '1')); OFFS = [int(v) for v in opt('--offsets', '0').split(',')]
DMGW = float(opt('--dmgw', '6')); TAG = opt('--tag', 'b')
MAXF = int(opt('--maxf', '9999'))

D = {'-': (), 'L': ('Left',), 'R': ('Right',)}
def mk(*rs): return [tuple(sorted(r)) for r in rs]
MAC = {}
for dn, d in D.items():
    MAC['W' + dn] = mk(*[d] * 5)
    MAC['J' + dn] = mk(d + ('A',), d + ('A',), d, d, d)
    MAC['S' + dn] = mk(d + ('Down',), d + ('Down', 'B'), d + ('B',), d, d)
    MAC['X' + dn] = mk(d + ('A',), d + ('A', 'Down'), d + ('Down', 'B'), d + ('B',), d)     # jump + slash on row 3
    MAC['s' + dn] = mk(('Down',), ('Down', 'B'), ('B',), d, d)                               # slash, no dir on the swing
HIST = [()] * 150

def pod_dead(s):
    return s['t6'] != 38 or s['pst6'] == 60
def key(s, rows, L):
    lg = tuple((b, L.held[b], min(L.run[b], 5), min(L.t - (L.starts[b][-1] if L.starts[b] else -99), 6)) for b in ('A', 'B', 'Down', 'Left', 'Right'))
    return (s['x86'], s['xsub'], s['y8a'], s['vy'], s['vy_sub'], s['anim'], s['rf84'], s['inv95'], s['hp65'], s['eh6'], s['t6'],
            s['pst6'], s['boss'], s['ey6'], s['ex6'], lg)

prefix = rows_of(PREF) if PREF else []
fc = core65()
roots = []
for v in BFS:
    fc.load('c0'); fc.poke(0xBF, v)
    if prefix: fc.step(prefix)
    fc.save(f'r{v}')
L0 = K.Legal(HIST + prefix)
nodes = []   # (slots per bf, rows, Legal, states per bf, info)
for o in OFFS:
    rr = [('Right',)] * o
    Lx = L0.copy(); ok = True
    for r in rr:
        if Lx.why(r): ok = False; break
        Lx.push(r)
    if not ok: continue
    sl = []; sts = []
    for v in BFS:
        res = fc.run_batch(f'r{v}', [rr or [()]], record='last', keep=True, prefix=f'o{o}_{v}_') if rr else None
        if rr: sl.append(res[0].slot); sts.append(res[0].states[-1])
        else: sl.append(f'r{v}'); sts.append(None)
    nodes.append((sl, rr, Lx, sts, {'podk': None}))

def score(sts, info, nrows):
    sc = 0.0
    for s in sts:
        if s is None: continue
        dmg = 16 - s['hp65']
        X, y = s['x86'], s['y8a']
        if PH == 'pod':
            php = 0 if pod_dead(s) else s['eh6']
            zone = (66, 100) if php else (110, 140)
            dz = max(0, zone[0] - X, X - zone[1])
            sc += php * 20 + dz * 0.8 + dmg * DMGW + (max(0, 175 - s['ey6']) * 0.0)
        else:
            php = 0 if (pod_dead(s) or s['t6'] != 38) else s['eh6']
            hh = s['boss']
            if s['t6'] == 38: zone = (66, 100)
            else: zone = (110, 140)
            dz = max(0, zone[0] - X, X - zone[1])
            sc += php * 20 + hh * 20 + dz * 0.8 + dmg * DMGW
    return sc / len(sts)

best = None; t0 = time.time(); gen = 0
for blk in range(NB):
    cand = []
    for ni, (sl, rr, Lx, sts, info) in enumerate(nodes):
        ms = []
        for mn, m in MAC.items():
            L2 = Lx.copy(); ok = True
            for r in m:
                if L2.why(r): ok = False; break
                L2.push(r)
            if ok: ms.append((mn, m, L2))
        if not ms: continue
        per = []
        for bi, v in enumerate(BFS):
            res = fc.run_batch(sl[bi], [m for _, m, _ in ms], record='all', keep=True, prefix=f'g{gen}n{ni}b{bi}_',
                               stops=[(0x66, '==', 0), (0x65, '==', 0)])
            per.append(res)
        for mi, (mn, m, L2) in enumerate(ms):
            rs = [per[bi][mi] for bi in range(len(BFS))]
            dead = False; goal = []; inf = dict(info)
            for bi, r in enumerate(rs):
                st = r.states
                if not st or st[-1]['hp65'] < HPMIN or st[-1]['st6d'] != 21: dead = True; break
                if PH == 'kill':
                    if r.status == 1 and st[-1]['boss'] == 0: goal.append(len(rr) + r.rows_played)
                    elif r.status == 1: dead = True; break
                else:
                    pk = next((len(rr) + j + 1 for j, s in enumerate(st) if pod_dead(s)), None)
                    if pk is not None: goal.append(min(pk, inf.get(f'pk{bi}') or 9999)); inf[f'pk{bi}'] = goal[-1]
            if dead: continue
            nr = rr + (m[:rs[0].rows_played] if PH == 'kill' and len(goal) == len(BFS) else m)
            if len(goal) == len(BFS):
                g = max(goal)
                hp = min(r.states[-1]['hp65'] for r in rs)
                if PH == 'kill':
                    if best is None or (g, -hp) < (best[0], -best[1]):
                        best = (g, hp, nr, [r.states[-1]['t63'] for r in rs]); print('GOAL', g, 'hp', hp, 'T', best[3], 'gen', gen, flush=True)
                    continue
                else:
                    if best is None or (g, -hp) < (best[0], -best[1]):
                        best = (g, hp, list(nr), [r.states[-1]['hp65'] for r in rs]); print('POD', g, 'hp', hp, 'gen', gen, flush=True)
            cand.append(([r.slot for r in rs], nr, L2, [r.states[-1] for r in rs], inf, mn))
    # select
    cand.sort(key=lambda c: score(c[3], c[4], len(c[1])))
    seen = set(); new = []
    for c in cand:
        k = tuple(key(s, c[1], c[2]) for s in c[3])
        if k in seen: continue
        seen.add(k); new.append(c[:5])
        if len(new) >= W: break
    for i in range(len(BFS)): pass
    fc.drop_prefix(f'g{gen - 1}n') if gen else None
    keepslots = {s for c in new for s in c[0]}
    nodes = new; gen += 1
    if nodes:
        s0 = nodes[0][3][0]
        print(f'blk {blk} rows {len(nodes[0][1])} n {len(nodes)} cand {len(cand)} top sc {score(nodes[0][3], nodes[0][4], 0):.1f} '
              f'X {s0["x86"]} y {s0["y8a"]} hp {s0["hp65"]} pod {s0["eh6"]}/{s0["t6"]} heart {s0["boss"]} '
              f'{"".join(c[-1] for c in cand[:1])} t {time.time() - t0:.0f}s', flush=True)
    if not nodes: break
    if best and len(nodes[0][1]) > best[0] + (10 if PH == 'pod' else 0): break
    if len(nodes[0][1]) > MAXF: break
fc.close()
if best:
    print('BEST', best[0], 'hp', best[1], best[3])
    if OUT:
        with open(OUT, 'w', newline='\n') as f:
            f.write(f'# l65 beam65 {PH} bf {",".join(map(str, BFS))}: goal row {best[0]} (control row = 1), hp {best[1]}; prefix {PREF or "-"}\n')
            for r in best[2]: f.write(('+'.join(r) if r else '') + '\n')
        print('wrote', OUT)
