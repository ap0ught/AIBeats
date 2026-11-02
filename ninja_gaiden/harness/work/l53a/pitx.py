"""l53a: proof grids for the room-27 pit WITHOUT the platform (TAS state 26607, hp poked 12).
G1 ground jumps (A+Left at k) + Left; G2 = G1 + one J&S spin (B+Left) j f after takeoff; G3 = G1 + a plain Down+B slash;
G4 from the X-545 pillar cling (pre53 rows to 26704): A+Right jump-off then air patterns (Left / new-press keep-speed / waits).
Success = Ryu on the floor left of the pit (X <= 479, y 208) or on any floor X < 496 with hp > 0.
python work/l53a/pitx.py"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core(tas_mst(26607)); fc.poke(0x65, 12); fc.save('b'); fc._ka_slot = 'b'
L, AL, BL, DB, N, AR, R = ('Left',), ('A', 'Left'), ('B', 'Left'), ('B', 'Down'), (), ('A', 'Right'), ('Right',)
pre = [row(l.strip()) for l in open('work/l53p/pre53_26704.txt') if l.strip() and not l.startswith('#')]
cands, meta = [], []
for k in range(30, 96):
    base = [L] * k + [AL, AL]
    cands.append(base + [L] * 120); meta.append(('G1', k))
    for j in range(1, 34, 2):
        cands.append(base + [L] * j + [BL, BL] + [L] * 120); meta.append(('G2', k, j))
        cands.append(base + [L] * j + [DB, DB] + [L] * 120); meta.append(('G3', k, j))
pats = {'L': [L] * 60, 'keep': ([BL, N, AL, N, N] + [N] * 0) * 12, 'keep2': ([BL, BL, N, AL, AL] ) * 12,
        'wait': [N] * 60, 'R': [R] * 60}
for d in range(0, 12):
    for nm, p in pats.items():
        for pre_air in ([], [L] * 2, [N] * 2):
            rows = pre[:-1] + [N] * d + [AR, AR] + pre_air + p
            cands.append(rows[:96 + 140]); meta.append(('G4', d, nm, len(pre_air)))
res = []
bad = 0
for i in range(0, len(cands), 48):
    rr = fc.run_batch('b', [c[:240] for c in cands[i:i+48]], record='all')
    for m, c, r in zip(meta[i:i+48], cands[i:i+48], rr):
        if legal_ok(c): bad += 1; continue
        ok = None; minx = 999; dead = False
        for j, s in enumerate(r.states):
            X, y = RXY(s)
            if s['hp65'] == 0 or y >= 240: dead = True; break
            if y < 216: minx = min(minx, X)
            if X <= 495 and y == 208 and (s['coll'] & 0x10): ok = 26608 + j; break
            if X <= 495 and y == 192 and (s['coll'] & 0x10): ok = 26608 + j; break
        res.append((ok or 99999, m, dead, minx))
print('cases', len(res), 'illegal skipped', bad)
for g in ('G1', 'G2', 'G3', 'G4'):
    sub = [q for q in res if q[1][0] == g]
    succ = [q for q in sub if q[0] < 99999]
    print(g, 'cases', len(sub), 'successes', len(succ), 'min X reached (y<216)', min(q[3] for q in sub), 'deaths', sum(q[2] for q in sub))
    for q in sorted(succ)[:5]: print('   ', q)
fc.close()
