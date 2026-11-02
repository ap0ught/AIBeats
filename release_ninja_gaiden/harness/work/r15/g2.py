"""stage 2: jump timing from the branch for g1's best candidates. python work/r15/g2.py <g1 json> <N> <out>"""
import sys, json; sys.path.insert(0, 'work/r15')
from rlib import *
g = json.load(open(sys.argv[1])); N = int(sys.argv[2]); out = sys.argv[3]
S = g['S']; base = C.rows_of(g['base']); pre = base[:S - F0]
lands = [r for r in g['rows'] if r[0]][:N]
cands = []; desc = []
for (land, d, hp, kill, np), c in zip(lands, g['cands'][:N]):
    c = [tuple(x) for x in c]
    for j in range(land - 4, land + 4):
        for pre_r in (0, 1):
            r = list(c[:j - S - 1])
            if pre_r: r[-1] = ('Right',) if r and 'B' not in r[-1] and 'A' not in r[-1] else r[-1]
            r += [('A', 'Right')] * 2 + [('Right',)] * 40
            if legal(pre, r): cands.append(r); desc.append((tuple(d), land, j, pre_r))
print('cands', len(cands), flush=True)
t = time.time(); res = run(cands, pre)
print('time', round(time.time() - t), flush=True)
rows = []
for i, st in enumerate(res):
    v = None
    for s in st:
        if s['hp'] == 0 or s['item'] != 133: break
        if s['room'] == 15 and s['X'] >= 140 and s['y'] <= 100: v = s['frame']; break
    alive = any(s['eact'] >> 7 & 1 and s['t7'] == 11 for s in st[-2:])
    rows.append((v, desc[i], st[-1]['ninpo'], st[-1]['hp'], alive))
rows.sort(key=lambda t: (t[0] is None, t[0] or 0))
for r in rows[:40]: print(r, flush=True)
best = [cands[desc.index(r[1])] for r in rows[:50] if r[0]]
json.dump({'S': S, 'base': g['base'], 'rows': rows[:300], 'best': best}, open(out, 'w'))
close()
