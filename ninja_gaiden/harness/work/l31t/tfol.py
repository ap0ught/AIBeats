"""prefix stage rows + TAS rows from TAS frame k0 with one extra 'Up' row after every TAS throw (Up+B) row
(a legal throw releases Right 2 frames); report X behind the TAS, item/ninpo changes, end.
python work/l31t/tfol.py <prefix> <k0> <n> [--out f] [--cut i]"""
import sys
sys.path.insert(0, 'work/l31t'); sys.path.insert(0, '.')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
out = opt('--out', ''); cut = opt('--cut', -1)
pre = C.rows_of(a[0]); k0 = int(a[1]); n = int(a[2])
want = []; tmap = []
for k in range(k0, k0 + n):
    r = tuple(TR[k]); want.append(r); tmap.append(k + 1)
    if 'B' in r and 'Up' in r and 'Right' not in r and 'Left' not in r:
        want.append(('Up',)); tmap.append(None)
rows = list(pre) + legal_after(pre, want)
r = play(rows)
lastk = None; prev = None
for i, s in enumerate(r.states[len(pre):]):
    k = tmap[i] if i < len(tmap) else None
    if k: lastk = k
    t = T[lastk] if lastk else None
    d = round((ax(t) - ax(s)) / 1.5, 1) if t else 0
    key = (s["item"], s["ninpo"], s["hp"], round(d))
    if key != prev or i % 100 == 0:
        print(f"i {len(pre)+i} f {F0+len(pre)+i+1} X {ax(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} it {s['item']} in {'+'.join(rows[len(pre)+i]) or '-'} | TAS {lastk} X {ax(t)} y {t['y']} np {t['ninpo']} it {t['item']} | behind {d}")
        prev = key
    if s['stage'] != 5 or ax(s) >= 2011:
        print('END at frame', F0 + len(pre) + i + 1, 'X', ax(s), 'np', s['ninpo'], 'it', s['item'], 'hp', s['hp'], 'sub62', s['subtimer']); break
if out:
    m = len(rows) if cut < 0 else cut
    C.write_inputs(out, rows[:m], f'3-1 rows: {a[0]} + TAS rows from {k0} with a release row after each throw')
    print('wrote', out, m)
