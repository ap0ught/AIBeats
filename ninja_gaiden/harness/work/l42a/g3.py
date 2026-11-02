"""18,242 evasion without B (np 5 poked at 18,200): replace the TAS jump (A 18,240-41) by A at j (2 rows) [or none],
optional A at j2; TAS B rows 1245/1277/1394 -> Right; spin B kept at 18,507. Report hits/np/X at 18,400 and 18,760."""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
r = [tuple(x) for x in C.rows_of('work/l42a/s1763.txt')]
for k in (1245, 1246, 1277, 1278, 1394, 1395, 1240+3, 1244):
    pass
base = list(r)
for k in (1245, 1246, 1277, 1278, 1394, 1395):
    base[k - 1] = ('Right',)
fc = core(); fc.step(base[:18200 - F0], record='last'); fc.poke(0x64, 5); fc.save('b'); fc._ka_slot = 'b'
batch = []; meta = []
def strip_a(rows, lo, hi):
    for f in range(lo, hi + 1):
        rows[f - F0 - 1] = tuple(x for x in rows[f - F0 - 1] if x != 'A') or ('Right',)
for j in [None] + list(range(18220, 18262)):
    for j2 in [None] + list(range(18250, 18300, 3)):
        if j2 and j and j2 < j + 6: continue
        rows = list(base)
        strip_a(rows, 18235, 18250)
        for jj in (j, j2):
            if jj:
                for f in (jj, jj + 1): rows[f - F0 - 1] = tuple(sorted(set(rows[f - F0 - 1]) | {'A'}))
        batch.append(rows[18200 - F0:18760 - F0]); meta.append((j, j2, rows))
res = []
for i in range(0, len(batch), 20):
    rr = fc.run_batch('b', batch[i:i + 20], record='all')
    for (j, j2, rows), rq in zip(meta[i:i + 20], rr):
        st = rq.states
        hits = [18201 + q for q, s in enumerate(st) if q and s['hp'] < st[q - 1]['hp']]
        s4 = st[18400 - 18201]; e = st[-1]
        res.append((len(hits), -C.abs_x(e), j, j2, hits[:3], C.abs_x(s4), C.abs_x(e), e['y'], e['hp'], e['ninpo'], e['item'], L.check(rows[:18760 - F0], HIST).get('pass')))
fc.close()
import json; json.dump([list(map(str,q)) for q in res], open('work/l42a/g3_res.json','w'))
res.sort(key=lambda q: (q[0], q[1]))
for q in res[:25]: print(q)
print('TAS X at 18400/18760:', C.abs_x(TT[18400 - 316]), C.abs_x(TT[18760 - 316]))
