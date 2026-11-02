"""Follow: from a Mesen state (after our-axis frame F0; --hist rows before it), play rows file (optional), then the legalized
TAS rows t1..t2 (our frame = TAS frame + LAG), mods 't1-t2=ROW' on the TAS axis. Reports events and the TAS-equivalent lag.
python work/l51b/fol.py <mst> F0 <hist> [--rows file] --lag L --t2 T [--mods ...] [--every 20] [--goal 'X>=2760 and y<=100']
  [--save tag@frame,...] (Mesen state + history at our frames)"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
RF = opt('--rows', ''); LAG = opt('--lag', 0); T2 = opt('--t2', 0); MODS = opt('--mods', ''); EV = opt('--every', 20)
GOAL = opt('--goal', ''); SL = opt('--slots', ''); SAVE = opt('--save', ''); OUT = opt('--out', '')
mst, F0, H = a[0], int(a[1]), a[2]
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
pre = [tuple(sorted(r)) for r in C.rows_of(RF)] if RF else []
mods = {}
for it in (MODS.split(',') if MODS else []):
    k, v = it.split('='); k1, k2 = (k.split('-') + [k])[:2]
    for t in range(int(k1), int(k2) + 1): mods[t] = set(row(v))
t1 = F0 + len(pre) + 1 - LAG
want = tasleg(t1, T2, mods) if T2 >= t1 else []
rows = pre + enforce(want, hist + pre)
lg = legal_ok(rows, hist)
print('legal', lg or 'ok', 'rows', len(rows), 'TAS from', t1, flush=True)
fc = core(mst)
_, recs, _ = fc.step(rows, record='all')
hp = np_ = None; g = None
GC = compile(GOAL, 'g', 'eval') if GOAL else None
for i, r in enumerate(recs):
    f = F0 + 1 + i; X, y = RXY(r)
    ev = []
    if hp is not None and r['hp65'] != hp: ev.append(f'hp {hp}->{r["hp65"]}')
    if np_ is not None and r['np64'] != np_: ev.append(f'np {np_}->{r["np64"]}')
    hp = r['hp65']; np_ = r['np64']
    t = f - LAG
    # TAS-equivalent: first TAS frame with X >= ours
    if ev or (EV and (f - F0) % EV == 0) or i == len(recs) - 1:
        te = next((u for u in range(22126, 24400) if tas_xy(u)[0] >= X), 0)
        print(f, 'X,y', (X, y), 'hp', r['hp65'], 'np', r['np64'], '| TAS@', t, tas_xy(t) if 22126 <= t <= 24525 else '', '| eqlag', f - te, ' '.join(ev), flush=True)
    if SL:
        s1, s2, st = map(int, SL.split(':'))
        if s1 <= f <= s2 and (f - s1) % st == 0:
            scr = X - r['x86']
            print('   ', f, (X, y), ' '.join(f's{j}t{r[f"t{j}"]}({scr + r[f"ex{j}"]},{r[f"ey{j}"]})' for j in range(8) if r['eact'] >> j & 1))
    if GC and g is None and eval(GC, dict(X=X, y=y, s=r)): g = f; print('GOAL at', f, 'lag', f - next(u for u in range(22126, 24400) if tas_xy(u)[0] >= X))
    if y >= 232 or r['hp65'] == 0: print('DEAD', f); break
if OUT: C.write_inputs(OUT, rows, f'fol {mst} F0 {F0} lag {LAG}')
if SAVE:
    tag_, at_ = (SAVE.split('@') + [''])[:2]
    n = int(at_) - F0 if at_ else len(rows); SAVE = tag_; rows = rows[:n]
    fc.load('s') if False else None
    fc2 = core(mst); fc2.step(rows, record='last'); fc2.save('o')
    fc2.save_file('o', f'states/mesen/l51b_{SAVE}.mst', frame=F0 + n)
    C.write_inputs(f'work/l51b/h_{SAVE}.inputs.txt', list(hist) + list(rows), f'l51b {SAVE}: power-on rows to {F0 + n}')
    print('saved', SAVE, 'at', F0 + n); fc2.close()
fc.close()
