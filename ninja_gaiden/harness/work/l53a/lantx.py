"""l53a: price the room-27 +5 lanterns on the ch1 line by INSERTING rows (stage rows; row 1 = 5-3 control row) on the e4 state.
X 400: insert [Down+B x2] before stage row k. X 240: replace rows j, j+1 by A+Left (jump) and insert [Down+B x2] before row j+d.
Both: combos. Reports room-28 frame, hp, np. python work/l53a/lantx.py"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
base = [row(l.strip()) for l in open('work/l53a/ch1_rows.txt') if l.strip()]
hist = [row(l.strip()) for l in open('work/l53a/hist_e4_27359.txt')]
F = 27360
fc = core('states/mesen/l53a_e4_27359.mst'); fc.save('b'); fc._ka_slot = 'b'
DB, AL = ('B', 'Down'), ('A', 'Left')
def mk(k400=None, j240=None, d240=None):
    rows = list(base)
    if j240 is not None:
        rows[j240 - 1] = rows[j240] = AL
        i = j240 - 1 + d240; rows[i:i] = [DB, DB]
    if k400 is not None:
        rows[k400 - 1:k400 - 1] = [DB, DB]
    return rows
cands = [(('base',), base)]
if 'combo' in sys.argv:
    for k in range(211, 219):
        for j in range(294, 304):
            for d in range(9, 16): cands.append((('both', k, j, d), mk(k400=k, j240=j, d240=d)))
for k in ([] if 'combo' in sys.argv else range(205, 222)): cands.append((('x400', k), mk(k400=k)))
for j in ([] if 'combo' in sys.argv else range(276, 330, 1)):
    for d in range(3, 16): cands.append((('x240', j, d), mk(j240=j, d240=d)))
cands = [(m, r) for m, r in cands if not legal_ok(r, hist)]
print('legal cases', len(cands), flush=True)
res = []
for i in range(0, len(cands), 48):
    rr = fc.run_batch('b', [c[1] + [()] * 30 for c in cands[i:i+48]], record='all')
    for (m, rows), r in zip(cands[i:i+48], rr):
        st = r.states; r28 = None; prev = None; ev = []
        for q, s in enumerate(st):
            if prev:
                if s['room6e'] != prev['room6e'] and r28 is None: r28 = F + q
                for kk in ('hp65', 'np64'):
                    if s[kk] != prev[kk]: ev.append(f'{F+q}:{kk[:2]}{prev[kk]}>{s[kk]}')
            prev = s
        res.append((m, r28, st[-1]['hp65'], st[-1]['np64'], ' '.join(ev)))
for g in ('base', 'x400', 'x240', 'both'):
    sub = [q for q in res if q[0][0] == g and q[1] and q[2] == 3]
    print(g, 'ok (room 28, hp 3):', len(sub), 'of', len([q for q in res if q[0][0] == g]))
    for q in sorted(sub, key=lambda q: (q[1], -q[3]))[:8]: print('  ', q)
fc.close()
