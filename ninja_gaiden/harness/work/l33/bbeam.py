"""3-3 Basaquer frame-synchronous legal beam on Mesen (machinery from work/l31t/tbeam.py).
    python -u work/l33/bbeam.py <tag> <out tag> [--width 300] [--frames 200] [--q 40] [--prefix rows_file]
        [--alpha 'A|B|...'] [--extra 12]
Start = states/mesen/l33_<tag>_ctl.mst (3-3 control), history = CANDS[tag]['pow'] (+ prefix rows).
Kill = boss hp $66 == 0. Metric M = kill row + 3*(timer + ninpo) at the kill (= 4-1 control - const).
Ranking per frame: boss hp, then diversity: classes (boss hp, ninpo, thrown-out) capped at --q, inside a class
round-robin over spatial cells (x//4, y//8, anim, inv>0), better Ryu hp first.
Keeps running --extra frames after the first kill to catch a better tally phase; prints every kill improvement.
Out: work/l33/bb_<out>.inputs.txt (legal rows from 3-3 control to the kill frame) + .json."""
import sys, time, threading, os, json
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
sys.path.insert(0, 'work/l33')
from lib import CANDS, mst as MSTOF, C, L, F
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
ALPHA = opt('--alpha', '-|Left|Right|A|A+Left|A+Right|B|B+Left|B+Right|B+Down|B+Up|Down|Down+Left|Down+Right')
W = opt('--width', 300); NF = opt('--frames', 200); Q = opt('--q', 40); EXTRA = opt('--extra', 12)
PREFIX = opt('--prefix', ''); NW = opt('--nw', 2); MINHP = opt('--minhp', 1)
tag, otag = a[:2]
hist = C.rows_of(CANDS[tag]['pow'])
pre = [tuple(sorted(r)) for r in C.rows_of(PREFIX)] if PREFIX else []
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
AL = [row(x) for x in ALPHA.split('|')]
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['thrown'] = 0xC8; FLD['bf'] = 0xBF
for j in range(3): FLD[f'fx{j}'] = 0x4BB + j; FLD[f'fy{j}'] = 0x4BE + j
FLD['bx'] = 0x467; FLD['by'] = 0x487
from pathlib import Path as _P
F.LUA = _P('work/l31t/fastcore_gc.lua').resolve()
data = open(MSTOF(tag), 'rb').read()
def make_cores():
    cs = [F.FastCore(boot_rows=None, ticks=True, fields=FLD) for _ in range(NW)]
    for c in cs: c.put('s0', data); c.load('s0'); c._ka_slot = 's0'
    return cs
cores = make_cores()
base = L.Enforcer(hist[-1900:])
if pre:
    lg = [tuple(sorted(base.emit(w))) for w in pre]
    assert lg == pre, 'prefix not legal'
    for c in cores:
        rr = c.run_batch('s0', [pre], record='last', keep=True, prefix='p')
        c.put('s1', c.get(rr[0].slot)); c._ka_slot = 's1'
    st1 = 's1'
else:
    st1 = 's0'
nodes = [(w, st1, tuple(pre), base, None) for w in range(1)]
stops = [(0x6D, 'changed', 0), (0x65, '==', 0), (0x66, '==', 0)]
t0 = time.time(); gen = 0
NREB = [0]
def rebuild(nl, why):
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
        if time.time() - _hb[0] > 150:
            print('WATCHDOG: no progress for 150 s', flush=True); faulthandler.dump_traceback(sys.stdout); sys.stdout.flush()
            for c in cores:
                try: c.proc.kill()
                except Exception: pass
            _hb[0] = time.time()
threading.Thread(target=_watch, daemon=True).start()
def expand(nodes, gen):
    out = []; errs = []
    lock = threading.Lock()
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
            c = cores[wi]
            res = []
            for ni, slot, kl in jobs[wi]:
                rr = c.run_batch(slot, [[lg] for lg, _ in kl], record='all', stops=stops, keep=True,
                                 prefix=f'g{gen}n{ni}_')
                for (lg, e2), r in zip(kl, rr):
                    if r.rows_played == 0 or not r.states: continue
                    st = r.states[-1]
                    res.append((wi, r.slot, nodes[ni][2] + (lg,), e2, st))
            with lock: out.extend(res)
        except Exception as ex:
            with lock: errs.append(ex)
    th = [threading.Thread(target=work, args=(wi,)) for wi in range(NW)]
    for t in th: t.start()
    for t in th: t.join()
    return out, errs
best = None   # (M, rows, state)
stop_at = None
for fr in range(len(pre), NF):
    gen += 1
    for _try in range(5):
        out, errs = expand(nodes, gen)
        if not errs: break
        nodes = rebuild(nodes, errs[0])
    else:
        raise SystemExit('too many Mesen failures')
    alive = []
    for n in out:
        s = n[4]
        if s['bosshp'] == 0 and s['stage'] == 7 and s['hp'] > 0:
            M = len(n[2]) + 3 * (s['timer'] + s['ninpo'])
            if best is None or M < best[0]:
                best = (M, n[2], s)
                print(f'KILL row {len(n[2])} timer {s["timer"]}.{s["subtimer"]} np {s["ninpo"]} hp {s["hp"]} M {M}', flush=True)
                C.write_inputs(f'work/l33/bb_{otag}.inputs.txt', list(n[2]), f'bbeam {tag} kill row {len(n[2])} M {M}')
                json.dump(dict(tag=tag, rows=len(n[2]), M=M, timer=s['timer'], sub=s['subtimer'], np=s['ninpo'], hp=s['hp']),
                          open(f'work/l33/bb_{otag}.json', 'w'))
                if stop_at is None: stop_at = fr + EXTRA
            continue
        if s['hp'] < MINHP or (s['dead'] & 0x80) or s['stage'] != 7: continue
        alive.append(n)
    if stop_at is not None and fr >= stop_at: break
    # ranking
    seen = set(); cls = {}
    for n in alive:
        s = n[4]
        key = (s['x'], s['xsub'], s['y'], s['vy'], s['vy_sub'], s['anim'], s['rflags'], s['inv'], s['bosshp'], s['ninpo'],
               s['hp'], s['thrown'], s['fx0'], s['fx1'], s['fx2'], s['fy0'], s['fy1'], s['fy2'], n[2][-1], n[2][-2] if len(n[2]) > 1 else ())
        if key in seen: continue
        seen.add(key)
        ck = (s['bosshp'], s['ninpo'], s['thrown'] != 0)
        cell = (s['x'] // 4, s['y'] // 8, s['anim'], s['inv'] > 0)
        cls.setdefault(ck, {}).setdefault(cell, []).append(n)
    nxt = []
    for ck in sorted(cls, key=lambda k: (k[0], -k[1], -int(k[2]))):
        cells = cls[ck]
        for v in cells.values(): v.sort(key=lambda n: (-n[4]['hp'], n[4]['inv']))
        lists = sorted(cells.values(), key=lambda v: (-v[0][4]['hp']))
        taken = 0; k = 0
        while taken < Q and any(len(v) > k for v in lists):
            for v in lists:
                if len(v) > k and taken < Q:
                    nxt.append(v[k]); taken += 1
            k += 1
        if len(nxt) >= W: break
    nxt = nxt[:W]
    try:
        bal = []
        cnt_w = [0] * NW
        for n in nxt: cnt_w[n[0]] += 1
        cap = (len(nxt) * 13) // (10 * NW) + 1
        for mi, n in enumerate(nxt):
            if cnt_w[n[0]] > cap:
                dst = min(range(NW), key=lambda q: cnt_w[q])
                if cnt_w[dst] < cap:
                    rr = cores[dst].run_batch(st1 if False else 's0', [list(n[2])], record='last', keep=True, prefix=f'm{gen}_{mi}_')
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
    _hb[0] = time.time()
    if not nodes:
        print('empty', flush=True); break
    b = nodes[0][4]
    hs = sorted(set(n[4]['bosshp'] for n in nodes))
    print(f'{time.time()-t0:5.0f}s row {fr+1} nodes {len(nodes)} best boss {b["bosshp"]} np {b["ninpo"]} hp {b["hp"]} x {b["x"]} y {b["y"]} bosses {hs[:6]} classes {len(cls)}', flush=True)
for c in cores:
    try: c.close()
    except Exception: pass
if best:
    print(f'BEST kill row {len(best[1])} M {best[0]}')
else:
    print('no kill')
    if nodes:
        C.write_inputs(f'work/l33/bb_{otag}_part.inputs.txt', list(nodes[0][2]), f'bbeam {tag} partial')
