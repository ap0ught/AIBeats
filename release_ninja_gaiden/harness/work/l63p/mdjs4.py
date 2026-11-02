"""6-4a J&S + 5 phase 2 (Mesen): phase 1 = A 37278, A+Right 37279, Right, A+Right 37301-02, Right, B+Right 37304-05 (spin),
Right to r=37330, then '-' (lands on the middle pedestal); phase 2: jump A x2 at j1 (+dir), slash cycles (Down|Down+B|B|-|-) from s1,
optional second jump at j2 with cycles. Stop at $66 == 0."""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
F0 = 37277; N = 130
R1 = int(sys.argv[1]) if len(sys.argv) > 1 else 37330
fc = core_at(F0)
for k, v in ((0xC9, 133), (0x64, 5), (0xC8, 0)): fc.poke(k, v)
fc.save('b'); fc._ka_slot = 'b'
hist = [()] * 150
CYC = [('Down',), ('B', 'Down'), ('B',), (), ()]
def base(f):
    if f == 37278: return ('A',)
    if f == 37279: return ('A', 'Right')
    if f in (37301, 37302): return ('A', 'Right')
    if f in (37304, 37305): return ('B', 'Right')
    if f < R1: return ('Right',)
    return ()
cands = {}
for j1 in range(37344, 37353):
    for d in range(1, 11):
        for jd in ('-',):
            for j2off in (None, 46):
                rows = []
                s1 = j1 + d
                for f in range(F0 + 1, F0 + 1 + N):
                    x = base(f)
                    if f >= j1 - 2:
                        x = ()
                        if f in (j1, j1 + 1): x = ('A',) if jd == '-' else ('A', jd)
                        elif f >= s1: x = CYC[(f - s1) % 5]
                        if j2off and f in (j1 + j2off, j1 + j2off + 1): x = ('A',)
                        elif j2off and f in (j1 + j2off - 1, j1 + j2off + 2): x = ()
                    rows.append(tuple(sorted(x)))
                if legal_ok(rows, hist): continue
                cands[(j1, d, jd, j2off)] = rows
print('cands', len(cands), flush=True)
names = list(cands); res = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [cands[n] for n in names[i:i+64]], record='all', stops=[(0x66, '==', 0)])
    for n, rr_ in zip(names[i:i+64], rs):
        mb = min(x['bosshp'] for x in rr_.states)
        res.append((0 if rr_.status == 1 else 1, mb, F0 + rr_.rows_played, min(x['hp65'] for x in rr_.states), n))
res.sort(key=lambda q: (q[0], q[1], q[2], str(q[4])))
for x in res[:20]: print(x, flush=True)
print('kills', sum(1 for x in res if x[0] == 0), 'of', len(res))
fc.close()
