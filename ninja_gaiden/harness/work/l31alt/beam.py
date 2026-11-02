"""3-1 item-plan beam (frame-synchronous, legal per row, Mesen). Start: 3-1 control (lock_31_ctl.mst) + optional
prefix rows. Buckets by (phase, throws, ammo) so FW-lantern / Star states are not crowded out by pure-X nodes.
    python -u work/l31alt/beam.py <tag> [--T 1] [--width 32] [--frames 1700] [--pre rows.txt] [--minhp 0]
      [--alpha ...] [--goal stage|fw|x:N] [--xw 0] [--star 1]
phase: 0 nothing, 1 Star held, 2 FW lantern broken (item falling/lying), 3 FW held ($C9 128).
Rules: never the hourglass (timestop), Up+B only with the Star and ammo, never lose the FW once held, throws <= T,
goal 'stage' = stage change with FW held and throws == T; goal 'fw' = FW held (and throws == T);
goal 'x:N' = X >= N (no item condition; for early segments).
Out: work/l31alt/b_<tag>.txt (rows after control, incl. prefix)"""
import sys, time, threading
sys.path.insert(0, 'work/l31alt')
from lib import *
a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d


T = opt('--T', 1); W = opt('--width', 32); NF = opt('--frames', 1700); PRE = opt('--pre', ''); MINHP = opt('--minhp', 0)
ALPHA = opt('--alpha', 'Right|A+Right|B+Right|A+B+Right|-|A|Left|A+Left|B|B+Up'); GOAL = opt('--goal', 'stage')
XW = opt('--xw', 0.0); STAR = opt('--star', 1 if T > 0 else 0); NOSTARX = opt('--nostarx', 820); NOFWX = opt('--nofwx', 1290)
MAXNP = opt('--maxnp', 99); YCAP = opt('--ycap', 0); AMMOX = opt('--ammox', 600); YW = opt('--yw', 0.0); KW = opt('--kw', 0.0); WASTE = opt('--waste', 1); PT = opt('--pt', ''); DBG = opt('--dbg', 0); THROWX = opt('--throwx', 0); DUMP = opt('--dump', 50); NW = opt('--nw', 2); BUCKN = opt('--npbuck', 1); MINNP = opt('--minnp', 0)
tag = a[0]
AL = [row(x) for x in ALPHA.split('|')]
fld = dict(FLD); fld['lmask'] = 0xC0; fld['timestop'] = 208
for j in range(4):
    fld[f'ls{j}'] = 0x4D1 + j; fld[f'li{j}'] = 0x4C9 + j
pre = [tuple(x) for x in (C.rows_of(PRE) if PRE else [])]
# Mesen's Lua dies when a core idles > ~1 s between commands (l31t/fcka.py): build the prefix state on one core,
# then create the others and copy the state.
c0 = F.FastCore(boot_rows=None, ticks=True, fields=fld)
c0.put('s0', open(MST, 'rb').read()); c0.load('s0')
if pre: c0.step(pre, record='last')
c0.save('s0'); m0 = c0.ram(); data = c0.get('s0')
cores = [c0]
for _ in range(NW - 1):
    c = F.FastCore(boot_rows=None, ticks=True, fields=fld); c.put('s0', data); c.load('s0'); c0.ram(); cores.append(c)


def fwlant(s):
    for j in range(4):
        if s['lmask'] & (1 << j) and (s[f'li{j}'] & 15) == 10 and (s[f'ls{j}'] & 4) and not (s[f'ls{j}'] & 8): return True
    return False


def phase(s):
    if s['item'] == 128: return 3
    if fwlant(s): return 2
    if s['item'] == 129: return 1
    return 0


TT = A.tas_trace(); YT = {}
for _f in range(TAS_CTL, TAS_CTL + 1400):
    _t = TT[_f]
    if _t['stage'] != 5: break
    _x = C.abs_x(_t)
    if _x not in YT: YT[_x] = _t['y']
_last = 192
YTX = []
for _x in range(0, 2100):
    _last = YT.get(_x, _last); YTX.append(_last)


def score(s):
    x = C.abs_x(s)
    if PT and phase(s) < 2:
        tx, ty = map(int, PT.split(':'))
        return 10000 + abs(x - tx) + abs(s['y'] - ty)
    return -(x + s['xsub'] / 256.0) - KW * (s['score_hi'] * 100 + s['score_lo'] - PTS0) + XW * (16 - s['hp']) + (YW * abs(s['y'] - YTX[min(max(x, 0), 2099)]) if YW else 0)


PTS0 = m0[0x61] * 100 + m0[0x60]; st0 = m0[0x6D]; LIVES = m0[0x76]; f0 = F0 + len(pre)
base = L.Enforcer((list(HIST) + pre)[-1900:])
s_init = dict(item=m0[0xC9], ninpo=m0[0x64], hp=m0[0x65], _thr=0, _had=m0[0xC9] == 128)
nodes = [(0, 's0', (), base, s_init)]
stops = [(0x6D, 'changed', 0), (0x65, '==', 0)]
t0 = time.time(); win = None; gen = 0; lastbest = None


def canthrow(s): return s['item'] == 129 and s['ninpo'] >= 3 and s['_thr'] < T and ('x' not in s or C.abs_x(s) >= THROWX)


def ok_goal(s):
    if GOAL.startswith('x:'): return C.abs_x(s) >= int(GOAL[2:]) and s['hp'] >= MINHP and s['ninpo'] >= MINNP
    if s['item'] != 128 or s['_thr'] != T or s['hp'] < MINHP: return False
    if GOAL.startswith('end:'): return C.abs_x(s) >= int(GOAL[4:])
    return s['stage'] != st0 if GOAL == 'stage' else True


for fr in range(NF):
    gen += 1
    jobs = {i: [] for i in range(NW)}
    for ni, (wk, slot, rows, en, s) in enumerate(nodes):
        kids = {}
        for w in AL:
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if ('Up' in lg and 'B' in lg) and not canthrow(s): continue
            if lg in kids: continue
            kids[lg] = e2
        wk2 = wk if fr > 0 else ni % NW
        jobs[wk2].append((ni, slot, list(kids.items())))
    out = []; lock = threading.Lock()

    def work(wi):
        c = cores[wi]; res = []
        for ni, slot, kl in jobs[wi]:
            rr = c.run_batch(slot, [[lg] for lg, _ in kl], record='all', stops=stops, keep=True, prefix=f'g{gen}n{ni}_')
            par = nodes[ni][4]
            for (lg, e2), r in zip(kl, rr):
                if r.rows_played == 0 or not r.states: continue
                s = r.states[-1]
                if DBG: print('child', lg, {k: s[k] for k in ('dead', 'hp', 'lives', 'timestop', 'ninpo', 'item', 'x', 'y')}, 'par', par.get('ninpo'), LIVES)
                if s['dead'] & 0x80 or s['hp'] == 0 or s['lives'] < LIVES or s['timestop']: continue
                thr = par['_thr'] + (1 if s['ninpo'] == par['ninpo'] - 3 else 0)
                if s['ninpo'] < par['ninpo'] and s['ninpo'] != par['ninpo'] - 3: continue
                if thr > T: continue
                if par['_had'] and s['item'] != 128: continue
                if s['ninpo'] > MAXNP: continue
                s['_thr'] = thr; s['_had'] = par['_had'] or s['item'] == 128
                res.append((wi, r.slot, nodes[ni][2] + (lg,), e2, s))
        with lock: out.extend(res)
    th = [threading.Thread(target=work, args=(wi,)) for wi in range(NW)]
    for t_ in th: t_.start()
    for t_ in th: t_.join()
    hits = [n for n in out if ok_goal(n[4])]
    if hits:
        hits.sort(key=lambda n: (-n[4]['hp'], score(n[4])))
        win = hits[0]; break
    out.sort(key=lambda n: (score(n[4]), -n[4]['hp']))
    seen = set(); cnt = {}; nxt = []; ycnt = {}
    for n in out:
        s = n[4]
        if s['stage'] != st0: continue
        X = C.abs_x(s); ph = phase(s)
        if STAR and ph == 0 and X > NOSTARX: continue
        if ph < 3 and X > NOFWX: continue
        if T > 0 and X > AMMOX and s['ninpo'] < 3 * (T - s['_thr']) and ph < 2: continue
        if T > 0 and ph == 3 and s['_thr'] < T: continue
        if WASTE and T > 0 and ph == 1 and s['_thr'] == T and s['thrown'] == 0: continue
        if s['hp'] < MINHP: continue
        key = (s['x'], s['xsub'], s['y'], s['vy'], s['vy_sub'], s['coll'], s['anim'], s['scroll'], n[2][-1], s['eact'],
               s['hp'], s['ninpo'], s['item'], s['_thr'], ph, s['rflags'])
        if key in seen: continue
        seen.add(key)
        bk = (ph, s['_thr'], min(s['ninpo'] // 3, BUCKN) if T else 0)
        if cnt.get(bk, 0) >= W: continue
        if YCAP:
            yk = (bk, s['y'] // 12, s['vy'] < 128, s['coll'])
            if ycnt.get(yk, 0) >= YCAP: continue
            ycnt[yk] = ycnt.get(yk, 0) + 1
        cnt[bk] = cnt.get(bk, 0) + 1
        nxt.append(n)
    bal = []
    for i, n in enumerate(nxt):
        dst = i % NW
        if n[0] != dst:
            cores[dst].put(n[1], cores[n[0]].get(n[1])); n = (dst,) + tuple(n[1:])
        bal.append(n)
    nodes = bal
    for wi in range(NW):
        if gen >= 2: cores[wi].drop_prefix(f'g{gen-1}n')
    if nodes and DUMP and fr % DUMP == 0:
        C.write_inputs(f'work/l31alt/b_{tag}_cur.txt', pre + list(max(nodes, key=lambda n: (phase(n[4]), -score(n[4])))[2]), f'l31alt beam {tag} current best')
    if nodes:
        lastbest = max(nodes, key=lambda n: (phase(n[4]), -score(n[4])))
        b = nodes[0][4]; lb = lastbest[4]
        if fr % 5 == 0 or len(nodes) < 3:
            print(f'{time.time()-t0:5.0f}s f {f0+fr+1} n {len(nodes)} bk {dict(sorted(cnt.items()))} | bestX {C.abs_x(b)} y {b["y"]} hp {b["hp"]} np {b["ninpo"]} it {b["item"]} | top X {C.abs_x(lb)} ph {phase(lb)} thr {lb["_thr"]} hp {lb["hp"]}', flush=True)
    else:
        print('empty'); break
for c in cores: c.close()
if win:
    s = win[4]
    print(f'GOAL at frame {f0+len(win[2])} stage rows {len(pre)+len(win[2])} X {C.abs_x(s)} y {s["y"]} hp {s["hp"]} np {s["ninpo"]} it {s["item"]} thr {s["_thr"]} stage {s["stage"]}')
    C.write_inputs(f'work/l31alt/b_{tag}.txt', pre + list(win[2]), f'l31alt beam {tag} T={T} goal {GOAL}')
else:
    print('no goal')
    if lastbest:
        C.write_inputs(f'work/l31alt/b_{tag}_part.txt', pre + list(lastbest[2]), f'l31alt beam {tag} partial'); print('partial rows', len(pre) + len(lastbest[2]))
