import sys, bisect, collections, csv
sys.path.insert(0, 'work/fastcore'); sys.path.insert(0, '.')
from dmc_neshawk import load, simulate
from ng.inputs import read_inputs, to_mask
W, N, R = load('work/fastcore/out/dmc2.bin.dmc')
rows = [to_mask(r) for r in read_inputs('logs/tas4751.inputs.txt')]
tr = {int(r['row']): r for r in csv.DictReader(open('logs/tas4751.trace.csv'))}
conf = set(k for k in tr if tr[k]['lagged'] == '0' and int(tr[k]['pad']) != rows[k - 1])
chg = set(k for k in tr if tr[k]['lagged'] == '0' and k >= 2 and int(tr[k - 1]['pad']) != rows[k - 1])
d = simulate(W, -27, max(N.values()) + 40000)
# x = DMA cycle relative to the nearest read, labelled with the read index
hc, hn = collections.Counter(), collections.Counter()
for f in sorted(chg):
    rr = R.get(f, [])[:16]
    if len(rr) < 16: continue
    i = bisect.bisect_left(d, rr[0] - 60)
    keys = set()
    while i < len(d) and d[i] <= rr[-1] + 30:
        x = d[i]
        j = min(range(16), key=lambda j: abs(rr[j] - x))
        keys.add((j, x - rr[j]))
        i += 1
    for k in keys:
        (hc if f in conf else hn)[k] += 1
# collapse by offset only, show conflict vs non-conflict counts for offsets -30..30
byoff_c, byoff_n = collections.Counter(), collections.Counter()
for (j, o), c in hc.items(): byoff_c[o] += c
for (j, o), c in hn.items(): byoff_n[o] += c
for o in range(-30, 31):
    if byoff_c[o] or byoff_n[o]:
        print('offset %3d  conflict %3d  no-conflict %3d' % (o, byoff_c[o], byoff_n[o]))
print('by read index for conflicts:', sorted(hc.items(), key=lambda kv: kv[0])[:80])

def vis(mask, prevpad, j):
    """deletion before read j (0..15): does the game keep the previous pad (and does that differ from the row)?"""
    b = [(mask >> (7 - k)) & 1 for k in range(8)]
    p, jj = divmod(j, 8)
    alt = b[:jj] + b[jj + 1:] + [1]
    v = 0
    for x in alt: v = (v << 1) | x
    return v != mask and prevpad != mask
print()
for shift in (0, 1):
    vc, vn = collections.Counter(), collections.Counter()
    for f in sorted(chg):
        rr = R.get(f, [])[:16]
        if len(rr) < 16: continue
        m = rows[f - 1]; prev = int(tr[f - 1]['pad'])
        i = bisect.bisect_left(d, rr[0] - 60)
        keys = set()
        while i < len(d) and d[i] <= rr[-1] + 30:
            x = d[i]
            for j in range(16):
                o = x - rr[j]
                if -6 <= o <= 6 and vis(m, prev, min(15, j + shift)):
                    keys.add(o)
            i += 1
        for o in keys:
            (vc if f in conf else vn)[o] += 1
    print('shift', shift, [(o, vc[o], vn[o]) for o in range(-6, 7)])
