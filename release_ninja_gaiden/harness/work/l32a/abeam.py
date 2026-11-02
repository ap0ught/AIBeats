"""3-2 (l32a copy of work/l32p/zbeam.py: item must stay 128, no ninpo%5 rule; out work/l32a/ab_<tag>) 3-1 frame-synchronous legal beam on Mesen (from work/l22a/abeam.py) with the 3-1 item rules of plan (a):
Star (129) must be held right of --starby, Fire Wheel (128) right of --fwby; no other art; never the hourglass
(timestop); with the FW held ninpo must stay a multiple of 5. Goal hit also needs item 128, ninpo % 5 == 0 and
ninpo >= --npmin.
    python -u work/l31t/tbeam.py <hist file> <mst> <goal> <tag> [--alpha ..] [--width 64] [--frames 1400]
        [--score tas --lag 165] [--minhp 0] [--starby 820] [--fwby 1240] [--npmin 0] [--itq 0] [--freeze f,..]
goal: x:R:ge|le:GX[:ylo:yhi] | stage | z:GX:YMAX | any:... (goal without the item/ninpo checks: prefix 'any,')
Out: work/l32a/ab_<tag>.inputs.txt (rows after the history, to the goal frame)"""
import sys, time, threading, os
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L
from ng import fastcore as F
sys.path.insert(0, 'work/l31t'); import fcka   # keepalive: Mesen's Lua dies on > ~1 s idle inside a callback
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
ALPHA = opt('--alpha', 'Right|A+Right|-|A|B+Right|Up+B|A+B+Right')
W = opt('--width', 64); NF = opt('--frames', 1400); MINHP = opt('--minhp', 0); SC = opt('--score', 'tas')
NPMIN = opt('--npmin', 0); STARBY = opt('--starby', 820); FWBY = opt('--fwby', 1240)
XW = opt('--xw', 0.0); NPW = opt('--npw', 0.0); LAG = opt('--lag', 165); EKW = opt('--ek', 0.0)
FREEZE = set(int(q) for q in opt('--freeze', '').split(',') if q); NOSTAR = opt('--nostar', 0)
ITQ = opt('--itq', 0); YW = opt('--yw', 0.1)  # cap per (item, ninpo) class
NPSET = [int(q) for q in opt('--npset', '').split(',') if q]  # allowed ninpo values right of --npx
NPX = opt('--npx', 99999)
GW = opt('--gw', 0.0); IW = opt('--iw', 0.0)
HGX = opt('--hgx', 1104); HGY = opt('--hgy', 96); HX0 = opt('--hx0', 1000); HW = opt('--hw', 0.0); POKEBF = opt('--pokebf', -1)
GX2 = opt('--gx2', 1252); FWBRK = opt('--fwbrk', 99999); FBW = opt('--fbw', 0.0)
GOTBY = [tuple(map(int, q.split(':'))) for q in opt('--gotby', '').split(',') if q]
TT = None
if SC in ('tas', 'tx'):
    sys.path.insert(0, 'ng/stages'); import a56_common as A; TT = A.tas_trace()
hf, mst, goal, tag = a[:4]
ANY = goal.startswith('any,')
if ANY: goal = goal[4:]
hist = C.rows_of(hf)
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
AL = [row(x) for x in ALPHA.split('|')]
g = goal.split(':')
def reached(s, st0):
    if g[0] == 'stage': return s['stage'] != st0
    if s['stage'] != st0: return False
    if g[0] == 'z': return C.abs_x(s) >= int(g[1]) and s['y'] <= int(g[2])
    if g[0] == 'br': return int(g[1]) <= C.abs_x(s) <= int(g[2]) and s['y'] == int(g[3]) and s['anim'] in (0, 1)
    if g[0] == 'item': return s['item'] == int(g[1])
    if s['room'] != int(g[1]): return False
    x = C.abs_x(s)
    ok = x <= int(g[3]) if g[2] == 'le' else x >= int(g[3])
    if ok and len(g) > 4: ok = int(g[4]) <= s['y'] <= int(g[5])
    return ok
def score(s):
    x = C.abs_x(s) + s['xsub'] / 256.0
    if SC == 'tas':
        t = TT[s['frame'] - LAG]
        v = abs(x - C.abs_x(t)) + abs(s['y'] - t['y']) + (0 if t['room'] == s['room'] else 500)
    elif SC == 'tx':
        t = TT[s['frame'] - LAG]
        v = (C.abs_x(t) - x) + YW * abs(s['y'] - t['y'])
    elif SC == 'x': v = -x
    elif SC == 'h2':
        X = C.abs_x(s); y = s['y']
        if y <= 96 and X >= 1088: v = max(0.0, (1100 - X) / 1.5)
        elif y < 120: v = max((1100 - X) / 1.5, (y - 96) / 2.5)
        else: v = max(abs(1075 - X) / 1.5, (y - 128) / 1.8) + 20
        v += HW * (16 - s['hp'])
    elif SC == 'w2':   # time-to-go to X GX2 via the branch/top of the tosser wall (h2 + the run on the top)
        X = C.abs_x(s); y = s['y']
        if y <= 100 and X >= 1088: v = (GX2 - X) / 1.5
        else:
            if y < 120: v = max((1100 - X) / 1.5, (y - 96) / 2.5)
            else: v = max(abs(1075 - X) / 1.5, (y - 128) / 1.8) + 20
            v += (GX2 - 1100) / 1.5
        v += HW * (16 - s['hp'])
    elif SC == 'hb':
        X = C.abs_x(s); y = s['y']
        v = max(abs(HGX - X) / 1.5, (y - HGY) / 1.8 if y > HGY else 0.0) + HW * (16 - s['hp'])
    elif SC == 'h':
        X = C.abs_x(s); y = s['y']
        v = max((HGX - X) / 1.5, (y - HGY) / 1.8 if X > HX0 else 0.0) + HW * (16 - s['hp'])
    else: v = 0
    v += EKW * bin(s.get('eact', 0)).count('1')
    return v - NPW * s['ninpo'] - GW * s.get('_got', 0) - IW * (s['item'] != 0) - FBW * fwb(s) + (0 if s['hp'] >= MINHP else 1e6) + XW * (16 - s['hp'])
def fwb(s):
    if s['item'] == 128: return True
    return any((s['lmask'] >> j) & 1 and (s[f'lit{j}'] & 15) == 10 and (s[f'lst{j}'] & 0x0C) for j in range(4))
def item_ok(s):
    if s.get('timestop', 0): return False
    if s['item'] != 128: return False          # 3-2: keep the Fire Wheel (never the Windmill)
    if NPSET and C.abs_x(s) > NPX and s['ninpo'] not in NPSET: return False
    for gx, gn in GOTBY:
        if C.abs_x(s) > gx and s.get('_got', 0) < gn: return False
    return True
NW = int(os.environ.get("FB_NW", "2"))
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['lmask'] = 0xC0
for _j in range(4): FLD[f'lst{_j}'] = 0x4D1 + _j; FLD[f'lit{_j}'] = 0x4C9 + _j
from pathlib import Path as _P
F.LUA = _P('work/l31t/fastcore_gc.lua').resolve()   # = ng/fastcore.lua + collectgarbage after DROP/DROPPREFIX
data = open(mst, 'rb').read()
if POKEBF >= 0:
    _c = F.FastCore(boot_rows=None, ticks=True); _c.put('s0', data); _c.load('s0'); _c.poke(0xBF, POKEBF & 255); _c.save('s0'); data = _c.get('s0'); _c.close()
def make_cores():
    cs = [F.FastCore(boot_rows=None, ticks=True, fields=FLD) for _ in range(NW)]
    for c in cs: c.put('s0', data); c.load('s0'); c._ka_slot = 's0'
    return cs
cores = make_cores()
st0 = cores[0].ram()[0x6D]; NP0 = cores[0].ram()[0x64]
f0 = len(hist)
base = L.Enforcer(hist[-1900:])
nodes = [(0, 's0', (), base, None)]
stops = [(0x6D, 'changed', 0), (0x6E, 'changed', 0), (0x65, '==', 0)]
t0 = time.time(); win = None; gen = 0
NREB = [0]
def rebuild(nl, why):
    """Mesen dies after many savestates: start new cores and replay every node's rows from s0."""
    global cores
    NREB[0] += 1
    print(f'REBUILD #{NREB[0]} at gen {gen} ({str(why)[:80]}), {len(nl)} nodes', flush=True)
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
import faulthandler
_hb = [time.time()]
def _watch():
    while True:
        time.sleep(30)
        if time.time() - _hb[0] > 120:
            print('WATCHDOG: no progress for 120 s', flush=True); faulthandler.dump_traceback(sys.stdout); sys.stdout.flush()
            for c in cores:
                try: c.proc.kill()      # unblocks the hung socket read -> exception -> rebuild
                except Exception: pass
            _hb[0] = time.time()
threading.Thread(target=_watch, daemon=True).start()
def expand(nodes, fr, gen):
    out = []; errs = []
    lock = threading.Lock()
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
        jobs[wk].append((ni, slot, list(kids.items())))
    def work(wi):
        try:
            c = cores[wi]
            res = []
            for ni, slot, kl in jobs[wi]:
                rr = c.run_batch(slot, [[lg] for lg, _ in kl], record='all', stops=stops, keep=True,
                                 prefix=f'g{gen}n{ni}_')
                for (lg, e2), r in zip(kl, rr):
                    if r.rows_played == 0 or not r.states: continue
                    st = r.states[-1]; st['frame'] = f0 + len(nodes[ni][2]) + 1
                    if any((q['dead'] & 0x80) for q in r.states): st['dead'] |= 0x80
                    par = nodes[ni][4]
                    pnp = par['ninpo'] if par else NP0
                    st['_got'] = (par['_got'] if par else 0) + max(0, st['ninpo'] - pnp)
                    res.append((wi, r.slot, nodes[ni][2] + (lg,), e2, st))
            with lock: out.extend(res)
        except Exception as ex:
            with lock: errs.append(ex)
    th = [threading.Thread(target=work, args=(wi,)) for wi in range(NW)]
    for t in th: t.start()
    for t in th: t.join()
    return out, errs
LIVES = None
for fr in range(NF):
    gen += 1
    for _try in range(5):
        out, errs = expand(nodes, fr, gen)
        if not errs: break
        nodes = rebuild(nodes, errs[0])
    else:
        raise SystemExit('too many Mesen failures')
    if LIVES is None and out: LIVES = max(n[4]['lives'] for n in out)
    hits = [n for n in out if not (n[4]['dead'] & 0x80) and item_ok(n[4])
            and n[4]['ninpo'] >= NPMIN
            and n[4]['lives'] >= LIVES and n[4]['hp'] >= MINHP and reached(n[4], st0)]
    if hits:
        hits.sort(key=lambda n: (-n[4]['hp'], -n[4]['ninpo']))
        win = hits[0]; break
    seen = set(); nxt = []; ovf = []; cnt = {}
    out.sort(key=lambda n: (score(n[4]), -n[4]['hp']))
    for n in out:
        s = n[4]
        if not item_ok(s): continue
        if s['hp'] == 0 or (s['dead'] & 0x80) or s['stage'] != st0 or s['hp'] < MINHP or s['lives'] < LIVES: continue
        key = (s['x'], s['xsub'], s['y'], s['vy'], s.get('vy_sub', 0), s['coll'], s['anim'],
               s['scroll'], s['room'], n[2][-1], s.get('eact', 0), s['hp'], s['ninpo'], s['item'], s.get('_got', 0))
        if key in seen: continue
        seen.add(key)
        ck = (s['item'], s['ninpo'])
        if ITQ and cnt.get(ck, 0) >= ITQ:
            ovf.append(n); continue
        cnt[ck] = cnt.get(ck, 0) + 1
        nxt.append(n)
        if len(nxt) >= W: break
    if len(nxt) < W: nxt += ovf[:W - len(nxt)]
    try:
        # keep nodes on their own core; move only the excess by REPLAYING its rows from s0 on the other core
        bal = []
        cnt_w = [0] * NW
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
    if nodes: lastbest = nodes[0]
    b = nodes[0][4] if nodes else None
    if b:
        cls = sorted(set((n[4]['item'], n[4]['ninpo']) for n in nodes))
        print(f'{time.time()-t0:5.0f}s frame {f0+fr+1} nodes {len(nodes)} best X {C.abs_x(b)} y {b["y"]} hp {b["hp"]} np {b["ninpo"]} it {b["item"]} fwb {int(fwb(b))} sc {score(b):.1f} cls {cls}', flush=True)
    else:
        print('empty', flush=True)
    _hb[0] = time.time()
    if not nodes: break
for c in cores:
    try: c.close()
    except Exception: pass
if win:
    s = win[4]
    print(f'GOAL at frame {f0+len(win[2])} rows {len(win[2])} X {C.abs_x(s)} y {s["y"]} room {s["room"]} hp {s["hp"]} np {s["ninpo"]} it {s["item"]} sub62 {s["subtimer"]}')
    C.write_inputs(f'work/l32a/ab_{tag}.inputs.txt', list(win[2]), f'tbeam {tag} goal {goal}')
else:
    print('no goal')
    try:
        C.write_inputs(f'work/l32a/ab_{tag}_part.inputs.txt', list(lastbest[2]), f'tbeam {tag} partial best')
        print('partial rows', len(lastbest[2]))
    except NameError: pass
