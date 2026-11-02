import sys, csv, collections
sys.path.insert(0, 'work/fastcore'); sys.path.insert(0, '.')
from ng.inputs import read_inputs, to_mask
rows = [to_mask(r) for r in read_inputs('logs/tas4751.inputs.txt')]
tr = {int(r['row']): r for r in csv.DictReader(open('logs/tas4751.trace.csv'))}
conf = set(k for k in tr if tr[k]['lagged'] == '0' and int(tr[k]['pad']) != rows[k - 1])
F = {}
curf = None
for line in open('work/fastcore/out/dmc1.bin.dmc'):
    p = line.split()
    if p[0] == 'F':
        curf = int(p[1]); F[curf] = dict(T0=int(p[2]), tau=int(p[3]), P=int(p[4]), b=int(p[5]), empty=p[6] == 'true',
                                         left=int(p[7]), silence=p[8] == 'true', R=[])
    else:
        F[curf]['R'].append(int(p[1]))
print('frames logged', len(F), 'conflicts', len(conf))
# Mesen collisions: frames with 17 reads, which read index is duplicated (two reads within 4 cycles)
def dma_times(d):
    per = d['P'] + 1
    t = d['T0'] + d['tau'] + 1 + (d['b'] - 1) * per
    return [t + n * 8 * per for n in range(-1, 3)], per
coll = {}
for f, d in F.items():
    if len(d['R']) == 17:
        R = d['R']; gaps = [R[i + 1] - R[i] for i in range(16)]
        i = min(range(16), key=lambda i: gaps[i])
        coll[f] = (i, gaps[i])
print('mesen 17-read frames', len(coll), collections.Counter(g for _, g in coll.values()).most_common(5))
# model check on Mesen collisions: offset of the extra read vs predicted DMA request
offs = collections.Counter()
for f, (i, g) in coll.items():
    d = F[f]; ts, per = dma_times(d)
    r = d['R'][i]
    best = min((r - t for t in ts), key=abs)
    offs[best] += 1
print('mesen: extra-read cycle - predicted DMA (most common)', offs.most_common(8))
# NesHawk conflicts: for each conflict frame, read-cycle minus predicted Mesen DMA, for all 16 reads (first 16 R)
h = collections.Counter(); nodata = 0
for f in sorted(conf):
    d = F.get(f)
    if not d: nodata += 1; continue
    ts, per = dma_times(d)
    if d['left'] == 0 and d['empty']:
        h['nosample'] += 1
    for r in d['R'][:16]:
        best = min((r - t for t in ts), key=abs)
        if abs(best) < 120:
            h[best] += 1
print('neshawk conflicts: nodata', nodata)
print('read - mesenDMA histogram near 0:', sorted(h.items(), key=lambda kv: -kv[1])[:25])

def dma_all(d, lo=-4, hi=4):
    per = d['P'] + 1
    t = d['T0'] + d['tau'] + 1 + (d['b'] - 1) * per
    return [t + n * 8 * per for n in range(lo, hi)]
score = collections.Counter()
for f in sorted(conf):
    d = F[f]
    ts = dma_all(d)
    hit = set()
    for r in d['R'][:16]:
        for t in ts:
            hit.add(r - t)
    for x in hit:
        score[x] += 1
print('delta candidates explaining most conflicts:', score.most_common(12))
