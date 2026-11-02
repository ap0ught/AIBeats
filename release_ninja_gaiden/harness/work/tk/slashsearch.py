"""Slash-timing search with diagnostics (tk). From start + rows[:N]: hold `dir` and press B at t1 (and t2), optional
A at ta, everything legalized by the Enforcer; horizon H frames. Reports for every candidate: first frame with the goal
(room, X <= / >= gx, y in [ylo, yhi]), hp, kills; keeps the best (earliest goal, then hp) and writes rows.
    python work/tk/slashsearch.py <start> <rows> N <hist> <out> <goal room,cmp,gx,ylo,yhi> [--dir Left] [--H 140]
        [--t1 0-40] [--t2 5-40|none] [--ta none|0-30] [--minutes 20]"""
import sys, time, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return v
    return d
def rng(s):
    pass
    out = []
    for part in s.split(','):
        if '-' in part:
            lo, hi = part.split('-'); st = 1
            if ':' in hi: hi, st = hi.split(':')
            out += list(range(int(lo), int(hi) + 1, int(st)))
        elif part == 'none': out.append(None)
        else: out.append(int(part))
    return out
NP = int(opt('--np', 0)); D = opt('--dir', 'Left'); H = int(opt('--H', 140)); mins = float(opt('--minutes', 20))
T1 = rng(opt('--t1', '0-40')); T2 = rng(opt('--t2', 'none')); TA = rng(opt('--ta', 'none')); SS = rng(opt('--stop', 'none'))
start, rf, N, hf, out, goal = a[0], a[1], int(a[2]), a[3], a[4], a[5]
g = goal.split(','); groom, gcmp, gx, ylo, yhi = int(g[0]), g[1], int(g[2]), int(g[3]), int(g[4])
rows = C.rows_of(rf)[:N]; hist = C.rows_of(hf)
def ok(s):
    x = C.abs_x(s)
    return s['room'] == groom and (x <= gx if gcmp == 'le' else x >= gx) and ylo <= s['y'] <= yhi and not (s['rflags'] & 4) and s['ninpo'] >= NP
e = C.open_emu('tk_slash.log'); t0 = time.time()
try:
    e.tick(TICKS); e.load(start); st = e.run(rows); sid = e.msave()
    print('at', st['frame'], C.abs_x(st), st['y'], 'hp', st['hp'], flush=True)
    en0 = A.Enforcer((hist + rows)[-1900:]); best = None; seen = set(); n = 0; diag = []
    for t1, t2, ta, ss in itertools.product(T1, T2, TA, SS):
        if t2 is not None and t2 <= t1 + 4: continue
        if time.time() - t0 > mins * 60: print('time up'); break
        want = []
        for i in range(H):
            r = {D} if (D != '-' and (ss is None or i < ss or (ta is not None and i >= ta))) else set()
            if i in (t1, t1 + 1) or (t2 is not None and i in (t2, t2 + 1)): r.add('B')
            if ta is not None and i in (ta, ta + 1): r.add('A')
            want.append(tuple(r))
        en = en0.copy(); rr = tuple(en.emit(w) for w in want)
        if rr in seen: continue
        seen.add(rr); e.mload(sid); e.trace(True); e.run(list(rr)); tr = e.last_trace; n += 1
        hit = next((i for i, s in enumerate(tr) if ok(s)), None)
        hp = min(s['hp'] for s in tr[:hit + 1 if hit is not None else len(tr)])
        far = min(C.abs_x(s) for s in tr) if gcmp == 'le' else max(C.abs_x(s) for s in tr)
        diag.append((hit if hit is not None else 9999, -hp, far, t1, t2, ta, ss))
        if hit is not None and (best is None or (-hp, hit) < (-best[1], best[0])):
            best = (hit, hp, t1, t2, ta)
            print('NEW', tr[hit]['frame'], 'hp', hp, 't1', t1, 't2', t2, 'ta', ta, 'stop', ss, f'evals {n}', flush=True)
            C.write_inputs(out, rows + list(rr[:hit + 1]), f'slashsearch {goal}: frame {tr[hit]["frame"]} hp {hp}')
    diag.sort(key=lambda d: (d[0], d[1], d[2] if gcmp == 'le' else -d[2]))
    print('evals', n, 'top:', diag[:12], flush=True)
finally:
    e.close()
