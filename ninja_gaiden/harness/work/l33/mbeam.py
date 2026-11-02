"""3-3 macro beam: steps = (walk, optional jump, turn, Fire Wheel / slash), every candidate replayed from 3-3 control.
    python -u work/l33/mbeam.py <tag> <out> --prefix <rows file> [--K 12] [--steps 5] [--slash 1]
A node = legal rows + the frame Ryu is free again. Steps from a node (t0 = its end):
  G: walk d (Right/Left/-) k rows, face f (2 rows of f), Up+B 2 rows, blanks until free (anim != 8) ;
  J: walk d k rows, jump A+d 2 rows, hold d m rows, face f 2 rows, Up+B 2 rows, blanks until landing ;
  S: (--slash) walk d k, jump, hold d m, B every 5 rows (n slashes) until landing.
Every candidate gets 24 blank rows of rollout after its step end (flames resolve). Node value = boss hp after the
rollout; keep the K best per (boss hp) by (end frame, -x closeness to --xgoal after --xfrom).
Kill: any candidate whose rows kill (M = kill + 3*(timer+np)); best M saved to work/l33/mb_<out>.inputs.txt."""
import sys, json, itertools, time
sys.path.insert(0, 'work/l33')
from sw import Ctx, spec, C
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
K = opt('--K', 12); STEPS = opt('--steps', 5); PRE = opt('--prefix', ''); SL = opt('--slash', 1)
XG = opt('--xgoal', 0); XF = opt('--xfrom', 999); KS = opt('--ks', '0,2,4,6,8,10,13,16,20,25,30')
MS = opt('--ms', '0,3,6,10,14,18,24,30'); TMAXR = opt('--tmax', 200)
tag, out = a[:2]
KL = [int(q) for q in KS.split(',')]; ML = [int(q) for q in MS.split(',')]
X = Ctx(tag)
pre = [tuple(sorted(r)) for r in C.rows_of(PRE)] if PRE else []
R = ('Right',); Lf = ('Left',)
def drow(d): return (d,) if d else ()
def steps_from(rows):
    out = []
    for d in ('Right', 'Left', None):
        for k in KL:
            if d is None and k > 16: continue
            w0 = [drow(d)] * k
            for f in ('Left', 'Right'):
                out.append(('G', d, k, f, 0, w0 + [(f,), (f,)] + spec('Up+B*2')))
                for m in ML:
                    wj = w0 + [tuple(sorted(drow(d) + ('A',)))] * 2 + [drow(d)] * m
                    out.append(('J', d, k, f, m, wj + [(f,), (f,)] + spec('Up+B*2')))
            if SL:
                for m in (0, 2, 4, 8):
                    wj = w0 + [tuple(sorted(drow(d) + ('A',)))] * 2 + [drow(d)] * m
                    for n in (1, 2, 3):
                        ws = list(wj)
                        for _ in range(n):
                            ws += [tuple(sorted(drow(d) + ('B',)))] * 2 + [drow(d)] * 3
                        out.append(('S', d, k, None, m, ws))
    return out
def proc(rows, s, r, sts, nst, pool):
    global best
    if r['kill']:
        if best is None or r['M'] < best[0]:
            best = (r['M'], r['rows'][:r['kill']], s)
            print(f'  KILL row {r["kill"]} M {r["M"]} np {r["np"]} step {s[:5]}', flush=True)
            C.write_inputs(f'work/l33/mb_{out}.inputs.txt', list(r['rows'][:r['kill']]), f'mbeam {tag} M {r["M"]}')
        return
    if r['hp'] <= 0 or len(sts) < nst: return
    # node end: first frame after the step where Ryu is free (anim not 8 and on the ground) within the rollout
    end = None
    for i in range(nst, len(sts)):
        q = sts[i]
        if q['anim'] in (0, 1) and q['y'] == 208:
            end = i + 1; break
    if end is None: return
    hpb = sts[-1]['bosshp']
    if sts[end - 1]['bosshp'] > hpb and False: pass
    x = sts[end - 1]['x']; npn = sts[end - 1]['ninpo']
    xs = abs(x - XG) if (XG and len(rows) + end >= XF) else 0
    lr = list(r['rows'][:len(rows) + end]); end = len(rows) + end
    key = (hpb, npn)
    pool.setdefault(key, []).append((end + xs / 1.5 + (3 if r['rhit'] else 0), lr, s, end, x, hpb, npn, r['rhit'][:2]))

best = None
nodes = [(pre, None)]
t0 = time.time()
for st in range(STEPS):
    pool = {}
    ncand = 0
    for rows, _ in nodes:
        ss = [s for s in steps_from(rows) if len(rows) + len(s[5]) <= TMAXR]
        ncand += len(ss)
        res = X.run_from(rows, [s[5] + [()] * 40 for s in ss])
        for s, r in zip(ss, res):
            sts = r['sts']; nst = len(s[5])
            proc(rows, s, r, sts, nst, pool)
    print(f'step {st+1}: {ncand} candidates from {len(nodes)} nodes', flush=True)
    nn = []
    for key in sorted(pool, key=lambda k: (k[0], -k[1])):
        L = sorted(pool[key], key=lambda q: q[0])
        seen = set()
        for q in L:
            sig = (q[3], q[4])
            if sig in seen: continue
            seen.add(sig); nn.append(q)
            if len([z for z in nn if (z[5], z[6]) == key]) >= K: break
        if len(nn) >= 4 * K: break
    for q in nn[:8]:
        print(f'   boss {q[5]} np {q[6]} end {q[3]} x {q[4]} rhit {q[7]} step {q[2][:5]}', flush=True)
    nodes = [(q[1], q) for q in nn]
    print(f'  {time.time()-t0:.0f}s', flush=True)
    if not nodes: break
X.close()
print('BEST', best[0] if best else None)
