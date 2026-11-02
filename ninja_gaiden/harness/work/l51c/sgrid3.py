"""vectorized sim: TWO waits (k1,w1),(k2,w2), w1+w2 <= MAXC, on ground frames (k2 may be the step KS+1). Both birds.
Success = first bird hit during the step jump with Ryu y <= 132. python work/l51c/sgrid3.py MAXC kstep"""
import sys, json, numpy as np
MAXC = int(sys.argv[1]); KSTEP = int(sys.argv[2])
BASE = sys.argv[4] if len(sys.argv) > 4 else None
if BASE:
    D = json.load(open(BASE)); BP = [dict(D['path'][0], f=D['cut'])] + D['path']; LAG = int(sys.argv[5]); F1 = BP[0]['f']
    BPc = json.load(open('work/l51c/base_path.json'))
    KS = 23670 + LAG - F1; KJ = 23714 + LAG - F1
    SP = next(i for i, a in enumerate(BP) if a['cam'] >= BPc[283]['cam'])
    bi = D['bird']
else:
    BP = json.load(open('work/l51c/base_path.json'))
    KS = 24200 - 23664; KJ = 24244 - 23664; SP = 283; bi = None
print('KS', KS, 'KJ', KJ, 'SP', SP, flush=True)
cam = np.array([a['cam'] for a in BP], np.int64); rx = np.array([a['rx'] for a in BP]); ry = np.array([a['y'] for a in BP])
fz = np.array([a['fz'] for a in BP]); air = np.array([a['air'] for a in BP]); Xr = np.array([a['X'] for a in BP])
slash = np.array(['B' in a['row'].split('+') for a in BP])
ground = [k for k in range(1, KS + 2) if not air[k - 1] and not air[k]] + [KS + 1]
ground = sorted(set(ground[::KSTEP] + [KS + 1]))
C = []
for i1, k1 in enumerate(ground):
    for k2 in ground[i1 + 1:]:
        for w1 in range(1, MAXC):
            for w2 in range(1, MAXC + 1 - w1):
                C.append((k1, w1, k2, w2))
for k1 in ground:
    for w1 in range(1, MAXC + 1): C.append((k1, w1, 10**6, 0))
C = np.array(C, np.int64); N = len(C); print('cands', N, flush=True)
k = np.zeros(N, np.int64); rem = np.zeros(N, np.int64)   # rem = wait frames left before advancing to index k+1
a0 = BP[0]
if bi:
    B0 = np.full(N, bi['B'], np.int64); V0 = np.full(N, bi['V'], np.int64); Y0 = np.full(N, bi['Y'], np.int64)
else:
    B0 = np.full(N, a0['cam'] + a0['bx']*256 + a0['bs'], np.int64); V0 = np.full(N, a0['v'], np.int64); Y0 = np.full(N, a0['by'], np.int64)
A0 = np.ones(N, bool)
B1 = np.zeros(N, np.int64); V1 = np.zeros(N, np.int64); Y1 = np.zeros(N, np.int64); A1 = np.zeros(N, bool)
done = np.zeros(N, bool); succ = np.zeros(N, bool); left = np.zeros(N, bool); hk = np.zeros(N, np.int64); used1 = np.zeros(N, bool); used2 = np.zeros(N, bool)
def stepb(B, V, Y, A, c, r, y, f):
    m = A & (f == 0)
    Yn = np.where(y >= Y, Y + 1, Y - 1); sx = (B - c) >> 8
    Vn = np.where(sx >= r, V - 16, V + 16)
    return np.where(m, B + Vn, B), np.where(m, Vn, V), np.where(m, Yn, Y)
def hitc(B, Y, A, c, r, y):
    sx = (B - c) >> 8; dy = y - Y
    return A & (np.abs(sx - r) < 10) & (((dy >= 0) & (dy < 25)) | ((dy < 0) & (dy > -8)))
it = 0
while True:
    act = ~done
    if not act.any(): break
    nxt = k + 1
    # waits trigger before advancing into index k1 / k2
    s1 = act & ~used1 & (nxt == C[:, 0]); rem[s1] = C[s1, 1]; used1 |= s1
    s2 = act & ~used2 & (nxt == C[:, 2]); rem[s2] = C[s2, 3]; used2 |= s2
    waiting = act & (rem > 0)
    adv = act & ~waiting
    k = np.where(adv, nxt, k); rem = np.where(waiting, rem - 1, rem)
    kk = np.minimum(k, len(BP) - 1)
    c = cam[kk]; r = rx[kk]; y = ry[kk]; f = np.where(waiting, 0, fz[kk])
    # spawn #19
    sp = adv & (k == SP) & ~A1
    B1 = np.where(sp, cam[SP] + 176*256 + 2, B1); V1 = np.where(sp, 0, V1); Y1 = np.where(sp, 208, Y1); A1 |= sp
    B0, V0, Y0 = stepb(B0, V0, Y0, A0 & act, c, r, y, f)
    B1, V1, Y1 = stepb(B1, V1, Y1, A1 & act & ~sp, c, r, y, f)
    # slash kill (crude)
    sl = adv & slash[kk]
    d0 = (B0 >> 8) - Xr[kk]; A0 &= ~(sl & (d0 >= 0) & (d0 < 32) & (Y0 - y > -40) & (Y0 - y < 10))
    h = act & (hitc(B0, Y0, A0, c, r, y) | hitc(B1, Y1, A1, c, r, y))
    inwin = (k > KS) & (k <= KJ) & (y <= 132)
    h0 = hitc(B0, Y0, A0, c, r, y); lf = np.where(h0, ((B0 - c) >> 8) < r, ((B1 - c) >> 8) < r)
    nh = h & inwin & ~succ; left |= nh & lf; hk = np.where(nh, k, hk)
    succ |= h & inwin; done |= h | (k >= KJ)
    it += 1
cost = C[:, 1] + C[:, 3]
idx = np.where(succ & left)[0] if len(sys.argv) > 3 and sys.argv[3] == 'L' else np.where(succ)[0]; idx = idx[np.argsort(cost[idx])]
print('successes', len(idx))
for i in idx[:400]: print('cost', cost[i], 'k1', BP[C[i,0]]['f'] if C[i,0] < len(BP) else C[i,0], 'w1', C[i,1], 'k2', BP[C[i,2]]['f'] if C[i,2] < len(BP) else '-', 'w2', C[i,3], 'L' if left[i] else 'R', 'hitX', Xr[hk[i]], 'kafter', hk[i])
