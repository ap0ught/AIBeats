"""Research state from a TAS state: python work/l51b/mkst.py S c K tag [mods 't1-t2=ROW,...'] [--rows file]
TAS state S (after row S) with $BF poked for c (= BF after the 5-1 control row on our axis, c 78 + lag), then the
legalized TAS rows S+1..K (or the rows in --rows file, played from S+1) -> states/mesen/l51b_<tag>.mst (after row K, TAS axis)
+ history work/l51b/h_<tag>.inputs.txt (legalized TAS rows before S + played rows)."""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
a = sys.argv[1:]
RF = ''
if '--rows' in a:
    i = a.index('--rows'); RF = a[i+1]; del a[i:i+2]
S, c, K, tag = int(a[0]), int(a[1]), int(a[2]), a[3]
mods = {}
if len(a) > 4 and a[4]:
    for it in a[4].split(','):
        k, v = it.split('='); k1, k2 = (k.split('-') + [k])[:2]
        for t in range(int(k1), int(k2) + 1): mods[t] = set(row(v))
hist = [tuple(sorted(w)) for w in tasleg(S - 300, S)]
hist = enforce(hist, [()] * 30)
if RF:
    rows = [tuple(sorted(r)) for r in C.rows_of(RF)]; K = S + len(rows)
else:
    rows = enforce(tasleg(S + 1, K, mods), hist)
lg = legal_ok(rows, hist)
print('legal', lg or 'ok', len(rows))
fc = core(tas_mst(S)); fc.poke(0xBF, (c + S - 22125) % 256)
if rows:
    _, recs, _ = fc.step(rows, record='all'); print('hits', trackhits(recs, S + 1)); r = recs[-1]
else:
    r = fc.step([], record='last')[1][-1] if False else None
if r is None:
    m = fc.ram(); X, y = XY(m); r = {'hp65': m[0x65], 'np64': m[0x64], 'item': m[0xC9], 'bf': m[0xBF]}
else:
    X, y = RXY(r)
print('after', K, 'X,y', (X, y), 'TAS', tas_xy(K), 'hp', r['hp65'], 'np', r['np64'], 'it', r['item'], 'BF', r['bf'])
fc.save('o'); fc.save_file('o', f'states/mesen/l51b_{tag}.mst', frame=K)
C.write_inputs(f'work/l51b/h_{tag}.inputs.txt', list(hist) + list(rows), f'l51b {tag}: TAS-axis rows to {K} (c {c})')
fc.close()
