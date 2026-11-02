"""Room-18 exit boost (launch into room 19), legal variants from the TAS state 19,660 (TAS hp 13 there).
Rows 19,661..19,699 = TAS (legal: Right + the 19,669 A); exit window 19,700..19,712: Right until the Left press, A press
(start a, len la), Left press (start l, len ll); then room 19 rows = TAS 19,734..19,766 legalized with the 19,747 A+Left
shifted by d. Score: distance to the TAS at 19,766 (X 118, y 160 before its L+R pillar zip) and the y reached."""
import sys, itertools; sys.path.insert(0, 'work/l43p')
from lib import *
S = 19660
tgt = tas_xy(19766); print('TAS @19766', tgt, 'TAS @19760', tas_xy(19760))
pre = legalize_tas(19661, 19699, [()] * 60)
cands = []; desc = []
for a, la, l, ll in itertools.product(range(19700, 19708), (2, 3), range(19699, 19708), (2, 3)):
    w = []
    for f in range(19700, 19734):
        r = set()
        if f < l: r.add('Right')
        if a <= f < a + la: r.add('A')
        if l <= f < l + ll: r.add('Left')
        w.append(tuple(sorted(r)))
    for d in (-2, -1, 0, 1, 2, 3):
        post = []
        for f in range(19734, 19767):
            r = set(T(f)) - {'A'}
            if f in (19737,): r |= {'A'}
            post.append(tuple(sorted(r)))
        # 19,747 A+Left shifted by d (2 frames)
        k = 19747 + d - 19734
        post[k] = tuple(sorted(set(post[k]) | {'A', 'Left'})); post[k + 1] = tuple(sorted(set(post[k + 1]) | {'A', 'Left'}))
        post[3] = ('A', 'Left'); post[4] = ('A', 'Left')    # 19,737-38 A+Left
        rows = pre + w + post
        if legal_ok(rows, [()] * 60): continue
        cands.append(rows); desc.append((a, la, l, ll, d))
print(len(cands), 'legal candidates', flush=True)
fc = core(tas_mst(S))
res = fc.run_batch('s', cands, record='all')
fc.close()
out = []
for dsc, r in zip(desc, res):
    st = r.states
    if len(st) < 106: continue
    ent = next((i for i, s in enumerate(st) if s['room6e'] == 19), None)
    xy = XY(st[-1]); ymin = min(XY(s)[1] for s in st[80:])
    hpe = st[-1]['hp65']
    out.append((abs(xy[0] - tgt[0]) + abs(xy[1] - tgt[1]), ymin, dsc, xy, hpe, S + 1 + ent if ent is not None else None))
out.sort(key=lambda z: (z[0], z[1]))
for z in out[:25]: print(z)
