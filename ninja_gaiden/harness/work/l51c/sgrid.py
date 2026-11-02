"""sim grid: one wait (k, w) on the base path; compare the wall bird with the TAS's s7 at TAS-eq checkpoints."""
import sys; sys.path.insert(0, 'work/l51c'); sys.path.insert(0, 'work/l51p')
from bsim2 import *
from lib0 import TM, XY
LAG = 530
def tas_rel(t, j=7):
    m = TM(t); X, y = XY(m); scr = (m[0x52]-256 if m[0x52] >= 128 else m[0x52])*256 + m[0x51]
    v = m[0x450+j]*256 + m[0x448+j]; v = v - 65536 if v >= 32768 else v
    return ((scr + m[0x460+j])*256 + m[0x458+j]) / 256 - X, v, m[0x480+j] - y
CK = [23450, 23500, 23550, 23600, 23650, 23670, 23700]
TR = {t: tas_rel(t) for t in CK}
def kof(t): return t + LAG - 23664    # path index of TAS-eq t (no wait)
res = []
b0 = init(0)
kmax = kof(23700)
# precompute prefix states
pre = {}; b = b0
for k in range(1, kmax + 1):
    pre[k - 1] = b
    a = BP[k]; b = step(b, a['cam'], a['rx'], a['y'], a['fz'])
for k in range(1, kof(23660)):
    if BP[k - 1]['air'] or BP[k]['air']: continue
    for w in range(1, 61):
        b = pre[k - 1]; p = BP[k - 1]
        for _ in range(w): b = step(b, p['cam'], p['rx'], p['y'], 0)
        err = 0; det = []
        for kk in range(k, kmax + 1):
            a = BP[kk]; b = step(b, a['cam'], a['rx'], a['y'], a['fz'])
            t = a['f'] - LAG
            if t in TR:
                u = b[0]/256 - a['X']; uT, vT, dyT = TR[t]
                e = abs(u - uT) + 16*abs(b[1] - vT)/256
                err = max(err, e); det.append((t, round(u), b[1]/256, b[2] - a['y']))
        res.append((err, BP[k]['f'], w, det))
res.sort(key=lambda q: q[0])
for r in res[:30]: print(round(r[0], 1), r[1], r[2], r[3][-3:])
print('TAS', [(t, round(TR[t][0]), TR[t][1]/256, TR[t][2]) for t in CK[-3:]])
