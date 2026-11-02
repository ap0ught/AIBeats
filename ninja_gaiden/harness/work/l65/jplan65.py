"""l65 jump planner for the 6-5 Demon (Mesen). A step = w pre-rows in direction pd, then a jump (A 2 f, air direction d) with the
legal slash-cancel cycle `Down | Down+B | B | - | -` from o rows after the jump press (repeating every 5), played until Ryu lands
(y 208 again) or the goal. Rows are checked with K.Legal (150 blank rows of history + prefix). Beam over steps.

python work/l65/jplan65.py --bf 243[,..] --goal pod|kill [--prefix f] [--width 6] [--levels 4] [--out f] [--ws 0,1,2,..] [--hpw 6]
"""
import sys, time
sys.path.insert(0, 'work/l65')
from lib65 import *
FLD['pst6'] = 0x42E
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
BFS = [int(v) for v in opt('--bf', '243').split(',')]
GOAL = opt('--goal', 'pod'); PREF = opt('--prefix', ''); W = int(opt('--width', '6')); LV = int(opt('--levels', '4'))
OUT = opt('--out', ''); WS = [int(v) for v in opt('--ws', '0,1,2,3,4,5,6,8,10,12,15').split(',')]
HPW = float(opt('--hpw', '6')); DMGW = float(opt('--dmgw', '30')); PDS = opt('--pds', 'R,-').split(',')
DS = opt('--ds', 'R,-,L').split(','); OS = [int(v) for v in opt('--os', '0,1,2,3,4').split(',')]
DM = opt('--dm', 'all,nob').split(',')
D = {'-': (), 'L': ('Left',), 'R': ('Right',)}
HIST = [()] * 150

def step_rows(w, pd, d, o, dm, n=56):
    if pd in D: rr = [tuple(sorted(D[pd]))] * w
    else:
        rr = []
        for sg in pd.split('.'): rr += [tuple(sorted(D[sg[0]]))] * int(sg[1:])
    hk = None
    if d.startswith('h'):
        kR, kL = map(int, d[1:].split('_')); hk = (kR, kL)
    for t in range(n):
        r = set(D[d]) if hk is None else set()
        if t < 2: r.add('A')
        k = t - o
        if hk is not None:
            if t >= hk[1]:
                r.add('Left'); rr.append(tuple(sorted(r))); continue
            if t < hk[0] and not (k >= 0 and k % 5 in (0, 1, 2)): r.add('Right')
        if k >= 0:
            ph = k % 5
            if ph == 0: r.add('Down')
            elif ph == 1: r |= {'Down', 'B'}
            elif ph == 2: r.add('B')
            if dm == 'nob' and ph in (0, 1, 2): r -= {'Left', 'Right'}
        rr.append(tuple(sorted(r)))
    return rr

def pod_dead(s): return s['t6'] != 38 or s['pst6'] == 60
def thp(s):
    p = 0 if pod_dead(s) else s['eh6']
    return p + (s['boss'] if s['st6d'] == 21 else 16)

prefix = rows_of(PREF) if PREF else []
fc = core65()
for v in BFS:
    fc.load('c0'); fc.poke(0xBF, v)
    if prefix: fc.step(prefix)
    fc.save(f'r{v}')
nodes = [([f'r{v}' for v in BFS], [], K.Legal(HIST + prefix), None, [])]
best = None; t0 = time.time()
cands_spec = []
for w in WS:
    for pd in (PDS if w else ['-']):
        for d in DS:
            for o in OS:
                for dm in DM:
                    if dm == 'nob' and (d == '-' or d.startswith('h')): continue
                    cands_spec.append((w, pd, d, o, dm))
print('cands per node', len(cands_spec), flush=True)
PRE2 = opt('--pre2', ''); DS0 = opt('--ds0', '-').split(',')
spec0 = cands_spec
if PRE2:
    nws, jrs = PRE2.split(':')
    nws = [int(x) for x in nws.split(',')]; j1, j2 = map(int, jrs.split('-'))
    spec0 = []
    for nw in nws:
        for jr in range(j1, j2 + 1):
            wt = jr - 1 - len(prefix) - nw
            if wt < 0: continue
            for d in DS0:
                for o in OS: spec0.append((nw + wt, f'R{nw}.-{wt}', d, o, 'all'))
    print('level-0 cands', len(spec0), flush=True)
for lv in range(LV):
    pool = []; nok = {}
    for ni, (sl, rr, Lx, _, spx) in enumerate(nodes):
        legal = []
        seen = set()
        for sp in (spec0 if lv == 0 else cands_spec):
            rows = step_rows(*sp)
            L2 = Lx.copy(); ok = True; nn = 0
            for r in rows:
                if L2.why(r): ok = False; break
                L2.push(r); nn += 1
            if not ok and nn < sp[0] + 12: continue
            rows = rows[:nn]
            if tuple(rows) in seen: continue
            seen.add(tuple(rows)); legal.append((sp, rows))
        print("node", ni, "legal", len(legal), flush=True); per = []
        for bi, v in enumerate(BFS):
            per.append(fc.run_batch(sl[bi], [r for _, r in legal], record='all', stops=[(0x66, '==', 0), (0x65, '==', 0)]))
        for ci, (sp, rows) in enumerate(legal):
            w = sp[0]
            ends = []; bad = False; kills = []; pods = []; look = []
            for bi in range(len(BFS)):
                st = per[bi][ci].states
                if not st: bad = True; break
                # landing: first index >= w + 6 with y 208 (or the stop)
                air = next((i for i in range(w, len(st)) if st[i]['rf84'] & 4), None)
                if air is None and per[bi][ci].status != 1: bad = True; break
                land = next((i for i in range((air or w) + 4, len(st)) if not (st[i]['rf84'] & 4)), len(st) - 1)
                if per[bi][ci].status == 1 and st[-1]['boss'] == 0 and st[-1]['hp65'] > 0 and st[-1]['st6d'] == 21:
                    kills.append(len(rr) + len(st)); land = len(st) - 1
                elif per[bi][ci].status == 1 or st[land]['st6d'] != 21: bad = True; break
                pk = next((len(rr) + i + 1 for i in range(land + 1) if pod_dead(st[i])), None)
                pods.append(pk)
                ends.append((land, st[land]))
                look.append(min(x['hp65'] for x in st[:min(len(st), land + 9)]))
            if bad: continue
            land = max(e[0] for e in ends)
            hp = min(look)
            if hp < 1: continue
            if GOAL == 'kill' and len(kills) == len(BFS):
                g = max(kills)
                if best is None or (g, -hp) < (best[0], -best[1]):
                    best = (g, hp, rr + rows[:g - len(rr)], spx + [sp]); print('KILL', len(prefix) + g, 'hp', hp, 'lv', lv, sp, flush=True)
                continue
            if GOAL == 'pod' and all(p is not None for p in pods):
                g = max(pods)
                if best is None or (g, -hp) < (best[0], -best[1]):
                    best = (g, hp, rr + rows[:land + 1], spx + [sp]); print('POD', g, 'hp', hp, 'lv', lv, sp, flush=True)
            nrows = len(rr) + land + 1
            sc = nrows + HPW * sum(thp(e[1]) for e in ends) / len(BFS) + DMGW * (16 - hp)
            pool.append((sc, ni, sp, land + 1, hp, [e[1] for e in ends]))
            nok[ni] = nok.get(ni, 0) + 1
    pool.sort(key=lambda q: q[0])
    print('lv', lv, 'ok per node', nok, 'best per node', {ni: min(q[0] for q in pool if q[1] == ni) for ni in nok}, flush=True)
    # dedupe by end key, keep W
    sel = []; seen = set()
    for q in pool:
        s = q[5][0]
        k = (q[1] if False else 0, s['x86'], s['y8a'], s['eh6'], s['boss'], s['hp65'], len(nodes[q[1]][1]) + q[3])
        if k in seen: continue
        seen.add(k); sel.append(q)
        if len(sel) >= W: break
    new = []
    for j, (sc, ni, sp, n, hp, ends) in enumerate(sel):
        sl, rr, Lx, _, spx = nodes[ni]
        full = step_rows(*sp)
        def held1(rows, n):
            if n >= len(rows): return False
            last = rows[n - 1]
            for b in last:
                c = 0; i = n - 1
                while i >= 0 and b in rows[i]: c += 1; i -= 1
                if c < 2: return True
            return False
        while held1(full, n): n += 1
        rows = full[:n]
        L2 = Lx.copy()
        for r in rows: L2.push(r)
        nsl = []
        for bi in range(len(BFS)):
            res = fc.run_batch(sl[bi], [rows], record='last', keep=True, prefix=f'L{lv}j{j}b{bi}_')
            nsl.append(res[0].slot)
        new.append((nsl, rr + rows, L2, ends, spx + [sp]))
        s = ends[0]
        print(f'lv {lv} #{j} sc {sc:.1f} rows {len(rr) + n} step {sp} X {s["x86"]} y {s["y8a"]} hp {hp} pod {s["eh6"] if not pod_dead(s) else 0} heart {s["boss"]} t {time.time() - t0:.0f}s', flush=True)
    nodes = new
    if not nodes: break
    if best and GOAL == 'kill' and min(len(n[1]) for n in nodes) >= best[0]: break
fc.close()
if best:
    print('BEST', len(prefix) + best[0], 'hp', best[1], 'steps', best[3])
    if OUT:
        with open(OUT, 'w', newline='\n') as f:
            f.write(f'# l65 jplan65 {GOAL} bf {",".join(map(str, BFS))}: goal row {len(prefix) + best[0]} (control row = 1), hp {best[1]}; '
                    f'prefix {PREF or "-"} ({len(prefix)} rows); steps {best[3]}\n')
            for r in prefix + best[2]: f.write(('+'.join(r) if r else '') + '\n')
        print('wrote', OUT)
