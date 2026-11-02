"""prefix rows + legalized TAS rows at lag (TAS row = our frame - lag), optional edits, from a Mesen state.
python work/l32b/follow.py <mst> <hist> <prefix rows|-> <lag> <n> <out rows file> [--edit 'frame:ROW,...'] [--every k] [--nob]
--edit uses OUR absolute frame numbers (row played on that frame); ROW like B+Right or - ."""
import sys
sys.path.insert(0, 'work/l32b'); sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
import xp, a56_common as A
from ng.solve import common as C, legality as L
TR = A.tas_rows(); T = A.tas_trace()
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
ev = opt('--every', 10); ed = opt('--edit', ''); nob = '--nob' in a
if nob: a.remove('--nob')
mst, hf, pf, lag, n, out = a[0], a[1], a[2], int(a[3]), int(a[4]), a[5]
H = C.rows_of(hf); f0 = len(H)
pre = C.rows_of(pf) if pf != '-' else []
edits = {}
for q in ed.split(','):
    if q: f, r = q.split(':'); edits[int(f)] = () if r == '-' else tuple(sorted(r.split('+')))
want = list(pre)
while len(want) < len(pre) + n:
    f = f0 + len(want) + 1
    w = edits.get(f, tuple(x for x in TR[f - lag] if not (nob and x == 'B')))
    want.append(w)
for f, r in edits.items():
    k = f - f0 - 1
    if 0 <= k < len(pre): want[k] = r
en = L.Enforcer(H[-1900:]); rows = [tuple(sorted(en.emit(w))) for w in want]
bad = [i for i, (w, r) in enumerate(zip(want, rows)) if tuple(sorted(w)) != r]
st = xp.run(mst, rows)
C.write_inputs(out, rows, f'follow {mst} prefix {pf} lag {lag}')
first = None
for i, s in enumerate(st):
    f = f0 + i + 1; t = T[f - lag] if f - lag < len(T) else None
    X = C.abs_x(s)
    off = t is not None and i >= len(pre) and (abs(X - C.abs_x(t)) > 2 or s['y'] != t['y'])
    if off and first is None: first = f
    if i % ev == 0 or (off and first == f) or i == len(st) - 1 or s['stage'] != st[0]['stage']:
        scr = X - s['x']
        enm = ' '.join(f"{j}:t{s[f't{j}']}@{scr + s[f'x{j}']},{s[f'y{j}']}" for j in range(8) if s['eb'] >> j & 1)
        print(f, '+'.join(rows[i]) or '-', 'X', X, 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'it', s['item'], 'st', s['stage'],
              '| TAS', (C.abs_x(t), t['y']) if t else None, '|', enm, '<<OFF' if off else '')
    if s['stage'] != st[0]['stage']: print('STAGE CHANGE at', f); break
print('first off-sync', first, 'legalized rows changed:', len(bad))
