import sys, bisect, collections, csv
sys.path.insert(0, 'work/fastcore'); sys.path.insert(0, '.')
from dmc_neshawk import load, simulate
from ng.inputs import read_inputs, to_mask
W, N, R = load('work/fastcore/out/dmc2.bin.dmc')
rows = [to_mask(r) for r in read_inputs('logs/tas4751.inputs.txt')]
tr = {int(r['row']): r for r in csv.DictReader(open('logs/tas4751.trace.csv'))}
conf = sorted(k for k in tr if tr[k]['lagged'] == '0' and int(tr[k]['pad']) != rows[k - 1])
d = simulate(W, -27, max(N.values()) + 40000)
for f in conf[:40]:
    rr = R[f][:16]
    i = bisect.bisect_left(d, rr[0] - 500)
    ds = [x for x in d[i:i + 6] if rr[0] - 500 <= x <= rr[-1] + 500]
    offs = [(j, r - x) for x in ds for j, r in enumerate(rr) if abs(r - x) <= 30]
    # writes in this frame
    wf = [(c - N[f], a, v) for c, a, v in W if N[f] <= c < rr[-1]] if f in N else []
    print(f, 'NMI->read0', rr[0] - N.get(f, 0), 'read span', rr[-1] - rr[0], 'dmas rel read0', [x - rr[0] for x in ds], 'near', offs, 'writes', [w for w in wf if w[1] != 0x4014])
