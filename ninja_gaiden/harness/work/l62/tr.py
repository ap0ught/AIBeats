"""trace: python work/l62/tr.py F0 rowsfile [rowsfile2 ...] [--mst path] [--poke C9=133,64=20] [--every 20] [--tasrows T1-T2] [--n N]
rows start at F0+1. --tasrows appends legalized TAS rows T1..T2."""
import sys
sys.path.insert(0, 'work/l62')
from lib62 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
MST = opt('--mst', ''); PK = opt('--poke', ''); EV = opt('--every', 0); TRW = opt('--tasrows', ''); N = opt('--n', 0); DB = opt('--downb', '')
pk = {int(k, 16): int(v) for k, v in (x.split('=') for x in PK.split(',') if x)}
F0 = int(a[0]); rows = []
for p in a[1:]: rows += rows_file(p)
if TRW:
    t1, t2 = map(int, TRW.split('-')); tl = legalize_tas(t1, t2, rows[-150:])
    dbs = [int(x) for x in DB.split(',') if x]
    tl = [tuple(sorted(set(r) | {'Down'})) if 'B' in r and (not dbs or t1 + i in dbs or t1 + i - 1 in dbs) else r for i, r in enumerate(tl)]
    rows += tl
if N: rows = (rows + [()] * N)[:N]
print('legal', legal_ok(rows) or 'ok', 'rows', len(rows))
fc = base(F0 if not MST else None, MST or None, pk)
st = run(fc, rows)
for e_ in events(st, F0 + 1, EV): print(e_)
s = st[-1]; print('end', F0 + len(st), RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'item', s['item'], 'rm', s['room6e'])
fc.close()
