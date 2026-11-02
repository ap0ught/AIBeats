"""Throw variants from TAS 23,700 (c = 78 + lag) run to 23,990 with Right after 23,830 replaced by TAS rows:
python work/l51b/thr2.py lag"""
import sys, itertools
sys.path.insert(0, 'work/l51b')
from lb import *
L = int(sys.argv[1]); c = 78 + L
S = 23700; N = 23990
hist = enforce(tasleg(S - 300, S), [()] * 30)
fc = core(tas_mst(S)); fc.poke(0xBF, (c + S - 22125) % 256); fc.save('b'); fc._ka_slot = 'b'
def run(mods):
    rows = enforce(tasleg(S + 1, N, mods), hist)
    lg = legal_ok(rows, hist)
    fc.load('b'); _, recs, _ = fc.step(rows, record='all')
    ev = []; hp = None; np_ = None
    for i, r in enumerate(recs):
        if hp is not None and r['hp65'] != hp: ev.append(f'{S+1+i}:hp{hp}->{r["hp65"]}@{RXY(r)[0]}')
        if np_ is not None and r['np64'] != np_: ev.append(f'{S+1+i}:np{np_}->{r["np64"]}')
        hp = r['hp65']; np_ = r['np64']
    g = next((S + 1 + i for i, r in enumerate(recs) if RXY(r)[0] >= 2760 and r['y8a'] <= 100), None)
    return lg, ' '.join(ev), RXY(recs[23830 - S - 1]), g
print('TAS: X>=2760 at 23963')
res = []
for t1 in range(23738, 23750):
    for t2 in range(23770, 23786):
        for r1 in ('BUR', 'BU'):
            m = {}
            for t in (t1, t1 + 1, t2, t2 + 1): m[t] = {'B', 'Up', 'Right'} if r1 == 'BUR' else {'B', 'Up'}
            out = run(m)
            res.append((out[3] or 99999, t1, t2, r1, out))
res.sort()
for r in res[:25]: print(r)
fc.close()
