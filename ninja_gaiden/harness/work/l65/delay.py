"""For every arrival bf: cheapest 6-4b Start delay d (each row later = +1 f and bf + 1; $62 / $3E at the 6-5 control are frozen
through the load, so they do not change) to a covered phase: cost = d + END(bf + d). Uses demon_all.tsv via pick.py.
python work/l65/delay.py [--t62 29] [--e3e 4] [--out work/l65/demon_delay.tsv]"""
import sys
sys.path.insert(0, 'work/l65')
import pick
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
t62 = int(opt('--t62', '29')); e3e = int(opt('--e3e', '4')); OUT = opt('--out', 'work/l65/demon_delay.tsv')
tab = pick.load()
endv = {}
for bf in range(256):
    c = pick.best(bf, t62, e3e, tab)
    if c: endv[bf] = (c[0][0], c[0][3])
rows = []
for bf in range(256):
    best = None
    for d in range(256):
        b = (bf + d) % 256
        if b in endv:
            cost = d + endv[b][0]
            if best is None or cost < best[0]: best = (cost, d, b, endv[b][1])
    rows.append((bf, *best))
with open(OUT, 'w', newline='\n') as f:
    f.write(f'# arrival bf, total = Start delay + END seen offset (t62 {t62}, e3e {e3e}), delay, phase used, line\n')
    for r in rows: f.write('\t'.join(map(str, r)) + '\n')
tot = [r[1] for r in rows]
print('total cost (delay + END): best', min(tot), 'worst', max(tot), 'mean %.1f' % (sum(tot) / 256))
print('worst arrivals', sorted(rows, key=lambda r: -r[1])[:5])
