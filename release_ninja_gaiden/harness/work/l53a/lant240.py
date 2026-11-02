"""l53a: price the room-27 +5 lantern X 240 y 160 on the ch1 line (TAS-state axis, row k = TAS frame k, from 26608):
jump (A+Left x2) at j, then a slash (Down+B x2 or B+Left x2) d frames later, rest = ch1 rows. Report np, hp, X at 26930,
room-28 frame. python work/l53a/lant240.py"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
base = [row(l.strip()) for l in open('work/l53a/ch1_rows.txt') if l.strip()]
hist = [row(l.strip()) for l in open('work/l53a/hist_e1_27396.txt')]
fc = core('states/mesen/l53a_e1_27396.mst'); fc.save('b'); fc._ka_slot = 'b'
F = 26608
cands = []
for j in range(26884, 26930):
    for d in range(2, 18):
        for sl in (('B', 'Down'), ('B', 'Left')):
            rows = list(base) + [()] * 40
            rows[j - F] = rows[j + 1 - F] = ('A', 'Left')
            rows[j + d - F] = rows[j + d + 1 - F] = sl
            if legal_ok(rows[:len(base)], hist): continue
            cands.append(((j, d, sl), rows))
print('legal cases', len(cands), flush=True)
out = []
for i in range(0, len(cands), 48):
    rr = fc.run_batch('b', [c[1] for c in cands[i:i+48]], record='all')
    for (m, rows), r in zip(cands[i:i+48], rr):
        st = r.states; r28 = None; caught = 0; prev = None; hp = st[-1]['hp65']
        for k, s in enumerate(st):
            if prev and s['np64'] > prev['np64']: caught += s['np64'] - prev['np64']
            if prev and s['room6e'] != prev['room6e'] and r28 is None: r28 = F + k
            prev = s
        out.append((m, caught, st[-1]['np64'], hp, RXY(st[26930 - F]), r28))
good = [o for o in out if o[1] and o[3] == 6]
print('caught +5, no hit:', len(good))
for o in sorted(good, key=lambda o: (o[5] or 99999, -o[4][0]))[:15]: print(o)
good2 = [o for o in out if o[2] >= 30 and o[3] >= 6]
print('np end >= 30 (plain slash), no hit:', len(good2))
for o in sorted(good2, key=lambda o: (o[5] or 99999, -o[4][0]))[:15]: print(o)
print('any caught', len([o for o in out if o[1]]))
fc.close()
