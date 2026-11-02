"""Shift a found heart line to other arrival phases and test it (Mesen, TAS control-1 state with $BF poked).
A line made by jplan65 from podP1.txt starts its first heart step with 'R{nw}.-{wt}' (walk, wait); for a phase w with heart-down
row hd(w) the shifted line waits wt + hd(w) - hd(v) rows instead (the heart pattern keeps its timing relative to the heart).
python work/l65/sweep.py <line.txt> --base-bf v [--vals 0-255] [--shifts 0] [--res work/l65/sweep_res.tsv]
Appends 'bf<TAB>file<TAB>kill row<TAB>hp' for every kill to --res and writes the shifted line files to work/l65/lines/."""
import sys, os, re
sys.path.insert(0, 'work/l65')
from lib65 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
V = int(opt('--base-bf', '0')); VS = opt('--vals', '0-255'); RES = opt('--res', 'work/l65/sweep_res.tsv')
EXTRA = [int(x) for x in opt('--shifts', '0').split(',')]
vals = []
for p in VS.split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    elif p: vals.append(int(p))
HD = {}
for l in open('work/l65/fb1.out'):
    p = l.split()
    if len(p) > 2 and p[1] == 'hd': HD[int(p[0])] = int(p[2])
src = a[0]
txt = open(src).read().splitlines()
hdr = txt[0]
m = re.search(r"\((\d+), 'R(\d+)\.-(\d+)'", hdr)
npre = int(re.search(r'\((\d+) rows\)', hdr).group(1))
nw, wt = int(m.group(2)), int(m.group(3))
rows = rows_of(src)
pre, rest = rows[:npre], rows[npre + nw + wt:]
os.makedirs('work/l65/lines', exist_ok=True)
fc = core65()
base = os.path.splitext(os.path.basename(src))[0]
out = []
for w in vals:
    for ex in EXTRA:
        d = HD[w] - HD[V] + ex
        if wt + d < 0: continue
        rr = pre + [('Right',)] * nw + [()] * (wt + d) + rest
        o = test_bfs(fc, rr + [()] * 20, [w])[w]
        if o[0]:
            fn = f'work/l65/lines/{base}_w{wt + d}.txt'
            if not os.path.exists(fn):
                with open(fn, 'w', newline='\n') as f:
                    f.write(f'# l65 6-5 line: {src} with the pre-heart wait {wt} -> {wt + d} rows (row 1 = 6-5 control row)\n')
                    for r in rr: f.write(('+'.join(r) if r else '') + '\n')
            out.append(f'{w}\t{fn}\t{o[0]}\t{o[1]}')
            print(w, 'shift', d, 'kill', o[0], 'hp', o[1], flush=True)
            break
fc.close()
with open(RES, 'a', newline='\n') as f:
    for l in out: f.write(l + '\n')
print('kills', len(out), 'of', len(vals))
