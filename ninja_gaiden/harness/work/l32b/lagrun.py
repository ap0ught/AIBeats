"""play legalized TAS rows (lag L) from our handover state; report sync vs TAS.
python work/l32b/lagrun.py <mst> <hist> <lag> <n> [--nob] [--every k]"""
import sys
sys.path.insert(0, 'work/l32b'); sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
import xp, a56_common as A
from ng.solve import common as C, legality as L
TR = A.tas_rows(); T = A.tas_trace()
a = sys.argv[1:]
nob = '--nob' in a
if nob: a.remove('--nob')
ev = 1
if '--every' in a:
    i = a.index('--every'); ev = int(a[i+1]); del a[i:i+2]
mst, hf, lag, n = a[0], a[1], int(a[2]), int(a[3])
H = C.rows_of(hf); f0 = len(H)
want = [tuple(x for x in TR[f0 - lag + k] if not (nob and x == 'B')) for k in range(n)]
en = L.Enforcer(H[-1900:])
rows = [tuple(sorted(en.emit(w))) for w in want]
st = xp.run(mst, rows)
for i, s in enumerate(st):
    f = f0 + i + 1; t = T[f - lag]
    if i % ev: continue
    scr = C.abs_x(s) - s['x']
    enm = ' '.join(f"{j}:t{s[f't{j}']}@{scr + s[f'x{j}']},{s[f'y{j}']}" for j in range(8) if s['eb'] >> j & 1)
    print(f, '+'.join(rows[i]) or '-', 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], '| TAS', C.abs_x(t), t['y'], '|', enm)
