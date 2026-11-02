"""Follow: prefix stage rows (first N rows) + legalized TAS rows at lag LAG (our f = TAS t + LAG) to TAS END.
Overrides: TAS 22,793-94 Left; 23,279-80 A+Right. Prints hp/np/item changes and X vs TAS every EV frames.
python work/l51a/fol.py <prefix> <N|all> <lag> <tas end> [ev] [--out file] [--ov t:row,t:row]"""
import sys; sys.path.insert(0, 'work/l51a')
from lib import *
a = sys.argv[1:]
out = None; ov = {}
if '--out' in a: i = a.index('--out'); out = a[i+1]; del a[i:i+2]
if '--ov' in a:
    i = a.index('--ov'); ov = {int(k): set(row(v)) for k, v in (x.split(':') for x in a[i+1].split(','))}; del a[i:i+2]
pre = rows_file(a[0]); N = len(pre) if a[1] == 'all' else int(a[1]); pre = pre[:N]
LG = int(a[2]); END = int(a[3]); EV = int(a[4]) if len(a) > 4 else 20
want = []
t0 = CTL + N - LG
for t in range(t0, END + 1):
    w = set(T(t))
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if t in (22793, 22794): w = {'Left'}
    if t in (23279, 23280): w = {'A', 'Right'}
    if t in ov: w = ov[t]
    want.append(w)
H = hist()
en = A.Enforcer(H[-1900:] + pre); rows = pre + [tuple(sorted(en.emit(w))) for w in want]
print('legal', legal_ok(rows, H) or 'ok', 'rows', len(rows), flush=True)
tr = trace(rows); prev = None
for i, t in enumerate(tr):
    f = t[0]; k = (t[3], t[4], t[5])
    if i >= N - 1 and ((f - CTL) % EV == 0 or k != prev or i == len(tr) - 1 or t[2] >= 230):
        tf = f - LG; tx = XY(TM(tf)) if TF0 < tf <= TF0 + NF else None
        print(f, 'tas', tf, 'X,y', t[1], t[2], 'hp', t[3], 'np', t[4], 'it', t[5], 'TAS', tx, P(rows[i]), flush=True)
        if t[2] >= 240 or t[3] == 0: break
    prev = k
if out: wr(out, rows, f'fol {a} lag {LG}')
