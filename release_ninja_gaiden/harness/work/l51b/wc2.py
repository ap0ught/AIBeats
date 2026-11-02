"""Boosted wall climb enumeration from a state at/just before the bird hit:
rows = [lr]*lead + [A+L]*a + [R]*n0 + ([A+L]*a + [R]*n)*k + R...   goal X>=1530 and y<=100 (TAS 23,133)
python work/l51b/wc2.py <mst> F0 <hist> [--leads 4:20] [--nr 75] [--out file]"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
a_ = sys.argv[1:]
def opt(n, d):
    if n in a_:
        i = a_.index(n); v = a_[i+1]; del a_[i:i+2]; return type(d)(v)
    return d
LE = opt('--leads', '4:20'); FAM = [int(x) for x in opt('--fam', '2,3,11,12,13,14').split(',')]; N0A, N0B = map(int, opt('--n0', '2:9').split(':')); NA, NB = map(int, opt('--n', '3:9').split(':')); NR = opt('--nr', 75); OUT = opt('--out', ''); TOP = opt('--top', 20)
mst, F0, H = a_[0], int(a_[1]), a_[2]
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
AL_, R_, N_ = ('A', 'Left'), ('Right',), ()
l1, l2 = map(int, LE.split(':'))
cands = []; seen = set()
for lead in range(l1, l2):
    for lr in (R_, N_):
        for a in FAM:
            cyc0 = {2: [AL_] * 2, 3: [AL_] * 3, 11: [AL_, ('A', 'Right')], 12: [('Left',), AL_, ('A', 'Right')], 13: [AL_, AL_, ('A', 'Right')], 14: [('Left',), AL_, ('A', 'Right'), ('A', 'Right')]}[a]
            for n0 in range(N0A, N0B):
                for n in range(NA, NB):
                    w = [lr] * lead + cyc0 + [R_] * n0 + (cyc0 + [R_] * n) * 8
                    w = (w + [R_] * NR)[:NR]
                    rows = enforce([set(x) for x in w], hist)
                    if legal_ok(rows, hist) or tuple(rows) in seen: continue
                    seen.add(tuple(rows)); cands.append(((lead, P(lr), a, n0, n), rows))
print('cands', len(cands), flush=True)
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 100):
    ch = cands[i:i+100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all')
    for (key, rows), r in zip(ch, rr):
        g = next((t for t, s in enumerate(r.states) if RXY(s)[0] >= 1530 and s['y8a'] <= 100), None)
        top = next((t for t, s in enumerate(r.states) if s['y8a'] <= 100 and RXY(s)[0] >= 1505), None)
        res.append((F0 + 1 + g if g is not None else 99999, F0 + 1 + top if top is not None else 99999, key, min(s['hp65'] for s in r.states)))
res.sort()
for x in res[:TOP]: print(x, flush=True)
if OUT and res[0][0] < 99999:
    key = res[0][2]; rows = [rw for kk, rw in cands if kk == key][0]
    C.write_inputs(OUT, rows[:res[0][0] - F0], f'wc2 {mst} best {res[0]}')
    print('wrote', OUT)
fc.close()
