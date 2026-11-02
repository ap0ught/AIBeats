"""3-2 second half: bird-aware legal frame beam on Mesen (from work/l31t/tbeam.py).
Keeps the type-11 bird alive (penalty if it is gone while Ryu X < --birdby), keeps diversity over the bird's phase
(class = bird rel-x bucket x speed bucket, at most --cap nodes per class), score = estimated frames to the goal.
    python -u work/l32b/pbeam.py <hist> <mst> <tag> [--goal 1950:97] [--width 300] [--frames 520] [--cap 6]
        [--alpha 'Right|A+Right|-|Left|A+Left|B+Right'] [--birdby 1780] [--minhp 7] [--hpw 0.5] [--npset 22,27]
        [--hgx 1904 --hgy 96] [--fix rowsfile]   (--fix: play these rows first, then beam)
Out: work/l32b/pb_<tag>.inputs.txt (rows after the history, to the goal frame)."""
import sys, time, threading, os
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L
from ng import fastcore as F
sys.path.insert(0, 'work/l31t'); import fcka
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
ALPHA = opt('--alpha', 'Right|A+Right|-|Left|A+Left|B+Right')
W = opt('--width', 300); NF = opt('--frames', 520); CAP = opt('--cap', 6); BIRDBY = opt('--birdby', 1780)
MINHP = opt('--minhp', 7); HPW = opt('--hpw', 0.5); GOAL = opt('--goal', '1950:97')
NPSET = [int(q) for q in opt('--npset', '22,27').split(',') if q]
HGX = opt('--hgx', 1904); HGY = opt('--hgy', 96); FIX = opt('--fix', ''); BUCK = opt('--buck', 6)
NW = opt('--workers', 2); SEED = opt('--seed', ''); CELL = opt('--cell', 0)
GX, GY = map(int, GOAL.split(':'))
hf, mst, tag = a[:3]
hist = C.rows_of(hf)
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
AL = [row(x) for x in ALPHA.split('|')]
FLD = dict(F._fields()); FLD['eb'] = 0x73
for j in range(8):
    FLD[f't{j}'] = 0x400 + j; FLD[f'ex{j}'] = 0x460 + j; FLD[f'ey{j}'] = 0x480 + j
    FLD[f'es{j}'] = 0x450 + j; FLD[f'ef{j}'] = 0x448 + j; FLD[f'eq{j}'] = 0x458 + j
F.LUA = __import__('pathlib').Path('work/l31t/fastcore_gc.lua').resolve()
def bird(s):
    """(rel x, speed in 1/256, y) of the type-11 bird nearest Ryu, or None"""
    X = C.abs_x(s); scr = X - s['x']; best = None
    for j in range(8):
        if s['eb'] >> j & 1 and s[f't{j}'] == 11:
            sp = s[f'es{j}']; sp = sp - 256 if sp >= 128 else sp
            b = (scr + s[f'ex{j}'] - X, sp * 256 + s[f'ef{j}'], s[f'ey{j}'], s[f'eq{j}'])
            if best is None or abs(b[0]) < abs(best[0]): best = b
    return best
def est(s):
    X = C.abs_x(s) + s['xsub'] / 256.0; y = s['y']
    if X >= HGX - 16 and y <= HGY:
        v = max(0.0, (GX - X) / 1.5)
    else:
        v = max((GX - X) / 1.5, (HGX - X) / 1.5 + (max(0, y - HGY) / 1.8 if X > 1700 else 0.0))
    return v
def score(s):
    v = est(s) + HPW * (16 - s['hp'])
    if C.abs_x(s) < BIRDBY and C.abs_x(s) > 1330 and bird(s) is None: v += 1000
    return v
def item_ok(s):
    return s['item'] == 128 and not s.get('timestop', 0) and s['ninpo'] in NPSET
data = open(mst, 'rb').read()
fixrows = C.rows_of(FIX) if FIX else []
def make_cores():
    cs = [F.FastCore(boot_rows=None, ticks=True, fields=FLD) for _ in range(NW)]
    for c in cs:
        c.put('s0', data); c.load('s0')
        if fixrows:
            c.step(fixrows, record='last'); c.save('s0')
        c._ka_slot = 's0'
    return cs
cores = make_cores()
r0 = cores[0].ram(); st0 = r0[0x6D]; LIVES = r0[0x76]
hist2 = list(hist) + list(fixrows)
f0 = len(hist2)
base = L.Enforcer(hist2[-1900:])
nodes = [(0, 's0', (), base, None)]
stops = [(0x6D, 'changed', 0), (0x6E, 'changed', 0), (0x65, '==', 0)]
t0 = time.time(); win = None; gen = 0
def rebuild(nl, why):
    global cores
    print(f'REBUILD at gen {gen} ({str(why)[:80]}), {len(nl)} nodes', flush=True)
    for c in cores:
        fcka.forget(c)
        try: c.proc.kill()
        except Exception: pass
    time.sleep(1)
    cores = make_cores()
    res = []
    for i, n in enumerate(nl):
        w = i % NW
        if not n[2]:
            res.append((w, 's0') + tuple(n[2:])); continue
        rr = cores[w].run_batch('s0', [list(n[2])], record='last', keep=True, prefix=f'm{gen}_R{i}_')
        res.append((w, rr[0].slot) + tuple(n[2:]))
    return res
def expand(nodes, gen):
    out = []; errs = []; lock = threading.Lock()
    jobs = {i: [] for i in range(NW)}
    for ni, (wk, slot, rows, en, s) in enumerate(nodes):
        kids = {}
        for w in AL:
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if lg in kids: continue
            kids[lg] = e2
        jobs[wk].append((ni, slot, list(kids.items())))
    def work(wi):
        try:
            c = cores[wi]; res = []
            for ni, slot, kl in jobs[wi]:
                rr = c.run_batch(slot, [[lg] for lg, _ in kl], record='all', stops=stops, keep=True, prefix=f'g{gen}n{ni}_')
                for (lg, e2), r in zip(kl, rr):
                    if r.rows_played == 0 or not r.states: continue
                    st = r.states[-1]; st['frame'] = f0 + len(nodes[ni][2]) + 1
                    res.append((wi, r.slot, nodes[ni][2] + (lg,), e2, st))
            with lock: out.extend(res)
        except Exception as ex:
            with lock: errs.append(ex)
    th = [threading.Thread(target=work, args=(wi,)) for wi in range(NW)]
    for t in th: t.start()
    for t in th: t.join()
    return out, errs
def ok(s):
    return (s['hp'] >= MINHP and not (s['dead'] & 0x80) and s['stage'] == st0 and s['lives'] >= LIVES and item_ok(s))
for fr in range(NF):
    gen += 1
    for _try in range(5):
        out, errs = expand(nodes, gen)
        if not errs: break
        nodes = rebuild(nodes, errs[0])
    else:
        raise SystemExit('too many Mesen failures')
    hits = [n for n in out if ok(n[4]) and C.abs_x(n[4]) >= GX and n[4]['y'] <= GY]
    if hits:
        hits.sort(key=lambda n: (-n[4]['hp'], -C.abs_x(n[4])))
        win = hits[0]; break
    out = [n for n in out if ok(n[4])]
    for n in out: n[4]['_sc'] = score(n[4])
    out.sort(key=lambda n: n[4]['_sc'])
    seen = set(); nxt = []; ovf = []; cnt = {}
    for n in out:
        s = n[4]; b = bird(s)
        key = (s['x'], s['xsub'], s['y'], s['vy'], s.get('vy_sub', 0), s['coll'], s['anim'], s['rflags'], s['scroll'],
               n[2][-1], s['eb'], s['hp'], s['ninpo'], s['inv'] > 0, b)
        if key in seen: continue
        seen.add(key)
        ck = ((C.abs_x(s) // CELL, s['y'] // CELL, s['anim']) if CELL else None) if b is None else (b[0] // BUCK, b[1] // 64, b[2] // 8)
        if cnt.get(ck, 0) >= CAP:
            ovf.append(n); continue
        cnt[ck] = cnt.get(ck, 0) + 1
        nxt.append(n)
        if len(nxt) >= W: break
    if len(nxt) < W: nxt += ovf[:W - len(nxt)]
    try:
        bal = []; cnt_w = [0] * NW
        for n in nxt: cnt_w[n[0]] += 1
        cap = (len(nxt) * 13) // (10 * NW) + 1
        for mi, n in enumerate(nxt):
            if cnt_w[n[0]] > cap:
                dst = min(range(NW), key=lambda q: cnt_w[q])
                if cnt_w[dst] < cap:
                    rr = cores[dst].run_batch('s0', [list(n[2])], record='last', keep=True, prefix=f'm{gen}_{mi}_')
                    cnt_w[n[0]] -= 1; cnt_w[dst] += 1
                    n = (dst, rr[0].slot) + tuple(n[2:])
            bal.append(n)
        keepset = set((n[0], n[1]) for n in bal)
        for wi in range(NW):
            if gen >= 2: cores[wi].drop_prefix(f'g{gen-1}n'); cores[wi].drop_prefix(f'm{gen-1}_')
            dead = [n[1] for n in out if n[0] == wi and (wi, n[1]) not in keepset]
            for q in range(0, len(dead), 150):
                cores[wi].drop(*dead[q:q + 150])
        nxt = bal
    except Exception as ex:
        nxt = rebuild(nxt, ex)
    nodes = nxt
    if not nodes: print('empty'); break
    lastbest = nodes[0]; b = nodes[0][4]
    if fr % 5 == 0 or fr < 3:
        print(f'{time.time()-t0:5.0f}s frame {f0+fr+1} nodes {len(nodes)} cls {len(cnt)} best X {C.abs_x(b)} y {b["y"]} hp {b["hp"]} np {b["ninpo"]} bird {bird(b)} sc {b["_sc"]:.1f}', flush=True)
for c in cores:
    try: c.close()
    except Exception: pass
if win:
    s = win[4]
    print(f'GOAL at frame {f0+len(win[2])} rows {len(fixrows)}+{len(win[2])} X {C.abs_x(s)} y {s["y"]} hp {s["hp"]} np {s["ninpo"]} it {s["item"]} sub62 {s["hudphase"]}')
    C.write_inputs(f'work/l32b/pb_{tag}.inputs.txt', list(fixrows) + list(win[2]), f'pbeam {tag} goal {GOAL} from {mst}')
else:
    print('no goal')
    try:
        C.write_inputs(f'work/l32b/pb_{tag}_part.inputs.txt', list(fixrows) + list(lastbest[2]), f'pbeam {tag} partial')
    except NameError: pass
