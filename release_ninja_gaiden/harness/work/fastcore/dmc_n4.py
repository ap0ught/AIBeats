"""Fit: NesHawk conflict iff a NesHawk DMC DMA request lands at a fixed offset from a $4016 read, with read cycles
corrected for the DMA stalls of each core inside the frame (Mesen schedule from its DMC state at NMI entry)."""
import bisect
import collections
import csv
import sys

sys.path.insert(0, 'work/fastcore'); sys.path.insert(0, '.')
from dmc_neshawk import simulate  # noqa: E402
from ng.inputs import read_inputs, to_mask  # noqa: E402

LOG, INP, TRC = sys.argv[1:4]
W, N, R = [], {}, collections.defaultdict(list)
for line in open(LOG):
    p = line.split()
    if p[0] == 'W':
        W.append((int(p[3]), int(p[1]), int(p[2])))
    elif p[0] == 'N':
        N[int(p[2])] = (int(p[1]), int(p[3]), int(p[4]), int(p[5]), p[6] == 'true', int(p[7]))
    elif p[0] == 'F':
        cur = int(p[1])
    elif p[0] == 'R':
        R[cur].append(int(p[1]))
W.sort()
rows = [to_mask(r) for r in read_inputs(INP)]
tr = {int(r['row']): r for r in csv.DictReader(open(TRC))}
conf = set(k for k in tr if tr[k]['lagged'] == '0' and int(tr[k]['pad']) != rows[k - 1])
chg = sorted(k for k in tr if tr[k]['lagged'] == '0' and k >= 2 and int(tr[k - 1]['pad']) != rows[k - 1]
             and k in N and len(R.get(k, [])) >= 16)


def mesen_dmas(f):
    n, tau, per, b, empty, L = N[f]
    per += 1
    t = n + tau + 1 + (b - 1) * per
    out = []
    full = not empty
    while L > 0 and full and t < n + 4000:
        out.append(t)
        L -= 1
        t += 8 * per
    return out


def vis(mask, prevpad, j):
    b = [(mask >> (7 - k)) & 1 for k in range(8)]
    jj = j % 8
    alt = b[:jj] + b[jj + 1:] + [1]
    v = 0
    for x in alt:
        v = (v << 1) | x
    return v != mask and prevpad != mask


MD = {f: mesen_dmas(f) for f in chg}
t_end = max(v[0] for v in N.values()) + 40000
results = []
for c0 in range(-60, 61):
    d = simulate(W, c0, t_end)
    for sM in (3, 4):
        for sN in (3, 4, 5):
            hits = collections.defaultdict(lambda: [0, 0])
            for f in chg:
                n0 = N[f][0]
                rr = R[f][:16]
                md = MD[f]
                i0 = bisect.bisect_left(d, n0 - 10)
                i1 = bisect.bisect_left(d, rr[-1] + 40)
                nd = d[i0:i1]
                m = rows[f - 1]
                prev = int(tr[f - 1]['pad'])
                offs = set()
                for j, r in enumerate(rr):
                    nm = sum(1 for x in md if x < r)
                    rn = r - sM * nm
                    for _ in range(2):
                        nn = sum(1 for x in nd if x < rn)
                        rn2 = r - sM * nm + sN * nn
                        if rn2 == rn:
                            break
                        rn = rn2
                    for x in nd:
                        o = rn - x
                        if -6 <= o <= 6 and vis(m, prev, j):
                            offs.add(o)
                for o in offs:
                    hits[o][0 if f in conf else 1] += 1
            for o, (tp, fp) in hits.items():
                results.append((tp - fp, tp, fp, c0, sM, sN, o))
results.sort(reverse=True)
print('conflicts', len(conf), 'change frames', len(chg))
for r in results[:20]:
    print('score %d tp %d fp %d  c0 %d sM %d sN %d offset %d' % r)
