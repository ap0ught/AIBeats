"""Frame-synchronous legal beam on Mesen: every frame each node tries every row of an alphabet (legalized by its own
Enforcer copy); children deduped by game state; best W by a progress score; first node reaching the goal wins.
    python -u work/l22f/fbeam.py <hist file> <mst> <goal> <tag> [--alpha "Right|Left|A+Right|A+Left|-|A|Up"]
        [--width 64] [--frames 120] [--minhp 0] [--score z|x|y] [--seed rows file] [--npmin 0]
goal: z:GX:YMAX (abs X >= GX and y <= YMAX) | room:R | x:R:ge|le:GX[:ylo:yhi] | stage
score: progress used to rank nodes (z: dx + 3*dy to the goal box; x/xl: abs X right/left; y: height)
Out: states/tmp/fb_<tag>.inputs.txt (rows after the history, to the goal frame)"""
import sys, time, threading
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L
from ng import fastcore as F
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
ALPHA = opt('--alpha', 'Right|Left|A+Right|A+Left|-|A|Up|B+Right')
W = opt('--width', 64); NF = opt('--frames', 120); MINHP = opt('--minhp', 0); SC = opt('--score', 'z')
NPMIN = opt('--npmin', 0); KEEP = opt('--keepitem', 133); ITEMS = [int(q) for q in opt('--items', '').split(',') if q]; JSBY = opt('--jsby', 0); YMAX = opt('--ymax', 999); NPQ = opt('--npq', 0); NEEDS = [tuple(map(int, q.split(':'))) for q in opt('--needs', '').split(',') if q]; NEED = opt('--need', 10); LANT = [tuple(map(int, q.split(':'))) for q in opt('--lant', '1616:5,1552:5,1088:10,800:5').split(',') if q]; XW = opt('--xw', 0.0); EKW = opt('--ek', 0.0); NPW = opt('--npw', 0.0); ZT = opt('--zt', ''); PT = opt('--pt', ''); LAG = opt('--lag', 0); NPEQ = opt('--npeq', -1); WPS = [tuple(map(int, q.split(':'))) for q in opt('--wps', '').split(',') if q]; RAD = opt('--rad', 6); FREEZE = set(int(q) for q in opt('--freeze', '').split(',') if q)
def wd(s, w): return abs(C.abs_x(s) - w[0]) + abs(s['y'] - w[1])
if SC == 'tas':
    sys.path.insert(0, 'ng/stages'); import a56_common as A; TT = A.tas_trace()
hf, mst, goal, tag = a[:4]
hist = C.rows_of(hf)
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
AL = [row(x) for x in ALPHA.split('|')]
g = goal.split(':')
def reached(s, st0):
    if g[0] == 'stage': return s['stage'] != st0
    if s['stage'] != st0: return False
    if g[0] == 'room': return s['room'] == int(g[1])
    if g[0] == 'item': return s['item'] == int(g[1])
    if g[0] == 'g': return s['room'] == int(g[1]) and int(g[2]) <= C.abs_x(s) <= int(g[3]) and s['y'] == int(g[4]) and (s['coll'] & 16) != 0
    if g[0] == 'z': return C.abs_x(s) >= int(g[1]) and s['y'] <= int(g[2]) and s['room'] == R0
    if s['room'] != int(g[1]): return False
    x = C.abs_x(s)
    ok = x <= int(g[3]) if g[2] == 'le' else x >= int(g[3])
    if ok and len(g) > 4: ok = int(g[4]) <= s['y'] <= int(g[5])
    return ok
def score(s):
    x = C.abs_x(s) + s['xsub'] / 256.0
    if SC == 'z':
        zg = ZT.split(':') if ZT else g[1:3]
        v = max(0, int(zg[0]) - x) + 3 * max(0, s['y'] - int(zg[1]))
    elif SC == 'p':
        tx, ty = map(int, PT.split(':')); v = abs(x - tx) + 3 * abs(s['y'] - ty)
    elif SC == 'tas':
        t = TT[s['frame'] - LAG]
        v = abs(x - C.abs_x(t)) + abs(s['y'] - t['y']) + (0 if t['room'] == s['room'] else 500)
    elif SC == 'wp':
        pw = s['_wp']
        if pw >= len(WPS): v = 0
        else:
            v = wd(s, WPS[pw]) + sum(abs(WPS[i][0]-WPS[i+1][0]) + abs(WPS[i][1]-WPS[i+1][1]) for i in range(pw, len(WPS)-1))
    elif SC == 'x': v = -x
    elif SC == 'xl': v = x
    elif SC == 'y': v = s['y']
    else: v = 0
    v += EKW * bin(s.get('eact', 0)).count('1')
    return v - NPW * s['ninpo'] + (0 if s['hp'] >= MINHP else 1e6) + XW * (16 - s['hp'])
NW = int(__import__("os").environ.get("FB_NW", "2"))
FLD = dict(F._fields()); FLD['eact'] = 0x73
cores = [F.FastCore(boot_rows=None, ticks=True, fields=FLD) for _ in range(NW)]
data = open(mst, 'rb').read()
for c in cores: c.put('s0', data); c.load('s0')
NP0 = cores[0].ram()[0x64]; st0 = cores[0].ram()[0x6D]; R0 = cores[0].ram()[0x6E]; LV0 = cores[0].ram()[0x76] if False else None
f0 = len(hist)
# node: (worker, slot, rows tuple, enforcer, state)
base = L.Enforcer(hist[-1900:])
nodes = [(0, 's0', (), base, None), ] if True else []
# put the start on worker 1 too
nodes_w = {0: 's0', 1: 's0'}
stops = [(0x6D, 'changed', 0), (0x6E, 'changed', 0), (0x65, '==', 0)]
t0 = time.time(); win = None; gen = 0
LIVES = None
for fr in range(NF):
    gen += 1
    jobs = {i: [] for i in range(NW)}
    for ni, (wk, slot, rows, en, s) in enumerate(nodes):
        kids = {}
        frz = (f0 + fr + 1) in FREEZE
        last = rows[-1] if rows else tuple(sorted(hist[-1]))
        for w in ([last] if frz else AL):
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if frz and lg != tuple(sorted(last)): continue
            if lg in kids: continue
            kids[lg] = e2
        wk2 = wk if fr > 0 else ni % NW
        jobs[wk2].append((ni, slot, list(kids.items())))
    out = []
    lock = threading.Lock()
    def work(wi):
        c = cores[wi]
        res = []
        for ni, slot, kl in jobs[wi]:
            rr = c.run_batch(slot, [[lg] for lg, _ in kl], record='all', stops=stops, keep=True,
                             prefix=f'g{gen}n{ni}_')
            for (lg, e2), r in zip(kl, rr):
                if r.rows_played == 0 or not r.states: continue
                st = r.states[-1]; st['frame'] = f0 + len(nodes[ni][2]) + 1
                if any((q['dead'] & 0x80) for q in r.states): st['dead'] |= 0x80
                pw = nodes[ni][4]['_wp'] if nodes[ni][4] else 0
                while pw < len(WPS) and wd(st, WPS[pw]) <= RAD: pw += 1
                st['_wp'] = pw
                par = nodes[ni][4]
                col = par['_col'] if par else frozenset()
                np0 = par['ninpo'] if par else NP0
                d = st['ninpo'] - np0
                if d > 0:
                    cand = [l for l in LANT if l not in col and l[1] == d]
                    if cand:
                        col = col | {min(cand, key=lambda l: abs(l[0] - C.abs_x(st)))}
                st['_col'] = col
                st['_pot'] = sum(l[1] for l in LANT if l not in col and l[0] <= C.abs_x(st) + 16)
                res.append((wi, r.slot, nodes[ni][2] + (lg,), e2, st))
        with lock: out.extend(res)
    th = [threading.Thread(target=work, args=(wi,)) for wi in range(NW)]
    for t in th: t.start()
    for t in th: t.join()
    # goal?
    if LIVES is None and out: LIVES = max(n[4]['lives'] for n in out)
    hits = [n for n in out if not (n[4]['dead'] & 0x80) and n[4]['item'] != 0 and ((n[4]['item'] == 133) if ITEMS else (not KEEP or n[4]['item'] == KEEP)) and (LIVES is None or n[4]['lives'] >= LIVES) and n[4]['hp'] >= MINHP and n[4]['ninpo'] >= NPMIN and (NPEQ < 0 or n[4]['ninpo'] == NPEQ) and reached(n[4], st0)]
    if hits:
        hits.sort(key=lambda n: (-n[4]['hp'], -n[4]['ninpo']))
        win = hits[0]; break
    seen = set(); nxt = []; ovf = []; cnt = {}
    out.sort(key=lambda n: (score(n[4]), -n[4]['hp']))
    for n in out:
        s = n[4]
        if ITEMS:
            if s['item'] not in ITEMS: continue
            if C.abs_x(s) < JSBY and s['item'] != 133: continue
        elif KEEP and s['item'] != KEEP: continue
        nd = max([NEED] + [n_ for x_, n_ in NEEDS if C.abs_x(s) > x_])
        if s['ninpo'] + s['_pot'] < nd: continue
        if s['y'] > YMAX: continue
        if s['hp'] == 0 or (s['dead'] & 0x80) or s['stage'] != st0 or s['hp'] < MINHP or s['item'] == 0 or (LIVES is not None and s['lives'] < LIVES): continue
        key = (s['x'], s['xsub'], s['y'], s['vy'], s['vy_sub'] if 'vy_sub' in s else 0, s['coll'], s['anim'],
               s['scroll'], s['room'], n[2][-1], s.get('eact', 0), s['hp'], s['ninpo'], s.get('_wp', 0), s['_col'])
        if key in seen: continue
        seen.add(key)
        if NPQ and cnt.get(s['ninpo'], 0) >= NPQ:
            ovf.append(n); continue
        cnt[s['ninpo']] = cnt.get(s['ninpo'], 0) + 1
        nxt.append(n)
        if len(nxt) >= W: break
    if len(nxt) < W: nxt += ovf[:W - len(nxt)]
    # balance: node i goes to worker i % NW (move its slot if needed)
    bal = []
    for i, n in enumerate(nxt):
        dst = i % NW
        if n[0] != dst:
            cores[dst].put(n[1], cores[n[0]].get(n[1]))
            n = (dst,) + tuple(n[1:])
        bal.append(n)
    nxt = bal
    # drop old slots
    for wi in range(NW):
        if gen >= 2: cores[wi].drop_prefix(f'g{gen-1}n')
    nodes = nxt
    if nodes: lastbest = nodes[0]
    if True:
        b = nodes[0][4] if nodes else None
        print(f'{time.time()-t0:5.0f}s frame {f0+fr+1} nodes {len(nodes)} best X {C.abs_x(b)} y {b["y"]} hp {b["hp"]} np {b["ninpo"]} it {b["item"]} pot {b["_pot"]} sc {score(b):.1f}' if b else 'empty', flush=True)
    if not nodes: break
for c in cores: c.close()
if win:
    s = win[4]
    print(f'GOAL at frame {f0+len(win[2])} rows {len(win[2])} X {C.abs_x(s)} y {s["y"]} room {s["room"]} hp {s["hp"]} np {s["ninpo"]}')
    C.write_inputs(f'work/l22a/fb_{tag}.inputs.txt', list(win[2]), f'fbeam {tag} goal {goal}')
else:
    print('no goal')
    try:
        C.write_inputs(f'work/l22a/fb_{tag}_part.inputs.txt', list(lastbest[2]), f'fbeam {tag} partial best')
        print('partial rows', len(lastbest[2]))
    except NameError: pass
