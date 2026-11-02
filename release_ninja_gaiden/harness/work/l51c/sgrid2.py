"""sim: one wait (k, w) on the ground before the step + j blank frames on the step (TAS-eq 23,670), then the base
TAS rows (jump 23,679). Birds: wall bird (alive unless the sim's slash check kills it) + #19 (spawn at path index 283).
Report combos whose FIRST bird hit is during the step jump with Ryu y <= 132, ranked by w + j.
python work/l51c/sgrid2.py [maxcost] [killwall]"""
import sys; sys.path.insert(0, 'work/l51c')
from bsim2 import *
MAXC = int(sys.argv[1]) if len(sys.argv) > 1 else 30
KILLWALL = int(sys.argv[2]) if len(sys.argv) > 2 else 0
KS = 24200 - 23664          # path index of the step arrival (TAS-eq 23,670)
KJ = 24244 - 23664          # end of the jump window (TAS-eq 23,714)
SPAWN19 = 283
SLASH = {k for k, a in enumerate(BP) if 'B' in a['row'].split('+')}
def hit(b, a):
    sx = (b[0] - a['cam']) >> 8
    if abs(sx - a['rx']) >= 10: return False
    dy = a['y'] - b[2]
    return (0 <= dy < 25) or (-8 < dy < 0)
def killed(b, a):
    d = (b[0] >> 8) - a['X']
    return 0 <= d < 32 and -40 < b[2] - a['y'] < 10
def adv(birds, a, fz=None):
    out = []
    for b in birds:
        out.append(None if b is None else step(b, a['cam'], a['rx'], a['y'], a['fz'] if fz is None else fz))
    return out
def spawn19(k):
    a = BP[k]; return (a['cam'] + 176*256 + 2, 0, 208)
res = []
# prefix states at each index (no wait): birds after index k
pre = {0: [init(0), None]}
birds = [init(0), None]
for k in range(1, KS + 1):
    a = BP[k]
    birds = adv(birds, a)
    if k == SPAWN19: birds[1] = spawn19(k)
    if KILLWALL and k in SLASH and birds[0] and killed(birds[0], a): birds[0] = None
    pre[k] = list(birds)
def walk(birds, k1, k2, waitat=None, w=0):
    """advance from after index k1 to after k2 with a w-frame stand before index waitat; return (birds, firsthit)"""
    for k in range(k1 + 1, k2 + 1):
        if k == waitat:
            p = BP[k - 1]
            for _ in range(w):
                pp = dict(p); pp['fz'] = 0
                birds = adv(birds, pp)
                for i, b in enumerate(birds):
                    if b and hit(b, p): return birds, (k, i, 'wait')
        a = BP[k]
        birds = adv(birds, a)
        if k == SPAWN19 and birds[1] is None: birds[1] = spawn19(k)
        if KILLWALL and k in SLASH and birds[0] and killed(birds[0], a): birds[0] = None
        for i, b in enumerate(birds):
            if b and hit(b, a): return birds, (k, i, a['X'], a['y'])
    return birds, None
for k in range(1, KS + 1):
    if BP[k - 1]['air'] or BP[k]['air']: continue
    for w in range(0, MAXC + 1):
        if w == 0 and k > 1: continue
        b, h = walk(list(pre[k - 1]), k - 1, KS, k, w)
        if h: continue
        for j in range(0, MAXC + 1 - w):
            bb, h2 = walk(list(b), KS, KJ, KS + 1, j)
            if h2 and h2[2] != 'wait' and h2[3] <= 132:
                res.append((w + j, BP[k]['f'], w, j, h2, [None if x is None else (x[0] >> 8, x[1], x[2]) for x in bb]))
                break
res.sort(key=lambda q: q[0])
print(len(res))
for r in res[:40]: print(r)
# summary: unique outcomes
seen = {}
for r in res:
    c, f, w, j, h, bb = r
    k, i = h[0], h[1]
    side = 'L' if bb[i][0] < h[2] else 'R'
    key = (w, j, k, i, side)
    seen.setdefault(key, []).append(f)
print('--- unique (w, j, hit k, bird, side): our frames s')
for key in sorted(seen, key=lambda q: (q[0] + q[1], q[2])):
    fs = seen[key]; print(key, 'cost', key[0] + key[1], 'hit TAS-eq', BP[key[2]]['f'] - 530, 's', fs[0], '-', fs[-1], len(fs))
