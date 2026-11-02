"""l53c: $BF scan of a row file. From TAS state F0 (or .mst + F0) poke $BF = v (all 256, or --vals a-b), play the rows,
report: room-change frame (first frame with $6E != start room), hp min, first hit frame, np at the end.
python work/l53c/bfscan.py <F0|path.mst F0> rows.txt [--poke '64=15'] [--vals 0-255] [--n N]
Rows file: one row per line ('-' blank), '#' comments, rows start at F0+1."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
POKE = opt('--poke', ''); VALS = opt('--vals', '0-255'); N = opt('--n', 0)
if a[0].endswith('.mst'):
    fc = core(a[0]); F0 = int(a[1]); RF = a[2]
else:
    F0 = int(a[0]); fc = core_at(F0); RF = a[1]
for p in [p for p in POKE.split(',') if p]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
rows = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')]
if N: rows = rows[:N]
fc.save('b'); fc._ka_slot = 'b'
r0 = fc.ram(); rm0 = r0[0x6E]
lo, hi = map(int, VALS.split('-'))
vals = list(range(lo, hi + 1))
summ = {}
for i0 in range(0, len(vals), 16):
    vs = vals[i0:i0 + 16]
    for v in vs:
        fc.load('b'); fc.poke(0xBF, v); fc.save(f'p{v}')
    rr = [fc.run_batch(f'p{v}', [rows], record='all')[0] for v in vs]
    for v, r in zip(vs, rr):
        st = r.states; ch = None; hits = []; hpmin = 99
        for i, s in enumerate(st):
            f = F0 + 1 + i
            if ch is None and s['room6e'] != rm0: ch = f
            if i and s['hp65'] < st[i-1]['hp65'] and st[i-1]['hp65'] < 100: hits.append(f)
            hpmin = min(hpmin, s['hp65'] if s['hp65'] < 100 else -1)
        e = st[-1]
        print(f'v {v:3d} room-change {ch} hpmin {hpmin} hits {hits[:4]} end hp {e["hp65"]} np {e["np64"]} it {e["item"]} X,y {RXY(e)}', flush=True)
        summ[v] = (ch, hpmin)
    for v in vs: fc.drop(f'p{v}')
good = [v for v in vals if summ[v][0] is not None and summ[v][1] >= 1]
print('GOOD', len(good), 'of', len(vals), ':', good)
chs = sorted(set(summ[v][0] for v in good))
print('room-change frames among good:', chs)
fc.close()
