"""Collect every (bf, line, kill row, hp) result into work/l65/demon_all.tsv and the best line per bf (for the TAS-like arrival
t62 29, e3e 4) into work/l65/demon_table.tsv. Sources: work/l65/sweep_res.tsv (+ any *.res.tsv in work/l65), l63p's r2d5 scan,
NesHawk confirmations in work/l65/nh_ok.tsv (bf<TAB>line<TAB>kill row)."""
import sys, os, glob
sys.path.insert(0, 'work/l65')
import pick
res = {}
def add(bf, line, k, hp):
    key = (bf, line)
    if key not in res or res[key][0] > k: res[key] = (k, hp)
for fn in ['work/l65/sweep_res.tsv'] + sorted(glob.glob('work/l65/*.res.tsv')):
    if not os.path.exists(fn): continue
    for l in open(fn):
        if l.startswith('#') or not l.strip(): continue
        p = l.split('\t')
        if p[2].strip() in ('-', 'None'): continue
        add(int(p[0]), p[1], int(p[2]), int(p[3]))
# l63p's Mesen scan of dm_r2d5_kill (kill frame 39239/39244/39249 = rows 307/312/317 from control 38,933)
for l in open('work/l63p/bf_65_r2d5.out'):
    if l.startswith('kill 392'):
        f = int(l.split()[1]); vs = l.split('[', 1)[1].rstrip(']\n').split(',')
        for v in vs: add(int(v), 'work/l63p/dm_r2d5_kill.txt', f - 38932, 12)
nh = set()
if os.path.exists('work/l65/nh_ok.tsv'):
    for l in open('work/l65/nh_ok.tsv'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 3: nh.add((int(p[0]), p[1], int(p[2])))
with open('work/l65/demon_all.tsv', 'w', newline='\n') as f:
    f.write('# bf\tline\tkill_row\thp\tneshawk\n')
    for (bf, line), (k, hp) in sorted(res.items()):
        f.write(f'{bf}\t{line}\t{k}\t{hp}\t{"y" if (bf, line, k) in nh else "n"}\n')
tab = pick.load('work/l65/demon_all.tsv')
best = {}
with open('work/l65/demon_table.tsv', 'w', newline='\n') as f:
    f.write('# bf = $BF before the 6-5 control row; END = END seen - control frame for $62 29 / $3E 4 at control-1 (TAS arrival; '
            'use pick.py for others); record pace 755.2\n# bf\tline\tkill_row\tEND_seen_offset\thp_left\tneshawk_checked\n')
    for bf in range(256):
        c = pick.best(bf, 29, 4, tab)
        if not c:
            f.write(f'{bf}\t-\t-\t-\t-\tn\n'); continue
        e, _, k, line, T, hp, nhf = c[0]
        best[bf] = e
        f.write(f'{bf}\t{line}\t{k}\t{e}\t{hp}\t{nhf}\n')
cov = sorted(best)
print('covered', len(cov), '/ 256')
if best:
    vals = sorted(best.values())
    print('END offset best', vals[0], 'worst', vals[-1], 'median', vals[len(vals) // 2])
    print('missing', [b for b in range(256) if b not in best])
