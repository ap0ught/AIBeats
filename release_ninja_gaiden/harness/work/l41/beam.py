"""4-1 frame-synchronous legal beam on Mesen (from work/l31t/tbeam.py). Rows are STAGE rows (row i -> frame 14,866+i).
    python -u work/l41/beam.py <prefix rows file|-> <start frame> <tag> --goal "<expr>" [--score "<expr>"]
        [--cell "<expr>"] [--cap 4] [--width 200] [--frames 300] [--minhp 0] [--alpha "Right|A+Right|..."]
        [--np "<expr>"] [--freeze f,..] [--mst path]
The prefix rows (to <start frame>) are played from l41_ctl once (or --mst gives a state AT <start frame>).
Expressions see: s (row dict), X (abs X), y, hp, np, room, item, f (frame), anim, vy, xs (X + subpixel).
item must stay 133 once held (J&S); never timestop. --np: extra condition (e.g. "np>=5").
Out: work/l41/bm_<tag>.inputs.txt (full stage rows to the goal frame) / bm_<tag>_part.inputs.txt"""
import sys, time, threading, os
sys.path.insert(0, 'work/l41')
from lib import *
import fcka
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
ALPHA = opt('--alpha', 'Right|A+Right|-|A|B+Right|Left|A+Left|A+B+Right')
W = opt('--width', 200); NF = opt('--frames', 300); MINHP = opt('--minhp', 0)
GOAL = opt('--goal', 'False'); SCORE = opt('--score', '-xs'); CELL = opt('--cell', ''); CAP = opt('--cap', 4)
NPC = opt('--np', 'True'); MST_ = opt('--mst', ''); NW = opt('--nw', 2)
FREEZE = set(int(q) for q in opt('--freeze', '').split(',') if q)
TT = None
if 'T(' in SCORE or 'T(' in GOAL:
    sys.path.insert(0, 'ng/stages'); import a56_common as A; TT = A.tas_trace()
def T(f): return TT[f]   # TAS trace row at TAS frame f
pf, f_start, tag = a[0], int(a[1]), a[2]
pre = [] if pf == '-' else list(C.rows_of(pf))[:f_start - F0]
assert len(pre) == f_start - F0, (len(pre), f_start)
def ev(expr, s):
    x = C.abs_x(s)
    return eval(expr, {'T': T, 'C': C}, dict(s=s, X=x, y=s['y'], hp=s['hp'], np=s['ninpo'], room=s['room'],
                                            item=s['item'], f=s['frame'], anim=s['anim'], vy=s['vy'],
                                            xs=x + s['xsub'] / 256.0))
AL = [row(x) for x in ALPHA.split('|')]
from pathlib import Path as _P
F.LUA = _P('work/l31t/fastcore_gc.lua').resolve()
def make_cores():
    cs = []
    for _ in range(NW):
        c = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
        c.put('s', open(MST_ or MST, 'rb').read()); c.load('s')
        if not MST_ and pre:
            c.step(pre, record='last')
        c.save('s0'); c._ka_slot = 's0'
        cs.append(c)
    return cs
cores = make_cores()
r0 = cores[0].ram(); st0 = r0[0x6D]; ITEM0 = r0[0xC9]; NP0 = r0[0x64]
print('start', f_start, 'X', X(r0), 'y', r0[0x8A], 'hp', r0[0x65], 'np', NP0, 'item', ITEM0, flush=True)
f0 = f_start
HP = hist_ctl() + pre
base = L.Enforcer(HP[-1900:])
nodes = [(0, 's0', (), base, None)]
stops = [(0x6D, 'changed', 0), (0x65, '==', 0)]
t0 = time.time(); win = None; gen = 0; LIVES = None


def ok_state(s):
    if s['hp'] == 0 or (s['dead'] & 0x80) or s['stage'] != st0 or s['hp'] < MINHP: return False
    if s.get('timestop', 0): return False
    if ITEM0 == 133 and s['item'] != 133: return False
    if LIVES is not None and s['lives'] < LIVES: return False
    return ev(NPC, s)


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


def expand(nodes, fr, gen):
    out = []; errs = []; lock = threading.Lock()
    jobs = {i: [] for i in range(NW)}
    for ni, (wk, slot, rows, en, s) in enumerate(nodes):
        kids = {}
        frz = (f0 + fr + 1) in FREEZE
        last = rows[-1] if rows else tuple(sorted(HP[-1]))
        for w in ([last] if frz else AL):
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if frz and lg != tuple(sorted(last)): continue
            if lg in kids: continue
            kids[lg] = e2
        jobs[wk].append((ni, slot, list(kids.items())))

    def work(wi):
        try:
            c = cores[wi]; res = []
            for ni, slot, kl in jobs[wi]:
                rr = c.run_batch(slot, [[lg] for lg, _ in kl], record='all', stops=stops, keep=True,
                                 prefix=f'g{gen}n{ni}_')
                for (lg, e2), r in zip(kl, rr):
                    if r.rows_played == 0 or not r.states: continue
                    st = r.states[-1]; st['frame'] = f0 + len(nodes[ni][2]) + 1
                    if any((q['dead'] & 0x80) for q in r.states): st['dead'] |= 0x80
                    res.append((wi, r.slot, nodes[ni][2] + (lg,), e2, st))
            with lock: out.extend(res)
        except Exception as ex:
            with lock: errs.append(ex)
    th = [threading.Thread(target=work, args=(wi,)) for wi in range(NW)]
    for t in th: t.start()
    for t in th: t.join()
    return out, errs


lastbest = None
for fr in range(NF):
    gen += 1
    for _try in range(5):
        out, errs = expand(nodes, fr, gen)
        if not errs: break
        nodes = rebuild(nodes, errs[0])
    else:
        raise SystemExit('too many Mesen failures')
    if LIVES is None and out: LIVES = max(n[4]['lives'] for n in out)
    hits = [n for n in out if ok_state(n[4]) and ev(GOAL, n[4])]
    if hits:
        hits.sort(key=lambda n: (ev(SCORE, n[4]), -n[4]['hp'], -n[4]['ninpo']))
        win = hits[0]; break
    seen = set(); nxt = []; cnt = {}
    out.sort(key=lambda n: (ev(SCORE, n[4]), -n[4]['hp']))
    for n in out:
        s = n[4]
        if not ok_state(s): continue
        key = (s['x'], s['xsub'], s['y'], s['vy'], s.get('vy_sub', 0), s['coll'], s['anim'], s['scroll'],
               s['scroll_sub'], s['room'], n[2][-1], s.get('eact', 0), s['hp'], s['ninpo'], s['item'], s['inv'],
               s['rflags'])
        if key in seen: continue
        seen.add(key)
        if CELL:
            ck = ev(CELL, s)
            if cnt.get(ck, 0) >= CAP: continue
            cnt[ck] = cnt.get(ck, 0) + 1
        nxt.append(n)
        if len(nxt) >= W: break
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
            for q in range(0, len(dead), 150): cores[wi].drop(*dead[q:q + 150])
        nxt = bal
    except Exception as ex:
        nxt = rebuild(nxt, ex)
    nodes = nxt
    if nodes: lastbest = nodes[0]
    b = nodes[0][4] if nodes else None
    if b:
        ys = sorted(set(n[4]['y'] for n in nodes))
        print(f'{time.time()-t0:5.0f}s frame {f0+fr+1} nodes {len(nodes)} best X {C.abs_x(b)} y {b["y"]} room {b["room"]} '
              f'hp {b["hp"]} np {b["ninpo"]} sc {ev(SCORE, b):.1f} ys {ys[:3]}..{ys[-3:]}', flush=True)
    else:
        print('empty', flush=True)
    if not nodes: break
for c in cores:
    try: c.close()
    except Exception: pass
if win:
    s = win[4]
    print(f'GOAL at frame {f0+len(win[2])} X {C.abs_x(s)} y {s["y"]} room {s["room"]} hp {s["hp"]} np {s["ninpo"]} item {s["item"]}')
    C.write_inputs(f'work/l41/bm_{tag}.inputs.txt', pre + list(win[2]), f'beam {tag} goal {GOAL} from {f_start}')
else:
    print('no goal')
    if lastbest:
        C.write_inputs(f'work/l41/bm_{tag}_part.inputs.txt', pre + list(lastbest[2]), f'beam {tag} partial best')
