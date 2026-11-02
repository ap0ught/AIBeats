"""Prefix rows (file, rows from TAS frame F0+1; '#' lines skipped; optionally cut to its first m rows: --cuts a,b,c) + a climb cycle
(every rotation) x k + tail, from the TAS state F0 (Mesen). Prints the best frames for the goal.
python work/l61p/chtest.py F0 prefix 'R1 R2 ...' 'goal' [--ks 4,5,6] [--tail Left] [--n 140] [--cuts ...] [--waits 0,1,2]"""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
KS = [int(x) for x in opt('--ks', '4,5,6,7,8').split(',')]; TAIL = row(opt('--tail', 'Left')); N = opt('--n', 140)
CUTS = opt('--cuts', ''); WAITS = [int(x) for x in opt('--waits', '0').split(',')]; WROW = row(opt('--wrow', '-'))
F0, PF, CYC, G = int(a[0]), a[1], [row(x) for x in a[2].split()], compile(a[3], 'g', 'eval')
pre = [row(l.strip()) for l in open(PF) if l.strip() and not l.startswith('#')] if PF != '-' else []
cuts = [int(x) for x in CUTS.split(',')] if CUTS else [len(pre)]
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
cands = {}
for m in cuts:
    for w in WAITS:
        for r in range(len(CYC)):
            q = CYC[r:] + CYC[:r]
            for k in KS:
                rows = (pre[:m] + [WROW] * w + q * k + [TAIL] * N)[:m + N]
                if legal_ok(rows, hist): continue
                cands[(m, w, r, k)] = rows
print('cands', len(cands), flush=True)
names = list(cands); res = []
for i in range(0, len(names), 64):
    rr = fc.run_batch('b', [cands[n] for n in names[i:i+64]], record='all')
    for n, r_ in zip(names[i:i+64], rr):
        for t, s in enumerate(r_.states):
            X, y = RXY(s)
            if eval(G, dict(X=X, y=y, s=s, hp=s['hp65'], rm=s['room6e'])): res.append((F0 + 1 + t, s['hp65'], n)); break
res.sort()
for x in res[:15]: print(x, flush=True)
if not res: print('no goal')
if res:
    n = res[0][2]; out = f'work/l61p/ch_{F0}_best.txt'
    open(out, 'w').write(f'# chtest best {res[0][:2]} {n} (rows from TAS frame {F0 + 1})\n' + '\n'.join(P(x) for x in cands[n][:res[0][0] - F0 + 2]) + '\n')
    print('wrote', out)
fc.close()
