"""Follow the TAS with legalized rows from a Mesen state (agent r1920).
python work/r1920/fol.py <mst> <F = frame after the state> <hist rows (power-on rows 1..F) | -> <t1> <t2> [--pre rows]
       [--out rows] [--step 4] [--set f=R+A,...]
Plays --pre rows, then TAS rows t1..t2 legalized (L+R -> R, U+D -> none, 1-f A/B extended by the Enforcer against the
real history). lag = (F + len(pre) + 1) - t1. Prints our X/y/hp/np vs the TAS at f - lag, first divergence.
--set overrides the wanted TAS row at TAS frame t (before legalizing)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/r1920')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from ng.solve.hitbox import BIT
import a56_common as A
from gbeam import FL, X
sys.path.insert(0, 'work/l43p')
from lib import TM, XY, legal_ok

a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d


PRE = opt('--pre', ''); OUT = opt('--out', ''); ST = opt('--step', 4); SET = opt('--set', '')
mst, F0, H, t1, t2 = a[0], int(a[1]), a[2], int(a[3]), int(a[4])
hist = [tuple(sorted(r)) for r in C.rows_of(H)][:F0] if H != '-' else [()] * 60
pre = [tuple(sorted(r)) for r in C.rows_of(PRE)] if PRE else []
over = {}
for tok in [t for t in SET.split(',') if t]:
    k, v = tok.split('=')
    over[int(k)] = () if v == '-' else tuple(sorted({'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}[c] for c in v))
TR0 = A.tas_rows()
want = []
for t in range(t1, t2 + 1):
    w = set(over[t]) if t in over else set(TR0[t - 1])
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    want.append(tuple(sorted(w)))
en = A.Enforcer(list(hist + pre)[-1900:])
add = [tuple(sorted(en.emit(w))) for w in want]
rows = pre + add
print('legal:', legal_ok(rows, hist) or 'PASS')
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'; fc.load('s')
_, recs, _ = fc.step(rows, record='all')
fc.close()
lag = F0 + len(pre) + 1 - t1
first = None
for i in range(len(pre), len(rows)):
    s = recs[i]; f = F0 + 1 + i; t = f - lag
    m = TM(t)
    tX, ty = XY(m) if m else (None, None)
    same = m is not None and (X(s), s['y'], s['room']) == (tX, ty, m[0x6E])
    if not same and first is None: first = f
    if (i - len(pre)) % ST == 0 or i == len(rows) - 1 or (not same and first == f) or rows[i] != want[i - len(pre)]:
        en_s = ' '.join(f"{j}:t{s[f't{j}']}@{s[f'ex{j}']}/{s[f'ey{j}']}" for j in range(8) if s['en'] & BIT[j])
        print(f, '+'.join(rows[i]) or '-', 'rm', s['room'], 'X', X(s), 'y', s['y'], 'hp', s['hp'], 'np', s['np'],
              '| TAS', t, None if m is None else (m[0x6E], tX, ty, m[0x65], m[0x64]), '' if same else 'DIFF', '|', en_s)
print('lag', lag, 'first divergence', first)
if OUT:
    C.write_inputs(OUT, rows, f'fol {mst} F {F0} pre {PRE} TAS {t1}-{t2} lag {lag}'); print('wrote', OUT)
